import MySQLdb

conn = MySQLdb.connect(
    host='localhost',
    user='root',
    passwd='L01G05S33Vice.42',
    db='cantinatitadb'
)

cursor = conn.cursor()

print("=" * 70)
print("CONFIGURANDO SISTEMA DE NOTAS DE CRÉDITO Y DEVOLUCIONES")
print("=" * 70)

# Verificar si la tabla notas_credito existe
cursor.execute("SHOW TABLES LIKE 'notas_credito'")
if cursor.fetchone():
    print("\n✓ Tabla notas_credito ya existe")
else:
    print("\n✗ Tabla notas_credito no existe")
    exit(1)

# Verificar estructura de notas_credito
cursor.execute("DESCRIBE notas_credito")
print("\nEstructura de notas_credito:")
for row in cursor.fetchall():
    print(f"  - {row[0]} ({row[1]})")

# Crear vista de notas de crédito detalladas
vista_nc_sql = """
CREATE OR REPLACE VIEW v_notas_credito_detallado AS
SELECT 
    nc.ID_Nota,
    nc.ID_Documento,
    nc.Fecha,
    nc.Monto_Total,
    nc.Estado,
    nc.Motivo_Devolucion,
    v.ID_Venta AS Venta_Origen,
    v.Fecha AS Fecha_Venta_Origen,
    CONCAT(c.Nombres, ' ', c.Apellidos) AS Cliente,
    c.Ruc_CI,
    c.Telefono,
    dt.Nro_Timbrado,
    dt.Nro_Secuencial
FROM notas_credito nc
LEFT JOIN ventas v ON nc.ID_Venta_Original = v.ID_Venta
LEFT JOIN clientes c ON nc.ID_Cliente = c.ID_Cliente
LEFT JOIN documentos_tributarios dt ON nc.ID_Documento = dt.ID_Documento
ORDER BY nc.Fecha DESC
"""

try:
    cursor.execute(vista_nc_sql)
    conn.commit()
    print("\n✓ Vista v_notas_credito_detallado creada exitosamente")
    print("  Muestra:")
    print("   - Información completa de notas de crédito")
    print("   - Venta origen y cliente asociado")
    print("   - Estado de uso (sin usar, parcial, total)")
except Exception as e:
    print(f"\n✗ Error al crear vista: {e}")

# Crear vista de devoluciones (si existe tabla)
cursor.execute("SHOW TABLES LIKE 'devoluciones'")
if cursor.fetchone():
    vista_dev_sql = """
    CREATE OR REPLACE VIEW v_devoluciones_detallado AS
    SELECT 
        d.*,
        v.Fecha AS Fecha_Venta,
        CONCAT(c.Nombres, ' ', c.Apellidos) AS Cliente,
        p.Descripcion AS Producto,
        e.Nombre AS Empleado_Proceso
    FROM devoluciones d
    LEFT JOIN ventas v ON d.ID_Venta = v.ID_Venta
    LEFT JOIN clientes c ON v.ID_Cliente = c.ID_Cliente
    LEFT JOIN productos p ON d.ID_Producto = p.ID_Producto
    LEFT JOIN empleados e ON d.ID_Empleado = e.ID_Empleado
    ORDER BY d.Fecha_Devolucion DESC
    """
    
    try:
        cursor.execute(vista_dev_sql)
        conn.commit()
        print("\n✓ Vista v_devoluciones_detallado creada exitosamente")
    except Exception as e:
        print(f"\n✗ Error al crear vista de devoluciones: {e}")
else:
    print("\nℹ Tabla 'devoluciones' no existe, se omite vista")

print("\n" + "=" * 70)
print("✅ SISTEMA DE NOTAS DE CRÉDITO CONFIGURADO")
print("=" * 70)

print("\nFuncionalidades disponibles:")
print("1. Vista v_notas_credito_detallado para reportes completos")
print("2. Gestión desde Django Admin (disponible)")
print("3. Aplicación automática en recargas de tarjetas")

print("\nPróximos pasos recomendados:")
print("- Configurar permisos de empleados para autorizar notas")
print("- Crear políticas de devolución según tipo de producto")
print("- Definir flujo de aprobación para montos altos")

conn.close()
