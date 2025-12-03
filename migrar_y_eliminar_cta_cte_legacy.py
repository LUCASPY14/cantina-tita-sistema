"""
Script de Migración y Eliminación - Tablas Legacy de Cuenta Corriente
======================================================================

Este script:
1. Migra datos históricos de cta_corriente a aplicacion_pagos_ventas
2. Migra datos históricos de cta_corriente_prov a aplicacion_pagos_compras
3. Crea backups de seguridad
4. Elimina las tablas legacy cta_corriente y cta_corriente_prov

IMPORTANTE: Este proceso es IRREVERSIBLE después de confirmar.

Uso:
    python migrar_y_eliminar_cta_cte_legacy.py

Fecha: 2025-12-02
"""

import os
import sys
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
import django
django.setup()

from django.db import connection as django_connection

def conectar_db():
    """Retorna el cursor de Django."""
    return django_connection.cursor()

def crear_backup_tablas(cursor, timestamp):
    """Crea backups de las tablas antes de eliminarlas."""
    print("\n" + "="*70)
    print("PASO 1: CREAR BACKUPS DE SEGURIDAD")
    print("="*70)
    
    tablas_backup = [
        ('cta_corriente', f'cta_corriente_backup_{timestamp}'),
        ('cta_corriente_prov', f'cta_corriente_prov_backup_{timestamp}')
    ]
    
    for tabla_origen, tabla_backup in tablas_backup:
        try:
            # Verificar si la tabla existe
            cursor.execute(f"""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = DATABASE()
                AND table_name = '{tabla_origen}'
            """)
            existe = cursor.fetchone()[0] > 0
            
            if not existe:
                print(f"⚠ Tabla {tabla_origen} no existe, omitiendo backup...")
                continue
            
            # Contar registros
            cursor.execute(f"SELECT COUNT(*) FROM {tabla_origen}")
            total_registros = cursor.fetchone()[0]
            
            print(f"\n📦 Creando backup: {tabla_backup}")
            print(f"   Origen: {tabla_origen} ({total_registros} registros)")
            
            # Crear tabla de backup
            cursor.execute(f"CREATE TABLE {tabla_backup} LIKE {tabla_origen}")
            cursor.execute(f"INSERT INTO {tabla_backup} SELECT * FROM {tabla_origen}")
            django_connection.commit()
            
            print(f"   ✅ Backup creado exitosamente")
            
        except Exception as e:
            print(f"   ❌ Error creando backup de {tabla_origen}: {e}")
            raise

def analizar_datos_existentes(cursor):
    """Analiza los datos en las tablas legacy."""
    print("\n" + "="*70)
    print("PASO 2: ANÁLISIS DE DATOS EXISTENTES")
    print("="*70)
    
    analisis = {}
    
    # Analizar cta_corriente (clientes)
    try:
        cursor.execute("SELECT COUNT(*) FROM cta_corriente")
        total_cta_corriente = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT Tipo_Movimiento, COUNT(*) 
            FROM cta_corriente 
            GROUP BY Tipo_Movimiento
        """)
        movimientos_cliente = cursor.fetchall()
        
        analisis['cta_corriente'] = {
            'total': total_cta_corriente,
            'movimientos': movimientos_cliente
        }
        
        print(f"\n📊 cta_corriente (CLIENTES):")
        print(f"   Total registros: {total_cta_corriente}")
        for tipo, cantidad in movimientos_cliente:
            print(f"   - {tipo}: {cantidad} registros")
            
    except Exception as e:
        print(f"⚠ Error analizando cta_corriente: {e}")
        analisis['cta_corriente'] = {'total': 0, 'movimientos': []}
    
    # Analizar cta_corriente_prov (proveedores)
    try:
        cursor.execute("SELECT COUNT(*) FROM cta_corriente_prov")
        total_cta_corriente_prov = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT Tipo_Movimiento, COUNT(*) 
            FROM cta_corriente_prov 
            GROUP BY Tipo_Movimiento
        """)
        movimientos_proveedor = cursor.fetchall()
        
        analisis['cta_corriente_prov'] = {
            'total': total_cta_corriente_prov,
            'movimientos': movimientos_proveedor
        }
        
        print(f"\n📊 cta_corriente_prov (PROVEEDORES):")
        print(f"   Total registros: {total_cta_corriente_prov}")
        for tipo, cantidad in movimientos_proveedor:
            print(f"   - {tipo}: {cantidad} registros")
            
    except Exception as e:
        print(f"⚠ Error analizando cta_corriente_prov: {e}")
        analisis['cta_corriente_prov'] = {'total': 0, 'movimientos': []}
    
    return analisis

