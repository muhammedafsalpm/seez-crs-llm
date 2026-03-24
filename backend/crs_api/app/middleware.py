import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict
import logging
from collections import defaultdict
from app.config import get_settings
from app.exceptions import RateLimitException

settings = get_settings()
logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""
    def __init__(self, app):
        super().__init__(app)
        self.requests: Dict[str, list] = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        
        # Check rate limit
        if await self.is_rate_limited(client_ip):
            raise RateLimitException()
        
        response = await call_next(request)
        return response
    
    async def is_rate_limited(self, client_ip: str) -> bool:
        """Check if client is rate limited"""
        # Simple in-memory rate limiting (replace with Redis in production)
        now = time.time()
        window = 60  # 1 minute
        limit = settings.RATE_LIMIT_PER_MINUTE
        
        requests = self.requests[client_ip]
        requests = [t for t in requests if now - t < window]
        self.requests[client_ip] = requests
        
        if len(requests) >= limit:
            return True
        
        requests.append(now)
        return False


class LoggingMiddleware(BaseHTTPMiddleware):
    """Request logging middleware"""
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url.path}")
        
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        logger.info(
            f"Response: {response.status_code} - "
            f"Time: {process_time:.3f}s"
        )
        
        response.headers["X-Process-Time"] = str(process_time)
        return response
