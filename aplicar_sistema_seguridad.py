"""
Script para crear el sistema de seguridad y auditoría
"""
import mysql.connector
from mysql.connector import Error
from decouple import config

def aplicar_sistema_seguridad():
    try:
        connection = mysql.connector.connect(
            host=config('DB_HOST', default='localhost'),
            user=config('DB_USER', default='root'),
            password=config('DB_PASSWORD', default=''),
            database=config('DB_NAME', default='cantinatitadb')
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            print("🔒 Creando sistema de seguridad y auditoría...")
            print("-" * 60)
            
            with open('crear_sistema_seguridad.sql', 'r', encoding='utf-8') as file:
                sql_script = file.read()
            
            # Ejecutar cada statement
            for statement in sql_script.split(';'):
                if statement.strip() and not statement.strip().startswith('--'):
                    try:
                        cursor.execute(statement)
                        connection.commit()
                        
                        for result in cursor:
                            if result:
                                print(result[0] if len(result) == 1 else result)
                    except Error as e:
                        if "already exists" in str(e):
                            print(f"⚠️  Tabla ya existe: {e}")
                        else:
                            print(f"⚠️  Advertencia: {e}")
            
            print("-" * 60)
            print("✅ Sistema de seguridad creado exitosamente")
            print("")
            print("📋 Tablas creadas:")
            print("   - intentos_login (Rate limiting)")
            print("   - auditoria_operaciones (Logging completo)")
            print("   - tokens_recuperacion (Reset password)")
            print("   - bloqueos_cuenta (Seguridad)")
            
            cursor.close()
            connection.close()
            
    except Error as e:
        print(f"❌ Error: {e}")
    except FileNotFoundError:
        print("❌ Archivo SQL no encontrado")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    aplicar_sistema_seguridad()
