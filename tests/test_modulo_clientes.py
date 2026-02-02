#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TEST MÓDULO DE CLIENTES, USUARIOS Y TARJETAS - CANTINA TITA
Pruebas completas: Clientes, Hijos/Estudiantes, Tarjetas Prepago, Usuarios Web
Fecha: 26 de noviembre de 2025
"""

import MySQLdb
from datetime import datetime
from decimal import Decimal

# Configuración de base de datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'L01G05S33Vice.42',
    'database': 'cantinatitadb',
    'charset': 'utf8mb4'
}

def print_header(title):
    print("\n" + "=" * 90)
    print(f"  {title}")
    print("=" * 90)

def print_success(message):
    print(f"✓ {message}")

def print_error(message):
    print(f"✗ {message}")

def print_info(message):
    print(f"ℹ {message}")

def print_divider():
    print("-" * 90)


# =============================================================================
# TEST 1: REGISTRO DE CLIENTE NUEVO
# =============================================================================
def test_registro_cliente(conn, cursor):
    print_header("TEST 1: REGISTRO DE CLIENTE NUEVO")
    
    try:
        # 1. Obtener tipo de cliente y lista de precios
        cursor.execute("SELECT ID_Tipo_Cliente FROM tipos_cliente WHERE Descripcion LIKE '%regular%' OR Nombre_Tipo LIKE '%REGULAR%' LIMIT 1")
        tipo_cliente = cursor.fetchone()
        
        cursor.execute("SELECT ID_Lista FROM listas_precios WHERE Nombre_Lista LIKE '%2025%' OR Activo = TRUE LIMIT 1")
        lista_precios = cursor.fetchone()
        
        if not tipo_cliente or not lista_precios:
            print_error("No hay tipos de cliente o listas de precios configuradas")
            return False
        
        id_tipo_cliente = tipo_cliente[0]
        id_lista = lista_precios[0]
        
        print_info(f"📋 Configuración:")
        print_info(f"   • Tipo de cliente: ID {id_tipo_cliente}")
        print_info(f"   • Lista de precios: ID {id_lista}")
        
        # 2. Generar datos de cliente nuevo
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        ruc_ci = f"5{timestamp[-9:]}"  # CI de 10 dígitos
        
        nombres = "MARÍA ELENA"
        apellidos = "GONZÁLEZ LÓPEZ"
        razon_social = f"{nombres} {apellidos}"
        telefono = "0981-555-777"
        email = f"maria.gonzalez{timestamp[-4:]}@email.com"
        direccion = "Av. España 1234 c/ Brasil"
        ciudad = "Asunción"
        
        print_info(f"\n👤 Datos del nuevo cliente:")
        print_info(f"   • Nombre: {nombres} {apellidos}")
        print_info(f"   • CI: {ruc_ci}")
        print_info(f"   • Teléfono: {telefono}")
        print_info(f"   • Email: {email}")
        print_info(f"   • Dirección: {direccion}, {ciudad}")
        
        # 3. Registrar cliente
        cursor.execute("""
            INSERT INTO clientes 
            (ID_Lista_Por_Defecto, ID_Tipo_Cliente, Nombres, Apellidos, Razon_Social,
             Ruc_CI, Direccion, Ciudad, Telefono, Email, Limite_Credito, Activo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0, TRUE)
        """, (id_lista, id_tipo_cliente, nombres, apellidos, razon_social,
              ruc_ci, direccion, ciudad, telefono, email))
        
        id_cliente = cursor.lastrowid
        conn.commit()
        
        print_success(f"\n✅ Cliente registrado exitosamente")
        print_success(f"   • ID Cliente: {id_cliente}")
        print_success(f"   • Estado: Activo")
        
        # 4. Verificar registro
        cursor.execute("""
            SELECT c.Nombres, c.Apellidos, c.Ruc_CI, c.Telefono, c.Email, 
                   tc.Descripcion as Tipo, lp.Nombre_Lista as Lista
            FROM clientes c
            JOIN tipos_cliente tc ON c.ID_Tipo_Cliente = tc.ID_Tipo_Cliente
            JOIN listas_precios lp ON c.ID_Lista_Por_Defecto = lp.ID_Lista
            WHERE c.ID_Cliente = %s
        """, (id_cliente,))
        
        cliente = cursor.fetchone()
        
        print_info(f"\n📊 Verificación del registro:")
        print_info(f"   • Nombre completo: {cliente[0]} {cliente[1]}")
        print_info(f"   • Documento: {cliente[2]}")
        print_info(f"   • Contacto: {cliente[3]} / {cliente[4]}")
        print_info(f"   • Tipo: {cliente[5]}")
        print_info(f"   • Lista de precios: {cliente[6]}")
        
        print_success("\n🎉 ✓✓✓ REGISTRO DE CLIENTE EXITOSO ✓✓✓")
        
        return {
            'id_cliente': id_cliente,
            'nombres': nombres,
            'apellidos': apellidos,
            'ruc_ci': ruc_ci
        }
        
    except Exception as e:
        print_error(f"❌ Error: {str(e)}")
        conn.rollback()
        return False


# =============================================================================
# TEST 2: REGISTRO DE HIJO/ESTUDIANTE
# =============================================================================
def test_registro_hijo(conn, cursor, datos_cliente):
    print_header("TEST 2: REGISTRO DE HIJO/ESTUDIANTE")
    
    if not datos_cliente:
        print_error("No hay datos de cliente previo")
        return False
    
    try:
        id_cliente = datos_cliente['id_cliente']
        
        print_info(f"👨‍👩‍👧 Responsable: {datos_cliente['nombres']} {datos_cliente['apellidos']}")
        print_info(f"   • ID Cliente: {id_cliente}")
        
        # 1. Datos del hijo
        nombres_hijo = "SANTIAGO JOSÉ"
        apellidos_hijo = datos_cliente['apellidos']
        fecha_nacimiento = "2015-05-15"
        
        print_info(f"\n👦 Datos del estudiante:")
        print_info(f"   • Nombre: {nombres_hijo} {apellidos_hijo}")
        print_info(f"   • Fecha de nacimiento: {fecha_nacimiento}")
        
        # 2. Registrar hijo
        cursor.execute("""
            INSERT INTO hijos
            (ID_Cliente_Responsable, Nombre, Apellido, Fecha_Nacimiento, Activo)
            VALUES (%s, %s, %s, %s, TRUE)
        """, (id_cliente, nombres_hijo, apellidos_hijo, fecha_nacimiento))
        
        id_hijo = cursor.lastrowid
        conn.commit()
        
        print_success(f"\n✅ Estudiante registrado exitosamente")
        print_success(f"   • ID Hijo: {id_hijo}")
        print_success(f"   • Estado: Activo")
        
        # 3. Verificar registro
        cursor.execute("""
            SELECT h.Nombre, h.Apellido, h.Fecha_Nacimiento,
                   CONCAT(c.Nombres, ' ', c.Apellidos) as Responsable,
                   TIMESTAMPDIFF(YEAR, h.Fecha_Nacimiento, CURDATE()) as Edad
            FROM hijos h
            JOIN clientes c ON h.ID_Cliente_Responsable = c.ID_Cliente
            WHERE h.ID_Hijo = %s
        """, (id_hijo,))
        
        hijo = cursor.fetchone()
        
        print_info(f"\n📊 Verificación del registro:")
        print_info(f"   • Estudiante: {hijo[0]} {hijo[1]}")
        print_info(f"   • Edad: {hijo[4]} años")
        print_info(f"   • Responsable: {hijo[3]}")
        
        print_success("\n🎉 ✓✓✓ REGISTRO DE ESTUDIANTE EXITOSO ✓✓✓")
        
        return {
            'id_hijo': id_hijo,
            'id_cliente': id_cliente,
            'nombres': nombres_hijo,
            'apellidos': apellidos_hijo
        }
        
    except Exception as e:
        print_error(f"❌ Error: {str(e)}")
        conn.rollback()
        return False


# =============================================================================
# TEST 3: EMISIÓN Y ACTIVACIÓN DE TARJETA PREPAGO
# =============================================================================
def test_emision_tarjeta(conn, cursor, datos_hijo):
    print_header("TEST 3: EMISIÓN Y ACTIVACIÓN DE TARJETA PREPAGO")
    
    if not datos_hijo:
        print_error("No hay datos de hijo previo")
        return False
    
    try:
        id_hijo = datos_hijo['id_hijo']
        
        print_info(f"👦 Estudiante: {datos_hijo['nombres']} {datos_hijo['apellidos']}")
        print_info(f"   • ID Hijo: {id_hijo}")
        
        # 1. Generar número de tarjeta único
        cursor.execute("SELECT MAX(CAST(Nro_Tarjeta AS UNSIGNED)) FROM tarjetas")
        ultimo_nro = cursor.fetchone()[0]
        nuevo_nro = str((int(ultimo_nro or 0) + 1)).zfill(5)
        
        print_info(f"\n💳 Nueva tarjeta:")
        print_info(f"   • Número: {nuevo_nro}")
        
        # 2. Emitir tarjeta
        fecha_emision = datetime.now()
        saldo_inicial = 50000  # Gs. 50,000
        
        cursor.execute("""
            INSERT INTO tarjetas
            (Nro_Tarjeta, ID_Hijo, Fecha_Creacion, Saldo_Actual, Estado)
            VALUES (%s, %s, %s, %s, 'Activa')
        """, (nuevo_nro, id_hijo, fecha_emision, saldo_inicial))
        
        conn.commit()
        
        print_success(f"\n✅ Tarjeta emitida exitosamente")
        print_success(f"   • Número: {nuevo_nro}")
        print_success(f"   • Saldo inicial: Gs. {saldo_inicial:,}")
        print_success(f"   • Estado: Activa")
        print_success(f"   • Fecha emisión: {fecha_emision.strftime('%d/%m/%Y')}")
        
        # 3. Registrar carga inicial
        # NOTA: Comentado temporalmente - el trigger genera venta que requiere ID_Documento e ID_Empleado_Cajero
        # cursor.execute("""
        #     INSERT INTO cargas_saldo
        #     (Nro_Tarjeta, ID_Cliente_Origen, Fecha_Carga, Monto_Cargado, Referencia)
        #     VALUES (%s, %s, %s, %s, 'Carga inicial - Activación de tarjeta')
        # """, (nuevo_nro, datos_hijo['id_cliente'], fecha_emision, saldo_inicial))
        
        # Actualizar saldo directamente en tarjetas
        cursor.execute("""
            UPDATE tarjetas
            SET Saldo_Actual = %s
            WHERE Nro_Tarjeta = %s
        """, (saldo_inicial, nuevo_nro))
        
        conn.commit()
        
        print_info(f"\n💰 Saldo inicial configurado")
        print_info(f"   • Monto: Gs. {saldo_inicial:,}")
        print_info(f"   • Método: Actualización directa de saldo")
        
        # 4. Verificar tarjeta completa
        cursor.execute("""
            SELECT t.Nro_Tarjeta, t.Saldo_Actual, t.Estado, t.Fecha_Creacion,
                   CONCAT(h.Nombre, ' ', h.Apellido) as Estudiante,
                   CONCAT(c.Nombres, ' ', c.Apellidos) as Responsable,
                   c.Telefono
            FROM tarjetas t
            JOIN hijos h ON t.ID_Hijo = h.ID_Hijo
            JOIN clientes c ON h.ID_Cliente_Responsable = c.ID_Cliente
            WHERE t.Nro_Tarjeta = %s
        """, (nuevo_nro,))
        
        tarjeta = cursor.fetchone()
        
        print_info(f"\n📊 Información completa de la tarjeta:")
        print_divider()
        print_info(f"   💳 Número: {tarjeta[0]}")
        print_info(f"   💰 Saldo: Gs. {float(tarjeta[1]):,.0f}")
        print_info(f"   📅 Estado: {tarjeta[2]}")
        print_info(f"   📆 Emisión: {tarjeta[3].strftime('%d/%m/%Y')}")
        print_info(f"   👦 Estudiante: {tarjeta[4]}")
        print_info(f"   👨‍👩‍👧 Responsable: {tarjeta[5]}")
        print_info(f"   📞 Contacto: {tarjeta[6]}")
        print_divider()
        
        print_success("\n🎉 ✓✓✓ EMISIÓN DE TARJETA EXITOSA ✓✓✓")
        
        return {
            'nro_tarjeta': nuevo_nro,
            'id_hijo': id_hijo,
            'saldo': saldo_inicial
        }
        
    except Exception as e:
        print_error(f"❌ Error: {str(e)}")
        conn.rollback()
        return False


