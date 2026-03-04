"""Low-bandwidth mode service for optimizing content delivery."""
import gzip
from typing import Dict, Any, Optional


class LowBandwidthService:
    """Service for handling low-bandwidth mode optimizations."""
    
    # Page size limit for low-bandwidth mode (in bytes)
    MAX_PAGE_SIZE = 100 * 1024  # 100KB
    
    @staticmethod
    def compress_text(text: str) -> bytes:
        """Compress text content using gzip.
        
        Args:
            text: Text content to compress
            
        Returns:
            Compressed bytes
        """
        return gzip.compress(text.encode('utf-8'))
    
    @staticmethod
    def decompress_text(compressed: bytes) -> str:
        """Decompress gzip-compressed text.
        
        Args:
            compressed: Compressed bytes
            
        Returns:
            Decompressed text string
        """
        return gzip.decompress(compressed).decode('utf-8')
    
    @staticmethod
    def strip_heavy_content(data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove or reduce heavy content for low-bandwidth mode.
        
        This includes:
        - Removing image URLs
        - Truncating long descriptions
        - Removing non-essential fields
        
        Args:
            data: Original data dictionary
            
        Returns:
            Optimized data dictionary
        """
        optimized = data.copy()
        
        # Truncate long descriptions
        if 'description' in optimized and len(optimized['description']) > 200:
            optimized['description'] = optimized['description'][:200] + "..."
        
        # Remove image fields if present
        if 'image_url' in optimized:
            del optimized['image_url']
        if 'banner_url' in optimized:
            del optimized['banner_url']
        
        # Remove non-essential metadata
        if 'metadata' in optimized:
            del optimized['metadata']
        
        return optimized
    
    @staticmethod
    def optimize_opportunity_list(
        opportunities: list[Dict[str, Any]],
        low_bandwidth: bool = False
    ) -> list[Dict[str, Any]]:
        """Optimize opportunity list for low-bandwidth mode.
        
        Args:
            opportunities: List of opportunity dictionaries
            low_bandwidth: Whether to apply low-bandwidth optimizations
            
        Returns:
            Optimized opportunity list
        """
        if not low_bandwidth:
            return opportunities
        
        optimized = []
        for opp in opportunities:
            optimized_opp = {
                'id': opp.get('id'),
                'title': opp.get('title'),
                'type': opp.get('type'),
                'deadline': opp.get('deadline'),
                'application_link': opp.get('application_link'),
                # Truncate description
                'description': opp.get('description', '')[:150] + "..." if len(opp.get('description', '')) > 150 else opp.get('description', '')
            }
            optimized.append(optimized_opp)
        
        return optimized
    
    @staticmethod
    def calculate_response_size(data: Any) -> int:
        """Calculate approximate size of response data in bytes.
        
        Args:
            data: Response data (dict, list, or string)
            
        Returns:
            Approximate size in bytes
        """
        import json
        
        if isinstance(data, (dict, list)):
            json_str = json.dumps(data)
            return len(json_str.encode('utf-8'))
        elif isinstance(data, str):
            return len(data.encode('utf-8'))
        else:
            return len(str(data).encode('utf-8'))
    
    @staticmethod
    def is_within_size_limit(data: Any, limit: int = MAX_PAGE_SIZE) -> bool:
        """Check if response data is within size limit.
        
        Args:
            data: Response data
            limit: Size limit in bytes (default: 100KB)
            
        Returns:
            True if within limit, False otherwise
        """
        size = LowBandwidthService.calculate_response_size(data)
        return size <= limit
    
    @staticmethod
    def get_low_bandwidth_headers() -> Dict[str, str]:
        """Get HTTP headers for low-bandwidth responses.
        
        Returns:
            Dictionary of headers
        """
        return {
            'Content-Encoding': 'gzip',
            'Cache-Control': 'public, max-age=3600',  # Cache for 1 hour
            'X-Low-Bandwidth-Mode': 'enabled'
        }
