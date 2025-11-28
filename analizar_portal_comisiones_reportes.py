import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()

print("\n" + "="*80)
print("ANÁLISIS DETALLADO: Portal Web, Comisiones y Reportes")
print("="*80)

# ============================================================================
# 1. PORTAL WEB PARA CLIENTES
# ============================================================================
print("\n" + "="*80)
print("1️⃣  PORTAL WEB PARA CLIENTES")
print("="*80)

print("\n📋 Tabla: usuarios_web_clientes")
cursor.execute("SHOW COLUMNS FROM usuarios_web_clientes")
columns = cursor.fetchall()
for col in columns:
    print(f"  - {col[0]:25s} {col[1]:20s} {'NULL' if col[2]=='YES' else 'NOT NULL':10s}")

cursor.execute("SELECT COUNT(*) FROM usuarios_web_clientes")
count = cursor.fetchone()[0]
print(f"\n  📊 Registros actuales: {count}")

if count > 0:
    cursor.execute("SELECT * FROM usuarios_web_clientes LIMIT 5")
    rows = cursor.fetchall()
    print("\n  📄 Datos existentes:")
    for row in rows:
        print(f"    - ID_Cliente: {row[0]}, Usuario: {row[1]}, Último acceso: {row[3]}")

# Ver trigger relacionado
print("\n  🔔 Triggers:")
cursor.execute("SHOW TRIGGERS WHERE `Table` = 'usuarios_web_clientes'")
triggers = cursor.fetchall()
for trigger in triggers:
    print(f"    - {trigger[0]} ({trigger[1]}) - {trigger[4]}")

# Ver tabla de auditoría
print("\n📋 Tabla: auditoria_usuarios_web")
cursor.execute("SHOW COLUMNS FROM auditoria_usuarios_web")
columns = cursor.fetchall()
for col in columns:
    print(f"  - {col[0]:25s} {col[1]:20s} {'NULL' if col[2]=='YES' else 'NOT NULL':10s}")

cursor.execute("SELECT COUNT(*) FROM auditoria_usuarios_web")
count = cursor.fetchone()[0]
print(f"\n  📊 Registros actuales: {count}")

# Verificar clientes existentes que podrían tener portal
print("\n  👥 Clientes disponibles para crear usuarios web:")
cursor.execute("""
    SELECT 
        c.ID_Cliente,
        c.Nombres,
        c.Apellidos,
        c.Email,
        c.Telefono,
        COUNT(h.ID_Hijo) as Total_Hijos,
        CASE 
            WHEN uw.ID_Cliente IS NOT NULL THEN 'SÍ'
            ELSE 'NO'
        END as Tiene_Usuario_Web
    FROM Clientes c
    LEFT JOIN Hijos h ON c.ID_Cliente = h.ID_Cliente_Responsable
    LEFT JOIN Usuarios_Web_Clientes uw ON c.ID_Cliente = uw.ID_Cliente
    GROUP BY c.ID_Cliente
    LIMIT 10
""")
clients = cursor.fetchall()
for client in clients:
    print(f"    - ID {client[0]}: {client[1]} {client[2]} | Email: {client[3] or 'N/A'} | Hijos: {client[5]} | Portal: {client[6]}")

# ============================================================================
# 2. SISTEMA DE COMISIONES BANCARIAS
# ============================================================================
print("\n" + "="*80)
print("2️⃣  SISTEMA DE COMISIONES BANCARIAS")
print("="*80)

# Medios de pago
print("\n📋 Tabla: medios_pago")
cursor.execute("""
    SELECT 
        ID_Medio_Pago,
        Descripcion,
        Genera_Comision,
        Requiere_Validacion,
        Activo
    FROM Medios_Pago
""")
medios = cursor.fetchall()
print(f"\n  📊 Total medios de pago: {len(medios)}")
for medio in medios:
    comision = '💳 Genera comisión' if medio[2] else '✓ Sin comisión'
    validacion = '🔒 Requiere validación' if medio[3] else ''
    activo = '✅' if medio[4] else '❌'
    print(f"    {activo} ID {medio[0]}: {medio[1]:30s} | {comision} {validacion}")

# Tarifas de comisión
print("\n📋 Tabla: tarifas_comision")
cursor.execute("SHOW COLUMNS FROM tarifas_comision")
columns = cursor.fetchall()
for col in columns:
    print(f"  - {col[0]:30s} {col[1]:20s} {'NULL' if col[2]=='YES' else 'NOT NULL':10s}")

cursor.execute("SELECT COUNT(*) FROM tarifas_comision")
count = cursor.fetchone()[0]
print(f"\n  📊 Registros actuales: {count}")

