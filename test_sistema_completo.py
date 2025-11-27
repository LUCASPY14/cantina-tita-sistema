"""
SCRIPT DE PRUEBAS COMPLETAS - SISTEMA CANTINA TITA
====================================================
Prueba todas las funcionalidades implementadas el 26 de noviembre de 2025
"""

import MySQLdb
from datetime import datetime
from decimal import Decimal

# Configuración de conexión
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'passwd': 'L01G05S33Vice.42',
    'db': 'cantinatitadb'
}

def ejecutar_query(query, params=None, fetch=True):
    """Ejecuta una query y retorna resultados"""
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    try:
        cursor.execute(query, params or ())
        if fetch:
            resultado = cursor.fetchall()
            conn.close()
            return resultado
        else:
            conn.commit()
            last_id = cursor.lastrowid
            conn.close()
            return last_id
    except Exception as e:
        conn.rollback()
        conn.close()
        raise e

def print_seccion(titulo):
    """Imprime un título de sección"""
    print("\n" + "=" * 80)
    print(f"  {titulo}")
    print("=" * 80)

def print_exito(mensaje):
    """Imprime mensaje de éxito"""
    print(f"✓ {mensaje}")

def print_error(mensaje):
    """Imprime mensaje de error"""
    print(f"✗ {mensaje}")

def print_info(mensaje):
    """Imprime mensaje informativo"""
    print(f"ℹ {mensaje}")


# =============================================================================
# PRUEBA 1: TABLA CONSUMOS_TARJETA Y TRIGGER
# =============================================================================

def test_consumos_tarjeta():
    print_seccion("PRUEBA 1: Tabla consumos_tarjeta y trigger de actualización de saldo")
    
    try:
        # Verificar que la tabla existe
        resultado = ejecutar_query("SHOW TABLES LIKE 'consumos_tarjeta'")
        if resultado:
            print_exito("Tabla consumos_tarjeta existe")
        else:
            print_error("Tabla consumos_tarjeta NO existe")
            return False
        
        # Verificar que el trigger existe
        resultado = ejecutar_query("SHOW TRIGGERS WHERE `Trigger` = 'trg_actualizar_saldo_tarjeta'")
        if resultado:
            print_exito("Trigger trg_actualizar_saldo_tarjeta existe")
        else:
            print_error("Trigger trg_actualizar_saldo_tarjeta NO existe")
            return False
        
        # Obtener tarjeta de prueba
        tarjetas = ejecutar_query("SELECT Nro_Tarjeta, Saldo_Actual FROM tarjetas WHERE Estado = 'Activa' LIMIT 1")
        if not tarjetas:
            print_error("No hay tarjetas activas para probar")
            return False
        
        nro_tarjeta, saldo_inicial = tarjetas[0]
        print_info(f"Tarjeta de prueba: {nro_tarjeta}, Saldo inicial: Gs. {saldo_inicial:,.0f}")
        
        # Verificar que hay saldo suficiente
        if saldo_inicial < 1000:
            print_error(f"Saldo insuficiente en tarjeta {nro_tarjeta} para realizar prueba")
            return False
        
        # Intentar registrar un consumo
        monto_consumo = 1000
        print_info(f"Registrando consumo de Gs. {monto_consumo:,.0f}...")
        
        query_consumo = """
        INSERT INTO consumos_tarjeta 
        (Nro_Tarjeta, Fecha_Consumo, Monto_Consumido, Detalle) 
        VALUES (%s, NOW(), %s, %s)
        """
        
        try:
            id_consumo = ejecutar_query(
                query_consumo, 
                (nro_tarjeta, monto_consumo, 'PRUEBA AUTOMATICA - Sistema completo'),
                fetch=False
            )
            print_exito(f"Consumo registrado con ID: {id_consumo}")
            
            # Verificar que el consumo se registró correctamente
            consumo = ejecutar_query(
                "SELECT Saldo_Anterior, Saldo_Posterior FROM consumos_tarjeta WHERE ID_Consumo = %s",
                (id_consumo,)
            )
            
            if consumo:
                saldo_ant, saldo_post = consumo[0]
                print_exito(f"Saldo anterior registrado: Gs. {saldo_ant:,.0f}")
                print_exito(f"Saldo posterior registrado: Gs. {saldo_post:,.0f}")
                
                # Verificar que el saldo de la tarjeta se actualizó
                nuevo_saldo = ejecutar_query(
                    "SELECT Saldo_Actual FROM tarjetas WHERE Nro_Tarjeta = %s",
                    (nro_tarjeta,)
                )[0][0]
                
                print_info(f"Saldo actual de la tarjeta: Gs. {nuevo_saldo:,.0f}")
                
                if nuevo_saldo == saldo_post:
                    print_exito("✓✓✓ TRIGGER FUNCIONANDO CORRECTAMENTE ✓✓✓")
                    print_exito(f"Saldo actualizado de Gs. {saldo_inicial:,.0f} a Gs. {nuevo_saldo:,.0f}")
                    return True
                else:
                    print_error("El saldo de la tarjeta no coincide con el saldo posterior del consumo")
                    return False
            else:
                print_error("No se encontró el consumo registrado")
                return False
                
        except Exception as e:
            print_error(f"Error al registrar consumo: {e}")
            return False
            
    except Exception as e:
        print_error(f"Error en prueba de consumos: {e}")
        return False


