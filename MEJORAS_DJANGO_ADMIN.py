# MEJORAS PARA DJANGO ADMIN - CANTINA TITA
# ========================================

"""
Este documento contiene mejoras recomendadas para el Django Admin.
Aplica estas personalizaciones en tus archivos admin.py de cada app.
"""

# ============================================================================
# 1. VENTAS - Admin Mejorado con Inlines
# ============================================================================

from django.contrib import admin
from django.utils.html import format_html
# from .models import Venta, DetalleVenta, PagoVenta  # Importar desde tu app
# Placeholders para evitar errores de linting en archivo de documentación
Venta = DetalleVenta = PagoVenta = None
Producto = Tarjeta = CargaSaldo = ConsumoTarjeta = NotaCredito = None

class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1
    fields = ('producto', 'cantidad', 'precio_unitario', 'subtotal')
    readonly_fields = ('subtotal',)
    
    def subtotal(self, obj):
        if obj.cantidad and obj.precio_unitario:
            return f"Gs. {obj.cantidad * obj.precio_unitario:,.0f}"
        return "Gs. 0"
    subtotal.short_description = 'Subtotal'

class PagoVentaInline(admin.TabularInline):
    model = PagoVenta
    extra = 1
    fields = ('medio_pago', 'monto_aplicado', 'referencia_transaccion', 'fecha_pago')
    readonly_fields = ('fecha_pago',)

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('id_venta', 'fecha_badge', 'cliente_link', 'monto_total_badge', 'estado_badge', 'empleado')
    list_filter = ('estado', 'tipo_venta', 'fecha')
    search_fields = ('cliente__nombres', 'cliente__apellidos', 'cliente__ruc_ci')
    date_hierarchy = 'fecha'
    readonly_fields = ('monto_total', 'fecha')
    inlines = [DetalleVentaInline, PagoVentaInline]
    
    fieldsets = (
        ('Información Principal', {
            'fields': ('cliente', 'hijo', 'fecha', 'tipo_venta')
        }),
        ('Detalles Financieros', {
            'fields': ('monto_total', 'estado', 'documento')
        }),
        ('Personal', {
            'fields': ('empleado_cajero',)
        }),
    )
    
    def fecha_badge(self, obj):
        return format_html(
            '<span style="background-color: #e3f2fd; padding: 4px 8px; border-radius: 4px;">{}</span>',
            obj.fecha.strftime('%d/%m/%Y %H:%M')
        )
    fecha_badge.short_description = 'Fecha'
    
    def cliente_link(self, obj):
        if obj.cliente:
            return format_html(
                '<a href="/admin/ventas/cliente/{}/change/">{} {}</a>',
                obj.cliente.id_cliente,
                obj.cliente.nombres,
                obj.cliente.apellidos
            )
        return '-'
    cliente_link.short_description = 'Cliente'
    
    def monto_total_badge(self, obj):
        return format_html(
            '<span style="color: #2e7d32; font-weight: bold;">Gs. {:,.0f}</span>',
            obj.monto_total
        )
    monto_total_badge.short_description = 'Monto Total'
    
    def estado_badge(self, obj):
        colors = {
            'Completada': '#4caf50',
            'Pendiente': '#ff9800',
            'Anulada': '#f44336'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 12px; border-radius: 12px;">{}</span>',
            colors.get(obj.estado, '#999'),
            obj.estado
        )
    estado_badge.short_description = 'Estado'
    
    actions = ['marcar_como_completada', 'generar_reporte_pdf']
    
    def marcar_como_completada(self, request, queryset):
        updated = queryset.update(estado='Completada')
        self.message_user(request, f'{updated} ventas marcadas como completadas.')
    marcar_como_completada.short_description = 'Marcar como Completada'
    
    def generar_reporte_pdf(self, request, queryset):
        # Implementar generación de PDF
        self.message_user(request, 'Generación de PDF - Por implementar')
    generar_reporte_pdf.short_description = 'Generar Reporte PDF'


