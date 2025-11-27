from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count
from datetime import date
# Import custom admin site
from .cantina_admin import cantina_admin_site
from .models import (
    # Catálogos y Tipos
    Categoria, TipoCliente, ListaPrecios, UnidadMedida, Impuesto, TipoRolGeneral,
    # Clientes
    Cliente, Hijo, Tarjeta,
    # Productos
    Producto, StockUnico,
    # Proveedores y Compras
    Proveedor, Compras, DetalleCompra, CtaCorrienteProv, CargasSaldo,
    # Empleados
    Empleado,
    # Empresa y Precios
    DatosEmpresa, PreciosPorLista, CostosHistoricos, HistoricoPrecios,
    # Usuarios Web
    UsuariosWebClientes,
    # Fiscalización
    PuntosExpedicion, Timbrados, DocumentosTributarios, DatosFacturacionElect, DatosFacturacionFisica,
    # Inventario
    MovimientosStock, AjustesInventario, DetalleAjuste,
    # Medios de Pago
    TiposPago, MediosPago, TarifasComision, Cajas, CierresCaja,
    # Ventas
    Ventas, DetalleVenta, PagosVenta, DetalleComisionVenta, ConciliacionPagos, CtaCorriente,
    # Notas de Crédito
    NotasCredito, DetalleNota,
    # Almuerzos
    PlanesAlmuerzo, SuscripcionesAlmuerzo, RegistroConsumoAlmuerzo, PagosAlmuerzoMensual,
    # Alertas y Auditoría
    AlertasSistema, SolicitudesNotificacion, AuditoriaEmpleados, AuditoriaUsuariosWeb, AuditoriaComisiones,
    # Vistas
    VistaStockAlerta, VistaSaldoClientes,
    # Nuevos modelos - 26 NOV 2025
    ConsumoTarjeta, VistaVentasDiaDetallado, VistaConsumosEstudiante, VistaStockCriticoAlertas,
    VistaRecargasHistorial, VistaResumenCajaDiario, VistaNotasCreditoDetallado,
)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['id_categoria', 'nombre', 'id_categoria_padre', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre']


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'descripcion', 'id_categoria', 'stock_badge', 'activo', 'activo_badge']
    list_filter = ['id_categoria', 'activo', 'permite_stock_negativo']
    search_fields = ['codigo', 'descripcion']
    list_editable = ['activo']
    readonly_fields = ['fecha_creacion']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'descripcion', 'id_categoria', 'id_unidad')
        }),
        ('Control de Stock', {
            'fields': ('stock_minimo', 'permite_stock_negativo'),
            'description': 'Configuración de inventario y alertas'
        }),
        ('Impuestos', {
            'fields': ('id_impuesto',)
        }),
        ('Estado', {
            'fields': ('activo', 'fecha_creacion')
        }),
    )
    
    def stock_badge(self, obj):
        if obj.stock_minimo is None or obj.stock_minimo == 0:
            return format_html('<span style="color: #999;">⚪ Sin definir</span>')
        elif obj.stock_minimo < 10:
            return format_html('<span style="color: #f44336;">🔴 {}</span>', obj.stock_minimo)
        elif obj.stock_minimo < 50:
            return format_html('<span style="color: #ff9800;">🟠 {}</span>', obj.stock_minimo)
        else:
            return format_html('<span style="color: #4caf50;">🟢 {}</span>', obj.stock_minimo)
    stock_badge.short_description = 'Stock Mínimo'
    
    def activo_badge(self, obj):
        if obj.activo:
            return format_html('<span style="color: #4caf50; font-weight: bold;">✓ Activo</span>')
        return format_html('<span style="color: #999;">✗ Inactivo</span>')
    activo_badge.short_description = 'Estado'
    
    actions = ['activar_productos', 'desactivar_productos']
    
    def activar_productos(self, request, queryset):
        updated = queryset.update(activo=True)
        self.message_user(request, f'{updated} productos activados.')
    activar_productos.short_description = 'Activar productos seleccionados'
    
    def desactivar_productos(self, request, queryset):
        updated = queryset.update(activo=False)
        self.message_user(request, f'{updated} productos desactivados.')
    desactivar_productos.short_description = 'Desactivar productos seleccionados'


