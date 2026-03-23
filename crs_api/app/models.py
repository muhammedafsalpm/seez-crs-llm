from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Literal
from enum import Enum
from datetime import datetime


class RecommenderType(str, Enum):
    FEW_SHOT = "few_shot"
    RAG = "rag"
    AGENT = "agent"


class Message(BaseModel):
    """Single message in conversation"""
    role: Literal["user", "assistant", "system"] = Field(..., description="Message sender role")
    content: str = Field(..., min_length=1, max_length=1000, description="Message content")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)
    
    @validator('content')
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError("Message content cannot be empty")
        return v.strip()


class RecommendationRequest(BaseModel):
    """Request model for recommendations"""
    conversation_history: List[Message] = Field(..., min_items=1, max_items=20)
    user_id: Optional[str] = Field(None, min_length=1, max_length=50)
    recommender_type: RecommenderType = Field(default=RecommenderType.RAG)
    num_recommendations: int = Field(default=5, ge=1, le=20)
    temperature: float = Field(default=0.7, ge=0, le=1)
    include_reasoning: bool = Field(default=True)
    stream: bool = Field(default=False)
    
    @validator('conversation_history')
    def validate_history(cls, v):
        # Ensure alternating roles
        for i, msg in enumerate(v):
            if i > 0 and msg.role == v[i-1].role:
                raise ValueError("Messages must alternate between user and assistant")
        return v


class RecommendationResponse(BaseModel):
    """Response model for recommendations"""
    recommendations: List[str] = Field(..., description="List of recommended items")
    reasoning: Optional[str] = Field(None, description="Reasoning behind recommendations")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "recommendations": ["Inception", "The Matrix", "Interstellar"],
                "reasoning": "Based on your interest in sci-fi and mind-bending plots...",
                "metadata": {"recommender_type": "rag", "processing_time_ms": 245}
            }
        }


class EvaluationMetrics(BaseModel):
    """Evaluation metrics for recommendations"""
    recall_at_k: Dict[int, float]
    ndcg_at_k: Dict[int, float]
    precision_at_k: Dict[int, float]
    mrr: float
    total_samples: int


class HealthResponse(BaseModel):
    """Health check response"""
    status: Literal["healthy", "degraded", "unhealthy"]
    version: str
    timestamp: datetime
    components: Dict[str, bool]