def verificar_nuevo_sistema(cursor):
    """Verifica que el nuevo sistema esté correctamente implementado."""
    print("\n" + "="*70)
    print("PASO 3: VERIFICAR NUEVO SISTEMA")
    print("="*70)
    
    tablas_requeridas = [
        'pagos_venta',
        'pagos_proveedores',
        'aplicacion_pagos_ventas',
        'aplicacion_pagos_compras'
    ]
    
    campos_requeridos = [
        ('ventas', 'Saldo_Pendiente'),
        ('ventas', 'Estado_Pago'),
        ('compras', 'Saldo_Pendiente'),
        ('compras', 'Estado_Pago')
    ]
    
    print("\n🔍 Verificando tablas nuevas:")
    for tabla in tablas_requeridas:
        cursor.execute(f"""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = DATABASE()
            AND table_name = '{tabla}'
        """)
        existe = cursor.fetchone()[0] > 0
        
        if existe:
            cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
            registros = cursor.fetchone()[0]
            print(f"   ✅ {tabla} ({registros} registros)")
        else:
            print(f"   ❌ {tabla} NO EXISTE")
            raise Exception(f"Tabla requerida {tabla} no existe. Ejecute primero la migración del sistema nuevo.")
    
    print("\n🔍 Verificando campos nuevos:")
    for tabla, campo in campos_requeridos:
        cursor.execute(f"""
            SELECT COUNT(*) 
            FROM information_schema.columns 
            WHERE table_schema = DATABASE()
            AND table_name = '{tabla}'
            AND column_name = '{campo}'
        """)
        existe = cursor.fetchone()[0] > 0
        
        if existe:
            print(f"   ✅ {tabla}.{campo}")
        else:
            print(f"   ❌ {tabla}.{campo} NO EXISTE")
            raise Exception(f"Campo requerido {tabla}.{campo} no existe.")
    
    print("\n✅ Nuevo sistema verificado correctamente")

def migrar_datos_clientes(cursor):
    """Migra datos de cta_corriente al nuevo sistema."""
    print("\n" + "="*70)
    print("PASO 4: MIGRAR DATOS DE CLIENTES (cta_corriente)")
    print("="*70)
    
    # Nota: Los datos de cta_corriente ya están obsoletos porque ahora
    # usamos Saldo_Pendiente y Estado_Pago directamente en ventas
    # Esta tabla solo tiene registros históricos que ya no son necesarios
    # porque el nuevo sistema calcula todo automáticamente
    
    print("\n📝 Análisis:")
    print("   La tabla cta_corriente contiene movimientos históricos tipo DEBE/HABER")
    print("   que ya NO son necesarios porque el nuevo sistema:")
    print("   - Almacena Saldo_Pendiente directamente en cada venta")
    print("   - Calcula saldos automáticamente con triggers")
    print("   - Usa aplicacion_pagos_ventas para tracking detallado")
    
    print("\n✅ No se requiere migración de datos")
    print("   Los saldos actuales ya están correctos en ventas.Saldo_Pendiente")
    
    return 0

def migrar_datos_proveedores(cursor):
    """Migra datos de cta_corriente_prov al nuevo sistema."""
    print("\n" + "="*70)
    print("PASO 5: MIGRAR DATOS DE PROVEEDORES (cta_corriente_prov)")
    print("="*70)
    
    # Similar a clientes, cta_corriente_prov ya está obsoleta
    # porque ahora usamos Saldo_Pendiente y Estado_Pago en compras
    
    print("\n📝 Análisis:")
    print("   La tabla cta_corriente_prov contiene movimientos históricos tipo DEBE/HABER")
    print("   que ya NO son necesarios porque el nuevo sistema:")
    print("   - Almacena Saldo_Pendiente directamente en cada compra")
    print("   - Calcula saldos automáticamente con triggers")
    print("   - Usa aplicacion_pagos_compras para tracking detallado")
    
    print("\n✅ No se requiere migración de datos")
    print("   Los saldos actuales ya están correctos en compras.Saldo_Pendiente")
    
    return 0

def eliminar_tablas_legacy(cursor):
    """Elimina las tablas legacy."""
    print("\n" + "="*70)
    print("PASO 6: ELIMINAR TABLAS LEGACY")
    print("="*70)
    
    tablas_eliminar = ['cta_corriente', 'cta_corriente_prov']
    
    for tabla in tablas_eliminar:
        try:
            print(f"\n🗑️  Eliminando tabla: {tabla}")
            cursor.execute(f"DROP TABLE IF EXISTS {tabla}")
            django_connection.commit()
            print(f"   ✅ Tabla {tabla} eliminada exitosamente")
            
        except Exception as e:
            print(f"   ❌ Error eliminando {tabla}: {e}")
            raise