@admin.register(TipoCliente)
class TipoClienteAdmin(admin.ModelAdmin):
    list_display = ['nombre_tipo', 'descripcion', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre_tipo']


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['ruc_ci', 'apellidos', 'nombres', 'razon_social', 'id_tipo_cliente', 'activo']
    list_filter = ['id_tipo_cliente', 'activo', 'ciudad']
    search_fields = ['ruc_ci', 'nombres', 'apellidos', 'razon_social']
    readonly_fields = ['fecha_registro']


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ['ruc', 'razon_social', 'telefono', 'email', 'ciudad', 'activo']
    list_filter = ['activo', 'ciudad']
    search_fields = ['ruc', 'razon_social']
    readonly_fields = ['fecha_registro']


@admin.register(StockUnico)
class StockUnicoAdmin(admin.ModelAdmin):
    list_display = ['id_producto', 'stock_actual', 'fecha_ultima_actualizacion']
    search_fields = ['id_producto__codigo', 'id_producto__descripcion']
    readonly_fields = ['fecha_ultima_actualizacion']


@admin.register(ListaPrecios)
class ListaPreciosAdmin(admin.ModelAdmin):
    list_display = ['nombre_lista', 'moneda', 'fecha_vigencia', 'activo']
    list_filter = ['activo', 'moneda']
    search_fields = ['nombre_lista']


@admin.register(UnidadMedida)
class UnidadMedidaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'abreviatura', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre']


@admin.register(Impuesto)
class ImpuestoAdmin(admin.ModelAdmin):
    list_display = ['nombre_impuesto', 'porcentaje', 'vigente_desde', 'vigente_hasta', 'activo']
    list_filter = ['activo', 'vigente_desde']
    search_fields = ['nombre_impuesto']


@admin.register(TipoRolGeneral)
class TipoRolGeneralAdmin(admin.ModelAdmin):
    list_display = ['nombre_rol', 'descripcion', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre_rol']


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'nombre', 'apellido', 'id_rol', 'email', 'activo']
    list_filter = ['id_rol', 'activo', 'ciudad']
    search_fields = ['nombre', 'apellido', 'usuario', 'email']
    readonly_fields = ['fecha_ingreso', 'contrasena_hash']


@admin.register(Hijo)
class HijoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'apellido', 'id_cliente_responsable', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre', 'apellido']


@admin.register(Tarjeta)
class TarjetaAdmin(admin.ModelAdmin):
    list_display = ['nro_tarjeta', 'hijo_nombre', 'saldo_badge', 'estado_badge', 'fecha_creacion']
    list_filter = ['estado', 'fecha_creacion']
    search_fields = ['nro_tarjeta', 'id_hijo__nombre', 'id_hijo__apellido']
    readonly_fields = ['fecha_creacion', 'saldo_actual']
    
    fieldsets = (
        ('Información de Tarjeta', {
            'fields': ('nro_tarjeta', 'id_hijo', 'fecha_creacion')
        }),
        ('Estado y Saldo', {
            'fields': ('estado', 'saldo_actual', 'saldo_alerta', 'fecha_vencimiento'),
            'description': 'Saldo se actualiza automáticamente con recargas y consumos'
        }),
    )
    
    def hijo_nombre(self, obj):
        return f"{obj.id_hijo.nombre} {obj.id_hijo.apellido}"
    hijo_nombre.short_description = 'Estudiante'
    
    def saldo_badge(self, obj):
        saldo = obj.saldo_actual
        if saldo > 10000:
            color = '#4caf50'
        elif saldo > 0:
            color = '#ff9800'
        else:
            color = '#f44336'
        saldo_formateado = '{:,.0f}'.format(saldo)
        return format_html(
            '<span style="color: {}; font-weight: bold; font-size: 14px;">Gs. {}</span>',
            color, saldo_formateado
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


# ==================== VISTAS DESHABILITADAS ====================
# Las vistas VistaStockAlerta y VistaSaldoClientes están comentadas
# porque las vistas MySQL correspondientes no existen en la base de datos

# @admin.register(VistaStockAlerta)
# class VistaStockAlertaAdmin(admin.ModelAdmin):
#     list_display = ['codigo', 'descripcion', 'stock_actual', 'stock_minimo']
#     search_fields = ['codigo', 'descripcion']
#     
#     def has_add_permission(self, request):
#         return False
#     
#     def has_delete_permission(self, request, obj=None):
#         return False
#     
#     def has_change_permission(self, request, obj=None):
#         return False


# @admin.register(VistaSaldoClientes)
# class VistaSaldoClientesAdmin(admin.ModelAdmin):
#     list_display = ['id_cliente', 'nombre_completo', 'saldo']
#     search_fields = ['nombre_completo']
#     
#     def has_add_permission(self, request):
#         return False
#     
#     def has_delete_permission(self, request, obj=None):
#         return False
#     
#     def has_change_permission(self, request, obj=None):
#         return False


# ==================== NUEVOS MODELOS ====================

# Infraestructura y Empresa
@admin.register(DatosEmpresa)
class DatosEmpresaAdmin(admin.ModelAdmin):
    list_display = ['razon_social', 'ruc', 'ciudad', 'telefono', 'activo']
    search_fields = ['razon_social', 'ruc', 'email']


# Precios y Costos
@admin.register(PreciosPorLista)
class PreciosPorListaAdmin(admin.ModelAdmin):
    list_display = ['id_producto', 'id_lista', 'precio_unitario_neto', 'fecha_vigencia']
    list_filter = ['id_lista']
    search_fields = ['id_producto__descripcion', 'id_producto__codigo']


@admin.register(CostosHistoricos)
class CostosHistoricosAdmin(admin.ModelAdmin):
    list_display = ['id_producto', 'costo_unitario_neto', 'fecha_compra', 'id_compra']
    list_filter = ['fecha_compra']
    search_fields = ['id_producto__descripcion', 'id_producto__codigo']


@admin.register(HistoricoPrecios)
class HistoricoPreciosAdmin(admin.ModelAdmin):
    list_display = ['id_producto', 'id_lista', 'precio_anterior', 'precio_nuevo', 'fecha_cambio', 'id_empleado_modifico']
    list_filter = ['fecha_cambio']
    search_fields = ['id_producto']


# Compras
@admin.register(Compras)
class ComprasAdmin(admin.ModelAdmin):
    list_display = ['id_compra', 'id_proveedor', 'fecha', 'monto_total']
    list_filter = ['fecha']
    search_fields = ['nro_factura', 'id_proveedor__razon_social']


@admin.register(DetalleCompra)
class DetalleCompraAdmin(admin.ModelAdmin):
    list_display = ['id_compra', 'id_producto', 'cantidad', 'costo_unitario_neto', 'subtotal_neto']
    search_fields = ['id_producto__descripcion', 'id_compra__nro_factura_proveedor']


@admin.register(CtaCorrienteProv)
class CtaCorrienteProvAdmin(admin.ModelAdmin):
    list_display = ['id_proveedor', 'tipo_movimiento', 'monto', 'fecha', 'saldo_acumulado']
    list_filter = ['tipo_movimiento', 'fecha']
    search_fields = ['id_proveedor__razon_social', 'referencia_doc']


@admin.register(CargasSaldo)
class CargasSaldoAdmin(admin.ModelAdmin):
    list_display = ['id_carga', 'nro_tarjeta', 'monto_badge', 'fecha_carga', 'id_cliente_origen']
    list_filter = ['fecha_carga']
    search_fields = ['nro_tarjeta__nro_tarjeta', 'id_cliente_origen__nombres']
    date_hierarchy = 'fecha_carga'
    readonly_fields = ['fecha_carga']
    
    def monto_badge(self, obj):
        monto_formateado = '{:,.0f}'.format(float(obj.monto_cargado))
        return format_html(
            '<span style="color: #2e7d32; font-weight: bold;">Gs. {}</span>',
            monto_formateado
        )
    monto_badge.short_description = 'Monto Recargado'


# Usuarios Web
@admin.register(UsuariosWebClientes)
class UsuariosWebClientesAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'id_cliente', 'ultimo_acceso', 'activo']
    list_filter = ['activo']
    search_fields = ['usuario']
    readonly_fields = ['contrasena_hash']


# Fiscalización
@admin.register(PuntosExpedicion)
class PuntosExpedicionAdmin(admin.ModelAdmin):
    list_display = ['codigo_establecimiento', 'codigo_punto_expedicion', 'descripcion_ubicacion', 'activo']
    list_filter = ['activo']


@admin.register(Timbrados)
class TimbradosAdmin(admin.ModelAdmin):
    list_display = ['nro_timbrado', 'tipo_documento', 'fecha_inicio', 'fecha_fin', 'es_electronico', 'activo']
    list_filter = ['tipo_documento', 'es_electronico', 'activo']
    search_fields = ['nro_timbrado']


@admin.register(DocumentosTributarios)
class DocumentosTributariosAdmin(admin.ModelAdmin):
    list_display = ['id_documento', 'nro_timbrado', 'nro_secuencial', 'fecha_emision', 'monto_total']
    list_filter = ['fecha_emision']
    search_fields = ['nro_secuencial']


@admin.register(DatosFacturacionElect)
class DatosFacturacionElectAdmin(admin.ModelAdmin):
    list_display = ['id_documento', 'cdc', 'estado_sifen', 'fecha_envio']
    list_filter = ['estado_sifen']
    search_fields = ['cdc']


@admin.register(DatosFacturacionFisica)
class DatosFacturacionFisicaAdmin(admin.ModelAdmin):
    list_display = ['id_documento', 'nro_preimpreso_interno']
    search_fields = ['nro_preimpreso_interno']


# Inventario
@admin.register(MovimientosStock)
class MovimientosStockAdmin(admin.ModelAdmin):
    list_display = ['id_producto', 'tipo_movimiento', 'cantidad', 'stock_resultante', 'fecha_hora']
    list_filter = ['tipo_movimiento', 'fecha_hora']
    search_fields = ['id_producto__descripcion', 'referencia_documento']
    readonly_fields = ['stock_resultante']
    
    fieldsets = (
        ('Información del Movimiento', {
            'fields': ('id_producto', 'tipo_movimiento', 'cantidad', 'fecha_hora')
        }),
        ('Referencias', {
            'fields': ('id_empleado_autoriza', 'id_venta', 'id_compra', 'referencia_documento')
        }),
        ('Stock Resultante (Automático)', {
            'fields': ('stock_resultante',),
            'description': '⚙️ Este campo se calcula automáticamente por el sistema. NO debe ser editado manualmente.'
        }),
    )


@admin.register(AjustesInventario)
class AjustesInventarioAdmin(admin.ModelAdmin):
    list_display = ['id_ajuste', 'tipo_ajuste', 'fecha_hora', 'id_empleado_responsable', 'estado']
    list_filter = ['tipo_ajuste', 'estado', 'fecha_hora']
    search_fields = ['motivo']


@admin.register(DetalleAjuste)
class DetalleAjusteAdmin(admin.ModelAdmin):
    list_display = ['id_ajuste', 'id_producto', 'cantidad_ajustada']
    search_fields = ['id_producto__descripcion']


# Medios de Pago
@admin.register(TiposPago)
class TiposPagoAdmin(admin.ModelAdmin):
    list_display = ['descripcion', 'activo']
    list_filter = ['activo']


@admin.register(MediosPago)
class MediosPagoAdmin(admin.ModelAdmin):
    list_display = ['descripcion', 'genera_comision', 'requiere_validacion', 'activo']
    list_filter = ['genera_comision', 'requiere_validacion', 'activo']


@admin.register(TarifasComision)
class TarifasComisionAdmin(admin.ModelAdmin):
    list_display = ['id_medio_pago', 'porcentaje_comision', 'monto_fijo_comision', 'fecha_inicio_vigencia', 'activo']
    list_filter = ['activo', 'fecha_inicio_vigencia']


@admin.register(Cajas)
class CajasAdmin(admin.ModelAdmin):
    list_display = ['nombre_caja', 'ubicacion', 'activo']
    list_filter = ['activo']


@admin.register(CierresCaja)
class CierresCajaAdmin(admin.ModelAdmin):
    list_display = ['id_caja', 'fecha_hora_apertura', 'fecha_hora_cierre', 'monto_inicial', 'monto_contado_fisico', 'diferencia_efectivo']
    list_filter = ['fecha_hora_apertura', 'fecha_hora_cierre']
    search_fields = ['id_caja__nombre_caja']


# Ventas
@admin.register(Ventas)
class VentasAdmin(admin.ModelAdmin):
    list_display = ['id_venta', 'id_cliente', 'tipo_venta', 'monto_total', 'fecha', 'estado']
    list_filter = ['tipo_venta', 'estado', 'fecha']
    search_fields = ['id_cliente__nombres', 'id_cliente__apellidos']


@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ['id_venta', 'id_producto', 'cantidad', 'precio_unitario_total', 'subtotal_total']
    search_fields = ['id_producto__descripcion']


@admin.register(PagosVenta)
class PagosVentaAdmin(admin.ModelAdmin):
    list_display = ['id_venta', 'id_medio_pago', 'monto_aplicado', 'fecha_pago']
    list_filter = ['id_medio_pago', 'fecha_pago']


@admin.register(DetalleComisionVenta)
class DetalleComisionVentaAdmin(admin.ModelAdmin):
    list_display = ['id_pago_venta', 'id_tarifa', 'monto_comision_calculada', 'porcentaje_aplicado']


@admin.register(ConciliacionPagos)
class ConciliacionPagosAdmin(admin.ModelAdmin):
    list_display = ['id_pago_venta', 'fecha_acreditacion', 'monto_acreditado', 'estado']
    list_filter = ['estado', 'fecha_acreditacion']


@admin.register(CtaCorriente)
class CtaCorrienteAdmin(admin.ModelAdmin):
    list_display = ['id_cliente', 'tipo_movimiento', 'monto', 'fecha', 'saldo_acumulado']
    list_filter = ['tipo_movimiento', 'fecha']
    search_fields = ['id_cliente__nombres', 'id_cliente__apellidos']


# Notas de Crédito
@admin.register(NotasCredito)
class NotasCreditoAdmin(admin.ModelAdmin):
    list_display = ['id_nota', 'id_cliente', 'monto_badge', 'fecha', 'estado_badge']
    list_filter = ['estado', 'fecha']
    search_fields = ['id_cliente__nombres', 'motivo_devolucion']
    readonly_fields = ['fecha']
    
    fieldsets = (
        ('Información Principal', {
            'fields': ('id_cliente', 'id_documento', 'fecha')
        }),
        ('Detalles', {
            'fields': ('id_venta_original', 'monto_total', 'motivo_devolucion')
        }),
        ('Estado', {
            'fields': ('estado',)
        }),
    )
    
    def monto_badge(self, obj):
        monto_formateado = '{:,.0f}'.format(float(obj.monto_total))
        return format_html(
            '<span style="color: #d32f2f; font-weight: bold;">Gs. {}</span>',
            monto_formateado
        )
    monto_badge.short_description = 'Monto'
    
    def estado_badge(self, obj):
        colors = {'Emitida': '#ff9800', 'Aplicada': '#4caf50', 'Anulada': '#999'}
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 12px; border-radius: 12px;">{}</span>',
            colors.get(obj.estado, '#999'), obj.estado
        )
    estado_badge.short_description = 'Estado'


