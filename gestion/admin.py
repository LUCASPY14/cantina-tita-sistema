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
    Proveedor, Compras, DetalleCompra, CargasSaldo,
    # Empleados
    Empleado,
    # Empresa y Precios
    DatosEmpresa, PreciosPorLista, CostosHistoricos, HistoricoPrecios,
    # Usuarios Web
    UsuariosWebClientes, UsuarioPortal,
    # Fiscalización
    PuntosExpedicion, Timbrados, DocumentosTributarios, DatosFacturacionElect, DatosFacturacionFisica,
    # Inventario
    MovimientosStock, AjustesInventario, DetalleAjuste,
    # Medios de Pago
    TiposPago, MediosPago, TarifasComision, Cajas, CierresCaja,
    # Ventas
    Ventas, DetalleVenta, PagosVenta, DetalleComisionVenta, ConciliacionPagos,
    # Notas de Crédito
    NotasCreditoCliente, DetalleNota,
    # Almuerzos
    PlanesAlmuerzo, SuscripcionesAlmuerzo, RegistroConsumoAlmuerzo, PagosAlmuerzoMensual,
    # Alertas y Auditoría
    AlertasSistema, SolicitudesNotificacion, AuditoriaEmpleados, AuditoriaUsuariosWeb, AuditoriaComisiones,
    # Vistas
    VistaStockAlerta, VistaSaldoClientes,
    # Nuevos modelos - 26 NOV 2025
    ConsumoTarjeta, VistaVentasDiaDetallado, VistaConsumosEstudiante, VistaStockCriticoAlertas,
    VistaRecargasHistorial, VistaResumenCajaDiario, VistaNotasCreditoDetallado,
    # Gestión Académica - 08 DIC 2025
    Grado, HistorialGradoHijo,
    # Alérgenos y Promociones - 08 DIC 2025
    Alergeno, ProductoAlergeno, Promocion, ProductoPromocion, CategoriaPromocion, PromocionAplicada,
)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['id_categoria', 'nombre', 'id_categoria_padre', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre']


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['codigo_barra', 'descripcion', 'id_categoria', 'stock_badge', 'activo', 'activo_badge']
    list_filter = ['id_categoria', 'activo', 'permite_stock_negativo']
    search_fields = ['codigo_barra', 'descripcion']
    list_editable = ['activo']
    # readonly_fields = ['fecha_creacion']  # Campo no existe en este modelo
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo_barra', 'descripcion', 'id_categoria', 'id_unidad_de_medida')
        }),
        ('Control de Stock', {
            'fields': ('stock_minimo', 'permite_stock_negativo'),
            'description': 'Configuración de inventario y alertas'
        }),
        ('Impuestos', {
            'fields': ('id_impuesto',)
        }),
        ('Estado', {
            'fields': ('activo',)
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
    list_display = ['nombre', 'apellido', 'id_cliente_responsable', 'grado', 'tiene_restricciones', 'activo']
    list_filter = ['activo', 'grado']
    search_fields = ['nombre', 'apellido', 'restricciones_compra']
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre', 'apellido', 'id_cliente_responsable', 'fecha_nacimiento', 'grado')
        }),
        ('Restricciones Alimentarias', {
            'fields': ('restricciones_compra',),
            'description': '⚠️ Ingrese restricciones alimentarias, alergias o intolerancias (ej: "Alérgico al maní, intolerante a la lactosa")'
        }),
        ('Foto e Identificación', {
            'fields': ('foto_perfil', 'fecha_foto'),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
    )
    
    def tiene_restricciones(self, obj):
        return bool(obj.restricciones_compra)
    tiene_restricciones.boolean = True
    tiene_restricciones.short_description = '⚠️ Restricciones'


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


@admin.register(CargasSaldo)
class CargasSaldoAdmin(admin.ModelAdmin):
    list_display = ['id_carga', 'nro_tarjeta', 'monto_badge', 'fecha_carga', 'id_cliente_origen']
    list_filter = ['fecha_carga']
    search_fields = ['nro_tarjeta__nro_tarjeta', 'id_cliente_origen__nombres']
    # date_hierarchy removed due to MySQL timezone tables requirement
    readonly_fields = ['fecha_carga']
    
    def monto_badge(self, obj):
        monto_formateado = '{:,.0f}'.format(float(obj.monto_cargado))
        return format_html(
            '<span style="color: #2e7d32; font-weight: bold;">Gs. {}</span>',
            monto_formateado
        )
    monto_badge.short_description = 'Monto Recargado'


# Usuarios Web
# SISTEMA LEGACY - DESHABILITADO
# Usar UsuarioPortal en su lugar (modelo nuevo para portal de clientes)
# @admin.register(UsuariosWebClientes)
class UsuariosWebClientesAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'id_cliente', 'ultimo_acceso', 'activo']
    list_filter = ['activo']
    search_fields = ['usuario', 'id_cliente__nombres', 'id_cliente__apellidos']
    readonly_fields = ['ultimo_acceso', 'campo_nueva_contrasena']
    actions = ['resetear_contrasena_a_ruc']
    
    fieldsets = (
        ('Información del Usuario', {
            'fields': ('id_cliente', 'usuario', 'activo', 'ultimo_acceso')
        }),
        ('Cambiar Contraseña', {
            'fields': ('campo_nueva_contrasena',),
            'description': 'Para cambiar la contraseña, use el campo de abajo o la acción "Resetear contraseña a RUC/CI" desde la lista.'
        }),
    )
    
    def campo_nueva_contrasena(self, obj):
        """Renderiza un campo HTML para cambiar contraseña"""
        if obj and obj.pk:
            html = f'''
            <div style="margin: 10px 0;">
                <input type="password" name="nueva_contrasena_manual" 
                       placeholder="Ingrese nueva contraseña" 
                       style="width: 300px; padding: 8px; border: 1px solid #ccc; border-radius: 4px;">
                <p style="color: #666; font-size: 12px; margin-top: 5px;">
                    Deje vacío para mantener la contraseña actual. 
                    RUC/CI actual del cliente: <strong>{obj.id_cliente.ruc_ci}</strong>
                </p>
            </div>
            '''
        else:
            html = '<p>Al crear el usuario, la contraseña será el RUC/CI del cliente automáticamente.</p>'
        
        from django.utils.safestring import mark_safe
        return mark_safe(html)
    
    campo_nueva_contrasena.short_description = "Nueva Contraseña"
    
    def save_model(self, request, obj, form, change):
        """Procesa la contraseña al guardar"""
        from django.contrib.auth.hashers import make_password
        
        # Obtener contraseña del campo HTML personalizado
        nueva_password = request.POST.get('nueva_contrasena_manual', '').strip()
        
        if nueva_password:
            # Se ingresó una contraseña nueva manualmente
            obj.contrasena_hash = make_password(nueva_password)
            self.message_user(
                request,
                f'✓ Contraseña actualizada exitosamente para usuario "{obj.usuario}"',
                level='SUCCESS'
            )
        elif not change or not obj.contrasena_hash:
            # Nueva instancia o sin contraseña: usar RUC/CI como contraseña temporal
            password_temporal = obj.id_cliente.ruc_ci
            obj.contrasena_hash = make_password(password_temporal)
            self.message_user(
                request,
                f'✓ Usuario creado. Contraseña temporal: <strong>{password_temporal}</strong> (RUC/CI del cliente)',
                level='WARNING'
            )
        
        super().save_model(request, obj, form, change)
    
    @admin.action(description='🔑 Resetear contraseña a RUC/CI del cliente')
    def resetear_contrasena_a_ruc(self, request, queryset):
        """Acción para resetear contraseña de usuarios seleccionados a su RUC/CI"""
        from django.contrib.auth.hashers import make_password
        
        count = 0
        detalles = []
        for usuario_web in queryset:
            password_temporal = usuario_web.id_cliente.ruc_ci
            usuario_web.contrasena_hash = make_password(password_temporal)
            usuario_web.save()
            detalles.append(f"{usuario_web.usuario} → {password_temporal}")
            count += 1
        
        mensaje = f'✓ {count} contraseña(s) reseteada(s). Nuevas contraseñas (RUC/CI): {", ".join(detalles)}'
        self.message_user(request, mensaje, level='SUCCESS')


