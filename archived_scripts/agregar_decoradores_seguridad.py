"""
Script para agregar decoradores de seguridad a todas las vistas
Sistema Cantina Tita - Enero 2026
"""

import os
import re

# Mapeo de archivos a decorador principal
DECORADORES_POR_ARCHIVO = {
    'pos_views.py': {
        'decorador': 'acceso_cajero',
        'excepciones': {
            # Funciones que requieren admin
            'proveedores_view': 'solo_administrador',
            'proveedor_detalle_view': 'solo_administrador',
            'proveedor_crear': 'solo_administrador',
            'proveedor_editar': 'solo_administrador',
            'proveedor_eliminar': 'solo_administrador',
            'inventario_dashboard': 'solo_administrador',
            'inventario_productos': 'solo_administrador',
            'kardex_producto': 'solo_administrador',
            'ajuste_inventario_view': 'solo_administrador',
            'actualizar_stock_masivo': 'solo_administrador',
            'compras_dashboard_view': 'solo_administrador',
            'nueva_compra_view': 'solo_administrador',
            'recepcion_mercaderia_view': 'solo_administrador',
            'deuda_proveedores_view': 'solo_administrador',
            # Funciones que requieren gerente o superior
            'comisiones_dashboard_view': 'solo_gerente_o_superior',
            'configurar_tarifas_view': 'solo_gerente_o_superior',
            'reporte_comisiones_view': 'solo_gerente_o_superior',
            'reportes_view': 'solo_gerente_o_superior',
            'exportar_reporte': 'solo_gerente_o_superior',
        }
    },
    'producto_views.py': {
        'decorador': 'solo_administrador',
        'excepciones': {}
    },
    'proveedor_views.py': {
        'decorador': 'solo_administrador',
        'excepciones': {}
    },
    'cliente_views.py': {
        'decorador': 'solo_administrador',
        'excepciones': {}
    },
    'comision_views.py': {
        'decorador': 'solo_gerente_o_superior',
        'excepciones': {}
    },
    'reporte_views.py': {
        'decorador': 'solo_gerente_o_superior',
        'excepciones': {}
    },
    'caja_views.py': {
        'decorador': 'acceso_cajero',
        'excepciones': {}
    },
    'almuerzo_views.py': {
        'decorador': 'acceso_cajero',
        'excepciones': {}
    },
}

def agregar_import_permisos(contenido, archivo):
    """Agregar import de permisos si no existe"""
    if 'from gestion.permisos import' in contenido:
        print(f"  ℹ️  {archivo}: Import ya existe")
        return contenido
    
    # Buscar después de otros imports de gestion
    patron = r'(from gestion\.[a-z_]+ import [^\n]+\n)'
    matches = list(re.finditer(patron, contenido))
    
    if matches:
        # Insertar después del último import de gestion
        ultimo_match = matches[-1]
        pos = ultimo_match.end()
        nuevo_import = "from gestion.permisos import acceso_cajero, solo_administrador, solo_gerente_o_superior\n"
        contenido = contenido[:pos] + nuevo_import + contenido[pos:]
        print(f"  ✅ {archivo}: Import agregado después de otros imports de gestion")
    else:
        # Insertar después de django imports
        patron_django = r'(from django\.[a-z._]+ import [^\n]+\n)'
        matches_django = list(re.finditer(patron_django, contenido))
        if matches_django:
            ultimo_match = matches_django[-1]
            pos = ultimo_match.end()
            nuevo_import = "\nfrom gestion.permisos import acceso_cajero, solo_administrador, solo_gerente_o_superior\n"
            contenido = contenido[:pos] + nuevo_import + contenido[pos:]
            print(f"  ✅ {archivo}: Import agregado después de imports de Django")
    
    return contenido

def agregar_decorador_a_funcion(contenido, nombre_funcion, decorador):
    """Agregar decorador a una función específica"""
    # Buscar la función
    patron = rf'(@[a-z_]+\s*(?:\([^)]*\))?\s*\n)*def {nombre_funcion}\('
    match = re.search(patron, contenido)
    
    if not match:
        return contenido, False
    
    # Ver si ya tiene el decorador
    decoradores_existentes = match.group(0)
    if f'@{decorador}' in decoradores_existentes:
        return contenido, False  # Ya tiene el decorador
    
    # Agregar decorador antes de la definición de la función
    pos = match.start()
    # Encontrar la última línea de decoradores
    lineas_antes = contenido[:pos].split('\n')
    
    # Si la línea anterior es un decorador, insertar allí
    if lineas_antes and lineas_antes[-1].strip().startswith('@'):
        nuevo_contenido = contenido[:pos] + f'@{decorador}\n' + contenido[pos:]
    else:
        # Buscar el inicio de los decoradores
        inicio_decoradores = pos
        while inicio_decoradores > 0:
            char_anterior = contenido[inicio_decoradores - 1]
            if char_anterior == '\n':
                linea_anterior = lineas_antes[-1] if lineas_antes else ''
                if not linea_anterior.strip().startswith('@'):
                    break
                inicio_decoradores = contenido.rfind('\n', 0, inicio_decoradores - 1) + 1
            else:
                inicio_decoradores -= 1
        
        nuevo_contenido = contenido[:inicio_decoradores] + f'@{decorador}\n' + contenido[inicio_decoradores:]
    
    return nuevo_contenido, True

def procesar_archivo(archivo, config):
    """Procesar un archivo de vistas"""
    filepath = os.path.join('gestion', archivo)
    
    if not os.path.exists(filepath):
        print(f"⚠️  {archivo}: No encontrado")
        return
    
    print(f"\n📄 Procesando {archivo}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    contenido_original = contenido
    
    # Agregar import
    contenido = agregar_import_permisos(contenido, archivo)
    
    # Encontrar todas las funciones def
    funciones = re.findall(r'^def (\w+)\(request', contenido, re.MULTILINE)
    funciones = [f for f in funciones if not f.startswith('_')]  # Excluir privadas
    
    decorador_default = config['decorador']
    excepciones = config['excepciones']
    
    cambios = 0
    for funcion in funciones:
        decorador = excepciones.get(funcion, decorador_default)
        contenido, modificado = agregar_decorador_a_funcion(contenido, funcion, decorador)
        if modificado:
            print(f"  ✅ {funcion}() → @{decorador}")
            cambios += 1
    
    if contenido != contenido_original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(contenido)
        print(f"\n  💾 {archivo}: {cambios} decoradores agregados")
    else:
        print(f"  ℹ️  {archivo}: Sin cambios necesarios")

def main():
    print("\n" + "="*80)
    print("  AGREGANDO DECORADORES DE SEGURIDAD A TODAS LAS VISTAS")
    print("  Sistema Cantina Tita - Enero 2026")
    print("="*80)
    
    total_archivos = 0
    total_cambios = 0
    
    for archivo, config in DECORADORES_POR_ARCHIVO.items():
        procesar_archivo(archivo, config)
        total_archivos += 1
    
    print("\n" + "="*80)
    print(f"✅ COMPLETADO: {total_archivos} archivos procesados")
    print("="*80 + "\n")
    
    print("📝 SIGUIENTE PASO:")
    print("   Ejecutar: python manage.py check")
    print("   Para verificar que no hay errores de sintaxis")

if __name__ == "__main__":
    main()
