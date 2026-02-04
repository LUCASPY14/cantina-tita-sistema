"""
Script para analizar la estructura de todas las tablas en la base de datos
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection

def analyze_database():
    """Analiza todas las tablas y sus relaciones"""
    with connection.cursor() as cursor:
        # Obtener todas las tablas
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        
        print("=" * 80)
        print("📊 ANÁLISIS COMPLETO DE LA BASE DE DATOS 'cantinatitadb'")
        print("=" * 80)
        print(f"\n🔢 Total de tablas: {len(tables)}\n")
        
        # Separar tablas por tipo
        vistas = [t for t in tables if t.startswith('v_')]
        tablas_regulares = [t for t in tables if not t.startswith('v_')]
        
        print(f"📋 Tablas regulares: {len(tablas_regulares)}")
        print(f"👁️  Vistas: {len(vistas)}\n")
        
        # Analizar cada tabla
        tablas_info = {}
        
        for table in tablas_regulares:
            print(f"\n{'='*80}")
            print(f"📦 TABLA: {table}")
            print('='*80)
            
            # Obtener estructura de columnas
            cursor.execute(f"DESCRIBE {table}")
            columns = cursor.fetchall()
            
            print("\n📝 Columnas:")
            for col in columns:
                field, type_, null, key, default, extra = col
                key_info = ""
                if key == "PRI":
                    key_info = " [PRIMARY KEY]"
                elif key == "MUL":
                    key_info = " [FOREIGN KEY]"
                elif key == "UNI":
                    key_info = " [UNIQUE]"
                
                null_info = "NULL" if null == "YES" else "NOT NULL"
                extra_info = f" {extra}" if extra else ""
                
                print(f"   • {field}: {type_} ({null_info}){key_info}{extra_info}")
            
            # Obtener foreign keys
            cursor.execute(f"""
                SELECT 
                    COLUMN_NAME,
                    REFERENCED_TABLE_NAME,
                    REFERENCED_COLUMN_NAME
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                WHERE TABLE_SCHEMA = 'cantinatitadb'
                AND TABLE_NAME = '{table}'
                AND REFERENCED_TABLE_NAME IS NOT NULL
            """)
            
            foreign_keys = cursor.fetchall()
            
            if foreign_keys:
                print("\n🔗 Relaciones (Foreign Keys):")
                for fk in foreign_keys:
                    col, ref_table, ref_col = fk
                    print(f"   • {col} → {ref_table}.{ref_col}")
            
            # Guardar información
            tablas_info[table] = {
                'columns': columns,
                'foreign_keys': foreign_keys
            }
        
        # Mostrar vistas
        if vistas:
            print(f"\n\n{'='*80}")
            print("👁️  VISTAS DE LA BASE DE DATOS")
            print('='*80)
            for vista in vistas:
                print(f"   • {vista}")
        
        # Generar resumen de relaciones
        print(f"\n\n{'='*80}")
        print("🔗 RESUMEN DE RELACIONES ENTRE TABLAS")
        print('='*80)
        
        relaciones = {}
        for tabla, info in tablas_info.items():
            if info['foreign_keys']:
                relaciones[tabla] = info['foreign_keys']
        
        for tabla, fks in sorted(relaciones.items()):
            print(f"\n📦 {tabla}:")
            for fk in fks:
                col, ref_table, ref_col = fk
                print(f"   └─> {ref_table} (via {col})")
        
        # Guardar análisis en archivo
        print(f"\n\n{'='*80}")
        print("💾 Guardando análisis en archivo...")
        print('='*80)
        
        with open('database_analysis.txt', 'w', encoding='utf-8') as f:
            f.write("ANÁLISIS COMPLETO DE LA BASE DE DATOS 'cantinatitadb'\n")
            f.write("="*80 + "\n\n")
            
            f.write(f"Total de tablas: {len(tables)}\n")
            f.write(f"Tablas regulares: {len(tablas_regulares)}\n")
            f.write(f"Vistas: {len(vistas)}\n\n")
            
            for table in tablas_regulares:
                f.write(f"\n{'='*80}\n")
                f.write(f"TABLA: {table}\n")
                f.write('='*80 + "\n\n")
                
                f.write("Columnas:\n")
                for col in tablas_info[table]['columns']:
                    field, type_, null, key, default, extra = col
                    f.write(f"  {field}: {type_} ({null}) [{key}] {extra}\n")
                
                if tablas_info[table]['foreign_keys']:
                    f.write("\nRelaciones:\n")
                    for fk in tablas_info[table]['foreign_keys']:
                        col, ref_table, ref_col = fk
                        f.write(f"  {col} -> {ref_table}.{ref_col}\n")
        
        print("✅ Análisis guardado en: database_analysis.txt")
        print("\n" + "="*80)

if __name__ == '__main__':
    analyze_database()
