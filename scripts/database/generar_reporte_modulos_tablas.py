"""
Reporte de Módulos y Tablas - Organización del DER

Genera un reporte detallado de:
1. Módulos del sistema
2. Tablas pertenecientes a cada módulo
3. Tablas sin módulo asignado
4. Relaciones entre tablas
5. Vistas de base de datos

Para organizar el Diagrama Entidad Relación (DER)
"""

import os
import django
import MySQLdb
from collections import defaultdict

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.apps import apps
from gestion.models import *

# ============================================================================
# CONFIGURACIÓN DE CONEXIÓN
# ============================================================================
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'passwd': 'L01G05S33Vice.42',
    'db': 'cantinatitadb'
}

print("=" * 100)
print(" " * 20 + "REPORTE DE MÓDULOS Y TABLAS - ORGANIZACIÓN DER")
print("=" * 100)

# ============================================================================
# PASO 1: OBTENER TODAS LAS TABLAS DE LA BASE DE DATOS
# ============================================================================
print("\n[1] Obteniendo tablas de la base de datos...")

conn = MySQLdb.connect(**DB_CONFIG)
cursor = conn.cursor()

cursor.execute("""
    SELECT TABLE_NAME, TABLE_TYPE, TABLE_COMMENT
    FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = 'cantinatitadb'
    ORDER BY TABLE_TYPE DESC, TABLE_NAME
""")

tablas_bd = {}
vistas_bd = {}
for row in cursor.fetchall():
    nombre, tipo, comentario = row
    if tipo == 'BASE TABLE':
        tablas_bd[nombre] = comentario or ''
    else:
        vistas_bd[nombre] = comentario or ''

print(f"✓ Total tablas encontradas: {len(tablas_bd)}")
print(f"✓ Total vistas encontradas: {len(vistas_bd)}")

# ============================================================================
# PASO 2: CLASIFICAR TABLAS POR MÓDULO SEGÚN MODELOS DJANGO
# ============================================================================
print("\n[2] Clasificando tablas por módulo según modelos Django...")

modulos = defaultdict(list)
tablas_con_modelo = set()

# Obtener todos los modelos de la app 'gestion'
app_models = apps.get_app_config('gestion').get_models()

# Definir categorías de módulos basadas en el análisis del sistema
CATEGORIAS_MODULOS = {
    'PRODUCTOS_Y_CATALOGOS': [
        'Producto', 'Categoria', 'UnidadMedida', 'Impuesto', 
        'ListaPrecios', 'HistoricoPrecios', 'PreciosPorLista',
        'Alergeno', 'ProductoAlergeno'
    ],
    'CLIENTES_Y_FAMILIA': [
        'Cliente', 'TipoCliente', 'Hijo', 'RestriccionesHijos',
        'UsuarioWeb', 'AceptacionTerminosSaldoNegativo'
    ],
    'TARJETAS_Y_SALDOS': [
        'Tarjeta', 'CargasSaldo', 'ConfiguracionLimitesTarjeta'
    ],
    'VENTAS_Y_FACTURACION': [
        'Ventas', 'DetalleVenta', 'TiposPago', 'MediosPago',
        'DocumentosTributarios', 'PuntosExpedicion', 'Timbrado'
    ],
    'PAGOS_Y_COBRANZAS': [
        'PagosVenta', 'PagosPendientes', 'NotasCreditoCliente',
        'DetalleNotaCredito', 'RegistroUsoNotaCredito'
    ],
    'STOCK_E_INVENTARIO': [
        'Stock', 'MovimientosStock', 'AjustesStock'
    ],
    'COMPRAS_Y_PROVEEDORES': [
        'Proveedor', 'Compra', 'DetalleCompra', 'TiposComprobante'
    ],
    'ALMUERZOS': [
        'TiposAlmuerzo', 'PlanesAlmuerzo', 'ComponentesAlmuerzo',
        'SuscripcionesAlmuerzo', 'RegistroConsumoAlmuerzo',
        'CuentasAlmuerzosHijos', 'PagosCuentasAlmuerzo',
        'AutorizacionesConsumo'
    ],
    'EMPLEADOS_Y_SEGURIDAD': [
        'Empleado', 'Rol', 'Permiso', 'EmpleadoPermiso',
        'SesionEmpleado', 'RegistroAcceso', 'Codigo2FA'
    ],
    'CAJA_Y_CIERRE': [
        'CierreCaja', 'DetalleCierreCaja', 'DiferenciaCaja'
    ],
    'PROMOCIONES': [
        'Promocion', 'CondicionPromocion', 'DescuentoPromocion'
    ],
    'COMISIONES': [
        'TarifaComision', 'ComisionTransaccion'
    ],
    'AUDITORIA_Y_LOGS': [
        'RegistroAuditoria'
    ],
    'CUENTA_CORRIENTE': [
        'CuentaCorrienteCliente', 'MovimientoCuentaCorriente'
    ],
    'CONFIGURACION': [
        'ConfiguracionSistema', 'ParametrosSistema'
    ]
}

