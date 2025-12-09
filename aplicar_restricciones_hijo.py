"""
Script para aplicar el campo de restricciones de compra a la tabla hijos
"""
import mysql.connector
from mysql.connector import Error
from decouple import config

def aplicar_campo_restricciones():
    try:
        # Conectar a la base de datos usando las mismas credenciales que Django
        connection = mysql.connector.connect(
            host=config('DB_HOST', default='localhost'),
            user=config('DB_USER', default='root'),
            password=config('DB_PASSWORD', default=''),
            database=config('DB_NAME', default='cantinatitadb')
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            print("🔧 Aplicando campo de restricciones de compra...")
            print("-" * 60)
            
            # Leer el archivo SQL
            with open('agregar_restricciones_hijo.sql', 'r', encoding='utf-8') as file:
                sql_script = file.read()
            
            # Ejecutar cada statement
            for statement in sql_script.split(';'):
                if statement.strip() and not statement.strip().startswith('--'):
                    try:
                        cursor.execute(statement)
                        connection.commit()
                        
                        # Mostrar resultado si hay
                        for result in cursor:
                            if result:
                                print(result[0] if len(result) == 1 else result)
                    except Error as e:
                        if "Duplicate column name" in str(e):
                            print("⚠️  El campo ya existe en la tabla")
                        else:
                            print(f"⚠️  Advertencia: {e}")
            
            print("-" * 60)
            print("✅ Campo de restricciones aplicado exitosamente")
            
            cursor.close()
            connection.close()
            
    except Error as e:
        print(f"❌ Error al conectar con MySQL: {e}")
    except FileNotFoundError:
        print("❌ Archivo SQL no encontrado")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    aplicar_campo_restricciones()
