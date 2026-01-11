"""
Decoradores y utilidades para Rate Limiting
"""
from functools import wraps
from django.core.cache import cache
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
import hashlib
import time


class RateLimiter:
    """
    Sistema de rate limiting personalizado usando Redis/Cache
    """
    
    def __init__(self, max_requests, window_seconds):
        """
        Args:
            max_requests: Número máximo de requests permitidos
            window_seconds: Ventana de tiempo en segundos
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    def get_cache_key(self, identifier):
        """Generar clave de cache única"""
        hash_id = hashlib.md5(identifier.encode()).hexdigest()
        return f'ratelimit:{hash_id}'
    
    def is_allowed(self, identifier):
        """
        Verificar si se permite el request
        
        Args:
            identifier: IP, usuario, o cualquier identificador único
            
        Returns:
            (allowed, remaining, reset_time)
        """
        cache_key = self.get_cache_key(identifier)
        
        # Obtener datos actuales del cache
        data = cache.get(cache_key)
        current_time = int(time.time())
        
        if data is None:
            # Primera request
            data = {
                'count': 1,
                'reset_time': current_time + self.window_seconds
            }
            cache.set(cache_key, data, self.window_seconds)
            return True, self.max_requests - 1, data['reset_time']
        
        # Verificar si la ventana expiró
        if current_time >= data['reset_time']:
            # Resetear contador
            data = {
                'count': 1,
                'reset_time': current_time + self.window_seconds
            }
            cache.set(cache_key, data, self.window_seconds)
            return True, self.max_requests - 1, data['reset_time']
        
        # Incrementar contador
        if data['count'] < self.max_requests:
            data['count'] += 1
            cache.set(cache_key, data, self.window_seconds)
            return True, self.max_requests - data['count'], data['reset_time']
        
        # Límite excedido
        return False, 0, data['reset_time']


def ratelimit(max_requests=60, window_seconds=3600, key_func=None):
    """
    Decorador para aplicar rate limiting a vistas
    
    Args:
        max_requests: Número máximo de requests
        window_seconds: Ventana de tiempo en segundos
        key_func: Función para obtener el identificador (default: IP)
    
    Ejemplo:
        @ratelimit(max_requests=10, window_seconds=60)
        def my_view(request):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            limiter = RateLimiter(max_requests, window_seconds)
            
            # Obtener identificador
            if key_func:
                identifier = key_func(request)
            else:
                # Usar IP por defecto
                identifier = get_client_ip(request)
            
            # Verificar límite
            allowed, remaining, reset_time = limiter.is_allowed(identifier)
            
            if not allowed:
                # Límite excedido
                if hasattr(request, 'accepted_renderer'):
                    # DRF Response
                    return Response({
                        'error': 'Rate limit exceeded',
                        'message': 'Demasiadas solicitudes. Por favor, intente más tarde.',
                        'retry_after': reset_time - int(time.time())
                    }, status=status.HTTP_429_TOO_MANY_REQUESTS)
                else:
                    # Django Response
                    return JsonResponse({
                        'error': 'Rate limit exceeded',
                        'message': 'Demasiadas solicitudes. Por favor, intente más tarde.',
                        'retry_after': reset_time - int(time.time())
                    }, status=429)
            
            # Agregar headers de rate limit
            response = func(request, *args, **kwargs)
            
            if hasattr(response, '__setitem__'):
                response['X-RateLimit-Limit'] = str(max_requests)
                response['X-RateLimit-Remaining'] = str(remaining)
                response['X-RateLimit-Reset'] = str(reset_time)
            
            return response
        
        return wrapper
    return decorator


def get_client_ip(request):
    """Obtener IP del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_identifier(request):
    """Obtener identificador del usuario (IP o user_id)"""
    if request.user.is_authenticated:
        return f'user:{request.user.id}'
    return f'ip:{get_client_ip(request)}'


# Decoradores predefinidos para casos comunes

def ratelimit_login(func):
    """Rate limit para login: 5 intentos por hora"""
    return ratelimit(max_requests=5, window_seconds=3600)(func)


def ratelimit_api(func):
    """Rate limit para APIs: 100 requests por hora"""
    return ratelimit(max_requests=100, window_seconds=3600, key_func=get_user_identifier)(func)


def ratelimit_venta(func):
    """Rate limit para ventas: 200 por hora"""
    return ratelimit(max_requests=200, window_seconds=3600, key_func=get_user_identifier)(func)


def ratelimit_recarga(func):
    """Rate limit para recargas: 30 por hora"""
    return ratelimit(max_requests=30, window_seconds=3600, key_func=get_user_identifier)(func)


# Middleware de Rate Limiting

class RateLimitMiddleware:
    """
    Middleware para aplicar rate limiting global
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.limiter = RateLimiter(max_requests=1000, window_seconds=3600)
    
    def __call__(self, request):
        # Obtener identificador
        identifier = get_client_ip(request)
        
        # Verificar límite
        allowed, remaining, reset_time = self.limiter.is_allowed(identifier)
        
        if not allowed:
            return JsonResponse({
                'error': 'Rate limit exceeded',
                'message': 'Demasiadas solicitudes. Por favor, intente más tarde.',
                'retry_after': reset_time - int(time.time())
            }, status=429)
        
        # Continuar con el request
        response = self.get_response(request)
        
        # Agregar headers
        response['X-RateLimit-Limit'] = '1000'
        response['X-RateLimit-Remaining'] = str(remaining)
        response['X-RateLimit-Reset'] = str(reset_time)
        
        return response
