"""Redis caching service."""
import json
import logging
from typing import Optional, Any
from datetime import timedelta

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

from config import config

logger = logging.getLogger(__name__)


class CacheService:
    """Service for caching data using Redis."""
    
    def __init__(self):
        self.redis_client = None
        self.enabled = False
        
        if REDIS_AVAILABLE:
            try:
                self.redis_client = redis.from_url(
                    config.REDIS_URL,
                    decode_responses=True,
                    socket_connect_timeout=5
                )
                # Test connection
                self.redis_client.ping()
                self.enabled = True
                logger.info("Redis cache enabled")
            except Exception as e:
                logger.warning(f"Redis not available, caching disabled: {str(e)}")
                self.enabled = False
        else:
            logger.warning("Redis library not installed, caching disabled")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        if not self.enabled:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {str(e)}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
            ttl: Time to live in seconds (optional)
        """
        if not self.enabled:
            return
        
        try:
            serialized = json.dumps(value)
            if ttl:
                self.redis_client.setex(key, ttl, serialized)
            else:
                self.redis_client.set(key, serialized)
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {str(e)}")
    
    def delete(self, key: str):
        """
        Delete value from cache.
        
        Args:
            key: Cache key to delete
        """
        if not self.enabled:
            return
        
        try:
            self.redis_client.delete(key)
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {str(e)}")
    
    def delete_pattern(self, pattern: str):
        """
        Delete all keys matching a pattern.
        
        Args:
            pattern: Pattern to match (e.g., "user:*")
        """
        if not self.enabled:
            return
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
        except Exception as e:
            logger.error(f"Error deleting cache pattern {pattern}: {str(e)}")
    
    def clear_all(self):
        """Clear all cache entries."""
        if not self.enabled:
            return
        
        try:
            self.redis_client.flushdb()
            logger.info("Cache cleared")
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")


# Cache key generators
class CacheKeys:
    """Cache key generators for different data types."""
    
    @staticmethod
    def user_profile(user_id: str) -> str:
        """Generate cache key for user profile."""
        return f"profile:{user_id}"
    
    @staticmethod
    def opportunities_list(filters: dict = None) -> str:
        """Generate cache key for opportunity listings."""
        if filters:
            filter_str = json.dumps(filters, sort_keys=True)
            return f"opportunities:list:{hash(filter_str)}"
        return "opportunities:list:all"
    
    @staticmethod
    def opportunity_detail(opportunity_id: str) -> str:
        """Generate cache key for opportunity details."""
        return f"opportunity:{opportunity_id}"
    
    @staticmethod
    def recommendations(user_id: str) -> str:
        """Generate cache key for user recommendations."""
        return f"recommendations:{user_id}"
    
    @staticmethod
    def educational_content(content_type: str, content_id: str) -> str:
        """Generate cache key for educational content."""
        return f"content:{content_type}:{content_id}"
    
    @staticmethod
    def glossary() -> str:
        """Generate cache key for glossary."""
        return "content:glossary:all"
    
    @staticmethod
    def guides() -> str:
        """Generate cache key for guides."""
        return "content:guides:all"


# Cache TTL constants (in seconds)
class CacheTTL:
    """Cache TTL constants."""
    PROFILE = 15 * 60  # 15 minutes
    OPPORTUNITIES = 5 * 60  # 5 minutes
    RECOMMENDATIONS = 60 * 60  # 1 hour
    EDUCATIONAL_CONTENT = None  # Indefinite
    GLOSSARY = None  # Indefinite
    GUIDES = None  # Indefinite


# Global cache instance
cache = CacheService()
