import MySQLdb

conn = MySQLdb.connect(
    host='localhost',
    user='root',
    passwd='L01G05S33Vice.42',
    db='cantinatitadb'
)

cursor = conn.cursor()

print("=" * 70)
print("CREANDO TABLA consumos_tarjeta")
print("=" * 70)

# Crear tabla consumos_tarjeta
create_table_sql = """
CREATE TABLE IF NOT EXISTS consumos_tarjeta (
    ID_Consumo BIGINT AUTO_INCREMENT PRIMARY KEY,
    Nro_Tarjeta VARCHAR(20) NOT NULL,
    Fecha_Consumo DATETIME NOT NULL,
    Monto_Consumido DECIMAL(10,2) NOT NULL,
    Detalle VARCHAR(200),
    Saldo_Anterior DECIMAL(10,2) NOT NULL,
    Saldo_Posterior DECIMAL(10,2) NOT NULL,
    ID_Empleado_Registro INT,
    FOREIGN KEY (Nro_Tarjeta) REFERENCES tarjetas(Nro_Tarjeta) ON UPDATE CASCADE,
    FOREIGN KEY (ID_Empleado_Registro) REFERENCES empleados(ID_Empleado),
    INDEX idx_tarjeta_fecha (Nro_Tarjeta, Fecha_Consumo),
    INDEX idx_fecha (Fecha_Consumo)
)
"""

try:
    cursor.execute(create_table_sql)
    conn.commit()
    print("\n✓ Tabla consumos_tarjeta creada exitosamente")
    print("  Columnas:")
    print("   - ID_Consumo (PK)")
    print("   - Nro_Tarjeta (FK a tarjetas)")
    print("   - Fecha_Consumo")
    print("   - Monto_Consumido")
    print("   - Detalle")
    print("   - Saldo_Anterior")
    print("   - Saldo_Posterior")
    print("   - ID_Empleado_Registro (FK a empleados)")
except Exception as e:
    print(f"\n✗ Error al crear tabla: {e}")
    conn.rollback()
    exit(1)

print("\n" + "=" * 70)
print("CREANDO TRIGGER PARA ACTUALIZAR SALDO AUTOMÁTICAMENTE")
print("=" * 70)

# Eliminar trigger si existe
cursor.execute("DROP TRIGGER IF EXISTS trg_actualizar_saldo_tarjeta")

# Crear trigger para actualizar saldo
trigger_sql = """
CREATE TRIGGER trg_actualizar_saldo_tarjeta
BEFORE INSERT ON consumos_tarjeta
FOR EACH ROW
BEGIN
    DECLARE v_saldo_actual DECIMAL(10,2);
    
    -- Obtener saldo actual de la tarjeta
    SELECT Saldo_Actual INTO v_saldo_actual
    FROM tarjetas
    WHERE Nro_Tarjeta = NEW.Nro_Tarjeta;
    
    -- Verificar que hay saldo suficiente
    IF v_saldo_actual < NEW.Monto_Consumido THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Saldo insuficiente en la tarjeta';
    END IF;
    
    -- Establecer saldos
    SET NEW.Saldo_Anterior = v_saldo_actual;
    SET NEW.Saldo_Posterior = v_saldo_actual - NEW.Monto_Consumido;
    
    -- Actualizar saldo en la tarjeta
    UPDATE tarjetas
    SET Saldo_Actual = NEW.Saldo_Posterior
    WHERE Nro_Tarjeta = NEW.Nro_Tarjeta;
END
"""

try:
    cursor.execute(trigger_sql)
    conn.commit()
    print("\n✓ Trigger trg_actualizar_saldo_tarjeta creado exitosamente")
    print("  Funcionalidad:")
    print("   - Valida saldo suficiente antes de consumo")
    print("   - Registra saldo anterior y posterior automáticamente")
    print("   - Actualiza saldo de la tarjeta automáticamente")
except Exception as e:
    print(f"\n✗ Error al crear trigger: {e}")
    conn.rollback()
    exit(1)

print("\n" + "=" * 70)
print("✅ SISTEMA DE CONSUMOS CONFIGURADO CORRECTAMENTE")
print("=" * 70)

print("\nAhora puedes:")
print("1. Registrar consumos con tarjeta fácilmente")
print("2. El saldo se actualiza automáticamente")
print("3. Se valida que haya saldo suficiente")
print("4. Se mantiene historial completo de consumos")

conn.close()
