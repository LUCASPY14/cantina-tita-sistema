"""
Script para verificar la conexión a la base de datos MySQL
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection
from django.conf import settings

def test_connection():
    """Prueba la conexión a la base de datos"""
    try:
        with connection.cursor() as cursor:
            # Obtener información de la base de datos
            cursor.execute('SELECT DATABASE()')
            db_name = cursor.fetchone()[0]
            
            # Obtener versión de MySQL
            cursor.execute('SELECT VERSION()')
            mysql_version = cursor.fetchone()[0]
            
            # Listar tablas existentes
            cursor.execute('SHOW TABLES')
            tables = cursor.fetchall()
            
            # Mostrar resultados
            print("=" * 60)
            print("✅ CONEXIÓN EXITOSA A MYSQL")
            print("=" * 60)
            print(f"📊 Base de datos: {db_name}")
            print(f"🔧 Versión MySQL: {mysql_version}")
            print(f"🏠 Host: {settings.DATABASES['default']['HOST']}")
            print(f"👤 Usuario: {settings.DATABASES['default']['USER']}")
            print(f"📋 Total de tablas: {len(tables)}")
            
            if tables:
                print("\n📋 Tablas existentes en la base de datos:")
                for table in tables:
                    print(f"   - {table[0]}")
            else:
                print("\n⚠️  No hay tablas en la base de datos")
                print("💡 Ejecuta las migraciones con: python manage.py migrate")
            
            print("\n" + "=" * 60)
            print("✅ La conexión a la base de datos está funcionando correctamente")
            print("=" * 60)
            
            return True
            
    except Exception as e:
        print("=" * 60)
        print("❌ ERROR DE CONEXIÓN")
        print("=" * 60)
        print(f"Error: {str(e)}")
        print("\n💡 Verifica:")
        print("   1. MySQL está ejecutándose")
        print("   2. Las credenciales en el archivo .env son correctas")
        print("   3. La base de datos 'cantinatitadb' existe")
        print("=" * 60)
        return False

if __name__ == '__main__':
    test_connection()
