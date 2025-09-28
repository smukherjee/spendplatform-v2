"""
High-performance async Redis cache implementation
"""
import redis.asyncio as redis
import pickle
import json
from typing import Any, Optional, Union
import os
import logging

logger = logging.getLogger(__name__)

class AsyncRedisCache:
    """Production-ready async Redis cache with error handling"""
    
    def __init__(self):
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_client = redis.from_url(
            redis_url,
            encoding="utf-8",
            decode_responses=False,  # Handle binary data
            max_connections=20,
            retry_on_timeout=True,
            socket_keepalive=True,
            health_check_interval=30,
            socket_connect_timeout=5,
            socket_timeout=5,
        )
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache with error handling"""
        try:
            value = await self.redis_client.get(key)
            if value is None:
                return None
            return pickle.loads(value)
        except Exception as e:
            logger.warning(f"Cache get error for key {key}: {str(e)}")
            return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        expire: Optional[int] = None
    ) -> bool:
        """Set value in cache with TTL"""
        try:
            serialized_value = pickle.dumps(value)
            if expire:
                return await self.redis_client.setex(key, expire, serialized_value)
            else:
                return await self.redis_client.set(key, serialized_value)
        except Exception as e:
            logger.warning(f"Cache set error for key {key}: {str(e)}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            return bool(await self.redis_client.delete(key))
        except Exception as e:
            logger.warning(f"Cache delete error for key {key}: {str(e)}")
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                return await self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.warning(f"Cache delete pattern error for {pattern}: {str(e)}")
            return 0
    
    async def health_check(self) -> bool:
        """Check Redis connection health"""
        try:
            await self.redis_client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis health check failed: {str(e)}")
            return False

# Global cache instance
redis_cache = AsyncRedisCache()