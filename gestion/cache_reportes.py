"""
Sistema de Cache para Reportes
===============================
Cachea reportes generados para mejorar performance
Usa Django cache framework con Redis/LocMem
"""

from django.core.cache import cache
from django.utils.encoding import force_str
from functools import wraps
import hashlib
import json
from datetime import datetime


class ReporteCache:
    """Gestor de cache para reportes"""
    
    # Timeouts por tipo de reporte (en segundos)
    TIMEOUT_VENTAS = 300  # 5 minutos
    TIMEOUT_PRODUCTOS = 600  # 10 minutos
    TIMEOUT_INVENTARIO = 1800  # 30 minutos
    TIMEOUT_CONSUMOS = 300  # 5 minutos
    TIMEOUT_CLIENTES = 1800  # 30 minutos
    TIMEOUT_CTA_CORRIENTE = 600  # 10 minutos
    TIMEOUT_DASHBOARD = 60  # 1 minuto
    TIMEOUT_ALMUERZOS = 300  # 5 minutos
    
    @staticmethod
    def generar_cache_key(tipo_reporte, **params):
        """
        Genera una clave única para el cache basada en el tipo y parámetros
        
        Args:
            tipo_reporte: str - Tipo de reporte (ventas, productos, etc.)
            **params: Parámetros del reporte (fechas, filtros, etc.)
        
        Returns:
            str - Cache key única
        """
        # Serializar parámetros ordenados
        params_str = json.dumps(params, sort_keys=True, default=str)
        
        # Crear hash de los parámetros
        params_hash = hashlib.md5(params_str.encode()).hexdigest()
        
        # Formato: reporte:tipo:hash
        return f"reporte:{tipo_reporte}:{params_hash}"
    
    @staticmethod
    def get_reporte(tipo_reporte, **params):
        """
        Obtiene un reporte del cache si existe
        
        Returns:
            Reporte cacheado o None si no existe
        """
        cache_key = ReporteCache.generar_cache_key(tipo_reporte, **params)
        return cache.get(cache_key)
    
    @staticmethod
    def set_reporte(tipo_reporte, data, timeout=None, **params):
        """
        Guarda un reporte en el cache
        
        Args:
            tipo_reporte: str - Tipo de reporte
            data: Datos del reporte a cachear
            timeout: int - Tiempo de expiración (segundos)
            **params: Parámetros del reporte
        """
        if timeout is None:
            # Usar timeout por defecto según tipo
            timeout = getattr(ReporteCache, f'TIMEOUT_{tipo_reporte.upper()}', 300)
        
        cache_key = ReporteCache.generar_cache_key(tipo_reporte, **params)
        cache.set(cache_key, data, timeout)
    
    @staticmethod
    def invalidar_reporte(tipo_reporte, **params):
        """
        Invalida (elimina) un reporte específico del cache
        """
        cache_key = ReporteCache.generar_cache_key(tipo_reporte, **params)
        cache.delete(cache_key)
    
    @staticmethod
    def invalidar_tipo(tipo_reporte):
        """
        Invalida todos los reportes de un tipo específico
        Usa patrón de clave para buscar y eliminar
        """
        pattern = f"reporte:{tipo_reporte}:*"
        # Nota: Esto requiere Redis. Para LocMem, solo podemos invalidar específicos
        try:
            cache.delete_pattern(pattern)
        except AttributeError:
            # LocMem no soporta delete_pattern
            pass
    
    @staticmethod
    def invalidar_todos():
        """Invalida todos los reportes del cache"""
        try:
            cache.delete_pattern("reporte:*")
        except AttributeError:
            # LocMem no soporta delete_pattern
            pass


def cache_reporte(tipo_reporte, timeout=None):
    """
    Decorator para cachear funciones de reportes automáticamente
    
    Uso:
        @cache_reporte('ventas', timeout=300)
        def reporte_ventas(fecha_inicio, fecha_fin):
            # ... generar reporte
            return reporte_data
    
    Args:
        tipo_reporte: str - Tipo de reporte (ventas, productos, etc.)
        timeout: int - Tiempo de expiración en segundos (opcional)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generar parámetros para cache key
            cache_params = {
                'args': str(args),
                **kwargs
            }
            
            # Intentar obtener del cache
            cached_result = ReporteCache.get_reporte(tipo_reporte, **cache_params)
            if cached_result is not None:
                return cached_result
            
            # Ejecutar función y cachear resultado
            result = func(*args, **kwargs)
            
            # Solo cachear si hay resultado válido
            if result is not None:
                ReporteCache.set_reporte(
                    tipo_reporte,
                    result,
                    timeout=timeout,
                    **cache_params
                )
            
            return result
        
        return wrapper
    return decorator


def invalidar_cache_al_guardar(tipo_reporte):
    """
    Decorator para invalidar cache cuando se guarda un modelo
    
    Uso:
        class Ventas(models.Model):
            # ...
            
            @invalidar_cache_al_guardar('ventas')
            def save(self, *args, **kwargs):
                super().save(*args, **kwargs)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            ReporteCache.invalidar_tipo(tipo_reporte)
            return result
        return wrapper
    return decorator


