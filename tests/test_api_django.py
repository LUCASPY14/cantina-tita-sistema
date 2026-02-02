"""
Pruebas de API usando Django Test Client (sin necesidad de servidor corriendo)
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
import json

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

# Cliente de prueba
client = Client()

# ============================================================================
# TEST 1: AUTENTICACIÓN JWT
# ============================================================================
def test_jwt_authentication():
    print_section("TEST 1: AUTENTICACIÓN JWT")
    
    # Obtener token
    response = client.post('/api/v1/auth/token/', {
        'username': 'admin',
        'password': 'admin123'
    })
    
    success = response.status_code == 200
    print_test("Obtener token JWT", success, f"Status: {response.status_code}")
    
    if success:
        data = json.loads(response.content)
        access_token = data.get('access')
        refresh_token = data.get('refresh')
        print(f"     Access token: {access_token[:50]}...")
        print(f"     Refresh token: {refresh_token[:50]}...")
        
        # Verificar token
        response = client.post('/api/v1/auth/token/verify/', {
            'token': access_token
        })
        print_test("Verificar token", response.status_code == 200)
        
        # Refrescar token
        response = client.post('/api/v1/auth/token/refresh/', {
            'refresh': refresh_token
        })
        print_test("Refrescar token", response.status_code == 200)
        
        return access_token
    
    return None

# ============================================================================
# TEST 2: ENDPOINTS GET
# ============================================================================
def test_get_endpoints(token):
    print_section("TEST 2: ENDPOINTS GET (Lectura)")
    
    headers = {'HTTP_AUTHORIZATION': f'Bearer {token}'}
    
    endpoints = [
        ('Categorías', '/api/v1/categorias/'),
        ('Productos', '/api/v1/productos/'),
        ('Clientes', '/api/v1/clientes/'),
        ('Tarjetas', '/api/v1/tarjetas/'),
        ('Ventas', '/api/v1/ventas/'),
        ('Stock', '/api/v1/stock/'),
        ('Movimientos Stock', '/api/v1/movimientos-stock/'),
        ('Empleados', '/api/v1/empleados/'),
        ('Proveedores', '/api/v1/proveedores/'),
    ]
    
    for name, url in endpoints:
        response = client.get(url, **headers)
        if response.status_code == 200:
            try:
                data = json.loads(response.content)
                count = data.get('count', len(data.get('results', [])))
                print_test(f"GET {name}", True, f"Status: 200 | Registros: {count}")
            except:
                print_test(f"GET {name}", True, f"Status: 200")
        else:
            print_test(f"GET {name}", False, f"Status: {response.status_code}")

# ============================================================================
# TEST 3: PAGINACIÓN
# ============================================================================
def test_pagination(token):
    print_section("TEST 3: PAGINACIÓN")
    
    headers = {'HTTP_AUTHORIZATION': f'Bearer {token}'}
    response = client.get('/api/v1/productos/', **headers)
    
    if response.status_code == 200:
        data = json.loads(response.content)
        has_pagination = all(key in data for key in ['count', 'next', 'previous', 'results'])
        print_test("Estructura de paginación", has_pagination)
        
        if has_pagination:
            print_test("Total registros", True, f"Count: {data['count']}")
            print_test("Resultados por página", True, f"Items: {len(data['results'])}")
            print_test("Link siguiente", data['next'] is not None or data['count'] <= 20)

# ============================================================================
# TEST 4: FILTROS Y BÚSQUEDA
# ============================================================================
def test_filters(token):
    print_section("TEST 4: FILTROS Y BÚSQUEDA")
    
    headers = {'HTTP_AUTHORIZATION': f'Bearer {token}'}
    
    # Búsqueda
    response = client.get('/api/v1/productos/?search=coca', **headers)
    success = response.status_code == 200
    if success:
        data = json.loads(response.content)
        count = data.get('count', 0)
        print_test("Búsqueda en productos", True, f"Resultados: {count}")
    else:
        print_test("Búsqueda en productos", False, f"Status: {response.status_code}")
    
    # Filtro
    response = client.get('/api/v1/productos/?activo=true', **headers)
    success = response.status_code == 200
    if success:
        data = json.loads(response.content)
        count = data.get('count', 0)
        print_test("Filtro por activo", True, f"Productos activos: {count}")
    else:
        print_test("Filtro por activo", False, f"Status: {response.status_code}")
    
    # Ordenamiento
    response = client.get('/api/v1/productos/?ordering=-codigo', **headers)
    print_test("Ordenamiento", response.status_code == 200)

# ============================================================================
# TEST 5: ACCIONES PERSONALIZADAS
# ============================================================================
def test_custom_actions(token):
    print_section("TEST 5: ACCIONES PERSONALIZADAS")
    
    headers = {'HTTP_AUTHORIZATION': f'Bearer {token}'}
    
    actions = [
        ('Stock crítico', '/api/v1/productos/stock_critico/'),
        ('Ventas del día', '/api/v1/ventas/ventas_dia/'),
        ('Estadísticas ventas', '/api/v1/ventas/estadisticas/'),
        ('Alertas de stock', '/api/v1/stock/alertas/'),
    ]
    
    for name, url in actions:
        response = client.get(url, **headers)
        if response.status_code == 200:
            try:
                data = json.loads(response.content)
                if isinstance(data, list):
                    print_test(name, True, f"Resultados: {len(data)}")
                elif isinstance(data, dict):
                    keys = ', '.join(list(data.keys())[:3])
                    print_test(name, True, f"Keys: {keys}...")
            except:
                print_test(name, True, f"Status: 200")
        else:
            print_test(name, False, f"Status: {response.status_code}")

# ============================================================================
# TEST 6: SWAGGER
# ============================================================================
def test_swagger():
    print_section("TEST 6: DOCUMENTACIÓN SWAGGER")
    
    response = client.get('/swagger.json')
    success = response.status_code == 200
    print_test("Swagger JSON", success, f"Status: {response.status_code}")
    
    if success:
        schema = json.loads(response.content)
        version = schema.get('swagger', schema.get('openapi'))
        print_test("OpenAPI version", True, f"Version: {version}")
        
        paths_count = len(schema.get('paths', {}))
        print_test("Endpoints documentados", True, f"Total: {paths_count}")
    
    response = client.get('/swagger/')
    print_test("Swagger UI", response.status_code == 200)
    
    response = client.get('/redoc/')
    print_test("ReDoc UI", response.status_code == 200)

# ============================================================================
# TEST 7: MODELOS Y BASE DE DATOS
# ============================================================================
def test_database():
    print_section("TEST 7: MODELOS Y BASE DE DATOS")
    
    from gestion.models import (
        Producto, Categoria, Cliente, Ventas,
        StockUnico, Empleado, Tarjeta
    )
    
    # Verificar modelos
    try:
        count = Producto.objects.count()
        print_test("Modelo Producto", True, f"Total registros: {count}")
    except Exception as e:
        print_test("Modelo Producto", False, str(e))
    
    try:
        count = Categoria.objects.count()
        print_test("Modelo Categoria", True, f"Total registros: {count}")
    except Exception as e:
        print_test("Modelo Categoria", False, str(e))
    
    try:
        count = Cliente.objects.count()
        print_test("Modelo Cliente", True, f"Total registros: {count}")
    except Exception as e:
        print_test("Modelo Cliente", False, str(e))
    
    try:
        count = Ventas.objects.count()
        print_test("Modelo Ventas", True, f"Total registros: {count}")
    except Exception as e:
        print_test("Modelo Ventas", False, str(e))
    
    try:
        count = StockUnico.objects.count()
        print_test("Modelo StockUnico", True, f"Total registros: {count}")
    except Exception as e:
        print_test("Modelo StockUnico", False, str(e))

# ============================================================================
# MAIN
# ============================================================================
def main():
    print(f"\n{Colors.YELLOW}{'='*60}")
    print("PRUEBAS API REST - CANTINA TITA (Django Test Client)")
    print(f"{'='*60}{Colors.END}")
    
    # Test base de datos
    test_database()
    
    # Test JWT
    token = test_jwt_authentication()
    
    if token:
        # Tests con autenticación
        test_get_endpoints(token)
        test_pagination(token)
        test_filters(token)
        test_custom_actions(token)
    
    # Test Swagger
    test_swagger()
    
    print(f"\n{Colors.YELLOW}{'='*60}")
    print("PRUEBAS COMPLETADAS")
    print(f"{'='*60}{Colors.END}\n")

if __name__ == '__main__':
    main()