@admin.register(UsuarioPortal)
class UsuarioPortalAdmin(admin.ModelAdmin):
    """Admin para UsuarioPortal - Portal de Padres (sistema nuevo)"""
    list_display = ['email', 'cliente', 'email_verificado', 'activo', 'ultimo_acceso', 'fecha_registro']
    list_filter = ['activo', 'email_verificado', 'fecha_registro']
    search_fields = ['email', 'cliente__nombres', 'cliente__apellidos', 'cliente__ruc_ci']
    readonly_fields = ['fecha_registro', 'ultimo_acceso', 'campo_nueva_password']
    actions = ['resetear_password_a_ruc', 'marcar_email_verificado']
    
    fieldsets = (
        ('Información del Usuario', {
            'fields': ('cliente', 'email', 'email_verificado', 'activo')
        }),
        ('Acceso', {
            'fields': ('fecha_registro', 'ultimo_acceso')
        }),
        ('Cambiar Contraseña', {
            'fields': ('campo_nueva_password',),
            'description': 'Para cambiar la contraseña, use el campo de abajo o la acción "Resetear password a RUC/CI".'
        }),
    )
    
    def campo_nueva_password(self, obj):
        """Renderiza campo para cambiar contraseña"""
        if obj and obj.pk:
            html = f'''
            <div style="margin: 10px 0;">
                <input type="password" name="nueva_password_portal" 
                       placeholder="Ingrese nueva contraseña" 
                       style="width: 300px; padding: 8px; border: 1px solid #ccc; border-radius: 4px;">
                <p style="color: #666; font-size: 12px; margin-top: 5px;">
                    Deje vacío para mantener la contraseña actual. 
                    RUC/CI del cliente: <strong>{obj.cliente.ruc_ci}</strong>
                </p>
            </div>
            '''
        else:
            html = '<p>Al crear el usuario, la contraseña será el RUC/CI del cliente automáticamente.</p>'
        
        from django.utils.safestring import mark_safe
        return mark_safe(html)
    
    campo_nueva_password.short_description = "Nueva Contraseña"
    
    def save_model(self, request, obj, form, change):
        """Procesa la contraseña al guardar"""
        from django.contrib.auth.hashers import make_password
        
        # Obtener contraseña del campo HTML
        nueva_password = request.POST.get('nueva_password_portal', '').strip()
        
        if nueva_password:
            obj.password_hash = make_password(nueva_password)
            self.message_user(
                request,
                f'✓ Contraseña actualizada para {obj.email}',
                level='SUCCESS'
            )
        elif not change or not obj.password_hash:
            # Usuario nuevo: usar RUC/CI
            password_temporal = obj.cliente.ruc_ci
            obj.password_hash = make_password(password_temporal)
            self.message_user(
                request,
                f'✓ Usuario creado. Contraseña temporal: <strong>{password_temporal}</strong> (RUC/CI)',
                level='WARNING'
            )
        
        super().save_model(request, obj, form, change)
    
    @admin.action(description='🔑 Resetear password a RUC/CI del cliente')
    def resetear_password_a_ruc(self, request, queryset):
        """Resetea contraseñas al RUC/CI del cliente"""
        from django.contrib.auth.hashers import make_password
        
        count = 0
        detalles = []
        for usuario in queryset:
            password_temporal = usuario.cliente.ruc_ci
            usuario.password_hash = make_password(password_temporal)
            usuario.save()
            detalles.append(f"{usuario.email} → {password_temporal}")
            count += 1
        
        mensaje = f'✓ {count} contraseña(s) reseteada(s): {", ".join(detalles)}'
        self.message_user(request, mensaje, level='SUCCESS')
    
    @admin.action(description='✅ Marcar email como verificado')
    def marcar_email_verificado(self, request, queryset):
        """Marca emails como verificados manualmente"""
        count = queryset.update(email_verificado=True)
        self.message_user(request, f'✓ {count} email(s) verificado(s)', level='SUCCESS')


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
    """
    Administración avanzada de Tarifas de Comisión
    """
    list_display = [
        'id_tarifa',
        'medio_pago_display', 
        'porcentaje_display',
        'monto_fijo_display',
        'fecha_inicio_vigencia',
        'fecha_fin_vigencia',
        'estado_vigencia',
        'activo'
    ]
    list_filter = [
        'activo',
        'id_medio_pago',
        'fecha_inicio_vigencia',
        ('fecha_fin_vigencia', admin.EmptyFieldListFilter),
    ]
    search_fields = ['id_medio_pago__descripcion']
    ordering = ['-fecha_inicio_vigencia', 'id_medio_pago']
    # date_hierarchy removed due to MySQL timezone tables requirement
    
    fieldsets = (
        ('Información General', {
            'fields': ('id_medio_pago', 'activo')
        }),
        ('Comisión', {
            'fields': ('porcentaje_comision', 'monto_fijo_comision'),
            'description': 'Configure el porcentaje y/o monto fijo de comisión. '
                          'Ejemplo: 1.8% se ingresa como 0.0180'
        }),
        ('Vigencia', {
            'fields': ('fecha_inicio_vigencia', 'fecha_fin_vigencia'),
            'description': 'Defina el período de vigencia de esta tarifa. '
                          'Deje "Fecha fin" vacío para vigencia indefinida.'
        }),
    )
    
    readonly_fields = ['id_tarifa']
    
    # Acciones personalizadas
    actions = ['activar_tarifas', 'desactivar_tarifas', 'finalizar_vigencia']
    
    def medio_pago_display(self, obj):
        """Muestra el medio de pago con color"""
        color = '#28a745' if obj.id_medio_pago.genera_comision else '#6c757d'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.id_medio_pago.descripcion
        )
    medio_pago_display.short_description = 'Medio de Pago'
    medio_pago_display.admin_order_field = 'id_medio_pago__descripcion'
    
    def porcentaje_display(self, obj):
        """Muestra el porcentaje formateado"""
        porcentaje = float(obj.porcentaje_comision) * 100
        porcentaje_formateado = '{:.2f}%'.format(porcentaje)
        return format_html(
            '<span style="font-weight: bold; color: #007bff;">{}</span>',
            porcentaje_formateado
        )
    porcentaje_display.short_description = 'Porcentaje'
    porcentaje_display.admin_order_field = 'porcentaje_comision'
    
    def monto_fijo_display(self, obj):
        """Muestra el monto fijo formateado"""
        if obj.monto_fijo_comision:
            monto_formateado = '{:,.0f}'.format(float(obj.monto_fijo_comision))
            return format_html(
                '<span style="color: #dc3545;">Gs {}</span>',
                monto_formateado
            )
        return format_html('<span style="color: #999;">-</span>')
    monto_fijo_display.short_description = 'Monto Fijo'
    monto_fijo_display.admin_order_field = 'monto_fijo_comision'
    
    def estado_vigencia(self, obj):
        """Muestra el estado de vigencia"""
        from django.utils import timezone
        now = timezone.now()
        
        if not obj.activo:
            return format_html(
                '<span style="background-color: #6c757d; color: white; '
                'padding: 3px 8px; border-radius: 3px; font-size: 11px;">INACTIVA</span>'
            )
        
        if obj.fecha_inicio_vigencia > now:
            return format_html(
                '<span style="background-color: #ffc107; color: black; '
                'padding: 3px 8px; border-radius: 3px; font-size: 11px;">FUTURA</span>'
            )
        
        if obj.fecha_fin_vigencia and obj.fecha_fin_vigencia < now:
            return format_html(
                '<span style="background-color: #dc3545; color: white; '
                'padding: 3px 8px; border-radius: 3px; font-size: 11px;">VENCIDA</span>'
            )
        
        return format_html(
            '<span style="background-color: #28a745; color: white; '
            'padding: 3px 8px; border-radius: 3px; font-size: 11px;">VIGENTE</span>'
        )
    estado_vigencia.short_description = 'Estado'
    
    # Acciones
    @admin.action(description='✅ Activar tarifas seleccionadas')
    def activar_tarifas(self, request, queryset):
        count = queryset.update(activo=True)
        self.message_user(request, f'{count} tarifa(s) activada(s) exitosamente.', level='success')
    
    @admin.action(description='❌ Desactivar tarifas seleccionadas')
    def desactivar_tarifas(self, request, queryset):
        count = queryset.update(activo=False)
        self.message_user(request, f'{count} tarifa(s) desactivada(s) exitosamente.', level='success')
    
    @admin.action(description='⏹️ Finalizar vigencia (establecer fecha fin hoy)')
    def finalizar_vigencia(self, request, queryset):
        from django.utils import timezone
        count = queryset.update(fecha_fin_vigencia=timezone.now(), activo=False)
        self.message_user(
            request,
            f'{count} tarifa(s) finalizadas exitosamente. Fecha fin establecida al día de hoy.',
            level='success'
        )
    
    def get_queryset(self, request):
        """Optimiza las consultas"""
        qs = super().get_queryset(request)
        return qs.select_related('id_medio_pago')
    
    def save_model(self, request, obj, form, change):
        """Validaciones adicionales al guardar"""
        from django.utils import timezone
        from django.contrib import messages
        
        # Validar que el porcentaje esté en rango válido (0% a 100%)
        if obj.porcentaje_comision < 0 or obj.porcentaje_comision > 1:
            messages.error(
                request,
                f'Error: El porcentaje debe estar entre 0 y 1 (0% a 100%). '
                f'Valor ingresado: {obj.porcentaje_comision}'
            )
            return
        
        # Validar que fecha inicio sea menor que fecha fin
        if obj.fecha_fin_vigencia and obj.fecha_inicio_vigencia >= obj.fecha_fin_vigencia:
            messages.error(
                request,
                'Error: La fecha de inicio debe ser anterior a la fecha de fin.'
            )
            return
        
        # Advertir sobre superposición de tarifas
        tarifas_activas = TarifasComision.objects.filter(
            id_medio_pago=obj.id_medio_pago,
            activo=True
        ).exclude(id_tarifa=obj.id_tarifa)
        
        if tarifas_activas.exists():
            messages.warning(
                request,
                f'Atención: Ya existe(n) {tarifas_activas.count()} tarifa(s) activa(s) '
                f'para {obj.id_medio_pago.descripcion}. '
                f'Verifique que no haya superposición de fechas.'
            )
        
        super().save_model(request, obj, form, change)
        
        if change:
            messages.success(request, f'Tarifa actualizada exitosamente.')
        else:
            messages.success(request, f'Tarifa creada exitosamente.')


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
    list_display = ['id_venta', 'id_producto', 'cantidad', 'precio_unitario', 'subtotal_total']
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


