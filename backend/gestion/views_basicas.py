"""
Views básicas para módulo de gestión - Implementación Fase 1
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q
from .models import *
import json

# ============ DASHBOARD Y INDEX ============
@login_required
def index(request):
    """Vista principal de gestión"""
    context = {
        'title': 'Inicio - Gestión',
        'total_productos': Producto.objects.filter(activo=True).count(),
        'total_clientes': Cliente.objects.filter(activo=True).count(),
        'total_empleados': Empleado.objects.filter(activo=True).count()
    }
    return render(request, 'gestion/dashboard.html', context)

@login_required
def dashboard(request):
    """Dashboard principal de gestión"""
    context = {
        'title': 'Dashboard - Gestión',
        'productos_count': Producto.objects.count(),
        'clientes_count': Cliente.objects.count(),
        'ventas_count': Ventas.objects.count(),
        'empleados_count': Empleado.objects.count()
    }
    return render(request, 'apps/gestion/dashboard/dashboard.html', context)

# ============ PRODUCTOS ============
@login_required
def productos_lista(request):
    """Lista de productos con búsqueda y paginación"""
    query = request.GET.get('q', '')
    productos = Producto.objects.filter(activo=True)
    
    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) | 
            Q(codigo_barras__icontains=query) |
            Q(descripcion__icontains=query)
        )
    
    paginator = Paginator(productos, 20)
    page = request.GET.get('page')
    productos = paginator.get_page(page)
    
    context = {
        'title': 'Productos',
        'productos': productos,
        'query': query
    }
    return render(request, 'apps/gestion/productos/lista.html', context)

@login_required  
def crear_producto(request):
    """Crear nuevo producto"""
    if request.method == 'POST':
        try:
            producto = Producto.objects.create(
                nombre=request.POST.get('nombre'),
                descripcion=request.POST.get('descripcion', ''),
                precio=float(request.POST.get('precio', 0)),
                costo=float(request.POST.get('costo', 0)),
                codigo_barras=request.POST.get('codigo_barras', ''),
                categoria_id=request.POST.get('categoria'),
                stock=int(request.POST.get('stock', 0)),
                stock_minimo=int(request.POST.get('stock_minimo', 0))
            )
            messages.success(request, f'Producto "{producto.nombre}" creado exitosamente')
            return redirect('gestion:productos_lista')
        except Exception as e:
            messages.error(request, f'Error al crear producto: {str(e)}')
    
    context = {
        'title': 'Crear Producto',
        'categorias': Categoria.objects.filter(activo=True)
    }
    return render(request, 'apps/gestion/productos/crear.html', context)

@login_required
def editar_producto(request, producto_id):
    """Editar producto existente"""
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == 'POST':
        try:
            producto.nombre = request.POST.get('nombre')
            producto.descripcion = request.POST.get('descripcion', '')
            producto.precio = float(request.POST.get('precio', 0))
            producto.costo = float(request.POST.get('costo', 0))
            producto.codigo_barras = request.POST.get('codigo_barras', '')
            producto.categoria_id = request.POST.get('categoria')
            producto.stock = int(request.POST.get('stock', 0))
            producto.stock_minimo = int(request.POST.get('stock_minimo', 0))
            producto.save()
            
            messages.success(request, f'Producto "{producto.nombre}" actualizado exitosamente')
            return redirect('gestion:productos_lista')
        except Exception as e:
            messages.error(request, f'Error al actualizar producto: {str(e)}')
    
    context = {
        'title': 'Editar Producto',
        'producto': producto,
        'categorias': Categoria.objects.filter(activo=True)
    }
    return render(request, 'apps/gestion/productos/editar.html', context)

# ============ CATEGORIAS ============
@login_required
def categorias_lista(request):
    """Lista de categorías"""
    categorias = Categoria.objects.filter(activo=True)
    
    context = {
        'title': 'Categorías',
        'categorias': categorias
    }
    return render(request, 'apps/gestion/categorias/lista.html', context)

@login_required
def crear_categoria(request):
    """Crear nueva categoría"""
    if request.method == 'POST':
        try:
            categoria = Categoria.objects.create(
                nombre=request.POST.get('nombre'),
                descripcion=request.POST.get('descripcion', '')
            )
            messages.success(request, f'Categoría "{categoria.nombre}" creada exitosamente')
            return redirect('gestion:categorias_lista')
        except Exception as e:
            messages.error(request, f'Error al crear categoría: {str(e)}')
    
    context = {'title': 'Crear Categoría'}
    return render(request, 'apps/gestion/categorias/crear.html', context)

@login_required
def editar_categoria(request, categoria_id):
    """Editar categoría existente"""
    categoria = get_object_or_404(Categoria, id=categoria_id)
    
    if request.method == 'POST':
        try:
            categoria.nombre = request.POST.get('nombre')
            categoria.descripcion = request.POST.get('descripcion', '')
            categoria.save()
            
            messages.success(request, f'Categoría "{categoria.nombre}" actualizada exitosamente')
            return redirect('gestion:categorias_lista')
        except Exception as e:
            messages.error(request, f'Error al actualizar categoría: {str(e)}')
    
    context = {
        'title': 'Editar Categoría',
        'categoria': categoria
    }
    return render(request, 'apps/gestion/categorias/editar.html', context)

@login_required
def eliminar_categoria(request, pk):
    """Eliminar categoría"""
    categoria = get_object_or_404(Categoria, id=pk)
    
    if request.method == 'POST':
        try:
            nombre = categoria.nombre
            categoria.delete()
            messages.success(request, f'Categoría "{nombre}" eliminada exitosamente')
            return redirect('gestion:categorias_lista')
        except Exception as e:
            messages.error(request, f'Error al eliminar categoría: {str(e)}')
            return redirect('gestion:categorias_lista')
    
    context = {
        'title': 'Eliminar Categoría',
        'categoria': categoria
    }
    return render(request, 'apps/gestion/categorias/eliminar.html', context)

# ============ CLIENTES ============
@login_required
def clientes_lista(request):
    """Lista de clientes"""
    query = request.GET.get('q', '')
    clientes = Cliente.objects.filter(activo=True)
    
    if query:
        clientes = clientes.filter(
            Q(nombres__icontains=query) |
            Q(apellidos__icontains=query) |
            Q(cedula__icontains=query) |
            Q(telefono__icontains=query)
        )
    
    paginator = Paginator(clientes, 20)
    page = request.GET.get('page')
    clientes = paginator.get_page(page)
    
    context = {
        'title': 'Clientes',
        'clientes': clientes,
        'query': query
    }
    return render(request, 'apps/gestion/clientes/lista.html', context)

# ============ VENTAS ============
@login_required
def ventas_lista(request):
    """Lista de ventas"""
    ventas = Ventas.objects.all().order_by('-fecha_venta')
    
    paginator = Paginator(ventas, 20)
    page = request.GET.get('page')
    ventas = paginator.get_page(page)
    
    context = {
        'title': 'Ventas',
        'ventas': ventas
    }
    return render(request, 'apps/gestion/ventas/lista.html', context)

# ============ EMPLEADOS ============
@login_required
def gestionar_empleados(request):
    """Gestión de empleados"""
    empleados = Empleado.objects.filter(activo=True)
    
    context = {
        'title': 'Gestión de Empleados',
        'empleados': empleados
    }
    return render(request, 'apps/gestion/empleados/gestionar.html', context)

@login_required
def crear_empleado(request):
    """Crear nuevo empleado"""
    if request.method == 'POST':
        try:
            # Crear usuario Django
            from django.contrib.auth.models import User
            user = User.objects.create_user(
                username=request.POST.get('username'),
                email=request.POST.get('email'),
                first_name=request.POST.get('nombres'),
                last_name=request.POST.get('apellidos'),
                password=request.POST.get('password')
            )
            
            # Crear empleado
            empleado = Empleado.objects.create(
                user=user,
                cedula=request.POST.get('cedula'),
                telefono=request.POST.get('telefono'),
                cargo=request.POST.get('cargo')
            )
            
            messages.success(request, f'Empleado "{empleado.user.get_full_name()}" creado exitosamente')
            return redirect('gestion:gestionar_empleados')
        except Exception as e:
            messages.error(request, f'Error al crear empleado: {str(e)}')
    
    context = {'title': 'Crear Empleado'}
    return render(request, 'apps/gestion/empleados/crear.html', context)

# ============ PORTAL BÁSICO ============
def portal_login(request):
    """Login del portal de clientes"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('gestion:portal_dashboard')
        else:
            messages.error(request, 'Credenciales inválidas')
    
    return render(request, 'apps/portal/auth/login.html', {'title': 'Portal - Login'})