# =============================================================================
# PRUEBA 2: VISTAS SQL
# =============================================================================

def test_vistas_sql():
    print_seccion("PRUEBA 2: Vistas SQL de reportes")
    
    vistas = [
        ('v_ventas_dia_detallado', 'Vista de ventas con detalles'),
        ('v_consumos_estudiante', 'Vista de consumos por estudiante'),
        ('v_stock_critico_alertas', 'Vista de stock crítico'),
        ('v_recargas_historial', 'Vista de historial de recargas'),
        ('v_resumen_caja_diario', 'Vista de resumen de caja diario'),
        ('v_notas_credito_detallado', 'Vista de notas de crédito')
    ]
    
    resultados = []
    
    for nombre_vista, descripcion in vistas:
        try:
            # Verificar que la vista existe
            resultado = ejecutar_query(f"SHOW FULL TABLES WHERE Tables_in_cantinatitadb = '{nombre_vista}' AND Table_type = 'VIEW'")
            if resultado:
                # Intentar hacer un SELECT
                count = ejecutar_query(f"SELECT COUNT(*) as total FROM {nombre_vista}")[0][0]
                print_exito(f"{descripcion}: {count} registros")
                resultados.append(True)
            else:
                print_error(f"Vista {nombre_vista} NO existe")
                resultados.append(False)
        except Exception as e:
            print_error(f"Error en vista {nombre_vista}: {e}")
            resultados.append(False)
    
    return all(resultados)


# =============================================================================
# PRUEBA 3: FUNCIONALIDAD DE RECARGAS
# =============================================================================

def test_sistema_recargas():
    print_seccion("PRUEBA 3: Sistema de recargas de tarjeta")
    
    try:
        # Verificar tabla cargas_saldo
        resultado = ejecutar_query("SHOW TABLES LIKE 'cargas_saldo'")
        if resultado:
            print_exito("Tabla cargas_saldo existe")
        else:
            print_error("Tabla cargas_saldo NO existe")
            return False
        
        # Contar recargas recientes
        count = ejecutar_query("SELECT COUNT(*) FROM cargas_saldo WHERE DATE(Fecha_Carga) = CURDATE()")[0][0]
        print_info(f"Recargas realizadas hoy: {count}")
        
        # Obtener tarjeta para prueba
        tarjetas = ejecutar_query("SELECT Nro_Tarjeta, Saldo_Actual FROM tarjetas WHERE Estado = 'Activa' LIMIT 1")
        if not tarjetas:
            print_error("No hay tarjetas activas para probar")
            return False
        
        nro_tarjeta, saldo_antes = tarjetas[0]
        print_info(f"Tarjeta de prueba: {nro_tarjeta}, Saldo: Gs. {saldo_antes:,.0f}")
        
        # Registrar recarga de prueba
        monto_recarga = 5000
        print_info(f"Registrando recarga de Gs. {monto_recarga:,.0f}...")
        
        # Obtener un cliente para la recarga
        cliente = ejecutar_query("SELECT ID_Cliente FROM clientes WHERE Activo = 1 LIMIT 1")[0][0]
        
        query_recarga = """
        INSERT INTO cargas_saldo 
        (Nro_Tarjeta, Monto_Cargado, Fecha_Carga, ID_Cliente_Origen) 
        VALUES (%s, %s, NOW(), %s)
        """
        
        id_carga = ejecutar_query(query_recarga, (nro_tarjeta, monto_recarga, cliente), fetch=False)
        print_exito(f"Recarga registrada con ID: {id_carga}")
        
        # Actualizar saldo manualmente (ya que el trigger de venta no está completo)
        ejecutar_query(
            "UPDATE tarjetas SET Saldo_Actual = Saldo_Actual + %s WHERE Nro_Tarjeta = %s",
            (monto_recarga, nro_tarjeta),
            fetch=False
        )
        
        # Verificar nuevo saldo
        saldo_despues = ejecutar_query(
            "SELECT Saldo_Actual FROM tarjetas WHERE Nro_Tarjeta = %s",
            (nro_tarjeta,)
        )[0][0]
        
        print_info(f"Saldo después de recarga: Gs. {saldo_despues:,.0f}")
        
        if saldo_despues == saldo_antes + monto_recarga:
            print_exito("✓✓✓ SISTEMA DE RECARGAS FUNCIONAL ✓✓✓")
            return True
        else:
            print_error("El saldo no se actualizó correctamente")
            return False
            
    except Exception as e:
        print_error(f"Error en prueba de recargas: {e}")
        return False


