from typing import List, Dict, Any, Optional
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
from app.services.base import BaseRecommender
from app.models import Message

from app.vector_store.faiss_index import FAISSVectorStore
from app.utils.prompts import get_rag_prompt, SYSTEM_PROMPT
import logging

logger = logging.getLogger(__name__)


class RAGRecommender(BaseRecommender):
    """Retrieval-Augmented Generation recommender with FAISS"""
    
    def __init__(self, data_loader, embedding_model=None):
        super().__init__(data_loader, embedding_model)
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(self.settings.EMBEDDING_MODEL)
        
        # Initialize FAISS vector store
        self.vector_store = FAISSVectorStore(dimension=self.settings.VECTOR_DIM)
        
        # Build or load index
        self._build_vector_store()
    
    def _build_vector_store(self):
        """Build FAISS index from conversations"""
        index_path = Path(self.settings.DATA_PATH) / "index"
        
        # Try to load existing index
        if index_path.exists():
            try:
                self.vector_store.load(index_path)
                logger.info("Loaded existing FAISS index")
                return
            except Exception as e:
                logger.warning(f"Could not load index: {e}")
        
        # Build new index
        logger.info("Building FAISS index from conversations...")
        vectors = []
        texts = []
        metadata = []
        
        # Use a subset of user data to build index (to avoid OOM or long wait)
        count = 0
        for user_id, user_data in self.data_loader.user_data.items():
            if count > 500: # Limit to 500 users for initial index
                break
            for conv in user_data.conversations[:2]:  # Limit per user
                for conv_key, conv_data in conv.items():
                    if isinstance(conv_data, dict) and "conversation_id" in conv_data:
                        conv_id = conv_data["conversation_id"]
                        conv_text = self.data_loader.conversation_texts.get(conv_id, "")
                        if conv_text and len(conv_text) > 50:
                            # Create embedding
                            embedding = self.embedding_model.encode(conv_text)
                            vectors.append(embedding)
                            texts.append(conv_text[:500])  # Truncate for storage
                            metadata.append({
                                "user_id": user_id,
                                "conversation_id": conv_id,
                                "rec_items": conv_data.get("rec_item", [])
                            })
            count += 1
        
        if vectors:
            vectors_array = np.array(vectors)
            self.vector_store.add(vectors_array, texts, metadata)
            self.vector_store.save(index_path)
            logger.info(f"Built FAISS index with {len(vectors)} vectors")
    
    async def recommend(
        self,
        conversation_history: List[Message],
        user_id: Optional[str] = None,
        num_recommendations: int = 5,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Generate recommendations using RAG"""
        
        # Format conversation
        formatted_conversation = self._format_conversation(conversation_history)
        
        # Create query embedding for retrieval
        query_embedding = self.embedding_model.encode(formatted_conversation)
        
        # Retrieve relevant conversations
        retrieved = self.vector_store.search(query_embedding, k=self.settings.RETRIEVAL_K)
        
        # Get user history
        user_history = None
        if user_id:
            user_history = self.data_loader.get_user_history(user_id)
        
        # Create RAG prompt with retrieved context
        retrieved_contexts = [text for text, _, _ in retrieved if text]
        prompt = get_rag_prompt(formatted_conversation, retrieved_contexts, user_history)
        
        # Call LLM using unified client (supports OpenAI and Ollama)
        try:
            response_text = await self._call_llm(
                prompt=prompt,
                system_prompt=SYSTEM_PROMPT,
                temperature=temperature
            )
            
            recommendations = self._parse_recommendations(response_text)
            recommendations = recommendations[:num_recommendations]
            
            return {
                "recommendations": recommendations,
                "reasoning": response_text[:1000],
                "metadata": {
                    "recommender_type": "rag",
                    "retrieved_docs": len(retrieved),
                    "top_similarity": retrieved[0][2] if retrieved else 0,
                    "user_id": user_id,
                    "llm_provider": self.settings.LLM_PROVIDER
                }
            }
            
        except Exception as e:
            logger.error(f"RAG recommendation failed: {e}")
            return {
                "recommendations": await self._get_fallback_recommendations(user_history),
                "reasoning": f"Error: {str(e)}",
                "metadata": {
                    "error": str(e), 
                    "recommender_type": "rag",
                    "llm_provider": self.settings.LLM_PROVIDER
                }
            }
    
    async def _get_fallback_recommendations(self, user_history: Optional[List[str]] = None) -> List[str]:
        """Get fallback recommendations"""
        all_items = self.data_loader.get_all_items()
        
        if not user_history:
            return all_items[:10]
        
        # Return items not in history
        return [item for item in all_items[:20] if item not in user_history][:10]