@login_required
def portal_logout(request):
    """Logout del portal"""
    logout(request)
    messages.success(request, 'Sesión cerrada correctamente')
    return redirect('gestion:portal_login')

@login_required
def portal_dashboard(request):
    """Dashboard del portal de clientes"""
    context = {
        'title': 'Portal - Dashboard',
        'user': request.user
    }
    return render(request, 'apps/portal/dashboard/dashboard.html', context)

@login_required
def portal_verificar_2fa(request):
    """Verificar código 2FA"""
    context = {
        'title': 'Portal - Verificar 2FA',
    }
    return render(request, 'apps/portal/auth/verificar-2fa.html', context)

@login_required
def portal_activar_2fa(request):
    """Activar autenticación 2FA"""
    context = {
        'title': 'Portal - Activar 2FA',
    }
    return render(request, 'apps/portal/auth/activar-2fa.html', context)

@login_required
def portal_deshabilitar_2fa(request):
    """Deshabilitar autenticación 2FA"""
    context = {
        'title': 'Portal - Deshabilitar 2FA',
    }
    return render(request, 'apps/portal/auth/deshabilitar-2fa.html', context)

@login_required
def portal_restablecer_password(request):
    """Restablecer contraseña"""
    context = {
        'title': 'Portal - Restablecer Password',
    }
    return render(request, 'apps/portal/auth/restablecer-password.html', context)