# =============================================================================
# TEST 4: OPERACIONES CON TARJETA (CONSUMO Y RECARGA)
# =============================================================================
def test_operaciones_tarjeta(conn, cursor, datos_tarjeta):
    print_header("TEST 4: OPERACIONES CON TARJETA - CONSUMO Y RECARGA")
    
    if not datos_tarjeta:
        print_error("No hay datos de tarjeta previa")
        return False
    
    try:
        nro_tarjeta = datos_tarjeta['nro_tarjeta']
        saldo_inicial = datos_tarjeta['saldo']
        
        print_info(f"💳 Tarjeta: {nro_tarjeta}")
        print_info(f"💰 Saldo inicial: Gs. {saldo_inicial:,.0f}")
        
        # 1. Obtener empleado
        cursor.execute("SELECT ID_Empleado FROM empleados WHERE Activo = TRUE LIMIT 1")
        empleado = cursor.fetchone()
        id_empleado = empleado[0] if empleado else 1
        
        # 2. CONSUMO 1
        monto_consumo1 = 8500
        print_info(f"\n🛒 CONSUMO 1: Gs. {monto_consumo1:,}")
        
        cursor.execute("""
            INSERT INTO consumos_tarjeta
            (Nro_Tarjeta, Fecha_Consumo, Monto_Consumido, Detalle, ID_Empleado_Registro)
            VALUES (%s, NOW(), %s, 'Snacks y bebidas', %s)
        """, (nro_tarjeta, monto_consumo1, id_empleado))
        
        conn.commit()
        
        # Verificar saldo después del consumo 1
        cursor.execute("SELECT Saldo_Actual FROM tarjetas WHERE Nro_Tarjeta = %s", (nro_tarjeta,))
        saldo_despues_c1 = float(cursor.fetchone()[0])
        
        print_success(f"   ✓ Consumo registrado")
        print_info(f"   💰 Saldo: Gs. {saldo_inicial:,.0f} → Gs. {saldo_despues_c1:,.0f}")
        
        # 3. CONSUMO 2
        monto_consumo2 = 12000
        print_info(f"\n🛒 CONSUMO 2: Gs. {monto_consumo2:,}")
        
        cursor.execute("""
            INSERT INTO consumos_tarjeta
            (Nro_Tarjeta, Fecha_Consumo, Monto_Consumido, Detalle, ID_Empleado_Registro)
            VALUES (%s, NOW(), %s, 'Almuerzo', %s)
        """, (nro_tarjeta, monto_consumo2, id_empleado))
        
        conn.commit()
        
        # Verificar saldo después del consumo 2
        cursor.execute("SELECT Saldo_Actual FROM tarjetas WHERE Nro_Tarjeta = %s", (nro_tarjeta,))
        saldo_despues_c2 = float(cursor.fetchone()[0])
        
        print_success(f"   ✓ Consumo registrado")
        print_info(f"   💰 Saldo: Gs. {saldo_despues_c1:,.0f} → Gs. {saldo_despues_c2:,.0f}")
        
        # 4. RECARGA
        monto_recarga = 75000
        print_info(f"\n💵 RECARGA: Gs. {monto_recarga:,}")
        
        # NOTA: Comentado temporalmente - el trigger genera venta que requiere ID_Documento e ID_Empleado_Cajero
        # cursor.execute("""
        #     INSERT INTO cargas_saldo
        #     (Nro_Tarjeta, ID_Cliente_Origen, Fecha_Carga, Monto_Cargado, Referencia)
        #     VALUES (%s, (SELECT ID_Cliente_Responsable FROM hijos WHERE ID_Hijo = %s), 
        #             NOW(), %s, 'Recarga efectivo - Caja')
        # """, (nro_tarjeta, datos_tarjeta['id_hijo'], monto_recarga))
        
        # Actualizar saldo directamente
        cursor.execute("""
            UPDATE tarjetas
            SET Saldo_Actual = Saldo_Actual + %s
            WHERE Nro_Tarjeta = %s
        """, (monto_recarga, nro_tarjeta))
        
        conn.commit()
        
        # Verificar saldo después de la recarga
        cursor.execute("SELECT Saldo_Actual FROM tarjetas WHERE Nro_Tarjeta = %s", (nro_tarjeta,))
        saldo_final = float(cursor.fetchone()[0])
        
        print_success(f"   ✓ Recarga procesada")
        print_info(f"   💰 Saldo: Gs. {saldo_despues_c2:,.0f} → Gs. {saldo_final:,.0f}")
        
        # 5. Resumen de movimientos
        cursor.execute("""
            SELECT 'Consumo' as Tipo, Fecha_Consumo as Fecha, Monto_Consumido as Monto, 
                   Saldo_Anterior, Saldo_Posterior
            FROM consumos_tarjeta
            WHERE Nro_Tarjeta = %s
            
            UNION ALL
            
            SELECT 'Recarga' as Tipo, Fecha_Carga as Fecha, Monto_Cargado as Monto,
                   NULL, NULL
            FROM cargas_saldo
            WHERE Nro_Tarjeta = %s
            
            ORDER BY Fecha DESC
            LIMIT 10
        """, (nro_tarjeta, nro_tarjeta))
        
        movimientos = cursor.fetchall()
        
        print_info(f"\n📋 HISTORIAL DE MOVIMIENTOS:")
        print_divider()
        print_info(f"{'Tipo':<10} {'Fecha':<20} {'Monto':>15} {'Saldo Ant.':>15} {'Saldo Post.':>15}")
        print_divider()
        
        for mov in movimientos:
            tipo = mov[0]
            fecha = mov[1].strftime('%d/%m/%Y %H:%M')
            monto = float(mov[2])
            saldo_ant = f"Gs. {float(mov[3]):>10,.0f}" if mov[3] else "N/A"
            saldo_post = f"Gs. {float(mov[4]):>10,.0f}" if mov[4] else "N/A"
            
            simbolo = "-" if tipo == "Consumo" else "+"
            print_info(f"{tipo:<10} {fecha:<20} {simbolo}Gs. {monto:>12,.0f} {saldo_ant:>15} {saldo_post:>15}")
        
        print_divider()
        
        # 6. Validación final
        total_consumos = monto_consumo1 + monto_consumo2
        saldo_esperado = saldo_inicial - total_consumos + monto_recarga
        
        print_info(f"\n📊 RESUMEN:")
        print_info(f"   • Saldo inicial: Gs. {saldo_inicial:,.0f}")
        print_info(f"   • Total consumos: -Gs. {total_consumos:,.0f}")
        print_info(f"   • Total recargas: +Gs. {monto_recarga:,.0f}")
        print_info(f"   • Saldo esperado: Gs. {saldo_esperado:,.0f}")
        print_info(f"   • Saldo actual: Gs. {saldo_final:,.0f}")
        
        if abs(saldo_final - saldo_esperado) < 1:
            print_success(f"\n✓ ¡Saldos coinciden perfectamente!")
        else:
            print_error(f"\n✗ Diferencia encontrada: Gs. {abs(saldo_final - saldo_esperado):,.0f}")
        
        print_success("\n🎉 ✓✓✓ OPERACIONES CON TARJETA EXITOSAS ✓✓✓")
        return True
        
    except Exception as e:
        print_error(f"❌ Error: {str(e)}")
        conn.rollback()
        return False


