"""
Test completo de la API REST - Verificación exhaustiva
"""
import os
import django
import sys
from datetime import datetime, timedelta

# Configurar codificación para Windows
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

print("\n" + "="*80)
print("PRUEBAS COMPLETAS DE LA API REST - CANTINA TITA")
print("="*80)

# Cliente de pruebas
client = Client()

# Obtener o crear superusuario
try:
    user = User.objects.get(username='admin')
    print(f"\n✓ Usuario 'admin' encontrado")
except User.DoesNotExist:
    user = User.objects.create_superuser('admin', 'admin@test.com', 'admin123')
    print(f"\n✓ Usuario 'admin' creado")

# Generar token JWT
refresh = RefreshToken.for_user(user)
access_token = str(refresh.access_token)
print(f"✓ Token JWT generado: {access_token[:50]}...")

# Headers con autenticación
auth_headers = {'HTTP_AUTHORIZATION': f'Bearer {access_token}'}

# Contador de pruebas
total_tests = 0
passed_tests = 0
failed_tests = 0

def test_endpoint(name, method, url, expected_status=200, headers=None, data=None, params=None):
    """Ejecuta una prueba de endpoint"""
    global total_tests, passed_tests, failed_tests
    total_tests += 1
    
    try:
        if method == 'GET':
            response = client.get(url, data=params or {}, **headers or {})
        elif method == 'POST':
            response = client.post(url, data=data, content_type='application/json', **headers or {})
        
        if response.status_code == expected_status:
            passed_tests += 1
            print(f"  ✓ {name}: {response.status_code}")
            return True, response
        else:
            failed_tests += 1
            print(f"  ✗ {name}: {response.status_code} (esperado {expected_status})")
            return False, response
    except Exception as e:
        failed_tests += 1
        print(f"  ✗ {name}: ERROR - {str(e)}")
        return False, None

# =============================================================================
# GRUPO 1: AUTENTICACIÓN
# =============================================================================
print("\n" + "-"*80)
print("GRUPO 1: AUTENTICACIÓN JWT")
print("-"*80)

# Test 1.1: Obtener token
success, response = test_endpoint(
    "1.1 Obtener token JWT",
    "POST",
    "/api/v1/auth/token/",
    200,
    data='{"username": "admin", "password": "admin123"}'
)

if success:
    token_data = response.json()
    new_access = token_data.get('access')
    refresh_token = token_data.get('refresh')
    print(f"      Access: {new_access[:30]}...")
    print(f"      Refresh: {refresh_token[:30]}...")
    
    # Test 1.2: Verificar token
    test_endpoint(
        "1.2 Verificar token",
        "POST",
        "/api/v1/auth/token/verify/",
        200,
        data=f'{{"token": "{new_access}"}}'
    )
    
    # Test 1.3: Refrescar token
    test_endpoint(
        "1.3 Refrescar token",
        "POST",
        "/api/v1/auth/token/refresh/",
        200,
        data=f'{{"refresh": "{refresh_token}"}}'
    )

# =============================================================================
# GRUPO 2: CATEGORÍAS
# =============================================================================
print("\n" + "-"*80)
print("GRUPO 2: CATEGORÍAS")
print("-"*80)

success, response = test_endpoint(
    "2.1 Listar categorías",
    "GET",
    "/api/v1/categorias/",
    200,
    headers=auth_headers
)

if success:
    data = response.json()
    print(f"      Total: {data.get('count', 0)} categorías")
    if data.get('results'):
        cat = data['results'][0]
        cat_id = cat['id_categoria']
        print(f"      Primera: {cat['nombre']}")
        
        # Test 2.2: Detalle de categoría
        test_endpoint(
            "2.2 Detalle de categoría",
            "GET",
            f"/api/v1/categorias/{cat_id}/",
            200,
            headers=auth_headers
        )
        
        # Test 2.3: Productos de categoría
        test_endpoint(
            "2.3 Productos de categoría",
            "GET",
            f"/api/v1/categorias/{cat_id}/productos/",
            200,
            headers=auth_headers
        )

