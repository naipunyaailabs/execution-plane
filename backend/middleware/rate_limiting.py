"""
Rate Limiting Middleware for FastAPI

Provides configurable rate limiting per user/IP/endpoint to prevent API abuse.
Supports multiple storage backends (Redis, in-memory) and flexible rate limit strategies.
"""

import time
import hashlib
from typing import Optional, Dict, Tuple
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter with configurable limits and storage backend"""
    
    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        storage_backend: str = "memory",  # "memory" or "redis"
        redis_url: Optional[str] = None
    ):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.storage_backend = storage_backend
        
        # In-memory storage (fallback)
        self._memory_store: Dict[str, list] = {}
        
        # Redis storage (if available)
        self._redis_client = None
        if storage_backend == "redis" and redis_url:
            try:
                import redis
                self._redis_client = redis.from_url(redis_url, decode_responses=True)
                logger.info("Rate limiter using Redis storage")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis for rate limiting: {e}. Using memory storage.")
                self.storage_backend = "memory"
    
    def _get_client_identifier(self, request: Request) -> str:
        """Get unique identifier for rate limiting (IP or user ID)"""
        # Try to get user ID from JWT token or header
        user_id = request.headers.get("X-User-ID")
        if user_id:
            return f"user:{user_id}"
        
        # Fall back to IP address
        client_ip = request.client.host if request.client else "unknown"
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP in the chain
            client_ip = forwarded_for.split(",")[0].strip()
        
        return f"ip:{client_ip}"
    
    def _get_key(self, identifier: str, endpoint: str, window: str) -> str:
        """Generate storage key for rate limit tracking"""
        key_string = f"ratelimit:{identifier}:{endpoint}:{window}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _check_limit_memory(self, key: str, limit: int, window_seconds: int) -> Tuple[bool, int, int]:
        """Check rate limit using in-memory storage"""
        current_time = time.time()
        
        if key not in self._memory_store:
            self._memory_store[key] = []
        
        # Remove old entries outside the window
        window_start = current_time - window_seconds
        self._memory_store[key] = [
            timestamp for timestamp in self._memory_store[key]
            if timestamp > window_start
        ]
        
        # Check if limit exceeded
        request_count = len(self._memory_store[key])
        if request_count >= limit:
            # Calculate reset time
            oldest_request = min(self._memory_store[key]) if self._memory_store[key] else current_time
            reset_time = int(oldest_request + window_seconds)
            return False, request_count, reset_time
        
        # Add current request
        self._memory_store[key].append(current_time)
        return True, request_count + 1, int(current_time + window_seconds)
    
    def _check_limit_redis(self, key: str, limit: int, window_seconds: int) -> Tuple[bool, int, int]:
        """Check rate limit using Redis storage"""
        if not self._redis_client:
            # Fallback to memory
            return self._check_limit_memory(key, limit, window_seconds)
        
        try:
            current_time = int(time.time())
            window_start = current_time - window_seconds
            
            # Use Redis sorted set for sliding window
            pipe = self._redis_client.pipeline()
            pipe.zremrangebyscore(key, 0, window_start)  # Remove old entries
            pipe.zcard(key)  # Count current entries
            pipe.zadd(key, {str(current_time): current_time})  # Add current request
            pipe.expire(key, window_seconds)  # Set expiration
            results = pipe.execute()
            
            request_count = results[1]
            if request_count >= limit:
                # Get oldest request to calculate reset time
                oldest = self._redis_client.zrange(key, 0, 0, withscores=True)
                if oldest:
                    reset_time = int(oldest[0][1] + window_seconds)
                else:
                    reset_time = current_time + window_seconds
                return False, request_count, reset_time
            
            return True, request_count + 1, current_time + window_seconds
            
        except Exception as e:
            logger.error(f"Redis rate limit check failed: {e}. Falling back to memory.")
            return self._check_limit_memory(key, limit, window_seconds)
    
    def check_rate_limit(
        self,
        request: Request,
        endpoint: Optional[str] = None
    ) -> Tuple[bool, Dict[str, int]]:
        """
        Check if request is within rate limits
        
        Returns:
            Tuple of (is_allowed, rate_limit_info)
            rate_limit_info contains: limit, remaining, reset
        """
        identifier = self._get_client_identifier(request)
        endpoint = endpoint or request.url.path
        
        # Check per-minute limit
        minute_key = self._get_key(identifier, endpoint, "minute")
        allowed_minute, count_minute, reset_minute = (
            self._check_limit_redis(minute_key, self.requests_per_minute, 60)
            if self.storage_backend == "redis"
            else self._check_limit_memory(minute_key, self.requests_per_minute, 60)
        )
        
        # Check per-hour limit
        hour_key = self._get_key(identifier, endpoint, "hour")
        allowed_hour, count_hour, reset_hour = (
            self._check_limit_redis(hour_key, self.requests_per_hour, 3600)
            if self.storage_backend == "redis"
            else self._check_limit_memory(hour_key, self.requests_per_hour, 3600)
        )
        
        # Request is allowed if both limits are not exceeded
        is_allowed = allowed_minute and allowed_hour
        
        # Determine which limit applies (the stricter one)
        if not allowed_minute:
            limit = self.requests_per_minute
            remaining = max(0, limit - count_minute)
            reset = reset_minute
        elif not allowed_hour:
            limit = self.requests_per_hour
            remaining = max(0, limit - count_hour)
            reset = reset_hour
        else:
            # Both limits OK, use minute limit for info
            limit = self.requests_per_minute
            remaining = limit - count_minute
            reset = reset_minute
        
        rate_limit_info = {
            "limit": limit,
            "remaining": remaining,
            "reset": reset
        }
        
        return is_allowed, rate_limit_info


class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for rate limiting"""
    
    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        storage_backend: str = "memory",
        redis_url: Optional[str] = None,
        exempt_paths: Optional[list] = None
    ):
        super().__init__(app)
        self.rate_limiter = RateLimiter(
            requests_per_minute=requests_per_minute,
            requests_per_hour=requests_per_hour,
            storage_backend=storage_backend,
            redis_url=redis_url
        )
        self.exempt_paths = exempt_paths or ["/health", "/docs", "/openapi.json", "/redoc"]
    
    def is_exempt(self, path: str) -> bool:
        """Check if path is exempt from rate limiting"""
        return any(path.startswith(exempt) for exempt in self.exempt_paths)
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for exempt paths
        if self.is_exempt(request.url.path):
            return await call_next(request)
        
        # Check rate limit
        is_allowed, rate_limit_info = self.rate_limiter.check_rate_limit(request)
        
        if not is_allowed:
            # Rate limit exceeded
            response = Response(
                content=f'{{"detail": "Rate limit exceeded. Limit: {rate_limit_info["limit"]}, Reset at: {rate_limit_info["reset"]}"}}',
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                media_type="application/json"
            )
            response.headers["X-RateLimit-Limit"] = str(rate_limit_info["limit"])
            response.headers["X-RateLimit-Remaining"] = str(rate_limit_info["remaining"])
            response.headers["X-RateLimit-Reset"] = str(rate_limit_info["reset"])
            response.headers["Retry-After"] = str(rate_limit_info["reset"] - int(time.time()))
            return response
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers to response
        response.headers["X-RateLimit-Limit"] = str(rate_limit_info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(rate_limit_info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(rate_limit_info["reset"])
        
        return response

