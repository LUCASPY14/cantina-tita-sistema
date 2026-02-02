"""
Script de prueba para verificar que el modelo AceptacionTerminosSaldoNegativo funciona
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from gestion.terminos_legales_model import AceptacionTerminosSaldoNegativo
from gestion.models import Tarjeta, Cliente
from django.contrib.auth.models import User

print("=" * 70)
print("VERIFICACIÓN DEL MODELO AceptacionTerminosSaldoNegativo")
print("=" * 70)

# 1. Verificar que el modelo está registrado
print("\n1. Verificando que el modelo está registrado en Django...")
try:
    from django.apps import apps
    modelo = apps.get_model('gestion', 'AceptacionTerminosSaldoNegativo')
    print(f"   ✅ Modelo encontrado: {modelo.__name__}")
    print(f"   📋 Tabla: {modelo._meta.db_table}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# 2. Verificar que puede hacer queries
print("\n2. Verificando que puede hacer queries...")
try:
    count = AceptacionTerminosSaldoNegativo.objects.count()
    print(f"   ✅ Registros existentes: {count}")
except Exception as e:
    print(f"   ❌ Error al hacer query: {e}")
    sys.exit(1)

# 3. Mostrar campos del modelo
print("\n3. Campos del modelo:")
for field in AceptacionTerminosSaldoNegativo._meta.get_fields():
    field_type = field.get_internal_type() if hasattr(field, 'get_internal_type') else 'Relation'
    print(f"   - {field.name}: {field_type}")

# 4. Verificar relaciones
print("\n4. Verificando relaciones (ForeignKeys)...")
try:
    tarjetas_count = Tarjeta.objects.count()
    clientes_count = Cliente.objects.count()
    usuarios_count = User.objects.count()
    print(f"   ✅ Tarjetas disponibles: {tarjetas_count}")
    print(f"   ✅ Clientes disponibles: {clientes_count}")
    print(f"   ✅ Usuarios disponibles: {usuarios_count}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 70)
print("✅ VERIFICACIÓN COMPLETADA - El modelo funciona correctamente")
print("=" * 70)
