import time
from functools import wraps
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework import status

def rate_limit(key_prefix, limit=5, period=60):
    """
    Limit requests to `limit` per `period` seconds per key (IP or user).
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Use IP address as key (or user if authenticated)
            if request.user.is_authenticated:
                ident = f"{key_prefix}:{request.user.pk}"
            else:
                ident = f"{key_prefix}:{request.META.get('REMOTE_ADDR')}"
            now = int(time.time())
            window = now // period
            cache_key = f"rl:{ident}:{window}"
            count = cache.get(cache_key, 0)
            if count >= limit:
                return Response(
                    {"detail": f"Rate limit exceeded. Max {limit} requests per {period} seconds."},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )
            cache.incr(cache_key)
            cache.expire(cache_key, period)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