@admin.register(DetalleNota)
class DetalleNotaAdmin(admin.ModelAdmin):
    list_display = ['id_nota', 'id_producto', 'cantidad', 'precio_unitario', 'subtotal']
    search_fields = ['id_producto__descripcion']


# =============================================================================
# NUEVOS ADMINS - 26 NOVIEMBRE 2025
# =============================================================================

@admin.register(ConsumoTarjeta)
class ConsumoTarjetaAdmin(admin.ModelAdmin):
    list_display = ['id_consumo', 'nro_tarjeta', 'monto_badge', 'saldo_anterior', 'saldo_posterior']
    list_filter = ['fecha_consumo']
    search_fields = ['nro_tarjeta__nro_tarjeta', 'detalle']
    readonly_fields = ['fecha_consumo', 'saldo_anterior', 'saldo_posterior']
    
    fieldsets = (
        ('Información del Consumo', {
            'fields': ('nro_tarjeta', 'fecha_consumo', 'detalle')
        }),
        ('Montos', {
            'fields': ('monto_consumido', 'saldo_anterior', 'saldo_posterior'),
            'description': 'Saldos se calculan automáticamente por trigger'
        }),
        ('Registro', {
            'fields': ('id_empleado_registro',)
        }),
    )
    
    def monto_badge(self, obj):
        monto_formateado = '{:,.0f}'.format(float(obj.monto_consumido))
        return format_html(
            '<span style="color: #d32f2f; font-weight: bold;">- Gs. {}</span>',
            monto_formateado
        )
    monto_badge.short_description = 'Monto Consumido'


