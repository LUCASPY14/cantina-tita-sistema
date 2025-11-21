from django.contrib import admin
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
)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['id_categoria', 'nombre', 'id_categoria_padre', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre']


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'descripcion', 'id_categoria', 'stock_minimo', 'activo']
    list_filter = ['id_categoria', 'activo']
    search_fields = ['codigo', 'descripcion']
    readonly_fields = ['fecha_creacion']


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
    list_display = ['nro_tarjeta', 'id_hijo', 'saldo_actual', 'estado']
    list_filter = ['estado']
    search_fields = ['nro_tarjeta']
    readonly_fields = ['fecha_creacion']


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
    list_display = ['nro_tarjeta', 'monto_cargado', 'fecha_carga', 'referencia']
    list_filter = ['fecha_carga']
    search_fields = ['nro_tarjeta__nro_tarjeta', 'referencia']


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
    list_display = ['id_nota', 'id_cliente', 'monto_total', 'fecha', 'estado']
    list_filter = ['estado', 'fecha']
    search_fields = ['id_cliente__nombres']


@admin.register(DetalleNota)
class DetalleNotaAdmin(admin.ModelAdmin):
    list_display = ['id_nota', 'id_producto', 'cantidad', 'precio_unitario', 'subtotal']
    search_fields = ['id_producto__descripcion']


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
