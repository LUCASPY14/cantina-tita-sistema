#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verificar Índices Existentes
============================
Muestra todos los índices actuales en las tablas principales
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.conf import settings
import pymysql

def main():
    print("\n" + "="*70)
    print("   VERIFICACIÓN DE ÍNDICES - CANTINA POS")
    print("="*70 + "\n")
    
    # Conectar
    db_config = settings.DATABASES['default']
    conn = pymysql.connect(
        host=db_config['HOST'],
        user=db_config['USER'],
        password=db_config['PASSWORD'],
        database=db_config['NAME'],
        port=int(db_config['PORT'])
    )
    
    cursor = conn.cursor()
    
    # Tablas a verificar
    tablas = [
        'ventas', 'detalle_venta', 'productos', 'tarjetas',
        'consumos_tarjeta', 'registro_consumo_almuerzo',
        'pagos_tarjeta', 'movimientos_stock', 'hijos', 'clientes'
    ]
    
    total_indices = 0
    total_custom = 0
    
    for tabla in tablas:
        try:
            cursor.execute(f"SHOW INDEX FROM {tabla}")
            indices = cursor.fetchall()
            
            print(f"\n📊 Tabla: {tabla}")
            print("   " + "-"*65)
            
            # Agrupar por nombre de índice
            indices_dict = {}
            for idx in indices:
                nombre = idx[2]
                columna = idx[4]
                if nombre not in indices_dict:
                    indices_dict[nombre] = []
                indices_dict[nombre].append(columna)
            
            # Mostrar índices
            primary = 0
            custom = 0
            foreign = 0
            
            for nombre, columnas in indices_dict.items():
                cols_str = ', '.join(columnas)
                
                if nombre == 'PRIMARY':
                    print(f"   🔑 PRIMARY KEY: {cols_str}")
                    primary += 1
                elif '_ibfk_' in nombre:
                    print(f"   🔗 FOREIGN KEY ({nombre}): {cols_str}")
                    foreign += 1
                else:
                    print(f"   ✅ INDEX ({nombre}): {cols_str}")
                    custom += 1
                    total_custom += 1
            
            total = primary + custom + foreign
            print(f"   📈 Total: {total} ({custom} custom, {foreign} FK, {primary} PK)")
            total_indices += total
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "="*70)
    print(f"   RESUMEN GLOBAL")
    print("="*70)
    print(f"\n   ✅ Total de índices: {total_indices}")
    print(f"   ✅ Índices personalizados: {total_custom}")
    print(f"\n   📊 Estado: {'OPTIMIZADO ✅' if total_custom >= 20 else 'NECESITA OPTIMIZACIÓN ⚠️'}")
    print("\n" + "="*70 + "\n")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