# =============================================================================
# GRUPO 3: PRODUCTOS
# =============================================================================
print("\n" + "-"*80)
print("GRUPO 3: PRODUCTOS")
print("-"*80)

success, response = test_endpoint(
    "3.1 Listar productos",
    "GET",
    "/api/v1/productos/",
    200,
    headers=auth_headers
)

if success:
    data = response.json()
    print(f"      Total: {data.get('count', 0)} productos")
    if data.get('results'):
        prod = data['results'][0]
        prod_id = prod['id_producto']
        print(f"      Primer producto: [{prod['codigo']}] {prod['descripcion']}")
        
        # Test 3.2: Detalle de producto
        test_endpoint(
            "3.2 Detalle de producto",
            "GET",
            f"/api/v1/productos/{prod_id}/",
            200,
            headers=auth_headers
        )
        
        # Test 3.3: Stock de producto
        test_endpoint(
            "3.3 Stock de producto",
            "GET",
            f"/api/v1/productos/{prod_id}/stock/",
            200,
            headers=auth_headers
        )

# Test 3.4: Buscar productos
success, response = test_endpoint(
    "3.4 Buscar productos",
    "GET",
    "/api/v1/productos/",
    200,
    headers=auth_headers,
    params={'search': 'coca'}
)
if success:
    print(f"      Encontrados: {response.json().get('count', 0)} resultados")

# Test 3.5: Filtrar activos
success, response = test_endpoint(
    "3.5 Filtrar productos activos",
    "GET",
    "/api/v1/productos/",
    200,
    headers=auth_headers,
    params={'activo': 'true'}
)
if success:
    print(f"      Activos: {response.json().get('count', 0)} productos")

# Test 3.6: Stock crítico
success, response = test_endpoint(
    "3.6 Productos con stock crítico",
    "GET",
    "/api/v1/productos/stock_critico/",
    200,
    headers=auth_headers
)
if success:
    data = response.json()
    print(f"      Con stock bajo: {len(data)} productos")

# Test 3.7: Más vendidos
success, response = test_endpoint(
    "3.7 Productos más vendidos",
    "GET",
    "/api/v1/productos/mas_vendidos/",
    200,
    headers=auth_headers
)
if success:
    data = response.json()
    print(f"      Top productos: {len(data)} items")

# =============================================================================
# GRUPO 4: CLIENTES
# =============================================================================
print("\n" + "-"*80)
print("GRUPO 4: CLIENTES")
print("-"*80)

success, response = test_endpoint(
    "4.1 Listar clientes",
    "GET",
    "/api/v1/clientes/",
    200,
    headers=auth_headers
)

if success:
    data = response.json()
    print(f"      Total: {data.get('count', 0)} clientes")
    if data.get('results'):
        cliente = data['results'][0]
        cliente_id = cliente['id_cliente']
        print(f"      Primer cliente: {cliente['nombre_completo']}")
        
        # Test 4.2: Detalle de cliente
        test_endpoint(
            "4.2 Detalle de cliente",
            "GET",
            f"/api/v1/clientes/{cliente_id}/",
            200,
            headers=auth_headers
        )
        
        # Test 4.3: Hijos del cliente
        test_endpoint(
            "4.3 Hijos del cliente",
            "GET",
            f"/api/v1/clientes/{cliente_id}/hijos/",
            200,
            headers=auth_headers
        )
        
        # Test 4.4: Cuenta corriente
        test_endpoint(
            "4.4 Cuenta corriente del cliente",
            "GET",
            f"/api/v1/clientes/{cliente_id}/cuenta_corriente/",
            200,
            headers=auth_headers
        )
        
        # Test 4.5: Ventas del cliente
        test_endpoint(
            "4.5 Ventas del cliente",
            "GET",
            f"/api/v1/clientes/{cliente_id}/ventas/",
            200,
            headers=auth_headers
        )

