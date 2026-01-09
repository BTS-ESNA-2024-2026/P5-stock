"""
Redis Cache Service for P5-Stock
Issue #35: Scalabilité et caching

Features:
- Database query caching
- Session caching
- Cache invalidation logic
- Monitoring cache hit rates
"""

import json
import hashlib
import pickle
from functools import wraps
from typing import Optional, Any, Callable, Union
from datetime import timedelta

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from flask import Flask, g, current_app


class CacheService:
    """
    Redis-based caching service for P5-Stock.
    Implements caching strategies for performance optimization.
    """
    
    # Cache key prefixes
    PREFIX_QUERY = "cache:query:"
    PREFIX_SESSION = "cache:session:"
    PREFIX_USER = "cache:user:"
    PREFIX_ASSET = "cache:asset:"
    
    # Default TTL values (in seconds)
    TTL_SHORT = 60          # 1 minute
    TTL_MEDIUM = 300        # 5 minutes
    TTL_LONG = 3600         # 1 hour
    TTL_SESSION = 1800      # 30 minutes
    
    def __init__(self, app: Optional[Flask] = None):
        self.app = app
        self.redis: Optional[Any] = None
        self._local_cache: dict = {}
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0
        }
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask) -> None:
        """Initialize with Flask application."""
        self.app = app
        
        # Configuration
        app.config.setdefault('REDIS_URL', 'redis://localhost:6379/0')
        app.config.setdefault('CACHE_ENABLED', True)
        app.config.setdefault('CACHE_DEFAULT_TTL', self.TTL_MEDIUM)
        
        # Connect to Redis
        if REDIS_AVAILABLE:
            try:
                self.redis = redis.from_url(
                    app.config['REDIS_URL'],
                    decode_responses=False,  # We handle encoding ourselves
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
                # Test connection
                self.redis.ping()
                app.logger.info("Redis cache connected successfully")
            except (redis.ConnectionError, redis.TimeoutError) as e:
                app.logger.warning(f"Redis connection failed, using local cache: {e}")
                self.redis = None
        else:
            app.logger.warning("Redis not installed, using local cache")
        
        # Register in extensions
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['cache'] = self
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a cache key from arguments."""
        key_data = json.dumps({'args': args, 'kwargs': kwargs}, sort_keys=True)
        key_hash = hashlib.sha256(key_data.encode()).hexdigest()[:16]
        return f"{prefix}{key_hash}"
    
    def _serialize(self, value: Any) -> bytes:
        """Serialize value for storage."""
        return pickle.dumps(value)
    
    def _deserialize(self, data: bytes) -> Any:
        """Deserialize value from storage."""
        return pickle.loads(data)
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        if not current_app.config.get('CACHE_ENABLED', True):
            return None
        
        try:
            if self.redis:
                data = self.redis.get(key)
                if data:
                    self._stats['hits'] += 1
                    return self._deserialize(data)
            else:
                if key in self._local_cache:
                    self._stats['hits'] += 1
                    return self._local_cache[key]
        except Exception as e:
            current_app.logger.error(f"Cache get error: {e}")
        
        self._stats['misses'] += 1
        return None
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds
            
        Returns:
            True if successful
        """
        if not current_app.config.get('CACHE_ENABLED', True):
            return False
        
        if ttl is None:
            ttl = current_app.config.get('CACHE_DEFAULT_TTL', self.TTL_MEDIUM)
        
        try:
            serialized = self._serialize(value)
            
            if self.redis:
                self.redis.setex(key, ttl, serialized)
            else:
                self._local_cache[key] = value
            
            self._stats['sets'] += 1
            return True
        except Exception as e:
            current_app.logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if successful
        """
        try:
            if self.redis:
                self.redis.delete(key)
            else:
                self._local_cache.pop(key, None)
            
            self._stats['deletes'] += 1
            return True
        except Exception as e:
            current_app.logger.error(f"Cache delete error: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern.
        
        Args:
            pattern: Redis pattern (e.g., "cache:user:*")
            
        Returns:
            Number of keys deleted
        """
        deleted = 0
        try:
            if self.redis:
                cursor = 0
                while True:
                    cursor, keys = self.redis.scan(cursor, match=pattern, count=100)
                    if keys:
                        deleted += self.redis.delete(*keys)
                    if cursor == 0:
                        break
            else:
                keys_to_delete = [
                    k for k in self._local_cache
                    if k.startswith(pattern.replace('*', ''))
                ]
                for key in keys_to_delete:
                    del self._local_cache[key]
                    deleted += 1
        except Exception as e:
            current_app.logger.error(f"Cache delete_pattern error: {e}")
        
        return deleted
    
    def clear(self) -> bool:
        """Clear all cache entries."""
        try:
            if self.redis:
                self.redis.flushdb()
            else:
                self._local_cache.clear()
            return True
        except Exception as e:
            current_app.logger.error(f"Cache clear error: {e}")
            return False
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        stats = self._stats.copy()
        total = stats['hits'] + stats['misses']
        stats['hit_rate'] = (stats['hits'] / total * 100) if total > 0 else 0
        
        if self.redis:
            try:
                info = self.redis.info('memory')
                stats['memory_used'] = info.get('used_memory_human', 'N/A')
            except Exception:
                stats['memory_used'] = 'N/A'
        
        return stats
    
    # ============================================
    # Specialized caching methods
    # ============================================
    
    def cache_query(
        self,
        query_id: str,
        result: Any,
        ttl: int = TTL_MEDIUM
    ) -> bool:
        """Cache a database query result."""
        key = f"{self.PREFIX_QUERY}{query_id}"
        return self.set(key, result, ttl)
    
    def get_cached_query(self, query_id: str) -> Optional[Any]:
        """Get cached database query result."""
        key = f"{self.PREFIX_QUERY}{query_id}"
        return self.get(key)
    
    def invalidate_asset_cache(self, asset_id: int) -> int:
        """Invalidate all cache entries for an asset."""
        pattern = f"{self.PREFIX_ASSET}{asset_id}:*"
        return self.delete_pattern(pattern)
    
    def invalidate_user_cache(self, user_id: int) -> int:
        """Invalidate all cache entries for a user."""
        pattern = f"{self.PREFIX_USER}{user_id}:*"
        return self.delete_pattern(pattern)


def cached(
    ttl: int = CacheService.TTL_MEDIUM,
    prefix: str = "cache:func:",
    key_func: Optional[Callable] = None
) -> Callable:
    """
    Decorator to cache function results.
    
    Args:
        ttl: Cache TTL in seconds
        prefix: Cache key prefix
        key_func: Custom function to generate cache key
    
    Usage:
        @cached(ttl=300)
        def get_expensive_data(user_id):
            return expensive_query(user_id)
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Get cache service
            cache = current_app.extensions.get('cache')
            if not cache:
                return f(*args, **kwargs)
            
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                key_data = json.dumps({
                    'func': f.__name__,
                    'args': str(args),
                    'kwargs': str(kwargs)
                }, sort_keys=True)
                cache_key = f"{prefix}{hashlib.sha256(key_data.encode()).hexdigest()[:16]}"
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Call function and cache result
            result = f(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator


def invalidate_cache(*patterns: str) -> Callable:
    """
    Decorator to invalidate cache after function execution.
    
    Args:
        patterns: Cache key patterns to invalidate
    
    Usage:
        @invalidate_cache("cache:user:*", "cache:query:*")
        def update_user(user_id, data):
            # Update user...
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs):
            result = f(*args, **kwargs)
            
            # Invalidate cache
            cache = current_app.extensions.get('cache')
            if cache:
                for pattern in patterns:
                    cache.delete_pattern(pattern)
            
            return result
        return wrapper
    return decorator