# =============================================================================
# ADMINS PARA VISTAS SQL (Solo lectura)
# =============================================================================

@admin.register(VistaVentasDiaDetallado)
class VistaVentasDiaDetalladoAdmin(admin.ModelAdmin):
    list_display = ['id_venta', 'fecha', 'cliente_completo', 'monto_total_badge', 'total_pagado', 'saldo_pendiente']
    list_filter = ['fecha']
    search_fields = ['cliente_completo', 'productos']
    
    def monto_total_badge(self, obj):
        monto_formateado = '{:,.0f}'.format(obj.monto_total)
        return format_html('<span style="color: #2e7d32; font-weight: bold;">Gs. {}</span>', monto_formateado)
    monto_total_badge.short_description = 'Monto Total'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(VistaConsumosEstudiante)
class VistaConsumosEstudianteAdmin(admin.ModelAdmin):
    list_display = ['estudiante', 'nro_tarjeta', 'saldo_badge', 'total_consumos', 'total_recargas']
    search_fields = ['estudiante', 'nro_tarjeta']
    
    def saldo_badge(self, obj):
        saldo = obj.saldo_actual
        color = '#4caf50' if saldo > 10000 else '#ff9800' if saldo > 0 else '#f44336'
        saldo_formateado = '{:,.0f}'.format(saldo)
        return format_html('<span style="color: {}; font-weight: bold;">Gs. {}</span>', color, saldo_formateado)
    saldo_badge.short_description = 'Saldo Actual'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(VistaStockCriticoAlertas)
class VistaStockCriticoAlertasAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'descripcion', 'nombre_categoria', 'stock_minimo', 'nivel_alerta_badge']
    list_filter = ['nombre_categoria', 'nivel_alerta']
    search_fields = ['codigo', 'descripcion']
    
    def nivel_alerta_badge(self, obj):
        colors = {
            'CRÍTICO - SIN STOCK': '#f44336',
            'URGENTE': '#ff5722',
            'BAJO': '#ff9800',
            'ATENCIÓN': '#ffc107',
            'REQUIERE ATENCIÓN': '#ff9800'
        }
        color = colors.get(obj.nivel_alerta, '#999')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 12px; border-radius: 12px; font-weight: bold;">{}</span>',
            color, obj.nivel_alerta
        )
    nivel_alerta_badge.short_description = 'Nivel de Alerta'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(VistaRecargasHistorial)
class VistaRecargasHistorialAdmin(admin.ModelAdmin):
    list_display = ['id_carga', 'estudiante', 'monto_badge', 'saldo_actual_tarjeta']
    search_fields = ['estudiante', 'responsable', 'nro_tarjeta']
    
    def monto_badge(self, obj):
        monto_formateado = '{:,.0f}'.format(obj.monto_cargado)
        return format_html('<span style="color: #2e7d32; font-weight: bold;">Gs. {}</span>', monto_formateado)
    monto_badge.short_description = 'Monto Recargado'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(VistaResumenCajaDiario)
