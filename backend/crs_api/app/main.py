from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import json
import time
from datetime import datetime
from typing import AsyncGenerator

from app.models import (
    RecommendationRequest, RecommendationResponse, 
    HealthResponse, RecommenderType
)
from app.services.few_shot import FewShotRecommender
from app.services.rag import RAGRecommender
from app.services.agent import AgentRecommender
from app.utils.data_loader import DataLoader
from app.middleware import RateLimitMiddleware, LoggingMiddleware
from app.config import get_settings
from app.exceptions import CRSException, InvalidUserException

settings = get_settings()

# Global instances
data_loader = None
few_shot_recommender = None
rag_recommender = None
agent_recommender = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan manager for startup/shutdown"""
    global data_loader, few_shot_recommender, rag_recommender, agent_recommender
    
    # Initialize data loader
    data_loader = DataLoader(settings.DATA_PATH)
    
    # Initialize recommenders
    few_shot_recommender = FewShotRecommender(data_loader)
    rag_recommender = RAGRecommender(data_loader)
    agent_recommender = AgentRecommender(data_loader)
    
    print(f"""
    ╔══════════════════════════════════════════════════════════╗
    ║  Conversational Recommender System API v{settings.VERSION}         ║
    ║  Dataset: LLM-REDIAL (Movie)                             ║
    ║  Models: Few-shot | RAG | Agent                          ║
    ║  Loaded: {len(data_loader.user_data)} users, {len(data_loader.item_map)} movies   ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    yield
    
    # Cleanup
    print("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="LLM-based Conversational Recommender System using LLM-REDIAL dataset",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add middleware
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.add_middleware(RateLimitMiddleware)
app.add_middleware(LoggingMiddleware)


def get_recommender(recommender_type: RecommenderType):
    """Dependency injection for recommenders"""
    if recommender_type == RecommenderType.FEW_SHOT:
        return few_shot_recommender
    elif recommender_type == RecommenderType.RAG:
        return rag_recommender
    elif recommender_type == RecommenderType.AGENT:
        return agent_recommender
    return rag_recommender


@app.get("/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version=settings.VERSION,
        timestamp=datetime.now(),
        components={
            "data_loader": data_loader is not None,
            "few_shot": few_shot_recommender is not None,
            "rag": rag_recommender is not None,
            "agent": agent_recommender is not None
        }
    )


@app.post("/api/v1/recommend", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """Get movie recommendations"""
    
    if not request.conversation_history:
        raise HTTPException(status_code=400, detail="Conversation history cannot be empty")
    
    recommender = get_recommender(request.recommender_type)
    
    start_time = time.time()
    
    try:
        result = await recommender.recommend(
            conversation_history=request.conversation_history,
            user_id=request.user_id,
            num_recommendations=request.num_recommendations,
            temperature=request.temperature
        )
        
        # Add processing time
        result["metadata"]["processing_time_ms"] = int((time.time() - start_time) * 1000)
        
        return RecommendationResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/recommend/stream")
async def get_recommendations_stream(request: RecommendationRequest):
    """Stream recommendations as they're generated"""
    
    async def generate() -> AsyncGenerator[str, None]:
        recommender = get_recommender(request.recommender_type)
        
        try:
            result = await recommender.recommend(
                conversation_history=request.conversation_history,
                user_id=request.user_id,
                num_recommendations=request.num_recommendations,
                temperature=request.temperature
            )
            
            # Stream recommendations one by one
            for i, rec in enumerate(result["recommendations"]):
                yield f"data: {json.dumps({'type': 'recommendation', 'index': i + 1, 'movie': rec})}\n\n"
                await asyncio.sleep(0.1)  # Simulate streaming
            
            # Stream reasoning
            if result.get("reasoning"):
                yield f"data: {json.dumps({'type': 'reasoning', 'content': result['reasoning']})}\n\n"
            
            # Stream metadata
            yield f"data: {json.dumps({'type': 'metadata', 'data': result['metadata']})}\n\n"
            
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")


@app.get("/api/v1/user/{user_id}")
async def get_user_info(user_id: str):
    """Get user information"""
    user_data = data_loader.get_user_data(user_id)
    
    if not user_data:
        raise InvalidUserException(user_id)
    
    return {
        "user_id": user_id,
        "history": user_data.history_interaction[:20],
        "might_likes": user_data.user_might_like[:10],
        "total_history": len(user_data.history_interaction),
        "total_conversations": len(user_data.conversations)
    }


@app.get("/api/v1/movies/search")
async def search_movies(q: str, limit: int = 10):
    """Search for movies"""
    results = data_loader.search_items(q, limit)
    return {"query": q, "results": results, "total": len(results)}


@app.get("/api/v1/metrics")
async def get_metrics():
    """Get system metrics"""
    return {
        "users": len(data_loader.user_data) if data_loader else 0,
        "movies": len(data_loader.item_map) if data_loader else 0,
        "conversations": len(data_loader.conversation_texts) if data_loader else 0
    }


@app.exception_handler(CRSException)
async def crs_exception_handler(request: Request, exc: CRSException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "code": exc.error_code}
    )
