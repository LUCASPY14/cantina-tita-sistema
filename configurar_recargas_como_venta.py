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
print("CONFIGURACIÓN: RECARGAS DE TARJETA COMO VENTAS")
print("=" * 70)

# 1. Crear categoría "Servicios" si no existe
print("\n1. Verificando categoría 'Servicios'...")
cursor.execute("""
    SELECT ID_Categoria FROM categorias WHERE Nombre = 'Servicios'
""")
categoria = cursor.fetchone()

if not categoria:
    cursor.execute("""
        INSERT INTO categorias (Nombre, Activo)
        VALUES ('Servicios', 1)
    """)
    conn.commit()
    cursor.execute("SELECT LAST_INSERT_ID()")
    id_categoria = cursor.fetchone()[0]
    print(f"   ✓ Categoría 'Servicios' creada (ID: {id_categoria})")
else:
    id_categoria = categoria[0]
    print(f"   ✓ Categoría 'Servicios' ya existe (ID: {id_categoria})")

# 2. Crear producto "Recarga de Tarjeta Estudiantil"
print("\n2. Verificando producto 'Recarga de Tarjeta'...")
cursor.execute("""
    SELECT ID_Producto FROM productos WHERE Codigo = 'REC-TAR'
""")
producto = cursor.fetchone()

if not producto:
    # Obtener ID de impuesto exento (0%)
    cursor.execute("""
        SELECT ID_Impuesto FROM impuestos WHERE Porcentaje = 0 AND Activo = 1
    """)
    impuesto = cursor.fetchone()
    if not impuesto:
        cursor.execute("""
            INSERT INTO impuestos (Nombre_Impuesto, Porcentaje, Activo)
            VALUES ('Exento', 0, 1)
        """)
        conn.commit()
        cursor.execute("SELECT LAST_INSERT_ID()")
        id_impuesto = cursor.fetchone()[0]
    else:
        id_impuesto = impuesto[0]
    
    # Obtener ID de unidad "UNIDAD"
    cursor.execute("""
        SELECT ID_Unidad FROM unidades_medida WHERE Abreviatura = 'UN' OR Nombre = 'Unidad'
    """)
    unidad = cursor.fetchone()
    if not unidad:
        cursor.execute("""
            INSERT INTO unidades_medida (Nombre, Abreviatura)
            VALUES ('Unidad', 'UN')
        """)
        conn.commit()
        cursor.execute("SELECT LAST_INSERT_ID()")
        id_unidad = cursor.fetchone()[0]
    else:
        id_unidad = unidad[0]
    
    cursor.execute("""
        INSERT INTO productos (
            Codigo, 
            Descripcion, 
            ID_Categoria, 
            ID_Unidad, 
            ID_Impuesto,
            Stock_Minimo,
            Activo
        ) VALUES (
            'REC-TAR',
            'Recarga de Tarjeta Estudiantil',
            %s,
            %s,
            %s,
            0,
            1
        )
    """, (id_categoria, id_unidad, id_impuesto))
    conn.commit()
    
    cursor.execute("SELECT LAST_INSERT_ID()")
    id_producto = cursor.fetchone()[0]
    print(f"   ✓ Producto 'Recarga de Tarjeta' creado (ID: {id_producto})")
    print(f"   - Código: REC-TAR")
    print(f"   - Es Servicio: SÍ (no controla stock)")
    print(f"   - Impuesto: Exento (0%)")
else:
    id_producto = producto[0]
    print(f"   ✓ Producto 'Recarga de Tarjeta' ya existe (ID: {id_producto})")

# 3. Crear trigger para generar venta automática al cargar saldo
print("\n3. Creando trigger para generar venta al cargar saldo...")

# Primero eliminar si existe
cursor.execute("DROP TRIGGER IF EXISTS trg_carga_saldo_genera_venta")

