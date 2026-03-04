"""Rate limiting middleware."""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class RateLimiter(BaseHTTPMiddleware):
    """
    Rate limiting middleware.
    Limits requests to 100 per minute per user/IP.
    """
    
    def __init__(self, app, requests_per_minute: int = 100):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts = defaultdict(list)
        self.cleanup_interval = timedelta(minutes=5)
        self.last_cleanup = datetime.utcnow()
    
    def _get_client_identifier(self, request: Request) -> str:
        """Get unique identifier for the client."""
        # Try to get user ID from request state (set by auth middleware)
        if hasattr(request.state, "user") and request.state.user:
            return f"user:{request.state.user.get('user_id', 'unknown')}"
        
        # Fall back to IP address
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return f"ip:{forwarded.split(',')[0].strip()}"
        
        client_host = request.client.host if request.client else "unknown"
        return f"ip:{client_host}"
    
    def _cleanup_old_requests(self):
        """Remove old request timestamps to prevent memory bloat."""
        now = datetime.utcnow()
        if now - self.last_cleanup > self.cleanup_interval:
            cutoff = now - timedelta(minutes=1)
            for client_id in list(self.request_counts.keys()):
                self.request_counts[client_id] = [
                    ts for ts in self.request_counts[client_id]
                    if ts > cutoff
                ]
                if not self.request_counts[client_id]:
                    del self.request_counts[client_id]
            self.last_cleanup = now
    
    async def dispatch(self, request: Request, call_next):
        """Process the request with rate limiting."""
        # Skip rate limiting for health check and root endpoints
        if request.url.path in ["/", "/health", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        client_id = self._get_client_identifier(request)
        now = datetime.utcnow()
        
        # Cleanup old requests periodically
        self._cleanup_old_requests()
        
        # Get request timestamps for this client in the last minute
        cutoff = now - timedelta(minutes=1)
        recent_requests = [
            ts for ts in self.request_counts[client_id]
            if ts > cutoff
        ]
        
        # Check if rate limit exceeded
        if len(recent_requests) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for {client_id}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate Limit Exceeded",
                    "message": f"Too many requests. Limit is {self.requests_per_minute} requests per minute.",
                    "retry_after": 60
                }
            )
        
        # Add current request timestamp
        recent_requests.append(now)
        self.request_counts[client_id] = recent_requests
        
        # Add rate limit headers to response
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(
            self.requests_per_minute - len(recent_requests)
        )
        response.headers["X-RateLimit-Reset"] = str(
            int((cutoff + timedelta(minutes=1)).timestamp())
        )
        
        return response
