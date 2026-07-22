"""Rate limiting middleware to prevent API abuse."""

import logging
import time
from collections import defaultdict
from typing import Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger("app.middleware.rate_limiter")


class RateLimiter:
    """Simple in-memory rate limiter using token bucket algorithm."""
    
    def __init__(
        self,
        requests_per_minute: int = 60,
        cleanup_interval: int = 300,
    ):
        self.requests_per_minute = requests_per_minute
        self.cleanup_interval = cleanup_interval
        self.request_times: dict[str, list[float]] = defaultdict(list)
        self.last_cleanup = time.time()

    def is_allowed(self, client_id: str) -> bool:
        """Check if client is within rate limit."""
        now = time.time()
        
        # Cleanup old entries periodically
        if now - self.last_cleanup > self.cleanup_interval:
            self._cleanup_old_entries(now)

        # Get request times for this client
        request_times = self.request_times[client_id]
        
        # Remove requests older than 1 minute
        minute_ago = now - 60
        request_times[:] = [t for t in request_times if t > minute_ago]

        # Check if within limit
        if len(request_times) >= self.requests_per_minute:
            return False

        # Add current request
        request_times.append(now)
        return True

    def _cleanup_old_entries(self, now: float) -> None:
        """Remove clients with no recent activity."""
        minute_ago = now - 60
        clients_to_remove = []
        
        for client_id, times in self.request_times.items():
            # Keep only recent times
            recent_times = [t for t in times if t > minute_ago]
            if not recent_times:
                clients_to_remove.append(client_id)
            else:
                self.request_times[client_id] = recent_times
        
        # Remove inactive clients
        for client_id in clients_to_remove:
            del self.request_times[client_id]
        
        self.last_cleanup = now


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for rate limiting."""
    
    def __init__(
        self,
        app,
        requests_per_minute: int = 100,
        excluded_paths: list[str] | None = None,
    ):
        super().__init__(app)
        self.limiter = RateLimiter(requests_per_minute=requests_per_minute)
        self.excluded_paths = excluded_paths or []

    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        """Apply rate limiting to requests."""
        # Skip rate limiting for excluded paths
        if any(request.url.path.startswith(path) for path in self.excluded_paths):
            return await call_next(request)

        # Get client identifier (IP address or user ID)
        client_id = self._get_client_id(request)

        # Check rate limit
        if not self.limiter.is_allowed(client_id):
            logger.warning(f"Rate limit exceeded for client: {client_id}")
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "message": "Rate limit exceeded. Maximum 100 requests per minute.",
                    "error": "rate_limit_exceeded",
                },
            )

        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.limiter.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(
            max(0, self.limiter.requests_per_minute - len(
                self.limiter.request_times.get(client_id, [])
            ))
        )
        
        return response

    @staticmethod
    def _get_client_id(request: Request) -> str:
        """Extract client identifier from request."""
        # Prefer X-Forwarded-For header (behind proxy)
        if "X-Forwarded-For" in request.headers:
            return request.headers["X-Forwarded-For"].split(",")[0].strip()
        
        # Fall back to direct client IP
        if request.client:
            return request.client.host
        
        # Last resort
        return "unknown"
