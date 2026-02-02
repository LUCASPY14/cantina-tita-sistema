import MySQLdb

conn = MySQLdb.connect(
    host='localhost',
    user='root',
    passwd='L01G05S33Vice.42',
    db='cantinatitadb'
)

cursor = conn.cursor()

print("Corrigiendo trigger trg_carga_saldo_genera_venta...")

# Eliminar trigger anterior
cursor.execute("DROP TRIGGER IF EXISTS trg_carga_saldo_genera_venta")

# Crear trigger corregido
trigger_sql = """
CREATE TRIGGER trg_carga_saldo_genera_venta
AFTER INSERT ON cargas_saldo
FOR EACH ROW
BEGIN
    DECLARE v_id_producto INT;
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
    WHERE DATE(Fecha_Hora_Apertura) = DATE(NEW.Fecha_Carga)
      AND Fecha_Hora_Cierre IS NULL
    ORDER BY Fecha_Hora_Apertura DESC
    LIMIT 1;
    
    -- Solo continuar si se encontraron los datos necesarios
    IF v_id_producto IS NOT NULL AND v_id_cliente IS NOT NULL AND v_id_tipo_pago IS NOT NULL THEN
        
        -- Crear venta SIN documento tributario (las recargas son prepagos)
        INSERT INTO ventas (
            ID_Cliente,
            ID_Tipo_Pago,
            Fecha,
            Tipo_Venta,
            Monto_Total,
            Estado
        ) VALUES (
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
    print("✓ Trigger corregido exitosamente")
    print("  - Columna corregida: Fecha_Apertura → Fecha_Hora_Apertura")
except Exception as e:
    print(f"✗ Error: {e}")
    conn.rollback()

conn.close()
