"""
Script para agregar campos de foto a la tabla hijos
Ejecuta el archivo agregar_campo_foto_hijo.sql
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.db import connection

def ejecutar_sql():
    """Ejecuta el script SQL para agregar campos de foto"""
    
    # Leer el archivo SQL
    sql_file = 'agregar_campo_foto_hijo.sql'
    
    if not os.path.exists(sql_file):
        print(f"❌ Error: No se encuentra el archivo {sql_file}")
        return False
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    # Ejecutar SQL
    try:
        with connection.cursor() as cursor:
            # Dividir por punto y coma y ejecutar cada comando
            comandos = [cmd.strip() for cmd in sql_script.split(';') if cmd.strip()]
            
            for comando in comandos:
                if comando:
                    print(f"Ejecutando: {comando[:80]}...")
                    cursor.execute(comando)
            
        print("\n✅ Campos agregados exitosamente a la tabla hijos:")
        print("   - Foto_Perfil (VARCHAR 255)")
        print("   - Fecha_Foto (DATETIME)")
        print("\n🎯 La tabla hijos ahora puede almacenar fotos de perfil")
        return True
        
    except Exception as e:
        print(f"\n❌ Error al ejecutar SQL: {str(e)}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("AGREGAR CAMPOS DE FOTO A TABLA HIJOS")
    print("=" * 60)
    print()
    
    if ejecutar_sql():
        print("\n✅ Proceso completado exitosamente")
    else:
        print("\n❌ El proceso falló")
        sys.exit(1)
