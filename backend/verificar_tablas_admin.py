"""
Verificar qué tablas existen en MySQL
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection
from django.contrib.admin.sites import site

print("=" * 80)
print("🔍 VERIFICANDO TABLAS EN MYSQL")
print("=" * 80)

# Obtener todas las tablas en la base de datos
with connection.cursor() as cursor:
    cursor.execute("SHOW TABLES")
    existing_tables = {table[0] for table in cursor.fetchall()}

print(f"\n📊 Tablas existentes en MySQL: {len(existing_tables)}")
for table in sorted(existing_tables):
    print(f"   ✓ {table}")

print("\n" + "=" * 80)
print("🔍 VERIFICANDO MODELOS REGISTRADOS EN ADMIN")
print("=" * 80)

# Verificar modelos del admin
registered = site._registry
missing_tables = []

for model in registered.keys():
    table_name = model._meta.db_table
    app_label = model._meta.app_label
    model_name = model.__name__
    
    if table_name not in existing_tables:
        missing_tables.append({
            'app': app_label,
            'model': model_name,
            'table': table_name
        })
        print(f"\n❌ {app_label}.{model_name}")
        print(f"   Tabla esperada: {table_name}")
        print(f"   Estado: NO EXISTE")
    else:
        print(f"\n✅ {app_label}.{model_name}")
        print(f"   Tabla: {table_name}")

print("\n" + "=" * 80)
print("📋 RESUMEN")
print("=" * 80)

if missing_tables:
    print(f"\n⚠️  Modelos SIN tabla ({len(missing_tables)}):")
    for item in missing_tables:
        print(f"   - {item['app']}.{item['model']} → {item['table']}")
    
    print("\n💡 SOLUCIÓN:")
    print("   Estos modelos deben ser desregistrados del admin")
    print("   o crear sus tablas con migraciones.")
else:
    print("\n✅ Todos los modelos del admin tienen sus tablas!")

print("\n" + "=" * 80)