# Invertir el diccionario para mapeo rápido
modelo_a_categoria = {}
for categoria, modelos_lista in CATEGORIAS_MODULOS.items():
    for modelo in modelos_lista:
        modelo_a_categoria[modelo] = categoria

# Clasificar modelos
for model in app_models:
    nombre_modelo = model.__name__
    categoria = modelo_a_categoria.get(nombre_modelo, 'SIN_CATEGORIA')
    
    try:
        tabla = model._meta.db_table
        tablas_con_modelo.add(tabla)
        
        # Obtener información adicional
        managed = getattr(model._meta, 'managed', True)
        verbose_name = model._meta.verbose_name
        
        modulos[categoria].append({
            'modelo': nombre_modelo,
            'tabla': tabla,
            'managed': managed,
            'verbose_name': verbose_name,
            'comentario': tablas_bd.get(tabla, ''),
            'es_vista': tabla.startswith('v_')
        })
    except Exception as e:
        print(f"  ⚠ Error procesando modelo {nombre_modelo}: {e}")

# Identificar tablas sin modelo
tablas_sin_modelo = set(tablas_bd.keys()) - tablas_con_modelo

print(f"✓ Modelos clasificados en {len(modulos)} categorías")
print(f"✓ Tablas con modelo Django: {len(tablas_con_modelo)}")
print(f"⚠ Tablas sin modelo Django: {len(tablas_sin_modelo)}")

# ============================================================================
# PASO 3: ANALIZAR RELACIONES ENTRE TABLAS
# ============================================================================
print("\n[3] Analizando relaciones (Foreign Keys)...")

cursor.execute("""
    SELECT 
        TABLE_NAME,
        COLUMN_NAME,
        REFERENCED_TABLE_NAME,
        REFERENCED_COLUMN_NAME,
        CONSTRAINT_NAME
    FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
    WHERE TABLE_SCHEMA = 'cantinatitadb'
    AND REFERENCED_TABLE_NAME IS NOT NULL
    ORDER BY TABLE_NAME, COLUMN_NAME
""")

relaciones = defaultdict(list)
for row in cursor.fetchall():
    tabla, columna, tabla_ref, columna_ref, constraint = row
    relaciones[tabla].append({
        'columna': columna,
        'referencia': f"{tabla_ref}.{columna_ref}",
        'constraint': constraint
    })

print(f"✓ Total relaciones encontradas: {sum(len(v) for v in relaciones.values())}")

# ============================================================================
# GENERAR REPORTE
# ============================================================================
print("\n" + "=" * 100)
print(" " * 35 + "REPORTE GENERADO")
print("=" * 100)

reporte = []
reporte.append("=" * 100)
reporte.append(" " * 20 + "REPORTE DE MÓDULOS Y TABLAS - DER CANTINATITADB")
reporte.append("=" * 100)
reporte.append(f"\nFecha de generación: 13 de enero de 2026")
reporte.append(f"Base de datos: cantinatitadb")
reporte.append(f"\nRESUMEN:")
reporte.append(f"  - Total tablas: {len(tablas_bd)}")
reporte.append(f"  - Total vistas: {len(vistas_bd)}")
reporte.append(f"  - Tablas con modelo: {len(tablas_con_modelo)}")
reporte.append(f"  - Tablas sin modelo: {len(tablas_sin_modelo)}")
reporte.append(f"  - Módulos identificados: {len(modulos)}")

# ============================================================================
# DETALLE POR MÓDULO
# ============================================================================
reporte.append("\n" + "=" * 100)
reporte.append("DETALLE DE MÓDULOS Y TABLAS")
reporte.append("=" * 100)

# Ordenar categorías por relevancia
orden_categorias = [
    'PRODUCTOS_Y_CATALOGOS',
    'CLIENTES_Y_FAMILIA',
    'TARJETAS_Y_SALDOS',
    'VENTAS_Y_FACTURACION',
    'PAGOS_Y_COBRANZAS',
    'STOCK_E_INVENTARIO',
    'COMPRAS_Y_PROVEEDORES',
    'ALMUERZOS',
    'EMPLEADOS_Y_SEGURIDAD',
    'CAJA_Y_CIERRE',
    'PROMOCIONES',
    'COMISIONES',
    'AUDITORIA_Y_LOGS',
    'CUENTA_CORRIENTE',
    'CONFIGURACION',
    'SIN_CATEGORIA'
]

