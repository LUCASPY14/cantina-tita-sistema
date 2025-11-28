import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()

# Obtener todas las tablas
print("\n" + "="*80)
print("ANÁLISIS DE LA BASE DE DATOS - cantinatitadb")
print("="*80)

cursor.execute("SHOW TABLES")
all_tables = [table[0] for table in cursor.fetchall()]

print(f"\n📊 Total de tablas en la base de datos: {len(all_tables)}")

# Categorizar las tablas
django_tables = [t for t in all_tables if t.startswith('django_') or t.startswith('auth_')]
almuerzo_tables = [t for t in all_tables if 'almuerzo' in t.lower()]
pos_tables = [t for t in all_tables if t in [
    'categoria_producto', 'producto', 'movimientos_inventario', 
    'ventas', 'detalle_venta', 'caja', 'movimientos_caja'
]]
cliente_tables = [t for t in all_tables if 'cliente' in t.lower() or 'hijo' in t.lower() or 'lista' in t.lower()]
facturacion_tables = [t for t in all_tables if 'factura' in t.lower() or 'pago' in t.lower()]
other_tables = [t for t in all_tables if t not in django_tables + almuerzo_tables + pos_tables + cliente_tables + facturacion_tables]

print("\n" + "="*80)
print("CATEGORIZACIÓN DE TABLAS")
print("="*80)

print(f"\n🔧 Tablas Django/Sistema ({len(django_tables)}):")
for table in sorted(django_tables):
    print(f"  - {table}")

print(f"\n🍽️  Tablas de Almuerzos ({len(almuerzo_tables)}):")
for table in sorted(almuerzo_tables):
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"  - {table} ({count} registros)")

print(f"\n🛒 Tablas de POS/Ventas ({len(pos_tables)}):")
for table in sorted(pos_tables):
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"  - {table} ({count} registros)")

print(f"\n👥 Tablas de Clientes/Hijos ({len(cliente_tables)}):")
for table in sorted(cliente_tables):
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  - {table} ({count} registros)")
    except Exception as e:
        print(f"  - {table} (ERROR: vista inválida)")

print(f"\n💰 Tablas de Facturación/Pagos ({len(facturacion_tables)}):")
for table in sorted(facturacion_tables):
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  - {table} ({count} registros)")
    except Exception as e:
        print(f"  - {table} (ERROR: vista inválida)")

print(f"\n📦 Otras Tablas ({len(other_tables)}):")
for table in sorted(other_tables):
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  - {table} ({count} registros)")
    except Exception as e:
        print(f"  - {table} (ERROR: {str(e)[:50]})")

# Analizar estructura de tablas no implementadas o con pocos datos
print("\n" + "="*80)
print("ANÁLISIS DETALLADO DE TABLAS CON POCOS/SIN DATOS")
print("="*80)

tables_to_analyze = []
for table in all_tables:
    if not table.startswith('django_') and not table.startswith('auth_'):
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            if count < 5:  # Tablas con menos de 5 registros
                tables_to_analyze.append((table, count))
        except Exception:
            # Ignorar vistas inválidas
            pass

for table, count in sorted(tables_to_analyze):
    print(f"\n📋 Tabla: {table} ({count} registros)")
    cursor.execute(f"SHOW COLUMNS FROM {table}")
    columns = cursor.fetchall()
    print("   Campos:")
    for col in columns:
        print(f"     - {col[0]} ({col[1]}) {'NULL' if col[2] == 'YES' else 'NOT NULL'} {col[3] if col[3] else ''}")

# Verificar vistas
print("\n" + "="*80)
print("VISTAS EN LA BASE DE DATOS")
print("="*80)

cursor.execute("SHOW FULL TABLES WHERE Table_Type = 'VIEW'")
views = cursor.fetchall()
if views:
    print(f"\n📊 Total de vistas: {len(views)}")
    for view in views:
        print(f"  - {view[0]}")
else:
    print("\n⚠️  No hay vistas definidas en la base de datos")

# Verificar procedimientos almacenados
print("\n" + "="*80)
print("PROCEDIMIENTOS ALMACENADOS")
print("="*80)

cursor.execute("SHOW PROCEDURE STATUS WHERE Db = 'cantinatitadb'")
procedures = cursor.fetchall()
if procedures:
    print(f"\n⚙️  Total de procedimientos: {len(procedures)}")
    for proc in procedures:
        print(f"  - {proc[1]} (Creado: {proc[4]})")
else:
    print("\n⚠️  No hay procedimientos almacenados")

# Verificar triggers
print("\n" + "="*80)
print("TRIGGERS EN LA BASE DE DATOS")
print("="*80)

cursor.execute("SHOW TRIGGERS")
triggers = cursor.fetchall()
if triggers:
    print(f"\n🔔 Total de triggers: {len(triggers)}")
    trigger_summary = {}
    for trigger in triggers:
        table = trigger[2]
        if table not in trigger_summary:
            trigger_summary[table] = []
        trigger_summary[table].append(trigger[0])
    
    for table, trigger_list in sorted(trigger_summary.items()):
        print(f"\n  📌 {table}:")
        for trig in trigger_list:
            print(f"     - {trig}")
else:
    print("\n⚠️  No hay triggers definidos")

print("\n" + "="*80)
print("RESUMEN Y RECOMENDACIONES")
print("="*80)

print("\n✅ ÁREAS IMPLEMENTADAS:")
print("  - Sistema de Almuerzos (planes, suscripciones, consumos, pagos)")
print("  - Gestión de Clientes e Hijos")

print("\n⚠️  ÁREAS PENDIENTES O CON DATOS MÍNIMOS:")
empty_business_tables = []
for table, count in tables_to_analyze:
    if table not in django_tables and table not in ['auth_group', 'auth_group_permissions', 'auth_permission']:
        empty_business_tables.append((table, count))

if empty_business_tables:
    for table, count in empty_business_tables[:10]:  # Mostrar las primeras 10
        print(f"  - {table} ({count} registros)")

print("\n" + "="*80)
