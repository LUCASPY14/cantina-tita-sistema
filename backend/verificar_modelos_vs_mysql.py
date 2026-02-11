"""
Script completo para verificar modelos de Django vs tablas MySQL
Identifica discrepancias entre db_column y columnas reales
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection
from django.apps import apps
from collections import defaultdict

print("=" * 100)
print("🔍 VERIFICACIÓN COMPLETA: MODELOS DJANGO vs TABLAS MYSQL")
print("=" * 100)

# ========================================================================
# 1. OBTENER TODAS LAS TABLAS EN MYSQL
# ========================================================================
with connection.cursor() as cursor:
    cursor.execute("SHOW TABLES")
    mysql_tables = {table[0] for table in cursor.fetchall()}

print(f"\n📊 TABLAS EN MYSQL: {len(mysql_tables)}")

# ========================================================================
# 2. OBTENER TODOS LOS MODELOS DE DJANGO
# ========================================================================
django_models = []
for app_config in apps.get_app_configs():
    if app_config.name in ['gestion', 'pos']:  # Solo nuestras apps
        for model in app_config.get_models():
            django_models.append(model)

print(f"📦 MODELOS EN DJANGO (gestion + pos): {len(django_models)}")

# ========================================================================
# 3. COMPARAR MODELOS CON TABLAS
# ========================================================================
print("\n" + "=" * 100)
print("📋 ANÁLISIS DETALLADO")
print("=" * 100)

modelos_sin_tabla = []
modelos_con_problemas = []
modelos_ok = []

for model in django_models:
    table_name = model._meta.db_table
    model_name = model.__name__
    app_label = model._meta.app_label
    
    # Verificar si la tabla existe
    if table_name not in mysql_tables:
        modelos_sin_tabla.append({
            'app': app_label,
            'model': model_name,
            'table': table_name
        })
        continue
    
    # Verificar columnas del modelo vs MySQL
    with connection.cursor() as cursor:
        cursor.execute(f"DESCRIBE {table_name}")
        mysql_columns = {col[0] for col in cursor.fetchall()}
    
    # Obtener campos del modelo
    model_columns = {}
    for field in model._meta.get_fields():
        if hasattr(field, 'db_column') and hasattr(field, 'column'):
            db_col = field.db_column or field.get_attname()
            model_columns[field.name] = db_col
    
    # Buscar discrepancias
    problemas = []
    for field_name, db_col in model_columns.items():
        if db_col not in mysql_columns:
            # Verificar si hay una versión en minúsculas
            db_col_lower = db_col.lower()
            if db_col_lower in mysql_columns:
                problemas.append(f"   ❌ Campo '{field_name}' → db_column='{db_col}' (debería ser '{db_col_lower}')")
            else:
                problemas.append(f"   ❌ Campo '{field_name}' → db_column='{db_col}' NO EXISTE en MySQL")
    
    if problemas:
        modelos_con_problemas.append({
            'app': app_label,
            'model': model_name,
            'table': table_name,
            'problemas': problemas
        })
    else:
        modelos_ok.append({
            'app': app_label,
            'model': model_name,
            'table': table_name,
            'columns': len(model_columns)
        })

# ========================================================================
# 4. MOSTRAR RESULTADOS
# ========================================================================

print("\n" + "🚨" * 50)
print("MODELOS SIN TABLA EN MYSQL")
print("🚨" * 50)
if modelos_sin_tabla:
    for item in modelos_sin_tabla:
        print(f"\n❌ {item['app']}.{item['model']}")
        print(f"   Tabla esperada: {item['table']}")
        print(f"   💡 Acción: Desregistrar del admin o crear la tabla")
else:
    print("\n✅ Todos los modelos tienen su tabla en MySQL")

print("\n" + "⚠️ " * 50)
print("MODELOS CON PROBLEMAS DE COLUMNAS")
print("⚠️ " * 50)
if modelos_con_problemas:
    for item in modelos_con_problemas:
        print(f"\n❌ {item['app']}.{item['model']} (tabla: {item['table']})")
        for problema in item['problemas']:
            print(problema)
        print(f"   💡 Acción: Corregir db_column o comentar el campo")
else:
    print("\n✅ Todos los modelos tienen columnas correctas")

print("\n" + "✅" * 50)
print("MODELOS CORRECTOS")
print("✅" * 50)
print(f"\nTotal: {len(modelos_ok)} modelos sin problemas")

# Agrupar por app
ok_por_app = defaultdict(list)
for item in modelos_ok:
    ok_por_app[item['app']].append(item['model'])

for app, models in sorted(ok_por_app.items()):
    print(f"\n📦 {app.upper()}: {len(models)} modelos")
    for model in sorted(models):
        print(f"   ✓ {model}")

# ========================================================================
# 5. RESUMEN FINAL
# ========================================================================
print("\n" + "=" * 100)
print("📊 RESUMEN FINAL")
print("=" * 100)

total = len(django_models)
ok = len(modelos_ok)
sin_tabla = len(modelos_sin_tabla)
con_problemas = len(modelos_con_problemas)

print(f"""
Total de modelos analizados: {total}

✅ Modelos correctos:           {ok} ({ok*100//total}%)
❌ Modelos sin tabla:           {sin_tabla} ({sin_tabla*100//total}%)
⚠️  Modelos con problemas:      {con_problemas} ({con_problemas*100//total}%)

""")

if sin_tabla > 0 or con_problemas > 0:
    print("🔧 ACCIONES NECESARIAS:")
    print("-" * 100)
    
    if sin_tabla > 0:
        print(f"\n1. DESREGISTRAR {sin_tabla} MODELOS DEL ADMIN:")
        for item in modelos_sin_tabla:
            print(f"   - {item['app']}.{item['model']}")
    
    if con_problemas > 0:
        print(f"\n2. CORREGIR {con_problemas} MODELOS CON PROBLEMAS DE COLUMNAS:")
        for item in modelos_con_problemas:
            print(f"   - {item['app']}.{item['model']}")
    
    print("\n" + "=" * 100)
else:
    print("🎉 ¡TODOS LOS MODELOS ESTÁN CORRECTOS!")
    print("=" * 100)
