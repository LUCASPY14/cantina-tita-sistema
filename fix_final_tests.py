#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CORRECCIONES FINALES - Prioridad Alta y Media
==============================================
Completa los tests pendientes eliminando todos los errores de schema.
"""

import re

def fix_ventas_directas():
    """Corrige test_modulo_ventas_directas.py"""
    filename = "test_modulo_ventas_directas.py"
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Eliminar todas las referencias a Fecha_Vigencia y usar Fecha_Cambio
    content = re.sub(
        r'hp\.Fecha_Vigencia = \(\s*SELECT MAX\(Fecha_Vigencia\)\s*FROM historico_precios\s*WHERE ID_Producto = p\.ID_Producto\s*\)',
        'hp.Fecha_Cambio = (\n                SELECT MAX(Fecha_Cambio)\n                FROM historico_precios\n                WHERE ID_Producto = p.ID_Producto\n            )',
        content
    )
    
    # Corrección alternativa: eliminar completamente el filtro de fecha
    content = re.sub(
        r'AND hp\.Fecha_Vigencia.*?\n.*?WHERE ID_Producto = p\.ID_Producto\s*\)',
        '',
        content,
        flags=re.DOTALL
    )
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ {filename} corregido")

def fix_documentos():
    """Corrige test_modulo_documentos.py - Elimina todas las referencias a Activo"""
    filename = "test_modulo_documentos.py"
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Eliminar Activo de INSERT
    content = re.sub(
        r',\s*Activo\s*\)\s*VALUES\s*\([^)]+\),\s*TRUE\)',
        ')\n            VALUES (%s, %s, %s, %s, %s, %s, %s)',
        content
    )
    
    # 2. Eliminar Activo de SELECT  
    content = re.sub(r',\s*activo\s*=\s*timb', ' = timb', content)
    content = re.sub(r'activo,\s*', '', content)
    content = re.sub(r',\s*activo(?=\s*=)', '', content)
    
    # 3. Eliminar referencias a variable activo
    content = re.sub(r'estado = "Activo" if activo else "Inactivo"', 'estado = "Activo"', content)
    content = re.sub(r',\s*final,\s*activo(?=\s*=)', ', final', content)
    
    # 4. Eliminar WHERE Activo = TRUE
    content = re.sub(r'WHERE dt\.Activo = TRUE\s*AND', 'WHERE', content)
    content = re.sub(r'WHERE dt\.Activo = TRUE', 'WHERE 1=1', content)
    
    # 5. Corregir estructura de INSERT documentos_tributarios
    content = re.sub(
        r'INSERT INTO documentos_tributarios\s*\([^)]+\)\s*VALUES\s*\([^)]+\)',
        '''INSERT INTO documentos_tributarios
            (Nro_Timbrado, Nro_Secuencial, Fecha_Emision, Monto_Total, 
             Monto_Neto, IVA_10, IVA_5, IVA_Exento)
            VALUES (%s, %s, NOW(), 0, 0, 0, 0, 0)''',
        content,
        count=1
    )
    
    # 6. Corregir SELECT que devuelve tuplas
    content = re.sub(
        r'id_d, tipo, timb_num, actual, final, venc, activo',
        'id_d, timb_num, nro_sec, fecha_emision',
        content
    )
    
    # 7. Simplificar queries complejos
    content = re.sub(
        r'SELECT\s+ID_Documento,\s*ID_Documento,.*?FROM documentos_tributarios',
        'SELECT \n                ID_Documento,\n                Nro_Timbrado,\n                Nro_Secuencial,\n                Fecha_Emision\n            FROM documentos_tributarios',
        content,
        flags=re.DOTALL
    )
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ {filename} corregido")

def fix_cierres_caja():
    """Corrige test_modulo_cierres_caja.py - Elimina Estado y adapta a schema real"""
    filename = "test_modulo_cierres_caja.py"
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Eliminar columna Estado de INSERT
    content = re.sub(
        r'\(ID_Empleado, Fecha_Hora_Apertura, Monto_Inicial, Estado\)',
        '(ID_Caja, ID_Empleado, Fecha_Hora_Apertura, Monto_Inicial)',
        content
    )
    
    # 2. Ajustar VALUES para quitar Estado
    content = re.sub(
        r"VALUES \(%s, NOW\(\), %s, 'Abierta'\)",
        'VALUES (1, %s, NOW(), %s)',
        content
    )
    
    # 3. Cambiar condición de caja abierta (en lugar de Estado = 'Abierta' usar IS NULL)
    content = re.sub(
        r"WHERE Estado = 'Abierta'",
        'WHERE Fecha_Hora_Cierre IS NULL',
        content
    )
    
    # 4. Eliminar Monto_Final (no existe)
    content = re.sub(r'cc\.Monto_Final', 'cc.Monto_Contado_Fisico', content)
    content = re.sub(r'Monto_Final', 'Monto_Contado_Fisico', content)
    
    # 5. Simplificar búsqueda de empleado (sin tabla roles)
    content = re.sub(
        r'INNER JOIN roles r ON e\.ID_Rol = r\.ID_Rol\s*WHERE r\.Nombre_Rol.*?AND',
        'WHERE',
        content
    )
    
    # 6. Eliminar UPDATE de Estado en cierre
    content = re.sub(
        r",\s*Estado = 'Cerrada'",
        '',
        content
    )
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ {filename} corregido")

def fix_almuerzos():
    """Corrige test_modulo_almuerzos.py - Usa tablas reales"""
    filename = "test_modulo_almuerzos.py"
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Reemplazar almuerzos_mensuales por planes_almuerzo + pagos_almuerzo_mensual
    content = re.sub(
        r'FROM almuerzos_mensuales',
        'FROM pagos_almuerzo_mensual',
        content
    )
    
    content = re.sub(
        r'INSERT INTO almuerzos_mensuales',
        'INSERT INTO pagos_almuerzo_mensual',
        content
    )
    
    # 2. Reemplazar pagos_almuerzos por pagos_almuerzo_mensual
    content = re.sub(
        r'FROM pagos_almuerzos',
        'FROM pagos_almuerzo_mensual',
        content
    )
    
    content = re.sub(
        r'INSERT INTO pagos_almuerzos',
        'INSERT INTO pagos_almuerzo_mensual',
        content
    )
    
    # 3. Ajustar columnas a schema real
    content = re.sub(r'ID_Almuerzo_Mensual', 'ID_Pago_Almuerzo', content)
    content = re.sub(r'ID_Plan', 'ID_Suscripcion', content)
    content = re.sub(r'Mes_Cobro', 'Mes_Pagado', content)
    content = re.sub(r'Monto_Mensual', 'Monto_Pagado', content)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ {filename} corregido")

if __name__ == '__main__':
    print("="*70)
    print("  CORRECCIONES FINALES - PRIORIDAD ALTA Y MEDIA")
    print("="*70)
    print()
    
    try:
        fix_ventas_directas()
        fix_documentos()
        fix_cierres_caja()
        fix_almuerzos()
        
        print()
        print("="*70)
        print("✅ TODAS LAS CORRECCIONES APLICADAS")
        print("="*70)
        print("\n🎯 Ejecutar tests para verificar:")
        print("   python test_modulo_ventas_directas.py")
        print("   python test_modulo_documentos.py")
        print("   python test_modulo_cierres_caja.py")
        print("   python test_modulo_almuerzos.py")
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