# Notas de Crédito
@admin.register(NotasCreditoCliente)
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
        if saldo is None:
            return format_html('<span style="color: #999;">Sin datos</span>')
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
    list_display = ['codigo_barra', 'descripcion', 'categoria', 'stock_actual', 'stock_minimo', 'diferencia_badge']
    list_filter = ['categoria']
    search_fields = ['codigo_barra', 'descripcion']
    
    def diferencia_badge(self, obj):
        diferencia = obj.stock_minimo - obj.stock_actual
        if diferencia > 50:
            color = '#f44336'  # Rojo - crítico
            nivel = 'CRÍTICO'
        elif diferencia > 20:
            color = '#ff5722'  # Naranja oscuro - urgente
            nivel = 'URGENTE'
        elif diferencia > 0:
            color = '#ff9800'  # Naranja - bajo
            nivel = 'BAJO'
        else:
            color = '#4caf50'  # Verde - OK
            nivel = 'OK'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 12px; border-radius: 12px; font-weight: bold;">{}</span>',
            color, nivel
        )
    diferencia_badge.short_description = 'Estado'
    
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
    list_display = ['id_nota', 'cliente', 'monto_badge', 'estado_badge', 'venta_original', 'fecha']
    list_filter = ['estado']
    search_fields = ['cliente', 'productos']
    
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
    list_display = ['descripcion', 'codigo_barra', 'categoria', 'stock_actual', 'stock_minimo', 'diferencia', 'nivel_alerta_badge']
    list_filter = ['nivel_alerta', 'categoria']
    search_fields = ['descripcion', 'codigo_barra']
    ordering = ['-nivel_alerta', '-diferencia']
    
    def nivel_alerta_badge(self, obj):
        colors = {
            'CRÍTICO': '#f44336',
            'URGENTE': '#ff5722',
            'BAJO': '#ff9800',
            'ATENCIÓN': '#ffc107'
        }
        color = colors.get(obj.nivel_alerta, '#999')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 12px; border-radius: 12px; font-weight: bold;">{}</span>',
            color, obj.nivel_alerta
        )
    nivel_alerta_badge.short_description = 'Nivel de Alerta'
    nivel_alerta_badge.admin_order_field = 'nivel_alerta'
    
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
cantina_admin_site.register(CargasSaldo, CargasSaldoAdmin)
cantina_admin_site.register(Empleado, EmpleadoAdmin)
cantina_admin_site.register(DatosEmpresa, DatosEmpresaAdmin)
cantina_admin_site.register(UnidadMedida, UnidadMedidaAdmin)
cantina_admin_site.register(Impuesto, ImpuestoAdmin)
cantina_admin_site.register(ListaPrecios, ListaPreciosAdmin)
cantina_admin_site.register(PreciosPorLista, PreciosPorListaAdmin)
cantina_admin_site.register(HistoricoPrecios, HistoricoPreciosAdmin)
cantina_admin_site.register(CostosHistoricos, CostosHistoricosAdmin)
# cantina_admin_site.register(UsuariosWebClientes, UsuariosWebClientesAdmin)  # LEGACY - DESHABILITADO
cantina_admin_site.register(UsuarioPortal, UsuarioPortalAdmin)
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
cantina_admin_site.register(NotasCreditoCliente, NotasCreditoAdmin)
cantina_admin_site.register(DetalleNota, DetalleNotaAdmin)
cantina_admin_site.register(PlanesAlmuerzo, PlanesAlmuerzoAdmin)
cantina_admin_site.register(SuscripcionesAlmuerzo, SuscripcionesAlmuerzoAdmin)
cantina_admin_site.register(RegistroConsumoAlmuerzo, RegistroConsumoAlmuerzoAdmin)
cantina_admin_site.register(PagosAlmuerzoMensual, PagosAlmuerzoMensualAdmin)
cantina_admin_site.register(AlertasSistema, AlertasSistemaAdmin)
cantina_admin_site.register(SolicitudesNotificacion, SolicitudesNotificacionAdmin)

