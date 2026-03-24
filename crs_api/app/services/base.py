from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import asyncio
import re
import logging
from app.models import Message
from app.services.llm_client import get_llm_client, BaseLLMClient, MockLLMClient
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class BaseRecommender(ABC):
    """Base recommender with common functionality"""
    
    def __init__(self, data_loader, embedding_model=None):
        self.data_loader = data_loader
        self.embedding_model = embedding_model
        self.llm_client: BaseLLMClient = get_llm_client()  # This now supports both OpenAI and Ollama
        self.settings = settings
    
    @abstractmethod
    async def recommend(
        self,
        conversation_history: List[Message],
        user_id: Optional[str] = None,
        num_recommendations: int = 5,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Generate recommendations"""
        pass
    
    def _format_conversation(self, messages: List[Message]) -> str:
        """Format conversation as string"""
        formatted = []
        for msg in messages[-self.settings.MAX_HISTORY_TURNS:]:
            formatted.append(f"{msg.role.capitalize()}: {msg.content}")
        return "\n".join(formatted)
    
    def _parse_recommendations(self, response: str) -> List[str]:
        """Parse recommendations from response"""
        movies = []
        
        # Try to find JSON first
        json_pattern = r'```json\s*({.*?})\s*```'
        json_match = re.search(json_pattern, response, re.DOTALL)
        if json_match:
            try:
                import json
                data = json.loads(json_match.group(1))
                if 'recommendations' in data:
                    return data['recommendations'][:10]
            except:
                pass
        
        # Pattern for numbered or bulleted lists
        lines = response.split('\n')
        for line in lines:
            # Check for bullet or number followed by movie
            match = re.search(r'[*-]\s*["\']?([^"\'\n]+)["\']?', line)
            if not match:
                match = re.search(r'\d+\.\s*["\']?([^"\'\n]+)["\']?', line)
            
            if match:
                candidate = match.group(1).strip()
                # Filter out common non-movie phrases
                if len(candidate) > 2 and not any(x in candidate.lower() for x in 
                    ['recommend', 'movie', 'film', 'here', 'based', 'watch']):
                    movies.append(candidate)
        
        # Pattern for quoted movies
        quoted = re.findall(r'"([^"]+)"', response)
        movies.extend(quoted)
        
        # Deduplicate and clean
        movies = list(dict.fromkeys(movies))
        return [m.strip() for m in movies if m.strip()][:10]
    
    async def _call_llm(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        """Unified LLM call using the configured client"""
        try:
            return await self.llm_client.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=self.settings.OPENAI_MAX_TOKENS  # Works for both
            )
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            # Fallback to mock if available
            if self.settings.USE_MOCK_LLM:
                logger.info("Falling back to mock LLM")
                mock_client = MockLLMClient()
                return await mock_client.generate(prompt, system_prompt, temperature)
            raise
