"""
Script para registrar la migración 0008 directamente en la base de datos
sin ejecutar ningún comando de Django que cause conflictos
"""

import mysql.connector
from decouple import config
from datetime import datetime

def registrar_migracion_manual():
    """Registra la migración 0008 en django_migrations directamente"""
    
    db_config = {
        'host': config('DB_HOST', default='localhost'),
        'user': config('DB_USER', default='root'),
        'password': config('DB_PASSWORD'),
        'database': config('DB_NAME', default='cantitatitadb'),
        'port': config('DB_PORT', default=3306, cast=int)
    }
    
    print(f"Conectando a MySQL: {db_config['user']}@{db_config['host']}/{db_config['database']}...")
    
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Verificar si ya existe la migración
        cursor.execute("""
            SELECT id FROM django_migrations 
            WHERE app = 'gestion' AND name = '0008_aceptacion_terminos_manual'
        """)
        
        if cursor.fetchone():
            print("⚠️  La migración 0008_aceptacion_terminos_manual ya está registrada")
            return True
        
        # Insertar la migración
        sql_insert = """
            INSERT INTO django_migrations (app, name, applied)
            VALUES ('gestion', '0008_aceptacion_terminos_manual', %s)
        """
        
        print("Registrando migración 0008_aceptacion_terminos_manual...")
        cursor.execute(sql_insert, (datetime.now(),))
        conn.commit()
        
        # Verificar
        cursor.execute("""
            SELECT id, app, name, applied 
            FROM django_migrations 
            WHERE app = 'gestion' 
            ORDER BY id DESC 
            LIMIT 5
        """)
        
        print("\n✅ Últimas 5 migraciones de 'gestion':")
        for row in cursor.fetchall():
            print(f"  [{row[0]}] {row[1]}.{row[2]} - {row[3]}")
        
        return True
        
    except mysql.connector.Error as e:
        print(f"❌ Error de MySQL: {e}")
        return False
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


if __name__ == '__main__':
    print("=" * 70)
    print("REGISTRAR MIGRACIÓN 0008 MANUALMENTE")
    print("=" * 70)
    
    success = registrar_migracion_manual()
    
    if success:
        print("\n✅ ÉXITO: Migración registrada")
        print("\n📋 Verificar con: python manage.py showmigrations gestion")
    else:
        print("\n❌ FALLO: No se pudo registrar la migración")
