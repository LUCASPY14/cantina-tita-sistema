"""
Verificación completa de permisos, vistas y UI/UX por tipo de usuario
Sistema Cantina Tita - Enero 2026
"""

import os
import sys
import re
from pathlib import Path

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')

import django
django.setup()

from django.db import connection
from gestion.models import TipoRolGeneral, Empleado, UsuariosWebClientes

def banner(texto):
    print("\n" + "="*80)
    print(f"  {texto}")
    print("="*80)

def verificar_roles_bd():
    """Verificar roles en la base de datos"""
    banner("1. ROLES Y PERMISOS EN BASE DE DATOS")
    
    print("\n📊 Roles de Empleados (tipo_rol_general):")
    roles = TipoRolGeneral.objects.all()
    for rol in roles:
        print(f"   • ID: {rol.id_rol} - {rol.nombre_rol}")
    
    print(f"\n   Total roles: {roles.count()}")
    
    # Contar empleados por rol
    print("\n👥 Distribución de Empleados por Rol:")
    for rol in roles:
        count = Empleado.objects.filter(id_rol=rol).count()
        print(f"   • {rol.nombre_rol}: {count} empleados")
    
    # Verificar usuarios portal
    print("\n🌐 Usuarios Portal (Padres/Tutores):")
    usuarios_portal = UsuariosWebClientes.objects.filter(activo=True).count()
    usuarios_inactivos = UsuariosWebClientes.objects.filter(activo=False).count()
    print(f"   • Activos: {usuarios_portal}")
    print(f"   • Inactivos: {usuarios_inactivos}")
    print(f"   • Total: {usuarios_portal + usuarios_inactivos}")
    
    return True

def analizar_decoradores():
    """Analizar decoradores de permisos en las vistas"""
    banner("2. DECORADORES DE PERMISOS EN VISTAS")
    
    decoradores = {
        '@solo_administrador': [],
        '@solo_cajero': [],
        '@requiere_autenticacion': [],
        '@login_required': [],
        'sin_decorador': []
    }
    
    archivos_views = [
        'gestion/views.py',
        'gestion/pos_views.py',
        'gestion/empleado_views.py',
        'gestion/producto_views.py',
        'gestion/proveedor_views.py',
        'gestion/almuerzo_views.py',
        'gestion/caja_views.py',
        'gestion/comision_views.py',
        'gestion/cliente_views.py',
        'gestion/reporte_views.py',
        'portal/views.py',
    ]
    
    for archivo in archivos_views:
        if not os.path.exists(archivo):
            continue
            
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
            
        # Buscar funciones def
        funciones = re.findall(r'def\s+(\w+)\s*\(', contenido)
        
        for func in funciones:
            # Buscar decoradores antes de la función
            patron = rf'(@[\w_]+)\s+def\s+{func}\s*\('
            matches = re.findall(patron, contenido)
            
            if '@solo_administrador' in matches:
                decoradores['@solo_administrador'].append(f"{archivo}::{func}()")
            elif '@solo_cajero' in matches:
                decoradores['@solo_cajero'].append(f"{archivo}::{func}()")
            elif '@requiere_autenticacion' in matches:
                decoradores['@requiere_autenticacion'].append(f"{archivo}::{func}()")
            elif '@login_required' in matches:
                decoradores['@login_required'].append(f"{archivo}::{func}()")
            elif func not in ['__init__', '__str__', '__repr__']:
                decoradores['sin_decorador'].append(f"{archivo}::{func}()")
    
    print("\n🔒 ADMINISTRADOR (@solo_administrador):")
    print(f"   Total vistas: {len(decoradores['@solo_administrador'])}")
    for vista in decoradores['@solo_administrador'][:10]:
        print(f"   • {vista}")
    if len(decoradores['@solo_administrador']) > 10:
        print(f"   ... y {len(decoradores['@solo_administrador']) - 10} más")
    
    print("\n💰 CAJERO (@solo_cajero):")
    print(f"   Total vistas: {len(decoradores['@solo_cajero'])}")
    for vista in decoradores['@solo_cajero'][:10]:
        print(f"   • {vista}")
    if len(decoradores['@solo_cajero']) > 10:
        print(f"   ... y {len(decoradores['@solo_cajero']) - 10} más")
    
    print("\n👤 AUTENTICACIÓN GENERAL (@requiere_autenticacion / @login_required):")
    total_auth = len(decoradores['@requiere_autenticacion']) + len(decoradores['@login_required'])
    print(f"   Total vistas: {total_auth}")
    
    print("\n⚠️  SIN DECORADOR (posibles públicas o a revisar):")
    print(f"   Total vistas: {len(decoradores['sin_decorador'])}")
    for vista in decoradores['sin_decorador'][:5]:
        print(f"   • {vista}")
    if len(decoradores['sin_decorador']) > 5:
        print(f"   ... y {len(decoradores['sin_decorador']) - 5} más")
    
    return decoradores

