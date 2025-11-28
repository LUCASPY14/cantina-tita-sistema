"""
Script de prueba completo para la API REST
Prueba autenticación JWT, endpoints principales, filtros y acciones personalizadas
"""
import requests
import json
from datetime import datetime

# Configuración
BASE_URL = 'http://127.0.0.1:8000'
API_URL = f'{BASE_URL}/api/v1'

# Credenciales
USERNAME = 'admin'
PASSWORD = 'admin123'

# Colores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name, success, details=''):
    """Imprime resultado de un test"""
    status = f"{Colors.GREEN}✓ PASS{Colors.END}" if success else f"{Colors.RED}✗ FAIL{Colors.END}"
    print(f"{status} - {name}")
    if details:
        print(f"     {details}")

def print_section(title):
    """Imprime encabezado de sección"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"{title}")
    print(f"{'='*60}{Colors.END}\n")

# Variables globales
access_token = None
refresh_token = None

# ============================================================================
# TEST 1: AUTENTICACIÓN JWT
# ============================================================================
def test_jwt_authentication():
    global access_token, refresh_token
    
    print_section("TEST 1: AUTENTICACIÓN JWT")
    
    # 1.1 Obtener token
    try:
        response = requests.post(f'{API_URL}/auth/token/', data={
            'username': USERNAME,
            'password': PASSWORD
        })
        
        if response.status_code == 200:
            data = response.json()
            access_token = data.get('access')
            refresh_token = data.get('refresh')
            print_test("Obtener token JWT", True, f"Access token: {access_token[:50]}...")
        else:
            print_test("Obtener token JWT", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("Obtener token JWT", False, str(e))
        return False
    
    # 1.2 Verificar token
    try:
        response = requests.post(f'{API_URL}/auth/token/verify/', data={
            'token': access_token
        })
        print_test("Verificar token", response.status_code == 200)
    except Exception as e:
        print_test("Verificar token", False, str(e))
    
    # 1.3 Refrescar token
    try:
        response = requests.post(f'{API_URL}/auth/token/refresh/', data={
            'refresh': refresh_token
        })
        if response.status_code == 200:
            new_access = response.json().get('access')
            print_test("Refrescar token", True, f"Nuevo access token: {new_access[:50]}...")
        else:
            print_test("Refrescar token", False, f"Status: {response.status_code}")
    except Exception as e:
        print_test("Refrescar token", False, str(e))
    
    return True

# ============================================================================
# TEST 2: ENDPOINTS GET (Lectura)
# ============================================================================
def test_get_endpoints():
    print_section("TEST 2: ENDPOINTS GET (Lectura)")
    
    headers = {'Authorization': f'Bearer {access_token}'}
    
    endpoints = [
        ('Categorías', f'{API_URL}/categorias/'),
        ('Productos', f'{API_URL}/productos/'),
        ('Clientes', f'{API_URL}/clientes/'),
        ('Tarjetas', f'{API_URL}/tarjetas/'),
        ('Ventas', f'{API_URL}/ventas/'),
        ('Stock', f'{API_URL}/stock/'),
        ('Movimientos Stock', f'{API_URL}/movimientos-stock/'),
        ('Empleados', f'{API_URL}/empleados/'),
        ('Proveedores', f'{API_URL}/proveedores/'),
    ]
    
    for name, url in endpoints:
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                count = data.get('count', len(data.get('results', [])))
                print_test(f"GET {name}", True, f"Registros: {count}")
            else:
                print_test(f"GET {name}", False, f"Status: {response.status_code}")
        except Exception as e:
            print_test(f"GET {name}", False, str(e))

# ============================================================================
# TEST 3: PAGINACIÓN
# ============================================================================
def test_pagination():
    print_section("TEST 3: PAGINACIÓN")
    
    headers = {'Authorization': f'Bearer {access_token}'}
    
    try:
        response = requests.get(f'{API_URL}/productos/', headers=headers)
        if response.status_code == 200:
            data = response.json()
            has_pagination = all(key in data for key in ['count', 'next', 'previous', 'results'])
            print_test("Estructura de paginación", has_pagination)
            
            if has_pagination:
                print_test("Total registros", True, f"Count: {data['count']}")
                print_test("Resultados por página", True, f"Items: {len(data['results'])}")
                print_test("Link siguiente página", data['next'] is not None, f"Next: {data['next']}")
        else:
            print_test("Paginación", False, f"Status: {response.status_code}")
    except Exception as e:
        print_test("Paginación", False, str(e))

# ============================================================================
# TEST 4: FILTROS Y BÚSQUEDA
# ============================================================================
def test_filters_and_search():
    print_section("TEST 4: FILTROS Y BÚSQUEDA")
    
    headers = {'Authorization': f'Bearer {access_token}'}
    
    # 4.1 Búsqueda en productos
    try:
        response = requests.get(f'{API_URL}/productos/?search=coca', headers=headers)
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', 0)
            print_test("Búsqueda en productos", True, f"Resultados para 'coca': {count}")
        else:
            print_test("Búsqueda en productos", False, f"Status: {response.status_code}")
    except Exception as e:
        print_test("Búsqueda en productos", False, str(e))
    
    # 4.2 Filtro por activo
    try:
        response = requests.get(f'{API_URL}/productos/?activo=true', headers=headers)
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', 0)
            print_test("Filtro por activo", True, f"Productos activos: {count}")
        else:
            print_test("Filtro por activo", False, f"Status: {response.status_code}")
    except Exception as e:
        print_test("Filtro por activo", False, str(e))
    
    # 4.3 Ordenamiento
    try:
        response = requests.get(f'{API_URL}/productos/?ordering=-codigo', headers=headers)
        if response.status_code == 200:
            print_test("Ordenamiento", True, "Ordenado por código descendente")
        else:
            print_test("Ordenamiento", False, f"Status: {response.status_code}")
    except Exception as e:
        print_test("Ordenamiento", False, str(e))

# ============================================================================
# TEST 5: ACCIONES PERSONALIZADAS
# ============================================================================
def test_custom_actions():
    print_section("TEST 5: ACCIONES PERSONALIZADAS")
    
    headers = {'Authorization': f'Bearer {access_token}'}
    
    actions = [
        ('Stock crítico', f'{API_URL}/productos/stock_critico/'),
        ('Ventas del día', f'{API_URL}/ventas/ventas_dia/'),
        ('Estadísticas ventas', f'{API_URL}/ventas/estadisticas/'),
        ('Alertas de stock', f'{API_URL}/stock/alertas/'),
    ]
    
    for name, url in actions:
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    count = len(data)
                    print_test(name, True, f"Resultados: {count}")
                elif isinstance(data, dict):
                    keys = ', '.join(list(data.keys())[:3])
                    print_test(name, True, f"Datos: {keys}...")
            else:
                print_test(name, False, f"Status: {response.status_code}")
        except Exception as e:
            print_test(name, False, str(e))

# ============================================================================
# TEST 6: SWAGGER DOCUMENTATION
# ============================================================================
def test_swagger():
    print_section("TEST 6: DOCUMENTACIÓN SWAGGER")
    
    try:
        response = requests.get(f'{BASE_URL}/swagger.json')
        if response.status_code == 200:
            schema = response.json()
            print_test("Swagger JSON", True, f"OpenAPI version: {schema.get('swagger', schema.get('openapi'))}")
            
            paths_count = len(schema.get('paths', {}))
            print_test("Endpoints documentados", True, f"Total: {paths_count} endpoints")
        else:
            print_test("Swagger JSON", False, f"Status: {response.status_code}")
    except Exception as e:
        print_test("Swagger JSON", False, str(e))
    
    try:
        response = requests.get(f'{BASE_URL}/swagger/')
        print_test("Swagger UI", response.status_code == 200)
    except Exception as e:
        print_test("Swagger UI", False, str(e))
    
    try:
        response = requests.get(f'{BASE_URL}/redoc/')
        print_test("ReDoc UI", response.status_code == 200)
    except Exception as e:
        print_test("ReDoc UI", False, str(e))

# ============================================================================
# TEST 7: SERIALIZERS
# ============================================================================
def test_serializers():
    print_section("TEST 7: ESTRUCTURA DE SERIALIZERS")
    
    headers = {'Authorization': f'Bearer {access_token}'}
    
    # Obtener un producto con detalle
    try:
        response = requests.get(f'{API_URL}/productos/', headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get('results'):
                producto = data['results'][0]
                expected_fields = ['id_producto', 'codigo', 'descripcion', 'activo']
                has_fields = all(field in producto for field in expected_fields)
                print_test("Campos de ProductoSerializer", has_fields, 
                          f"Campos: {', '.join(list(producto.keys())[:5])}...")
    except Exception as e:
        print_test("ProductoSerializer", False, str(e))
    
    # Obtener una venta con detalle
    try:
        response = requests.get(f'{API_URL}/ventas/', headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get('results'):
                venta = data['results'][0]
                print_test("Campos de VentaSerializer", True,
                          f"Campos: {', '.join(list(venta.keys())[:5])}...")
    except Exception as e:
        print_test("VentaSerializer", False, str(e))

# ============================================================================
# MAIN
# ============================================================================
def main():
    print(f"\n{Colors.YELLOW}{'='*60}")
    print("PRUEBAS COMPLETAS DE API REST - CANTINA TITA")
    print(f"{'='*60}{Colors.END}")
    print(f"Base URL: {BASE_URL}")
    print(f"API URL: {API_URL}")
    print(f"Usuario: {USERNAME}")
    print(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Verificar que el servidor esté corriendo
    try:
        response = requests.get(BASE_URL, timeout=2)
        print(f"{Colors.GREEN}✓ Servidor Django corriendo{Colors.END}\n")
    except:
        print(f"{Colors.RED}✗ ERROR: Servidor no disponible en {BASE_URL}{Colors.END}")
        print("Por favor, inicia el servidor con: python manage.py runserver")
        return
    
    # Ejecutar tests
    if test_jwt_authentication():
        test_get_endpoints()
        test_pagination()
        test_filters_and_search()
        test_custom_actions()
        test_swagger()
        test_serializers()
    
    print(f"\n{Colors.YELLOW}{'='*60}")
    print("PRUEBAS COMPLETADAS")
    print(f"{'='*60}{Colors.END}\n")

if __name__ == '__main__':
    main()
