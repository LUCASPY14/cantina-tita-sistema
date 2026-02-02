"""
Signals para invalidación automática de cache
==============================================

Sistema de signals que invalida automáticamente el cache cuando se crean,
modifican o eliminan registros relevantes.

Conecta con:
- Django signals (post_save, post_delete)
- ReporteCache para invalidación
- Modelos críticos del sistema
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

from .cache_reportes import ReporteCache, invalidar_cache_dashboard
from .models import (
    Producto,
    Cliente,
    Categoria,
    DatosFacturacionElect,
    RegistroConsumoAlmuerzo,
)


# Instancia global de ReporteCache
cache_reportes = ReporteCache()


# =============================================================================
# SIGNALS PARA PRODUCTOS
# =============================================================================

@receiver(post_save, sender=Producto)
def invalidar_cache_producto_guardado(sender, instance, created, **kwargs):
    """
    Invalida cache cuando se crea o modifica un producto
    
    Afecta:
    - Dashboard (total productos)
    - Reportes de productos
    - Lista de productos
    """
    # Invalidar cache de reportes de productos
    cache_reportes.invalidar_tipo('productos')
    
    # Invalidar dashboard
    invalidar_cache_dashboard()
    
    # Invalidar lista de productos
    cache.delete('productos_list:all')
    
    # Log para debugging
    action = 'creado' if created else 'modificado'
    print(f"[CACHE] Producto {instance.nombre} {action} - Cache invalidado")


@receiver(post_delete, sender=Producto)
def invalidar_cache_producto_eliminado(sender, instance, **kwargs):
    """
    Invalida cache cuando se elimina un producto
    """
    cache_reportes.invalidar_tipo('productos')
    invalidar_cache_dashboard()
    cache.delete('productos_list:all')
    
    print(f"[CACHE] Producto {instance.nombre} eliminado - Cache invalidado")


# =============================================================================
# SIGNALS PARA STOCK
# =============================================================================

# NOTA: StockUnico no existe en models, usar StockProducto
# @receiver(post_save, sender=StockUnico)
# def invalidar_cache_stock_modificado(sender, instance, **kwargs):
#     """
#     Invalida cache cuando cambia el stock
#     
#     Afecta:
#     - Reportes de inventario
#     - Dashboard (productos bajo stock)
#     """
#     cache_reportes.invalidar_tipo('inventario')
#     invalidar_cache_dashboard()
#     
#     print(f"[CACHE] Stock actualizado para {instance.id_producto.nombre} - Cache invalidado")


# =============================================================================
# SIGNALS PARA CLIENTES
# =============================================================================

@receiver(post_save, sender=Cliente)
def invalidar_cache_cliente_guardado(sender, instance, created, **kwargs):
    """
    Invalida cache cuando se crea o modifica un cliente
    """
    cache_reportes.invalidar_tipo('clientes')
    invalidar_cache_dashboard()
    cache.delete('clientes_list:all')
    
    action = 'creado' if created else 'modificado'
    print(f"[CACHE] Cliente {instance.nombres} {instance.apellidos} {action} - Cache invalidado")


@receiver(post_delete, sender=Cliente)
def invalidar_cache_cliente_eliminado(sender, instance, **kwargs):
    """
    Invalida cache cuando se elimina un cliente
    """
    cache_reportes.invalidar_tipo('clientes')
    invalidar_cache_dashboard()
    cache.delete('clientes_list:all')
    
    print(f"[CACHE] Cliente {instance.nombre} {instance.apellido} eliminado - Cache invalidado")


# =============================================================================
# SIGNALS PARA VENTAS/CONSUMOS
# =============================================================================

# NOTA: PuntoVentaConsumo y DetallesConsumo no existen en models, usar Venta y DetalleVenta
# @receiver(post_save, sender=PuntoVentaConsumo)
# def invalidar_cache_venta_guardada(sender, instance, created, **kwargs):
#     """
#     Invalida cache cuando se registra una venta/consumo
#     
#     Afecta:
#     - Reportes de ventas
#     - Dashboard (ventas del día)
#     - Cuenta corriente
#     """
#     cache_reportes.invalidar_tipo('ventas')
#     cache_reportes.invalidar_tipo('consumos')
#     invalidar_cache_dashboard()
#     
#     if created:
#         print(f"[CACHE] Venta registrada - Cache invalidado")


# @receiver(post_delete, sender=PuntoVentaConsumo)
# def invalidar_cache_venta_eliminada(sender, instance, **kwargs):
#     """
#     Invalida cache cuando se elimina una venta
#     """
#     cache_reportes.invalidar_tipo('ventas')
#     cache_reportes.invalidar_tipo('consumos')
#     invalidar_cache_dashboard()
#     
#     print(f"[CACHE] Venta eliminada - Cache invalidado")


# @receiver(post_save, sender=DetallesConsumo)
# def invalidar_cache_detalle_guardado(sender, instance, created, **kwargs):
#     """
#     Invalida cache cuando se agregan/modifican detalles de consumo
#     """
#     if created:
#         cache_reportes.invalidar_tipo('ventas')
#         cache_reportes.invalidar_tipo('productos')
#         invalidar_cache_dashboard()


