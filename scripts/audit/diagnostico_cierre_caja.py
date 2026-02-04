import MySQLdb

# Conectar a la base de datos
conn = MySQLdb.connect(
    host='localhost',
    user='root',
    password='L01G05S33Vice.42',
    database='cantinatitadb'
)

cursor = conn.cursor()

print("=" * 80)
print("DIAGNÓSTICO: CIERRE DE CAJA Y TRIGGER")
print("=" * 80)

# 1. Ver datos actuales del cierre
print("\n1. DATOS ACTUALES DEL CIERRE DE CAJA:")
print("-" * 80)
cursor.execute("""
    SELECT ID_Cierre, ID_Caja, 
           Fecha_Hora_Apertura, Fecha_Hora_Cierre,
           Monto_Inicial, Monto_Contado_Fisico, Diferencia_Efectivo
    FROM cierres_caja
    WHERE ID_Cierre = 1
""")
cierre = cursor.fetchone()

if cierre:
    print(f"ID Cierre: {cierre[0]}")
    print(f"ID Caja: {cierre[1]}")
    print(f"Apertura: {cierre[2]}")
    print(f"Cierre: {cierre[3]}")
    print(f"Monto Inicial: {cierre[4]}")
    print(f"Monto Contado: {cierre[5]}")
    print(f"Diferencia: {cierre[6]}")

# 2. Ver pagos asociados a este cierre
print("\n2. PAGOS ASOCIADOS AL CIERRE:")
print("-" * 80)
cursor.execute("""
    SELECT pv.ID_Pago, mp.Descripcion, pv.Monto_Aplicado, v.ID_Venta
    FROM pagos_venta pv
    JOIN medios_pago mp ON pv.ID_Medio_Pago = mp.ID_Medio_Pago
    JOIN ventas v ON pv.ID_Venta = v.ID_Venta
    WHERE pv.ID_Cierre = 1
""")
pagos = cursor.fetchall()

total_pagos = 0
if pagos:
    for pago in pagos:
        print(f"Pago ID: {pago[0]} | Medio: {pago[1]} | Monto: Gs. {pago[2]:,.2f} | Venta: {pago[3]}")
        total_pagos += float(pago[2])
    print(f"\nTotal pagos: Gs. {total_pagos:,.2f}")
else:
    print("No hay pagos registrados para este cierre")

# 3. Verificar el trigger
print("\n3. VERIFICAR TRIGGER:")
print("-" * 80)
cursor.execute("SHOW CREATE TRIGGER trg_calcular_diferencia_caja")
trigger = cursor.fetchone()

if trigger:
    print("✓ Trigger existe")
    print(f"\nCódigo del trigger:")
    print(trigger[2][:500] + "...")
else:
    print("✗ Trigger no existe")

# 4. Calcular manualmente lo que debería ser
print("\n4. CÁLCULO MANUAL:")
print("-" * 80)
if cierre and cierre[5] is not None:
    monto_esperado = float(cierre[4]) + total_pagos
    monto_contado = float(cierre[5])
    diferencia_calculada = monto_contado - monto_esperado
    
    print(f"Monto inicial: Gs. {cierre[4]:,.2f}")
    print(f"+ Pagos efectivo: Gs. {total_pagos:,.2f}")
    print(f"= Esperado: Gs. {monto_esperado:,.2f}")
    print(f"\nMonto contado: Gs. {monto_contado:,.2f}")
    print(f"Diferencia: Gs. {diferencia_calculada:,.2f}")
    
    # 5. Actualizar manualmente si el trigger no funcionó
    print("\n5. ACTUALIZACIÓN MANUAL:")
    print("-" * 80)
    try:
        cursor.execute("""
            UPDATE cierres_caja
            SET Diferencia_Efectivo = %s
            WHERE ID_Cierre = 1
        """, (diferencia_calculada,))
        conn.commit()
        print(f"✓ Diferencia actualizada manualmente a: Gs. {diferencia_calculada:,.2f}")
    except Exception as e:
        print(f"✗ Error al actualizar: {e}")
else:
    print("No se puede calcular porque Monto_Contado_Fisico está vacío")

cursor.close()
conn.close()

print("\n" + "=" * 80)
print("✅ DIAGNÓSTICO COMPLETADO")
print("=" * 80)