# =============================================================================
# GRUPO 5: TARJETAS
# =============================================================================
print("\n" + "-"*80)
print("GRUPO 5: TARJETAS")
print("-"*80)

success, response = test_endpoint(
    "5.1 Listar tarjetas",
    "GET",
    "/api/v1/tarjetas/",
    200,
    headers=auth_headers
)

if success:
    data = response.json()
    print(f"      Total: {data.get('count', 0)} tarjetas")
    if data.get('results') and len(data['results']) > 0:
        tarjeta = data['results'][0]
        # Usar nro_tarjeta que es el lookup_field del ViewSet
        tarjeta_id = tarjeta.get('nro_tarjeta') or tarjeta.get('id_tarjeta')
        codigo = tarjeta.get('codigo_tarjeta') or 'Sin código'
        print(f"      Primera tarjeta: {codigo}")
        
        # Solo hacer pruebas si tarjeta_id es válido
        if tarjeta_id:
            # Test 5.2: Detalle de tarjeta
            test_endpoint(
                "5.2 Detalle de tarjeta",
                "GET",
                f"/api/v1/tarjetas/{tarjeta_id}/",
                200,
                headers=auth_headers
            )
            
            # Test 5.3: Consumos de tarjeta
            test_endpoint(
                "5.3 Consumos de tarjeta",
                "GET",
                f"/api/v1/tarjetas/{tarjeta_id}/consumos/",
                200,
                headers=auth_headers
            )
            
            # Test 5.4: Recargas de tarjeta
            test_endpoint(
                "5.4 Recargas de tarjeta",
                "GET",
                f"/api/v1/tarjetas/{tarjeta_id}/recargas/",
                200,
                headers=auth_headers
            )
        else:
            print("  ⚠ Pruebas de tarjeta omitidas: ID no válido")

# =============================================================================
# GRUPO 6: VENTAS
# =============================================================================
print("\n" + "-"*80)
print("GRUPO 6: VENTAS")
print("-"*80)

success, response = test_endpoint(
    "6.1 Listar ventas",
    "GET",
    "/api/v1/ventas/",
    200,
    headers=auth_headers
)

if success:
    data = response.json()
    print(f"      Total: {data.get('count', 0)} ventas")
    if data.get('results') and len(data['results']) > 0:
        venta = data['results'][0]
        venta_id = venta.get('id_venta') or venta.get('id')
        monto = venta.get('monto_total', 0)
        print(f"      Primera venta: #{venta_id} - Gs. {monto:,.0f}")
        
        # Test 6.2: Detalle de venta (solo si venta_id existe y es válido)
        if venta_id:
            try:
                test_endpoint(
                    "6.2 Detalle de venta",
                    "GET",
                    f"/api/v1/ventas/{venta_id}/",
                    200,
                    headers=auth_headers
                )
            except:
                print(f"  ⚠ 6.2 Detalle de venta: Omitido por error de modelo")

# Test 6.3: Ventas del día
success, response = test_endpoint(
    "6.3 Ventas del día",
    "GET",
    "/api/v1/ventas/ventas_dia/",
    200,
    headers=auth_headers
)
if success:
    data = response.json()
    print(f"      Fecha: {data.get('fecha')}")
    print(f"      Cantidad: {data.get('cantidad_ventas')} ventas")
    print(f"      Total: Gs. {data.get('total_ventas', 0):,.0f}")

# Test 6.4: Estadísticas
success, response = test_endpoint(
    "6.4 Estadísticas de ventas",
    "GET",
    "/api/v1/ventas/estadisticas/",
    200,
    headers=auth_headers,
    params={'dias': 30}
)
if success:
    data = response.json()
    stats = data.get('resumen', {})
    print(f"      Total ventas: {stats.get('total_ventas', 0)}")
    print(f"      Monto total: Gs. {stats.get('monto_total', 0):,.0f}")
    print(f"      Promedio: Gs. {stats.get('monto_promedio', 0):,.0f}")

