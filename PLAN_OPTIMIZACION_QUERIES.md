"""
PLAN DE OPTIMIZACIÓN - QUERIES DJANGO Y PAGINACIÓN
==================================================
Fecha: 10 Enero 2026

FASE 1: OPTIMIZACIÓN DE QUERIES (85-95% reducción)
===================================================

ARCHIVOS A OPTIMIZAR:
--------------------

1. api_views.py (ALTA PRIORIDAD)
   Problemas detectados:
   - ClienteViewSet.cuenta_corriente: 2 queries separadas (combinar con aggregate)
   - ClienteViewSet.ventas: falta prefetch_related para detalles
   - TarjetaViewSet: falta select_related en varios métodos
   - ProductoViewSet.stock_critico: N+1 queries en loop
   - ProductoViewSet.mas_vendidos: OK (usa annotate)
   
   Optimizaciones:
   ✅ Agregar select_related('id_cliente', 'id_empleado_cajero')
   ✅ Agregar prefetch_related('detalleventa_set__id_producto')
   ✅ Usar only() para limitar campos en listados
   ✅ Combinar queries en cuenta_corriente

2. pos_general_views.py (ALTA PRIORIDAD)
   Problemas detectados:
   - buscar_producto_api: Loop con queries individuales para precios/stock
   - verificar_tarjeta_api: Ya tiene select_related ✅
   - verificar_restricciones_carrito_api: Loop de verificación
   
   Optimizaciones:
   ✅ Prefetch precios en búsqueda de productos
   ✅ Usar annotate para calcular stock en 1 query
   ✅ Batch queries para restricciones

3. pos_views.py (MEDIA PRIORIDAD)
   Problemas:
   - Listados sin select_related
   - Sin paginación
   
4. portal_views.py (MEDIA PRIORIDAD)
   - Queries sin optimizar en historial
   - Sin paginación

FASE 2: PAGINACIÓN (MEJOR UX)
==============================

VISTAS A PAGINAR:
----------------
1. Listado de ventas (25-50 por página)
2. Listado de productos (50-100 por página)
3. Historial de consumos (25 por página)
4. Reportes (configurable)

IMPLEMENTACIÓN:
--------------
- Django Paginator para templates
- PageNumberPagination para API REST
- Configuración global en settings.py
- UI con Bootstrap 5 pagination

MÉTRICAS ESPERADAS:
==================

ANTES (sin optimización):
- Listado 100 ventas: ~150 queries (N+1)
- Dashboard: ~200 queries
- Historial tarjeta: ~50 queries

DESPUÉS (optimizado):
- Listado 100 ventas: 3-5 queries (select_related + prefetch_related)
- Dashboard: 5-10 queries
- Historial tarjeta: 2-3 queries

REDUCCIÓN: 85-95% ✅

PLAN DE EJECUCIÓN:
=================

1. Optimizar api_views.py (30 min)
2. Optimizar pos_general_views.py (30 min)
3. Implementar paginación en API (20 min)
4. Implementar paginación en templates (30 min)
5. Testing y verificación (20 min)

TOTAL ESTIMADO: 2 horas
"""
