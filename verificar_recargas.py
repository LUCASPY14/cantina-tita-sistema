from django.db import connection
from datetime import datetime

print("="*70)
print("🔎 VERIFICACIÓN DE RECARGAS DE TARJETAS")
print("="*70)

cursor = connection.cursor()

# 1. Buscar tarjeta de prueba
nro_tarjeta = '01024'
cursor.execute("SELECT saldo_actual, estado FROM tarjetas WHERE nro_tarjeta=%s", [nro_tarjeta])
row = cursor.fetchone()
if row:
    saldo, estado = row
    print(f"Tarjeta {nro_tarjeta}: saldo={saldo}, estado={estado}")
else:
    print(f"❌ Tarjeta {nro_tarjeta} no encontrada")
    exit()

# 2. Verificar recargas recientes
hoy = datetime.now().date()
cursor.execute("""
    SELECT id_carga, monto_cargado, forma_pago, fecha_carga, saldo_anterior, saldo_posterior
    FROM cargassaldo
    WHERE nro_tarjeta=%s AND DATE(fecha_carga)=%s
    ORDER BY fecha_carga DESC LIMIT 5
""", [nro_tarjeta, hoy])
recargas = cursor.fetchall()
if recargas:
    print(f"\nRecargas de hoy para tarjeta {nro_tarjeta}:")
    for r in recargas:
        print(f"  - ID:{r[0]} Monto:{r[1]} Forma:{r[2]} Fecha:{r[3]} Saldo:{r[4]}→{r[5]}")
else:
    print("No hay recargas hoy para esta tarjeta.")

# 3. Verificar comisión configurada para recarga con tarjeta de débito
cursor.execute("""
    SELECT m.id_medio_pago, m.descripcion, t.porcentaje, t.monto_fijo
    FROM medios_pago m
    LEFT JOIN tarifascomision t ON t.id_medio_pago = m.id_medio_pago AND t.activo=1
    WHERE m.descripcion LIKE '%Débito%'
""")
comisiones = cursor.fetchall()
if comisiones:
    print("\nTarifa de comisión para recarga con Débito:")
    for c in comisiones:
        print(f"  - Medio:{c[1]} Porcentaje:{c[2]} Monto fijo:{c[3]}")
else:
    print("No hay comisión configurada para Débito.")

print("\n"+"="*70)
print("✅ Verificación completada")
print("="*70)
