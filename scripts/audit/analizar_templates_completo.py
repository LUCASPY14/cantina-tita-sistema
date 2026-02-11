"""
Script para analizar exhaustivamente todos los templates HTML y organizarlos por categorías
"""
import os
from pathlib import Path
from collections import defaultdict
import re

def extraer_info_template(ruta):
    """Extrae información relevante de un template"""
    try:
        with open(ruta, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        info = {
            'ruta': str(ruta),
            'nombre': ruta.name,
            'carpeta': ruta.parent.name,
            'carpeta_completa': str(ruta.parent.relative_to(BASE_DIR)),
            'extends': None,
            'title': None,
            'acciones': [],
            'modelos': [],
            'formularios': False,
            'tablas': False,
            'modals': False,
            'alpine_js': False,
            'htmx': False,
            'tailwind': False
        }
        
        # Extraer extends
        match_extends = re.search(r'{%\s*extends\s+["\'](.+?)["\']\s*%}', contenido)
        if match_extends:
            info['extends'] = match_extends.group(1)
        
        # Extraer title
        match_title = re.search(r'{%\s*block\s+title\s*%}(.+?){%\s*endblock\s*%}', contenido, re.DOTALL)
        if match_title:
            info['title'] = match_title.group(1).strip()
        
        # Detectar acciones HTTP
        if 'method="POST"' in contenido or 'method=\'POST\'' in contenido:
            info['acciones'].append('POST')
        if 'hx-post' in contenido:
            info['acciones'].append('HTMX-POST')
        if 'hx-get' in contenido:
            info['acciones'].append('HTMX-GET')
        if 'hx-delete' in contenido:
            info['acciones'].append('HTMX-DELETE')
        
        # Detectar modelos comunes
        modelos = ['Producto', 'Cliente', 'Venta', 'Empleado', 'Categoria', 'Almuerzo', 
                   'Recarga', 'Tarjeta', 'Caja', 'Compra', 'Proveedor', 'Usuario']
        for modelo in modelos:
            if modelo.lower() in contenido.lower():
                info['modelos'].append(modelo)
        
        # Detectar características
        info['formularios'] = '<form' in contenido or 'form-' in contenido
        info['tablas'] = '<table' in contenido or 'tabla' in contenido.lower()
        info['modals'] = 'modal' in contenido.lower()
        info['alpine_js'] = 'x-data' in contenido or 'Alpine' in contenido
        info['htmx'] = 'hx-' in contenido
        info['tailwind'] = any(cls in contenido for cls in ['bg-', 'text-', 'flex', 'grid'])
        
        return info
    except Exception as e:
        print(f"Error procesando {ruta}: {e}")
        return None

def categorizar_template(info):
    """Categoriza un template según su propósito"""
    nombre = info['nombre'].lower()
    carpeta = info['carpeta'].lower()
    carpeta_completa = info['carpeta_completa'].lower()
    
    # Base templates
    if 'base' in nombre or carpeta == 'base':
        return 'BASE_TEMPLATES'
    
    # Components
    if carpeta == 'components' or carpeta in ['forms', 'modals', 'navigation', 'widgets']:
        return 'COMPONENTS'
    
    # Emails
    if 'email' in carpeta_completa or 'notification' in carpeta_completa or 'reminder' in carpeta_completa:
        return 'EMAILS'
    
    # Auth
    if any(word in nombre for word in ['login', 'logout', '2fa', 'password', 'auth']):
        return 'AUTH'
    if carpeta == 'auth' or 'two_factor' in carpeta_completa:
        return 'AUTH'
    
    # Dashboard
    if 'dashboard' in nombre or carpeta == 'dashboard':
        return 'DASHBOARDS'
    
    # POS - Ventas
    if any(word in nombre for word in ['venta', 'sale', 'pos', 'ticket']):
        return 'POS_VENTAS'
    
    # POS - Caja
    if any(word in nombre for word in ['caja', 'arqueo', 'apertura', 'cierre', 'cash_register']):
        return 'POS_CAJA'
    
    # Recargas
    if 'recarga' in nombre or carpeta == 'recharges':
        return 'RECARGAS'
    
    # Almuerzos
    if 'almuerzo' in nombre or 'lunch' in carpeta_completa or 'menu' in nombre:
        return 'ALMUERZOS'
    
    # Cuenta Corriente
    if any(word in nombre for word in ['cuenta_corriente', 'cc_', 'saldo']):
        return 'CUENTA_CORRIENTE'
    
    # Inventario
    if any(word in nombre for word in ['inventario', 'stock', 'kardex', 'ajuste', 'inventory']):
        return 'INVENTARIO'
    
    # Productos
    if 'producto' in nombre or carpeta == 'products':
        return 'PRODUCTOS'
    
    # Clientes
    if 'cliente' in nombre or carpeta == 'clients':
        return 'CLIENTES'
    
    # Empleados
    if 'empleado' in nombre or carpeta == 'employees':
        return 'EMPLEADOS'
    
    # Categorías
    if 'categoria' in nombre or carpeta == 'categories':
        return 'CATEGORIAS'
    
    # Compras
    if 'compra' in nombre or carpeta == 'purchases':
        return 'COMPRAS'
    
    # Proveedores
    if 'proveedor' in nombre or carpeta == 'suppliers':
        return 'PROVEEDORES'
    
    # Reportes
    if 'reporte' in nombre or carpeta == 'reports':
        return 'REPORTES'
    
    # Facturación
    if 'facturacion' in nombre:
        return 'FACTURACION'
    
    # Comisiones
    if 'comision' in nombre or carpeta == 'commissions':
        return 'COMISIONES'
    
    # Autorizaciones
    if 'autorizacion' in nombre or 'autorizar' in nombre:
        return 'AUTORIZACIONES'
    
    # Seguridad
    if 'seguridad' in nombre or 'security' in carpeta_completa or 'log' in nombre or 'auditoria' in nombre:
        return 'SEGURIDAD'
    
    # Alertas
    if 'alerta' in nombre:
        return 'ALERTAS'
    
    # Portal Padres
    if 'portal' in carpeta_completa and 'pos' not in carpeta_completa:
        return 'PORTAL_PADRES'
    
    # Admin
    if carpeta == 'admin' or 'admin' in carpeta_completa:
        return 'ADMIN'
    
    # Perfil/Usuario
    if 'perfil' in nombre or 'profile' in carpeta_completa:
        return 'PERFIL'
    
    # Hijos (portal padres)
    if 'hijo' in nombre or 'children' in carpeta_completa:
        return 'PORTAL_HIJOS'
    
    # Pagos
    if 'pago' in nombre or 'payment' in carpeta_completa:
        return 'PAGOS'
    
    # Configuración
    if 'configurar' in nombre or 'settings' in carpeta_completa:
        return 'CONFIGURACION'
    
    return 'OTROS'

# Base directory
BASE_DIR = Path(r'd:\anteproyecto20112025\frontend\templates')

# Analizar todos los templates
templates_por_categoria = defaultdict(list)
todos_los_templates = []

print("🔍 Analizando templates...\n")

for template_path in BASE_DIR.rglob('*.html'):
    info = extraer_info_template(template_path)
    if info:
        categoria = categorizar_template(info)
        templates_por_categoria[categoria].append(info)
        todos_los_templates.append(info)

# Mostrar resultados
print(f"\n📊 ANÁLISIS COMPLETO DE TEMPLATES")
print(f"{'='*80}\n")
print(f"Total de templates encontrados: {len(todos_los_templates)}\n")

# Estadísticas por categoría
print(f"📁 DISTRIBUCIÓN POR CATEGORÍAS:")
print(f"{'-'*80}")
for categoria in sorted(templates_por_categoria.keys()):
    count = len(templates_por_categoria[categoria])
    print(f"{categoria:30} {count:3} templates")

print(f"\n\n📋 DETALLE POR CATEGORÍA:")
print(f"{'='*80}\n")

for categoria in sorted(templates_por_categoria.keys()):
    templates = templates_por_categoria[categoria]
    print(f"\n🔹 {categoria} ({len(templates)} templates)")
    print(f"{'-'*80}")
    
    for info in sorted(templates, key=lambda x: x['carpeta_completa']):
        print(f"  📄 {info['nombre']}")
        print(f"     📂 Ubicación: {info['carpeta_completa']}")
        if info['title']:
            print(f"     📌 Título: {info['title'][:50]}...")
        if info['extends']:
            print(f"     🔗 Extends: {info['extends']}")
        if info['modelos']:
            print(f"     🗂️  Modelos: {', '.join(set(info['modelos'][:3]))}")
        
        caracteristicas = []
        if info['formularios']:
            caracteristicas.append('Formularios')
        if info['tablas']:
            caracteristicas.append('Tablas')
        if info['modals']:
            caracteristicas.append('Modals')
        if info['alpine_js']:
            caracteristicas.append('Alpine.js')
        if info['htmx']:
            caracteristicas.append('HTMX')
        
        if caracteristicas:
            print(f"     ⚙️  Características: {', '.join(caracteristicas)}")
        print()

# Detectar duplicados (mismo nombre en diferentes carpetas)
print(f"\n\n🔄 POSIBLES DUPLICADOS:")
print(f"{'='*80}\n")

nombres_archivos = defaultdict(list)
for info in todos_los_templates:
    nombres_archivos[info['nombre']].append(info['carpeta_completa'])

duplicados = {k: v for k, v in nombres_archivos.items() if len(v) > 1}

if duplicados:
    for nombre, ubicaciones in sorted(duplicados.items()):
        print(f"⚠️  {nombre}")
        for ubicacion in ubicaciones:
            print(f"    - {ubicacion}")
        print()
else:
    print("✅ No se encontraron archivos duplicados por nombre\n")

# Análisis de tecnologías usadas
print(f"\n\n🛠️  TECNOLOGÍAS UTILIZADAS:")
print(f"{'='*80}\n")

tech_stats = {
    'Tailwind CSS': sum(1 for t in todos_los_templates if t['tailwind']),
    'Alpine.js': sum(1 for t in todos_los_templates if t['alpine_js']),
    'HTMX': sum(1 for t in todos_los_templates if t['htmx']),
    'Formularios': sum(1 for t in todos_los_templates if t['formularios']),
    'Tablas': sum(1 for t in todos_los_templates if t['tablas']),
    'Modales': sum(1 for t in todos_los_templates if t['modals']),
}

for tech, count in tech_stats.items():
    porcentaje = (count / len(todos_los_templates)) * 100
    print(f"{tech:20} {count:3} templates ({porcentaje:5.1f}%)")

# Estructura de base templates
print(f"\n\n🏗️  BASE TEMPLATES:")
print(f"{'='*80}\n")

base_templates = [t for t in todos_los_templates if 'base' in t['nombre'].lower()]
for template in base_templates:
    print(f"  {template['nombre']:30} -> {template['carpeta_completa']}")

# Guardar reporte en archivo
reporte_path = BASE_DIR.parent.parent / 'REPORTE_TEMPLATES_ORGANIZACION.md'
with open(reporte_path, 'w', encoding='utf-8') as f:
    f.write("# 📊 Reporte de Organización de Templates\n\n")
    f.write(f"**Fecha:** {Path(__file__).stat().st_mtime}\n")
    f.write(f"**Total de templates:** {len(todos_los_templates)}\n\n")
    
    f.write("## 📁 Distribución por Categorías\n\n")
    for categoria in sorted(templates_por_categoria.keys()):
        count = len(templates_por_categoria[categoria])
        f.write(f"- **{categoria}**: {count} templates\n")
    
    f.write("\n## 📋 Detalle por Categoría\n\n")
    for categoria in sorted(templates_por_categoria.keys()):
        templates = templates_por_categoria[categoria]
        f.write(f"\n### {categoria} ({len(templates)} templates)\n\n")
        
        for info in sorted(templates, key=lambda x: x['carpeta_completa']):
            f.write(f"#### `{info['nombre']}`\n")
            f.write(f"- **Ubicación:** `{info['carpeta_completa']}`\n")
            if info['title']:
                f.write(f"- **Título:** {info['title']}\n")
            if info['extends']:
                f.write(f"- **Extends:** `{info['extends']}`\n")
            if info['modelos']:
                f.write(f"- **Modelos:** {', '.join(set(info['modelos']))}\n")
            f.write("\n")
    
    if duplicados:
        f.write("\n## 🔄 Archivos Duplicados\n\n")
        for nombre, ubicaciones in sorted(duplicados.items()):
            f.write(f"### {nombre}\n")
            for ubicacion in ubicaciones:
                f.write(f"- `{ubicacion}`\n")
            f.write("\n")

print(f"\n\n✅ Reporte guardado en: {reporte_path}")
