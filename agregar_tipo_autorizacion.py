from django.db import connection

print("=" * 70)
print("🔧 AGREGANDO COLUMNA Tipo_Autorizacion A TABLA tarjetas")
print("=" * 70)

cursor = connection.cursor()

try:
    # Agregar columna Tipo_Autorizacion
    print("\n1. Agregando columna Tipo_Autorizacion...")
    cursor.execute("""
        ALTER TABLE tarjetas 
        ADD COLUMN Tipo_Autorizacion VARCHAR(20) NULL
        COMMENT 'Tipo de autorizacion: NORMAL, SUPERVISOR'
    """)
    print("   ✅ Columna agregada exitosamente")
    
except Exception as e:
    if "Duplicate column name" in str(e):
        print("   ⚠️ La columna ya existe (OK)")
    else:
        print(f"   ❌ Error: {e}")
        raise

try:
    # Actualizar tarjetas existentes a NORMAL por defecto
    print("\n2. Estableciendo valor por defecto en tarjetas existentes...")
    cursor.execute("""
        UPDATE tarjetas 
        SET Tipo_Autorizacion = 'NORMAL' 
        WHERE Tipo_Autorizacion IS NULL
    """)
    affected = cursor.rowcount
    print(f"   ✅ {affected} tarjeta(s) actualizada(s) a tipo NORMAL")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    raise

try:
    # Crear índice para búsquedas rápidas
    print("\n3. Creando índice para tipo de autorización...")
    cursor.execute("""
        CREATE INDEX IDX_Tarjetas_Tipo_Autorizacion 
        ON tarjetas(Tipo_Autorizacion, Estado)
    """)
    print("   ✅ Índice creado exitosamente")
    
except Exception as e:
    if "Duplicate key name" in str(e):
        print("   ⚠️ El índice ya existe (OK)")
    else:
        print(f"   ❌ Error: {e}")
        # No es crítico, continuar

# Verificar estructura
print("\n4. Verificando estructura de la columna...")
cursor.execute("DESCRIBE tarjetas")
columns = cursor.fetchall()
for col in columns:
    if col[0] == 'Tipo_Autorizacion':
        print(f"   ✅ {col[0]}: {col[1]} {col[2]} {col[3]}")
        break

# Mostrar resumen
print("\n5. Resumen de tarjetas por tipo:")
cursor.execute("""
    SELECT 
        Tipo_Autorizacion,
        COUNT(*) as Total,
        SUM(CASE WHEN Estado IN ('ACTIVA', 'Activa') THEN 1 ELSE 0 END) as Activas
    FROM tarjetas
    GROUP BY Tipo_Autorizacion
""")
resumen = cursor.fetchall()
for r in resumen:
    tipo = r[0] if r[0] else "NULL"
    print(f"   {tipo}: {r[1]} total ({r[2]} activas)")

print("\n" + "=" * 70)
print("✅ MIGRACIÓN COMPLETADA")
print("=" * 70)
print("\nPróximos pasos:")
print("1. Configurar una tarjeta como SUPERVISOR en el admin")
print("2. Ir a: http://127.0.0.1:8000/admin/gestion/tarjeta/")
print("3. Editar una tarjeta y establecer:")
print("   - Tipo_Autorizacion: SUPERVISOR")
print("   - Estado: ACTIVA")
print("4. Asegurar que el responsable sea un empleado con rol autorizado")