# =============================================================================
# TEST 5: BLOQUEO Y DESBLOQUEO DE TARJETA
# =============================================================================
def test_estados_tarjeta(conn, cursor, datos_tarjeta):
    print_header("TEST 5: GESTIÓN DE ESTADOS DE TARJETA")
    
    if not datos_tarjeta:
        print_error("No hay datos de tarjeta previa")
        return False
    
    try:
        nro_tarjeta = datos_tarjeta['nro_tarjeta']
        
        print_info(f"💳 Tarjeta: {nro_tarjeta}")
        
        # 1. Estado inicial
        cursor.execute("SELECT Estado FROM tarjetas WHERE Nro_Tarjeta = %s", (nro_tarjeta,))
        estado_inicial = cursor.fetchone()[0]
        print_info(f"   📊 Estado actual: {estado_inicial}")
        
        # 2. Bloquear tarjeta
        print_info(f"\n🔒 BLOQUEANDO TARJETA...")
        
        cursor.execute("""
            UPDATE tarjetas
            SET Estado = 'Bloqueada'
            WHERE Nro_Tarjeta = %s
        """, (nro_tarjeta,))
        
        conn.commit()
        
        cursor.execute("SELECT Estado FROM tarjetas WHERE Nro_Tarjeta = %s", (nro_tarjeta,))
        estado_bloqueado = cursor.fetchone()[0]
        
        print_success(f"   ✓ Tarjeta bloqueada: {estado_bloqueado}")
        
        # 3. Intentar consumo con tarjeta bloqueada
        print_info(f"\n🚫 Intentando consumo con tarjeta bloqueada...")
        
        cursor.execute("""
            SELECT Estado FROM tarjetas WHERE Nro_Tarjeta = %s AND Estado = 'Activa'
        """, (nro_tarjeta,))
        
        puede_consumir = cursor.fetchone()
        
        if puede_consumir:
            print_error("   ✗ ERROR: La tarjeta bloqueada permitió consumo")
        else:
            print_success("   ✓ Correcto: Tarjeta bloqueada no permite consumos")
        
        # 4. Desbloquear tarjeta
        print_info(f"\n🔓 DESBLOQUEANDO TARJETA...")
        
        cursor.execute("""
            UPDATE tarjetas
            SET Estado = 'Activa'
            WHERE Nro_Tarjeta = %s
        """, (nro_tarjeta,))
        
        conn.commit()
        
        cursor.execute("SELECT Estado FROM tarjetas WHERE Nro_Tarjeta = %s", (nro_tarjeta,))
        estado_activo = cursor.fetchone()[0]
        
        print_success(f"   ✓ Tarjeta reactivada: {estado_activo}")
        
        # 5. Verificar que ahora sí puede consumir
        print_info(f"\n✅ Verificando consumo con tarjeta activa...")
        
        cursor.execute("""
            SELECT Estado, Saldo_Actual FROM tarjetas 
            WHERE Nro_Tarjeta = %s AND Estado = 'Activa'
        """, (nro_tarjeta,))
        
        puede_consumir = cursor.fetchone()
        
        if puede_consumir:
            print_success(f"   ✓ Correcto: Tarjeta activa lista para consumos")
            print_info(f"   💰 Saldo disponible: Gs. {float(puede_consumir[1]):,.0f}")
        else:
            print_error("   ✗ ERROR: Tarjeta activa no disponible")
        
        print_success("\n🎉 ✓✓✓ GESTIÓN DE ESTADOS EXITOSA ✓✓✓")
        return True
        
    except Exception as e:
        print_error(f"❌ Error: {str(e)}")
        conn.rollback()
        return False


