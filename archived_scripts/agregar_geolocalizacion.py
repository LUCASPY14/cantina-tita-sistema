import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection

def agregar_columnas_geolocalizacion():
    """Agregar columnas ciudad y pais a tablas de seguridad"""
    print("🌍 Agregando columnas de geolocalización...")
    
    with connection.cursor() as cursor:
        # Verificar y agregar a intentos_login
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'intentos_login' 
            AND COLUMN_NAME = 'ciudad'
        """)
        if cursor.fetchone()[0] == 0:
            cursor.execute("ALTER TABLE intentos_login ADD COLUMN ciudad VARCHAR(100) AFTER ip_address")
            print("✅ Columna 'ciudad' agregada a intentos_login")
        else:
            print("ℹ️ Columna 'ciudad' ya existe en intentos_login")
        
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'intentos_login' 
            AND COLUMN_NAME = 'pais'
        """)
        if cursor.fetchone()[0] == 0:
            cursor.execute("ALTER TABLE intentos_login ADD COLUMN pais VARCHAR(100) AFTER ciudad")
            print("✅ Columna 'pais' agregada a intentos_login")
        else:
            print("ℹ️ Columna 'pais' ya existe en intentos_login")
        
        # Verificar y agregar a auditoria_operaciones
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'auditoria_operaciones' 
            AND COLUMN_NAME = 'ciudad'
        """)
        if cursor.fetchone()[0] == 0:
            cursor.execute("ALTER TABLE auditoria_operaciones ADD COLUMN ciudad VARCHAR(100) AFTER ip_address")
            print("✅ Columna 'ciudad' agregada a auditoria_operaciones")
        else:
            print("ℹ️ Columna 'ciudad' ya existe en auditoria_operaciones")
        
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'auditoria_operaciones' 
            AND COLUMN_NAME = 'pais'
        """)
        if cursor.fetchone()[0] == 0:
            cursor.execute("ALTER TABLE auditoria_operaciones ADD COLUMN pais VARCHAR(100) AFTER ciudad")
            print("✅ Columna 'pais' agregada a auditoria_operaciones")
        else:
            print("ℹ️ Columna 'pais' ya existe en auditoria_operaciones")
    
    print("✅ Proceso completado!")

if __name__ == '__main__':
    agregar_columnas_geolocalizacion()