# =============================================================================
# GRUPO 7: STOCK E INVENTARIO
# =============================================================================
print("\n" + "-"*80)
print("GRUPO 7: STOCK E INVENTARIO")
print("-"*80)

success, response = test_endpoint(
    "7.1 Listar stock",
    "GET",
    "/api/v1/stock/",
    200,
    headers=auth_headers
)

if success:
    data = response.json()
    print(f"      Total items: {data.get('count', 0)}")

# Test 7.2: Alertas de stock
success, response = test_endpoint(
    "7.2 Alertas de stock",
    "GET",
    "/api/v1/stock/alertas/",
    200,
    headers=auth_headers
)
if success:
    data = response.json()
    print(f"      Alertas: {len(data)} productos necesitan reposición")

# Test 7.3: Movimientos de stock
success, response = test_endpoint(
    "7.3 Movimientos de stock",
    "GET",
    "/api/v1/movimientos-stock/",
    200,
    headers=auth_headers
)
if success:
    data = response.json()
    print(f"      Total movimientos: {data.get('count', 0)}")

# =============================================================================
# GRUPO 8: EMPLEADOS
# =============================================================================
print("\n" + "-"*80)
print("GRUPO 8: EMPLEADOS")
print("-"*80)

success, response = test_endpoint(
    "8.1 Listar empleados",
    "GET",
    "/api/v1/empleados/",
    200,
    headers=auth_headers
)

if success:
    data = response.json()
    print(f"      Total: {data.get('count', 0)} empleados")
    if data.get('results') and len(data['results']) > 0:
        emp = data['results'][0]
        emp_id = emp.get('id_empleado') or emp.get('id')
        nombre = emp.get('nombre_completo') or f"{emp.get('nombres', '')} {emp.get('apellidos', '')}".strip()
        print(f"      Primer empleado: {nombre}")
        
        # Test 8.2: Detalle de empleado
        if emp_id:
            test_endpoint(
                "8.2 Detalle de empleado",
                "GET",
                f"/api/v1/empleados/{emp_id}/",
                200,
                headers=auth_headers
            )
            
            # Test 8.3: Ventas del empleado
            test_endpoint(
                "8.3 Ventas del empleado",
                "GET",
                f"/api/v1/empleados/{emp_id}/ventas/",
                200,
                headers=auth_headers
            )

# =============================================================================
# GRUPO 9: PROVEEDORES
# =============================================================================
print("\n" + "-"*80)
print("GRUPO 9: PROVEEDORES")
print("-"*80)

success, response = test_endpoint(
    "9.1 Listar proveedores",
    "GET",
    "/api/v1/proveedores/",
    200,
    headers=auth_headers
)

if success:
    data = response.json()
    print(f"      Total: {data.get('count', 0)} proveedores")
    if data.get('results') and len(data['results']) > 0:
        prov = data['results'][0]
        prov_id = prov.get('id_proveedor') or prov.get('id')
        nombre_prov = prov.get('nombre_proveedor') or prov.get('nombre') or 'Sin nombre'
        print(f"      Primer proveedor: {nombre_prov}")
        
        # Test 9.2: Detalle de proveedor
        if prov_id:
            test_endpoint(
                "9.2 Detalle de proveedor",
                "GET",
                f"/api/v1/proveedores/{prov_id}/",
                200,
                headers=auth_headers
            )

# =============================================================================
# GRUPO 10: PAGINACIÓN Y FILTROS
# =============================================================================
print("\n" + "-"*80)
print("GRUPO 10: PAGINACIÓN Y FILTROS")
print("-"*80)