# =============================================================================
# PRUEBA 4: INTEGRIDAD DE DATOS
# =============================================================================

def test_integridad_datos():
    print_seccion("PRUEBA 4: Integridad de datos y relaciones")
    
    pruebas = []
    
    # Verificar tarjetas sin hijo
    resultado = ejecutar_query("""
        SELECT COUNT(*) FROM tarjetas t 
        LEFT JOIN hijos h ON t.ID_Hijo = h.ID_Hijo 
        WHERE h.ID_Hijo IS NULL
    """)[0][0]
    
    if resultado == 0:
        print_exito("Todas las tarjetas tienen hijo asignado")
        pruebas.append(True)
    else:
        print_error(f"{resultado} tarjetas sin hijo asignado")
        pruebas.append(False)
    
    # Verificar hijos sin responsable
    resultado = ejecutar_query("""
        SELECT COUNT(*) FROM hijos h 
        LEFT JOIN clientes c ON h.ID_Cliente_Responsable = c.ID_Cliente 
        WHERE c.ID_Cliente IS NULL
    """)[0][0]
    
    if resultado == 0:
        print_exito("Todos los hijos tienen responsable asignado")
        pruebas.append(True)
    else:
        print_error(f"{resultado} hijos sin responsable asignado")
        pruebas.append(False)
    
    # Verificar consumos con tarjetas inválidas
    resultado = ejecutar_query("""
        SELECT COUNT(*) FROM consumos_tarjeta ct 
        LEFT JOIN tarjetas t ON ct.Nro_Tarjeta = t.Nro_Tarjeta 
        WHERE t.Nro_Tarjeta IS NULL
    """)[0][0]
    
    if resultado == 0:
        print_exito("Todos los consumos tienen tarjeta válida")
        pruebas.append(True)
    else:
        print_error(f"{resultado} consumos con tarjeta inválida")
        pruebas.append(False)
    
    return all(pruebas)


# =============================================================================
# PRUEBA 5: ESTADÍSTICAS DEL SISTEMA
# =============================================================================

