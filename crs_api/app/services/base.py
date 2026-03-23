from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.models import Message
import logging

logger = logging.getLogger(__name__)


class BaseRecommender(ABC):
    """Base recommender with common functionality"""
    
    def __init__(self, data_loader, embedding_model=None):
        self.data_loader = data_loader
        self.embedding_model = embedding_model
        # Use a reasonable default for history if not defined in data_loader
        self.max_history_turns = getattr(data_loader, 'MAX_HISTORY_TURNS', 10)
    
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
        for msg in messages[-self.max_history_turns:]:
            formatted.append(f"{msg.role.capitalize()}: {msg.content}")
        return "\n".join(formatted)
    
    def _parse_recommendations(self, response: str) -> List[str]:
        """Parse recommendations from response"""
        import re
        
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
