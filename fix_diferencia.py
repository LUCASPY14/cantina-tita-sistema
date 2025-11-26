import MySQLdb

conn = MySQLdb.connect(
    host='localhost',
    user='root',
    password='L01G05S33Vice.42',
    database='cantinatitadb'
)

cursor = conn.cursor()

print("ACTUALIZANDO DIFERENCIA DE CIERRE DE CAJA")
print("=" * 60)

# Ver datos actuales
cursor.execute("""
    SELECT c.Monto_Inicial, c.Monto_Contado_Fisico,
           IFNULL(SUM(pv.Monto_Aplicado), 0) as Total_Pagos
    FROM cierres_caja c
    LEFT JOIN pagos_venta pv ON c.ID_Cierre = pv.ID_Cierre
    LEFT JOIN medios_pago mp ON pv.ID_Medio_Pago = mp.ID_Medio_Pago 
        AND mp.Descripcion = 'EFECTIVO'
    WHERE c.ID_Cierre = 1
    GROUP BY c.ID_Cierre, c.Monto_Inicial, c.Monto_Contado_Fisico
""")
datos = cursor.fetchone()

if datos:
    monto_inicial = float(datos[0]) if datos[0] else 0
    monto_contado = float(datos[1]) if datos[1] else 0
    total_pagos = float(datos[2]) if datos[2] else 0
    
    esperado = monto_inicial + total_pagos
    diferencia = monto_contado - esperado
    
    print(f"Monto inicial:    Gs. {monto_inicial:,.2f}")
    print(f"Pagos efectivo:   Gs. {total_pagos:,.2f}")
    print(f"Total esperado:   Gs. {esperado:,.2f}")
    print(f"Monto contado:    Gs. {monto_contado:,.2f}")
    print(f"Diferencia:       Gs. {diferencia:,.2f}")
    
    if monto_contado > 0:
        # Actualizar
        cursor.execute("""
            UPDATE cierres_caja 
            SET Diferencia_Efectivo = %s 
            WHERE ID_Cierre = 1
        """, (diferencia,))
        conn.commit()
        
        print("\n✓ Diferencia actualizada exitosamente")
        print(f"  Diferencia guardada: Gs. {diferencia:,.2f}")
    else:
        print("\nError: Monto contado es 0 o NULL")
else:
    print("Error: No se encontró el cierre de caja")

cursor.close()
conn.close()