@login_required
def portal_revocar_terminos(request):
    """Revocar términos y condiciones"""
    context = {
        'title': 'Portal - Revocar Términos',
    }
    return render(request, 'apps/portal/auth/revocar-terminos.html', context)

@login_required
def portal_mis_hijos(request):
    """Ver información de mis hijos"""
    context = {
        'title': 'Portal - Mis Hijos',
    }
    return render(request, 'apps/portal/hijos/mis-hijos.html', context)

@login_required
def portal_consumos_hijo(request, hijo_id):
    """Ver consumos de un hijo específico"""
    context = {
        'title': 'Portal - Consumos del Hijo',
        'hijo_id': hijo_id
    }
    return render(request, 'apps/portal/hijos/consumos-hijo.html', context)

@login_required
def portal_restricciones_hijo(request, hijo_id):
    """Ver restricciones de un hijo específico"""
    context = {
        'title': 'Portal - Restricciones del Hijo',
        'hijo_id': hijo_id
    }
    return render(request, 'apps/portal/hijos/restricciones-hijo.html', context)

@login_required
def portal_cargar_saldo(request):
    """Cargar saldo a tarjetas"""
    context = {
        'title': 'Portal - Cargar Saldo',
    }
    return render(request, 'apps/portal/pagos/cargar-saldo.html', context)

@login_required
def portal_pagos(request):
    """Ver histórico de pagos"""
    context = {
        'title': 'Portal - Pagos',
    }
    return render(request, 'apps/portal/pagos/pagos.html', context)

@login_required
def portal_recargas(request):
    """Ver histórico de recargas"""
    context = {
        'title': 'Portal - Recargas',
    }
    return render(request, 'apps/portal/pagos/recargas.html', context)

@login_required
def portal_recargar_tarjeta(request):
    """Recargar tarjeta específica"""
    context = {
        'title': 'Portal - Recargar Tarjeta',
    }
    return render(request, 'apps/portal/pagos/recargar-tarjeta.html', context)

@login_required
def portal_notificaciones_saldo(request):
    """Configurar notificaciones de saldo"""
    context = {
        'title': 'Portal - Notificaciones de Saldo',
    }
    return render(request, 'apps/portal/notificaciones/notificaciones-saldo.html', context)

