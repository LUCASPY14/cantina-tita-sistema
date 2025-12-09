from django.db import connection

print("=" * 70)
print("🔐 VERIFICACIÓN DE TARJETAS DE SUPERVISOR")
print("=" * 70)

cursor = connection.cursor()

# 1. Verificar si existen tarjetas con tipo_autorizacion
print("\n📋 1. COLUMNA tipo_autorizacion EN TABLA tarjetas")
print("-" * 70)
cursor.execute("DESCRIBE tarjetas")
columns = cursor.fetchall()
tiene_campo = False
for col in columns:
    if col[0] == 'Tipo_Autorizacion':
        tiene_campo = True
        print(f"✓ Campo encontrado: {col[0]} ({col[1]})")
        break

if not tiene_campo:
    print("⚠️ La columna 'Tipo_Autorizacion' NO existe en la tabla tarjetas")
    print("   Se debe agregar primero con:")
    print("   ALTER TABLE tarjetas ADD COLUMN Tipo_Autorizacion VARCHAR(20) NULL;")
else:
    # 2. Buscar tarjetas de supervisor
    print("\n🎫 2. TARJETAS DE SUPERVISOR EXISTENTES")
    print("-" * 70)
    cursor.execute("""
        SELECT 
            t.Nro_Tarjeta,
            t.Tipo_Autorizacion,
            t.Estado,
            h.Nombre,
            h.Apellido,
            c.Nombres as Cliente_Nombre,
            c.Apellidos as Cliente_Apellido,
            c.RUC_CI
        FROM tarjetas t
        LEFT JOIN hijos h ON t.ID_Hijo = h.ID_Hijo
        LEFT JOIN clientes c ON h.ID_Cliente_Responsable = c.ID_Cliente
        WHERE t.Tipo_Autorizacion = 'SUPERVISOR'
        ORDER BY t.Nro_Tarjeta
    """)
    tarjetas_supervisor = cursor.fetchall()
    
    if tarjetas_supervisor:
        print(f"✓ Se encontraron {len(tarjetas_supervisor)} tarjeta(s) de supervisor:\n")
        for t in tarjetas_supervisor:
            print(f"  📌 Tarjeta: {t[0]}")
            print(f"     Tipo: {t[1]}")
            print(f"     Estado: {t[2]}")
            print(f"     Hijo: {t[3]} {t[4]}")
            print(f"     Responsable: {t[5]} {t[6]} (CI: {t[7]})")
            print()
    else:
        print("⚠️ NO hay tarjetas con Tipo_Autorizacion = 'SUPERVISOR'")
        print()
        print("Para crear una tarjeta de supervisor:")
        print("1. Ir a: http://127.0.0.1:8000/admin/gestion/tarjeta/")
        print("2. Editar una tarjeta existente")
        print("3. Establecer: Tipo_Autorizacion = 'SUPERVISOR'")
        print("4. Asegurar: Estado = 'ACTIVA'")
    
    # 3. Verificar empleados supervisores
    print("\n👔 3. EMPLEADOS CON ROL DE SUPERVISOR")
    print("-" * 70)
    cursor.execute("""
        SELECT 
            e.ID_Empleado,
            e.Nombre,
            e.Apellido,
            e.CI,
            r.Nombre_Rol,
            e.Activo
        FROM empleados e
        INNER JOIN tipos_rol_general r ON e.ID_Rol = r.ID_Rol
        WHERE r.Nombre_Rol IN ('SUPERVISOR', 'ADMINISTRADOR', 'GERENTE')
        ORDER BY r.Nombre_Rol, e.Nombre
    """)
    empleados_supervisor = cursor.fetchall()
    
    if empleados_supervisor:
        print(f"✓ Se encontraron {len(empleados_supervisor)} empleado(s) con rol autorizado:\n")
        for emp in empleados_supervisor:
            estado = "✓ Activo" if emp[5] else "✗ Inactivo"
            print(f"  👤 {emp[1]} {emp[2]}")
            print(f"     ID: {emp[0]} | CI: {emp[3]}")
            print(f"     Rol: {emp[4]} | {estado}")
            print()
    else:
        print("⚠️ NO hay empleados con rol de SUPERVISOR/ADMINISTRADOR/GERENTE")
    
    # 4. Intentar emparejar tarjetas con empleados
    if tarjetas_supervisor and empleados_supervisor:
        print("\n🔗 4. EMPAREJAMIENTO TARJETA-EMPLEADO")
        print("-" * 70)
        for t in tarjetas_supervisor:
            ruc_ci_cliente = t[7]
            empleado_match = None
            for emp in empleados_supervisor:
                if emp[3] == ruc_ci_cliente:
                    empleado_match = emp
                    break
            
            if empleado_match:
                print(f"✓ Tarjeta {t[0]} → Empleado {empleado_match[1]} {empleado_match[2]}")
                print(f"  Coincidencia por CI: {ruc_ci_cliente}")
            else:
                print(f"⚠️ Tarjeta {t[0]} NO tiene empleado supervisor asociado")
                print(f"   CI del responsable: {ruc_ci_cliente}")
                print(f"   Solución: Crear empleado con CI {ruc_ci_cliente} y rol SUPERVISOR")
        print()
    
    # 5. Mostrar todas las tarjetas activas (para referencia)
    print("\n📊 5. RESUMEN DE TARJETAS ACTIVAS")
    print("-" * 70)
    cursor.execute("""
        SELECT 
            COUNT(*) as Total,
            Tipo_Autorizacion
        FROM tarjetas
        WHERE Estado IN ('ACTIVA', 'Activa')
        GROUP BY Tipo_Autorizacion
    """)
    resumen = cursor.fetchall()
    
    if resumen:
        for r in resumen:
            tipo = r[1] if r[1] else "SIN TIPO"
            print(f"  {r[0]} tarjeta(s): {tipo}")
    
    cursor.execute("""
        SELECT COUNT(*) FROM tarjetas WHERE Estado IN ('ACTIVA', 'Activa')
    """)
    total = cursor.fetchone()[0]
    print(f"\n  Total: {total} tarjetas activas")

print("\n" + "=" * 70)
print("✅ VERIFICACIÓN COMPLETADA")
print("=" * 70)

# Sugerencias finales
if not tiene_campo:
    print("\n⚠️ ACCIÓN REQUERIDA:")
    print("   1. Agregar columna Tipo_Autorizacion a tabla tarjetas")
    print("   2. Ejecutar el script de migración correspondiente")
elif not tarjetas_supervisor:
    print("\n⚠️ ACCIÓN REQUERIDA:")
    print("   1. Configurar al menos una tarjeta como SUPERVISOR")
    print("   2. Asegurar que el responsable de esa tarjeta sea un empleado")
    print("   3. El empleado debe tener rol SUPERVISOR/ADMIN/GERENTE")
elif not empleados_supervisor:
    print("\n⚠️ ACCIÓN REQUERIDA:")
    print("   1. Crear empleados con rol de SUPERVISOR")
    print("   2. Asociar CI del empleado con el responsable de la tarjeta")
else:
    print("\n✅ SISTEMA LISTO:")
    print("   - Tarjetas de supervisor configuradas")
    print("   - Empleados supervisores disponibles")
    print("   - Autorización de ventas a crédito operativa")
