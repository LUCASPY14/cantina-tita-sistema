"""
Script de Migración: Cuenta Corriente con Tablas Intermedias
Sistema Cantina Tita
Fecha: 2025-12-02

Este script ejecuta la migración de forma segura:
1. Verifica pre-requisitos
2. Crea backup de tablas afectadas
3. Ejecuta la migración
4. Valida resultados
"""

import os
import sys
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
import django
django.setup()

from django.db import connection, transaction

def print_section(title):
    """Imprime un separador de sección"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def verificar_prerequisitos():
    """Verifica que existan las tablas necesarias"""
    print_section("PASO 1: Verificando Pre-requisitos")
    
    tablas_requeridas = ['ventas', 'compras', 'pagos_venta', 'clientes', 'proveedores', 'medios_pago']
    
    with connection.cursor() as cursor:
        for tabla in tablas_requeridas:
            cursor.execute(f"SHOW TABLES LIKE '{tabla}'")
            if not cursor.fetchone():
                print(f"  [ERROR] Tabla requerida no existe: {tabla}")
                return False
            else:
                print(f"  [OK] Tabla existe: {tabla}")
    
    print("\n  Todos los pre-requisitos cumplidos!")
    return True

def crear_backup():
    """Crea backup de tablas que serán modificadas"""
    print_section("PASO 2: Creando Backup de Seguridad")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    tablas_backup = ['ventas', 'compras', 'pagos_venta', 'cta_corriente', 'cta_corriente_prov']
    
    with connection.cursor() as cursor:
        for tabla in tablas_backup:
            cursor.execute(f"SHOW TABLES LIKE '{tabla}'")
            if cursor.fetchone():
                nombre_backup = f"{tabla}_backup_{timestamp}"
                print(f"  Creando backup: {nombre_backup}...")
                try:
                    cursor.execute(f"CREATE TABLE {nombre_backup} LIKE {tabla}")
                    cursor.execute(f"INSERT INTO {nombre_backup} SELECT * FROM {tabla}")
                    print(f"  [OK] Backup creado: {nombre_backup}")
                except Exception as e:
                    print(f"  [ADVERTENCIA] No se pudo crear backup de {tabla}: {e}")
    
    print(f"\n  Backups creados con timestamp: {timestamp}")
    return timestamp

def ejecutar_migracion():
    """Ejecuta el script SQL de migración"""
    print_section("PASO 3: Ejecutando Migración")
    
    # Leer el script SQL
    script_path = 'migracion_cta_corriente.sql'
    
    if not os.path.exists(script_path):
        print(f"  [ERROR] No se encontró el archivo: {script_path}")
        return False
    
    with open(script_path, 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    # Dividir en sentencias individuales
    sentencias = [s.strip() for s in sql_script.split(';') if s.strip() and not s.strip().startswith('--')]
    
    print(f"  Ejecutando {len(sentencias)} sentencias SQL...")
    
    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                for i, sentencia in enumerate(sentencias, 1):
                    # Saltar comentarios y líneas vacías
                    if sentencia.startswith('SELECT') and 'Paso' in sentencia:
                        print(f"\n  [{i}/{len(sentencias)}] {sentencia[:60]}...")
                        cursor.execute(sentencia)
                        resultado = cursor.fetchall()
                        if resultado:
                            print(f"       > {resultado[0][0]}")
                    elif sentencia.strip():
                        # Ejecutar sentencia
                        cursor.execute(sentencia)
                        
                        # Mostrar progreso
                        if 'CREATE TABLE' in sentencia.upper():
                            tabla = sentencia.split('TABLE')[1].split('(')[0].strip().split()[0]
                            print(f"  [OK] Tabla creada: {tabla}")
                        elif 'CREATE OR REPLACE VIEW' in sentencia.upper():
                            vista = sentencia.split('VIEW')[1].split('AS')[0].strip()
                            print(f"  [OK] Vista creada: {vista}")
                        elif 'ALTER TABLE' in sentencia.upper():
                            tabla = sentencia.split('TABLE')[1].split('ADD')[0].strip()
                            print(f"  [OK] Tabla modificada: {tabla}")
        
        print("\n  [ÉXITO] Migración ejecutada correctamente!")
        return True
        
    except Exception as e:
        print(f"\n  [ERROR] Error durante la migración: {e}")
        print("  [INFO] Los cambios NO se aplicaron (rollback automático)")
        return False

def validar_resultados():
    """Valida que la migración se haya completado correctamente"""
    print_section("PASO 4: Validando Resultados")
    
    elementos_esperados = {
        'TABLAS': ['pagos_proveedores', 'aplicacion_pagos_ventas', 'aplicacion_pagos_compras'],
        'VISTAS': [
            'vista_movimientos_cta_cte_clientes',
            'vista_saldo_clientes',
            'vista_movimientos_cta_cte_proveedores',
            'vista_saldo_proveedores'
        ]
    }
    
    todo_ok = True
    
    with connection.cursor() as cursor:
        for tipo, elementos in elementos_esperados.items():
            print(f"\n  Verificando {tipo}:")
            for elemento in elementos:
                cursor.execute(f"SHOW TABLES LIKE '{elemento}'")
                if cursor.fetchone():
                    print(f"  [OK] {elemento}")
                else:
                    print(f"  [ERROR] No se creó: {elemento}")
                    todo_ok = False
        
        # Verificar campos agregados a ventas
        print(f"\n  Verificando campos en tabla 'ventas':")
        cursor.execute("DESCRIBE ventas")
        campos = [campo[0] for campo in cursor.fetchall()]
        
        if 'Saldo_Pendiente' in campos:
            print(f"  [OK] Campo Saldo_Pendiente agregado")
        else:
            print(f"  [ADVERTENCIA] Campo Saldo_Pendiente no encontrado")
        
        if 'Estado_Pago' in campos:
            print(f"  [OK] Campo Estado_Pago agregado")
        else:
            print(f"  [ADVERTENCIA] Campo Estado_Pago no encontrado")
        
        # Verificar campos agregados a compras
        print(f"\n  Verificando campos en tabla 'compras':")
        cursor.execute("DESCRIBE compras")
        campos = [campo[0] for campo in cursor.fetchall()]
        
        if 'Saldo_Pendiente' in campos:
            print(f"  [OK] Campo Saldo_Pendiente agregado")
        else:
            print(f"  [ADVERTENCIA] Campo Saldo_Pendiente no encontrado")
        
        if 'Estado_Pago' in campos:
            print(f"  [OK] Campo Estado_Pago agregado")
        else:
            print(f"  [ADVERTENCIA] Campo Estado_Pago no encontrado")
    
    return todo_ok

def mostrar_resumen():
    """Muestra resumen de la estructura nueva"""
    print_section("RESUMEN DE LA NUEVA ESTRUCTURA")
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                TABLE_NAME AS Elemento,
                TABLE_TYPE AS Tipo,
                COALESCE(TABLE_COMMENT, 'N/A') AS Descripcion
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = 'cantinatitadb'
            AND TABLE_NAME IN (
                'pagos_proveedores',
                'aplicacion_pagos_ventas', 
                'aplicacion_pagos_compras',
                'vista_movimientos_cta_cte_clientes',
                'vista_saldo_clientes',
                'vista_movimientos_cta_cte_proveedores',
                'vista_saldo_proveedores'
            )
            ORDER BY TABLE_TYPE DESC, TABLE_NAME
        """)
        
        resultados = cursor.fetchall()
        
        print(f"\n  {'Elemento':<45} {'Tipo':<15} {'Descripción'}")
        print("  " + "-" * 68)
        
        for elemento, tipo, desc in resultados:
            print(f"  {elemento:<45} {tipo:<15} {desc[:30]}")
    
    print("\n  [INFO] Las tablas antiguas 'cta_corriente' y 'cta_corriente_prov'")
    print("         se mantienen pero ahora son redundantes.")
    print("         Considera eliminarlas después de migrar todos los datos.")

