import MySQLdb

conn = MySQLdb.connect(
    host='localhost',
    user='root',
    password='L01G05S33Vice.42',
    database='cantinatitadb'
)

cursor = conn.cursor()

print("=" * 70)
print("ACTUALIZANDO DIFERENCIA DE CIERRE DE CAJA")
print("=" * 70)

# Paso 1: Ver cierre actual
cursor.execute("SELECT Monto_Inicial, Monto_Contado_Fisico FROM cierres_caja WHERE ID_Cierre = 1")
cierre = cursor.fetchone()

# Paso 2: Ver pagos en efectivo
cursor.execute("""
    SELECT SUM(pv.Monto_Aplicado)
    FROM pagos_venta pv
    JOIN medios_pago mp ON pv.ID_Medio_Pago = mp.ID_Medio_Pago
    WHERE pv.ID_Cierre = 1 AND mp.Descripcion = 'EFECTIVO'
""")
pagos = cursor.fetchone()

if cierre and cierre[1]:
    inicial = float(cierre[0])
    contado = float(cierre[1])
    total_pagos = float(pagos[0]) if pagos and pagos[0] else 0.0
    
    esperado = inicial + total_pagos
    diferencia = contado - esperado
    
    print(f"\nMonto inicial:      Gs. {inicial:,.2f}")
    print(f"Pagos en efectivo:  Gs. {total_pagos:,.2f}")
    print(f"Total esperado:     Gs. {esperado:,.2f}")
    print(f"Monto contado:      Gs. {contado:,.2f}")
    print(f"─" * 70)
    print(f"DIFERENCIA:         Gs. {diferencia:,.2f}")
    
    cursor.execute("UPDATE cierres_caja SET Diferencia_Efectivo = %s WHERE ID_Cierre = 1", (diferencia,))
    conn.commit()
    
    print(f"\n✅ DIFERENCIA ACTUALIZADA: Gs. {diferencia:,.2f}")
else:
    print("\n❌ ERROR: Cierre no encontrado o monto contado vacío")

cursor.close()
conn.close()

print("=" * 70)