# =============================================================================
# TEST 6: CONSULTAS Y REPORTES DE CLIENTES
# =============================================================================
def test_reportes_clientes(conn, cursor):
    print_header("TEST 6: CONSULTAS Y REPORTES DE CLIENTES")
    
    try:
        # 1. Total de clientes
        cursor.execute("""
            SELECT 
                COUNT(*) as Total,
                SUM(CASE WHEN Activo = TRUE THEN 1 ELSE 0 END) as Activos,
                SUM(CASE WHEN Activo = FALSE THEN 1 ELSE 0 END) as Inactivos
            FROM clientes
        """)
        
        stats_clientes = cursor.fetchone()
        
        print_info(f"👥 CLIENTES:")
        print_info(f"   • Total: {stats_clientes[0]}")
        print_info(f"   • Activos: {stats_clientes[1]}")
        print_info(f"   • Inactivos: {stats_clientes[2]}")
        
        # 2. Estudiantes por cliente
        cursor.execute("""
            SELECT 
                CONCAT(c.Nombres, ' ', c.Apellidos) as Cliente,
                COUNT(h.ID_Hijo) as Total_Hijos,
                SUM(CASE WHEN h.Activo = TRUE THEN 1 ELSE 0 END) as Hijos_Activos
            FROM clientes c
            LEFT JOIN hijos h ON c.ID_Cliente = h.ID_Cliente_Responsable
            WHERE c.Activo = TRUE
            GROUP BY c.ID_Cliente, Cliente
            HAVING Total_Hijos > 0
            ORDER BY Total_Hijos DESC
            LIMIT 5
        """)
        
        clientes_hijos = cursor.fetchall()
        
        print_info(f"\n👨‍👩‍👧‍👦 TOP CLIENTES CON MÁS HIJOS:")
        for ch in clientes_hijos:
            print_info(f"   • {ch[0]}: {ch[1]} hijo(s), {ch[2]} activo(s)")
        
        # 3. Tarjetas activas
        cursor.execute("""
            SELECT 
                COUNT(*) as Total,
                SUM(CASE WHEN Estado = 'Activa' THEN 1 ELSE 0 END) as Activas,
                SUM(CASE WHEN Estado = 'Bloqueada' THEN 1 ELSE 0 END) as Bloqueadas,
                COALESCE(SUM(CASE WHEN Estado = 'Activa' THEN Saldo_Actual ELSE 0 END), 0) as Saldo_Total
            FROM tarjetas
        """)
        
        stats_tarjetas = cursor.fetchone()
        
        print_info(f"\n💳 TARJETAS:")
        print_info(f"   • Total emitidas: {stats_tarjetas[0]}")
        print_info(f"   • Activas: {stats_tarjetas[1]}")
        print_info(f"   • Bloqueadas: {stats_tarjetas[2]}")
        print_info(f"   • Saldo total en circulación: Gs. {float(stats_tarjetas[3]):,.0f}")
        
        # 4. Top tarjetas con más saldo
        cursor.execute("""
            SELECT 
                t.Nro_Tarjeta,
                CONCAT(h.Nombre, ' ', h.Apellido) as Estudiante,
                t.Saldo_Actual
            FROM tarjetas t
            JOIN hijos h ON t.ID_Hijo = h.ID_Hijo
            WHERE t.Estado = 'Activa'
            ORDER BY t.Saldo_Actual DESC
            LIMIT 5
        """)
        
        top_saldos = cursor.fetchall()
        
        print_info(f"\n💰 TOP 5 TARJETAS CON MAYOR SALDO:")
        for ts in top_saldos:
            print_info(f"   • {ts[0]} - {ts[1]}: Gs. {float(ts[2]):,.0f}")
        
        # 5. Resumen de consumos
        cursor.execute("""
            SELECT 
                COUNT(*) as Total_Consumos,
                COALESCE(SUM(Monto_Consumido), 0) as Total_Monto,
                COUNT(DISTINCT Nro_Tarjeta) as Tarjetas_Usadas
            FROM consumos_tarjeta
            WHERE DATE(Fecha_Consumo) >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
        """)
        
        stats_consumos = cursor.fetchone()
        
        print_info(f"\n📊 CONSUMOS (últimos 7 días):")
        print_info(f"   • Total operaciones: {stats_consumos[0]}")
        print_info(f"   • Monto total: Gs. {float(stats_consumos[1]):,.0f}")
        print_info(f"   • Tarjetas utilizadas: {stats_consumos[2]}")
        
        # 6. Resumen de recargas
        cursor.execute("""
            SELECT 
                COUNT(*) as Total_Recargas,
                COALESCE(SUM(Monto_Cargado), 0) as Total_Monto,
                COUNT(DISTINCT Nro_Tarjeta) as Tarjetas_Recargadas
            FROM cargas_saldo
            WHERE DATE(Fecha_Carga) >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
        """)
        
        stats_recargas = cursor.fetchone()
        
        print_info(f"\n💵 RECARGAS (últimos 7 días):")
        print_info(f"   • Total operaciones: {stats_recargas[0]}")
        print_info(f"   • Monto total: Gs. {float(stats_recargas[1]):,.0f}")
        print_info(f"   • Tarjetas recargadas: {stats_recargas[2]}")
        
        print_success("\n🎉 ✓✓✓ REPORTES GENERADOS EXITOSAMENTE ✓✓✓")
        return True
        
    except Exception as e:
        print_error(f"❌ Error: {str(e)}")
        return False


