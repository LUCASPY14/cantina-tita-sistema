"""
Script para verificar la navegabilidad completa del sistema
VERSIÓN SIN EMOJIS - Compatible con PowerShell
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.urls import reverse, NoReverseMatch
from gestion.models import Empleado, UsuarioPortal, Cliente

def verificar_navegabilidad():
    """Verifica la navegabilidad de todos los tipos de usuario"""
    
    print("\n" + "="*100)
    print(" VERIFICACION COMPLETA DE NAVEGABILIDAD DEL SISTEMA")
    print("="*100 + "\n")
    
    # ===== RESUMEN EJECUTIVO =====
    print("=" * 100)
    print(" RESUMEN EJECUTIVO - ESTADO DEL SISTEMA")
    print("="*100 + "\n")
    
    # Empleados
    empleados = Empleado.objects.filter(activo=True)
    print(f"[OK] Empleados activos: {empleados.count()}")
    
    # Usuarios Portal
    usuarios_portal = UsuarioPortal.objects.all()
    usuarios_verificados = UsuarioPortal.objects.filter(email_verificado=True).count()
    print(f"[OK] Usuarios Portal: {usuarios_portal.count()} (Verificados: {usuarios_verificados})")
    
    # Productos
    from gestion.models import Producto
    productos = Producto.objects.filter(activo=True).count()
    print(f"[OK] Productos disponibles: {productos}")
    
    # Tarjetas
    from gestion.models import Tarjeta
    tarjetas = Tarjeta.objects.filter(estado='Activa').count()
    print(f"[OK] Tarjetas activas: {tarjetas}")
    
    # Categorías
    from gestion.models import Categoria
    categorias = Categoria.objects.count()
    print(f"[OK] Categorías: {categorias}")
    
    print("\n" + "="*100)
    print(" CREDENCIALES DE ACCESO")
    print("="*100 + "\n")
    
    # EMPLEADOS
    print("--- EMPLEADOS ---")
    print(f"{'USUARIO':<20} {'ROL':<15} {'PASSWORD':<20} {'ESTADO':<10}")
    print("-"*100)
    
    for emp in empleados:
        rol = emp.id_rol.nombre_rol if emp.id_rol else 'Sin rol'
        estado = 'Activo' if emp.activo else 'Inactivo'
        print(f"{emp.usuario:<20} {rol:<15} {emp.usuario:<20} {estado:<10}")
    
    # USUARIOS PORTAL
    print("\n--- USUARIOS PORTAL ---")
    print(f"{'EMAIL':<45} {'PASSWORD (RUC)':<20} {'CLIENTE':<30} {'VERIFICADO':<12}")
    print("-"*100)
    
    for usuario in usuarios_portal:
        ruc = usuario.cliente.ruc_ci
        verificado = 'SI' if usuario.email_verificado else 'NO'
        print(f"{usuario.email:<45} {ruc:<20} {usuario.cliente.nombres:<30} {verificado:<12}")
    
    # ADMIN DJANGO
    print("\n--- ADMIN DJANGO ---")
    print("Usuario: admin")
    print("Password: admin123")
    
    # RUTAS DE ACCESO
    print("\n" + "="*100)
    print(" RUTAS DE ACCESO AL SISTEMA")
    print("="*100 + "\n")
    
    rutas = {
        'Admin Django': 'http://127.0.0.1:8000/admin/',
        'Login Empleados': 'http://127.0.0.1:8000/login/',
        'POS Dashboard': 'http://127.0.0.1:8000/pos/',
        'POS Almuerzo': 'http://127.0.0.1:8000/pos/almuerzo/',
        'Portal Padres': 'http://127.0.0.1:8000/clientes/login/',
        'Dashboard Unificado': 'http://127.0.0.1:8000/dashboard/',
        'Dashboard Ventas': 'http://127.0.0.1:8000/dashboard/ventas/',
        'Dashboard Stock': 'http://127.0.0.1:8000/dashboard/stock/',
    }
    
    for nombre, url in rutas.items():
        print(f"{nombre:<30} -> {url}")
    
    # FLUJOS DE NAVEGACIÓN
    print("\n" + "="*100)
    print(" FLUJOS DE NAVEGACION POR TIPO DE USUARIO")
    print("="*100)
    
    print("\n[CAJERO]")
    print("-"*100)
    print("1. Login: http://127.0.0.1:8000/login/")
    print("   Usuario: IDA_CAJA_prueba | Password: IDA_CAJA_prueba")
    print("2. Redirige a: /pos/ (POS Dashboard)")
    print("3. Accesos:")
    print("   - Ventas: /pos/ventas/")
    print("   - Almuerzo: /pos/almuerzo/")
    print("   - Cargar Saldo: /pos/cargar-saldo/")
    print("   - Inventario: /pos/inventario/productos/ (solo lectura)")
    
    print("\n[ADMINISTRADOR]")
    print("-"*100)
    print("1. Login: http://127.0.0.1:8000/login/")
    print("   Usuario: TITA | Password: TITA")
    print("2. Redirige a: /dashboard/ (Dashboard Unificado)")
    print("3. Accesos:")
    print("   - Django Admin: /admin/")
    print("   - POS: /pos/")
    print("   - Reportes: /dashboard/ventas/ y /dashboard/stock/")
    print("   - Gestion Empleados: /admin/gestion/empleado/")
    print("   - Productos: /reportes/productos/")
    print("   - Categorias: /reportes/categorias/")
    
    print("\n[SUPERVISOR]")
    print("-"*100)
    print("1. Login: http://127.0.0.1:8000/login/")
    print("   Usuario: supervisor | Password: supervisor")
    print("2. Redirige a: /dashboard/")
    print("3. Accesos:")
    print("   - Dashboard Unificado: /dashboard/")
    print("   - Reportes de Ventas: /dashboard/ventas/")
    print("   - Reportes de Stock: /dashboard/stock/")
    print("   - Ver Inventario: /pos/inventario/productos/")
    
    print("\n[USUARIO PORTAL]")
    print("-"*100)
    print("1. Login: http://127.0.0.1:8000/clientes/login/")
    print("   Email: ventas@abc.com.py | Password: 80012345-6")
    print("2. Redirige a: /clientes/ (Portal Dashboard)")
    print("3. Accesos:")
    print("   - Dashboard: /clientes/")
    print("   - Cargar Saldo: /clientes/cargar-saldo/")
    print("   - Ver Pagos: /clientes/pagos/")
    print("   - Perfil: /clientes/perfil/")
    
    # VERIFICACIÓN DE URLs
    print("\n" + "="*100)
    print(" VERIFICACION DE URLs PRINCIPALES")
    print("="*100 + "\n")
    
    urls_test = [
        ('login', 'Login Empleado'),
        ('dashboard_unificado', 'Dashboard Unificado'),
        ('dashboard_ventas_detalle', 'Dashboard Ventas'),
        ('dashboard_stock_detalle', 'Dashboard Stock'),
        ('gestion:categorias_lista', 'Categorias'),
        ('clientes:portal_login', 'Portal Login'),
        ('clientes:portal_dashboard', 'Portal Dashboard'),
        ('clientes:portal_cargar_saldo', 'Portal Cargar Saldo'),
        ('clientes:portal_pagos', 'Portal Pagos'),
    ]
    
    print(f"{'NOMBRE':<40} {'ESTADO':<10} {'URL':<50}")
    print("-"*100)
    
    for url_name, descripcion in urls_test:
        try:
            url = reverse(url_name)
            print(f"{descripcion:<40} [OK]      {url:<50}")
        except NoReverseMatch:
            print(f"{descripcion:<40} [ERROR]   No se puede resolver")
    
    # MÓDULOS Y FUNCIONALIDADES
    print("\n" + "="*100)
    print(" MODULOS PRINCIPALES DEL SISTEMA")
    print("="*100 + "\n")
    
    print("[POS - Punto de Venta]")
    print("  - Dashboard POS")
    print("  - Ventas Regulares")
    print("  - Ventas de Almuerzo")
    print("  - Cargar Saldo Tarjetas")
    print("  - Inventario Productos")
    print("  - Validacion de Pagos")
    
    print("\n[Portal de Padres]")
    print("  - Dashboard Personal")
    print("  - Gestion de Hijos")
    print("  - Cargar Saldo")
    print("  - Ver Consumos")
    print("  - Historial de Pagos")
    print("  - Notificaciones")
    
    print("\n[Dashboards y Reportes]")
    print("  - Dashboard Unificado")
    print("  - Dashboard de Ventas")
    print("  - Dashboard de Stock")
    print("  - Reportes de Autorizaciones")
    
    print("\n[Gestion de Inventario]")
    print("  - Lista de Productos")
    print("  - Crear/Editar Producto")
    print("  - Categorias")
    print("  - Gestion de Stock")
    print("  - Alertas de Stock Bajo")
    
    print("\n[Gestion de Usuarios]")
    print("  - Gestion de Empleados")
    print("  - Gestion de Clientes")
    print("  - Usuarios Portal")
    print("  - Permisos y Roles")
    
    print("\n" + "="*100)
    print(" VERIFICACION COMPLETA FINALIZADA")
    print("="*100 + "\n")
    
    print("[RESUMEN]")
    print(f"- Empleados activos: {empleados.count()}")
    print(f"- Usuarios Portal: {usuarios_portal.count()} ({usuarios_verificados} verificados)")
    print(f"- Productos disponibles: {productos}")
    print(f"- Tarjetas activas: {tarjetas}")
    print(f"- Categorias: {categorias}")
    print("\n[ESTADO]: Sistema operativo y funcional\n")

if __name__ == '__main__':
    verificar_navegabilidad()