# ============================================================================
# ADMIN PARA GESTIÓN ACADÉMICA
# ============================================================================

@admin.register(Grado, site=cantina_admin_site)
class GradoAdmin(admin.ModelAdmin):
    list_display = ['nombre_grado', 'nivel', 'orden_visualizacion', 'es_ultimo_grado']
    list_filter = ['nivel', 'es_ultimo_grado']
    search_fields = ['nombre_grado']
    ordering = ['orden_visualizacion']
    
    fieldsets = (
        ('Información del Grado', {
            'fields': ('nombre_grado', 'nivel', 'orden_visualizacion')
        }),
        ('Configuración', {
            'fields': ('es_ultimo_grado',),
            'description': 'Marcar si es el último grado del sistema'
        }),
    )

@admin.register(HistorialGradoHijo, site=cantina_admin_site)
class HistorialGradoHijoAdmin(admin.ModelAdmin):
    list_display = ['id_hijo', 'grado_anterior', 'grado_nuevo', 'anio_escolar', 'motivo', 'fecha_cambio', 'usuario_registro']
    list_filter = ['anio_escolar', 'motivo', 'fecha_cambio']
    search_fields = ['id_hijo__nombre_completo', 'grado_anterior', 'grado_nuevo']
    date_hierarchy = 'fecha_cambio'
    ordering = ['-fecha_cambio']
    readonly_fields = ['fecha_cambio']
    
    fieldsets = (
        ('Estudiante', {
            'fields': ('id_hijo',)
        }),
        ('Cambio de Grado', {
            'fields': ('grado_anterior', 'grado_nuevo', 'anio_escolar', 'motivo')
        }),
        ('Auditoría', {
            'fields': ('fecha_cambio', 'usuario_registro', 'observaciones'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Los registros se crean automáticamente desde el sistema
        return False
    
    def has_delete_permission(self, request, obj=None):
        # No permitir eliminar el historial
        return False


# =============================================================================
# ADMINISTRACIÓN DE ALÉRGENOS Y RESTRICCIONES ALIMENTARIAS
# =============================================================================

@admin.register(Alergeno, site=cantina_admin_site)
class AlergenoAdmin(admin.ModelAdmin):
    list_display = ['icono_nombre', 'nivel_severidad', 'cantidad_palabras_clave', 'activo', 'fecha_creacion']
    list_filter = ['nivel_severidad', 'activo', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion']
    readonly_fields = ['fecha_creacion']
    ordering = ['nivel_severidad', 'nombre']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'icono', 'descripcion')
        }),
        ('Clasificación', {
            'fields': ('nivel_severidad', 'activo')
        }),
        ('Palabras Clave para Detección', {
            'fields': ('palabras_clave',),
            'description': 'Formato JSON: ["palabra1", "palabra2", "palabra3"]. Ejemplos: ["maní", "peanut", "cacahuete"]'
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion', 'usuario_creacion'),
            'classes': ('collapse',)
        }),
    )
    
    def icono_nombre(self, obj):
        return f'{obj.icono} {obj.nombre}' if obj.icono else obj.nombre
    icono_nombre.short_description = 'Alérgeno'
    
    def cantidad_palabras_clave(self, obj):
        import json
        try:
            palabras = json.loads(obj.palabras_clave) if isinstance(obj.palabras_clave, str) else obj.palabras_clave
            return len(palabras)
        except:
            return 0
    cantidad_palabras_clave.short_description = 'N° Palabras'


@admin.register(ProductoAlergeno, site=cantina_admin_site)
class ProductoAlergenoAdmin(admin.ModelAdmin):
    list_display = ['id_producto', 'id_alergeno', 'tipo_presencia', 'fecha_registro', 'usuario_registro']
    list_filter = ['contiene', 'id_alergeno', 'fecha_registro']
    search_fields = ['id_producto__descripcion', 'id_alergeno__nombre']
    readonly_fields = ['fecha_registro']
    autocomplete_fields = ['id_producto', 'id_alergeno']
    
    fieldsets = (
        ('Relación', {
            'fields': ('id_producto', 'id_alergeno', 'contiene')
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        }),
        ('Auditoría', {
            'fields': ('fecha_registro', 'usuario_registro'),
            'classes': ('collapse',)
        }),
    )
    
    def tipo_presencia(self, obj):
        if obj.contiene:
            return format_html('<span style="color: red; font-weight: bold;">⚠️ Contiene</span>')
        else:
            return format_html('<span style="color: orange;">⚠️ Puede contener trazas</span>')
    tipo_presencia.short_description = 'Tipo'


# =============================================================================
# ADMINISTRACIÓN DE PROMOCIONES Y DESCUENTOS
# =============================================================================

@admin.register(Promocion, site=cantina_admin_site)
class PromocionAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo_promocion', 'valor_mostrado', 'vigencia_estado', 'usos_mostrado', 'activo', 'prioridad']
    list_filter = ['tipo_promocion', 'activo', 'aplica_a', 'fecha_inicio']
    search_fields = ['nombre', 'descripcion', 'codigo_promocion']
    date_hierarchy = 'fecha_inicio'
    ordering = ['prioridad', '-fecha_inicio']
    readonly_fields = ['fecha_creacion', 'usos_actuales']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'descripcion', 'activo', 'prioridad')
        }),
        ('Configuración de Descuento', {
            'fields': ('tipo_promocion', 'valor_descuento', 'aplica_a')
        }),
        ('Vigencia', {
            'fields': ('fecha_inicio', 'fecha_fin', 'hora_inicio', 'hora_fin', 'dias_semana'),
            'description': 'Días de semana en formato JSON: [1,2,3,4,5] (1=Lun, 7=Dom)'
        }),
        ('Condiciones', {
            'fields': ('min_cantidad', 'monto_minimo', 'requiere_codigo', 'codigo_promocion')
        }),
        ('Límites de Uso', {
            'fields': ('max_usos_cliente', 'max_usos_total', 'usos_actuales')
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion', 'usuario_creacion'),
            'classes': ('collapse',)
        }),
    )
    
    def valor_mostrado(self, obj):
        if obj.tipo_promocion == 'DESCUENTO_PORCENTAJE':
            return f'{obj.valor_descuento}%'
        elif obj.tipo_promocion in ['DESCUENTO_MONTO', 'PRECIO_FIJO']:
            return f'Gs. {obj.valor_descuento:,.0f}'
        elif obj.tipo_promocion == 'NXM':
            return f'{int(100/obj.valor_descuento)}x{int(100/obj.valor_descuento)-1}'
        return str(obj.valor_descuento)
    valor_mostrado.short_description = 'Valor'
    
    def vigencia_estado(self, obj):
        from django.utils import timezone
        ahora = timezone.now().date()
        
        if obj.fecha_inicio > ahora:
            return format_html('<span style="color: gray;">⏳ Próximamente</span>')
        elif obj.fecha_fin and obj.fecha_fin < ahora:
            return format_html('<span style="color: red;">❌ Expirada</span>')
        else:
            return format_html('<span style="color: green;">✅ Vigente</span>')
    vigencia_estado.short_description = 'Estado'
    
    def usos_mostrado(self, obj):
        if obj.max_usos_total:
            porcentaje = (obj.usos_actuales / obj.max_usos_total) * 100
            color = 'red' if porcentaje >= 90 else 'orange' if porcentaje >= 70 else 'green'
            return format_html(
                '<span style="color: {};">{} / {}</span>',
                color, obj.usos_actuales, obj.max_usos_total
            )
        return f'{obj.usos_actuales} (sin límite)'
    usos_mostrado.short_description = 'Usos'
    
    def nivel_severidad_ficticio(self, obj):
        # Campo ficticio para agrupar en filtros
        return obj.activo
    nivel_severidad_ficticio.short_description = 'Estado'