# =============================================================================
# FUNCIONES HELPER PARA VISTAS
# =============================================================================

def get_reporte_cacheado(request, tipo_reporte, generador_func, timeout=None):
    """
    Helper para obtener reportes con cache en vistas
    
    Args:
        request: HttpRequest
        tipo_reporte: str - Tipo de reporte
        generador_func: callable - Función que genera el reporte
        timeout: int - Timeout del cache (opcional)
    
    Returns:
        HttpResponse con el reporte
    
    Ejemplo:
        def reporte_ventas_pdf(request):
            return get_reporte_cacheado(
                request,
                'ventas',
                lambda: ReportesPDF.reporte_ventas(fecha_inicio, fecha_fin),
                timeout=300
            )
    """
    # Extraer parámetros de la request
    params = {
        'formato': 'pdf',  # o 'excel'
        **dict(request.GET.items())
    }
    
    # Intentar obtener del cache
    cached_result = ReporteCache.get_reporte(tipo_reporte, **params)
    if cached_result:
        return cached_result
    
    # Generar reporte
    result = generador_func()
    
    # Cachear resultado
    if result:
        ReporteCache.set_reporte(tipo_reporte, result, timeout=timeout, **params)
    
    return result


def get_datos_dashboard_cacheados():
    """
    Obtiene datos del dashboard con cache
    Cache de 1 minuto para dashboard principal
    
    Returns:
        dict con estadísticas del dashboard
    """
    cache_key = "dashboard:estadisticas:principal"
    
    # Intentar obtener del cache
    datos = cache.get(cache_key)
    if datos:
        return datos
    
    # Generar estadísticas (importar aquí para evitar circular imports)
    from .models import Producto, Cliente, Ventas, ConsumoTarjeta
    from django.db.models import Sum, Count
    from django.utils import timezone
    
    hoy = timezone.now().date()
    
    datos = {
        'total_productos': Producto.objects.filter(activo=True).count(),
        'total_clientes': Cliente.objects.filter(activo=True).count(),
        'ventas_hoy': Ventas.objects.filter(fecha__date=hoy).count(),
        'total_ventas_hoy': Ventas.objects.filter(
            fecha__date=hoy
        ).aggregate(total=Sum('monto_total'))['total'] or 0,
        'consumos_hoy': ConsumoTarjeta.objects.filter(fecha_consumo__date=hoy).count(),
        'total_consumos_hoy': ConsumoTarjeta.objects.filter(
            fecha_consumo__date=hoy
        ).aggregate(total=Sum('monto'))['total'] or 0,
        'ultima_actualizacion': timezone.now()
    }
    
    # Cachear por 1 minuto
    cache.set(cache_key, datos, ReporteCache.TIMEOUT_DASHBOARD)
    
    return datos


def invalidar_cache_dashboard():
    """Invalida el cache del dashboard"""
    cache.delete("dashboard:estadisticas:principal")


# =============================================================================
# ESTADÍSTICAS DE CACHE
# =============================================================================

def get_stats_cache():
    """
    Obtiene estadísticas del cache (si está disponible)
    
    Returns:
        dict con estadísticas o None si no están disponibles
    """
    try:
        # Esto funciona con Redis
        from django.core.cache.backends.redis import RedisCache
        if isinstance(cache, RedisCache):
            stats = cache._cache.info('stats')
            return {
                'tipo': 'Redis',
                'hits': stats.get('keyspace_hits', 0),
                'misses': stats.get('keyspace_misses', 0),
                'memoria_usada': stats.get('used_memory_human', 'N/A')
            }
    except:
        pass
    
    return {
        'tipo': 'LocMem',
        'info': 'Estadísticas no disponibles en LocMem'
    }
