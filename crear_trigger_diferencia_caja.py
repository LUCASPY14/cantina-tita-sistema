import MySQLdb

# Conectar a la base de datos
conn = MySQLdb.connect(
    host='localhost',
    user='root',
    password='L01G05S33Vice.42',
    database='cantinatitadb'
)

cursor = conn.cursor()

print("=" * 80)
print("CREANDO TRIGGER PARA CALCULAR DIFERENCIA DE CAJA")
print("=" * 80)

# 1. Eliminar trigger si existe
print("\n1. Eliminando trigger anterior (si existe)...")
try:
    cursor.execute("DROP TRIGGER IF EXISTS trg_calcular_diferencia_caja")
    conn.commit()
    print("✓ Trigger anterior eliminado")
except Exception as e:
    print(f"Info: {e}")

# 2. Crear nuevo trigger
print("\n2. Creando trigger para calcular diferencia automáticamente...")

trigger_sql = """
CREATE TRIGGER trg_calcular_diferencia_caja
BEFORE UPDATE ON cierres_caja
FOR EACH ROW
BEGIN
    DECLARE total_esperado DECIMAL(10,2);
    
    -- Si se está registrando el cierre (Monto_Contado_Fisico no es NULL)
    IF NEW.Monto_Contado_Fisico IS NOT NULL AND OLD.Monto_Contado_Fisico IS NULL THEN
        
        -- Calcular total esperado: Monto inicial + Suma de pagos en efectivo de esta caja
        SELECT NEW.Monto_Inicial + IFNULL(SUM(pv.Monto_Aplicado), 0)
        INTO total_esperado
        FROM pagos_venta pv
        JOIN medios_pago mp ON pv.ID_Medio_Pago = mp.ID_Medio_Pago
        WHERE pv.ID_Cierre = NEW.ID_Cierre
          AND mp.Descripcion = 'EFECTIVO';
        
        -- Calcular diferencia: Monto contado - Monto esperado
        SET NEW.Diferencia_Efectivo = NEW.Monto_Contado_Fisico - total_esperado;
        
    END IF;
END
"""

try:
    cursor.execute(trigger_sql)
    conn.commit()
    print("✓ Trigger creado correctamente")
except Exception as e:
    print(f"✗ Error: {e}")

# 3. Verificar trigger creado
print("\n3. Verificando trigger...")
cursor.execute("""
    SELECT TRIGGER_NAME, EVENT_MANIPULATION, ACTION_TIMING, EVENT_OBJECT_TABLE
    FROM information_schema.TRIGGERS
    WHERE TRIGGER_SCHEMA = 'cantinatitadb'
    AND TRIGGER_NAME = 'trg_calcular_diferencia_caja'
""")
trigger = cursor.fetchone()

if trigger:
    print(f"✓ Trigger activo: {trigger[0]}")
    print(f"  Evento: {trigger[2]} {trigger[1]} en tabla {trigger[3]}")
else:
    print("✗ Trigger no encontrado")

# 4. Verificar cierre de caja actual
print("\n4. Estado del cierre de caja actual:")
cursor.execute("""
    SELECT c.ID_Cierre, c.Monto_Inicial, c.Monto_Contado_Fisico, c.Diferencia_Efectivo,
           DATE_FORMAT(c.Fecha_Hora_Apertura, '%d/%m/%Y %H:%i') as Apertura,
           DATE_FORMAT(c.Fecha_Hora_Cierre, '%d/%m/%Y %H:%i') as Cierre,
           IFNULL(SUM(pv.Monto_Aplicado), 0) as Total_Efectivo
    FROM cierres_caja c
    LEFT JOIN pagos_venta pv ON c.ID_Cierre = pv.ID_Cierre
    LEFT JOIN medios_pago mp ON pv.ID_Medio_Pago = mp.ID_Medio_Pago AND mp.Descripcion = 'EFECTIVO'
    WHERE c.ID_Cierre = 1
    GROUP BY c.ID_Cierre
""")
cierre = cursor.fetchone()

if cierre:
    print(f"\nCierre ID: {cierre[0]}")
    print(f"  Apertura: {cierre[4]}")
    print(f"  Cierre: {cierre[5] if cierre[5] else 'Pendiente'}")
    print(f"  Monto inicial: Gs. {cierre[1]:,.2f}")
    print(f"  Pagos efectivo: Gs. {cierre[6]:,.2f}")
    print(f"  Total esperado: Gs. {cierre[1] + cierre[6]:,.2f}")
    print(f"  Monto contado: {('Gs. ' + format(cierre[2], ',.2f')) if cierre[2] else 'Sin contar'}")
    print(f"  Diferencia: {('Gs. ' + format(cierre[3], ',.2f')) if cierre[3] is not None else 'Sin calcular'}")

cursor.close()
conn.close()

print("\n" + "=" * 80)
print("✅ TRIGGER CREADO EXITOSAMENTE")
print("=" * 80)
print("\nAhora cuando edites el cierre de caja:")
print("1. Ve a: http://localhost:8000/admin/gestion/cierrescaja/1/change/")
print("2. Completa 'Monto contado fisico' con el efectivo contado")
print("3. Guarda")
print("4. La 'Diferencia efectivo' se calculará automáticamente")