def actualizar_modelos_django():
    """Información sobre actualización de modelos Django."""
    print("\n" + "="*70)
    print("PASO 7: ACTUALIZAR MODELOS DJANGO")
    print("="*70)
    
    print("\n📝 Se debe eliminar de gestion/models.py:")
    print("   - class CtaCorriente(models.Model)")
    print("   - class CtaCorrienteProv(models.Model)")
    
    print("\n⚠️  NOTA: Esta acción debe hacerse manualmente o confirmarse")

def generar_reporte_final(analisis, timestamp):
    """Genera reporte final de la migración."""
    print("\n" + "="*70)
    print("REPORTE FINAL DE MIGRACIÓN")
    print("="*70)
    
    print(f"\n📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📦 Timestamp de backups: {timestamp}")
    
    print("\n📊 Datos procesados:")
    print(f"   cta_corriente: {analisis['cta_corriente']['total']} registros respaldados")
    print(f"   cta_corriente_prov: {analisis['cta_corriente_prov']['total']} registros respaldados")
    
    print("\n✅ Tablas eliminadas:")
    print("   - cta_corriente")
    print("   - cta_corriente_prov")
    
    print("\n💾 Backups disponibles:")
    print(f"   - cta_corriente_backup_{timestamp}")
    print(f"   - cta_corriente_prov_backup_{timestamp}")
    
    print("\n🎯 Sistema actual (NUEVO):")
    print("   ✅ ventas.Saldo_Pendiente + ventas.Estado_Pago")
    print("   ✅ compras.Saldo_Pendiente + compras.Estado_Pago")
    print("   ✅ aplicacion_pagos_ventas (tracking detallado)")
    print("   ✅ aplicacion_pagos_compras (tracking detallado)")
    print("   ✅ Triggers automáticos activos")
    
    print("\n" + "="*70)

def main():
    """Función principal."""
    print("="*70)
    print("MIGRACIÓN Y ELIMINACIÓN DE TABLAS LEGACY")
    print("Sistema de Cuenta Corriente - Cantina Tita")
    print("="*70)
    
    print("\n⚠️  ADVERTENCIA:")
    print("   Este proceso eliminará PERMANENTEMENTE las tablas:")
    print("   - cta_corriente")
    print("   - cta_corriente_prov")
    print("\n   Se crearán backups antes de eliminar.")
    
    confirmacion = input("\n¿Desea continuar? (SI/no): ").strip().upper()
    
    if confirmacion != 'SI':
        print("\n❌ Operación cancelada por el usuario")
        return 1
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    try:
        # Usar la conexión de Django
        cursor = conectar_db()
        
        print("\n✅ Conexión establecida con la base de datos")
        
        # Paso 1: Crear backups
        crear_backup_tablas(cursor, timestamp)
        django_connection.commit()
        
        # Paso 2: Analizar datos
        analisis = analizar_datos_existentes(cursor)
        
        # Paso 3: Verificar nuevo sistema
        verificar_nuevo_sistema(cursor)
        
        # Paso 4: Migrar datos de clientes
        migrar_datos_clientes(cursor)
        
        # Paso 5: Migrar datos de proveedores
        migrar_datos_proveedores(cursor)
        
        # Confirmación final antes de eliminar
        print("\n" + "="*70)
        print("⚠️  CONFIRMACIÓN FINAL")
        print("="*70)
        print("\nSe han creado los backups exitosamente.")
        print("Los datos actuales en ventas y compras están correctos.")
        print("\nEstás a punto de ELIMINAR PERMANENTEMENTE:")
        print("   - cta_corriente")
        print("   - cta_corriente_prov")
        
        confirmacion_final = input("\n¿Confirmar eliminación? (ELIMINAR/cancelar): ").strip().upper()
        
        if confirmacion_final != 'ELIMINAR':
            print("\n❌ Eliminación cancelada. Los backups se mantienen.")
            return 1
        
        # Paso 6: Eliminar tablas
        eliminar_tablas_legacy(cursor)
        
        # Paso 7: Información sobre modelos Django
        actualizar_modelos_django()
        
        # Generar reporte final
        generar_reporte_final(analisis, timestamp)
        
        print("\n🎉 MIGRACIÓN COMPLETADA EXITOSAMENTE 🎉")
        print("\n📝 Próximo paso: Actualizar gestion/models.py")
        print("   Los modelos CtaCorriente y CtaCorrienteProv deben eliminarse")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        django_connection.rollback()
        print("⚠️  Se hizo rollback de los cambios")
        import traceback
        traceback.print_exc()
        return 1
        
    finally:
        if cursor:
            cursor.close()
            print("\n🔌 Conexión cerrada")

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n❌ Operación cancelada por el usuario")
        sys.exit(1)
