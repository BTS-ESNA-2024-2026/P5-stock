"""
Rate Limiter Middleware for P5-Stock
Issue #28: DDoS protection (rate limiting 10 req/s per IP)

Uses Redis for distributed rate limiting across multiple instances.
Implements sliding window algorithm for accuracy.
"""

import time
import hashlib
from functools import wraps
from typing import Optional, Callable, Any, Tuple

from flask import Flask, request, g, abort, Response, jsonify


class RateLimiter:
    """
    Redis-based rate limiter using sliding window algorithm.
    Provides DDoS protection with configurable limits.
    """
    
    def __init__(
        self,
        app: Optional[Flask] = None,
        redis_client: Optional[Any] = None,
        default_limit: int = 10,
        default_window: int = 1
    ):
        """
        Initialize rate limiter.
        
        Args:
            app: Flask application
            redis_client: Redis client instance
            default_limit: Default requests per window
            default_window: Default window size in seconds
        """
        self.app = app
        self.redis = redis_client
        self.default_limit = default_limit
        self.default_window = default_window
        self._fallback_storage: dict = {}
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask) -> None:
        """Initialize with Flask application."""
        self.app = app
        
        # Configuration
        app.config.setdefault('RATELIMIT_ENABLED', True)
        app.config.setdefault('RATELIMIT_DEFAULT', '10/second')
        app.config.setdefault('RATELIMIT_STORAGE_URL', 'redis://localhost:6379')
        app.config.setdefault('RATELIMIT_HEADERS_ENABLED', True)
        
        # Register before_request handler
        app.before_request(self._check_rate_limit)
        
        # Register after_request handler for headers
        app.after_request(self._add_rate_limit_headers)
        
        # Store in extensions
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['rate_limiter'] = self
    
    def _get_client_key(self) -> str:
        """Generate unique key for client."""
        # Get client IP
        client_ip = self._get_client_ip()
        
        # Optional: Include user ID for authenticated users
        user_id = getattr(g, 'user_id', None)
        
        if user_id:
            key_data = f"{client_ip}:{user_id}"
        else:
            key_data = client_ip
        
        # Hash for consistency
        return hashlib.sha256(key_data.encode()).hexdigest()[:16]
    
    def _get_client_ip(self) -> str:
        """Get real client IP, handling proxy headers."""
        if 'X-Forwarded-For' in request.headers:
            return request.headers['X-Forwarded-For'].split(',')[0].strip()
        if 'X-Real-IP' in request.headers:
            return request.headers['X-Real-IP']
        return request.remote_addr or '127.0.0.1'
    
    def _check_rate_limit(self) -> Optional[Response]:
        """Check if request exceeds rate limit."""
        if not self.app.config.get('RATELIMIT_ENABLED', True):
            return None
        
        # Skip rate limiting for certain paths
        exempt_paths = ['/health', '/metrics', '/favicon.ico']
        if request.path in exempt_paths:
            return None
        
        # Get limit for this endpoint
        limit, window = self._get_limit_for_endpoint()
        
        # Check rate limit
        client_key = self._get_client_key()
        is_allowed, remaining, reset_time = self._check_limit(client_key, limit, window)
        
        # Store for headers
        g.rate_limit = limit
        g.rate_limit_remaining = remaining
        g.rate_limit_reset = reset_time
        
        if not is_allowed:
            response = jsonify({
                'error': 'Too Many Requests',
                'message': f'Rate limit exceeded. Limit: {limit} requests per {window} seconds.',
                'retry_after': reset_time - int(time.time())
            })
            response.status_code = 429
            return abort(response)
        
        return None
    
    def _get_limit_for_endpoint(self) -> Tuple[int, int]:
        """Get rate limit configuration for current endpoint."""
        # Default limit
        limit = self.default_limit
        window = self.default_window
        
        # Check for endpoint-specific limits
        endpoint_limits = {
            '/auth/login': (5, 60),      # 5 requests per minute for login
            '/auth/register': (3, 60),    # 3 requests per minute for registration
            '/api/': (100, 60),           # 100 requests per minute for API
        }
        
        for path_prefix, (path_limit, path_window) in endpoint_limits.items():
            if request.path.startswith(path_prefix):
                limit = path_limit
                window = path_window
                break
        
        return limit, window
    
    def _check_limit(
        self,
        key: str,
        limit: int,
        window: int
    ) -> Tuple[bool, int, int]:
        """
        Check rate limit using sliding window algorithm.
        
        Returns:
            Tuple of (is_allowed, remaining, reset_time)
        """
        current_time = int(time.time())
        window_start = current_time - window
        redis_key = f"ratelimit:{key}:{request.path}"
        
        if self.redis:
            return self._check_limit_redis(redis_key, limit, window, current_time, window_start)
        else:
            return self._check_limit_memory(redis_key, limit, window, current_time, window_start)
    
    def _check_limit_redis(
        self,
        key: str,
        limit: int,
        window: int,
        current_time: int,
        window_start: int
    ) -> Tuple[bool, int, int]:
        """Check rate limit using Redis."""
        pipe = self.redis.pipeline()
        
        # Remove old entries
        pipe.zremrangebyscore(key, 0, window_start)
        
        # Count current entries
        pipe.zcard(key)
        
        # Add current request
        pipe.zadd(key, {str(current_time): current_time})
        
        # Set expiry
        pipe.expire(key, window * 2)
        
        results = pipe.execute()
        request_count = results[1]
        
        remaining = max(0, limit - request_count - 1)
        reset_time = current_time + window
        is_allowed = request_count < limit
        
        return is_allowed, remaining, reset_time
    
    def _check_limit_memory(
        self,
        key: str,
        limit: int,
        window: int,
        current_time: int,
        window_start: int
    ) -> Tuple[bool, int, int]:
        """Check rate limit using in-memory storage (for development)."""
        # Initialize if needed
        if key not in self._fallback_storage:
            self._fallback_storage[key] = []
        
        # Remove old entries
        self._fallback_storage[key] = [
            ts for ts in self._fallback_storage[key]
            if ts > window_start
        ]
        
        request_count = len(self._fallback_storage[key])
        
        # Add current request
        self._fallback_storage[key].append(current_time)
        
        remaining = max(0, limit - request_count - 1)
        reset_time = current_time + window
        is_allowed = request_count < limit
        
        return is_allowed, remaining, reset_time
    
    def _add_rate_limit_headers(self, response: Response) -> Response:
        """Add rate limit headers to response."""
        if not self.app.config.get('RATELIMIT_HEADERS_ENABLED', True):
            return response
        
        if hasattr(g, 'rate_limit'):
            response.headers['X-RateLimit-Limit'] = str(g.rate_limit)
            response.headers['X-RateLimit-Remaining'] = str(g.rate_limit_remaining)
            response.headers['X-RateLimit-Reset'] = str(g.rate_limit_reset)
        
        return response


def rate_limit(limit: int = 10, window: int = 1) -> Callable:
    """
    Decorator for endpoint-specific rate limiting.
    
    Args:
        limit: Number of requests allowed
        window: Time window in seconds
    
    Usage:
        @app.route('/api/resource')
        @rate_limit(limit=5, window=60)  # 5 requests per minute
        def resource():
            return 'OK'
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args: Any, **kwargs: Any) -> Any:
            # Store custom limit in g for this request
            g.custom_rate_limit = limit
            g.custom_rate_window = window
            return f(*args, **kwargs)
        
        # Mark function with rate limit metadata
        decorated_function._rate_limit = limit
        decorated_function._rate_window = window
        
        return decorated_function
    return decorator
