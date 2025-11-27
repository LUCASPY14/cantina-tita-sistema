import MySQLdb

conn = MySQLdb.connect(
    host='localhost',
    user='root',
    passwd='L01G05S33Vice.42',
    db='cantinatitadb'
)

cursor = conn.cursor()

print("Configurando timbrado para recargas...")

# Verificar si existe timbrado para recargas
cursor.execute("SELECT ID_Timbrado FROM timbrados WHERE Descripcion = 'Recargas - Sin timbrado'")
timbrado = cursor.fetchone()

if not timbrado:
    cursor.execute("""
        INSERT INTO timbrados (
            Nro_Timbrado,
            Descripcion,
            Fecha_Inicio,
            Fecha_Fin,
            Activo
        ) VALUES (
            '0',
            'Recargas - Sin timbrado',
            '2025-01-01',
            '2099-12-31',
            1
        )
    """)
    conn.commit()
    cursor.execute("SELECT LAST_INSERT_ID()")
    id_timbrado = cursor.fetchone()[0]
    print(f"✓ Timbrado creado (ID: {id_timbrado})")
else:
    id_timbrado = timbrado[0]
    print(f"✓ Timbrado ya existe (ID: {id_timbrado})")

print("\nActualizando trigger con documento tributario simplificado...")

# Eliminar trigger anterior
cursor.execute("DROP TRIGGER IF EXISTS trg_carga_saldo_genera_venta")

# Crear trigger final
trigger_sql = f"""
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
    DECLARE v_siguiente_secuencial INT;
    
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
    
    -- Obtener siguiente número secuencial para recargas
    SELECT COALESCE(MAX(Nro_Secuencial), 0) + 1 INTO v_siguiente_secuencial
    FROM documentos_tributarios
    WHERE Nro_Timbrado = {id_timbrado};
    
    -- Solo continuar si se encontraron los datos necesarios
    IF v_id_producto IS NOT NULL AND v_id_cliente IS NOT NULL AND v_id_tipo_pago IS NOT NULL THEN
        
        -- Crear documento tributario simplificado
        INSERT INTO documentos_tributarios (
            Nro_Timbrado,
            Nro_Secuencial,
            Fecha_Emision,
            Monto_Total,
            Monto_Exento
        ) VALUES (
            {id_timbrado},
            v_siguiente_secuencial,
            NEW.Fecha_Carga,
            NEW.Monto_Cargado,
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
    print("✓ Trigger creado exitosamente con documentos tributarios")
except Exception as e:
    print(f"✗ Error: {e}")
    conn.rollback()

conn.close()
