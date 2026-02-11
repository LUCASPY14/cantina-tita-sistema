"""
Dashboard Unificado de Monitoreo
Centraliza todas las métricas críticas del sistema en una sola vista
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum, Count, Avg, Q, F
from django.core.cache import cache
from datetime import timedelta
import psutil
import os

from gestion.models import (
    Producto, StockUnico, Tarjeta, CargasSaldo,
    ConsumoTarjeta, Cliente, AlertasSistema, MovimientosStock, Categoria
)
from pos.models import Venta as Ventas, DetalleVenta
from gestion.permisos import solo_gerente_o_superior


@solo_gerente_o_superior
def dashboard_unificado(request):
    """
    Dashboard principal con métricas del sistema
    Cachea datos por 60 segundos para mejorar performance
    Acceso: Gerentes y Administradores
    """
    # Intentar obtener desde cache
    cache_key = f'dashboard_data_{request.user.id}'
    cached_data = cache.get(cache_key)
    
    if cached_data:
        context = cached_data
        context['from_cache'] = True
    else:
        # Calcular métricas
        hoy = timezone.now().date()
        hace_7_dias = hoy - timedelta(days=7)
        hace_30_dias = hoy - timedelta(days=30)
        
        # === MÉTRICAS DE VENTAS ===
        ventas_hoy = Ventas.objects.filter(fecha__date=hoy)
        ventas_7dias = Ventas.objects.filter(fecha__date__gte=hace_7_dias)
        ventas_30dias = Ventas.objects.filter(fecha__date__gte=hace_30_dias)
        
        metricas_ventas = {
            'hoy_total': ventas_hoy.aggregate(
                total=Sum('monto_total'),
                cantidad=Count('id_venta')
            ),
            'hoy_efectivo': 0,  # Calcular manualmente si es necesario
            'hoy_tarjeta': 0,   # Calcular manualmente si es necesario
            'hoy_qr': 0,        # Calcular manualmente si es necesario
            'semana_total': ventas_7dias.aggregate(
                total=Sum('monto_total'),
                cantidad=Count('id_venta')
            ),
            'mes_total': ventas_30dias.aggregate(
                total=Sum('monto_total'),
                cantidad=Count('id_venta')
            ),
            'promedio_venta': ventas_hoy.aggregate(
                promedio=Avg('monto_total')
            )['promedio'] or 0,
        }
        
        # === MÉTRICAS DE STOCK ===
        stock_bajo = StockUnico.objects.filter(
            stock_actual__lte=F('id_producto__stock_minimo')
        ).select_related('id_producto')
        
        stock_critico = stock_bajo.filter(
            stock_actual__lte=F('id_producto__stock_minimo') / 2
        )
        
        metricas_stock = {
            'total_productos': Producto.objects.filter(activo=True).count(),
            'bajo_stock': stock_bajo.count(),
            'critico': stock_critico.count(),
            'sin_stock': StockUnico.objects.filter(stock_actual=0).count(),
            'productos_bajo_stock': stock_bajo[:10],  # Top 10
            # TODO: Corregir cálculo de valor_inventario cuando se defina estructura de precios
            'valor_inventario': 0,  # Temporalmente en 0
            # 'valor_inventario': StockUnico.objects.aggregate(
            #     total=Sum(F('stock_actual') * F('id_producto__precio'))
            # )['total'] or 0,
        }
        
        # === MÉTRICAS DE TARJETAS ===
        tarjetas_activas = Tarjeta.objects.filter(estado='activa')
        recargas_hoy = CargasSaldo.objects.filter(
            fecha_carga__date=hoy,
            estado='CONFIRMADO'
        )
        consumos_hoy = ConsumoTarjeta.objects.filter(
            fecha_consumo__date=hoy
        )
        
        metricas_tarjetas = {
            'activas': tarjetas_activas.count(),
            'bloqueadas': Tarjeta.objects.filter(estado='bloqueada').count(),
            'saldo_total': tarjetas_activas.aggregate(
                total=Sum('saldo_actual')
            )['total'] or 0,
            'recargas_hoy_total': recargas_hoy.aggregate(
                total=Sum('monto_cargado'),
                cantidad=Count('id_carga')
            ),
            'consumos_hoy_total': consumos_hoy.aggregate(
                total=Sum('monto_consumido'),
                cantidad=Count('id_consumo')
            ),
            'promedio_saldo': tarjetas_activas.aggregate(
                promedio=Avg('saldo_actual')
            )['promedio'] or 0,
            'saldo_bajo': tarjetas_activas.filter(saldo_actual__lt=10000).count(),
        }
        
        # === ALERTAS ACTIVAS ===
        alertas_activas = AlertasSistema.objects.filter(
            estado='Pendiente'
        ).order_by('-fecha_creacion')[:10]
        
        alertas_stats = {
            'criticas': AlertasSistema.objects.filter(estado='Pendiente', tipo='Stock Bajo').count(),
            'importantes': AlertasSistema.objects.filter(estado='Pendiente', tipo='Saldo Bajo').count(),
            'normales': AlertasSistema.objects.filter(estado='Pendiente', tipo='Sistema').count(),
            'total': AlertasSistema.objects.filter(estado='Pendiente').count(),
            'ultimas': alertas_activas,
        }
        
        # === MÉTRICAS DE CLIENTES ===
        metricas_clientes = {
            'total': Cliente.objects.filter(activo=True).count(),
            'con_tarjeta': Cliente.objects.filter(
                activo=True,
                hijos__tarjeta__isnull=False
            ).distinct().count(),
            'nuevos_mes': Cliente.objects.filter(
                fecha_registro__gte=hace_30_dias
            ).count(),
        }
        
        # === MÉTRICAS DEL SISTEMA ===
        try:
            # Información del servidor
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Información de backups
            backup_dir = 'backups'
            backups_info = {'existe': False, 'ultimo': None, 'total': 0}
            
            if os.path.exists(backup_dir):
                backups = [f for f in os.listdir(backup_dir) if f.endswith('.sql.gz')]
                backups_info['existe'] = True
                backups_info['total'] = len(backups)
                if backups:
                    ultimo_backup = max(backups, key=lambda x: os.path.getmtime(
                        os.path.join(backup_dir, x)
                    ))
                    ultimo_timestamp = os.path.getmtime(
                        os.path.join(backup_dir, ultimo_backup)
                    )
                    backups_info['ultimo'] = timezone.datetime.fromtimestamp(
                        ultimo_timestamp
                    )
            
            # Estado de Redis
            redis_activo = False
            try:
                cache.set('health_check', 'ok', 10)
                redis_activo = cache.get('health_check') == 'ok'
            except:
                pass
            
            metricas_sistema = {
                'cpu': cpu_percent,
                'cpu_alerta': cpu_percent > 80,
                'memoria_usada': memory.percent,
                'memoria_alerta': memory.percent > 85,
                'memoria_disponible_gb': memory.available / (1024**3),
                'disco_usado': disk.percent,
                'disco_alerta': disk.percent > 90,
                'disco_libre_gb': disk.free / (1024**3),
                'redis_activo': redis_activo,
                'backups': backups_info,
            }
        except Exception as e:
            metricas_sistema = {
                'error': str(e),
                'cpu': 0,
                'memoria_usada': 0,
                'disco_usado': 0,
                'redis_activo': False,
            }
        
        # === TOP PRODUCTOS ===
        from django.db.models import OuterRef, Subquery
        
        # Productos más vendidos hoy
        top_productos_hoy = Producto.objects.filter(
            detalleventa__id_venta__fecha__date=hoy
        ).annotate(
            vendidos=Count('detalleventa')
        ).order_by('-vendidos')[:5]
        
        context = {
            'ventas': metricas_ventas,
            'stock': metricas_stock,
            'tarjetas': metricas_tarjetas,
            'alertas': alertas_stats,
            'clientes': metricas_clientes,
            'sistema': metricas_sistema,
            'top_productos': top_productos_hoy,
            'ultima_actualizacion': timezone.now(),
            'from_cache': False,
        }
        
        # Guardar en cache por 60 segundos
        cache.set(cache_key, context, 60)
    
    return render(request, 'gestion/dashboard.html', context)


@login_required
def dashboard_ventas_detalle(request):
    """
    Dashboard detallado de ventas con gráficos
    """
    import json
    from django.core.serializers.json import DjangoJSONEncoder
    
    hoy = timezone.now().date()
    hace_30_dias = hoy - timedelta(days=30)
    
    # Ventas por día (últimos 30 días)
    ventas_por_dia = []
    for i in range(30):
        dia = hoy - timedelta(days=i)
        ventas_dia = Ventas.objects.filter(fecha__date=dia).aggregate(
            total=Sum('monto_total'),
            cantidad=Count('id_venta')
        )
        ventas_por_dia.append({
            'fecha': dia.strftime('%d/%m'),
            'total': float(ventas_dia['total'] or 0),
            'cantidad': ventas_dia['cantidad'],
        })
    
    ventas_por_dia.reverse()
    
    # Ventas por medio de pago
    ventas_por_medio_raw = Ventas.objects.filter(
        fecha__date__gte=hace_30_dias
    ).values('id_tipo_pago__descripcion').annotate(
        total=Sum('monto_total'),
        cantidad=Count('id_venta')
    ).order_by('-total')
    
    ventas_por_medio = [{
        'medio_pago': item['id_tipo_pago__descripcion'] or 'Sin especificar',
        'total': float(item['total'] or 0),
        'cantidad': item['cantidad']
    } for item in ventas_por_medio_raw]
    
    # Ventas por categoría
    ventas_por_categoria_raw = DetalleVenta.objects.filter(
        id_venta__fecha__date__gte=hace_30_dias
    ).values('id_producto__id_categoria__nombre').annotate(
        total=Sum(F('cantidad') * F('precio_unitario')),
        cantidad=Sum('cantidad')
    ).order_by('-total')[:10]
    
    ventas_por_categoria = [{
        'categoria': item['id_producto__id_categoria__nombre'] or 'Sin categoría',
        'total': float(item['total'] or 0),
        'cantidad': item['cantidad'] or 0
    } for item in ventas_por_categoria_raw]
    
    context = {
        'ventas_por_dia': ventas_por_dia,
        'ventas_por_dia_json': json.dumps(ventas_por_dia, cls=DjangoJSONEncoder),
        'ventas_por_medio': ventas_por_medio,
        'ventas_por_medio_json': json.dumps(ventas_por_medio, cls=DjangoJSONEncoder),
        'ventas_por_categoria': ventas_por_categoria,
        'ventas_por_categoria_json': json.dumps(ventas_por_categoria, cls=DjangoJSONEncoder),
    }
    
    return render(request, 'dashboard/ventas_detalle.html', context)


@login_required
def dashboard_stock_detalle(request):
    """
    Dashboard detallado de inventario
    """
    import json
    from django.core.serializers.json import DjangoJSONEncoder
    
    # Stock por categoría
    stock_por_categoria = []
    
    for categoria in Categoria.objects.all():
        productos = Producto.objects.filter(id_categoria=categoria, activo=True)
        stock_info = StockUnico.objects.filter(
            id_producto__in=productos
        ).aggregate(
            total_productos=Count('id_producto'),
            total_unidades=Sum('stock_actual'),
            # TODO: Calcular valor usando relación precios cuando esté implementado
            # valor_total=Sum(F('stock_actual') * F('id_producto__precio')),
            bajo_stock=Count('id_producto', filter=Q(stock_actual__lte=F('id_producto__stock_minimo')))
        )
        
        stock_por_categoria.append({
            'categoria': categoria.nombre,
            'productos': stock_info['total_productos'] or 0,
            'unidades': stock_info['total_unidades'] or 0,
            'valor': 0,  # TODO: Calcular con precios
            'bajo_stock': stock_info['bajo_stock'] or 0,
        })
    
    # Movimientos recientes de stock
    movimientos_recientes = MovimientosStock.objects.select_related(
        'id_producto', 'id_empleado_autoriza'
    ).order_by('-fecha_hora')[:20]
    
    context = {
        'stock_por_categoria': stock_por_categoria,
        'stock_por_categoria_json': json.dumps(stock_por_categoria, cls=DjangoJSONEncoder),
        'movimientos_recientes': movimientos_recientes,
    }
    
    return render(request, 'dashboard/stock_detalle.html', context)


@login_required
def invalidar_cache_dashboard(request):
    """
    Invalida el cache del dashboard para forzar actualización
    """
    from django.http import JsonResponse
    
    cache_key = f'dashboard_data_{request.user.id}'
    cache.delete(cache_key)
    
    return JsonResponse({
        'success': True,
        'message': 'Cache invalidado correctamente'
    })
