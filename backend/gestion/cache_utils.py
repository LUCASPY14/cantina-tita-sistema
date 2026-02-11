"""
Utilidades de caché para optimizar performance
"""
from django.core.cache import cache
from django.conf import settings
from functools import wraps
import hashlib
import json


def cache_result(timeout=None, key_prefix='', vary_on=None):
    """
    Decorador para cachear resultados de funciones
    
    Args:
        timeout: Tiempo de cache en segundos (None = default)
        key_prefix: Prefijo para la clave de cache
        vary_on: Lista de parámetros para variar la cache
    
    Ejemplo:
        @cache_result(timeout=300, key_prefix='productos', vary_on=['categoria_id'])
        def get_productos(categoria_id):
            return Producto.objects.filter(categoria_id=categoria_id)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generar clave de cache
            cache_key = _generate_cache_key(func.__name__, key_prefix, args, kwargs, vary_on)
            
            # Intentar obtener del cache
            result = cache.get(cache_key)
            
            if result is not None:
                return result
            
            # Ejecutar función y cachear resultado
            result = func(*args, **kwargs)
            
            # Determinar timeout
            cache_timeout = timeout or getattr(settings, 'CACHE_MIDDLEWARE_SECONDS', 300)
            
            # Guardar en cache
            cache.set(cache_key, result, cache_timeout)
            
            return result
        
        return wrapper
    return decorator


def _generate_cache_key(func_name, prefix, args, kwargs, vary_on):
    """Generar clave única de cache"""
    key_parts = [prefix, func_name]
    
    if vary_on:
        # Usar solo parámetros especificados
        for param in vary_on:
            if param in kwargs:
                key_parts.append(f'{param}:{kwargs[param]}')
    else:
        # Usar todos los argumentos
        for arg in args:
            key_parts.append(str(arg))
        for k, v in sorted(kwargs.items()):
            key_parts.append(f'{k}:{v}')
    
    key_string = ':'.join(key_parts)
    
    # Hash para claves muy largas
    if len(key_string) > 200:
        key_string = hashlib.md5(key_string.encode()).hexdigest()
    
    return key_string


def invalidate_cache(key_prefix='', **filters):
    """
    Invalidar cache con un prefijo o filtros específicos
    
    Ejemplo:
        invalidate_cache(key_prefix='productos', categoria_id=5)
    """
    # Esta es una implementación simple
    # Para producción, considera usar django-redis con pattern matching
    if key_prefix:
        # Intento de invalidación por prefijo
        # Nota: Requiere django-redis o similar para pattern matching
        try:
            from django_redis import get_redis_connection
            conn = get_redis_connection("default")
            pattern = f"*{key_prefix}*"
            keys = conn.keys(pattern)
            if keys:
                conn.delete(*keys)
        except:
            # Fallback: limpiar todo el cache
            cache.clear()


class CacheManager:
    """
    Manager centralizado para operaciones de cache
    """
    
    @staticmethod
    def get_dashboard_data(user_id):
        """Obtener datos del dashboard desde cache"""
        cache_key = f'dashboard:user:{user_id}'
        return cache.get(cache_key)
    
    @staticmethod
    def set_dashboard_data(user_id, data, timeout=60):
        """Guardar datos del dashboard en cache"""
        cache_key = f'dashboard:user:{user_id}'
        cache.set(cache_key, data, timeout)
    
    @staticmethod
    def get_productos_by_categoria(categoria_id):
        """Obtener productos por categoría desde cache"""
        cache_key = f'productos:categoria:{categoria_id}'
        return cache.get(cache_key)
    
    @staticmethod
    def set_productos_by_categoria(categoria_id, productos, timeout=300):
        """Guardar productos en cache"""
        cache_key = f'productos:categoria:{categoria_id}'
        cache.set(cache_key, productos, timeout)
    
    @staticmethod
    def invalidate_productos():
        """Invalidar cache de productos"""
        invalidate_cache(key_prefix='productos')
    
    @staticmethod
    def get_saldo_tarjeta(tarjeta_id):
        """Obtener saldo de tarjeta desde cache"""
        cache_key = f'saldo:tarjeta:{tarjeta_id}'
        return cache.get(cache_key)
    
    @staticmethod
    def set_saldo_tarjeta(tarjeta_id, saldo, timeout=30):
        """Guardar saldo de tarjeta en cache (30 segundos)"""
        cache_key = f'saldo:tarjeta:{tarjeta_id}'
        cache.set(cache_key, saldo, timeout)
    
    @staticmethod
    def invalidate_saldo_tarjeta(tarjeta_id):
        """Invalidar cache de saldo de tarjeta específica"""
        cache_key = f'saldo:tarjeta:{tarjeta_id}'
        cache.delete(cache_key)
    
    @staticmethod
    def get_estadisticas_ventas(fecha):
        """Obtener estadísticas de ventas desde cache"""
        cache_key = f'stats:ventas:{fecha}'
        return cache.get(cache_key)
    
    @staticmethod
    def set_estadisticas_ventas(fecha, data, timeout=180):
        """Guardar estadísticas de ventas (3 minutos)"""
        cache_key = f'stats:ventas:{fecha}'
        cache.set(cache_key, data, timeout)
