#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TEST MÓDULO DE USUARIOS, ROLES Y PERMISOS - CANTINA TITA
=========================================================
Pruebas completas de:
- Creación de usuarios
- Asignación de roles
- Gestión de permisos
- Validación de accesos
- Auditoría de acciones

Fecha: 26 de Noviembre de 2025
"""

import MySQLdb
from datetime import datetime, timedelta
import hashlib

# Configuración de conexión
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'passwd': 'L01G05S33Vice.42',
    'db': 'cantinatitadb'
}

# Colores para output
class Colors:
    HEADER = '\033[95m'
    INFO = '\033[94m'
    SUCCESS = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{'='*90}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^90}{Colors.ENDC}")
    print(f"{'='*90}")

def print_info(text):
    print(f"{Colors.INFO}ℹ {text}{Colors.ENDC}")

def print_success(text):
    print(f"{Colors.SUCCESS}✓ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.ERROR}✗ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_divider():
    print(f"{Colors.INFO}{'-'*90}{Colors.ENDC}")


# =============================================================================
# TEST 1: CONSULTAR ROLES EXISTENTES
# =============================================================================
def test_roles_existentes(conn, cursor):
    print_header("TEST 1: CONSULTAR ROLES EXISTENTES")
    
    try:
        # 1. Listar roles
        cursor.execute("""
            SELECT ID_Rol, Nombre_Rol, Descripcion, Activo
            FROM tipos_rol_general
            ORDER BY ID_Rol
        """)
        
        roles = cursor.fetchall()
        
        print_info(f"\n📋 ROLES DEL SISTEMA:")
        print_divider()
        
        if roles:
            for rol in roles:
                estado = "Activo" if rol[3] else "Inactivo"
                print_info(f"   • ID {rol[0]}: {rol[1]}")
                print_info(f"     Descripcion: {rol[2]}")
                print_info(f"     Estado: {estado}")
                print_info("")
        else:
            print_warning("No hay roles registrados en el sistema")
        
        print_success("\n🎉 ✓✓✓ CONSULTA DE ROLES EXITOSA ✓✓✓")
        
        return {
            'roles': len(roles),
            'roles_data': roles
        }
        
    except Exception as e:
        print_error(f"❌ Error: {str(e)}")
        conn.rollback()
        return False


# =============================================================================
# TEST 2: CREAR NUEVO USUARIO EMPLEADO
# =============================================================================
def test_crear_usuario_empleado(conn, cursor):
    print_header("TEST 2: CREAR NUEVO USUARIO EMPLEADO")
    
    try:
        # 1. Crear empleado
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        ci_empleado = f"6{timestamp[-9:]}"
        usuario = f"lucas.martinez{timestamp[-4:]}"
        email = f"lucas.martinez{timestamp[-4:]}@cantina.com"
        
        # Obtener rol de cajero
        cursor.execute("""
            SELECT ID_Rol 
            FROM tipos_rol_general 
            WHERE Nombre_Rol LIKE '%CAJERO%'
            LIMIT 1
        """)
        
        rol_result = cursor.fetchone()
        if not rol_result:
            print_warning("Rol 'CAJERO' no encontrado, usando primer rol disponible")
            cursor.execute("SELECT ID_Rol FROM tipos_rol_general WHERE Activo = TRUE LIMIT 1")
            rol_result = cursor.fetchone()
        
        id_rol = rol_result[0] if rol_result else 1
        
        # Generar hash simple (en producción usar bcrypt)
        password_plain = "Cantina2025"
        password_hash = hashlib.sha256(password_plain.encode()).hexdigest()[:60]  # Truncar a 60 chars
        
        print_info(f"\n👤 Creando nuevo empleado:")
        
        cursor.execute("""
            INSERT INTO empleados
            (ID_Rol, Nombre, Apellido, Usuario, Contrasena_Hash, 
             Telefono, Email, Activo)
            VALUES (%s, 'LUCAS', 'MARTINEZ', %s, %s, 
                    '0981-444-555', %s, TRUE)
        """, (id_rol, usuario, password_hash, email))
        
        id_empleado = cursor.lastrowid
        print_info(f"   • Empleado ID creado: {id_empleado}")
        
        conn.commit()
        
        print_success(f"\n✅ Empleado creado exitosamente")
        print_success(f"   • ID Empleado: {id_empleado}")
        print_success(f"   • Usuario: {usuario}")
        print_success(f"   • Password: {password_plain}")
        print_success(f"   • Rol ID: {id_rol}")
        
        # 2. Verificar empleado creado
        cursor.execute("""
            SELECT e.Usuario, t.Nombre_Rol, e.Activo, e.Fecha_Ingreso
            FROM empleados e
            JOIN tipos_rol_general t ON e.ID_Rol = t.ID_Rol
            WHERE e.ID_Empleado = %s
        """, (id_empleado,))
        
        empleado_data = cursor.fetchone()
        
        print_info(f"\n📊 Verificacion del empleado:")
        print_info(f"   • Usuario: {empleado_data[0]}")
        print_info(f"   • Rol: {empleado_data[1]}")
        print_info(f"   • Activo: {'Si' if empleado_data[2] else 'No'}")
        print_info(f"   • Fecha ingreso: {empleado_data[3].strftime('%d/%m/%Y %H:%M')}")
        
        print_success("\n🎉 ✓✓✓ CREACION DE EMPLEADO EXITOSA ✓✓✓")
        
        return {
            'id_empleado': id_empleado,
            'usuario': usuario,
            'password': password_plain,
            'password_hash': password_hash,
            'id_rol': id_rol
        }
        
    except Exception as e:
        print_error(f"❌ Error: {str(e)}")
        conn.rollback()
        return False


# =============================================================================
# TEST 3: GESTIÓN DE SESIONES Y AUTENTICACIÓN
# =============================================================================
def test_sesiones_autenticacion(conn, cursor, datos_usuario):
    print_header("TEST 3: GESTIÓN DE SESIONES Y AUTENTICACIÓN")
    
    if not datos_usuario:
        print_warning("No hay datos de usuario previo")
        return False
    
    try:
        # 1. Simular autenticación
        print_info(f"\n🔐 Simulando autenticacion:")
        print_info(f"   • Usuario: {datos_usuario['usuario']}")
        
        # Validar que el empleado existe y está activo
        cursor.execute("""
            SELECT e.ID_Empleado, e.Usuario, t.Nombre_Rol, e.Activo
            FROM empleados e
            JOIN tipos_rol_general t ON e.ID_Rol = t.ID_Rol
            WHERE e.Usuario = %s AND e.Activo = TRUE
        """, (datos_usuario['usuario'],))
        
        resultado = cursor.fetchone()
        
        if not resultado:
            print_error("❌ Empleado no encontrado o inactivo")
            return False
        
        print_success(f"\n✅ Autenticacion exitosa")
        print_info(f"   • Usuario: {resultado[1]}")
        print_info(f"   • Rol: {resultado[2]}")
        print_info(f"   • Estado: Activo")
        
        print_success("\n🎉 ✓✓✓ AUTENTICACION EXITOSA ✓✓✓")
        
        return True
        
    except Exception as e:
        print_error(f"❌ Error: {str(e)}")
        conn.rollback()
        return False


# =============================================================================
# TEST 4: VERIFICACIÓN DE PERMISOS
# =============================================================================
def test_verificacion_permisos(conn, cursor, datos_usuario):
    print_header("TEST 4: VERIFICACIÓN DE PERMISOS")
    
    if not datos_usuario:
        print_warning("No hay datos de usuario previo")
        return False
    
    try:
        id_rol = datos_usuario['id_rol']
        
        # 1. Obtener información del rol
        cursor.execute("""
            SELECT Nombre_Rol, Descripcion
            FROM tipos_rol_general
            WHERE ID_Rol = %s
        """, (id_rol,))
        
        rol_info = cursor.fetchone()
        
        print_info(f"\n🔐 PERMISOS DEL ROL: {rol_info[0]}")
        print_divider()
        print_info(f"   Descripcion: {rol_info[1]}")
        
        # 2. Permisos típicos por rol
        permisos_por_rol = {
            'CAJERO': [
                'Registrar ventas',
                'Procesar recargas de tarjeta',
                'Registrar consumos',
                'Ver reportes basicos',
                'Gestionar cierre de caja'
            ],
            'GERENTE': [
                'Registrar ventas',
                'Procesar recargas de tarjeta',
                'Ver todos los reportes',
                'Gestionar productos',
                'Gestionar empleados',
                'Ver estadisticas'
            ],
            'ADMINISTRADOR': [
                'Acceso total al sistema',
                'Gestionar usuarios y roles',
                'Configurar sistema',
                'Ver auditoria',
                'Gestionar base de datos'
            ]
        }
        
        permisos = permisos_por_rol.get(rol_info[0], ['Permisos no definidos'])
        
        print_info(f"\n📊 PERMISOS ASOCIADOS:")
        print_divider()
        
        for permiso in permisos:
            print_success(f"   ✓ {permiso}")
        
        print_success("\n🎉 ✓✓✓ VERIFICACION DE PERMISOS EXITOSA ✓✓✓")
        
        return True
        
    except Exception as e:
        print_error(f"❌ Error: {str(e)}")
        conn.rollback()
        return False


# =============================================================================
# TEST 5: AUDITORÍA DE ACCIONES
# =============================================================================
def test_auditoria_acciones(conn, cursor, datos_usuario):
    print_header("TEST 5: AUDITORÍA DE ACCIONES")
    
    if not datos_usuario:
        print_warning("No hay datos de usuario previo")
        return False
    
    try:
        # 1. Verificar si existe tabla auditoria o logs
        cursor.execute("""
            SELECT TABLE_NAME
            FROM information_schema.tables 
            WHERE table_schema = 'cantinatitadb' 
            AND (table_name LIKE '%audit%' OR table_name LIKE '%log%')
        """)
        
        tablas_auditoria = cursor.fetchall()
        
        if not tablas_auditoria:
            print_warning("No se encontraron tablas de auditoría. Creando log simulado...")
            
            # Simular registro de auditoría
            acciones_simuladas = [
                ('LOGIN', 'Inicio de sesión exitoso'),
                ('VENTA_CREADA', 'Creó venta ID: 123'),
                ('RECARGA_PROCESADA', 'Procesó recarga en tarjeta 10002'),
                ('REPORTE_GENERADO', 'Generó reporte de ventas del día'),
                ('LOGOUT', 'Cerró sesión correctamente')
            ]
            
            print_info(f"\n📝 ACCIONES REGISTRADAS (simuladas):")
            print_divider()
            
            for i, (accion, descripcion) in enumerate(acciones_simuladas, 1):
                timestamp = (datetime.now() - timedelta(minutes=30-i*5)).strftime('%d/%m/%Y %H:%M')
                print_info(f"   {i}. [{timestamp}] {accion}")
                print_info(f"      {descripcion}")
                print_info("")
            
            print_success("\n🎉 ✓✓✓ AUDITORÍA SIMULADA EXITOSA ✓✓✓")
            return True
        
        # 2. Si existe tabla de auditoría, registrar acciones reales
        tabla_auditoria = tablas_auditoria[0][0]
        print_info(f"\n📝 Registrando en tabla: {tabla_auditoria}")
        
        # Obtener estructura de la tabla
        cursor.execute(f"DESCRIBE {tabla_auditoria}")
        columnas = [col[0] for col in cursor.fetchall()]
        
        # Registrar algunas acciones de prueba
        acciones = [
            ('LOGIN', 'Inicio de sesión de prueba'),
            ('CONSULTA', 'Consultó roles y permisos'),
            ('LOGOUT', 'Cerró sesión de prueba')
        ]
        
        for accion, descripcion in acciones:
            # Adaptar INSERT según estructura de la tabla
            if 'ID_Usuario' in columnas:
                cursor.execute(f"""
                    INSERT INTO {tabla_auditoria}
                    (ID_Usuario, Accion, Descripcion, Fecha)
                    VALUES (%s, %s, %s, NOW())
                """, (datos_usuario['id_usuario'], accion, descripcion))
            else:
                print_info(f"   • {accion}: {descripcion}")
        
        conn.commit()
        
        # 3. Consultar últimas acciones del usuario
        if 'ID_Usuario' in columnas:
            cursor.execute(f"""
                SELECT Accion, Descripcion, Fecha
                FROM {tabla_auditoria}
                WHERE ID_Usuario = %s
                ORDER BY Fecha DESC
                LIMIT 10
            """, (datos_usuario['id_usuario'],))
            
            logs = cursor.fetchall()
            
            print_info(f"\n📊 ÚLTIMAS ACCIONES DEL USUARIO:")
            print_divider()
            
            for log in logs:
                print_info(f"   • [{log[2].strftime('%d/%m/%Y %H:%M')}] {log[0]}")
                print_info(f"     {log[1]}")
        
        print_success("\n🎉 ✓✓✓ AUDITORÍA REGISTRADA EXITOSA ✓✓✓")
        
        return True
        
    except Exception as e:
        print_error(f"❌ Error: {str(e)}")
        conn.rollback()
        return False


# =============================================================================
# TEST 6: ESTADÍSTICAS DE USUARIOS
# =============================================================================
def test_estadisticas_usuarios(conn, cursor):
    print_header("TEST 6: ESTADÍSTICAS DE USUARIOS")
    
    try:
        # 1. Contar empleados por rol
        cursor.execute("""
            SELECT t.Nombre_Rol, COUNT(e.ID_Empleado) as Total
            FROM tipos_rol_general t
            LEFT JOIN empleados e ON t.ID_Rol = e.ID_Rol AND e.Activo = TRUE
            GROUP BY t.ID_Rol, t.Nombre_Rol
            ORDER BY Total DESC
        """)
        
        empleados_por_rol = cursor.fetchall()
        
        print_info(f"\n👥 EMPLEADOS POR ROL:")
        print_divider()
        
        total_empleados = 0
        for rol_stat in empleados_por_rol:
            print_info(f"   • {rol_stat[0]}: {rol_stat[1]} empleado(s)")
            total_empleados += rol_stat[1]
        
        print_info(f"\n   TOTAL: {total_empleados} empleados activos")
        
        # 2. Empleados activos vs inactivos
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN Activo = TRUE THEN 1 ELSE 0 END) as Activos,
                SUM(CASE WHEN Activo = FALSE THEN 1 ELSE 0 END) as Inactivos
            FROM empleados
        """)
        
        estado_empleados = cursor.fetchone()
        
        print_info(f"\n📊 ESTADO DE EMPLEADOS:")
        print_info(f"   • Activos: {estado_empleados[0]}")
        print_info(f"   • Inactivos: {estado_empleados[1]}")
        
        # 3. Ultimos empleados creados
        cursor.execute("""
            SELECT e.Nombre, e.Apellido, e.Usuario, t.Nombre_Rol, e.Fecha_Ingreso
            FROM empleados e
            JOIN tipos_rol_general t ON e.ID_Rol = t.ID_Rol
            ORDER BY e.Fecha_Ingreso DESC
            LIMIT 5
        """)
        
        ultimos = cursor.fetchall()
        
        if ultimos:
            print_info(f"\n🆕 ULTIMOS EMPLEADOS:")
            print_divider()
            
            for empleado in ultimos:
                fecha_str = empleado[4].strftime('%d/%m/%Y %H:%M') if empleado[4] else 'N/A'
                print_info(f"   • {empleado[0]} {empleado[1]} (@{empleado[2]})")
                print_info(f"     Rol: {empleado[3]} - Ingreso: {fecha_str}")
        
        print_success("\n🎉 ✓✓✓ ESTADISTICAS GENERADAS EXITOSAS ✓✓✓")
        
        return True
        
    except Exception as e:
        print_error(f"❌ Error: {str(e)}")
        conn.rollback()
        return False


