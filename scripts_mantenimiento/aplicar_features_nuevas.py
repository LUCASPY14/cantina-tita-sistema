"""
Script para aplicar migraciones de features nuevas:
- Alérgenos y restricciones alimentarias
- Promociones y descuentos
"""
import os
import django
import sys

sys.path.append('D:/anteproyecto20112025')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection

def ejecutar_sql_desde_archivo(archivo):
    """Ejecuta comandos SQL desde un archivo"""
    print(f"\n{'='*70}")
    print(f" EJECUTANDO: {archivo}")
    print(f"{'='*70}\n")
    
    with open(archivo, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Dividir por statements (ignoring comments)
    statements = []
    current_statement = []
    
    for line in sql_content.split('\n'):
        line = line.strip()
        
        # Ignorar comentarios y líneas vacías
        if line.startswith('--') or line.startswith('/*') or not line:
            continue
        if line.startswith('*/'):
            continue
            
        current_statement.append(line)
        
        # Si termina con ; es un statement completo
        if line.endswith(';'):
            full_statement = ' '.join(current_statement)
            if full_statement.strip():
                statements.append(full_statement)
            current_statement = []
    
    # Ejecutar cada statement
    with connection.cursor() as cursor:
        exitos = 0
        errores = 0
        
        for i, statement in enumerate(statements, 1):
            try:
                # Ignorar statements de comentarios
                if 'USE cantinatitadb' in statement:
                    continue
                    
                cursor.execute(statement)
                
                # Mostrar progreso para ciertos comandos
                if statement.strip().upper().startswith('CREATE TABLE'):
                    table_name = statement.split('CREATE TABLE')[1].split('(')[0].strip().replace('IF NOT EXISTS', '').strip()
                    print(f"✓ Tabla creada: {table_name}")
                    exitos += 1
                elif statement.strip().upper().startswith('INSERT INTO'):
                    table_name = statement.split('INSERT INTO')[1].split('(')[0].strip()
                    print(f"✓ Datos insertados en: {table_name}")
                    exitos += 1
                elif statement.strip().upper().startswith('SELECT'):
                    if 'FROM alergenos' in statement or 'FROM promociones' in statement:
                        results = cursor.fetchall()
                        print(f"✓ Consulta ejecutada: {len(results)} registros")
                        for row in results:
                            print(f"  {row}")
                    exitos += 1
                else:
                    exitos += 1
                    
            except Exception as e:
                print(f"✗ Error en statement {i}: {e}")
                print(f"  SQL: {statement[:100]}...")
                errores += 1
        
        print(f"\n{'='*70}")
        print(f" RESUMEN:")
        print(f" ✓ Exitosos: {exitos}")
        print(f" ✗ Errores: {errores}")
        print(f"{'='*70}\n")
        
        return errores == 0


def main():
    print("\n")
    print("█" * 70)
    print("█" + " " * 68 + "█")
    print("█" + "  APLICAR MIGRACIONES - FEATURES NUEVAS".center(68) + "█")
    print("█" + " " * 68 + "█")
    print("█" * 70)
    
    archivo_sql = 'migrations_features_nuevas.sql'
    
    if not os.path.exists(archivo_sql):
        print(f"\n❌ ERROR: No se encontró el archivo {archivo_sql}")
        return False
    
    try:
        exito = ejecutar_sql_desde_archivo(archivo_sql)
        
        if exito:
            print("\n✅ MIGRACIONES APLICADAS EXITOSAMENTE\n")
            print("Tablas creadas:")
            print("  1. alergenos")
            print("  2. producto_alergenos")
            print("  3. promociones")
            print("  4. productos_promocion")
            print("  5. categorias_promocion")
            print("  6. promociones_aplicadas")
            print("\nDatos iniciales:")
            print("  - 10 alérgenos comunes")
            print("  - 3 promociones ejemplo")
            print("\nPróximo paso:")
            print("  - Registrar modelos en admin.py")
            print("  - Crear utils para matching de restricciones")
            print("  - Crear utils para cálculo de promociones")
            return True
        else:
            print("\n⚠️ Hubo algunos errores durante la migración")
            print("Revisa los mensajes arriba para más detalles")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    try:
        if main():
            print("\n✅ Proceso completado exitosamente")
            sys.exit(0)
        else:
            print("\n❌ Proceso completado con errores")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Proceso interrumpido por el usuario")
        sys.exit(1)
