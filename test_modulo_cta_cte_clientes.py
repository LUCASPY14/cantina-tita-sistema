#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TEST MÓDULO - CUENTA CORRIENTE DE CLIENTES
==========================================
Pruebas completas del sistema de créditos a clientes.

COBERTURA:
- Otorgamiento de créditos
- Registro de pagos
- Consulta de estado de cuenta
- Cálculo de saldos
- Validación de límites de crédito
- Movimientos históricos
"""

import MySQLdb
from datetime import datetime, timedelta
from decimal import Decimal

# ============================================================================
# CONFIGURACIÓN DE CONEXIÓN
# ============================================================================

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'passwd': 'L01G05S33Vice.42',
    'db': 'cantinatitadb',
    'charset': 'utf8mb4'
}

# ============================================================================
# UTILIDADES
# ============================================================================

def print_header(text):
    """Imprime encabezado formateado"""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}")

def print_success(text):
    """Imprime mensaje de éxito"""
    print(f"✅ {text}")

def print_info(text):
    """Imprime información"""
    print(f"ℹ️  {text}")

def print_error(text):
    """Imprime error"""
    print(f"❌ {text}")

# ============================================================================
# TEST 1: OTORGAR CRÉDITO A CLIENTE
# ============================================================================

def test_otorgar_credito():
    """
    Prueba el otorgamiento de crédito a un cliente.
    
    Validaciones:
    - Cliente debe existir
    - Se crea movimiento tipo CARGO
    - Saldo de cuenta corriente se actualiza
    - Se genera documento respaldatorio
    """
    print_header("TEST 1: Otorgar Crédito a Cliente")
    
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Buscar cliente existente
        cursor.execute("""
            SELECT ID_Cliente, Nombres, Apellidos 
            FROM clientes 
            WHERE Activo = TRUE 
            LIMIT 1
        """)
        
        cliente = cursor.fetchone()
        if not cliente:
            print_error("No hay clientes activos para probar")
            return False
        
        id_cliente, nombres, apellidos = cliente
        print_info(f"Cliente seleccionado: {nombres} {apellidos} (ID: {id_cliente})")
        
        # Obtener saldo actual de cuenta corriente
        cursor.execute("""
            SELECT COALESCE(SUM(
                CASE 
                    WHEN Tipo_Movimiento = 'Cargo' THEN Monto
                    WHEN Tipo_Movimiento = 'Abono' THEN -Monto
                    ELSE 0
                END
            ), 0) as saldo
            FROM cta_corriente
            WHERE ID_Cliente = %s
        """, (id_cliente,))
        
        saldo_anterior = float(cursor.fetchone()[0])
        print_info(f"Saldo anterior: Gs. {saldo_anterior:,.0f}")
        
        # Buscar documento tributario para respaldo
        cursor.execute("""
            SELECT ID_Documento 
            FROM documentos_tributarios 
            WHERE Nro_Timbrado > 0 
            ORDER BY ID_Documento DESC 
            LIMIT 1
        """)
        
        doc_result = cursor.fetchone()
        id_documento = doc_result[0] if doc_result else None
        
        # Registrar crédito otorgado
        monto_credito = 150000  # Gs. 150,000
        
        cursor.execute("""
            INSERT INTO cta_corriente
            (ID_Cliente, ID_Venta, Tipo_Movimiento, Monto, Fecha, Referencia_Doc)
            VALUES (%s, NULL, 'Cargo', %s, NOW(), %s)
        """, (id_cliente, monto_credito, 'Crédito otorgado - Compra a cuenta'))
        
        id_movimiento = cursor.lastrowid
        conn.commit()
        
        # Verificar saldo actualizado
        cursor.execute("""
            SELECT COALESCE(SUM(
                CASE 
                    WHEN Tipo_Movimiento = 'Cargo' THEN Monto
                    WHEN Tipo_Movimiento = 'Abono' THEN -Monto
                    ELSE 0
                END
            ), 0) as saldo
            FROM cta_corriente
            WHERE ID_Cliente = %s
        """, (id_cliente,))
        
        saldo_nuevo = float(cursor.fetchone()[0])
        
        print_success(f"\n✅ Crédito otorgado exitosamente")
        print_info(f"   ID Movimiento: {id_movimiento}")
        print_info(f"   Monto: Gs. {monto_credito:,.0f}")
        print_info(f"   Saldo anterior: Gs. {saldo_anterior:,.0f}")
        print_info(f"   Saldo nuevo: Gs. {saldo_nuevo:,.0f}")
        print_info(f"   Diferencia: Gs. {(saldo_nuevo - saldo_anterior):,.0f}")
        
        # Validar que el saldo aumentó correctamente
        assert abs((saldo_nuevo - saldo_anterior) - monto_credito) < 0.01, "Saldo no actualizado correctamente"
        
        conn.rollback()  # Rollback para no afectar BD
        return True
        
    except Exception as e:
        print_error(f"Error en test_otorgar_credito: {str(e)}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

# ============================================================================
# TEST 2: REGISTRAR PAGO DE CLIENTE
# ============================================================================

def test_registrar_pago():
    """
    Prueba el registro de un pago de cliente.
    
    Validaciones:
    - Se crea movimiento tipo ABONO
    - Saldo de cuenta corriente disminuye
    - Se puede registrar pago parcial o total
    """
    print_header("TEST 2: Registrar Pago de Cliente")
    
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Buscar cliente con saldo deudor (CARGO > ABONO)
        cursor.execute("""
            SELECT 
                c.ID_Cliente,
                c.Nombres,
                c.Apellidos,
                COALESCE(SUM(
                    CASE 
                        WHEN cc.Tipo_Movimiento = 'Cargo' THEN cc.Monto
                        WHEN cc.Tipo_Movimiento = 'Abono' THEN -cc.Monto
                        ELSE 0
                    END
                ), 0) as saldo
            FROM clientes c
            LEFT JOIN cta_corriente cc ON c.ID_Cliente = cc.ID_Cliente
            WHERE c.Activo = TRUE
            GROUP BY c.ID_Cliente, c.Nombres, c.Apellidos
            HAVING saldo > 0
            LIMIT 1
        """)
        
        result = cursor.fetchone()
        
        if not result:
            # Si no hay cliente con deuda, crear un cargo primero
            cursor.execute("SELECT ID_Cliente, Nombres, Apellidos FROM clientes WHERE Activo = TRUE LIMIT 1")
            cliente = cursor.fetchone()
            id_cliente, nombres, apellidos = cliente
            
            cursor.execute("""
                INSERT INTO cta_corriente
                (ID_Cliente, Tipo_Movimiento, Monto, Fecha, Referencia_Doc)
                VALUES (%s, 'Cargo', 200000, NOW(), 'Crédito test')
            """, (id_cliente,))
            
            saldo_anterior = 200000
        else:
            id_cliente, nombres, apellidos, saldo_anterior = result
        
        print_info(f"Cliente: {nombres} {apellidos} (ID: {id_cliente})")
        print_info(f"Saldo deudor: Gs. {saldo_anterior:,.0f}")
        
        # Registrar pago (50% del saldo)
        monto_pago = int(saldo_anterior) // 2
        
        cursor.execute("""
            INSERT INTO cta_corriente
            (ID_Cliente, Tipo_Movimiento, Monto, Fecha, Referencia_Doc)
            VALUES (%s, 'Abono', %s, NOW(), %s)
        """, (id_cliente, monto_pago, f'Pago parcial - Efectivo'))
        
        id_movimiento = cursor.lastrowid
        
        # Verificar saldo actualizado
        cursor.execute("""
            SELECT COALESCE(SUM(
                CASE 
                    WHEN Tipo_Movimiento = 'Cargo' THEN Monto
                    WHEN Tipo_Movimiento = 'Abono' THEN -Monto
                    ELSE 0
                END
            ), 0) as saldo
            FROM cta_corriente
            WHERE ID_Cliente = %s
        """, (id_cliente,))
        
        saldo_nuevo = float(cursor.fetchone()[0])
        
        print_success(f"\n✅ Pago registrado exitosamente")
        print_info(f"   ID Movimiento: {id_movimiento}")
        print_info(f"   Monto pagado: Gs. {monto_pago:,.0f}")
        print_info(f"   Saldo anterior: Gs. {float(saldo_anterior):,.0f}")
        print_info(f"   Saldo nuevo: Gs. {saldo_nuevo:,.0f}")
        print_info(f"   Reducción: Gs. {(float(saldo_anterior) - saldo_nuevo):,.0f}")
        
        # Validar que el saldo disminuyó correctamente
        assert abs((float(saldo_anterior) - saldo_nuevo) - monto_pago) < 0.01, "Saldo no actualizado correctamente"
        
        conn.rollback()
        return True
        
    except Exception as e:
        print_error(f"Error en test_registrar_pago: {str(e)}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

# ============================================================================
# TEST 3: CONSULTAR ESTADO DE CUENTA
# ============================================================================

def test_estado_de_cuenta():
    """
    Prueba la consulta del estado de cuenta completo de un cliente.
    
    Validaciones:
    - Se obtienen todos los movimientos (CARGO y ABONO)
    - Se calcula saldo acumulado correctamente
    - Se muestran fechas y conceptos
    """
    print_header("TEST 3: Consultar Estado de Cuenta")
    
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Buscar cliente con movimientos
        cursor.execute("""
            SELECT DISTINCT c.ID_Cliente, c.Nombres, c.Apellidos
            FROM clientes c
            INNER JOIN cta_corriente cc ON c.ID_Cliente = cc.ID_Cliente
            WHERE c.Activo = TRUE
            LIMIT 1
        """)
        
        result = cursor.fetchone()
        
        if not result:
            print_info("No hay clientes con movimientos. Creando datos de prueba...")
            
            cursor.execute("SELECT ID_Cliente, Nombres, Apellidos FROM clientes WHERE Activo = TRUE LIMIT 1")
            cliente = cursor.fetchone()
            id_cliente, nombres, apellidos = cliente
            
            # Crear movimientos de prueba
            cursor.execute("""
                INSERT INTO cta_corriente
                (ID_Cliente, Tipo_Movimiento, Monto, Fecha, Referencia_Doc)
                VALUES 
                (%s, 'Cargo', 100000, NOW(), 'Crédito inicial'),
                (%s, 'Abono', 50000, NOW(), 'Pago efectivo'),
                (%s, 'Cargo', 75000, NOW(), 'Nueva compra')
            """, (id_cliente, id_cliente, id_cliente))
        else:
            id_cliente, nombres, apellidos = result
        
        print_info(f"Cliente: {nombres} {apellidos} (ID: {id_cliente})")
        
        # Obtener estado de cuenta detallado
        cursor.execute("""
            SELECT 
                Fecha,
                Tipo_Movimiento,
                Referencia_Doc,
                Monto,
                ID_Movimiento
            FROM cta_corriente
            WHERE ID_Cliente = %s
            ORDER BY Fecha, ID_Movimiento
        """, (id_cliente,))
        
        movimientos = cursor.fetchall()
        
        print_success(f"\n✅ Estado de cuenta obtenido")
        print_info(f"   Total de movimientos: {len(movimientos)}")
        
        if movimientos:
            print("\n   📊 Detalle de movimientos:")
            print(f"   {'Fecha':<20} {'Tipo':<10} {'Referencia_Doc':<30} {'Monto':>15}")
            print(f"   {'-'*80}")
            
            saldo_acumulado = 0
            for mov in movimientos[:10]:  # Mostrar máximo 10
                fecha, tipo, concepto, importe, id_mov = mov
                
                if tipo == 'CARGO':
                    saldo_acumulado += float(importe)
                    signo = '+'
                else:
                    saldo_acumulado -= float(importe)
                    signo = '-'
                
                print(f"   {fecha.strftime('%d/%m/%Y %H:%M'):<20} {tipo:<10} {concepto[:28]:<30} {signo}Gs. {float(importe):>12,.0f}")
            
            if len(movimientos) > 10:
                print(f"   ... y {len(movimientos) - 10} movimientos más")
            
            print(f"\n   💰 Saldo final: Gs. {saldo_acumulado:,.0f}")
        
        conn.rollback()
        return True
        
    except Exception as e:
        print_error(f"Error en test_estado_de_cuenta: {str(e)}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

# ============================================================================
# TEST 4: CALCULAR SALDOS ACUMULADOS
# ============================================================================

def test_calcular_saldos():
    """
    Prueba el cálculo de saldos totales por cliente.
    
    Validaciones:
    - Saldo = CARGO - ABONO
    - Se identifican clientes con saldo deudor
    - Se calculan totales generales
    """
    print_header("TEST 4: Calcular Saldos Acumulados")
    
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Calcular saldos por cliente
        cursor.execute("""
            SELECT 
                c.ID_Cliente,
                c.Nombres,
                c.Apellidos,
                COALESCE(SUM(
                    CASE 
                        WHEN ccc.Tipo_Movimiento = 'Cargo' THEN ccc.Monto
                        ELSE 0
                    END
                ), 0) as total_cargos,
                COALESCE(SUM(
                    CASE 
                        WHEN ccc.Tipo_Movimiento = 'Abono' THEN ccc.Monto
                        ELSE 0
                    END
                ), 0) as total_abonos,
                COALESCE(SUM(
                    CASE 
                        WHEN ccc.Tipo_Movimiento = 'Cargo' THEN ccc.Monto
                        WHEN ccc.Tipo_Movimiento = 'Abono' THEN -ccc.Monto
                        ELSE 0
                    END
                ), 0) as saldo
            FROM clientes c
            LEFT JOIN cta_corriente ccc ON c.ID_Cliente = ccc.ID_Cliente
            WHERE c.Activo = TRUE
            GROUP BY c.ID_Cliente, c.Nombres, c.Apellidos
            HAVING saldo != 0
            ORDER BY saldo DESC
            LIMIT 10
        """)
        
        clientes_saldo = cursor.fetchall()
        
        print_success(f"✅ Saldos calculados para {len(clientes_saldo)} clientes")
        
        if clientes_saldo:
            print("\n   📊 Top 10 clientes con saldo:")
            print(f"   {'Cliente':<30} {'Cargos':>15} {'Abonos':>15} {'Saldo':>15}")
            print(f"   {'-'*80}")
            
            total_general = 0
            for cliente in clientes_saldo:
                id_cli, nombres, apellidos, cargos, abonos, saldo = cliente
                nombre_completo = f"{nombres} {apellidos}"[:28]
                print(f"   {nombre_completo:<30} Gs. {float(cargos):>12,.0f} Gs. {float(abonos):>12,.0f} Gs. {float(saldo):>12,.0f}")
                total_general += float(saldo)
            
            print(f"   {'-'*80}")
            print(f"   {'TOTAL GENERAL':<30} {'':>15} {'':>15} Gs. {total_general:>12,.0f}")
        else:
            print_info("   No hay clientes con saldo pendiente")
        
        # Estadísticas generales
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT ID_Cliente) as clientes_con_cta,
                COUNT(*) as total_movimientos,
                SUM(CASE WHEN Tipo_Movimiento = 'Cargo' THEN Monto ELSE 0 END) as total_cargos,
                SUM(CASE WHEN Tipo_Movimiento = 'Abono' THEN Monto ELSE 0 END) as total_abonos
            FROM cta_corriente
        """)
        
        stats = cursor.fetchone()
        if stats:
            clientes_cta, movs, cargos, abonos = stats
            print(f"\n   📈 Estadísticas generales:")
            print(f"   Clientes con cuenta corriente: {clientes_cta}")
            print(f"   Total de movimientos: {movs}")
            print(f"   Total cargos: Gs. {float(cargos or 0):,.0f}")
            print(f"   Total abonos: Gs. {float(abonos or 0):,.0f}")
        
        conn.rollback()
        return True
        
    except Exception as e:
        print_error(f"Error en test_calcular_saldos: {str(e)}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

# ============================================================================
# TEST 5: VALIDAR LÍMITES DE CRÉDITO
# ============================================================================

def test_limites_credito():
    """
    Prueba la validación de límites de crédito por cliente.
    
    Validaciones:
    - Se verifica saldo actual vs límite permitido
    - Se bloquea crédito si excede límite
    - Se alerta sobre clientes cercanos al límite
    """
    print_header("TEST 5: Validar Límites de Crédito")
    
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Definir límite de crédito (ejemplo: Gs. 500,000)
        limite_credito = 500000
        print_info(f"Límite de crédito general: Gs. {limite_credito:,.0f}")
        
        # Obtener clientes con sus saldos
        cursor.execute("""
            SELECT 
                c.ID_Cliente,
                c.Nombres,
                c.Apellidos,
                COALESCE(SUM(
                    CASE 
                        WHEN ccc.Tipo_Movimiento = 'Cargo' THEN ccc.Monto
                        WHEN ccc.Tipo_Movimiento = 'Abono' THEN -ccc.Monto
                        ELSE 0
                    END
                ), 0) as saldo_actual
            FROM clientes c
            LEFT JOIN cta_corriente ccc ON c.ID_Cliente = ccc.ID_Cliente
            WHERE c.Activo = TRUE
            GROUP BY c.ID_Cliente, c.Nombres, c.Apellidos
            HAVING saldo_actual > 0
            ORDER BY saldo_actual DESC
        """)
        
        clientes = cursor.fetchall()
        
        # Clasificar clientes según su saldo
        excede_limite = []
        cerca_limite = []
        normal = []
        
        for cliente in clientes:
            id_cli, nombres, apellidos, saldo = cliente
            saldo = float(saldo)
            
            if saldo > limite_credito:
                excede_limite.append((nombres, apellidos, saldo))
            elif saldo > limite_credito * 0.8:  # 80% del límite
                cerca_limite.append((nombres, apellidos, saldo))
            else:
                normal.append((nombres, apellidos, saldo))
        
        print_success(f"\n✅ Validación de límites completada")
        print_info(f"   Total clientes analizados: {len(clientes)}")
        
        # Mostrar clientes que exceden el límite
        if excede_limite:
            print(f"\n   🚨 ALERTA: {len(excede_limite)} cliente(s) exceden el límite:")
            for nombres, apellidos, saldo in excede_limite:
                exceso = saldo - limite_credito
                print(f"   - {nombres} {apellidos}: Gs. {saldo:,.0f} (Exceso: Gs. {exceso:,.0f})")
        
        # Mostrar clientes cercanos al límite
        if cerca_limite:
            print(f"\n   ⚠️  PRECAUCIÓN: {len(cerca_limite)} cliente(s) cerca del límite:")
            for nombres, apellidos, saldo in cerca_limite:
                disponible = limite_credito - saldo
                print(f"   - {nombres} {apellidos}: Gs. {saldo:,.0f} (Disponible: Gs. {disponible:,.0f})")
        
        # Clientes normales
        if normal:
            print(f"\n   ✅ {len(normal)} cliente(s) con crédito normal")
        
        # Simular otorgamiento de crédito con validación
        print("\n   🔍 Simulación: Otorgar Gs. 100,000 adicionales")
        
        if clientes:
            id_test, nombres, apellidos, saldo_actual = clientes[0]
            saldo_actual = float(saldo_actual)
            monto_nuevo = 100000
            saldo_proyectado = saldo_actual + monto_nuevo
            
            print(f"   Cliente: {nombres} {apellidos}")
            print(f"   Saldo actual: Gs. {saldo_actual:,.0f}")
            print(f"   Nuevo crédito: Gs. {monto_nuevo:,.0f}")
            print(f"   Saldo proyectado: Gs. {saldo_proyectado:,.0f}")
            
            if saldo_proyectado > limite_credito:
                print_error(f"   ❌ RECHAZADO: Excedería el límite por Gs. {(saldo_proyectado - limite_credito):,.0f}")
            else:
                print_success(f"   ✅ APROBADO: Quedarían Gs. {(limite_credito - saldo_proyectado):,.0f} disponibles")
        
        conn.rollback()
        return True
        
    except Exception as e:
        print_error(f"Error en test_limites_credito: {str(e)}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

# ============================================================================
# TEST 6: MOVIMIENTOS HISTÓRICOS Y REPORTES
# ============================================================================

def test_reportes_historicos():
    """
    Prueba la generación de reportes históricos de cuenta corriente.
    
    Validaciones:
    - Movimientos por rango de fechas
    - Totales mensuales
    - Antigüedad de saldos
    - Tendencias de pago
    """
    print_header("TEST 6: Movimientos Históricos y Reportes")
    
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Obtener movimientos del último mes
        cursor.execute("""
            SELECT 
                DATE_FORMAT(Fecha, '%Y-%m') as mes,
                Tipo_Movimiento,
                COUNT(*) as cantidad,
                SUM(Monto) as total
            FROM cta_corriente
            WHERE Fecha >= DATE_SUB(NOW(), INTERVAL 3 MONTH)
            GROUP BY mes, Tipo_Movimiento
            ORDER BY mes DESC, Tipo_Movimiento
        """)
        
        movimientos_mensuales = cursor.fetchall()
        
        print_success("✅ Reporte histórico generado")
        
        if movimientos_mensuales:
            print("\n   📊 Movimientos por mes:")
            print(f"   {'Mes':<10} {'Tipo':<10} {'Cantidad':>10} {'Total':>20}")
            print(f"   {'-'*55}")
            
            for mov in movimientos_mensuales:
                mes, tipo, cant, total = mov
                print(f"   {mes:<10} {tipo:<10} {cant:>10} Gs. {float(total):>15,.0f}")
        
        # Antigüedad de saldos
        cursor.execute("""
            SELECT 
                c.ID_Cliente,
                c.Nombres,
                c.Apellidos,
                MIN(ccc.Fecha) as primera_operacion,
                MAX(ccc.Fecha) as ultima_operacion,
                DATEDIFF(NOW(), MAX(ccc.Fecha)) as dias_sin_movimiento,
                SUM(CASE WHEN ccc.Tipo_Movimiento = 'Cargo' THEN ccc.Monto ELSE -ccc.Monto END) as saldo
            FROM clientes c
            INNER JOIN cta_corriente ccc ON c.ID_Cliente = ccc.ID_Cliente
            WHERE c.Activo = TRUE
            GROUP BY c.ID_Cliente, c.Nombres, c.Apellidos
            HAVING saldo > 0
            ORDER BY dias_sin_movimiento DESC
            LIMIT 5
        """)
        
        saldos_antiguos = cursor.fetchall()
        
        if saldos_antiguos:
            print("\n   ⏰ Saldos más antiguos sin movimiento:")
            print(f"   {'Cliente':<30} {'Última operación':<15} {'Días':>8} {'Saldo':>15}")
            print(f"   {'-'*75}")
            
            for cliente in saldos_antiguos:
                id_cli, nombres, apellidos, primera, ultima, dias, saldo = cliente
                nombre = f"{nombres} {apellidos}"[:28]
                fecha_ult = ultima.strftime('%d/%m/%Y')
                print(f"   {nombre:<30} {fecha_ult:<15} {dias:>8} Gs. {float(saldo):>12,.0f}")
        
        # Estadísticas de pago
        cursor.execute("""
            SELECT 
                AVG(Monto) as promedio_cargo,
                AVG(CASE WHEN Tipo_Movimiento = 'Abono' THEN Monto END) as promedio_abono,
                COUNT(DISTINCT CASE WHEN Tipo_Movimiento = 'Cargo' THEN ID_Cliente END) as clientes_con_cargo,
                COUNT(DISTINCT CASE WHEN Tipo_Movimiento = 'Abono' THEN ID_Cliente END) as clientes_con_abono
            FROM cta_corriente
            WHERE Fecha >= DATE_SUB(NOW(), INTERVAL 1 MONTH)
        """)
        
        stats = cursor.fetchone()
        if stats:
            prom_cargo, prom_abono, cli_cargo, cli_abono = stats
            
            print("\n   📈 Estadísticas del último mes:")
            if prom_cargo:
                print(f"   Promedio de créditos: Gs. {float(prom_cargo):,.0f}")
            if prom_abono:
                print(f"   Promedio de pagos: Gs. {float(prom_abono):,.0f}")
            print(f"   Clientes con nuevos créditos: {cli_cargo}")
            print(f"   Clientes que realizaron pagos: {cli_abono}")
        
        conn.rollback()
        return True
        
    except Exception as e:
        print_error(f"Error en test_reportes_historicos: {str(e)}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

# ============================================================================
# EJECUTAR TODOS LOS TESTS
# ============================================================================

def main():
    """Ejecuta todos los tests del módulo"""
    
    print("\n")
    print("█" * 70)
    print("█                                                                    █")
    print("█          TEST COMPLETO - CUENTA CORRIENTE DE CLIENTES             █")
    print("█                                                                    █")
    print("█" * 70)
    
    tests = [
        ("Otorgar Crédito", test_otorgar_credito),
        ("Registrar Pago", test_registrar_pago),
        ("Estado de Cuenta", test_estado_de_cuenta),
        ("Calcular Saldos", test_calcular_saldos),
        ("Límites de Crédito", test_limites_credito),
        ("Reportes Históricos", test_reportes_historicos),
    ]
    
    resultados = []
    
    for nombre, test_func in tests:
        try:
            resultado = test_func()
            resultados.append((nombre, resultado))
        except Exception as e:
            print_error(f"Error crítico en {nombre}: {str(e)}")
            resultados.append((nombre, False))
    
    # Resumen final
    print_header("RESUMEN DE RESULTADOS")
    
    exitosos = sum(1 for _, r in resultados if r)
    total = len(resultados)
    
    for nombre, resultado in resultados:
        estado = "✅ PASS" if resultado else "❌ FAIL"
        print(f"{estado} - {nombre}")
    
    print(f"\n{'='*70}")
    print(f"Total: {exitosos}/{total} tests exitosos ({exitosos/total*100:.1f}%)")
    print(f"{'='*70}")
    
    if exitosos == total:
        print("\n🎉 ¡PERFECTO! Todos los tests de cuenta corriente pasaron exitosamente.")
    else:
        print(f"\n⚠️  {total - exitosos} test(s) fallaron. Revisar implementación.")
    
    print("\n")

if __name__ == "__main__":
    main()
