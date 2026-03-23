from typing import List, Dict, Any, Optional
import openai
import asyncio
from app.services.base import BaseRecommender
from app.utils.prompts import SYSTEM_PROMPT, get_improved_prompt_1, get_improved_prompt_2
from app.config import get_settings
from app.models import Message
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class FewShotRecommender(BaseRecommender):
    """Few-shot learning recommender with prompt improvements"""
    
    def __init__(self, data_loader, embedding_model=None):
        super().__init__(data_loader, embedding_model)
        self.examples = data_loader.get_conversation_examples(5)
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
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
        # This implements the 2 prompt improvements
        if len(conversation_history) > 3:
            # Use chain-of-thought for longer conversations
            prompt = get_improved_prompt_2(formatted_conversation, user_history)
        else:
            # Use structured extraction for shorter conversations
            prompt = get_improved_prompt_1(formatted_conversation, user_history)
        
        # Call LLM with retry logic
        for attempt in range(3):
            try:
                response = await self.client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature,
                    max_tokens=settings.OPENAI_MAX_TOKENS,
                    timeout=30.0
                )
                
                response_text = response.choices[0].message.content
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
                        "attempt": attempt + 1
                    }
                }
                
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {e}")
                if attempt == 2:
                    return {
                        "recommendations": await self._get_fallback_recommendations(user_history),
                        "reasoning": f"Error: {str(e)}",
                        "metadata": {"error": str(e), "recommender_type": "few_shot"}
                    }
                await asyncio.sleep(1)
    
    async def _get_fallback_recommendations(self, user_history: Optional[List[str]] = None) -> List[str]:
        """Get fallback recommendations"""
        all_items = self.data_loader.get_all_items()
        
        if not user_history:
            return all_items[:10]
        
        # Return items not in history
        return [item for item in all_items[:20] if item not in user_history][:10]
