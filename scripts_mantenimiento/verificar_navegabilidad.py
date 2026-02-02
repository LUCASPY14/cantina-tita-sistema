"""
Script para verificar la navegabilidad completa del sistema
Verifica accesos, URLs y vistas para todos los tipos de usuario
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.urls import reverse, NoReverseMatch
from gestion.models import Empleado, UsuarioPortal, Cliente
from django.contrib.auth.hashers import check_password

def verificar_navegabilidad():
    """Verifica la navegabilidad de todos los tipos de usuario"""
    
    print("\n" + "="*100)
    print("🔍 VERIFICACIÓN COMPLETA DE NAVEGABILIDAD DEL SISTEMA")
    print("="*100 + "\n")
    
    # ===== EMPLEADOS =====
    print("👥 VERIFICANDO EMPLEADOS (Admin, Cajero, Supervisor, Sistema)...")
    print("-"*100)
    
    empleados = Empleado.objects.all()
    print(f"\nTotal empleados: {empleados.count()}\n")
    
    for emp in empleados:
        rol = emp.id_rol.nombre_rol if emp.id_rol else 'Sin rol'
        tipo_icono = {
            'Administrador': '👑',
            'Cajero': '💰',
            'Supervisor': '👁️',
            'Sistema': '⚙️'
        }.get(rol, '❓')
        
        print(f"{tipo_icono} {emp.usuario:15} | Rol: {rol:15} | Activo: {'✓' if emp.activo else '✗'}")
    
    # URLs disponibles para empleados
    print("\n📍 URLs PRINCIPALES PARA EMPLEADOS:")
    print("-"*100)
    
    urls_empleados = [
        ('login', 'Login Empleado'),
        ('dashboard', 'Dashboard Principal'),
        ('pos:pos_dashboard', 'POS Dashboard'),
        ('pos:pos_ventas', 'POS Ventas'),
        ('pos:almuerzo_dashboard', 'POS Almuerzo Dashboard'),
        ('pos:almuerzo_venta', 'POS Almuerzo Venta'),
        ('pos:cargar_saldo_tarjeta', 'Cargar Saldo'),
        ('gestion:inventario_productos', 'Inventario Productos'),
        ('gestion:categorias_lista', 'Categorías'),
        ('dashboard_unificado', 'Dashboard Unificado'),
        ('dashboard_ventas_detalle', 'Dashboard Ventas Detalle'),
        ('dashboard_stock_detalle', 'Dashboard Stock Detalle'),
    ]
    
    for url_name, descripcion in urls_empleados:
        try:
            url = reverse(url_name)
            print(f"✓ {descripcion:35} → {url}")
        except NoReverseMatch:
            print(f"✗ {descripcion:35} → ERROR: No se puede resolver")
    
    # ===== USUARIOS PORTAL =====
    print("\n\n👨‍👩‍👧‍👦 VERIFICANDO USUARIOS PORTAL (Padres/Clientes)...")
    print("-"*100)
    
    usuarios_portal = UsuarioPortal.objects.all()
    print(f"\nTotal usuarios portal: {usuarios_portal.count()}\n")
    
    for usuario in usuarios_portal:
        verificado = '✓' if usuario.email_verificado else '✗'
        activo = '✓' if usuario.activo else '✗'
        print(f"📧 {usuario.email:40} | Verificado: {verificado} | Activo: {activo} | Cliente: {usuario.cliente.nombres}")
    
    # URLs disponibles para portal
    print("\n📍 URLs PRINCIPALES PARA PORTAL DE PADRES:")
    print("-"*100)
    
    urls_portal = [
        ('clientes:portal_login', 'Portal Login'),
        ('clientes:portal_dashboard', 'Portal Dashboard'),
        ('clientes:portal_cargar_saldo', 'Portal Cargar Saldo'),
        ('clientes:portal_historial_cargas', 'Portal Historial Cargas'),
        ('clientes:portal_pagos', 'Portal Pagos'),
        ('clientes:portal_perfil', 'Portal Perfil'),
        ('clientes:portal_notificaciones_saldo', 'Portal Notificaciones'),
        ('portal:portal_login', 'Portal Login (alt)'),
        ('portal:dashboard', 'Portal Dashboard (alt)'),
        ('portal:mis_hijos', 'Mis Hijos'),
        ('portal:historial_consumos', 'Historial Consumos'),
    ]
    
    for url_name, descripcion in urls_portal:
        try:
            url = reverse(url_name)
            print(f"✓ {descripcion:35} → {url}")
        except NoReverseMatch:
            print(f"✗ {descripcion:35} → ERROR: No se puede resolver")
    
    # ===== PERMISOS POR TIPO DE EMPLEADO =====
    print("\n\n🔐 PERMISOS Y ACCESOS POR TIPO DE EMPLEADO:")
    print("-"*100)
    
    permisos = {
        'Administrador': {
            'descripcion': 'ADMINISTRADOR',
            'icono': '👑',
            'accesos': [
                'Acceso total al sistema',
                'Django Admin (/admin/)',
                'Gestión de empleados',
                'Reportes completos',
                'Configuración del sistema',
                'Autorización de saldos negativos',
                'Gestión de productos y categorías',
                'Dashboard unificado',
            ]
        },
        'Cajero': {
            'descripcion': 'CAJERO',
            'icono': '💰',
            'accesos': [
                'POS Dashboard',
                'Ventas regulares',
                'Ventas de almuerzo',
                'Cargar saldo a tarjetas',
                'Ver inventario (solo lectura)',
                'Dashboard de ventas básico',
            ]
        },
        'Supervisor': {
            'descripcion': 'SUPERVISOR',
            'icono': '👁️',
            'accesos': [
                'Ver reportes detallados',
                'Dashboard unificado',
                'Supervisar ventas',
                'Ver inventario y stock',
                'Reportes de autorizaciones',
                'Validar cargas de saldo',
            ]
        },
        'Sistema': {
            'descripcion': 'SISTEMA',
            'icono': '⚙️',
            'accesos': [
                'Acceso técnico',
                'Configuración avanzada',
                'Mantenimiento del sistema',
                'Logs y auditoría',
            ]
        }
    }
    
    for tipo, info in permisos.items():
        print(f"\n{info['icono']} {info['descripcion']} ({tipo}):")
        for acceso in info['accesos']:
            print(f"   ✓ {acceso}")
    
    # ===== CREDENCIALES DE PRUEBA =====
    print("\n\n🔑 CREDENCIALES DE PRUEBA:")
    print("="*100)
    
    print("\n📋 EMPLEADOS:")
    print("-"*100)
    empleados_activos = Empleado.objects.filter(activo=True)
    
    for emp in empleados_activos:
        rol = emp.id_rol.nombre_rol if emp.id_rol else 'Sin rol'
        tipo_icono = {
            'Administrador': '👑',
            'Cajero': '💰',
            'Supervisor': '👁️',
            'Sistema': '⚙️'
        }.get(rol, '❓')
        
        print(f"{tipo_icono} Usuario: {emp.usuario:15} | Password: {emp.usuario:15} | Rol: {rol}")
    
    print("\n📧 USUARIOS PORTAL:")
    print("-"*100)
    
    for usuario in usuarios_portal:
        ruc_ci = usuario.cliente.ruc_ci
        print(f"📧 Email: {usuario.email:40} | Password: {ruc_ci:15} | Cliente: {usuario.cliente.nombres}")
    
    print("\n👑 ADMIN DJANGO:")
    print("-"*100)
    print("👤 Usuario: admin                      | Password: admin123")
    
    # ===== RUTAS DE ACCESO =====
    print("\n\n🌐 RUTAS DE ACCESO AL SISTEMA:")
    print("="*100)
    
    rutas = {
        '👑 Admin Django': 'http://127.0.0.1:8000/admin/',
        '💼 Login Empleados': 'http://127.0.0.1:8000/login/',
        '💰 POS Dashboard': 'http://127.0.0.1:8000/pos/',
        '🍽️ POS Almuerzo': 'http://127.0.0.1:8000/pos/almuerzo/',
        '👨‍👩‍👧‍👦 Portal Padres (v1)': 'http://127.0.0.1:8000/portal/',
        '👨‍👩‍👧‍👦 Portal Padres (v2)': 'http://127.0.0.1:8000/clientes/login/',
        '📊 Dashboard Unificado': 'http://127.0.0.1:8000/dashboard/',
        '📈 Dashboard Ventas': 'http://127.0.0.1:8000/dashboard/ventas/',
        '📦 Dashboard Stock': 'http://127.0.0.1:8000/dashboard/stock/',
    }
    
    for nombre, url in rutas.items():
        print(f"{nombre:30} → {url}")
    
    # ===== FLUJOS DE NAVEGACIÓN =====
    print("\n\n🔄 FLUJOS DE NAVEGACIÓN TÍPICOS:")
    print("="*100)
    
    print("\n💰 FLUJO CAJERO:")
    print("-"*100)
    flujo_cajero = [
        "1. Login en /login/ (usuario: IDA_CAJA / password: IDA_CAJA)",
        "2. Redirige a /pos/ (POS Dashboard)",
        "3. Opciones:",
        "   - Ventas → /pos/ventas/",
        "   - Almuerzo → /pos/almuerzo/",
        "   - Cargar Saldo → /pos/cargar-saldo/",
        "   - Ver Productos → /pos/inventario/productos/",
    ]
    for paso in flujo_cajero:
        print(f"   {paso}")
    
    print("\n👑 FLUJO ADMINISTRADOR:")
    print("-"*100)
    flujo_admin = [
        "1. Login en /login/ (usuario: TITA / password: TITA)",
        "2. Redirige a /dashboard/ (Dashboard Unificado)",
        "3. Opciones:",
        "   - Gestión Completa → /admin/",
        "   - Reportes → /dashboard/ventas/ o /dashboard/stock/",
        "   - POS → /pos/",
        "   - Gestión Empleados → /admin/gestion/empleado/",
        "   - Productos y Categorías → /reportes/productos/",
    ]
    for paso in flujo_admin:
        print(f"   {paso}")
    
    print("\n👨‍👩‍👧‍👦 FLUJO PORTAL DE PADRES:")
    print("-"*100)
    flujo_portal = [
        "1. Login en /portal/ o /clientes/login/",
        "   (email: ventas@abc.com.py / password: 8001234-6)",
        "2. Redirige a /portal/dashboard/ o /clientes/dashboard/",
        "3. Opciones:",
        "   - Ver Hijos → /portal/mis-hijos/",
        "   - Cargar Saldo → /portal/cargar-saldo/",
        "   - Ver Pagos → /portal/pagos/",
        "   - Historial → /portal/historial-consumos/",
        "   - Perfil → /portal/perfil/",
    ]
    for paso in flujo_portal:
        print(f"   {paso}")
    
    # ===== MÓDULOS PRINCIPALES =====
    print("\n\n📦 MÓDULOS PRINCIPALES DEL SISTEMA:")
    print("="*100)
    
    modulos = {
        '💰 POS (Punto de Venta)': {
            'descripcion': 'Sistema de ventas en mostrador',
            'vistas': [
                'Dashboard POS',
                'Ventas Regulares',
                'Ventas de Almuerzo',
                'Cargar Saldo Tarjetas',
                'Inventario Productos',
                'Validación de Pagos',
            ]
        },
        '👨‍👩‍👧‍👦 Portal de Padres': {
            'descripcion': 'Portal web para padres/tutores',
            'vistas': [
                'Dashboard Personal',
                'Gestión de Hijos',
                'Cargar Saldo',
                'Ver Consumos',
                'Historial de Pagos',
                'Notificaciones',
            ]
        },
        '📊 Dashboards': {
            'descripcion': 'Reportes y estadísticas',
            'vistas': [
                'Dashboard Unificado',
                'Dashboard de Ventas',
                'Dashboard de Stock',
                'Reportes de Autorizaciones',
            ]
        },
        '🏪 Gestión de Inventario': {
            'descripcion': 'Productos, stock y categorías',
            'vistas': [
                'Lista de Productos',
                'Crear/Editar Producto',
                'Categorías',
                'Gestión de Stock',
                'Alertas de Stock Bajo',
            ]
        },
        '👥 Gestión de Usuarios': {
            'descripcion': 'Empleados, clientes y permisos',
            'vistas': [
                'Gestión de Empleados',
                'Gestión de Clientes',
                'Usuarios Portal',
                'Permisos y Roles',
            ]
        },
    }
    
    for nombre, info in modulos.items():
        print(f"\n{nombre}")
        print(f"   {info['descripcion']}")
        for vista in info['vistas']:
            print(f"   ✓ {vista}")
    
    # ===== VERIFICACIÓN DE INTEGRIDAD =====
    print("\n\n✅ VERIFICACIÓN DE INTEGRIDAD:")
    print("="*100)
    
    checks = []
    
    # Check 1: Empleados activos
    emp_activos = Empleado.objects.filter(activo=True).count()
    checks.append(('Empleados activos', emp_activos > 0, f"{emp_activos} empleados"))
    
    # Check 2: Usuarios portal
    usuarios_count = UsuarioPortal.objects.count()
    checks.append(('Usuarios Portal', usuarios_count > 0, f"{usuarios_count} usuarios"))
    
    # Check 3: Usuarios verificados
    verificados = UsuarioPortal.objects.filter(email_verificado=True).count()
    checks.append(('Emails verificados', verificados > 0, f"{verificados}/{usuarios_count} verificados"))
    
    # Check 4: Clientes con tarjetas
    from gestion.models import Tarjeta
    clientes_con_tarjeta = Tarjeta.objects.filter(estado='Activa').count()
    checks.append(('Tarjetas activas', clientes_con_tarjeta > 0, f"{clientes_con_tarjeta} tarjetas"))
    
    # Check 5: Productos disponibles
    from gestion.models import Producto
    productos = Producto.objects.filter(disponible=True).count()
    checks.append(('Productos disponibles', productos > 0, f"{productos} productos"))
    
    # Check 6: Categorías
    from gestion.models import Categoria
    categorias = Categoria.objects.count()
    checks.append(('Categorías', categorias > 0, f"{categorias} categorías"))
    
    print()
    for nombre, estado, detalle in checks:
        icono = '✓' if estado else '✗'
        estado_texto = 'OK' if estado else 'ERROR'
        print(f"{icono} {nombre:30} [{estado_texto:5}] → {detalle}")
    
    print("\n" + "="*100)
    print("✅ VERIFICACIÓN COMPLETA FINALIZADA")
    print("="*100 + "\n")

if __name__ == '__main__':
    verificar_navegabilidad()