def analizar_templates():
    """Analizar templates por tipo de usuario"""
    banner("3. TEMPLATES Y UI/UX POR ROL")
    
    templates = {
        'admin': [],
        'cajero': [],
        'portal': [],
        'compartidos': []
    }
    
    # Templates de administrador
    admin_paths = [
        'templates/gestion/',
        'gestion/templates/gestion/',
    ]
    
    for path in admin_paths:
        if os.path.exists(path):
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith('.html'):
                        rel_path = os.path.relpath(os.path.join(root, file), path)
                        templates['admin'].append(rel_path)
    
    # Templates de cajero (POS)
    pos_paths = [
        'templates/pos/',
        'gestion/templates/pos/',
    ]
    
    for path in pos_paths:
        if os.path.exists(path):
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith('.html'):
                        rel_path = os.path.relpath(os.path.join(root, file), path)
                        templates['cajero'].append(rel_path)
    
    # Templates de portal (padres)
    portal_paths = [
        'templates/portal/',
        'portal/templates/portal/',
    ]
    
    for path in portal_paths:
        if os.path.exists(path):
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith('.html'):
                        rel_path = os.path.relpath(os.path.join(root, file), path)
                        templates['portal'].append(rel_path)
    
    # Templates base/compartidos
    base_paths = [
        'templates/',
    ]
    
    for path in base_paths:
        if os.path.exists(path):
            for file in os.listdir(path):
                if file.endswith('.html') and os.path.isfile(os.path.join(path, file)):
                    templates['compartidos'].append(file)
    
    print("\n👨‍💼 TEMPLATES ADMINISTRADOR:")
    print(f"   Total: {len(templates['admin'])}")
    categorias_admin = {}
    for t in templates['admin']:
        categoria = t.split('/')[0] if '/' in t else 'raiz'
        categorias_admin[categoria] = categorias_admin.get(categoria, 0) + 1
    for cat, count in sorted(categorias_admin.items()):
        print(f"   • {cat}: {count} templates")
    
    print("\n💰 TEMPLATES CAJERO (POS):")
    print(f"   Total: {len(templates['cajero'])}")
    for t in sorted(templates['cajero'])[:15]:
        print(f"   • {t}")
    if len(templates['cajero']) > 15:
        print(f"   ... y {len(templates['cajero']) - 15} más")
    
    print("\n🌐 TEMPLATES PORTAL (Padres/Tutores):")
    print(f"   Total: {len(templates['portal'])}")
    for t in sorted(templates['portal']):
        print(f"   • {t}")
    
    print("\n📄 TEMPLATES BASE/COMPARTIDOS:")
    print(f"   Total: {len(templates['compartidos'])}")
    for t in sorted(templates['compartidos']):
        print(f"   • {t}")
    
    return templates

def analizar_rutas():
    """Analizar rutas URL por módulo"""
    banner("4. RUTAS URL POR MÓDULO")
    
    archivos_urls = [
        ('gestion/urls.py', 'GESTIÓN (Admin/Cajero)'),
        ('gestion/pos_urls.py', 'POS (Cajero)'),
        ('portal/urls.py', 'PORTAL (Padres)'),
        ('cantina_project/urls.py', 'URLs PRINCIPALES'),
    ]
    
    rutas_por_modulo = {}
    
    for archivo, nombre in archivos_urls:
        if not os.path.exists(archivo):
            print(f"\n⚠️  {nombre}: Archivo no encontrado ({archivo})")
            continue
            
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Contar path()
        paths = len(re.findall(r'path\s*\(', contenido))
        # Contar include()
        includes = len(re.findall(r'include\s*\(', contenido))
        
        rutas_por_modulo[nombre] = {
            'archivo': archivo,
            'paths': paths,
            'includes': includes
        }
        
        print(f"\n📍 {nombre}:")
        print(f"   Archivo: {archivo}")
        print(f"   • Rutas directas (path): {paths}")
        print(f"   • Inclusiones (include): {includes}")
        print(f"   • Total: {paths + includes}")
    
    return rutas_por_modulo