class VistaResumenCajaDiarioAdmin(admin.ModelAdmin):
    list_display = ['fecha', 'total_ventas', 'monto_ventas_badge', 'total_recargas', 'monto_recargas_badge', 'total_ingresos_badge']
    list_filter = ['fecha']
    
    def monto_ventas_badge(self, obj):
        monto_formateado = '{:,.0f}'.format(float(obj.monto_total_ventas))
        return format_html('<span style="color: #1976d2; font-weight: bold;">Gs. {}</span>', monto_formateado)
    monto_ventas_badge.short_description = 'Monto Ventas'
    
    def monto_recargas_badge(self, obj):
        monto_formateado = '{:,.0f}'.format(float(obj.monto_total_recargas))
        return format_html('<span style="color: #388e3c; font-weight: bold;">Gs. {}</span>', monto_formateado)
    monto_recargas_badge.short_description = 'Monto Recargas'
    
    def total_ingresos_badge(self, obj):
        monto_formateado = '{:,.0f}'.format(float(obj.total_ingresos_dia))
        return format_html('<span style="color: #2e7d32; font-weight: bold; font-size: 14px;">Gs. {}</span>', monto_formateado)
    total_ingresos_badge.short_description = 'Total Ingresos'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(VistaNotasCreditoDetallado)
class VistaNotasCreditoDetalladoAdmin(admin.ModelAdmin):
    list_display = ['id_nota', 'cliente', 'monto_badge', 'estado_badge', 'venta_origen']
    list_filter = ['estado']
    search_fields = ['cliente', 'ruc_ci', 'motivo_devolucion']
    
    def monto_badge(self, obj):
        monto_formateado = '{:,.0f}'.format(float(obj.monto_total))
        return format_html('<span style="color: #d32f2f; font-weight: bold;">Gs. {}</span>', monto_formateado)
    monto_badge.short_description = 'Monto'
    
    def estado_badge(self, obj):
        colors = {'Emitida': '#ff9800', 'Aplicada': '#4caf50', 'Anulada': '#999'}
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 12px; border-radius: 12px;">{}</span>',
            colors.get(obj.estado, '#999'), obj.estado
        )
    estado_badge.short_description = 'Estado'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