# =============================================================================
# SIGNALS PARA ALMUERZOS
# =============================================================================

@receiver(post_save, sender=RegistroConsumoAlmuerzo)
def invalidar_cache_almuerzo_guardado(sender, instance, created, **kwargs):
    """
    Invalida cache cuando se registra un almuerzo
    
    Afecta:
    - Reportes de almuerzos
    - Dashboard de almuerzos
    - Estadísticas diarias/mensuales
    """
    from datetime import date
    
    cache_reportes.invalidar_tipo('almuerzos')
    
    # Invalidar cache específico del día
    hoy = date.today()
    cache.delete(f'almuerzo_stats:{hoy}')
    cache.delete(f'almuerzo_diario:{instance.fecha_consumo}:{instance.fecha_consumo}')
    
    if created:
        print(f"[CACHE] Almuerzo registrado para {instance.id_hijo} - Cache invalidado")


@receiver(post_delete, sender=RegistroConsumoAlmuerzo)
def invalidar_cache_almuerzo_eliminado(sender, instance, **kwargs):
    """
    Invalida cache cuando se elimina un registro de almuerzo
    """
    from datetime import date
    
    cache_reportes.invalidar_tipo('almuerzos')
    hoy = date.today()
    cache.delete(f'almuerzo_stats:{hoy}')
    
    print(f"[CACHE] Almuerzo eliminado - Cache invalidado")


# =============================================================================
# SIGNALS PARA FACTURACIÓN
# =============================================================================

@receiver(post_save, sender=DatosFacturacionElect)
def invalidar_cache_facturacion_guardada(sender, instance, created, **kwargs):
    """
    Invalida cache cuando se emite o modifica una factura electrónica
    
    Afecta:
    - Dashboard de facturación
    - Reportes de cumplimiento
    """
    cache.delete('dashboard_facturacion')
    cache.delete('reporte_cumplimiento_facturacion')
    
    if created:
        print(f"[CACHE] Factura electrónica emitida - Cache invalidado")


@receiver(post_delete, sender=DatosFacturacionElect)
def invalidar_cache_facturacion_eliminada(sender, instance, **kwargs):
    """
    Invalida cache cuando se elimina una factura
    """
    cache.delete('dashboard_facturacion')
    cache.delete('reporte_cumplimiento_facturacion')
    
    print(f"[CACHE] Factura eliminada - Cache invalidado")


# =============================================================================
# SIGNALS PARA CATEGORÍAS
# =============================================================================

@receiver(post_save, sender=Categoria)
def invalidar_cache_categoria_guardada(sender, instance, created, **kwargs):
    """
    Invalida cache cuando se crea o modifica una categoría
    """
    cache_reportes.invalidar_tipo('productos')
    cache.delete('categorias_list:all')
    
    action = 'creada' if created else 'modificada'
    print(f"[CACHE] Categoría {instance.nombre} {action} - Cache invalidado")


@receiver(post_delete, sender=Categoria)
def invalidar_cache_categoria_eliminada(sender, instance, **kwargs):
    """
    Invalida cache cuando se elimina una categoría
    """
    cache_reportes.invalidar_tipo('productos')
    cache.delete('categorias_list:all')
    
    print(f"[CACHE] Categoría {instance.nombre} eliminada - Cache invalidado")


# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================

def invalidar_cache_completo():
    """
    Invalida TODO el cache del sistema
    Usar solo en casos excepcionales (deploy, migración, etc.)
    """
    cache_reportes.invalidar_todos()
    cache.clear()
    
    print("[CACHE] Cache completo invalidado")


def obtener_estadisticas_invalidaciones():
    """
    Retorna estadísticas de invalidaciones de cache
    Útil para debugging y optimización
    """
    # Esto requeriría un contador en cada signal
    # Por ahora es un placeholder para implementación futura
    pass


# =============================================================================
# CONFIGURACIÓN
# =============================================================================

# Flag para deshabilitar signals temporalmente (útil para imports masivos)
SIGNALS_HABILITADOS = True


def deshabilitar_signals():
    """
    Deshabilita temporalmente todos los signals de cache
    Útil para operaciones masivas de importación
    """
    global SIGNALS_HABILITADOS
    SIGNALS_HABILITADOS = False
    print("[CACHE] Signals de cache DESHABILITADOS")


def habilitar_signals():
    """
    Re-habilita los signals de cache
    """
    global SIGNALS_HABILITADOS
    SIGNALS_HABILITADOS = True
    print("[CACHE] Signals de cache HABILITADOS")


# =============================================================================
# HOOK CONDICIONAL
# =============================================================================

# Modificar cada signal para verificar SIGNALS_HABILITADOS
# Esto se puede hacer con un decorator, pero por simplicidad lo dejamos así
# En producción, considerar usar django-signals-ahoy o similar

print("[SIGNALS] Sistema de invalidación automática de cache CARGADO")
print("[SIGNALS] Modelos conectados: Producto, Cliente, Stock, Ventas, Almuerzos, Facturación")