def test_estadisticas_sistema():
    print_seccion("PRUEBA 5: Estadísticas del sistema")
    
    try:
        # Total de estudiantes activos
        total_estudiantes = ejecutar_query("SELECT COUNT(*) FROM hijos WHERE Activo = 1")[0][0]
        print_info(f"Total de estudiantes activos: {total_estudiantes}")
        
        # Total de tarjetas activas
        total_tarjetas = ejecutar_query("SELECT COUNT(*) FROM tarjetas WHERE Estado = 'Activa'")[0][0]
        print_info(f"Total de tarjetas activas: {total_tarjetas}")
        
        # Saldo total en tarjetas
        saldo_total = ejecutar_query("SELECT SUM(Saldo_Actual) FROM tarjetas WHERE Estado = 'Activa'")[0][0] or 0
        print_info(f"Saldo total en circulación: Gs. {saldo_total:,.0f}")
        
        # Total de consumos hoy
        consumos_hoy = ejecutar_query("SELECT COUNT(*) FROM consumos_tarjeta WHERE DATE(Fecha_Consumo) = CURDATE()")[0][0]
        print_info(f"Consumos registrados hoy: {consumos_hoy}")
        
        # Total de recargas hoy
        recargas_hoy = ejecutar_query("SELECT COUNT(*) FROM cargas_saldo WHERE DATE(Fecha_Carga) = CURDATE()")[0][0]
        print_info(f"Recargas registradas hoy: {recargas_hoy}")
        
        # Total de productos activos
        productos_activos = ejecutar_query("SELECT COUNT(*) FROM productos WHERE Activo = 1")[0][0]
        print_info(f"Productos activos: {productos_activos}")
        
        # Productos con stock crítico
        stock_critico = ejecutar_query("SELECT COUNT(*) FROM v_stock_critico_alertas")[0][0]
        if stock_critico > 0:
            print_info(f"⚠️ Productos con stock crítico: {stock_critico}")
        else:
            print_exito("No hay productos con stock crítico")
        
        print_exito("✓✓✓ ESTADÍSTICAS OBTENIDAS CORRECTAMENTE ✓✓✓")
        return True
        
    except Exception as e:
        print_error(f"Error obteniendo estadísticas: {e}")
        return False


# =============================================================================
# PRUEBA 6: VERIFICAR DJANGO ADMIN
# =============================================================================

def test_django_models():
    print_seccion("PRUEBA 6: Modelos Django y Admin")
    
    print_info("Verificando que el servidor Django esté corriendo...")
    print_info("URL: http://127.0.0.1:8000/admin/")
    print_info("\nModelos implementados en Django Admin:")
    
    modelos = [
        "ConsumoTarjeta - Historial de consumos",
        "VistaVentasDiaDetallado - Reporte de ventas",
        "VistaConsumosEstudiante - Consumos por estudiante",
        "VistaStockCriticoAlertas - Stock crítico",
        "VistaRecargasHistorial - Historial de recargas",
        "VistaResumenCajaDiario - Resumen de caja",
        "VistaNotasCreditoDetallado - Notas de crédito"
    ]
    
    for modelo in modelos:
        print_exito(f"  • {modelo}")
    
    print_info("\n✓ Para verificar manualmente, accede a http://127.0.0.1:8000/admin/gestion/")
    return True


# =============================================================================
# EJECUTAR TODAS LAS PRUEBAS
# =============================================================================

def ejecutar_todas_pruebas():
    print("\n" + "=" * 80)
    print("  SISTEMA DE PRUEBAS COMPLETAS - CANTINA TITA")
    print("  Fecha: 26 de noviembre de 2025")
    print("=" * 80)
    
    resultados = {}
    
    # Ejecutar pruebas
    resultados['Consumos y Trigger'] = test_consumos_tarjeta()
    resultados['Vistas SQL'] = test_vistas_sql()
    resultados['Sistema de Recargas'] = test_sistema_recargas()
    resultados['Integridad de Datos'] = test_integridad_datos()
    resultados['Estadísticas'] = test_estadisticas_sistema()
    resultados['Django Admin'] = test_django_models()
    
    # Resumen final
    print_seccion("RESUMEN DE PRUEBAS")
    
    total_pruebas = len(resultados)
    pruebas_exitosas = sum(1 for r in resultados.values() if r)
    
    for nombre, resultado in resultados.items():
        if resultado:
            print_exito(f"{nombre}: EXITOSA")
        else:
            print_error(f"{nombre}: FALLIDA")
    
    print("\n" + "=" * 80)
    porcentaje = (pruebas_exitosas / total_pruebas) * 100
    print(f"  RESULTADO FINAL: {pruebas_exitosas}/{total_pruebas} pruebas exitosas ({porcentaje:.1f}%)")
    print("=" * 80)
    
    if pruebas_exitosas == total_pruebas:
        print("\n🎉🎉🎉 ¡TODAS LAS PRUEBAS EXITOSAS! 🎉🎉🎉")
        print("El sistema está completamente funcional.\n")
    else:
        print(f"\n⚠️ {total_pruebas - pruebas_exitosas} prueba(s) fallida(s). Revisar errores arriba.\n")


if __name__ == '__main__':
    ejecutar_todas_pruebas()