for i, categoria in enumerate(orden_categorias, 1):
    if categoria not in modulos:
        continue
    
    tablas_modulo = modulos[categoria]
    if not tablas_modulo:
        continue
    
    # Título del módulo
    nombre_modulo = categoria.replace('_', ' ')
    reporte.append(f"\n{'─' * 100}")
    reporte.append(f"MÓDULO {i}: {nombre_modulo}")
    reporte.append(f"{'─' * 100}")
    reporte.append(f"Total tablas: {len(tablas_modulo)}")
    reporte.append("")
    
    # Listar tablas del módulo
    for j, tabla_info in enumerate(sorted(tablas_modulo, key=lambda x: x['tabla']), 1):
        tabla = tabla_info['tabla']
        modelo = tabla_info['modelo']
        verbose = tabla_info['verbose_name']
        comentario = tabla_info['comentario']
        managed = "Django" if tabla_info['managed'] else "Manual"
        tipo = "VISTA" if tabla_info['es_vista'] else "TABLA"
        
        reporte.append(f"  {j}. {tabla} ({tipo})")
        reporte.append(f"     Modelo: {modelo}")
        reporte.append(f"     Descripción: {verbose}")
        if comentario:
            reporte.append(f"     Comentario BD: {comentario}")
        reporte.append(f"     Gestión: {managed}")
        
        # Relaciones
        if tabla in relaciones and relaciones[tabla]:
            reporte.append(f"     Relaciones FK:")
            for rel in relaciones[tabla]:
                reporte.append(f"       • {rel['columna']} → {rel['referencia']}")
        
        reporte.append("")

# ============================================================================
# TABLAS SIN MÓDULO
# ============================================================================
if tablas_sin_modelo:
    reporte.append(f"\n{'─' * 100}")
    reporte.append("TABLAS SIN MODELO DJANGO ASIGNADO")
    reporte.append(f"{'─' * 100}")
    reporte.append(f"Total: {len(tablas_sin_modelo)}")
    reporte.append("\nEstas tablas existen en la BD pero no tienen modelo en Django:")
    reporte.append("")
    
    for j, tabla in enumerate(sorted(tablas_sin_modelo), 1):
        comentario = tablas_bd.get(tabla, '')
        reporte.append(f"  {j}. {tabla}")
        if comentario:
            reporte.append(f"     Comentario: {comentario}")
        
        # Relaciones
        if tabla in relaciones and relaciones[tabla]:
            reporte.append(f"     Relaciones FK:")
            for rel in relaciones[tabla]:
                reporte.append(f"       • {rel['columna']} → {rel['referencia']}")
        
        reporte.append("")

# ============================================================================
# VISTAS DE BASE DE DATOS
# ============================================================================
if vistas_bd:
    reporte.append(f"\n{'─' * 100}")
    reporte.append("VISTAS DE BASE DE DATOS")
    reporte.append(f"{'─' * 100}")
    reporte.append(f"Total: {len(vistas_bd)}")
    reporte.append("")
    
    for j, (vista, comentario) in enumerate(sorted(vistas_bd.items()), 1):
        reporte.append(f"  {j}. {vista}")
        if comentario:
            reporte.append(f"     Comentario: {comentario}")
        
        # Verificar si tiene modelo
        if vista in tablas_con_modelo:
            # Buscar el modelo
            for cat, tablas in modulos.items():
                modelo_vista = next((t for t in tablas if t['tabla'] == vista), None)
                if modelo_vista:
                    reporte.append(f"     Modelo: {modelo_vista['modelo']}")
                    reporte.append(f"     Módulo: {cat.replace('_', ' ')}")
                    break
        else:
            reporte.append(f"     ⚠ Sin modelo Django")
        
        reporte.append("")

# ============================================================================
# RESUMEN PARA DER
# ============================================================================
reporte.append(f"\n{'=' * 100}")
reporte.append("RECOMENDACIONES PARA ORGANIZAR EL DER")
reporte.append(f"{'=' * 100}")

