"""
Script para agregar campo Grado a la tabla hijos
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.db import connection

def ejecutar_sql():
    sql_file = 'agregar_campo_grado_hijo.sql'
    
    if not os.path.exists(sql_file):
        print(f"❌ Error: No se encuentra el archivo {sql_file}")
        return False
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    try:
        with connection.cursor() as cursor:
            # Ejecutar solo el ALTER TABLE (saltar el USE)
            comandos = [cmd.strip() for cmd in sql_script.split(';') if cmd.strip() and 'USE' not in cmd.upper()]
            
            for comando in comandos:
                if comando and 'ALTER TABLE' in comando.upper():
                    print(f"Ejecutando: ALTER TABLE hijos ADD COLUMN Grado...")
                    cursor.execute(comando)
                elif comando and 'DESCRIBE' in comando.upper():
                    print(f"Verificando estructura de tabla...")
                    cursor.execute(comando)
                elif comando and 'SELECT' in comando.upper():
                    cursor.execute(comando)
                    resultado = cursor.fetchone()
                    if resultado:
                        print(f"\n✅ {resultado[0]}")
            
        print("\n✅ Campo Grado agregado exitosamente:")
        print("   - Grado (VARCHAR 50) - Curso actual del estudiante")
        print("\n🎓 Ejemplos de valores: '1ro Básico', '2do Básico', '6to Grado', etc.")
        return True
        
    except Exception as e:
        print(f"\n❌ Error al ejecutar SQL: {str(e)}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("AGREGAR CAMPO GRADO A TABLA HIJOS")
    print("=" * 60)
    print()
    
    if ejecutar_sql():
        print("\n✅ Proceso completado exitosamente")
    else:
        print("\n❌ El proceso falló")
        sys.exit(1)
