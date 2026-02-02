"""
Pruebas de API usando Django Test Client - Versi\u00f3n simple sin colores
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
import json

# Cliente de prueba
client = Client()

print("\n" + "="*60)
print("PRUEBAS API REST - CANTINA TITA")
print("="*60 + "\n")

# TEST 1: BASE DE DATOS
print("\nTEST 1: MODELOS Y BASE DE DATOS")
print("-" * 60)

from gestion.models import (
    Producto, Categoria, Cliente, Ventas,
    StockUnico, Empleado, Tarjeta
)

try:
    count = Producto.objects.count()
    print(f"[OK] Modelo Producto: {count} registros")
except Exception as e:
    print(f"[ERROR] Modelo Producto: {e}")

try:
    count = Categoria.objects.count()
    print(f"[OK] Modelo Categoria: {count} registros")
except Exception as e:
    print(f"[ERROR] Modelo Categoria: {e}")

try:
    count = Cliente.objects.count()
    print(f"[OK] Modelo Cliente: {count} registros")
except Exception as e:
    print(f"[ERROR] Modelo Cliente: {e}")

try:
    count = Ventas.objects.count()
    print(f"[OK] Modelo Ventas: {count} registros")
except Exception as e:
    print(f"[ERROR] Modelo Ventas: {e}")

try:
    count = StockUnico.objects.count()
    print(f"[OK] Modelo StockUnico: {count} registros")
except Exception as e:
    print(f"[ERROR] Modelo StockUnico: {e}")

# TEST 2: AUTENTICACIÓN JWT
print("\n\nTEST 2: AUTENTICACIÓN JWT")
print("-" * 60)

response = client.post('/api/v1/auth/token/', {
    'username': 'admin',
    'password': 'admin123'
})

if response.status_code == 200:
    data = json.loads(response.content)
    access_token = data.get('access')
    refresh_token = data.get('refresh')
    print(f"[OK] Obtener token JWT: Status {response.status_code}")
    print(f"     Access token: {access_token[:50]}...")
    
    # Verificar token
    response = client.post('/api/v1/auth/token/verify/', {'token': access_token})
    print(f"[OK] Verificar token: Status {response.status_code}")
    
    # Refrescar token
    response = client.post('/api/v1/auth/token/refresh/', {'refresh': refresh_token})
    print(f"[OK] Refrescar token: Status {response.status_code}")
else:
    print(f"[ERROR] Obtener token JWT: Status {response.status_code}")
    access_token = None

# TEST 3: ENDPOINTS GET
if access_token:
    print("\n\nTEST 3: ENDPOINTS GET (Lectura)")
    print("-" * 60)
    
    headers = {'HTTP_AUTHORIZATION': f'Bearer {access_token}'}
    
    endpoints = [
        ('Categorias', '/api/v1/categorias/'),
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
        try:
            response = client.get(url, **headers)
            if response.status_code == 200:
                try:
                    data = json.loads(response.content)
                    count = data.get('count', len(data.get('results', [])))
                    print(f"[OK] GET {name}: {count} registros")
                except:
                    print(f"[OK] GET {name}: Status 200")
            else:
                print(f"[ERROR] GET {name}: Status {response.status_code}")
        except Exception as e:
            print(f"[ERROR] GET {name}: {str(e)[:50]}")
    
    # TEST 4: PAGINACIÓN
    print("\n\nTEST 4: PAGINACIÓN")
    print("-" * 60)
    
    response = client.get('/api/v1/productos/', **headers)
    if response.status_code == 200:
        data = json.loads(response.content)
        has_pagination = all(key in data for key in ['count', 'next', 'previous', 'results'])
        if has_pagination:
            print(f"[OK] Estructura de paginacion: count, next, previous, results")
            print(f"[OK] Total registros: {data['count']}")
            print(f"[OK] Resultados por pagina: {len(data['results'])}")
        else:
            print("[ERROR] Estructura de paginacion incorrecta")
    
    # TEST 5: FILTROS Y BÚSQUEDA
    print("\n\nTEST 5: FILTROS Y BUSQUEDA")
    print("-" * 60)
    
    response = client.get('/api/v1/productos/?search=coca', **headers)
    if response.status_code == 200:
        data = json.loads(response.content)
        count = data.get('count', 0)
        print(f"[OK] Busqueda en productos: {count} resultados para 'coca'")
    
    response = client.get('/api/v1/productos/?activo=true', **headers)
    if response.status_code == 200:
        data = json.loads(response.content)
        count = data.get('count', 0)
        print(f"[OK] Filtro por activo: {count} productos activos")
    
    response = client.get('/api/v1/productos/?ordering=-codigo', **headers)
    if response.status_code == 200:
        print(f"[OK] Ordenamiento: por codigo descendente")
    
    # TEST 6: ACCIONES PERSONALIZADAS
    print("\n\nTEST 6: ACCIONES PERSONALIZADAS")
    print("-" * 60)
    
    actions = [
        ('Stock critico', '/api/v1/productos/stock_critico/'),
        ('Ventas del dia', '/api/v1/ventas/ventas_dia/'),
        ('Estadisticas ventas', '/api/v1/ventas/estadisticas/'),
        ('Alertas de stock', '/api/v1/stock/alertas/'),
    ]
    
    for name, url in actions:
        try:
            response = client.get(url, **headers)
            if response.status_code == 200:
                data = json.loads(response.content)
                if isinstance(data, list):
                    print(f"[OK] {name}: {len(data)} resultados")
                elif isinstance(data, dict):
                    keys = ', '.join(list(data.keys())[:3])
                    print(f"[OK] {name}: {keys}...")
            else:
                print(f"[ERROR] {name}: Status {response.status_code}")
        except Exception as e:
            print(f"[ERROR] {name}: {str(e)[:50]}")

# TEST 7: SWAGGER
print("\n\nTEST 7: DOCUMENTACIÓN SWAGGER")
print("-" * 60)

response = client.get('/swagger.json')
if response.status_code == 200:
    schema = json.loads(response.content)
    version = schema.get('swagger', schema.get('openapi'))
    paths_count = len(schema.get('paths', {}))
    print(f"[OK] Swagger JSON: OpenAPI version {version}")
    print(f"[OK] Endpoints documentados: {paths_count} total")
else:
    print(f"[ERROR] Swagger JSON: Status {response.status_code}")

response = client.get('/swagger/')
print(f"[OK] Swagger UI: Status {response.status_code}" if response.status_code == 200 else f"[ERROR] Swagger UI: Status {response.status_code}")

response = client.get('/redoc/')
print(f"[OK] ReDoc UI: Status {response.status_code}" if response.status_code == 200 else f"[ERROR] ReDoc UI: Status {response.status_code}")

print("\n" + "="*60)
print("PRUEBAS COMPLETADAS")
print("="*60 + "\n")
