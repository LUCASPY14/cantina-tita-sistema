import MySQLdb
import sys

# Conexión a MySQL
conn = MySQLdb.connect(
    host='localhost',
    user='root',
    passwd='L01G05S33Vice.42',
    db='cantinatitadb'
)

cursor = conn.cursor()

print("=" * 70)
print("MIGRACIÓN: Adaptación Módulo de Almuerzos")
print("=" * 70)

try:
    # ============================================================================
    # 1. CREAR TABLA: tipos_almuerzo
    # ============================================================================
    print("\n[1/9] Creando tabla tipos_almuerzo...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tipos_almuerzo (
            ID_Tipo_Almuerzo INT AUTO_INCREMENT PRIMARY KEY,
            Nombre VARCHAR(100) NOT NULL,
            Descripcion TEXT,
            Precio_Unitario DECIMAL(10,2) NOT NULL,
            Fecha_Creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            Activo TINYINT(1) DEFAULT 1,
            
            INDEX idx_activo (Activo)
        ) ENGINE=InnoDB COMMENT='Catálogo de tipos de almuerzo con precios individuales'
    """)
    conn.commit()
    print("✅ Tabla tipos_almuerzo creada")
    
    # Insertar datos de ejemplo
    print("\n[2/9] Insertando tipos de almuerzo...")
    cursor.execute("""
        INSERT IGNORE INTO tipos_almuerzo (Nombre, Descripcion, Precio_Unitario) VALUES
        ('Almuerzo Completo', 'Almuerzo completo con entrada, plato principal, postre y bebida', 30000.00),
        ('Almuerzo Básico', 'Plato principal y bebida', 20000.00),
        ('Almuerzo Vegetariano', 'Almuerzo completo opción vegetariana', 28000.00),
        ('Almuerzo Especial', 'Menú especial del día', 35000.00)
    """)
    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM tipos_almuerzo")
    count = cursor.fetchone()[0]
    print(f"✅ Tipos de almuerzo insertados: {count} registros")
    
    # ============================================================================
    # 2. MODIFICAR TABLA: registro_consumo_almuerzo
    # ============================================================================
    print("\n[3/9] Modificando tabla registro_consumo_almuerzo...")
    
    # Agregar Nro_Tarjeta
    try:
        cursor.execute("""
            ALTER TABLE registro_consumo_almuerzo 
            ADD COLUMN Nro_Tarjeta VARCHAR(20) NULL AFTER ID_Hijo
        """)
        conn.commit()
        print("  ✅ Columna Nro_Tarjeta agregada")
    except MySQLdb.OperationalError as e:
        if 'Duplicate column name' in str(e):
            print("  ℹ️  Columna Nro_Tarjeta ya existe")
        else:
            raise
    
    # Agregar FK Nro_Tarjeta
    try:
        cursor.execute("""
            ALTER TABLE registro_consumo_almuerzo
            ADD CONSTRAINT fk_registro_tarjeta 
                FOREIGN KEY (Nro_Tarjeta) REFERENCES tarjetas(Nro_Tarjeta) 
                ON UPDATE CASCADE
        """)
        conn.commit()
        print("  ✅ FK Nro_Tarjeta configurada")
    except MySQLdb.OperationalError as e:
        if 'Duplicate foreign key' in str(e) or 'already exists' in str(e):
            print("  ℹ️  FK Nro_Tarjeta ya existe")
        else:
            raise
    
    # Agregar ID_Tipo_Almuerzo
    try:
        cursor.execute("""
            ALTER TABLE registro_consumo_almuerzo
            ADD COLUMN ID_Tipo_Almuerzo INT NULL AFTER Nro_Tarjeta
        """)
        conn.commit()
        print("  ✅ Columna ID_Tipo_Almuerzo agregada")
    except MySQLdb.OperationalError as e:
        if 'Duplicate column name' in str(e):
            print("  ℹ️  Columna ID_Tipo_Almuerzo ya existe")
        else:
            raise
    
    # Agregar FK ID_Tipo_Almuerzo
    try:
        cursor.execute("""
            ALTER TABLE registro_consumo_almuerzo
            ADD CONSTRAINT fk_registro_tipo_almuerzo
                FOREIGN KEY (ID_Tipo_Almuerzo) REFERENCES tipos_almuerzo(ID_Tipo_Almuerzo)
        """)
        conn.commit()
        print("  ✅ FK ID_Tipo_Almuerzo configurada")
    except MySQLdb.OperationalError as e:
        if 'Duplicate foreign key' in str(e) or 'already exists' in str(e):
            print("  ℹ️  FK ID_Tipo_Almuerzo ya existe")
        else:
            raise
    
    # Agregar Costo_Almuerzo
    try:
        cursor.execute("""
            ALTER TABLE registro_consumo_almuerzo
            ADD COLUMN Costo_Almuerzo DECIMAL(10,2) NULL AFTER ID_Tipo_Almuerzo
        """)
        conn.commit()
        print("  ✅ Columna Costo_Almuerzo agregada")
    except MySQLdb.OperationalError as e:
        if 'Duplicate column name' in str(e):
            print("  ℹ️  Columna Costo_Almuerzo ya existe")
        else:
            raise
    
    # Agregar Marcado_En_Cuenta
    try:
        cursor.execute("""
            ALTER TABLE registro_consumo_almuerzo
            ADD COLUMN Marcado_En_Cuenta TINYINT(1) DEFAULT 0 AFTER Costo_Almuerzo
        """)
        conn.commit()
        print("  ✅ Columna Marcado_En_Cuenta agregada")
    except MySQLdb.OperationalError as e:
        if 'Duplicate column name' in str(e):
            print("  ℹ️  Columna Marcado_En_Cuenta ya existe")
        else:
            raise
    
    # Agregar índice
    try:
        cursor.execute("""
            ALTER TABLE registro_consumo_almuerzo
            ADD INDEX idx_marcado (Marcado_En_Cuenta, Fecha_Consumo)
        """)
        conn.commit()
        print("  ✅ Índice idx_marcado agregado")
    except MySQLdb.OperationalError as e:
        if 'Duplicate key name' in str(e):
            print("  ℹ️  Índice idx_marcado ya existe")
        else:
            raise
    
    # Hacer ID_Suscripcion opcional
    cursor.execute("""
        ALTER TABLE registro_consumo_almuerzo
        MODIFY COLUMN ID_Suscripcion BIGINT NULL
    """)
    conn.commit()
    print("  ✅ ID_Suscripcion ahora es opcional")
    
    # ============================================================================
    # 3. CREAR TABLA: cuentas_almuerzo_mensual
    # ============================================================================
    print("\n[4/9] Creando tabla cuentas_almuerzo_mensual...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cuentas_almuerzo_mensual (
            ID_Cuenta BIGINT AUTO_INCREMENT PRIMARY KEY,
            ID_Hijo INT NOT NULL,
            Anio INT NOT NULL,
            Mes TINYINT NOT NULL CHECK (Mes BETWEEN 1 AND 12),
            Cantidad_Almuerzos INT NOT NULL DEFAULT 0,
            Monto_Total DECIMAL(10,2) NOT NULL DEFAULT 0,
            Forma_Cobro ENUM('CONTADO_ANTICIPADO', 'CREDITO_MENSUAL') NOT NULL,
            Monto_Pagado DECIMAL(10,2) NOT NULL DEFAULT 0,
            Estado ENUM('PENDIENTE', 'PARCIAL', 'PAGADO') NOT NULL DEFAULT 'PENDIENTE',
            Fecha_Generacion DATE NOT NULL,
            Fecha_Actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            Observaciones TEXT,
            
            FOREIGN KEY (ID_Hijo) REFERENCES hijos(ID_Hijo),
            UNIQUE KEY uk_cuenta_mes (ID_Hijo, Anio, Mes),
            INDEX idx_estado (Estado),
            INDEX idx_fecha_gen (Fecha_Generacion)
        ) ENGINE=InnoDB COMMENT='Cuentas mensuales de almuerzo por estudiante'
    """)
    conn.commit()
    print("✅ Tabla cuentas_almuerzo_mensual creada")
    
    # ============================================================================
    # 4. CREAR TABLA: pagos_cuentas_almuerzo
    # ============================================================================
    print("\n[5/9] Creando tabla pagos_cuentas_almuerzo...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pagos_cuentas_almuerzo (
            ID_Pago BIGINT AUTO_INCREMENT PRIMARY KEY,
            ID_Cuenta BIGINT NOT NULL,
            Fecha_Pago DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            Medio_Pago ENUM('EFECTIVO', 'DEBITO', 'CREDITO', 'TRANSFERENCIA', 'OTRO') NOT NULL,
            Monto DECIMAL(10,2) NOT NULL,
            Referencia VARCHAR(50),
            Observaciones TEXT,
            ID_Empleado_Registro INT,
            
            FOREIGN KEY (ID_Cuenta) REFERENCES cuentas_almuerzo_mensual(ID_Cuenta),
            FOREIGN KEY (ID_Empleado_Registro) REFERENCES empleados(ID_Empleado),
            INDEX idx_fecha_pago (Fecha_Pago),
            INDEX idx_cuenta (ID_Cuenta)
        ) ENGINE=InnoDB COMMENT='Pagos de cuentas de almuerzo (independiente de tarjeta)'
    """)
    conn.commit()
    print("✅ Tabla pagos_cuentas_almuerzo creada")
    
    # ============================================================================
    # 5. CREAR VISTAS
    # ============================================================================
    print("\n[6/9] Creando vista v_almuerzos_diarios...")
    cursor.execute("DROP VIEW IF EXISTS v_almuerzos_diarios")
    cursor.execute("""
        CREATE VIEW v_almuerzos_diarios AS
        SELECT 
            rca.ID_Registro_Consumo,
            rca.Fecha_Consumo,
            rca.Hora_Registro,
            h.ID_Hijo,
            CONCAT(h.Nombre, ' ', h.Apellido) AS Estudiante,
            c.Nombres AS Responsable_Nombre,
            c.Apellidos AS Responsable_Apellido,
            rca.Nro_Tarjeta,
            ta.Nombre AS Tipo_Almuerzo,
            ta.Descripcion AS Descripcion_Almuerzo,
            rca.Costo_Almuerzo,
            rca.Marcado_En_Cuenta,
            CASE 
                WHEN rca.ID_Suscripcion IS NOT NULL THEN 'PLAN'
                ELSE 'ESPORADICO'
            END AS Origen,
            rca.ID_Suscripcion
        FROM registro_consumo_almuerzo rca
        INNER JOIN hijos h ON rca.ID_Hijo = h.ID_Hijo
        INNER JOIN clientes c ON h.ID_Cliente_Responsable = c.ID_Cliente
        LEFT JOIN tipos_almuerzo ta ON rca.ID_Tipo_Almuerzo = ta.ID_Tipo_Almuerzo
    """)
    conn.commit()
    print("✅ Vista v_almuerzos_diarios creada")
    
    print("\n[7/9] Creando vista v_cuentas_almuerzo_detallado...")
    cursor.execute("DROP VIEW IF EXISTS v_cuentas_almuerzo_detallado")
    cursor.execute("""
        CREATE VIEW v_cuentas_almuerzo_detallado AS
        SELECT 
            cam.ID_Cuenta,
            cam.ID_Hijo,
            CONCAT(h.Nombre, ' ', h.Apellido) AS Estudiante,
            c.Nombres AS Responsable_Nombre,
            c.Apellidos AS Responsable_Apellido,
            c.Telefono AS Responsable_Telefono,
            cam.Anio,
            cam.Mes,
            cam.Cantidad_Almuerzos,
            cam.Monto_Total,
            cam.Forma_Cobro,
            cam.Monto_Pagado,
            (cam.Monto_Total - cam.Monto_Pagado) AS Saldo_Pendiente,
            cam.Estado,
            cam.Fecha_Generacion,
            cam.Fecha_Actualizacion,
            COUNT(pca.ID_Pago) AS Cantidad_Pagos
        FROM cuentas_almuerzo_mensual cam
        INNER JOIN hijos h ON cam.ID_Hijo = h.ID_Hijo
        INNER JOIN clientes c ON h.ID_Cliente_Responsable = c.ID_Cliente
        LEFT JOIN pagos_cuentas_almuerzo pca ON cam.ID_Cuenta = pca.ID_Cuenta
        GROUP BY cam.ID_Cuenta
    """)
    conn.commit()
    print("✅ Vista v_cuentas_almuerzo_detallado creada")
    
    print("\n[8/9] Creando vista v_reporte_mensual_separado...")
    cursor.execute("DROP VIEW IF EXISTS v_reporte_mensual_separado")
    cursor.execute("""
        CREATE VIEW v_reporte_mensual_separado AS
        SELECT 
            h.ID_Hijo,
            CONCAT(h.Nombre, ' ', h.Apellido) AS Estudiante,
            t.Nro_Tarjeta,
            t.Saldo_Actual AS Saldo_Tarjeta_Actual,
            
            COALESCE(SUM(CASE 
                WHEN YEAR(rca.Fecha_Consumo) = YEAR(CURDATE()) 
                 AND MONTH(rca.Fecha_Consumo) = MONTH(CURDATE())
                THEN 1 ELSE 0 
            END), 0) AS Almuerzos_Mes_Actual,
            
            COALESCE(SUM(CASE 
                WHEN YEAR(rca.Fecha_Consumo) = YEAR(CURDATE()) 
                 AND MONTH(rca.Fecha_Consumo) = MONTH(CURDATE())
                THEN rca.Costo_Almuerzo ELSE 0 
            END), 0) AS Total_Almuerzos_Mes,
            
            COALESCE(SUM(CASE 
                WHEN YEAR(ct.Fecha_Consumo) = YEAR(CURDATE()) 
                 AND MONTH(ct.Fecha_Consumo) = MONTH(CURDATE())
                THEN ct.Monto_Consumido ELSE 0 
            END), 0) AS Consumos_Tarjeta_Mes,
            
            COALESCE(SUM(CASE 
                WHEN YEAR(cs.Fecha_Carga) = YEAR(CURDATE()) 
                 AND MONTH(cs.Fecha_Carga) = MONTH(CURDATE())
                THEN cs.Monto_Cargado ELSE 0 
            END), 0) AS Cargas_Tarjeta_Mes
            
        FROM hijos h
        LEFT JOIN tarjetas t ON h.ID_Hijo = t.ID_Hijo
        LEFT JOIN registro_consumo_almuerzo rca ON h.ID_Hijo = rca.ID_Hijo
        LEFT JOIN consumos_tarjeta ct ON t.Nro_Tarjeta = ct.Nro_Tarjeta
        LEFT JOIN cargas_saldo cs ON t.Nro_Tarjeta = cs.Nro_Tarjeta
        WHERE h.Activo = 1
        GROUP BY h.ID_Hijo, t.Nro_Tarjeta, t.Saldo_Actual
    """)
    conn.commit()
    print("✅ Vista v_reporte_mensual_separado creada")
    
    # ============================================================================
    # 6. ÍNDICES ADICIONALES
    # ============================================================================
    print("\n[9/9] Agregando índices adicionales...")
    try:
        cursor.execute("""
            ALTER TABLE registro_consumo_almuerzo 
            ADD INDEX idx_fecha_hijo (Fecha_Consumo, ID_Hijo)
        """)
        conn.commit()
        print("  ✅ Índice idx_fecha_hijo agregado")
    except MySQLdb.OperationalError as e:
        if 'Duplicate key name' in str(e):
            print("  ℹ️  Índice idx_fecha_hijo ya existe")
        else:
            raise
    
    try:
        cursor.execute("""
            ALTER TABLE cuentas_almuerzo_mensual
            ADD INDEX idx_anio_mes (Anio, Mes)
        """)
        conn.commit()
        print("  ✅ Índice idx_anio_mes agregado")
    except MySQLdb.OperationalError as e:
        if 'Duplicate key name' in str(e):
            print("  ℹ️  Índice idx_anio_mes ya existe")
        else:
            raise
    
    # ============================================================================
    # RESUMEN FINAL
    # ============================================================================
    print("\n" + "=" * 70)
    print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
    print("=" * 70)
    
    cursor.execute("SELECT COUNT(*) FROM tipos_almuerzo")
    tipos = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM cuentas_almuerzo_mensual")
    cuentas = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM pagos_cuentas_almuerzo")
    pagos = cursor.fetchone()[0]
    
    print(f"""
Resumen de tablas:
  - tipos_almuerzo: {tipos} registros
  - cuentas_almuerzo_mensual: {cuentas} registros
  - pagos_cuentas_almuerzo: {pagos} registros

Vistas creadas:
  - v_almuerzos_diarios
  - v_cuentas_almuerzo_detallado
  - v_reporte_mensual_separado
    """)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    conn.rollback()
    sys.exit(1)
finally:
    cursor.close()
    conn.close()

print("Conexión cerrada.")
