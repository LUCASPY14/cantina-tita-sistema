"""
Custom Admin Site for Cantina Tita
Provides personalized dashboard with statistics and quick access to key operations
"""

from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from datetime import date, timedelta, datetime
from decimal import Decimal


class CantinaAdminSite(admin.AdminSite):
    """
    Custom Admin Site with personalized dashboard
    """
    site_header = 'Cantina Tita - Sistema de Gestión'
    site_title = 'Cantina Tita Admin'
    index_title = 'Panel de Control Principal'
    
    def get_urls(self):
        """Add custom dashboard URL"""
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view), name='dashboard'),
        ]
        return custom_urls + urls
    
    def dashboard_view(self, request):
        """
        Dashboard view with comprehensive statistics
        """
        from gestion.models import (
            Ventas, CargasSaldo, ConsumoTarjeta, Tarjeta, 
            Producto, StockUnico, Cliente, Empleado,
            CierresCaja, NotasCredito, AlertasSistema,
            VistaStockAlerta, VistaSaldoClientes, Proveedor,
            Categoria, TiposPago
        )
        
        # Fecha actual
        hoy = date.today()
        inicio_mes = date(hoy.year, hoy.month, 1)
        inicio_semana = hoy - timedelta(days=hoy.weekday())
        
        # =====================================================================
        # ESTADÍSTICAS DE VENTAS
        # =====================================================================
        ventas_hoy = Ventas.objects.filter(
            fecha__date=hoy,
            estado='Completada'
        ).aggregate(
            total=Sum('monto_total'),
            cantidad=Count('id_venta')
        )
        
        ventas_semana = Ventas.objects.filter(
            fecha__date__gte=inicio_semana,
            estado='Completada'
        ).aggregate(
            total=Sum('monto_total'),
            cantidad=Count('id_venta')
        )
        
        ventas_mes = Ventas.objects.filter(
            fecha__date__gte=inicio_mes,
            estado='Completada'
        ).aggregate(
            total=Sum('monto_total'),
            cantidad=Count('id_venta')
        )
        
        # =====================================================================
        # ESTADÍSTICAS DE RECARGAS
        # =====================================================================
        recargas_hoy = CargasSaldo.objects.filter(
            fecha_carga__date=hoy
        ).aggregate(
            total=Sum('monto_cargado'),
            cantidad=Count('id_carga')
        )
        
        recargas_semana = CargasSaldo.objects.filter(
            fecha_carga__date__gte=inicio_semana
        ).aggregate(
            total=Sum('monto_cargado'),
            cantidad=Count('id_carga')
        )
        
        recargas_mes = CargasSaldo.objects.filter(
            fecha_carga__date__gte=inicio_mes
        ).aggregate(
            total=Sum('monto_cargado'),
            cantidad=Count('id_carga')
        )
        
        # =====================================================================
        # ESTADÍSTICAS DE CONSUMOS (TARJETAS)
        # =====================================================================
        consumos_hoy = ConsumoTarjeta.objects.filter(
            fecha_consumo__date=hoy
        ).aggregate(
            total=Sum('monto_consumido'),
            cantidad=Count('id_consumo')
        )
        
        consumos_semana = ConsumoTarjeta.objects.filter(
            fecha_consumo__date__gte=inicio_semana
        ).aggregate(
            total=Sum('monto_consumido'),
            cantidad=Count('id_consumo')
        )
        
        # =====================================================================
        # ESTADÍSTICAS DE TARJETAS
        # =====================================================================
        tarjetas_stats = {
            'total': Tarjeta.objects.count(),
            'activas': Tarjeta.objects.filter(estado='Activa').count(),
            'bloqueadas': Tarjeta.objects.filter(estado='Bloqueada').count(),
            'saldo_total': Tarjeta.objects.aggregate(
                total=Sum('saldo_actual')
            )['total'] or Decimal('0.00')
        }
        
        # Tarjetas con saldo bajo (menos de 10,000 Gs)
        tarjetas_saldo_bajo = Tarjeta.objects.filter(
            estado='Activa',
            saldo_actual__lt=10000
        ).count()
        
        # =====================================================================
        # ESTADÍSTICAS DE PRODUCTOS E INVENTARIO
        # =====================================================================
        productos_stats = {
            'total': Producto.objects.count(),
            'activos': Producto.objects.filter(activo=True).count(),
            'stock_bajo': Producto.objects.filter(
                stock_minimo__lte=10,
                activo=True
            ).count()
        }
        
        # Alertas de stock desde vista
        alertas_stock = VistaStockAlerta.objects.all()[:10]
        
        # =====================================================================
        # ESTADÍSTICAS DE CLIENTES
        # =====================================================================
        clientes_stats = {
            'total': Cliente.objects.count(),
            'activos': Cliente.objects.filter(activo=True).count(),
            'nuevos_mes': Cliente.objects.filter(
                fecha_registro__gte=inicio_mes
            ).count()
        }
        
        # Clientes con saldo a favor desde vista
        clientes_saldo_favor = VistaSaldoClientes.objects.filter(
            saldo_actual__gt=0
        )[:10]
        
        # =====================================================================
        # ESTADÍSTICAS DE EMPLEADOS Y CAJAS
        # =====================================================================
        empleados_stats = {
            'total': Empleado.objects.count(),
            'activos': Empleado.objects.filter(activo=True).count()
        }
        
        # Última caja cerrada
        ultimo_cierre = CierresCaja.objects.order_by('-fecha_hora_cierre').first()
        
        # =====================================================================
        # NOTAS DE CRÉDITO
        # =====================================================================
        notas_credito_mes = NotasCredito.objects.filter(
            fecha__gte=inicio_mes
        ).aggregate(
            total=Sum('monto_total'),
            cantidad=Count('id_nota')
        )
        
        # =====================================================================
        # ALERTAS DEL SISTEMA
        # =====================================================================
        alertas_pendientes = AlertasSistema.objects.filter(
            estado='Pendiente'
        ).order_by('-fecha_creacion')[:5]
        
        # =====================================================================
        # TOP 5 PRODUCTOS MÁS VENDIDOS (HOY)
        # =====================================================================
        from pos.models import DetalleVenta
        
        top_productos_hoy = DetalleVenta.objects.filter(
            id_venta__fecha__date=hoy,
            id_venta__estado='Completada'
        ).values(
            'id_producto__descripcion'
        ).annotate(
            cantidad_vendida=Sum('cantidad'),
            total_vendido=Sum('subtotal_total')
        ).order_by('-cantidad_vendida')[:5]
        
        # =====================================================================
        # PREPARAR CONTEXTO
        # =====================================================================
        context = {
            'title': 'Dashboard - Cantina Tita',
            'hoy': hoy,
            'inicio_semana': inicio_semana,
            'inicio_mes': inicio_mes,
            
            # Ventas
            'ventas_hoy': ventas_hoy,
            'ventas_semana': ventas_semana,
            'ventas_mes': ventas_mes,
            
            # Recargas
            'recargas_hoy': recargas_hoy,
            'recargas_semana': recargas_semana,
            'recargas_mes': recargas_mes,
            
            # Consumos
            'consumos_hoy': consumos_hoy,
            'consumos_semana': consumos_semana,
            
            # Tarjetas
            'tarjetas_stats': tarjetas_stats,
            'tarjetas_saldo_bajo': tarjetas_saldo_bajo,
            
            # Productos e Inventario
            'productos_stats': productos_stats,
            'alertas_stock': alertas_stock,
            
            # Clientes
            'clientes_stats': clientes_stats,
            'clientes_saldo_favor': clientes_saldo_favor,
            
            # Empleados y Cajas
            'empleados_stats': empleados_stats,
            'ultimo_cierre': ultimo_cierre,
            
            # Notas de Crédito
            'notas_credito_mes': notas_credito_mes,
            
            # Alertas
            'alertas_pendientes': alertas_pendientes,
            
            # Top Productos
            'top_productos_hoy': top_productos_hoy,
            
            # Datos para filtros de reportes
            'clientes_lista': Cliente.objects.filter(activo=True).order_by('apellidos', 'nombres')[:100],
            'proveedores_lista': Proveedor.objects.filter(activo=True).order_by('razon_social')[:50],
            'empleados_lista': Empleado.objects.filter(activo=True).order_by('nombre', 'apellido')[:50],
            'categorias_lista': Categoria.objects.filter(activo=True).order_by('nombre'),
            'tipos_pago': TiposPago.objects.filter(activo=True).order_by('descripcion'),
        }
        
        return render(request, 'admin/dashboard.html', context)
    
    def index(self, request, extra_context=None):
        """
        Override default admin index to redirect to dashboard
        """
        extra_context = extra_context or {}
        extra_context['dashboard_url'] = '/admin/dashboard/'
        return super().index(request, extra_context)


# Instancia del sitio admin personalizado
cantina_admin_site = CantinaAdminSite(name='cantina_admin')
