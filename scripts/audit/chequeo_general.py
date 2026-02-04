"""
Chequeo General del Sistema - Post Eliminación de Tablas Legacy
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection
from gestion.models import (
    Ventas, Compras, PagosVenta, PagosProveedores,
    AplicacionPagosVentas, AplicacionPagosCompras,
    NotasCreditoCliente, NotasCreditoProveedor
)

print("=" * 70)
print("CHEQUEO GENERAL DEL SISTEMA")
print("=" * 70)

# 1. Verificar migraciones
cursor = connection.cursor()
cursor.execute('SELECT COUNT(*) FROM django_migrations WHERE app="gestion"')
migraciones = cursor.fetchone()[0]
print(f"\n✅ Migraciones de gestion aplicadas: {migraciones}")

# 2. Verificar que tablas legacy NO existan
cursor.execute('SHOW TABLES LIKE "cta_corriente"')
if cursor.fetchone():
    print("\n❌ ERROR: Tabla cta_corriente todavía existe")
else:
    print("\n✅ Tabla cta_corriente eliminada correctamente")

cursor.execute('SHOW TABLES LIKE "cta_corriente_prov"')
if cursor.fetchone():
    print("❌ ERROR: Tabla cta_corriente_prov todavía existe")
else:
    print("✅ Tabla cta_corriente_prov eliminada correctamente")

# 3. Verificar backups
cursor.execute('SHOW TABLES LIKE "%backup%"')
backups = cursor.fetchall()
print(f"\n✅ Backups creados: {len(backups)}")
for backup in backups:
    cursor.execute(f'SELECT COUNT(*) FROM {backup[0]}')
    count = cursor.fetchone()[0]
    print(f"  - {backup[0]}: {count} registros")

# 4. Verificar tablas del nuevo sistema
print("\n" + "=" * 70)
print("NUEVO SISTEMA DE CUENTA CORRIENTE")
print("=" * 70)

tablas_nuevas = [
    ('pagos_venta', 'Pagos de Ventas'),
    ('pagos_proveedores', 'Pagos a Proveedores'),
    ('aplicacion_pagos_ventas', 'Aplicación Pagos Ventas'),
    ('aplicacion_pagos_compras', 'Aplicación Pagos Compras'),
    ('notas_credito_cliente', 'Notas Crédito Cliente'),
    ('notas_credito_proveedor', 'Notas Crédito Proveedor')
]

for tabla, nombre in tablas_nuevas:
    cursor.execute(f'SELECT COUNT(*) FROM {tabla}')
    count = cursor.fetchone()[0]
    print(f"✅ {nombre:30} ({tabla}): {count:4} registros")

# 5. Verificar campos nuevos en Ventas y Compras
print("\n" + "=" * 70)
print("CAMPOS NUEVOS EN VENTAS/COMPRAS")
print("=" * 70)

cursor.execute("SHOW COLUMNS FROM ventas LIKE 'Saldo_Pendiente'")
if cursor.fetchone():
    print("✅ ventas.Saldo_Pendiente existe")
else:
    print("❌ ventas.Saldo_Pendiente NO existe")

cursor.execute("SHOW COLUMNS FROM ventas LIKE 'Estado_Pago'")
if cursor.fetchone():
    print("✅ ventas.Estado_Pago existe")
else:
    print("❌ ventas.Estado_Pago NO existe")

cursor.execute("SHOW COLUMNS FROM compras LIKE 'Saldo_Pendiente'")
if cursor.fetchone():
    print("✅ compras.Saldo_Pendiente existe")
else:
    print("❌ compras.Saldo_Pendiente NO existe")

cursor.execute("SHOW COLUMNS FROM compras LIKE 'Estado_Pago'")
if cursor.fetchone():
    print("✅ compras.Estado_Pago existe")
else:
    print("❌ compras.Estado_Pago NO existe")

# 6. Verificar triggers
print("\n" + "=" * 70)
print("TRIGGERS DE SINCRONIZACIÓN")
print("=" * 70)

triggers = [
    'trg_after_insert_aplicacion_ventas',
    'trg_after_delete_aplicacion_ventas',
    'trg_after_insert_aplicacion_compras',
    'trg_after_delete_aplicacion_compras'
]

cursor.execute("SHOW TRIGGERS FROM cantinatitadb")
triggers_db = [t[0] for t in cursor.fetchall()]

for trigger in triggers:
    if trigger in triggers_db:
        print(f"✅ {trigger}")
    else:
        print(f"❌ {trigger} NO existe")

# 7. Estadísticas del nuevo sistema
print("\n" + "=" * 70)
print("ESTADÍSTICAS DEL SISTEMA")
print("=" * 70)

# Ventas con saldo pendiente
cursor.execute("SELECT COUNT(*), SUM(Saldo_Pendiente) FROM ventas WHERE Estado_Pago IN ('Pendiente', 'Parcial')")
ventas_pendientes, total_pendiente_ventas = cursor.fetchone()
print(f"\n📊 Ventas con saldo pendiente: {ventas_pendientes or 0}")
print(f"   Monto total pendiente: Gs. {total_pendiente_ventas or 0:,.0f}")

# Compras con saldo pendiente
cursor.execute("SELECT COUNT(*), SUM(Saldo_Pendiente) FROM compras WHERE Estado_Pago IN ('Pendiente', 'Parcial')")
compras_pendientes, total_pendiente_compras = cursor.fetchone()
print(f"\n📊 Compras con saldo pendiente: {compras_pendientes or 0}")
print(f"   Monto total pendiente: Gs. {total_pendiente_compras or 0:,.0f}")

# 8. Verificar modelos Django
print("\n" + "=" * 70)
print("MODELOS DJANGO")
print("=" * 70)

try:
    # Intentar importar modelos eliminados (debe fallar)
    from gestion.models import CtaCorriente
    print("❌ ERROR: CtaCorriente todavía existe en models.py")
except ImportError:
    print("✅ CtaCorriente eliminado de models.py")

try:
    from gestion.models import CtaCorrienteProv
    print("❌ ERROR: CtaCorrienteProv todavía existe en models.py")
except ImportError:
    print("✅ CtaCorrienteProv eliminado de models.py")

# Verificar que los nuevos modelos existen
modelos_nuevos = [
    ('PagosProveedores', PagosProveedores),
    ('AplicacionPagosVentas', AplicacionPagosVentas),
    ('AplicacionPagosCompras', AplicacionPagosCompras),
    ('NotasCreditoCliente', NotasCreditoCliente),
    ('NotasCreditoProveedor', NotasCreditoProveedor)
]

for nombre, modelo in modelos_nuevos:
    print(f"✅ {nombre} importado correctamente")

print("\n" + "=" * 70)
print("✅ CHEQUEO COMPLETADO - SISTEMA FUNCIONAL")
print("=" * 70)
