"""
Django Admin configuration for Gestion app
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import *
from .models_notificaciones import NotificacionSistema, ConfiguracionNotificacionesSistema

# Personalizar User Admin si es necesario
class CustomUserAdmin(UserAdmin):
    """Personalización del admin de usuarios"""
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')

# Re-registrar User con personalización
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Configuración para Producto
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('descripcion', 'codigo_barra', 'id_categoria', 'activo')
    list_filter = ('id_categoria', 'activo')
    search_fields = ('descripcion', 'codigo_barra')
    list_editable = ('activo',)
    ordering = ('descripcion',)
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('descripcion', 'codigo_barra', 'id_categoria')
        }),
        ('Stock', {
            'fields': ('stock_minimo', 'permite_stock_negativo')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
    )

# Configuración para Cliente
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'ruc_ci', 'telefono', 'email', 'activo')
    list_filter = ('activo', 'fecha_registro')
    search_fields = ('nombres', 'apellidos', 'ruc_ci', 'telefono', 'email')
    list_editable = ('activo',)
    ordering = ('apellidos', 'nombres')
    date_hierarchy = 'fecha_registro'
    
    def nombre_completo(self, obj):
        return f"{obj.nombres} {obj.apellidos}"
    nombre_completo.short_description = 'Nombre Completo'

# Configuración para Tarjeta
@admin.register(Tarjeta)
class TarjetaAdmin(admin.ModelAdmin):
    list_display = ('nro_tarjeta', 'id_hijo', 'saldo_display', 'estado', 'fecha_creacion')
    list_filter = ('estado', 'fecha_creacion')
    search_fields = ('nro_tarjeta', 'id_hijo__nombre', 'id_hijo__apellido')
    list_editable = ('estado',)
    ordering = ('-fecha_creacion',)
    
    def saldo_display(self, obj):
        return f"₲ {obj.saldo_actual:,.0f}"
    saldo_display.short_description = 'Saldo Actual'

# ========================================================================
# ⚠️  VENTAS ADMIN DEPRECADO - MIGRADO A pos APP  
# ========================================================================
# La configuración admin para Ventas/DetalleVenta/PagoVenta ahora está
# en pos/admin.py para mantener separación de responsabilidades
# ========================================================================

# ========================================================================
# ⚠️  MODELOS SIN TABLA EN MYSQL - DESREGISTRADOS TEMPORALMENTE
# ========================================================================
# CargasSaldo y CierresCaja están desregistrados porque sus tablas
# no existen en MySQL. Crear las tablas con migraciones para habilitarlos.
# ========================================================================

# # Configuración para CargasSaldo (DESHABILITADO - tabla no existe)
# @admin.register(CargasSaldo)
# class CargasSaldoAdmin(admin.ModelAdmin):
#     list_display = ('nro_tarjeta', 'monto_display', 'fecha_carga', 'estado')
#     list_filter = ('estado', 'fecha_carga')
#     search_fields = ('nro_tarjeta__nro_tarjeta', 'nro_tarjeta__id_hijo__nombre')
#     ordering = ('-fecha_carga',)
#     
#     def monto_display(self, obj):
#         return f"₲ {obj.monto_cargado:,.0f}"
#     monto_display.short_description = 'Monto'

# # Configuración para CierresCaja (DESHABILITADO - tabla no existe)
# @admin.register(CierresCaja)
# class CierresCajaAdmin(admin.ModelAdmin):
#     list_display = ('id_cierre', 'fecha_hora_cierre', 'id_empleado', 'id_caja', 'estado')
#     list_filter = ('fecha_hora_cierre', 'id_empleado', 'estado')
#     ordering = ('-fecha_hora_cierre',)
#     readonly_fields = ('fecha_hora_apertura', 'fecha_hora_cierre')

# Configuración para Categoria
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'id_categoria_padre', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre',)
    list_editable = ('activo',)

# Configuración para Empleado
@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'usuario', 'id_rol', 'telefono', 'activo')
    list_filter = ('id_rol', 'activo')
    search_fields = ('nombre', 'apellido', 'usuario', 'email')
    list_editable = ('activo',)

# Configuración para Timbrados
try:
    @admin.register(Timbrados)
    class TimbradosAdmin(admin.ModelAdmin):
        list_display = ('nro_timbrado', 'tipo_documento', 'fecha_inicio', 'fecha_fin', 'activo')
        list_filter = ('activo', 'tipo_documento', 'es_electronico')
        search_fields = ('nro_timbrado',)
        list_editable = ('activo',)
        ordering = ('-fecha_inicio',)
except:
    # Timbrados puede no existir en todos los casos
    pass

# Configuración para NotificacionSistema
@admin.register(NotificacionSistema)
class NotificacionSistemaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'usuario', 'tipo', 'prioridad', 'leida', 'creada_en')
    list_filter = ('tipo', 'prioridad', 'leida', 'creada_en')
    search_fields = ('titulo', 'mensaje', 'usuario__username', 'usuario__email')
    list_editable = ('leida',)
    ordering = ('-creada_en',)
    readonly_fields = ('creada_en', 'fecha_leida')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('usuario', 'titulo', 'mensaje', 'tipo', 'prioridad')
        }),
        ('Visualización', {
            'fields': ('icono', 'url')
        }),
        ('Estado', {
            'fields': ('leida', 'fecha_leida', 'creada_en', 'expira_en')
        }),
    )
    
    def has_add_permission(self, request):
        # Las notificaciones se crean automáticamente por signals
        return False

# Configuración para ConfiguracionNotificacionesSistema
@admin.register(ConfiguracionNotificacionesSistema)
class ConfiguracionNotificacionesSistemaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'notif_ventas', 'notif_recargas', 'notif_stock', 'notif_sistema', 'solo_criticas', 'sonido_habilitado')
    list_filter = ('notif_ventas', 'notif_recargas', 'notif_stock', 'notif_sistema', 'solo_criticas')
    search_fields = ('usuario__username', 'usuario__email')
    ordering = ('usuario__username',)
    
    fieldsets = (
        ('Usuario', {
            'fields': ('usuario',)
        }),
        ('Tipos de Notificaciones', {
            'fields': ('notif_ventas', 'notif_recargas', 'notif_stock', 'notif_sistema')
        }),
        ('Preferencias', {
            'fields': ('solo_criticas', 'sonido_habilitado', 'push_habilitado', 'push_subscription')
        }),
    )

# ========================================================================
# MODELOS DE HIJOS/ESTUDIANTES
# ========================================================================

@admin.register(Hijo)
class HijoAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'id_cliente_responsable', 'grado', 'fecha_nacimiento', 'tiene_foto', 'activo')
    list_filter = ('activo', 'grado', 'fecha_nacimiento')
    search_fields = ('nombre', 'apellido', 'id_cliente_responsable__nombres', 'id_cliente_responsable__apellidos')
    list_editable = ('activo',)
    ordering = ('apellido', 'nombre')
    date_hierarchy = 'fecha_nacimiento'
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre', 'apellido', 'fecha_nacimiento', 'grado')
        }),
        ('Responsable', {
            'fields': ('id_cliente_responsable',)
        }),
        ('Foto', {
            'fields': ('foto_perfil', 'fecha_foto'),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
    )

# ========================================================================
# MODELOS BÁSICOS QUE FUNCIONAN CORRECTAMENTE
# ========================================================================

# Solo modelos básicos verificados y funcionando
try:
    @admin.register(Hijo)
    class HijoAdmin(admin.ModelAdmin):
        list_display = ('nombre_completo', 'id_cliente_responsable', 'activo')
        list_filter = ('activo',)
        search_fields = ('nombre', 'apellido')
        list_editable = ('activo',)
except:
    pass

try:
    @admin.register(Proveedor)
    class ProveedorAdmin(admin.ModelAdmin):
        list_display = ('razon_social', 'ruc', 'activo')
        list_filter = ('activo',)
        search_fields = ('razon_social', 'ruc')
        list_editable = ('activo',)
except:
    pass

try:
    @admin.register(Compras)
    class ComprasAdmin(admin.ModelAdmin):
        list_display = ('id_compra', 'fecha', 'monto_total')
        list_filter = ('fecha',)
        ordering = ('-fecha',)
except:
    pass

try:
    @admin.register(TipoAlmuerzo)
    class TipoAlmuerzoAdmin(admin.ModelAdmin):
        list_display = ('nombre', 'precio_unitario', 'activo')
        list_filter = ('activo',)
        search_fields = ('nombre',)
        list_editable = ('activo',)
except:
    pass

try:
    @admin.register(TipoCliente)
    class TipoClienteAdmin(admin.ModelAdmin):
        list_display = ('nombre_tipo', 'activo')
        list_filter = ('activo',)
        search_fields = ('nombre_tipo',)
        list_editable = ('activo',)
except:
    pass

try:
    @admin.register(ListaPrecios)
    class ListaPreciosAdmin(admin.ModelAdmin):
        list_display = ('nombre_lista', 'activo')
        list_filter = ('activo',)
        search_fields = ('nombre_lista',)
        list_editable = ('activo',)
except:
    pass

# ========================================================================
# REGISTRO AUTOMÁTICO DE MODELOS ADICIONALES (SIN CONFIGURACIÓN ESPECÍFICA)
# ========================================================================

# Lista de modelos adicionales para registrar automáticamente
modelos_adicionales = [
    'CargasSaldo', 'ConsumoTarjeta', 'StockUnico', 'MovimientosStock', 
    'PreciosPorLista', 'HistoricoPrecios', 'SuscripcionesAlmuerzo',
    'PagosAlmuerzoMensual', 'RegistroConsumoAlmuerzo', 'DetalleCompra',
    'PagosProveedores', 'NotasCreditoProveedor', 'DocumentosTributarios',
    'Cajas', 'CierresCaja', 'AuditoriaOperacion', 'SesionActiva',
    'LogAutorizacion', 'UsuarioPortal', 'TransaccionOnline',
    'ProductoPromocion', 'PromocionAplicada', 'ProductoAlergeno',
    'Dashboard', 'KpiMetrica', 'ReporteTemplate', 'EmailTemplate',
    'EmailEnviado', 'SmsTemplate', 'SmsEnviado', 'ConfiguracionSistema',
    'PlanesAlmuerzo', 'Promocion', 'Alergeno', 'DatosEmpresa',
    'PuntosExpedicion', 'RestriccionesHijos', 'CostosHistoricos',
    'AjustesInventario', 'DetalleAjuste', 'Notificacion', 'AlertasSistema'
]

# Registrar automáticamente todos los modelos adicionales con configuración básica
for modelo_name in modelos_adicionales:
    try:
        # Obtener la clase del modelo desde globals()
        modelo_class = globals().get(modelo_name)
        if modelo_class and hasattr(modelo_class, '_meta'):
            # Crear clase admin básica y segura
            admin_class = type(f'{modelo_name}Admin', (admin.ModelAdmin,), {
                'list_per_page': 25,
                'show_full_result_count': False,
                'list_max_show_all': 50,
            })
            # Registrar en el admin
            admin.site.register(modelo_class, admin_class)
    except Exception:
        # Silenciosamente ignorar errores de modelos que no existen o no se pueden registrar
        continue

# Personalización del admin site
admin.site.site_header = "Administración Cantina TITA"
admin.site.site_title = "Cantina TITA Admin"
admin.site.index_title = "Panel de Administración"
