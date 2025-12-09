from django.db import connection

print("=" * 70)
print("🔐 ESTADO DE TARJETAS DE SUPERVISOR")
print("=" * 70)

cursor = connection.cursor()

# 1. Verificar si existe la columna Tipo_Autorizacion
print("\n1. Verificando columna Tipo_Autorizacion...")
cursor.execute("DESCRIBE tarjetas")
tiene_columna = any(col[0] == 'Tipo_Autorizacion' for col in cursor.fetchall())

if tiene_columna:
    print("   ✅ Columna existe")
else:
    print("   ❌ Columna NO existe")
    print("   Ejecutar: ALTER TABLE tarjetas ADD COLUMN Tipo_Autorizacion VARCHAR(20) NULL")
    exit()

# 2. Verificar tarjetas de supervisor
print("\n2. Tarjetas configuradas como SUPERVISOR:")
cursor.execute("""
    SELECT 
        t.Nro_Tarjeta,
        t.Estado,
        h.Nombre,
        h.Apellido
    FROM tarjetas t
    LEFT JOIN hijos h ON t.ID_Hijo = h.ID_Hijo
    WHERE t.Tipo_Autorizacion = 'SUPERVISOR'
""")
supervisores = cursor.fetchall()

if supervisores:
    print(f"   ✅ {len(supervisores)} tarjeta(s) encontrada(s):")
    for s in supervisores:
        print(f"      🔐 {s[0]} - {s[2]} {s[3]} ({s[1]})")
else:
    print("   ⚠️ NO hay tarjetas configuradas como SUPERVISOR")

# 3. Ver todas las tarjetas activas
print("\n3. Tarjetas activas disponibles:")
cursor.execute("""
    SELECT 
        t.Nro_Tarjeta,
        t.Tipo_Autorizacion,
        h.Nombre,
        h.Apellido
    FROM tarjetas t
    LEFT JOIN hijos h ON t.ID_Hijo = h.ID_Hijo
    WHERE t.Estado IN ('ACTIVA', 'Activa')
    ORDER BY t.Nro_Tarjeta
""")
tarjetas = cursor.fetchall()

print(f"   Total: {len(tarjetas)} tarjeta(s)")
for t in tarjetas:
    tipo = t[1] if t[1] else "NORMAL"
    simbolo = "🔐" if tipo == "SUPERVISOR" else "🎫"
    print(f"   {simbolo} {t[0]} - {t[2]} {t[3]} ({tipo})")

# 4. Resumen
print("\n" + "=" * 70)
print("RESUMEN:")
print("=" * 70)
print(f"✓ Total tarjetas activas: {len(tarjetas)}")
print(f"✓ Tarjetas SUPERVISOR: {len(supervisores)}")
print(f"✓ Tarjetas NORMAL: {len([t for t in tarjetas if not t[1] or t[1] == 'NORMAL'])}")

if not supervisores:
    print("\n⚠️ ACCIÓN NECESARIA:")
    print("Para configurar una tarjeta como SUPERVISOR:")
    print("1. Ir a: http://127.0.0.1:8000/admin/gestion/tarjeta/")
    print("2. Editar una de las tarjetas listadas arriba")
    print("3. En el campo 'Tipo Autorizacion' seleccionar: SUPERVISOR")
    print("4. Guardar cambios")
    print("\nEjemplo con tarjeta 00203:")
    print("   UPDATE tarjetas SET Tipo_Autorizacion='SUPERVISOR' WHERE Nro_Tarjeta='00203';")
else:
    print("\n✅ Sistema listo para autorización de supervisor")
