"""Middleware for handling low-bandwidth mode."""
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import gzip
import json

from services.low_bandwidth_service import LowBandwidthService


class LowBandwidthMiddleware(BaseHTTPMiddleware):
    """Middleware to handle low-bandwidth mode optimizations."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.low_bandwidth_service = LowBandwidthService()
    
    async def dispatch(self, request: Request, call_next):
        """Process request and apply low-bandwidth optimizations if needed.
        
        Args:
            request: Incoming request
            call_next: Next middleware/handler
            
        Returns:
            Response (potentially optimized)
        """
        # Check if low-bandwidth mode is requested
        low_bandwidth = request.headers.get('X-Low-Bandwidth-Mode') == 'true'
        
        # Process request
        response = await call_next(request)
        
        # Apply optimizations if low-bandwidth mode is enabled
        if low_bandwidth and isinstance(response, JSONResponse):
            # Get response body
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            
            # Parse JSON
            try:
                data = json.loads(body.decode('utf-8'))
                
                # Apply optimizations
                if isinstance(data, list):
                    data = self.low_bandwidth_service.optimize_opportunity_list(data, True)
                elif isinstance(data, dict):
                    data = self.low_bandwidth_service.strip_heavy_content(data)
                
                # Compress response
                compressed_body = gzip.compress(json.dumps(data).encode('utf-8'))
                
                # Create new response with compressed data
                headers = dict(response.headers)
                headers.update(self.low_bandwidth_service.get_low_bandwidth_headers())
                
                return Response(
                    content=compressed_body,
                    status_code=response.status_code,
                    headers=headers,
                    media_type="application/json"
                )
            
            except Exception as e:
                # If optimization fails, return original response
                print(f"Low-bandwidth optimization failed: {str(e)}")
                return response
        
        return response
