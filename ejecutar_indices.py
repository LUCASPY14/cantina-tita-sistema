#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ejecutar Script de Optimización de Índices
==========================================
Aplica los índices de optimización usando pymysql
"""

import pymysql
import sys
import os
import django
from pathlib import Path
from datetime import datetime

# Setup Django
sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.conf import settings

def conectar_bd():
    """Conectar a la base de datos usando configuración de Django"""
    try:
        db_config = settings.DATABASES['default']
        conn = pymysql.connect(
            host=db_config['HOST'],
            user=db_config['USER'],
            password=db_config['PASSWORD'],
            database=db_config['NAME'],
            port=int(db_config['PORT']),
            charset='utf8mb4'
        )
        return conn
    except Exception as e:
        print(f"❌ Error conectando a BD: {e}")
        return None

def ejecutar_sql_file(archivo_sql):
    """Ejecutar un archivo SQL línea por línea"""
    
    print("\n" + "="*50)
    print("   OPTIMIZACIÓN DE ÍNDICES - CANTINA POS")
    print("="*50 + "\n")
    
    # Conectar
    conn = conectar_bd()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    # Leer archivo SQL
    print(f"📄 Leyendo: {archivo_sql}")
    try:
        with open(archivo_sql, 'r', encoding='utf-8') as f:
            contenido = f.read()
    except Exception as e:
        print(f"❌ Error leyendo archivo: {e}")
        return False
    
    # Separar por líneas
    lineas = contenido.split('\n')
    comando_actual = ""
    comandos_ejecutados = 0
    comandos_exitosos = 0
    comandos_fallidos = 0
    
    print(f"\n🚀 Ejecutando comandos SQL...\n")
    
    for i, linea in enumerate(lineas, 1):
        # Ignorar comentarios y líneas vacías
        linea = linea.strip()
        if not linea or linea.startswith('--') or linea.startswith('/*'):
            continue
        
        # Acumular líneas hasta encontrar punto y coma
        comando_actual += " " + linea
        
        if linea.endswith(';'):
            comando = comando_actual.strip()
            comando_actual = ""
            
            # Ejecutar comando
            try:
                # Mostrar qué se está ejecutando (primeras 60 chars)
                cmd_preview = comando[:60] + "..." if len(comando) > 60 else comando
                
                if comando.upper().startswith('CREATE INDEX'):
                    # Extraer nombre del índice
                    parts = comando.split()
                    idx_name = parts[2] if len(parts) > 2 else "unknown"
                    print(f"  ✓ Creando índice: {idx_name}")
                elif comando.upper().startswith('ANALYZE TABLE'):
                    table = comando.split()[2].replace(';', '')
                    print(f"  ✓ Analizando tabla: {table}")
                else:
                    print(f"  ▶ {cmd_preview}")
                
                cursor.execute(comando)
                comandos_ejecutados += 1
                comandos_exitosos += 1
                
            except pymysql.err.OperationalError as e:
                error_code = e.args[0]
                
                # Índice duplicado no es error crítico
                if error_code == 1061:  # Duplicate key name
                    print(f"    ℹ️  Ya existe (OK)")
                    comandos_ejecutados += 1
                    comandos_exitosos += 1
                else:
                    print(f"    ❌ Error: {e}")
                    comandos_fallidos += 1
                    
            except Exception as e:
                print(f"    ❌ Error: {e}")
                comandos_fallidos += 1
    
    # Commit de cambios
    conn.commit()
    
    # Resumen
    print("\n" + "="*50)
    print("   RESUMEN DE EJECUCIÓN")
    print("="*50)
    print(f"\n✅ Comandos ejecutados: {comandos_ejecutados}")
    print(f"✅ Exitosos: {comandos_exitosos}")
    if comandos_fallidos > 0:
        print(f"⚠️  Fallidos: {comandos_fallidos}")
    
    # Verificar índices creados
    print("\n" + "="*50)
    print("   VERIFICACIÓN DE ÍNDICES")
    print("="*50 + "\n")
    
    # Tablas principales para verificar
    tablas_principales = [
        'ventas', 'detalle_venta', 'productos', 
        'consumos_tarjeta', 'tarjetas', 'registro_consumo_almuerzo',
        'pagos_tarjeta', 'movimientos_stock'
    ]
    
    total_indices = 0
    for tabla in tablas_principales:
        try:
            cursor.execute(f"SHOW INDEX FROM {tabla}")
            indices = cursor.fetchall()
            # Filtrar índices custom (no PRIMARY)
            indices_custom = [idx for idx in indices if idx[2] != 'PRIMARY']
            if indices_custom:
                print(f"📊 {tabla}: {len(indices_custom)} índices")
                total_indices += len(indices_custom)
        except:
            pass
    
    print(f"\n✅ Total de índices creados: {total_indices}")
    
    # Cerrar conexión
    cursor.close()
    conn.close()
    
    print("\n" + "="*50)
    print(f"   ✅ OPTIMIZACIÓN COMPLETADA")
    print("="*50 + "\n")
    
    return True

if __name__ == "__main__":
    archivo = "optimizar_indices_bd.sql"
    
    print(f"\n🕐 Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    exito = ejecutar_sql_file(archivo)
    
    print(f"🕐 Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    sys.exit(0 if exito else 1)
