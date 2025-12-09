from django.db import connection

print("=" * 70)
print("🔍 VERIFICACIÓN COMPLETA DE TARJETA SUPERVISOR")
print("=" * 70)

cursor = connection.cursor()

# 1. Verificar estructura de tabla empleados
print("\n📋 1. ESTRUCTURA DE TABLA empleados")
print("-" * 70)
cursor.execute("DESCRIBE empleados")
columns_empleados = cursor.fetchall()
print("Columnas disponibles:")
for col in columns_empleados[:15]:  # Primeras 15 columnas
    print(f"  - {col[0]} ({col[1]})")

# 2. Buscar empleados con rol supervisor
print("\n👔 2. EMPLEADOS CON ROL DE SUPERVISOR/ADMIN")
print("-" * 70)
cursor.execute("""
    SELECT 
        e.ID_Empleado,
        e.Nombre,
        e.Apellido,
        e.RUC_CI,
        r.Nombre_Rol,
        e.Activo
    FROM empleados e
    INNER JOIN tipos_rol_general r ON e.ID_Rol = r.ID_Rol
    WHERE r.Nombre_Rol IN ('SUPERVISOR', 'ADMINISTRADOR', 'GERENTE')
    ORDER BY r.Nombre_Rol, e.Nombre
""")
empleados = cursor.fetchall()

if empleados:
    print(f"✓ Se encontraron {len(empleados)} empleado(s):\n")
    for emp in empleados:
        estado = "✓ Activo" if emp[5] else "✗ Inactivo"
        print(f"  👤 {emp[1]} {emp[2]}")
        print(f"     ID: {emp[0]} | RUC/CI: {emp[3]}")
        print(f"     Rol: {emp[4]} | {estado}")
        print()
else:
    print("⚠️ NO hay empleados con rol autorizado")

# 3. Verificar tarjetas activas
print("\n🎫 3. TARJETAS ACTIVAS DISPONIBLES")
print("-" * 70)
cursor.execute("""
    SELECT 
        t.Nro_Tarjeta,
        t.Tipo_Autorizacion,
        t.Estado,
        h.Nombre as Hijo_Nombre,
        h.Apellido as Hijo_Apellido,
        c.Nombres as Resp_Nombre,
        c.Apellidos as Resp_Apellido,
        c.RUC_CI as Resp_CI
    FROM tarjetas t
    LEFT JOIN hijos h ON t.ID_Hijo = h.ID_Hijo
    LEFT JOIN clientes c ON h.ID_Cliente_Responsable = c.ID_Cliente
    WHERE t.Estado IN ('ACTIVA', 'Activa')
    ORDER BY t.Tipo_Autorizacion DESC, t.Nro_Tarjeta
""")
tarjetas = cursor.fetchall()

if tarjetas:
    print(f"✓ Total: {len(tarjetas)} tarjeta(s) activa(s)\n")
    for t in tarjetas:
        tipo = t[1] if t[1] else "NORMAL"
        simbolo = "🔐" if tipo == "SUPERVISOR" else "🎫"
        print(f"  {simbolo} Tarjeta: {t[0]} ({tipo})")
        print(f"     Estado: {t[2]}")
        print(f"     Estudiante: {t[3]} {t[4]}")
        print(f"     Responsable: {t[5]} {t[6]} (CI: {t[7]})")
        print()
else:
    print("⚠️ NO hay tarjetas activas")

# 4. Buscar coincidencias entre tarjetas y empleados
print("\n🔗 4. COINCIDENCIAS TARJETA-EMPLEADO")
print("-" * 70)

if tarjetas and empleados:
    encontrado = False
    for t in tarjetas:
        ci_responsable = t[7]
        for emp in empleados:
            if emp[3] == ci_responsable:
                encontrado = True
                print(f"✓ COINCIDENCIA ENCONTRADA:")
                print(f"  Tarjeta: {t[0]}")
                print(f"  Responsable: {t[5]} {t[6]} (CI: {ci_responsable})")
                print(f"  Empleado: {emp[1]} {emp[2]} ({emp[4]})")
                print(f"  Tipo actual: {t[1] if t[1] else 'NORMAL'}")
                if t[1] != 'SUPERVISOR':
                    print(f"  ⚠️ Puede configurarse como SUPERVISOR")
                print()
    
    if not encontrado:
        print("⚠️ NO hay coincidencias entre responsables y empleados")
        print("\nResponsables con tarjetas:")
        for t in tarjetas:
            print(f"  - CI: {t[7]} ({t[5]} {t[6]})")
        print("\nEmpleados supervisores:")
        for emp in empleados:
            print(f"  - CI: {emp[3]} ({emp[1]} {emp[2]})")
else:
    if not tarjetas:
        print("⚠️ NO hay tarjetas activas")
    if not empleados:
        print("⚠️ NO hay empleados con rol autorizado")

# 5. Verificar si ya existe tarjeta de supervisor
print("\n🔐 5. TARJETAS DE SUPERVISOR CONFIGURADAS")
print("-" * 70)
cursor.execute("""
    SELECT 
        t.Nro_Tarjeta,
        t.Estado,
        h.Nombre,
        h.Apellido,
        c.RUC_CI
    FROM tarjetas t
    LEFT JOIN hijos h ON t.ID_Hijo = h.ID_Hijo
    LEFT JOIN clientes c ON h.ID_Cliente_Responsable = c.ID_Cliente
    WHERE t.Tipo_Autorizacion = 'SUPERVISOR'
""")
supervisores = cursor.fetchall()

if supervisores:
    print(f"✓ {len(supervisores)} tarjeta(s) configurada(s):\n")
    for s in supervisores:
        print(f"  🔐 Tarjeta: {s[0]}")
        print(f"     Estado: {s[1]}")
        print(f"     Estudiante: {s[2]} {s[3]}")
        print(f"     CI Responsable: {s[4]}")
        print()
else:
    print("⚠️ NO hay tarjetas configuradas como SUPERVISOR")

print("\n" + "=" * 70)
print("✅ VERIFICACIÓN COMPLETADA")
print("=" * 70)

# Sugerencias
if not supervisores and tarjetas and empleados:
    print("\n💡 SUGERENCIA:")
    print("   Hay empleados y tarjetas disponibles.")
    print("   Pasos para configurar:")
    print("   1. Ir a: http://127.0.0.1:8000/admin/gestion/tarjeta/")
    print("   2. Buscar tarjeta de un responsable que sea empleado")
    print("   3. Editar y establecer: Tipo_Autorizacion = 'SUPERVISOR'")
elif supervisores:
    print("\n✅ SISTEMA LISTO:")
    print("   Tarjeta(s) de supervisor configurada(s) correctamente")
else:
    print("\n⚠️ ACCIÓN REQUERIDA:")
    print("   1. Crear empleados con rol SUPERVISOR/ADMINISTRADOR")
    print("   2. Crear tarjetas para esos empleados")
    print("   3. Configurar tipo de autorización")
