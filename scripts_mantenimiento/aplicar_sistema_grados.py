"""
Script para crear el sistema de gestión de grados
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.db import connection

def ejecutar_sql():
    sql_file = 'crear_sistema_grados.sql'
    
    if not os.path.exists(sql_file):
        print(f"❌ Error: No se encuentra el archivo {sql_file}")
        return False
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    try:
        with connection.cursor() as cursor:
            # Ejecutar comandos (saltar el USE)
            comandos = [cmd.strip() for cmd in sql_script.split(';') if cmd.strip() and 'USE' not in cmd.upper()]
            
            for comando in comandos:
                if comando:
                    if 'CREATE TABLE' in comando.upper():
                        tabla = 'grados' if 'grados (' in comando else 'historial_grados_hijos'
                        print(f"Creando tabla: {tabla}...")
                        cursor.execute(comando)
                    elif 'INSERT INTO' in comando.upper():
                        print(f"Insertando grados predefinidos...")
                        cursor.execute(comando)
                    elif 'SELECT' in comando.upper():
                        cursor.execute(comando)
                        resultado = cursor.fetchone()
                        if resultado:
                            print(f"  {resultado[0]}")
            
        print("\n✅ Sistema de grados creado exitosamente:")
        print("   📋 Tabla 'grados' - Catálogo de niveles educativos")
        print("   📜 Tabla 'historial_grados_hijos' - Auditoría de cambios")
        print("   🎓 14 grados predefinidos insertados")
        print("\n📚 Grados disponibles:")
        print("   • Jardín, Pre-escolar")
        print("   • 1° a 9° Grado (Educación Básica)")
        print("   • 1° a 3° Curso (Educación Media)")
        return True
        
    except Exception as e:
        print(f"\n❌ Error al ejecutar SQL: {str(e)}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("CREAR SISTEMA DE GESTIÓN DE GRADOS")
    print("=" * 60)
    print()
    
    if ejecutar_sql():
        print("\n✅ Proceso completado exitosamente")
    else:
        print("\n❌ El proceso falló")
        sys.exit(1)
