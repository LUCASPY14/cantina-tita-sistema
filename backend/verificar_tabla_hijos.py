"""
Verificar estructura de la tabla hijos en MySQL
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection

print("=" * 80)
print("🔍 VERIFICANDO TABLA 'hijos' EN MYSQL")
print("=" * 80)

with connection.cursor() as cursor:
    # Verificar si la tabla existe
    cursor.execute("SHOW TABLES LIKE 'hijos'")
    result = cursor.fetchone()
    
    if result:
        print("\n✅ Tabla 'hijos' existe")
        print("\n📋 COLUMNAS EN LA TABLA:")
        cursor.execute("DESCRIBE hijos")
        columns = cursor.fetchall()
        
        for col in columns:
            print(f"\n   Columna: {col[0]}")
            print(f"   Tipo: {col[1]}")
            print(f"   Null: {col[2]}")
            print(f"   Key: {col[3]}")
            print(f"   Default: {col[4]}")
    else:
        print("\n❌ Tabla 'hijos' NO existe")

print("\n" + "=" * 80)
print("🔍 CAMPOS ESPERADOS POR EL MODELO DJANGO:")
print("=" * 80)

from gestion.models import Hijo

print("\nCampos del modelo Hijo:")
for field in Hijo._meta.get_fields():
    if hasattr(field, 'db_column'):
        print(f"   - {field.name} → db_column: {field.db_column}")
    else:
        print(f"   - {field.name} (relación inversa)")

print("\n" + "=" * 80)
