"""
Análisis Final de Permisos y Decoradores
Sistema Cantina Tita - Enero 2026
"""

import os
import sys
import re
from pathlib import Path

def banner(texto):
    print("\n" + "="*80)
    print(f"  {texto}")
    print("="*80)

def contar_decoradores_por_archivo():
    """Contar decoradores en cada archivo de vistas"""
    banner("ANÁLISIS DE DECORADORES POR ARCHIVO")
    
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
        'gestion/dashboard_views.py',
        'gestion/pagos_admin_views.py',
        'gestion/portal_views.py',
    ]
    
    decoradores_encontrados = {
        '@solo_administrador': 0,
        '@solo_gerente_o_superior': 0,
        '@acceso_cajero': 0,
        '@requiere_rol': 0,
        '@login_required_portal': 0,
    }
    
    total_funciones = 0
    funciones_protegidas = 0
    
    for archivo in archivos_views:
        if not os.path.exists(archivo):
            continue
            
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Encontrar todas las funciones
        funciones = re.findall(r'^def\s+(\w+)\s*\(', contenido, re.MULTILINE)
        # Filtrar funciones privadas y especiales
        funciones = [f for f in funciones if not f.startswith('_')]
        
        total_funciones += len(funciones)
        
        # Contar decoradores
        for decorador in decoradores_encontrados.keys():
            count = len(re.findall(re.escape(decorador), contenido))
            decoradores_encontrados[decorador] += count
            funciones_protegidas += count
        
        # Mostrar por archivo
        archivo_corto = archivo.split('/')[-1]
        decoradores_archivo = sum(len(re.findall(re.escape(d), contenido)) for d in decoradores_encontrados.keys())
        
        if decoradores_archivo > 0:
            print(f"\n📄 {archivo_corto}")
            print(f"   Funciones: {len(funciones)} | Protegidas: {decoradores_archivo}")
            
            for dec, _ in decoradores_encontrados.items():
                count = len(re.findall(re.escape(dec), contenido))
                if count > 0:
                    print(f"   • {dec}: {count}")
    
    print("\n" + "-"*80)
    print("\n📊 TOTALES GENERALES:")
    print(f"   Total funciones públicas: {total_funciones}")
    print(f"   Funciones protegidas: {funciones_protegidas}")
    print(f"   Sin protección: {total_funciones - funciones_protegidas}")
    print(f"   % Protegidas: {(funciones_protegidas/total_funciones*100):.1f}%")
    
    print("\n🔒 DECORADORES USADOS:")
    for dec, count in sorted(decoradores_encontrados.items(), key=lambda x: -x[1]):
        if count > 0:
            print(f"   • {dec}: {count} vistas")
    
    return decoradores_encontrados, total_funciones, funciones_protegidas

def verificar_archivo_permisos():
    """Verificar existencia y contenido del archivo de permisos"""
    banner("SISTEMA DE PERMISOS")
    
    archivo_permisos = 'gestion/permisos.py'
    
    if os.path.exists(archivo_permisos):
        print(f"\n✅ Archivo de permisos encontrado: {archivo_permisos}")
        
        with open(archivo_permisos, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        print(f"\n📐 Tamaño: {len(contenido)} caracteres")
        
        # Buscar decoradores definidos
        decoradores = re.findall(r'^def\s+(\w+)\s*\(', contenido, re.MULTILINE)
        print(f"\n🔧 Decoradores definidos ({len(decoradores)}):")
        for dec in decoradores:
            if not dec.startswith('_'):
                print(f"   • {dec}()")
        
        # Buscar constantes de roles
        roles = re.findall(r"ROL_\w+\s*=\s*'(\w+)'", contenido)
        print(f"\n👥 Roles definidos ({len(roles)}):")
        for rol in roles:
            print(f"   • {rol}")
        
    else:
        print(f"\n❌ Archivo de permisos NO encontrado: {archivo_permisos}")
        print("   ⚠️  Se recomienda crear este archivo con los decoradores")

def main():
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*18 + "ANÁLISIS FINAL DE PERMISOS Y DECORADORES" + " "*20 + "║")
    print("║" + " "*25 + "Sistema Cantina Tita" + " "*34 + "║")
    print("╚" + "="*78 + "╝")
    
    verificar_archivo_permisos()
    decoradores, total, protegidas = contar_decoradores_por_archivo()
    
    # Conclusión
    banner("CONCLUSIÓN")
    
    porcentaje = (protegidas/total*100) if total > 0 else 0
    
    if porcentaje >= 80:
        estado = "✅ EXCELENTE"
    elif porcentaje >= 60:
        estado = "⚠️ BUENO (mejorar)"
    elif porcentaje >= 40:
        estado = "⚠️ REGULAR (revisar)"
    else:
        estado = "❌ CRÍTICO (urgente)"
    
    print(f"\n🎯 Estado de Seguridad: {estado}")
    print(f"   Protección: {porcentaje:.1f}% de las vistas")
    print(f"   Vistas protegidas: {protegidas}/{total}")
    print(f"   Vistas sin decorador: {total - protegidas}")
    
    print("\n📝 Recomendaciones:")
    if porcentaje < 100:
        print(f"   • Agregar decoradores a {total - protegidas} vistas restantes")
    print("   • Verificar que vistas sin decorador sean realmente públicas")
    print("   • Considerar usar @requiere_rol_minimo para jerarquías")
    print("   • Implementar tests de permisos")
    
    print("\n" + "="*80)
    print("✅ ANÁLISIS COMPLETADO")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