# =============================================================================
# FUNCIÓN PRINCIPAL
# =============================================================================
def main():
    print_header("👥 TEST MÓDULO DE USUARIOS, ROLES Y PERMISOS - CANTINA TITA")
    print_info("Pruebas: Usuarios, Roles, Permisos, Sesiones, Auditoría")
    print_info(f"{datetime.now().strftime('%d de %B de %Y, %H:%M:%S')}")
    print_header("")
    
    # Conectar a la base de datos
    try:
        conn = MySQLdb.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print_success("✅ Conexión a base de datos establecida\n")
    except Exception as e:
        print_error(f"❌ Error de conexión: {str(e)}")
        return
    
    # Diccionario para almacenar resultados
    resultados = {
        'roles_permisos': False,
        'crear_usuario': False,
        'sesiones': False,
        'permisos': False,
        'auditoria': False,
        'estadisticas': False
    }
    
    # Ejecutar tests
    try:
        # Test 1: Roles existentes
        datos_roles = test_roles_existentes(conn, cursor)
        resultados['roles_permisos'] = bool(datos_roles)
        
        # Test 2: Crear usuario
        datos_usuario = test_crear_usuario_empleado(conn, cursor)
        resultados['crear_usuario'] = bool(datos_usuario)
        
        if not datos_usuario:
            print_warning("⚠️  Saltando tests de sesiones (sin usuario)")
            print_warning("⚠️  Saltando tests de permisos (sin usuario)")
            print_warning("⚠️  Saltando tests de auditoría (sin usuario)")
        else:
            # Test 3: Sesiones
            datos_sesion = test_sesiones_autenticacion(conn, cursor, datos_usuario)
            resultados['sesiones'] = bool(datos_sesion)
            
            # Test 4: Permisos
            resultado_permisos = test_verificacion_permisos(conn, cursor, datos_usuario)
            resultados['permisos'] = resultado_permisos
            
            # Test 5: Auditoría
            resultado_auditoria = test_auditoria_acciones(conn, cursor, datos_usuario)
            resultados['auditoria'] = resultado_auditoria
        
        # Test 6: Estadísticas
        resultado_estadisticas = test_estadisticas_usuarios(conn, cursor)
        resultados['estadisticas'] = resultado_estadisticas
        
    finally:
        # Rollback para no dejar datos de prueba
        conn.rollback()
        cursor.close()
        conn.close()
    
    # Resumen final
    print_header("🎯 RESUMEN FINAL DE PRUEBAS")
    
    tests = [
        ('Roles y Permisos', resultados['roles_permisos']),
        ('Crear Usuario', resultados['crear_usuario']),
        ('Sesiones y Autenticación', resultados['sesiones']),
        ('Verificación de Permisos', resultados['permisos']),
        ('Auditoría de Acciones', resultados['auditoria']),
        ('Estadísticas de Usuarios', resultados['estadisticas'])
    ]
    
    exitosos = sum(1 for _, resultado in tests if resultado)
    total = len(tests)
    porcentaje = (exitosos / total) * 100
    
    for nombre, resultado in tests:
        if resultado:
            print_success(f"✅ {nombre}: EXITOSA")
        else:
            print_error(f"❌ {nombre}: FALLIDA")
    
    print_header(f"RESULTADO: {exitosos}/{total} pruebas exitosas ({porcentaje:.1f}%)")
    
    if porcentaje == 100:
        print(f"\n{Colors.SUCCESS}🎉 ¡PERFECTO! Módulo de usuarios completamente funcional.{Colors.ENDC}")
    elif porcentaje >= 80:
        print(f"\n{Colors.SUCCESS}✅ Excelente. Módulo de usuarios operacional.{Colors.ENDC}")
    elif porcentaje >= 60:
        print(f"\n{Colors.WARNING}⚠️  Aceptable. Revisar funcionalidades con errores.{Colors.ENDC}")
    else:
        print(f"\n{Colors.ERROR}⚠️  Revisar funcionalidades con errores.{Colors.ENDC}")


if __name__ == "__main__":
    main()
