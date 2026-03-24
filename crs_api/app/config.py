from pydantic_settings import BaseSettings
from typing import Optional, Literal
from functools import lru_cache


class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Conversational Recommender System"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1
    
    # LLM Provider Settings
    LLM_PROVIDER: Literal["openai", "ollama"] = "openai"  # Default to openai for backward compatibility
    USE_MOCK_LLM: bool = False  # Fallback to mock if provider fails
    
    # OpenAI Settings
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_MAX_TOKENS: int = 500
    
    # Ollama Settings
    OLLAMA_MODEL: str = "mistral"  # Options: mistral, llama2, phi, etc.
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_TEMPERATURE: float = 0.7
    OLLAMA_MAX_TOKENS: int = 500
    
    # Dataset Settings
    DATA_PATH: str = "./data"
    MOVIE_DOMAIN: str = "Movie"
    MAX_HISTORY_TURNS: int = 10
    MAX_RECOMMENDATIONS: int = 10
    
    # RAG Settings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    VECTOR_DIM: int = 384
    RETRIEVAL_K: int = 5
    SIMILARITY_THRESHOLD: float = 0.3
    
    # Cache Settings
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL: int = 3600  # 1 hour
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_DAY: int = 1000
    
    # Performance
    BATCH_SIZE: int = 100
    ASYNC_WORKERS: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