if count > 0:
    cursor.execute("""
        SELECT 
            t.ID_Tarifa,
            m.Descripcion as Medio_Pago,
            t.Porcentaje_Comision,
            t.Monto_Fijo_Comision,
            t.Fecha_Inicio_Vigencia,
            t.Fecha_Fin_Vigencia,
            t.Activo
        FROM Tarifas_Comision t
        JOIN Medios_Pago m ON t.ID_Medio_Pago = m.ID_Medio_Pago
    """)
    tarifas = cursor.fetchall()
    print("\n  📄 Tarifas configuradas:")
    for tarifa in tarifas:
        print(f"    - {tarifa[1]}: {tarifa[2]}% + ${tarifa[3] or 0} | Vigencia: {tarifa[4]} a {tarifa[5] or 'Actual'}")

# Detalle de comisiones por venta
print("\n📋 Tabla: detalle_comision_venta")
cursor.execute("SHOW COLUMNS FROM detalle_comision_venta")
columns = cursor.fetchall()
for col in columns:
    print(f"  - {col[0]:30s} {col[1]:20s} {'NULL' if col[2]=='YES' else 'NOT NULL':10s}")

cursor.execute("SELECT COUNT(*) FROM detalle_comision_venta")
count = cursor.fetchone()[0]
print(f"\n  📊 Registros actuales: {count}")

# Conciliación de pagos
print("\n📋 Tabla: conciliacion_pagos")
cursor.execute("SHOW COLUMNS FROM conciliacion_pagos")
columns = cursor.fetchall()
for col in columns:
    print(f"  - {col[0]:30s} {col[1]:20s} {'NULL' if col[2]=='YES' else 'NOT NULL':10s}")

cursor.execute("SELECT COUNT(*) FROM conciliacion_pagos")
count = cursor.fetchone()[0]
print(f"\n  📊 Registros actuales: {count}")

# Auditoría de comisiones
print("\n📋 Tabla: auditoria_comisiones")
cursor.execute("SELECT COUNT(*) FROM auditoria_comisiones")
count = cursor.fetchone()[0]
print(f"  📊 Registros de auditoría: {count}")

# Ver triggers relacionados
print("\n  🔔 Triggers de comisiones:")
cursor.execute("SHOW TRIGGERS WHERE `Table` LIKE '%comision%' OR `Table` = 'pagos_venta'")
triggers = cursor.fetchall()
for trigger in triggers:
    print(f"    - {trigger[0]} en {trigger[2]} ({trigger[1]}/{trigger[4]})")

# Ver pagos de venta existentes para analizar
print("\n  💰 Análisis de pagos existentes:")
cursor.execute("""
    SELECT 
        pv.ID_Pago_Venta,
        v.ID_Venta,
        v.Fecha,
        mp.Descripcion as Medio_Pago,
        pv.Monto_Aplicado,
        pv.Referencia_Transaccion
    FROM Pagos_Venta pv
    JOIN Ventas v ON pv.ID_Venta = v.ID_Venta
    JOIN Medios_Pago mp ON pv.ID_Medio_Pago = mp.ID_Medio_Pago
    LIMIT 10
""")
pagos = cursor.fetchall()
print(f"    Total pagos registrados: {len(pagos)}")
for pago in pagos:
    print(f"    - Venta {pago[1]} | {pago[2]} | {pago[3]} | ${pago[4]:,} | Ref: {pago[5] or 'N/A'}")

# ============================================================================
# 3. REPORTES AVANZADOS (VISTAS)
# ============================================================================
print("\n" + "="*80)
print("3️⃣  REPORTES AVANZADOS (VISTAS)")
print("="*80)

# Listar todas las vistas
cursor.execute("SHOW FULL TABLES WHERE Table_Type = 'VIEW'")
views = cursor.fetchall()
print(f"\n📊 Total de vistas: {len(views)}")

# Analizar cada vista
vistas_info = []
for view in views:
    view_name = view[0]
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {view_name}")
        count = cursor.fetchone()[0]
        status = "✅ OK"
        
        # Obtener columnas
        cursor.execute(f"SHOW COLUMNS FROM {view_name}")
        columns = cursor.fetchall()
        col_count = len(columns)
        
        vistas_info.append({
            'name': view_name,
            'count': count,
            'columns': col_count,
            'status': status
        })
    except Exception as e:
        vistas_info.append({
            'name': view_name,
            'count': 0,
            'columns': 0,
            'status': f"❌ ERROR: {str(e)[:50]}"
        })

# Mostrar resumen
print("\n📋 Estado de vistas:")
for vista in sorted(vistas_info, key=lambda x: x['name']):
    print(f"  {vista['status']:60s} {vista['name']:40s} | {vista['count']:4d} registros | {vista['columns']:2d} columnas")

# Analizar vistas específicas para reportes
print("\n" + "="*80)
print("VISTAS DE REPORTES - DETALLE")
print("="*80)