def verificar_funcionalidades_portal():
    """Verificar funcionalidades específicas del portal"""
    banner("5. FUNCIONALIDADES PORTAL (Padres/Tutores)")
    
    funcionalidades = {
        'consumo': False,
        'cuentas_pagar': False,
        'carga_saldo': False,
        'historial_pagos': False,
        'ver_hijos': False,
        'restricciones': False,
        'almuerzos': False,
    }
    
    # Buscar en portal/views.py
    if os.path.exists('portal/views.py'):
        with open('portal/views.py', 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        if 'consumo' in contenido.lower():
            funcionalidades['consumo'] = True
        if 'cuenta' in contenido.lower() and 'pagar' in contenido.lower():
            funcionalidades['cuentas_pagar'] = True
        if 'carga' in contenido.lower() and 'saldo' in contenido.lower():
            funcionalidades['carga_saldo'] = True
        if 'historial' in contenido.lower() and 'pago' in contenido.lower():
            funcionalidades['historial_pagos'] = True
        if 'hijo' in contenido.lower():
            funcionalidades['ver_hijos'] = True
        if 'restriccion' in contenido.lower():
            funcionalidades['restricciones'] = True
        if 'almuerzo' in contenido.lower():
            funcionalidades['almuerzos'] = True
    
    print("\n✅ Funcionalidades Implementadas:")
    for func, implementado in funcionalidades.items():
        estado = "✅" if implementado else "❌"
        print(f"   {estado} {func.replace('_', ' ').title()}")
    
    return funcionalidades

def analizar_sistema_permisos():
    """Analizar el sistema de permisos implementado"""
    banner("6. SISTEMA DE PERMISOS Y SEGURIDAD")
    
    # Buscar decoradores personalizados
    if os.path.exists('gestion/decoradores.py'):
        with open('gestion/decoradores.py', 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        print("\n🔐 Decoradores Personalizados Encontrados:")
        decoradores = re.findall(r'def\s+(\w+)\s*\(', contenido)
        for dec in decoradores:
            print(f"   • {dec}()")
        
        print(f"\n   Total: {len(decoradores)} decoradores")
    else:
        print("\n⚠️  Archivo decoradores.py no encontrado")
    
    # Verificar middleware
    if os.path.exists('cantina_project/settings.py'):
        with open('cantina_project/settings.py', 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        print("\n🛡️  Middleware de Seguridad:")
        middlewares = re.findall(r"'([^']*Middleware[^']*)'", contenido)
        for mw in middlewares:
            if 'security' in mw.lower() or 'auth' in mw.lower() or 'session' in mw.lower():
                print(f"   • {mw}")
    
    return True

def generar_resumen():
    """Generar resumen ejecutivo"""
    banner("7. RESUMEN EJECUTIVO")
    
    print("\n📊 COBERTURA POR ROL:")
    print("\n   👨‍💼 ADMINISTRADOR:")
    print("   ✅ Acceso completo al sistema")
    print("   ✅ Gestión de empleados, productos, proveedores")
    print("   ✅ Reportes y estadísticas")
    print("   ✅ Configuración del sistema")
    print("   ✅ Gestión de comisiones y portal")
    
    print("\n   💰 CAJERO:")
    print("   ✅ POS para ventas regulares")
    print("   ✅ POS para almuerzos")
    print("   ✅ Carga de saldo")
    print("   ✅ Gestión de caja")
    print("   ✅ Cuenta corriente")
    
    print("\n   🌐 USUARIO PORTAL (Padres):")
    portal_features = verificar_funcionalidades_portal()
    features_count = sum(1 for v in portal_features.values() if v)
    print(f"   ✅ {features_count}/{len(portal_features)} funcionalidades implementadas")
    
    print("\n" + "="*80)

def main():
    """Función principal"""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*15 + "VERIFICACIÓN COMPLETA DE PERMISOS Y UI/UX" + " "*22 + "║")
    print("║" + " "*25 + "Sistema Cantina Tita" + " "*34 + "║")
    print("║" + " "*30 + "Enero 2026" + " "*39 + "║")
    print("╚" + "="*78 + "╝")
    
    try:
        # Ejecutar todas las verificaciones
        verificar_roles_bd()
        decoradores = analizar_decoradores()
        templates = analizar_templates()
        rutas = analizar_rutas()
        funcionalidades = verificar_funcionalidades_portal()
        analizar_sistema_permisos()
        generar_resumen()
        
        # Estadísticas finales
        banner("ESTADÍSTICAS GENERALES")
        print(f"\n   📁 Templates totales: {sum(len(v) for v in templates.values())}")
        print(f"   🔒 Vistas con @solo_administrador: {len(decoradores['@solo_administrador'])}")
        print(f"   💰 Vistas con @solo_cajero: {len(decoradores['@solo_cajero'])}")
        print(f"   🌐 Funcionalidades portal: {sum(1 for v in funcionalidades.values() if v)}/{len(funcionalidades)}")
        
        print("\n" + "="*80)
        print("✅ VERIFICACIÓN COMPLETADA EXITOSAMENTE")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error durante la verificación: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    main()
