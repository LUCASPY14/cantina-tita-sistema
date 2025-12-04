import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    # Eliminar el trigger problemático
    print("Eliminando trigger trg_validar_limite_credito...")
    try:
        cursor.execute("DROP TRIGGER IF EXISTS trg_validar_limite_credito")
        print("✅ Trigger eliminado exitosamente")
    except Exception as e:
        print(f"❌ Error: {e}")