# Almuerzos
@admin.register(PlanesAlmuerzo)
class PlanesAlmuerzoAdmin(admin.ModelAdmin):
    list_display = ['nombre_plan', 'precio_mensual', 'dias_semana_incluidos', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre_plan']


@admin.register(SuscripcionesAlmuerzo)
class SuscripcionesAlmuerzoAdmin(admin.ModelAdmin):
    list_display = ['id_hijo', 'id_plan_almuerzo', 'fecha_inicio', 'fecha_fin', 'estado']
    list_filter = ['estado', 'fecha_inicio']
    search_fields = ['id_hijo__nombre', 'id_hijo__apellido']


@admin.register(RegistroConsumoAlmuerzo)
class RegistroConsumoAlmuerzoAdmin(admin.ModelAdmin):
    list_display = ['id_hijo', 'fecha_consumo', 'hora_registro', 'id_suscripcion']
    list_filter = ['fecha_consumo']
    search_fields = ['id_hijo__nombre', 'id_hijo__apellido']


@admin.register(PagosAlmuerzoMensual)
class PagosAlmuerzoMensualAdmin(admin.ModelAdmin):
    list_display = ['id_suscripcion', 'mes_pagado', 'monto_pagado', 'fecha_pago', 'estado']
    list_filter = ['estado', 'mes_pagado']


# Alertas
@admin.register(AlertasSistema)
class AlertasSistemaAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'mensaje', 'fecha_creacion', 'estado', 'fecha_leida', 'fecha_resolucion']
    list_filter = ['tipo', 'estado', 'fecha_creacion']
    search_fields = ['mensaje', 'observaciones']


@admin.register(SolicitudesNotificacion)
class SolicitudesNotificacionAdmin(admin.ModelAdmin):
    list_display = ['id_cliente', 'destino', 'estado', 'fecha_solicitud', 'fecha_envio']
    list_filter = ['destino', 'estado']
    search_fields = ['id_cliente__nombres', 'mensaje']


# Auditoría
@admin.register(AuditoriaEmpleados)
class AuditoriaEmpleadosAdmin(admin.ModelAdmin):
    list_display = ['id_empleado', 'campo_modificado', 'fecha_cambio', 'ip_origen']
    list_filter = ['campo_modificado', 'fecha_cambio']
    search_fields = ['id_empleado__nombre', 'campo_modificado']


@admin.register(AuditoriaUsuariosWeb)
class AuditoriaUsuariosWebAdmin(admin.ModelAdmin):
    list_display = ['id_cliente', 'campo_modificado', 'fecha_cambio', 'ip_origen']
    list_filter = ['fecha_cambio']
    search_fields = ['id_cliente__nombres', 'campo_modificado', 'ip_origen']


@admin.register(AuditoriaComisiones)
class AuditoriaComisionesAdmin(admin.ModelAdmin):
    list_display = ['id_tarifa', 'campo_modificado', 'fecha_cambio', 'valor_anterior', 'valor_nuevo', 'id_empleado_modifico']
    list_filter = ['campo_modificado', 'fecha_cambio']
    search_fields = ['id_tarifa__id_medio_pago__descripcion', 'campo_modificado']


# Vistas
@admin.register(VistaStockAlerta)
class VistaStockAlertaAdmin(admin.ModelAdmin):
    list_display = ['producto', 'codigo', 'categoria', 'stock_actual', 'stock_minimo', 'cantidad_faltante', 'nivel_alerta']
    list_filter = ['nivel_alerta', 'categoria']
    search_fields = ['producto', 'codigo']
    ordering = ['-nivel_alerta', '-cantidad_faltante']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(VistaSaldoClientes)
class VistaSaldoClientesAdmin(admin.ModelAdmin):
    list_display = ['nombre_completo', 'ruc_ci', 'tipo_cliente', 'saldo_actual', 'ultima_actualizacion', 'total_movimientos']
    list_filter = ['tipo_cliente']
    search_fields = ['nombre_completo', 'nombres', 'apellidos', 'ruc_ci']
    ordering = ['-saldo_actual']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


# ============================================================================
# REGISTRO DE MODELOS EN EL ADMIN PERSONALIZADO
# ============================================================================

