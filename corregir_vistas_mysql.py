"""
Script para corregir las 5 vistas MySQL con errores
"""
import mysql.connector
from mysql.connector import Error

# Configuración de conexión
config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'L01G05S33Vice.42',
    'database': 'cantinatitadb'
}

def ejecutar_sql(cursor, sql, descripcion=""):
    """Ejecuta un comando SQL y maneja errores"""
    try:
        cursor.execute(sql)
        print(f"✅ {descripcion}")
        return True
    except Error as e:
        print(f"❌ ERROR en {descripcion}: {e}")
        return False

def corregir_vistas():
    """Corrige las 5 vistas MySQL con errores"""
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        print("="*80)
        print("CORRECCIÓN DE VISTAS MYSQL CON ERRORES")
        print("="*80 + "\n")
        
        # ========================================================================
        # VISTA 1: v_resumen_silencioso_hijo
        # ========================================================================
        print("\n📊 Vista 1: v_resumen_silencioso_hijo")
        print("-" * 80)
        
        ejecutar_sql(cursor, "DROP VIEW IF EXISTS v_resumen_silencioso_hijo", 
                    "Eliminando vista antigua v_resumen_silencioso_hijo")
        
        sql_vista1 = """
        CREATE VIEW v_resumen_silencioso_hijo AS
        SELECT 
            h.ID_Hijo,
            h.Nombre,
            h.Apellido,
            h.Grado,
            t.Nro_Tarjeta,
            t.Saldo_Actual,
            t.Estado AS Estado_Tarjeta,
            c.Nombres AS Responsable_Nombres,
            c.Apellidos AS Responsable_Apellidos,
            c.Telefono AS Responsable_Telefono,
            COUNT(DISTINCT ct.ID_Consumo) AS Total_Consumos,
            COALESCE(SUM(ct.Monto_Consumido), 0) AS Total_Consumido
        FROM hijos h
        LEFT JOIN clientes c ON h.ID_Cliente_Responsable = c.ID_Cliente
        LEFT JOIN tarjetas t ON h.ID_Hijo = t.ID_Hijo
        LEFT JOIN consumos_tarjeta ct ON t.Nro_Tarjeta = ct.Nro_Tarjeta
        WHERE h.Activo = 1
        GROUP BY 
            h.ID_Hijo,
            h.Nombre,
            h.Apellido,
            h.Grado,
            t.Nro_Tarjeta,
            t.Saldo_Actual,
            t.Estado,
            c.Nombres,
            c.Apellidos,
            c.Telefono
        """
        ejecutar_sql(cursor, sql_vista1, "Creando vista v_resumen_silencioso_hijo")
        
        # ========================================================================
        # VISTA 2: v_control_asistencia
        # ========================================================================
        print("\n📊 Vista 2: v_control_asistencia")
        print("-" * 80)
        
        ejecutar_sql(cursor, "DROP VIEW IF EXISTS v_control_asistencia", 
                    "Eliminando vista antigua v_control_asistencia")
        
        sql_vista2 = """
        CREATE VIEW v_control_asistencia AS
        SELECT 
            rca.ID_Registro_Consumo AS ID_Registro,
            rca.Fecha_Consumo AS Fecha_Registro,
            rca.Hora_Registro,
            ta.Nombre AS Tipo_Almuerzo,
            h.Nombre AS Hijo_Nombre,
            h.Apellido AS Hijo_Apellido,
            h.Grado,
            c.Nombres AS Responsable_Nombres,
            c.Apellidos AS Responsable_Apellidos,
            sa.ID_Suscripcion,
            pa.Nombre_Plan,
            pa.Precio_Mensual AS Precio_Plan
        FROM registro_consumo_almuerzo rca
        INNER JOIN tipos_almuerzo ta ON rca.ID_Tipo_Almuerzo = ta.ID_Tipo_Almuerzo
        INNER JOIN suscripciones_almuerzo sa ON rca.ID_Suscripcion = sa.ID_Suscripcion
        INNER JOIN planes_almuerzo pa ON sa.ID_Plan_Almuerzo = pa.ID_Plan_Almuerzo
        INNER JOIN hijos h ON sa.ID_Hijo = h.ID_Hijo
        INNER JOIN clientes c ON h.ID_Cliente_Responsable = c.ID_Cliente
        WHERE rca.Fecha_Consumo >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        ORDER BY rca.Fecha_Consumo DESC, rca.Hora_Registro DESC
        """
        ejecutar_sql(cursor, sql_vista2, "Creando vista v_control_asistencia")
        
        # ========================================================================
        # VISTA 3: v_saldo_tarjetas_compras  
        # ========================================================================
        print("\n📊 Vista 3: v_saldo_tarjetas_compras")
        print("-" * 80)
        
        ejecutar_sql(cursor, "DROP VIEW IF EXISTS v_saldo_tarjetas_compras", 
                    "Eliminando vista antigua v_saldo_tarjetas_compras")
        
        sql_vista3 = """
        CREATE VIEW v_saldo_tarjetas_compras AS
        SELECT 
            t.Nro_Tarjeta,
            h.Nombre AS Estudiante_Nombre,
            h.Apellido AS Estudiante_Apellido,
            t.Saldo_Actual,
            t.Estado,
            COALESCE(SUM(ct.Monto_Consumido), 0) AS Total_Consumido,
            COALESCE(SUM(cs.Monto_Cargado), 0) AS Total_Cargado,
            COUNT(DISTINCT ct.ID_Consumo) AS Cantidad_Compras,
            MAX(ct.Fecha_Consumo) AS Ultima_Compra
        FROM tarjetas t
        INNER JOIN hijos h ON t.ID_Hijo = h.ID_Hijo
        LEFT JOIN consumos_tarjeta ct ON t.Nro_Tarjeta = ct.Nro_Tarjeta
        LEFT JOIN cargas_saldo cs ON t.Nro_Tarjeta = cs.Nro_Tarjeta
        GROUP BY 
            t.Nro_Tarjeta,
            h.Nombre,
            h.Apellido,
            t.Saldo_Actual,
            t.Estado
        """
        ejecutar_sql(cursor, sql_vista3, "Creando vista v_saldo_tarjetas_compras")
        
        # ========================================================================
        # VISTA 4: v_tarjetas_detalle
        # ========================================================================
        print("\n📊 Vista 4: v_tarjetas_detalle")
        print("-" * 80)
        
        ejecutar_sql(cursor, "DROP VIEW IF EXISTS v_tarjetas_detalle", 
                    "Eliminando vista antigua v_tarjetas_detalle")
        
        sql_vista4 = """
        CREATE VIEW v_tarjetas_detalle AS
        SELECT 
            t.Nro_Tarjeta,
            t.Saldo_Actual,
            t.Estado,
            t.Fecha_Vencimiento,
            t.Saldo_Alerta,
            h.ID_Hijo,
            h.Nombre AS Estudiante_Nombre,
            h.Apellido AS Estudiante_Apellido,
            h.Grado,
            h.Restricciones_Compra,
            c.ID_Cliente,
            c.Nombres AS Responsable_Nombres,
            c.Apellidos AS Responsable_Apellidos,
            c.Telefono AS Responsable_Telefono,
            c.Email AS Responsable_Email,
            CASE 
                WHEN t.Saldo_Actual <= COALESCE(t.Saldo_Alerta, 5000) THEN 'ALERTA'
                WHEN t.Estado = 'Bloqueada' THEN 'BLOQUEADA'
                WHEN t.Fecha_Vencimiento < CURDATE() THEN 'VENCIDA'
                ELSE 'NORMAL'
            END AS Nivel_Alerta
        FROM tarjetas t
        INNER JOIN hijos h ON t.ID_Hijo = h.ID_Hijo
        INNER JOIN clientes c ON h.ID_Cliente_Responsable = c.ID_Cliente
        """
        ejecutar_sql(cursor, sql_vista4, "Creando vista v_tarjetas_detalle")
        
        # ========================================================================
        # VISTA 5: v_ventas_dia
        # ========================================================================
        print("\n📊 Vista 5: v_ventas_dia")
        print("-" * 80)
        
        ejecutar_sql(cursor, "DROP VIEW IF EXISTS v_ventas_dia", 
                    "Eliminando vista antigua v_ventas_dia")
        
        sql_vista5 = """
        CREATE VIEW v_ventas_dia AS
        SELECT 
            DATE(v.Fecha) AS Fecha,
            COUNT(DISTINCT v.ID_Venta) AS Cantidad_Ventas,
            COALESCE(SUM(v.Monto_Total), 0) AS Total_Vendido,
            COALESCE(SUM(v.Saldo_Pendiente), 0) AS Total_Pendiente,
            COALESCE(SUM(v.Monto_Total - v.Saldo_Pendiente), 0) AS Total_Pagado,
            COUNT(DISTINCT v.ID_Cliente) AS Clientes_Atendidos,
            COALESCE(AVG(v.Monto_Total), 0) AS Ticket_Promedio
        FROM ventas v
        WHERE v.Fecha >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)
        GROUP BY DATE(v.Fecha)
        ORDER BY DATE(v.Fecha) DESC
        """
        ejecutar_sql(cursor, sql_vista5, "Creando vista v_ventas_dia")
        
        # Commit de todos los cambios
        conn.commit()
        
        # ========================================================================
        # VERIFICAR VISTAS
        # ========================================================================
        print("\n" + "="*80)
        print("VERIFICACIÓN DE VISTAS CORREGIDAS")
        print("="*80)
        
        vistas_corregidas = [
            'v_resumen_silencioso_hijo',
            'v_control_asistencia',
            'v_saldo_tarjetas_compras',
            'v_tarjetas_detalle',
            'v_ventas_dia'
        ]
        
        for vista in vistas_corregidas:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {vista}")
                resultado = cursor.fetchone()
                print(f"✅ {vista:35} - {resultado[0]:5} registros")
            except Error as e:
                print(f"❌ {vista:35} - ERROR: {e}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*80)
        print("✅ PROCESO COMPLETADO")
        print("="*80)
        
    except Error as e:
        print(f"\n❌ ERROR DE CONEXIÓN: {e}")

if __name__ == "__main__":
    corregir_vistas()
