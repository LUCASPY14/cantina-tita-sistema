import MySQLdb
from datetime import datetime

# Conectar a la base de datos
conn = MySQLdb.connect(
    host='localhost',
    user='root',
    passwd='L01G05S33Vice.42',
    db='cantinatitadb'
)

cursor = conn.cursor()

print("=" * 70)
print("PRUEBA DEL SISTEMA DE RECARGAS DE TARJETA")
print("=" * 70)

# 1. Verificar que existe el trigger
print("\n1. Verificando trigger trg_carga_saldo_genera_venta...")
cursor.execute("SHOW TRIGGERS LIKE 'cargas_saldo'")
triggers = cursor.fetchall()
trigger_existe = False
for t in triggers:
    if t[0] == 'trg_carga_saldo_genera_venta':
        trigger_existe = True
        print(f"   ✓ Trigger encontrado: {t[0]}")
        print(f"   - Evento: {t[1]}")
        print(f"   - Timing: {t[4]}")

if not trigger_existe:
    print("   ✗ ERROR: Trigger no encontrado!")
    print("   Ejecuta: python configurar_recargas_como_venta.py")
    exit(1)

# 2. Verificar que existe el producto REC-TAR
print("\n2. Verificando producto REC-TAR...")
cursor.execute("SELECT ID_Producto, Codigo, Descripcion FROM productos WHERE Codigo = 'REC-TAR'")
producto = cursor.fetchone()
if producto:
    print(f"   ✓ Producto encontrado:")
    print(f"   - ID: {producto[0]}")
    print(f"   - Código: {producto[1]}")
    print(f"   - Descripción: {producto[2]}")
else:
    print("   ✗ ERROR: Producto REC-TAR no encontrado!")
    exit(1)

# 3. Verificar o crear tarjeta de prueba
print("\n3. Preparando tarjeta de prueba...")
cursor.execute("SELECT Nro_Tarjeta, Saldo_Actual FROM tarjetas WHERE Nro_Tarjeta = '9999'")
tarjeta = cursor.fetchone()

if not tarjeta:
    # Buscar o crear hijo de prueba
    cursor.execute("SELECT ID_Hijo FROM hijos WHERE Nombre = 'Test' AND Apellido = 'Prueba'")
    hijo = cursor.fetchone()
    
    if not hijo:
        # Buscar cliente para asociar
        cursor.execute("SELECT ID_Cliente FROM clientes LIMIT 1")
        cliente = cursor.fetchone()
        if cliente:
            cursor.execute("""
                INSERT INTO hijos (ID_Cliente_Responsable, Nombre, Apellido, Fecha_Nacimiento)
                VALUES (%s, 'Test', 'Prueba', '2015-01-01')
            """, (cliente[0],))
            conn.commit()
            cursor.execute("SELECT LAST_INSERT_ID()")
            id_hijo = cursor.fetchone()[0]
            print(f"   ✓ Hijo de prueba creado (ID: {id_hijo})")
        else:
            print("   ✗ ERROR: No hay clientes en el sistema")
            exit(1)
    else:
        id_hijo = hijo[0]
    
    # Crear tarjeta de prueba
    cursor.execute("""
        INSERT INTO tarjetas (Nro_Tarjeta, ID_Hijo, Saldo_Actual, Estado, Fecha_Vencimiento)
        VALUES ('9999', %s, 0, 'Activa', '2025-12-31')
    """, (id_hijo,))
    conn.commit()
    print("   ✓ Tarjeta de prueba creada (9999)")
    saldo_anterior = 0
else:
    saldo_anterior = float(tarjeta[1])
    print(f"   ✓ Tarjeta de prueba encontrada (9999)")
    print(f"   - Saldo actual: Gs. {saldo_anterior:,.0f}")

# 4. Contar registros antes de la recarga
print("\n4. Contando registros antes de la recarga...")
cursor.execute("SELECT COUNT(*) FROM cargas_saldo WHERE Nro_Tarjeta = '9999'")
recargas_antes = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM ventas WHERE Tipo_Venta = 'Recarga Tarjeta'")
ventas_antes = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM pagos_venta WHERE Referencia_Transaccion LIKE '%Recarga Tarjeta 9999%'")
pagos_antes = cursor.fetchone()[0]

print(f"   - Recargas anteriores: {recargas_antes}")
print(f"   - Ventas de recarga anteriores: {ventas_antes}")
print(f"   - Pagos de recarga anteriores: {pagos_antes}")

# 5. Registrar una recarga de prueba
print("\n5. Registrando recarga de prueba...")
monto_recarga = 50000.00

# Obtener cliente asociado a la tarjeta
cursor.execute("""
    SELECT h.ID_Cliente_Responsable 
    FROM tarjetas t
    JOIN hijos h ON t.ID_Hijo = h.ID_Hijo
    WHERE t.Nro_Tarjeta = '9999'
""")
cliente_result = cursor.fetchone()
id_cliente = cliente_result[0] if cliente_result else None

try:
    cursor.execute("""
        INSERT INTO cargas_saldo (
            Nro_Tarjeta,
            ID_Cliente_Origen,
            Fecha_Carga,
            Monto_Cargado
        ) VALUES (%s, %s, %s, %s)
    """, ('9999', id_cliente, datetime.now(), monto_recarga))
    conn.commit()
    cursor.execute("SELECT LAST_INSERT_ID()")
    id_recarga = cursor.fetchone()[0]
    print(f"   ✓ Recarga registrada exitosamente (ID: {id_recarga})")
    print(f"   - Monto: Gs. {monto_recarga:,.0f}")