class ProductoPromocionInline(admin.TabularInline):
    model = ProductoPromocion
    extra = 1
    autocomplete_fields = ['id_producto']


class CategoriaPromocionInline(admin.TabularInline):
    model = CategoriaPromocion
    extra = 1
    autocomplete_fields = ['id_categoria']


@admin.register(PromocionAplicada, site=cantina_admin_site)
class PromocionAplicadaAdmin(admin.ModelAdmin):
    list_display = ['id_venta', 'id_promocion', 'monto_descontado_mostrado', 'fecha_aplicacion']
    list_filter = ['id_promocion', 'fecha_aplicacion']
    search_fields = ['id_venta__id_venta']
    readonly_fields = ['fecha_aplicacion']
    date_hierarchy = 'fecha_aplicacion'
    
    fieldsets = (
        ('Aplicación', {
            'fields': ('id_venta', 'id_promocion', 'monto_descontado', 'fecha_aplicacion')
        }),
    )
    
    def monto_descontado_mostrado(self, obj):
        return format_html('<span style="color: green; font-weight: bold;">-Gs. {:,.0f}</span>', obj.monto_descontado)
    monto_descontado_mostrado.short_description = 'Descuento'
    
    def has_add_permission(self, request):
        # Se crean automáticamente desde el POS
        return False
    
    def has_change_permission(self, request, obj=None):
        # No permitir editar
        return False


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