# Registrar todos los modelos admin en el sitio personalizado
cantina_admin_site.register(Categoria, CategoriaAdmin)
cantina_admin_site.register(Producto, ProductoAdmin)
cantina_admin_site.register(TipoCliente, TipoClienteAdmin)
cantina_admin_site.register(Cliente, ClienteAdmin)
cantina_admin_site.register(Hijo, HijoAdmin)
cantina_admin_site.register(Tarjeta, TarjetaAdmin)
cantina_admin_site.register(StockUnico, StockUnicoAdmin)
cantina_admin_site.register(Proveedor, ProveedorAdmin)
cantina_admin_site.register(Compras, ComprasAdmin)
cantina_admin_site.register(DetalleCompra, DetalleCompraAdmin)
cantina_admin_site.register(CtaCorrienteProv, CtaCorrienteProvAdmin)
cantina_admin_site.register(CargasSaldo, CargasSaldoAdmin)
cantina_admin_site.register(Empleado, EmpleadoAdmin)
cantina_admin_site.register(DatosEmpresa, DatosEmpresaAdmin)
cantina_admin_site.register(UnidadMedida, UnidadMedidaAdmin)
cantina_admin_site.register(Impuesto, ImpuestoAdmin)
cantina_admin_site.register(ListaPrecios, ListaPreciosAdmin)
cantina_admin_site.register(PreciosPorLista, PreciosPorListaAdmin)
cantina_admin_site.register(HistoricoPrecios, HistoricoPreciosAdmin)
cantina_admin_site.register(CostosHistoricos, CostosHistoricosAdmin)
cantina_admin_site.register(UsuariosWebClientes, UsuariosWebClientesAdmin)
cantina_admin_site.register(PuntosExpedicion, PuntosExpedicionAdmin)
cantina_admin_site.register(Timbrados, TimbradosAdmin)
cantina_admin_site.register(DocumentosTributarios, DocumentosTributariosAdmin)
cantina_admin_site.register(DatosFacturacionElect, DatosFacturacionElectAdmin)
cantina_admin_site.register(DatosFacturacionFisica, DatosFacturacionFisicaAdmin)
cantina_admin_site.register(MovimientosStock, MovimientosStockAdmin)
cantina_admin_site.register(AjustesInventario, AjustesInventarioAdmin)
cantina_admin_site.register(DetalleAjuste, DetalleAjusteAdmin)
cantina_admin_site.register(TiposPago, TiposPagoAdmin)
cantina_admin_site.register(MediosPago, MediosPagoAdmin)
cantina_admin_site.register(TarifasComision, TarifasComisionAdmin)
cantina_admin_site.register(Cajas, CajasAdmin)
cantina_admin_site.register(CierresCaja, CierresCajaAdmin)
cantina_admin_site.register(Ventas, VentasAdmin)
cantina_admin_site.register(DetalleVenta, DetalleVentaAdmin)
cantina_admin_site.register(PagosVenta, PagosVentaAdmin)
cantina_admin_site.register(DetalleComisionVenta, DetalleComisionVentaAdmin)
cantina_admin_site.register(ConciliacionPagos, ConciliacionPagosAdmin)
cantina_admin_site.register(CtaCorriente, CtaCorrienteAdmin)
cantina_admin_site.register(NotasCredito, NotasCreditoAdmin)
cantina_admin_site.register(DetalleNota, DetalleNotaAdmin)
cantina_admin_site.register(PlanesAlmuerzo, PlanesAlmuerzoAdmin)
cantina_admin_site.register(SuscripcionesAlmuerzo, SuscripcionesAlmuerzoAdmin)
cantina_admin_site.register(RegistroConsumoAlmuerzo, RegistroConsumoAlmuerzoAdmin)
cantina_admin_site.register(PagosAlmuerzoMensual, PagosAlmuerzoMensualAdmin)
cantina_admin_site.register(AlertasSistema, AlertasSistemaAdmin)
cantina_admin_site.register(SolicitudesNotificacion, SolicitudesNotificacionAdmin)
cantina_admin_site.register(AuditoriaEmpleados, AuditoriaEmpleadosAdmin)
cantina_admin_site.register(AuditoriaUsuariosWeb, AuditoriaUsuariosWebAdmin)
cantina_admin_site.register(AuditoriaComisiones, AuditoriaComisionesAdmin)
cantina_admin_site.register(VistaStockAlerta, VistaStockAlertaAdmin)
cantina_admin_site.register(VistaSaldoClientes, VistaSaldoClientesAdmin)
cantina_admin_site.register(ConsumoTarjeta, ConsumoTarjetaAdmin)
cantina_admin_site.register(TipoRolGeneral, TipoRolGeneralAdmin)

# Registrar vistas adicionales en el admin personalizado
cantina_admin_site.register(VistaVentasDiaDetallado, VistaVentasDiaDetalladoAdmin)
cantina_admin_site.register(VistaConsumosEstudiante, VistaConsumosEstudianteAdmin)
cantina_admin_site.register(VistaStockCriticoAlertas, VistaStockCriticoAlertasAdmin)
cantina_admin_site.register(VistaRecargasHistorial, VistaRecargasHistorialAdmin)
cantina_admin_site.register(VistaResumenCajaDiario, VistaResumenCajaDiarioAdmin)
cantina_admin_site.register(VistaNotasCreditoDetallado, VistaNotasCreditoDetalladoAdmin)