@require_http_methods(["GET"])
def api_portal_movimientos(request, tarjeta_id):
    """API para obtener movimientos de una tarjeta"""
    return JsonResponse({
        'tarjeta_id': tarjeta_id,
        'movimientos': []
    })

@require_http_methods(["GET"])
def api_portal_saldo(request, tarjeta_id):
    """API para obtener saldo de una tarjeta"""
    return JsonResponse({
        'tarjeta_id': tarjeta_id,
        'saldo': 0
    })

@login_required
def portal_perfil(request):
    """Ver/editar perfil del portal"""
    context = {
        'title': 'Portal - Mi Perfil',
    }
    return render(request, 'apps/portal/perfil/perfil.html', context)

@login_required
def portal_cambiar_password(request):
    """Cambiar contraseña del portal"""
    context = {
        'title': 'Portal - Cambiar Contraseña',
    }
    return render(request, 'apps/portal/auth/cambiar-password.html', context)

@login_required
def portal_configurar_2fa(request):
    """Configurar autenticación 2FA"""
    context = {
        'title': 'Portal - Configurar 2FA',
    }
    return render(request, 'apps/portal/auth/configurar-2fa.html', context)

# ============ VIEWS PLACEHOLDER ============
# Views que solo renderizan templates básicos

@login_required
def reportes(request):
    """Vista de reportes básica"""
    context = {'title': 'Reportes'}
    return render(request, 'apps/gestion/reportes/index.html', context)

@login_required
def importar_productos(request):
    """Vista de importación de productos"""
    context = {'title': 'Importar Productos'}
    return render(request, 'apps/gestion/productos/importar.html', context)

@login_required
def exportar_productos_excel(request):
    """Exportar productos a Excel"""
    # Implementación básica
    context = {'title': 'Exportar a Excel'}
    return render(request, 'apps/gestion/productos/exportar.html', context)

@login_required
def exportar_productos_csv(request):
    """Exportar productos a CSV"""
    # Implementación básica
    context = {'title': 'Exportar a CSV'}
    return render(request, 'apps/gestion/productos/exportar.html', context)

@login_required
def importar_productos(request):
    """Importar productos desde archivo"""
    # Implementación básica
    context = {'title': 'Importar Productos'}
    return render(request, 'apps/gestion/productos/importar.html', context)


# ========================= DASHBOARD VIEWS =========================

@login_required
def dashboard_unificado(request):
    """Dashboard principal unificado"""
    from django.db.models import Count, Sum
    from django.utils import timezone
    
    context = {
        'total_productos': Producto.objects.count(),
        'total_clientes': Cliente.objects.count(),
        'total_empleados': User.objects.filter(is_staff=True).count(),
        'ventas_hoy': Ventas.objects.filter(
            fecha__date=timezone.now().date()
        ).count() if 'Ventas' in globals() else 0,
    }
    return render(request, 'apps/dashboard/dashboard_unificado.html', context)

@login_required
def dashboard_ventas_detalle(request):
    """Dashboard detallado de ventas"""
    context = {
        'ventas_recientes': [],  # Placeholder
        'total_ventas_mes': 0,
        'promedio_venta': 0,
    }
    return render(request, 'apps/dashboard/ventas_detalle.html', context)

@login_required
def dashboard_stock_detalle(request):
    """Dashboard detallado de stock"""
    context = {
        'productos_bajo_stock': Producto.objects.filter(stock__lt=10).count(),
        'productos_sin_stock': Producto.objects.filter(stock=0).count(),
        'valor_inventario': 0,  # Calcular
    }
    return render(request, 'apps/dashboard/stock_detalle.html', context)

@login_required
def invalidar_cache_dashboard(request):
    """Invalidar cache del dashboard"""
    from django.core.cache import cache
    cache.clear()
    messages.success(request, 'Cache del dashboard invalidado exitosamente')
    return redirect('dashboard_unificado')


# ============ FACTURACIÓN ELECTRÓNICA ============
@login_required
def facturacion_listado(request):
    """Listado de facturación electrónica"""
    context = {
        'title': 'Facturación Electrónica',
    }
    return render(request, 'apps/facturacion/listado.html', context)