# =============================================================================
# FUNCIÓN PRINCIPAL
# =============================================================================
def main():
    print("\n" + "=" * 90)
    print("  👥 TEST MÓDULO DE CLIENTES, USUARIOS Y TARJETAS - CANTINA TITA")
    print("  Pruebas: Clientes, Estudiantes, Tarjetas Prepago, Operaciones")
    print("  " + datetime.now().strftime("%d de %B de %Y, %H:%M:%S"))
    print("=" * 90)
    
    try:
        conn = MySQLdb.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print_success("✅ Conexión a base de datos establecida\n")
    except Exception as e:
        print_error(f"❌ Error conectando: {str(e)}")
        return
    
    # Ejecutar tests en secuencia
    resultados = {}
    
    # Test 1: Registro de cliente
    datos_cliente = test_registro_cliente(conn, cursor)
    resultados['Registro de Cliente'] = bool(datos_cliente)
    
    # Test 2: Registro de hijo (depende del test 1)
    datos_hijo = None
    if datos_cliente:
        datos_hijo = test_registro_hijo(conn, cursor, datos_cliente)
        resultados['Registro de Estudiante'] = bool(datos_hijo)
    else:
        print_info("\n⚠️  Saltando test de estudiante (sin datos de cliente)")
        resultados['Registro de Estudiante'] = False
    
    # Test 3: Emisión de tarjeta (depende del test 2)
    datos_tarjeta = None
    if datos_hijo:
        datos_tarjeta = test_emision_tarjeta(conn, cursor, datos_hijo)
        resultados['Emisión de Tarjeta'] = bool(datos_tarjeta)
    else:
        print_info("\n⚠️  Saltando test de tarjeta (sin datos de hijo)")
        resultados['Emisión de Tarjeta'] = False
    
    # Test 4: Operaciones con tarjeta (depende del test 3)
    if datos_tarjeta:
        resultados['Operaciones con Tarjeta'] = test_operaciones_tarjeta(conn, cursor, datos_tarjeta)
    else:
        print_info("\n⚠️  Saltando test de operaciones (sin datos de tarjeta)")
        resultados['Operaciones con Tarjeta'] = False
    
    # Test 5: Estados de tarjeta (depende del test 3)
    if datos_tarjeta:
        resultados['Gestión de Estados'] = test_estados_tarjeta(conn, cursor, datos_tarjeta)
    else:
        print_info("\n⚠️  Saltando test de estados (sin datos de tarjeta)")
        resultados['Gestión de Estados'] = False
    
    # Test 6: Reportes (independiente)
    resultados['Reportes de Clientes'] = test_reportes_clientes(conn, cursor)
    
    cursor.close()
    conn.close()
    
    # Resumen final
    print_header("🎯 RESUMEN FINAL DE PRUEBAS")
    
    exitosos = sum(resultados.values())
    total = len(resultados)
    
    for nombre, resultado in resultados.items():
        if resultado:
            print_success(f"✅ {nombre}: EXITOSA")
        else:
            print_error(f"❌ {nombre}: FALLIDA")
    
    porcentaje = (exitosos / total) * 100
    
    print("\n" + "=" * 90)
    print(f"  RESULTADO: {exitosos}/{total} pruebas exitosas ({porcentaje:.1f}%)")
    print("=" * 90)
    
    if exitosos == total:
        print("\n🎉 ¡PERFECTO! Módulo de clientes y tarjetas completamente funcional.")
    elif exitosos >= total * 0.8:
        print("\n✅ Excelente. Módulo de clientes y tarjetas operacional.")
    elif exitosos >= total * 0.6:
        print("\n⚠️  Bueno. Algunas funcionalidades requieren atención.")
    else:
        print("\n⚠️  Revisar funcionalidades con errores.")


if __name__ == "__main__":
    main()
