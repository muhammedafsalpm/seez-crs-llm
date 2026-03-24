import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
import logging
from tqdm import tqdm
from functools import lru_cache

logger = logging.getLogger(__name__)


@dataclass
class UserData:
    """User data container"""
    user_id: str
    history_interaction: List[str]
    user_might_like: List[str]
    conversations: List[Dict]
    likes: List[str]
    dislikes: List[str]


class DataLoader:
    """Optimized data loader with caching"""
    
    def __init__(self, data_path: str):
        self.data_path = Path(data_path)
        print(f"Initializing DataLoader with path: {self.data_path.absolute()}")
        if not self.data_path.exists():
            print(f"❌ ERROR: Data path does not exist: {self.data_path}")
        
        self.item_map: Dict[str, str] = {}
        self.user_map: Dict[str, int] = {}
        self.user_data: Dict[str, UserData] = {}
        self.conversation_texts: Dict[int, str] = {}
        self._load_data()
    
    def _load_data(self):
        """Load all data with progress bars"""
        logger.info(f"Loading LLM-REDIAL Movie dataset from {self.data_path}...")
        
        # Load item map
        item_map_path = self.data_path / "item_map.json"
        if item_map_path.exists():
            with open(item_map_path, 'r') as f:
                self.item_map = json.load(f)
            logger.info(f"Loaded {len(self.item_map)} items")
        
        # Load user map (adjusted to user_ids.json as observed in filesystem)
        user_map_path = self.data_path / "user_ids.json"
        if user_map_path.exists():
            with open(user_map_path, 'r') as f:
                self.user_map = json.load(f)
            logger.info(f"Loaded {len(self.user_map)} users from user_ids.json")
        else:
            # Fallback to user_map.json if it exists
            user_map_path = self.data_path / "user_map.json"
            if user_map_path.exists():
                with open(user_map_path, 'r') as f:
                    self.user_map = json.load(f)
                logger.info(f"Loaded {len(self.user_map)} users from user_map.json")
        
        # Load final data
        final_data_path = self.data_path / "final_data.jsonl"
        if final_data_path.exists():
            with open(final_data_path, 'r') as f:
                for line in tqdm(f, desc="Loading user data"):
                    try:
                        entry = json.loads(line)
                        self._process_user_entry(entry)
                    except json.JSONDecodeError:
                        continue
            logger.info(f"Loaded {len(self.user_data)} users with data")
        
        # Load conversation texts
        conv_path = self.data_path / "Conversation.txt"
        if conv_path.exists():
            self._load_conversations(conv_path)
            logger.info(f"Loaded {len(self.conversation_texts)} conversations")
    
    def _process_user_entry(self, entry: Dict):
        """Process single user entry"""
        for user_id, user_info in entry.items():
            # The structure in final_data.jsonl seems to have "history_interaction" or "history_item"
            # Based on my check: {"A30Q8X8B1S3GGT": {"history_item": ...}}
            history = user_info.get("history_interaction", user_info.get("history_item", []))
            might_likes = user_info.get("user_might_like", [])
            
            # Convert item IDs to names
            history_names = [self.item_map.get(str(hid), str(hid)) for hid in history]
            might_likes_names = [self.item_map.get(str(mid), str(mid)) for mid in might_likes]
            
            # Extract likes/dislikes (based on paper: ratings >=4 = likes, <=2 = dislikes)
            # Use might_likes as likes proxy as per original implementation
            likes = might_likes_names[:len(might_likes_names)//2]
            dislikes = might_likes_names[len(might_likes_names)//2:]
            
            self.user_data[user_id] = UserData(
                user_id=user_id,
                history_interaction=history_names,
                user_might_like=might_likes_names,
                conversations=user_info.get("Conversation", []),
                likes=likes,
                dislikes=dislikes
            )
    
    def _load_conversations(self, path: Path):
        """Parse Conversation.txt file"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.strip().split('\n\n')
            current_id = None
            current_text = []
            
            for line in lines:
                line = line.strip()
                if line.isdigit():
                    if current_id is not None:
                        self.conversation_texts[current_id] = '\n'.join(current_text)
                    current_id = int(line)
                    current_text = []
                else:
                    current_text.append(line)
            
            if current_id is not None:
                self.conversation_texts[current_id] = '\n'.join(current_text)
        except Exception as e:
            logger.error(f"Error loading conversations: {e}")
    
    @lru_cache(maxsize=1000)
    def get_user_data(self, user_id: str) -> Optional[UserData]:
        """Get user data with caching"""
        return self.user_data.get(user_id)
    
    def get_user_history(self, user_id: str) -> List[str]:
        """Get user's historical interactions"""
        user_data = self.get_user_data(user_id)
        return user_data.history_interaction if user_data else []
    
    def get_user_might_likes(self, user_id: str) -> List[str]:
        """Get items user might like"""
        user_data = self.get_user_data(user_id)
        return user_data.user_might_like if user_data else []
    
    def get_conversation_examples(self, num_examples: int = 5) -> List[Tuple[str, List[str]]]:
        """Get examples for few-shot learning"""
        examples = []
        for user_id, user_data in list(self.user_data.items())[:num_examples]:
            for conv in user_data.conversations[:1]:
                # Each conv is a dict with conversation_id as key or contains it
                for conv_key, conv_data in conv.items():
                    if isinstance(conv_data, dict) and "conversation_id" in conv_data:
                        conv_id = conv_data["conversation_id"]
                        conv_text = self.conversation_texts.get(conv_id, "")
                        if conv_text:
                            rec_items = [self.item_map.get(str(rid), str(rid)) 
                                        for rid in conv_data.get("rec_item", [])]
                            examples.append((conv_text, rec_items))
        return examples
    
    def get_all_items(self) -> List[str]:
        """Get all item names"""
        return list(self.item_map.values())
    
    def search_items(self, query: str, limit: int = 10) -> List[str]:
        """Search items by name"""
        query_lower = query.lower()
        matches = [name for name in self.item_map.values() 
                  if query_lower in name.lower()]
        return matches[:limit]