@login_required
def facturacion_kude(request):
    """Generar KUDE de facturación"""
    context = {
        'title': 'Generar KUDE',
    }
    return render(request, 'apps/facturacion/kude.html', context)

@login_required
def facturacion_anular_api(request):
    """API para anular facturación"""
    if request.method == 'POST':
        return JsonResponse({
            'status': 'success',
            'message': 'Factura anulada correctamente'
        })
    return JsonResponse({
        'status': 'error',
        'message': 'Método no permitido'
    })

@login_required
def facturacion_reporte_cumplimiento(request):
    """Reporte de cumplimiento de facturación"""
    context = {
        'title': 'Reporte de Cumplimiento',
    }
    return render(request, 'apps/facturacion/reporte-cumplimiento.html', context)


# ============ REPORTES ============
@login_required
def reporte_mensual_completo(request):
    """Reporte mensual completo"""
    context = {
        'title': 'Reporte Mensual Completo',
    }
    return render(request, 'apps/reportes/mensual-completo.html', context)


# ============ VALIDACIONES ============
@login_required
def validar_pago_action(request):
    """Acción para validar pagos"""
    if request.method == 'POST':
        return JsonResponse({
            'status': 'success',
            'message': 'Pago validado correctamente'
        })
    context = {
        'title': 'Validar Pago',
    }
    return render(request, 'apps/validacion/validar-pago.html', context)


# ============ PORTAL DE PADRES - VISTAS STUB ============

def portal_registro(request):
    """Vista de registro para el portal de padres"""
    messages.info(request, 'El registro de padres está temporalmente deshabilitado. Contacte al administrador.')
    return redirect('clientes:portal_login')


def portal_login(request):
    """Redirige al login de clientes"""
    return redirect('clientes:portal_login')


def portal_logout(request):
    """Redirige al logout de clientes"""
    return redirect('clientes:portal_logout')


def portal_dashboard(request):
    """Redirige al dashboard de clientes"""
    return redirect('clientes:portal_dashboard')


def portal_verificar_2fa(request):
    """Vista stub para 2FA"""
    messages.info(request, '2FA no configurado aún')
    return redirect('clientes:portal_dashboard')


def portal_activar_2fa(request):
    """Vista stub para activar 2FA"""
    messages.info(request, '2FA no configurado aún')
    return redirect('clientes:portal_dashboard')


def portal_deshabilitar_2fa(request):
    """Vista stub para deshabilitar 2FA"""
    messages.info(request, '2FA no configurado aún')
    return redirect('clientes:portal_dashboard')


def portal_restablecer_password(request):
    """Vista stub para restablecer password"""
    messages.info(request, 'Función no disponible aún')
    return redirect('clientes:portal_login')


def portal_revocar_terminos(request):
    """Vista stub para revocar términos"""
    messages.info(request, 'Función no disponible aún')
    return redirect('clientes:portal_dashboard')


def portal_mis_hijos(request):
    """Redirige a la vista de clientes"""
    return redirect('clientes:portal_dashboard')


def portal_consumos_hijo(request, hijo_id):
    """Vista stub para consumos de hijo"""
    return redirect('clientes:portal_dashboard')


def portal_restricciones_hijo(request, hijo_id):
    """Vista stub para restricciones de hijo"""
    return redirect('clientes:portal_dashboard')


def portal_cargar_saldo(request):
    """Vista stub para cargar saldo"""
    return redirect('clientes:portal_cargar_saldo')


def portal_pagos(request):
    """Vista stub para pagos"""
    return redirect('clientes:portal_dashboard')


def portal_recargas(request):
    """Vista stub para recargas"""
    return redirect('clientes:portal_recargas')


def portal_recargar_tarjeta(request):
    """Vista stub para recargar tarjeta"""
    return redirect('clientes:portal_cargar_saldo')


def portal_notificaciones_saldo(request):
    """Vista stub para notificaciones de saldo"""
    return redirect('clientes:portal_dashboard')


def api_portal_movimientos(request, tarjeta_id):
    """API stub para movimientos"""
    return JsonResponse({'error': 'Not implemented'}, status=501)


def api_portal_saldo(request, tarjeta_id):
    """API stub para saldo"""
    return JsonResponse({'error': 'Not implemented'}, status=501)

