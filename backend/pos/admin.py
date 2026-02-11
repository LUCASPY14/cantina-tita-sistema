from django.contrib import admin
from .models import Venta, DetalleVenta, PagoVenta


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    """Admin para Ventas"""
    list_display = ('id_venta', 'nro_factura_venta', 'id_cliente', 'fecha', 'monto_total', 'estado_pago', 'estado', 'tipo_venta')
    list_filter = ('estado', 'estado_pago', 'tipo_venta', 'genera_factura_legal', 'fecha')
    search_fields = ('nro_factura_venta', 'id_cliente__nombre_completo', 'id_hijo__nombre_completo')
    date_hierarchy = 'fecha'
    readonly_fields = ('fecha',)
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nro_factura_venta', 'id_cliente', 'id_hijo', 'fecha')
        }),
        ('Empleado y Pago', {
            'fields': ('id_empleado_cajero', 'id_tipo_pago', 'tipo_venta')
        }),
        ('Montos', {
            'fields': ('monto_total', 'saldo_pendiente', 'estado_pago')
        }),
        ('Autorización (Crédito)', {
            'fields': ('autorizado_por', 'motivo_credito'),
            'classes': ('collapse',)
        }),
        ('Estado y Facturación', {
            'fields': ('estado', 'genera_factura_legal')
        }),
    )


@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    """Admin para Detalles de Venta"""
    list_display = ('id_detalle', 'id_venta', 'id_producto', 'cantidad', 'precio_unitario', 'subtotal_total')
    list_filter = ('id_venta__fecha',)
    search_fields = ('id_producto__descripcion', 'id_venta__nro_factura_venta')
    readonly_fields = ('subtotal_total',)


@admin.register(PagoVenta)
class PagoVentaAdmin(admin.ModelAdmin):
    """Admin para Pagos de Venta"""
    list_display = ('id_pago_venta', 'id_venta', 'id_medio_pago', 'monto_aplicado', 'fecha_pago', 'estado')
    list_filter = ('estado', 'fecha_pago', 'id_medio_pago')
    search_fields = ('referencia_transaccion', 'id_venta__nro_factura_venta', 'nro_tarjeta_usada__numero_tarjeta')
    readonly_fields = ('fecha_pago',)
    exclude = ('id_cierre',)  # Excluir porque la tabla cierres_caja no existe