reporte.append("\n1. AGRUPACIÓN POR MÓDULOS (Color coding sugerido):")
agrupaciones = [
    ("🔵 AZUL", ["PRODUCTOS_Y_CATALOGOS", "STOCK_E_INVENTARIO"]),
    ("🟢 VERDE", ["CLIENTES_Y_FAMILIA", "TARJETAS_Y_SALDOS"]),
    ("🟠 NARANJA", ["VENTAS_Y_FACTURACION", "PAGOS_Y_COBRANZAS"]),
    ("🟡 AMARILLO", ["ALMUERZOS"]),
    ("🔴 ROJO", ["EMPLEADOS_Y_SEGURIDAD", "CAJA_Y_CIERRE"]),
    ("🟣 MORADO", ["COMPRAS_Y_PROVEEDORES"]),
    ("🟤 CAFÉ", ["PROMOCIONES", "COMISIONES"]),
    ("⚫ GRIS", ["AUDITORIA_Y_LOGS", "CUENTA_CORRIENTE", "CONFIGURACION"])
]

for color, categorias in agrupaciones:
    reporte.append(f"\n{color}:")
    for cat in categorias:
        if cat in modulos:
            tablas = [t['tabla'] for t in modulos[cat]]
            reporte.append(f"  • {cat.replace('_', ' ')}: {len(tablas)} tablas")
            reporte.append(f"    {', '.join(tablas[:5])}{'...' if len(tablas) > 5 else ''}")

reporte.append("\n2. ENTIDADES CENTRALES (núcleo del sistema):")
reporte.append("  • clientes (base de todo)")
reporte.append("  • hijos (relacionado con tarjetas y almuerzos)")
reporte.append("  • productos (base de ventas)")
reporte.append("  • ventas (transacciones principales)")
reporte.append("  • tarjetas (sistema de prepago)")

reporte.append("\n3. RELACIONES PRINCIPALES:")
cursor.execute("""
    SELECT 
        TABLE_NAME,
        COUNT(*) as total_fk
    FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
    WHERE TABLE_SCHEMA = 'cantinatitadb'
    AND REFERENCED_TABLE_NAME IS NOT NULL
    GROUP BY TABLE_NAME
    ORDER BY total_fk DESC
    LIMIT 10
""")

reporte.append("  Tablas con más relaciones FK:")
for tabla, total in cursor.fetchall():
    reporte.append(f"    • {tabla}: {total} FK")

reporte.append("\n4. SUGERENCIAS DE DISPOSICIÓN:")
reporte.append("  • Centro: clientes, hijos, tarjetas, ventas")
reporte.append("  • Izquierda: productos, categorías, stock")
reporte.append("  • Derecha: almuerzos, suscripciones")
reporte.append("  • Abajo: empleados, caja, auditoría")
reporte.append("  • Arriba: compras, proveedores")

reporte.append("\n" + "=" * 100)
reporte.append("FIN DEL REPORTE")
reporte.append("=" * 100)

# ============================================================================
# GUARDAR REPORTE
# ============================================================================
archivo_reporte = 'd:/anteproyecto20112025/REPORTE_MODULOS_TABLAS_DER.txt'
with open(archivo_reporte, 'w', encoding='utf-8') as f:
    f.write('\n'.join(reporte))

print(f"\n✅ Reporte generado exitosamente")
print(f"📄 Archivo: {archivo_reporte}")

# Imprimir resumen en consola
print("\n" + "=" * 100)
print("RESUMEN EJECUTIVO")
print("=" * 100)
print(f"\nMÓDULOS IDENTIFICADOS ({len([k for k in modulos.keys() if k != 'SIN_CATEGORIA'])}):")
for cat in orden_categorias:
    if cat in modulos and modulos[cat]:
        nombre = cat.replace('_', ' ')
        total = len(modulos[cat])
        print(f"  • {nombre}: {total} tablas")

if tablas_sin_modelo:
    print(f"\n⚠ TABLAS SIN MODELO ({len(tablas_sin_modelo)}):")
    for tabla in sorted(list(tablas_sin_modelo))[:10]:
        print(f"  • {tabla}")
    if len(tablas_sin_modelo) > 10:
        print(f"  ... y {len(tablas_sin_modelo) - 10} más")

print(f"\n📊 ESTADÍSTICAS:")
print(f"  Total tablas en BD: {len(tablas_bd)}")
print(f"  Total vistas: {len(vistas_bd)}")
print(f"  Tablas modeladas: {len(tablas_con_modelo)}")
print(f"  Relaciones FK: {sum(len(v) for v in relaciones.values())}")

conn.close()

print("\n" + "=" * 100)
print("✅ ANÁLISIS COMPLETADO")
print("=" * 100)