except Exception as e:
    print(f"   ✗ ERROR al registrar recarga: {e}")
    conn.rollback()
    exit(1)

# 6. Verificar que se crearon los registros automáticos
print("\n6. Verificando registros creados automáticamente...")

# Esperar un momento para que el trigger se ejecute
import time
time.sleep(1)

# Verificar venta
cursor.execute("""
    SELECT ID_Venta, Monto_Total, Estado, Tipo_Venta
    FROM ventas 
    WHERE Tipo_Venta = 'Recarga Tarjeta'
    ORDER BY ID_Venta DESC 
    LIMIT 1
""")
venta = cursor.fetchone()

if venta:
    print(f"   ✓ VENTA creada automáticamente:")
    print(f"   - ID Venta: {venta[0]}")
    print(f"   - Monto: Gs. {float(venta[1]):,.0f}")
    print(f"   - Estado: {venta[2]}")
    print(f"   - Tipo: {venta[3]}")
    id_venta_creada = venta[0]
else:
    print("   ✗ ERROR: No se creó la venta automáticamente")
    id_venta_creada = None

# Verificar documento tributario
if id_venta_creada:
    cursor.execute("""
        SELECT dt.ID_Documento, dt.Monto_Total, dt.Monto_Exento
        FROM documentos_tributarios dt
        JOIN ventas v ON dt.ID_Documento = v.ID_Documento
        WHERE v.ID_Venta = %s
    """, (id_venta_creada,))
    documento = cursor.fetchone()
    
    if documento:
        print(f"   ✓ DOCUMENTO TRIBUTARIO creado:")
        print(f"   - ID Documento: {documento[0]}")
        print(f"   - Monto Total: Gs. {float(documento[1]):,.0f}")
        print(f"   - Monto Exento: Gs. {float(documento[2]):,.0f}")
    else:
        print("   ✗ ERROR: No se creó el documento tributario")

# Verificar detalle de venta
if id_venta_creada:
    cursor.execute("""
        SELECT dv.ID_Producto, p.Codigo, dv.Cantidad, dv.Subtotal_Total
        FROM detalle_venta dv
        JOIN productos p ON dv.ID_Producto = p.ID_Producto
        WHERE dv.ID_Venta = %s
    """, (id_venta_creada,))
    detalle = cursor.fetchone()
    
    if detalle:
        print(f"   ✓ DETALLE DE VENTA creado:")
        print(f"   - Producto: {detalle[1]}")
        print(f"   - Cantidad: {float(detalle[2])}")
        print(f"   - Subtotal: Gs. {float(detalle[3]):,.0f}")
    else:
        print("   ✗ ERROR: No se creó el detalle de venta")

# Verificar pago
if id_venta_creada:
    cursor.execute("""
        SELECT pv.ID_Pago_Venta, mp.Descripcion, pv.Monto_Aplicado, pv.Referencia_Transaccion
        FROM pagos_venta pv
        JOIN medios_pago mp ON pv.ID_Medio_Pago = mp.ID_Medio_Pago
        WHERE pv.ID_Venta = %s
    """, (id_venta_creada,))
    pago = cursor.fetchone()
    
    if pago:
        print(f"   ✓ PAGO registrado:")
        print(f"   - ID Pago: {pago[0]}")
        print(f"   - Medio: {pago[1]}")
        print(f"   - Monto: Gs. {float(pago[2]):,.0f}")
        print(f"   - Referencia: {pago[3]}")
    else:
        print("   ✗ ERROR: No se registró el pago")

# 7. Verificar actualización de saldo
print("\n7. Verificando actualización de saldo...")
cursor.execute("SELECT Saldo_Actual FROM tarjetas WHERE Nro_Tarjeta = '9999'")
saldo_nuevo = float(cursor.fetchone()[0])

print(f"   - Saldo anterior: Gs. {saldo_anterior:,.0f}")
print(f"   - Monto recargado: Gs. {monto_recarga:,.0f}")
print(f"   - Saldo esperado: Gs. {(saldo_anterior + monto_recarga):,.0f}")
print(f"   - Saldo actual: Gs. {saldo_nuevo:,.0f}")

if saldo_nuevo == (saldo_anterior + monto_recarga):
    print("   ✓ Saldo actualizado correctamente")
else:
    print(f"   ⚠️ ADVERTENCIA: Diferencia de Gs. {(saldo_nuevo - (saldo_anterior + monto_recarga)):,.0f}")

# 8. Resumen final
print("\n" + "=" * 70)
print("RESUMEN DE LA PRUEBA")
print("=" * 70)

cursor.execute("SELECT COUNT(*) FROM cargas_saldo WHERE Nro_Tarjeta = '9999'")
recargas_despues = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM ventas WHERE Tipo_Venta = 'Recarga Tarjeta'")
ventas_despues = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM pagos_venta WHERE Referencia_Transaccion LIKE '%Recarga Tarjeta 9999%'")
pagos_despues = cursor.fetchone()[0]

print(f"\nRegistros creados:")
print(f"  - Recargas: {recargas_despues - recargas_antes} nueva(s)")
print(f"  - Ventas: {ventas_despues - ventas_antes} nueva(s)")
print(f"  - Pagos: {pagos_despues - pagos_antes} nuevo(s)")

print(f"\nEstado de la tarjeta 9999:")
print(f"  - Saldo actual: Gs. {saldo_nuevo:,.0f}")
print(f"  - Total recargado: Gs. {monto_recarga:,.0f}")

print("\n✅ PRUEBA COMPLETADA")
print("=" * 70)

conn.close()