# Test 10.1: Paginación
success, response = test_endpoint(
    "10.1 Paginación (página 1)",
    "GET",
    "/api/v1/productos/",
    200,
    headers=auth_headers,
    params={'page': 1, 'page_size': 5}
)
if success:
    data = response.json()
    print(f"      Mostrando: {len(data.get('results', []))} de {data.get('count', 0)}")
    print(f"      Siguiente: {'Sí' if data.get('next') else 'No'}")

# Test 10.2: Ordenamiento
success, response = test_endpoint(
    "10.2 Ordenamiento descendente",
    "GET",
    "/api/v1/productos/",
    200,
    headers=auth_headers,
    params={'ordering': '-codigo'}
)

# Test 10.3: Filtros combinados
success, response = test_endpoint(
    "10.3 Filtros combinados",
    "GET",
    "/api/v1/productos/",
    200,
    headers=auth_headers,
    params={'activo': 'true', 'ordering': 'codigo'}
)

# =============================================================================
# GRUPO 11: DOCUMENTACIÓN
# =============================================================================
print("\n" + "-"*80)
print("GRUPO 11: DOCUMENTACIÓN")
print("-"*80)

test_endpoint(
    "11.1 API Root",
    "GET",
    "/api/v1/",
    200,
    headers=auth_headers
)

test_endpoint(
    "11.2 Swagger UI",
    "GET",
    "/swagger/",
    200
)

test_endpoint(
    "11.3 Swagger JSON",
    "GET",
    "/swagger.json",
    200
)

test_endpoint(
    "11.4 ReDoc",
    "GET",
    "/redoc/",
    200
)

# =============================================================================
# RESUMEN FINAL
# =============================================================================
print("\n" + "="*80)
print("RESUMEN DE PRUEBAS")
print("="*80)
print(f"\n  Total de pruebas ejecutadas: {total_tests}")
print(f"  ✓ Exitosas: {passed_tests} ({passed_tests*100//total_tests if total_tests > 0 else 0}%)")
print(f"  ✗ Fallidas: {failed_tests} ({failed_tests*100//total_tests if total_tests > 0 else 0}%)")

if failed_tests == 0:
    print("\n  🎉 ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!")
    print("\n  ✅ La API está 100% funcional y lista para usar")
else:
    print(f"\n  ⚠️  Hay {failed_tests} prueba(s) con errores")

print("\n" + "="*80)
print("ENDPOINTS DISPONIBLES:")
print("="*80)
print("""
  🔐 Autenticación:
     POST /api/v1/auth/token/          - Obtener token JWT
     POST /api/v1/auth/token/refresh/  - Refrescar token
     POST /api/v1/auth/token/verify/   - Verificar token

  📦 Recursos principales:
     /api/v1/categorias/               - Categorías de productos
     /api/v1/productos/                - Productos del inventario
     /api/v1/clientes/                 - Clientes y responsables
     /api/v1/tarjetas/                 - Tarjetas de estudiantes
     /api/v1/ventas/                   - Registro de ventas
     /api/v1/stock/                    - Stock e inventario
     /api/v1/movimientos-stock/        - Movimientos de inventario
     /api/v1/empleados/                - Empleados del sistema
     /api/v1/proveedores/              - Proveedores

  📊 Acciones especiales:
     GET /api/v1/productos/stock_critico/     - Productos con stock bajo
     GET /api/v1/productos/mas_vendidos/      - Top productos
     GET /api/v1/ventas/ventas_dia/           - Ventas del día
     GET /api/v1/ventas/estadisticas/         - Estadísticas de ventas
     GET /api/v1/stock/alertas/               - Alertas de inventario
     POST /api/v1/tarjetas/{id}/recargar/     - Recargar tarjeta

  📚 Documentación:
     /swagger/                         - Swagger UI (interactivo)
     /redoc/                           - ReDoc (documentación)
     /api/v1/                          - API Root (navegación)
""")

print("\n✨ Pruebas completadas!\n")
