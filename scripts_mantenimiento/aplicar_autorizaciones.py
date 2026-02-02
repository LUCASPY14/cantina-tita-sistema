#!/usr/bin/env python
"""
Script para aplicar el sistema de autorizaciones con tarjetas.
Ejecuta el SQL que crea las tablas necesarias.
"""

import os
import sys
import django
import pymysql
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.conf import settings

def ejecutar_sql():
    """Ejecuta el script SQL para crear el sistema de autorizaciones"""
    
    print("=" * 80)
    print("APLICANDO SISTEMA DE AUTORIZACIONES CON TARJETAS")
    print("=" * 80)
    
    # Leer el archivo SQL
    sql_file = BASE_DIR / 'crear_sistema_autorizacion.sql'
    
    if not sql_file.exists():
        print(f"\n❌ ERROR: No se encontró el archivo {sql_file}")
        return False
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Conectar a la base de datos
    db_config = settings.DATABASES['default']
    
    try:
        connection = pymysql.connect(
            host=db_config['HOST'],
            user=db_config['USER'],
            password=db_config['PASSWORD'],
            database=db_config['NAME'],
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        
        # Dividir el SQL en statements individuales
        statements = []
        current_statement = []
        
        for line in sql_content.split('\n'):
            line = line.strip()
            
            # Ignorar comentarios y líneas vacías
            if not line or line.startswith('--'):
                continue
            
            current_statement.append(line)
            
            # Si termina con punto y coma, es el fin del statement
            if line.endswith(';'):
                statements.append(' '.join(current_statement))
                current_statement = []
        
        print(f"\n📄 Ejecutando {len(statements)} statements SQL...\n")
        
        for i, statement in enumerate(statements, 1):
            try:
                # Mostrar resumen del statement
                statement_type = statement.split()[0].upper()
                if statement_type == 'CREATE':
                    table_name = statement.split('TABLE')[1].split('(')[0].strip()
                    print(f"[{i}/{len(statements)}] Creando tabla {table_name}...")
                elif statement_type == 'INSERT':
                    print(f"[{i}/{len(statements)}] Insertando datos iniciales...")
                else:
                    print(f"[{i}/{len(statements)}] Ejecutando {statement_type}...")
                
                cursor.execute(statement)
                print(f"    ✅ Completado")
                
            except pymysql.Error as e:
                if 'already exists' in str(e) or 'Duplicate entry' in str(e):
                    print(f"    ⚠️  Ya existe (saltando)")
                else:
                    print(f"    ❌ Error: {e}")
                    raise
        
        connection.commit()
        
        # Verificar las tablas creadas
        print("\n" + "=" * 80)
        print("VERIFICACIÓN DEL SISTEMA")
        print("=" * 80)
        
        # Verificar tarjetas de autorización
        cursor.execute("""
            SELECT 
                Codigo_Barra,
                Tipo_Autorizacion,
                Puede_Anular_Almuerzos,
                Puede_Anular_Ventas,
                Puede_Anular_Recargas,
                Puede_Modificar_Precios,
                Activo
            FROM tarjetas_autorizacion
            ORDER BY ID_Tarjeta_Autorizacion
        """)
        
        tarjetas = cursor.fetchall()
        
        print(f"\n📋 Tarjetas de autorización creadas: {len(tarjetas)}")
        print("\n{:<15} {:<12} {:^8} {:^8} {:^8} {:^8} {:^6}".format(
            "Código", "Tipo", "Almuerzo", "Ventas", "Recarga", "Precio", "Activo"
        ))
        print("-" * 80)
        
        for tarjeta in tarjetas:
            print("{:<15} {:<12} {:^8} {:^8} {:^8} {:^8} {:^6}".format(
                tarjeta[0],
                tarjeta[1],
                '✓' if tarjeta[2] else '✗',
                '✓' if tarjeta[3] else '✗',
                '✓' if tarjeta[4] else '✗',
                '✓' if tarjeta[5] else '✗',
                '✓' if tarjeta[6] else '✗'
            ))
        
        # Verificar tabla de logs
        cursor.execute("SELECT COUNT(*) FROM log_autorizaciones")
        logs_count = cursor.fetchone()[0]
        print(f"\n📊 Logs de autorización: {logs_count} registros")
        
        print("\n" + "=" * 80)
        print("✅ SISTEMA DE AUTORIZACIONES APLICADO EXITOSAMENTE")
        print("=" * 80)
        
        print("\n📝 Próximos pasos:")
        print("   1. Las tarjetas por defecto están creadas (ADMIN001, SUPER001, CAJERO001)")
        print("   2. Implementar vistas para autorizar anulaciones")
        print("   3. Integrar en POS de almuerzos y ventas")
        print("   4. Crear interfaz para gestionar tarjetas")
        
        cursor.close()
        connection.close()
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    try:
        resultado = ejecutar_sql()
        sys.exit(0 if resultado else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Proceso cancelado por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