# Vista de ventas del día
print("\n📊 v_ventas_dia_detallado")
try:
    cursor.execute("SELECT * FROM v_ventas_dia_detallado LIMIT 1")
    row = cursor.fetchone()
    if row:
        cursor.execute("SHOW COLUMNS FROM v_ventas_dia_detallado")
        columns = cursor.fetchall()
        print("  Columnas disponibles:")
        for col in columns:
            print(f"    - {col[0]}")
except Exception as e:
    print(f"  ❌ Error: {e}")

# Vista de productos más vendidos
print("\n📊 v_productos_mas_vendidos")
try:
    cursor.execute("SELECT * FROM v_productos_mas_vendidos")
    productos = cursor.fetchall()
    print(f"  Total productos: {len(productos)}")
    for prod in productos[:5]:
        print(f"    - {prod[2]}: {prod[3]} unidades | ${prod[4]:,} ingresos | {prod[5]} ventas")
except Exception as e:
    print(f"  ❌ Error: {e}")

# Vista de resumen de caja
print("\n📊 v_resumen_caja_diario")
try:
    cursor.execute("SELECT * FROM v_resumen_caja_diario")
    cajas = cursor.fetchall()
    print(f"  Total días registrados: {len(cajas)}")
    for caja in cajas:
        print(f"    - Fecha: {caja[0]} | Ventas: {caja[1]} (${caja[2]:,}) | Recargas: {caja[3]} (${caja[4]:,}) | Total: ${caja[5]:,}")
except Exception as e:
    print(f"  ❌ Error: {e}")

# Vista de stock con alertas
print("\n📊 v_stock_critico_alertas")
try:
    cursor.execute("SELECT * FROM v_stock_critico_alertas LIMIT 10")
    stock = cursor.fetchall()
    cursor.execute("SHOW COLUMNS FROM v_stock_critico_alertas")
    columns = cursor.fetchall()
    print(f"  Total productos con alertas: {len(stock)}")
    print("  Columnas:")
    for col in columns:
        print(f"    - {col[0]}")
except Exception as e:
    print(f"  ❌ Error: {e}")

# Vista de consumos de estudiantes
print("\n📊 v_consumos_estudiante")
try:
    cursor.execute("SELECT * FROM v_consumos_estudiante LIMIT 5")
    consumos = cursor.fetchall()
    cursor.execute("SHOW COLUMNS FROM v_consumos_estudiante")
    columns = cursor.fetchall()
    print(f"  Total registros: {len(consumos)}")
    print("  Columnas:")
    for col in columns:
        print(f"    - {col[0]}")
except Exception as e:
    print(f"  ❌ Error: {e}")

# Vista de saldo de clientes
print("\n📊 v_saldo_clientes")
try:
    cursor.execute("SELECT * FROM v_saldo_clientes")
    saldos = cursor.fetchall()
    print(f"  Total clientes: {len(saldos)}")
    for saldo in saldos[:5]:
        print(f"    - {saldo[3]}: Saldo ${saldo[6]:,} | RUC: {saldo[4]} | Movimientos: {saldo[8]}")
except Exception as e:
    print(f"  ❌ Error: {e}")

# ============================================================================
# RESUMEN FINAL
# ============================================================================
print("\n" + "="*80)
print("RESUMEN Y RECOMENDACIONES")
print("="*80)

print("\n🎯 PORTAL WEB CLIENTES:")
cursor.execute("SELECT COUNT(*) FROM Clientes WHERE Email IS NOT NULL AND Email != ''")
clientes_con_email = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM usuarios_web_clientes")
usuarios_web = cursor.fetchone()[0]
print(f"  - Clientes con email: {clientes_con_email}")
print(f"  - Usuarios web creados: {usuarios_web}")
print(f"  - Potencial: {clientes_con_email - usuarios_web} clientes pueden registrarse")

print("\n💳 COMISIONES BANCARIAS:")
cursor.execute("SELECT COUNT(*) FROM medios_pago WHERE Activo = 1")
medios_activos = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM tarifas_comision WHERE Activo = 1")
tarifas_activas = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM pagos_venta")
pagos_totales = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM detalle_comision_venta")
comisiones_calc = cursor.fetchone()[0]
print(f"  - Medios de pago activos: {medios_activos}")
print(f"  - Tarifas configuradas: {tarifas_activas}")
print(f"  - Pagos registrados: {pagos_totales}")
print(f"  - Comisiones calculadas: {comisiones_calc}")
print(f"  - Pendiente calcular: {pagos_totales - comisiones_calc} pagos")

print("\n📊 REPORTES:")
vistas_ok = sum(1 for v in vistas_info if '✅' in v['status'])
vistas_error = sum(1 for v in vistas_info if '❌' in v['status'])
print(f"  - Vistas funcionales: {vistas_ok}/{len(vistas_info)}")
print(f"  - Vistas con error: {vistas_error}")
print(f"  - Datos disponibles: Ventas, Stock, Consumos, Saldos, Caja")

print("\n" + "="*80)