# ============================================================================
# 2. PRODUCTOS - Admin con Filtros Avanzados
# ============================================================================

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'descripcion', 'categoria', 'stock_badge', 'precio_badge', 'activo_badge')
    list_filter = ('activo', 'categoria', 'permite_stock_negativo')
    search_fields = ('codigo', 'descripcion')
    list_editable = ('activo',)
    readonly_fields = ('fecha_creacion',)
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'descripcion', 'categoria', 'unidad')
        }),
        ('Control de Stock', {
            'fields': ('stock_minimo', 'permite_stock_negativo'),
            'description': 'Configuración de inventario y alertas'
        }),
        ('Estado', {
            'fields': ('activo', 'fecha_creacion')
        }),
    )
    
    def stock_badge(self, obj):
        if obj.stock_minimo == 0:
            color = '#999'
            icon = '⚪'
        elif obj.stock_minimo < 10:
            color = '#f44336'
            icon = '🔴'
        elif obj.stock_minimo < 50:
            color = '#ff9800'
            icon = '🟠'
        else:
            color = '#4caf50'
            icon = '🟢'
        
        return format_html(
            '{} <span style="color: {}; font-weight: bold;">{}</span>',
            icon, color, obj.stock_minimo
        )
    stock_badge.short_description = 'Stock Mínimo'
    
    def precio_badge(self, obj):
        # Obtener precio desde historico_precios o precio_lista
        # Por ahora, mostrar placeholder
        return format_html('<span style="color: #1976d2;">Ver precios</span>')
    precio_badge.short_description = 'Precio'
    
    def activo_badge(self, obj):
        if obj.activo:
            return format_html('<span style="color: #4caf50;">✓ Activo</span>')
        return format_html('<span style="color: #999;">✗ Inactivo</span>')
    activo_badge.short_description = 'Estado'
    
    actions = ['activar_productos', 'desactivar_productos', 'alerta_stock_bajo']
    
    def activar_productos(self, request, queryset):
        updated = queryset.update(activo=True)
        self.message_user(request, f'{updated} productos activados.')
    activar_productos.short_description = 'Activar productos seleccionados'
    
    def desactivar_productos(self, request, queryset):
        updated = queryset.update(activo=False)
        self.message_user(request, f'{updated} productos desactivados.')
    desactivar_productos.short_description = 'Desactivar productos seleccionados'
    
    def alerta_stock_bajo(self, request, queryset):
        bajo = queryset.filter(stock_minimo__lt=10)
        self.message_user(request, f'{bajo.count()} productos con stock bajo.')
    alerta_stock_bajo.short_description = 'Verificar stock bajo'


# ============================================================================
# 3. TARJETAS Y RECARGAS - Admin Completo
# ============================================================================

@admin.register(Tarjeta)
class TarjetaAdmin(admin.ModelAdmin):
    list_display = ('nro_tarjeta', 'hijo_nombre', 'saldo_badge', 'estado_badge', 'fecha_emision')
    list_filter = ('estado', 'fecha_emision')
    search_fields = ('nro_tarjeta', 'hijo__nombre', 'hijo__apellido')
    readonly_fields = ('fecha_emision', 'saldo_actual')
    
    fieldsets = (
        ('Información de Tarjeta', {
            'fields': ('nro_tarjeta', 'hijo', 'fecha_emision')
        }),
        ('Estado y Saldo', {
            'fields': ('estado', 'saldo_actual'),
            'description': 'Saldo se actualiza automáticamente con recargas y consumos'
        }),
    )
    
    def hijo_nombre(self, obj):
        return f"{obj.hijo.nombre} {obj.hijo.apellido}"
    hijo_nombre.short_description = 'Estudiante'
    
    def saldo_badge(self, obj):
        color = '#4caf50' if obj.saldo_actual > 10000 else '#ff9800' if obj.saldo_actual > 0 else '#f44336'
        return format_html(
            '<span style="color: {}; font-weight: bold; font-size: 14px;">Gs. {:,.0f}</span>',
            color, obj.saldo_actual
        )
    saldo_badge.short_description = 'Saldo'
    
    def estado_badge(self, obj):
        colors = {'Activa': '#4caf50', 'Bloqueada': '#f44336', 'Inactiva': '#999'}
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 12px; border-radius: 12px;">{}</span>',
            colors.get(obj.estado, '#999'), obj.estado
        )
    estado_badge.short_description = 'Estado'
    
    actions = ['bloquear_tarjetas', 'desbloquear_tarjetas']
    
    def bloquear_tarjetas(self, request, queryset):
        updated = queryset.update(estado='Bloqueada')
        self.message_user(request, f'{updated} tarjetas bloqueadas.')
    bloquear_tarjetas.short_description = 'Bloquear tarjetas'
    
    def desbloquear_tarjetas(self, request, queryset):
        updated = queryset.update(estado='Activa')
        self.message_user(request, f'{updated} tarjetas desbloqueadas.')
    desbloquear_tarjetas.short_description = 'Desbloquear tarjetas'


@admin.register(CargaSaldo)
class CargaSaldoAdmin(admin.ModelAdmin):
    list_display = ('id_carga', 'nro_tarjeta', 'monto_badge', 'fecha_carga', 'cliente_origen')
    list_filter = ('fecha_carga',)
    search_fields = ('nro_tarjeta__nro_tarjeta', 'cliente_origen__nombres')
    date_hierarchy = 'fecha_carga'
    readonly_fields = ('fecha_carga',)
    
    def monto_badge(self, obj):
        return format_html(
            '<span style="color: #2e7d32; font-weight: bold;">Gs. {:,.0f}</span>',
            obj.monto_cargado
        )
    monto_badge.short_description = 'Monto Recargado'


# ============================================================================
# 4. CONSUMOS - Nuevo Admin
# ============================================================================

