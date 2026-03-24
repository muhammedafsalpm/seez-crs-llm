from typing import List, Dict, Any, Optional
from app.services.base import BaseRecommender
from app.models import Message

from app.utils.prompts import SYSTEM_PROMPT, get_improved_prompt_1, get_improved_prompt_2, get_few_shot_prompt
import logging

logger = logging.getLogger(__name__)


class FewShotRecommender(BaseRecommender):
    """Few-shot learning recommender with prompt improvements"""
    
    def __init__(self, data_loader, embedding_model=None):
        super().__init__(data_loader, embedding_model)
        self.examples = data_loader.get_conversation_examples(5)
    
    async def recommend(
        self,
        conversation_history: List[Message],
        user_id: Optional[str] = None,
        num_recommendations: int = 5,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Generate recommendations using few-shot learning"""
        
        # Format conversation
        formatted_conversation = self._format_conversation(conversation_history)
        
        # Get user history if available
        user_history = None
        if user_id:
            user_history = self.data_loader.get_user_history(user_id)
        
        # Use improved prompt for better accuracy
        if len(conversation_history) > 3:
            # Use chain-of-thought for longer conversations
            prompt = get_improved_prompt_2(formatted_conversation, user_history)
        else:
            # Use structured extraction for shorter conversations
            prompt = get_improved_prompt_1(formatted_conversation, user_history)
        
        # Call LLM using unified client (supports OpenAI and Ollama)
        try:
            response_text = await self._call_llm(
                prompt=prompt,
                system_prompt=SYSTEM_PROMPT,
                temperature=temperature
            )
            
            recommendations = self._parse_recommendations(response_text)
            
            # Limit to requested number
            recommendations = recommendations[:num_recommendations]
            
            # Add fallbacks if needed
            if len(recommendations) < num_recommendations and user_history:
                fallbacks = await self._get_fallback_recommendations(user_history)
                recommendations.extend(fallbacks[:num_recommendations - len(recommendations)])
            
            return {
                "recommendations": recommendations,
                "reasoning": response_text[:1000] if len(response_text) > 1000 else response_text,
                "metadata": {
                    "recommender_type": "few_shot",
                    "num_examples": len(self.examples),
                    "prompt_improvement": "chain_of_thought" if len(conversation_history) > 3 else "preference_extraction",
                    "user_id": user_id,
                    "llm_provider": self.settings.LLM_PROVIDER
                }
            }
            
        except Exception as e:
            logger.error(f"Few-shot recommendation failed: {e}")
            return {
                "recommendations": await self._get_fallback_recommendations(user_history),
                "reasoning": f"Error: {str(e)}",
                "metadata": {
                    "error": str(e), 
                    "recommender_type": "few_shot",
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
