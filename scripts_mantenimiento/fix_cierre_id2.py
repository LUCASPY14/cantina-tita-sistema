import MySQLdb

conn = MySQLdb.connect(
    host='localhost',
    user='root',
    password='L01G05S33Vice.42',
    database='cantinatitadb'
)

cursor = conn.cursor()

print("=" * 70)
print("ACTUALIZANDO DIFERENCIA DE CIERRE DE CAJA ID=2")
print("=" * 70)

# Datos del cierre
cursor.execute("SELECT Monto_Inicial, Monto_Contado_Fisico FROM cierres_caja WHERE ID_Cierre = 2")
cierre = cursor.fetchone()

# Pagos en efectivo
cursor.execute("""
    SELECT SUM(pv.Monto_Aplicado)
    FROM pagos_venta pv
    JOIN medios_pago mp ON pv.ID_Medio_Pago = mp.ID_Medio_Pago
    WHERE pv.ID_Cierre = 2 AND mp.Descripcion = 'EFECTIVO'
""")
pagos = cursor.fetchone()

if cierre:
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
    
    if diferencia == 0:
        print(f"\n✅ CAJA CUADRADA (sin diferencia)")
    elif diferencia > 0:
        print(f"\n💰 SOBRANTE de Gs. {diferencia:,.2f}")
    else:
        print(f"\n⚠️  FALTANTE de Gs. {abs(diferencia):,.2f}")
    
    cursor.execute("UPDATE cierres_caja SET Diferencia_Efectivo = %s WHERE ID_Cierre = 2", (diferencia,))
    conn.commit()
    
    print(f"\n✅ DIFERENCIA ACTUALIZADA EN BASE DE DATOS")
else:
    print("\n❌ ERROR: Cierre no encontrado")

cursor.close()
conn.close()

print("=" * 70)
