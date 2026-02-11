#!/usr/bin/env python
"""Debug script para ver qué está leyendo el script de verificación"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from gestion.models import TipoCliente
from django.db import connection

# Ver columnas de MySQL
with connection.cursor() as cursor:
    cursor.execute("DESCRIBE tipos_cliente")
    mysql_cols = {col[0] for col in cursor.fetchall()}

print("="*80)
print(" Columnas en MySQL:")
print("="*80)
for col in sorted(mysql_cols):
   print(f"  - {col}")

print("\n" + "="*80)
print("🔍 Campos del modelo TipoCliente:")
print("="*80)

for field in TipoCliente._meta.get_fields():
    if hasattr(field, 'db_column'):
        nombre_campo = field.name
        db_col_especificado = field.db_column  # Lo que está en el código
        db_col_real = field.column  # Lo que Django calcula
        
        print(f"\nCampo: {nombre_campo}")
        print(f"  db_column en código: {db_col_especificado}")
        print(f"  column (computed):   {db_col_real}")
        print(f"  ¿Existe en MySQL?    {db_col_especificado in mysql_cols if db_col_especificado else db_col_real in mysql_cols}")
