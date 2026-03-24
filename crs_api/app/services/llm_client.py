"""
Abstract LLM Client supporting multiple providers
- OpenAI
- Ollama (local)
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import aiohttp
import openai
import logging
import asyncio
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients"""
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """Generate response from LLM"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if LLM service is available"""
        pass


class OpenAIClient(BaseLLMClient):
    """OpenAI API Client"""
    
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """Generate using OpenAI"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=30.0
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check if OpenAI API is available"""
        try:
            # Simple models list check
            await self.client.models.list()
            return True
        except Exception as e:
            logger.error(f"OpenAI health check failed: {e}")
            return False


class OllamaClient(BaseLLMClient):
    """Local Ollama Client"""
    
    def __init__(self):
        self.base_url = settings.OLLAMA_URL
        self.model = settings.OLLAMA_MODEL
        self._session: Optional[aiohttp.ClientSession] = None
        print(f"🔧 Initialized OllamaClient with URL: {self.base_url}, Model: {self.model}")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create session"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """Generate using Ollama"""
        session = await self._get_session()
        
        # Combine system prompt if provided
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        print(f"📤 Sending to Ollama: {self.base_url}/api/generate")
        print(f"   Model: {self.model}")
        print(f"   Prompt length: {len(full_prompt)} chars")
        
        try:
            async with session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                print(f"📥 Response status: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    generated_text = result.get("response", "")
                    print(f"✅ Generated {len(generated_text)} chars")
                    return generated_text
                else:
                    error_text = await response.text()
                    print(f"❌ Ollama error: {error_text}")
                    raise Exception(f"Ollama API error: {response.status}")
                    
        except aiohttp.ClientConnectorError:
            print(f"❌ Cannot connect to Ollama at {self.base_url}")
            print(f"   Make sure Ollama is running: ollama serve")
            raise Exception("Ollama service not available")
            
        except asyncio.TimeoutError:
            print(f"❌ Ollama request timeout")
            raise Exception("Ollama request timeout")
            
        except Exception as e:
            print(f"❌ Ollama generation error: {e}")
            raise
    
    async def close(self):
        """Close session"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def health_check(self) -> bool:
        """Check if Ollama is available and model is loaded"""
        session = await self._get_session()
        try:
            print(f"🔍 Health check: {self.base_url}/api/tags")
            async with session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    models = [m.get("name", "") for m in data.get("models", [])]
                    print(f"   Available models: {models}")
                    if any(self.model in m for m in models):
                        print(f"   ✅ Model '{self.model}' found")
                        return True
                    else:
                        print(f"   ❌ Model '{self.model}' not found")
                        return False
                return False
        except Exception as e:
            print(f"   ❌ Health check failed: {e}")
            return False


class MockLLMClient(BaseLLMClient):
    """Mock client for testing (no API calls)"""
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """Return mock recommendations"""
        return """Based on your preferences, here are my recommendations:

1. The Matrix - A mind-bending sci-fi classic with incredible action
2. Inception - Complex narrative with stunning visuals
3. Interstellar - Combines science with emotional depth
4. John Wick - Stylish action with great choreography
5. The Bourne Identity - Smart spy thriller with intense action

These movies match your interest in action, sci-fi, and intelligent storytelling."""
    
    async def health_check(self) -> bool:
        """Mock is always healthy"""
        return True


def get_llm_client() -> BaseLLMClient:
    """Factory function to get appropriate LLM client"""
    
    # Use mock if explicitly set
    if settings.USE_MOCK_LLM:
        logger.info("Using Mock LLM Client")
        return MockLLMClient()
    
    # Use configured provider
    if settings.LLM_PROVIDER == "openai":
        logger.info("Using OpenAI Client")
        return OpenAIClient()
    elif settings.LLM_PROVIDER == "ollama":
        logger.info(f"Using Ollama Client (model: {settings.OLLAMA_MODEL})")
        return OllamaClient()
    else:
        logger.warning(f"Unknown LLM provider: {settings.LLM_PROVIDER}, falling back to OpenAI")
        return OpenAIClient()
