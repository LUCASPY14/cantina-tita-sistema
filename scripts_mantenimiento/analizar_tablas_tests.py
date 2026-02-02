"""
Script para analizar estructura de tablas para crear tests
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection

def analizar_tabla(tabla):
    """Analiza la estructura de una tabla"""
    print(f"\n{'='*60}")
    print(f"TABLA: {tabla}")
    print('='*60)
    
    with connection.cursor() as cursor:
        # Obtener estructura
        cursor.execute(f'DESCRIBE {tabla}')
        columns = cursor.fetchall()
        
        print("\nCOLUMNAS:")
        for col in columns:
            field, tipo, null, key, default, extra = col
            print(f"  - {field:30} {tipo:20} {'NULL' if null=='YES' else 'NOT NULL':10} {key:5} {extra}")
        
        # Obtener foreign keys
        cursor.execute(f"""
            SELECT 
                COLUMN_NAME, 
                REFERENCED_TABLE_NAME, 
                REFERENCED_COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = 'cantinatitadb'
              AND TABLE_NAME = '{tabla}'
              AND REFERENCED_TABLE_NAME IS NOT NULL
        """)
        fks = cursor.fetchall()
        
        if fks:
            print("\nFOREIGN KEYS:")
            for fk in fks:
                print(f"  - {fk[0]} -> {fk[1]}.{fk[2]}")
        
        # Contar registros
        cursor.execute(f'SELECT COUNT(*) FROM {tabla}')
        count = cursor.fetchone()[0]
        print(f"\nREGISTROS EXISTENTES: {count}")

# Tablas críticas sin tests
print("\n" + "="*60)
print("ANÁLISIS DE TABLAS PARA CREAR TESTS")
print("="*60)

print("\n" + "#"*60)
print("# 1. INVENTARIO Y STOCK")
print("#"*60)
analizar_tabla('stock_unico')
analizar_tabla('movimientos_stock')
analizar_tabla('ajustes_inventario')
analizar_tabla('detalle_ajuste')

print("\n" + "#"*60)
print("# 2. PRECIOS Y LISTAS")
print("#"*60)
analizar_tabla('listas_precios')
analizar_tabla('precios_por_lista')
analizar_tabla('historico_precios')

print("\n" + "#"*60)
print("# 3. NOTAS DE CRÉDITO")
print("#"*60)
analizar_tabla('notas_credito')
analizar_tabla('detalle_nota')

print("\n" + "#"*60)
print("# 4. COMISIONES")
print("#"*60)
analizar_tabla('tarifas_comision')
analizar_tabla('detalle_comision_venta')

print("\n" + "#"*60)
print("# 5. OTRAS TABLAS IMPORTANTES")
print("#"*60)
analizar_tabla('puntos_expedicion')
analizar_tabla('impuestos')
analizar_tabla('unidades_medida')

print("\n" + "="*60)
print("ANÁLISIS COMPLETADO")
print("="*60)
