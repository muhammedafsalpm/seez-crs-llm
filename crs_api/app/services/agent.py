from typing import List, Dict, Any, Optional
from app.services.base import BaseRecommender
from app.models import Message

from app.utils.prompts import get_agent_prompt, SYSTEM_PROMPT
import logging

logger = logging.getLogger(__name__)


class AgentRecommender(BaseRecommender):
    """Agent-based recommender simulating tool use"""
    
    def __init__(self, data_loader, embedding_model=None):
        super().__init__(data_loader, embedding_model)
        self.available_movies = data_loader.get_all_items()
    
    async def recommend(
        self,
        conversation_history: List[Message],
        user_id: Optional[str] = None,
        num_recommendations: int = 5,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Generate recommendations using agent-based approach"""
        
        # Format conversation
        formatted_conversation = self._format_conversation(conversation_history)
        
        # Get user history and might-likes
        user_history = None
        might_likes = None
        
        if user_id:
            user_history = self.data_loader.get_user_history(user_id)
            might_likes = self.data_loader.get_user_might_likes(user_id)
        
        # Use might_likes as the "database" for the agent
        available_items = might_likes if might_likes else self.available_movies[:50]
        
        # Create agent prompt
        prompt = get_agent_prompt(formatted_conversation, available_items, user_history)
        
        # Call LLM using unified client
        try:
            response_text = await self._call_llm(
                prompt=prompt,
                system_prompt=SYSTEM_PROMPT,
                temperature=temperature
            )
            
            recommendations = self._parse_recommendations(response_text)
            
            # Filter to ensure recommendations are from available items
            available_set = set(available_items)
            recommendations = [r for r in recommendations if r in available_set]
            recommendations = recommendations[:num_recommendations]
            
            # Add personalized fallbacks if needed
            if len(recommendations) < num_recommendations and might_likes:
                fallbacks = might_likes[:num_recommendations]
                recommendations.extend(fallbacks[:num_recommendations - len(recommendations)])
            
            return {
                "recommendations": recommendations,
                "reasoning": response_text[:1000],
                "metadata": {
                    "recommender_type": "agent",
                    "user_id": user_id,
                    "personalized": user_id is not None,
                    "available_items": len(available_items),
                    "llm_provider": self.settings.LLM_PROVIDER
                }
            }
            
        except Exception as e:
            logger.error(f"Agent recommendation failed: {e}")
            return {
                "recommendations": might_likes[:num_recommendations] if might_likes else self.available_movies[:num_recommendations],
                "reasoning": f"Error: {str(e)}",
                "metadata": {
                    "error": str(e), 
                    "recommender_type": "agent",
                    "llm_provider": self.settings.LLM_PROVIDER
                }
            }
