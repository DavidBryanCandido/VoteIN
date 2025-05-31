import time
from functools import wraps
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse

def rate_limit(key_prefix, limit=5, period=60):
    """
    Rate limiting decorator that limits requests based on IP address.
    
    Args:
        key_prefix (str): Prefix for the cache key
        limit (int): Maximum number of requests allowed in the period
        period (int): Time period in seconds
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(view_instance, request, *args, **kwargs):
            # Get client IP
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            
            # Create cache key with prefix
            cache_key = f'rate_limit_{key_prefix}_{ip}'
            
            # Get current count
            current = cache.get(cache_key, 0)
            
            if current >= limit:
                return JsonResponse({
                    'error': f'Rate limit exceeded. Maximum {limit} requests per {period} seconds.'
                }, status=429)
            
            # Increment counter
            cache.set(cache_key, current + 1, period)
            
            return view_func(view_instance, request, *args, **kwargs)
        return _wrapped_view
    return decorator