@admin.register(ConsumoTarjeta)
class ConsumoTarjetaAdmin(admin.ModelAdmin):
    list_display = ('id_consumo', 'nro_tarjeta', 'fecha_consumo', 'monto_badge', 'saldo_anterior', 'saldo_posterior')
    list_filter = ('fecha_consumo',)
    search_fields = ('nro_tarjeta__nro_tarjeta', 'detalle')
    date_hierarchy = 'fecha_consumo'
    readonly_fields = ('fecha_consumo', 'saldo_anterior', 'saldo_posterior')
    
    fieldsets = (
        ('Información del Consumo', {
            'fields': ('nro_tarjeta', 'fecha_consumo', 'detalle')
        }),
        ('Montos', {
            'fields': ('monto_consumido', 'saldo_anterior', 'saldo_posterior'),
            'description': 'Saldos se calculan automáticamente'
        }),
    )
    
    def monto_badge(self, obj):
        return format_html(
            '<span style="color: #d32f2f; font-weight: bold;">- Gs. {:,.0f}</span>',
            obj.monto_consumido
        )
    monto_badge.short_description = 'Monto Consumido'


# ============================================================================
# 5. DASHBOARD PERSONALIZADO (opcional)
# ============================================================================

from django.urls import path
from django.shortcuts import render
from django.db.models import Sum, Count
from datetime import date

class CantinaAdminSite(admin.AdminSite):
    site_header = 'Cantina Tita - Administración'
    site_title = 'Cantina Tita Admin'
    index_title = 'Panel de Control'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view), name='dashboard'),
        ]
        return custom_urls + urls
    
    def dashboard_view(self, request):
        # Estadísticas del día
        hoy = date.today()
        
        ventas_hoy = Venta.objects.filter(fecha__date=hoy).aggregate(
            total=Sum('monto_total'),
            cantidad=Count('id_venta')
        )
        
        recargas_hoy = CargaSaldo.objects.filter(fecha_carga__date=hoy).aggregate(
            total=Sum('monto_cargado'),
            cantidad=Count('id_carga')
        )
        
        context = {
            'ventas_hoy': ventas_hoy,
            'recargas_hoy': recargas_hoy,
            'title': 'Dashboard',
        }
        
        return render(request, 'admin/dashboard.html', context)

# Para usar el dashboard personalizado:
# admin_site = CantinaAdminSite(name='cantina_admin')
# Luego registrar todos los modelos con admin_site.register()


# ============================================================================
# 6. AUTOCOMPLETE FIELDS
# ============================================================================

# En VentaAdmin:
autocomplete_fields = ['cliente', 'hijo', 'empleado_cajero']

# Luego en ClienteAdmin:
search_fields = ['nombres', 'apellidos', 'ruc_ci']

# Y en ProductoAdmin para DetalleVentaInline:
autocomplete_fields = ['producto']


# ============================================================================
# 7. NOTAS DE CRÉDITO
# ============================================================================

@admin.register(NotaCredito)
class NotaCreditoAdmin(admin.ModelAdmin):
    list_display = ('id_nota', 'cliente', 'fecha', 'monto_badge', 'estado_badge', 'venta_original')
    list_filter = ('estado', 'fecha')
    search_fields = ('cliente__nombres', 'cliente__apellidos', 'motivo_devolucion')
    readonly_fields = ('fecha',)
    
    fieldsets = (
        ('Información Principal', {
            'fields': ('cliente', 'documento', 'fecha')
        }),
        ('Detalles', {
            'fields': ('venta_original', 'monto_total', 'motivo_devolucion')
        }),
        ('Estado', {
            'fields': ('estado',)
        }),
    )
    
    def monto_badge(self, obj):
        return format_html(
            '<span style="color: #d32f2f; font-weight: bold;">Gs. {:,.0f}</span>',
            obj.monto_total
        )
    monto_badge.short_description = 'Monto'
    
    def estado_badge(self, obj):
        colors = {'Emitida': '#ff9800', 'Aplicada': '#4caf50', 'Anulada': '#999'}
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 12px; border-radius: 12px;">{}</span>',
            colors.get(obj.estado, '#999'), obj.estado
        )
    estado_badge.short_description = 'Estado'


# ============================================================================
# RESUMEN DE MEJORAS IMPLEMENTADAS:
# ============================================================================
"""
✓ Inlines para detalle de ventas y pagos
✓ Badges coloridos para estados y montos
✓ Filtros avanzados por fecha, estado, categoría
✓ Acciones batch (marcar completadas, activar/desactivar)
✓ Links entre modelos relacionados
✓ Autocomplete fields para búsquedas rápidas
✓ Campos readonly calculados automáticamente
✓ Organización con fieldsets
✓ Dashboard personalizado (opcional)
✓ Formateo de moneda (Gs.)

PRÓXIMOS PASOS:
1. Aplicar estas mejoras en tus archivos admin.py
2. Crear template admin/dashboard.html si usas dashboard personalizado
3. Agregar permisos personalizados según rol de empleado
4. Implementar exportación a Excel/PDF en acciones
5. Crear reportes personalizados desde el admin
"""
