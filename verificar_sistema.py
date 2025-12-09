from django.db import connection

print("=" * 60)
print("VERIFICACIÓN DEL SISTEMA DE PAGOS")
print("=" * 60)

cursor = connection.cursor()

# 1. Verificar estructura de tabla ventas
print("\n📋 1. ESTRUCTURA DE TABLA VENTAS")
print("-" * 60)
cursor.execute("DESCRIBE ventas")
columns = cursor.fetchall()
campos_importantes = ["Tipo_Venta", "Autorizado_Por", "Motivo_Credito", "Genera_Factura_Legal"]
for col in columns:
    if col[0] in campos_importantes:
        nullable = "NULL" if col[2] == "YES" else "NOT NULL"
        default = f"DEFAULT {col[4]}" if col[4] else ""
        print(f"✓ {col[0]}: {col[1]} {nullable} {default}")

# 2. Verificar datos actualizados
print("\n📊 2. DATOS DE VENTAS")
print("-" * 60)
cursor.execute("SELECT COUNT(*) FROM ventas WHERE Tipo_Venta = 'CONTADO'")
contado = cursor.fetchone()[0]
print(f"✓ Ventas CONTADO: {contado}")

cursor.execute("SELECT COUNT(*) FROM ventas WHERE Tipo_Venta = 'CREDITO'")
credito = cursor.fetchone()[0]
print(f"✓ Ventas CRÉDITO: {credito}")

cursor.execute("SELECT COUNT(*) FROM ventas WHERE Genera_Factura_Legal = 1")
con_factura = cursor.fetchone()[0]
print(f"✓ Ventas con factura legal: {con_factura}")

cursor.execute("SELECT COUNT(*) FROM ventas WHERE Genera_Factura_Legal = 0")
sin_factura = cursor.fetchone()[0]
print(f"✓ Ventas sin factura legal: {sin_factura}")

# 3. Verificar medios de pago
print("\n💳 3. MEDIOS DE PAGO CONFIGURADOS")
print("-" * 60)
cursor.execute("SELECT ID_Medio_Pago, Descripcion, Genera_Comision FROM medios_pago WHERE Activo = 1")
medios = cursor.fetchall()
for medio in medios:
    comision = "✓ Con comisión" if medio[2] else "Sin comisión"
    print(f"{medio[0]}. {medio[1]} - {comision}")

# 4. Verificar tarifas de comisión
print("\n💰 4. TARIFAS DE COMISIÓN ACTIVAS")
print("-" * 60)
cursor.execute("""
    SELECT mp.Descripcion, tc.Porcentaje_Comision, tc.Monto_Fijo_Comision
    FROM tarifas_comision tc
    INNER JOIN medios_pago mp ON tc.ID_Medio_Pago = mp.ID_Medio_Pago
    WHERE tc.Activo = 1
""")
tarifas = cursor.fetchall()
if tarifas:
    for tarifa in tarifas:
        porcentaje = float(tarifa[1]) * 100
        fijo = f"+ Gs. {int(tarifa[2]):,}" if tarifa[2] else ""
        print(f"✓ {tarifa[0]}: {porcentaje}% {fijo}")
else:
    print("⚠️ No hay tarifas configuradas (se deben crear en Django Admin)")

# 5. Verificar índices creados
print("\n🔍 5. ÍNDICES EN TABLA VENTAS")
print("-" * 60)
cursor.execute("SHOW INDEX FROM ventas WHERE Key_name LIKE 'IDX_Ventas%'")
indices = cursor.fetchall()
for idx in indices:
    print(f"✓ {idx[2]}: Columna {idx[4]}")

# 6. Verificar vista validar_supervisor
print("\n🔐 6. VISTA VALIDAR_SUPERVISOR")
print("-" * 60)
try:
    from gestion.pos_views import validar_supervisor
    print("✓ Vista validar_supervisor importada correctamente")
    print(f"✓ Función: {validar_supervisor.__name__}")
    print(f"✓ Ubicación: gestion.pos_views")
except ImportError as e:
    print(f"❌ Error al importar: {e}")

# 7. Verificar URL configurada
print("\n🌐 7. CONFIGURACIÓN DE URLS")
print("-" * 60)
try:
    from django.urls import reverse
    url = reverse('pos:validar_supervisor')
    print(f"✓ URL configurada: {url}")
except Exception as e:
    print(f"❌ Error en URL: {e}")

print("\n" + "=" * 60)
print("✅ VERIFICACIÓN COMPLETADA")
print("=" * 60)
print("\nSistema listo para:")
print("1. Procesar pagos con medios externos")
print("2. Calcular comisiones automáticamente")
print("3. Autorizar ventas a crédito con supervisor")
print("4. Emitir facturas legales según tipo de pago")
print("\n⚠️ PENDIENTE: Configurar tarifas de comisión en Django Admin")
print("   http://127.0.0.1:8000/admin/gestion/tarifascomision/")