trigger_sql = """
CREATE TRIGGER trg_carga_saldo_genera_venta
AFTER INSERT ON cargas_saldo
FOR EACH ROW
BEGIN
    DECLARE v_id_producto INT;
    DECLARE v_id_documento BIGINT;
    DECLARE v_id_venta BIGINT;
    DECLARE v_id_cliente INT;
    DECLARE v_id_tipo_pago INT;
    DECLARE v_id_medio_pago INT;
    DECLARE v_id_cierre BIGINT;
    
    -- Obtener ID del producto "Recarga de Tarjeta"
    SELECT ID_Producto INTO v_id_producto 
    FROM productos 
    WHERE Codigo = 'REC-TAR' 
    LIMIT 1;
    
    -- Obtener cliente origen
    SET v_id_cliente = NEW.ID_Cliente_Origen;
    
    -- Obtener ID de tipo de pago CONTADO
    SELECT ID_Tipo_Pago INTO v_id_tipo_pago 
    FROM tipos_pago 
    WHERE Descripcion = 'CONTADO' 
    LIMIT 1;
    
    -- Obtener ID de medio de pago EFECTIVO
    SELECT ID_Medio_Pago INTO v_id_medio_pago 
    FROM medios_pago 
    WHERE Descripcion = 'EFECTIVO' 
    LIMIT 1;
    
    -- Obtener cierre de caja activo del día
    SELECT ID_Cierre INTO v_id_cierre
    FROM cierres_caja
    WHERE DATE(Fecha_Apertura) = DATE(NEW.Fecha_Carga)
      AND Fecha_Cierre IS NULL
    ORDER BY Fecha_Apertura DESC
    LIMIT 1;
    
    -- Solo continuar si se encontraron los datos necesarios
    IF v_id_producto IS NOT NULL AND v_id_cliente IS NOT NULL THEN
        
        -- Crear documento tributario (sin timbrado para recargas)
        INSERT INTO documentos_tributarios (
            Fecha_Emision,
            Monto_Total,
            Monto_Gravado_10,
            Monto_IVA_10,
            Monto_Gravado_5,
            Monto_IVA_5,
            Monto_Exento
        ) VALUES (
            NEW.Fecha_Carga,
            NEW.Monto_Cargado,
            0,
            0,
            0,
            0,
            NEW.Monto_Cargado
        );
        
        SET v_id_documento = LAST_INSERT_ID();
        
        -- Crear venta
        INSERT INTO ventas (
            ID_Documento,
            ID_Cliente,
            ID_Tipo_Pago,
            Fecha,
            Tipo_Venta,
            Monto_Total,
            Estado
        ) VALUES (
            v_id_documento,
            v_id_cliente,
            v_id_tipo_pago,
            NEW.Fecha_Carga,
            'Recarga Tarjeta',
            NEW.Monto_Cargado,
            'Completada'
        );
        
        SET v_id_venta = LAST_INSERT_ID();
        
        -- Crear detalle de venta
        INSERT INTO detalle_venta (
            ID_Venta,
            ID_Producto,
            Cantidad,
            Precio_Unitario_Neto,
            Precio_Unitario_Total,
            Subtotal_Neto,
            Subtotal_Total,
            Monto_IVA
        ) VALUES (
            v_id_venta,
            v_id_producto,
            1,
            NEW.Monto_Cargado,
            NEW.Monto_Cargado,
            NEW.Monto_Cargado,
            NEW.Monto_Cargado,
            0
        );
        
        -- Registrar pago
        IF v_id_medio_pago IS NOT NULL THEN
            INSERT INTO pagos_venta (
                ID_Venta,
                ID_Medio_Pago,
                ID_Cierre,
                Monto_Aplicado,
                Referencia_Transaccion,
                Fecha_Pago
            ) VALUES (
                v_id_venta,
                v_id_medio_pago,
                v_id_cierre,
                NEW.Monto_Cargado,
                CONCAT('Recarga Tarjeta ', NEW.Nro_Tarjeta),
                NEW.Fecha_Carga
            );
        END IF;
        
        -- Actualizar referencia en cargas_saldo
        UPDATE cargas_saldo 
        SET Referencia = CONCAT('Venta ID: ', v_id_venta)
        WHERE ID_Carga = NEW.ID_Carga;
        
    END IF;
END
"""

try:
    cursor.execute(trigger_sql)
    conn.commit()
    print("   ✓ Trigger 'trg_carga_saldo_genera_venta' creado correctamente")
    print("   - Se activa DESPUÉS de INSERT en cargas_saldo")
    print("   - Genera automáticamente:")
    print("     * Documento tributario (exento)")
    print("     * Venta con estado 'Completada'")
    print("     * Detalle de venta (producto REC-TAR)")
    print("     * Pago en efectivo")
except Exception as e:
    print(f"   ✗ Error al crear trigger: {e}")
    conn.rollback()

print("\n" + "=" * 70)
print("CONFIGURACIÓN COMPLETADA")
print("=" * 70)
print("\nAhora cuando registres una carga de saldo:")
print("1. Se creará automáticamente una VENTA")
print("2. Se generará FACTURA (exenta de IVA)")
print("3. Se registrará el PAGO en efectivo")
print("4. El efectivo ingresará a CAJA")
print("\nCuando el estudiante consuma con la tarjeta:")
print("1. NO se crea venta (ya se facturó en la recarga)")
print("2. SOLO se descuenta el saldo de la tarjeta")

conn.close()

print("\n✅ Sistema configurado correctamente")