def main():
    """Función principal"""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "MIGRACIÓN DE CUENTA CORRIENTE" + " " * 24 + "║")
    print("║" + " " * 18 + "Sistema Cantina Tita" + " " * 30 + "║")
    print("╚" + "═" * 68 + "╝")
    
    # Confirmar ejecución
    print("\nEsta migración realizará los siguientes cambios:")
    print("  1. Creará tabla 'pagos_proveedores'")
    print("  2. Creará tablas intermedias para aplicación de pagos")
    print("  3. Agregará campos Estado_Pago y Saldo_Pendiente")
    print("  4. Creará vistas para consulta de cuenta corriente")
    print("  5. Creará backups de tablas existentes")
    
    respuesta = input("\n¿Desea continuar? (SI/no): ").strip().upper()
    
    if respuesta not in ['SI', 'S', 'YES', 'Y', '']:
        print("\n[INFO] Migración cancelada por el usuario.")
        return
    
    try:
        # Paso 1: Verificar pre-requisitos
        if not verificar_prerequisitos():
            print("\n[ERROR] No se cumplen los pre-requisitos. Migración abortada.")
            return
        
        # Paso 2: Crear backups
        timestamp_backup = crear_backup()
        
        # Paso 3: Ejecutar migración
        if not ejecutar_migracion():
            print("\n[ERROR] La migración falló. Revise los mensajes anteriores.")
            print(f"[INFO] Los backups están disponibles con timestamp: {timestamp_backup}")
            return
        
        # Paso 4: Validar resultados
        if validar_resultados():
            print("\n[ÉXITO] Validación completada correctamente!")
        else:
            print("\n[ADVERTENCIA] Algunas validaciones fallaron. Revise los mensajes.")
        
        # Mostrar resumen
        mostrar_resumen()
        
        print_section("MIGRACIÓN COMPLETADA")
        print("\n  [ÉXITO] La migración se completó exitosamente!")
        print(f"  [INFO] Backups creados con timestamp: {timestamp_backup}")
        print("\n  Próximos pasos:")
        print("    1. Actualizar modelos Django (models.py)")
        print("    2. Migrar datos de pagos_venta a aplicacion_pagos_ventas")
        print("    3. Actualizar vistas Django para usar nuevas tablas/vistas")
        print("    4. Probar funcionalidad de cuenta corriente")
        
    except KeyboardInterrupt:
        print("\n\n[INFO] Migración interrumpida por el usuario.")
    except Exception as e:
        print(f"\n[ERROR] Error inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
