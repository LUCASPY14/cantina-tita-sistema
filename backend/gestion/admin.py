"""
Django Admin configuration for Gestion app
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import *

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
            'fields': ('descripcion', 'codigo_barra', 'id_categoria', 'id_unidad_de_medida', 'id_impuesto')
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

# Configuración para CargasSaldo
@admin.register(CargasSaldo)
class CargasSaldoAdmin(admin.ModelAdmin):
    list_display = ('nro_tarjeta', 'monto_display', 'fecha_carga', 'estado')
    list_filter = ('estado', 'fecha_carga')
    search_fields = ('nro_tarjeta__nro_tarjeta', 'nro_tarjeta__id_hijo__nombre')
    ordering = ('-fecha_carga',)
    date_hierarchy = 'fecha_carga'
    
    def monto_display(self, obj):
        return f"₲ {obj.monto_cargado:,.0f}"
    monto_display.short_description = 'Monto'

# Configuración para CierresCaja
@admin.register(CierresCaja)
class CierresCajaAdmin(admin.ModelAdmin):
    list_display = ('id_cierre', 'fecha_hora_cierre', 'id_empleado', 'id_caja', 'estado')
    list_filter = ('fecha_hora_cierre', 'id_empleado', 'estado')
    ordering = ('-fecha_hora_cierre',)
    date_hierarchy = 'fecha_hora_cierre'
    readonly_fields = ('fecha_hora_apertura', 'fecha_hora_cierre')

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

# Personalización del admin site
admin.site.site_header = "Administración Cantina TITA"
admin.site.site_title = "Cantina TITA Admin"
admin.site.index_title = "Panel de Administración"
