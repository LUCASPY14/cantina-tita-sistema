"""
Script de demostración de operaciones con la API REST
Muestra ejemplos prácticos de uso de los endpoints
"""
import requests
import json
from datetime import datetime

# Configuración
BASE_URL = 'http://127.0.0.1:8000'
API_URL = f'{BASE_URL}/api/v1'

print("\n" + "="*70)
print("DEMO: USO DE LA API REST - CANTINA TITA")
print("="*70)

# =============================================================================
# PASO 1: AUTENTICACIÓN JWT
# =============================================================================
print("\n[PASO 1] AUTENTICACIÓN JWT")
print("-" * 70)

# Login
print("\n1. Obteniendo token de acceso...")
response = requests.post(f'{API_URL}/auth/token/', json={
    'username': 'admin',
    'password': 'admin123'
})

if response.status_code == 200:
    tokens = response.json()
    access_token = tokens['access']
    refresh_token = tokens['refresh']
    print(f"✓ Token obtenido exitosamente")
    print(f"  Access Token: {access_token[:50]}...")
    print(f"  Refresh Token: {refresh_token[:50]}...")
else:
    print(f"✗ Error al obtener token: {response.status_code}")
    exit()

# Headers para las siguientes peticiones
headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

# =============================================================================
# PASO 2: CONSULTAR DATOS (GET)
# =============================================================================
print("\n\n[PASO 2] CONSULTAR DATOS CON GET")
print("-" * 70)

# 2.1 Listar productos
print("\n2.1. Listando productos (primeros 5)...")
response = requests.get(f'{API_URL}/productos/', headers=headers, params={'page_size': 5})
if response.status_code == 200:
    data = response.json()
    print(f"✓ Total de productos: {data['count']}")
    print(f"  Mostrando: {len(data['results'])} productos")
    for producto in data['results'][:3]:
        print(f"  - [{producto['codigo']}] {producto['descripcion']}")
        print(f"    Stock: {producto.get('stock_actual', 'N/A')} | Precio: Gs. {producto.get('precio_actual', 0):,.0f}")

# 2.2 Buscar producto específico
print("\n2.2. Buscando productos con 'coca'...")
response = requests.get(f'{API_URL}/productos/', headers=headers, params={'search': 'coca'})
if response.status_code == 200:
    data = response.json()
    print(f"✓ Encontrados: {data['count']} resultados")
    for producto in data['results']:
        print(f"  - {producto['descripcion']} (Código: {producto['codigo']})")

# 2.3 Ver detalles de un producto
print("\n2.3. Obteniendo detalles del primer producto...")
response = requests.get(f'{API_URL}/productos/1/', headers=headers)
if response.status_code == 200:
    producto = response.json()
    print(f"✓ Producto encontrado:")
    print(f"  ID: {producto['id_producto']}")
    print(f"  Código: {producto['codigo']}")
    print(f"  Descripción: {producto['descripcion']}")
    print(f"  Activo: {'Sí' if producto['activo'] else 'No'}")

# =============================================================================
# PASO 3: USAR FILTROS Y ORDENAMIENTO
# =============================================================================
print("\n\n[PASO 3] FILTROS Y ORDENAMIENTO")
print("-" * 70)

# 3.1 Filtrar productos activos
print("\n3.1. Filtrando productos activos...")
response = requests.get(f'{API_URL}/productos/', headers=headers, params={
    'activo': 'true',
    'page_size': 3
})
if response.status_code == 200:
    data = response.json()
    print(f"✓ Productos activos: {data['count']}")
    for producto in data['results']:
        print(f"  - {producto['descripcion']}")

# 3.2 Ordenar por código descendente
print("\n3.2. Ordenando productos por código (descendente)...")
response = requests.get(f'{API_URL}/productos/', headers=headers, params={
    'ordering': '-codigo',
    'page_size': 3
})
if response.status_code == 200:
    data = response.json()
    print(f"✓ Primeros 3 productos ordenados:")
    for producto in data['results']:
        print(f"  - [{producto['codigo']}] {producto['descripcion']}")

# =============================================================================
# PASO 4: ACCIONES PERSONALIZADAS
# =============================================================================
print("\n\n[PASO 4] ACCIONES PERSONALIZADAS")
print("-" * 70)

# 4.1 Stock crítico
print("\n4.1. Consultando productos con stock crítico...")
response = requests.get(f'{API_URL}/productos/stock_critico/', headers=headers)
if response.status_code == 200:
    data = response.json()
    if len(data) > 0:
        print(f"✓ Productos con stock bajo: {len(data)}")
        for item in data[:3]:
            print(f"  - {item['descripcion']}")
            print(f"    Stock actual: {item['stock_actual']} | Mínimo: {item['stock_minimo']}")
            print(f"    Faltan: {item['diferencia']} unidades")
    else:
        print("✓ No hay productos con stock crítico")

# 4.2 Ventas del día
print("\n4.2. Consultando ventas del día...")
response = requests.get(f'{API_URL}/ventas/ventas_dia/', headers=headers)
if response.status_code == 200:
    data = response.json()
    print(f"✓ Ventas del día {data['fecha']}:")
    print(f"  Cantidad: {data['cantidad_ventas']} ventas")
    print(f"  Total: Gs. {data['total_ventas']:,.0f}")
    if len(data['ventas']) > 0:
        print(f"  Primera venta:")
        venta = data['ventas'][0]
        print(f"  - ID: {venta['id_venta']} | Cliente: {venta.get('cliente_nombre', 'N/A')}")

# 4.3 Estadísticas de ventas
print("\n4.3. Consultando estadísticas de ventas...")
response = requests.get(f'{API_URL}/ventas/estadisticas/', headers=headers, params={
    'dias': 30
})
if response.status_code == 200:
    data = response.json()
    stats = data['resumen']
    print(f"✓ Estadísticas (últimos 30 días):")
    print(f"  Total ventas: {stats['total_ventas']}")
    print(f"  Monto total: Gs. {stats['monto_total']:,.0f}")
    print(f"  Promedio: Gs. {stats['monto_promedio']:,.0f}")
    
    if len(data['por_estado']) > 0:
        print(f"\n  Por estado:")
        for estado in data['por_estado']:
            print(f"  - {estado['estado'] or 'Sin estado'}: {estado['cantidad']} ventas (Gs. {estado['monto']:,.0f})")

# =============================================================================
# PASO 5: CONSULTAR DATOS RELACIONADOS
# =============================================================================
print("\n\n[PASO 5] DATOS RELACIONADOS")
print("-" * 70)

# 5.1 Clientes con sus hijos
print("\n5.1. Listando clientes...")
response = requests.get(f'{API_URL}/clientes/', headers=headers, params={'page_size': 3})
if response.status_code == 200:
    data = response.json()
    print(f"✓ Total clientes: {data['count']}")
    for cliente in data['results'][:2]:
        print(f"\n  Cliente: {cliente['nombre_completo']}")
        print(f"  RUC/CI: {cliente['ruc_ci']}")
        print(f"  Hijos: {cliente['total_hijos']}")
        print(f"  Saldo cuenta corriente: Gs. {cliente['saldo_cuenta_corriente']:,.0f}")
        
        # Obtener hijos del cliente
        response_hijos = requests.get(
            f"{API_URL}/clientes/{cliente['id_cliente']}/hijos/", 
            headers=headers
        )
        if response_hijos.status_code == 200:
            hijos = response_hijos.json()
            if len(hijos) > 0:
                print(f"  Lista de hijos:")
                for hijo in hijos:
                    print(f"    - {hijo['nombre']} {hijo['apellido']}")

# 5.2 Categorías con productos
print("\n5.2. Categorías con sus productos...")
response = requests.get(f'{API_URL}/categorias/', headers=headers, params={'page_size': 2})
if response.status_code == 200:
    data = response.json()
    for categoria in data['results'][:2]:
        print(f"\n  Categoría: {categoria['nombre']}")
        print(f"  Total productos: {categoria['total_productos']}")
        print(f"  Subcategorías: {categoria['total_subcategorias']}")

# =============================================================================
# PASO 6: PAGINACIÓN
# =============================================================================
print("\n\n[PASO 6] NAVEGACIÓN CON PAGINACIÓN")
print("-" * 70)

print("\n6.1. Navegando páginas de productos...")
page = 1
response = requests.get(f'{API_URL}/productos/', headers=headers, params={
    'page': page,
    'page_size': 5
})

if response.status_code == 200:
    data = response.json()
    print(f"✓ Página {page} de productos:")
    print(f"  Total: {data['count']} productos")
    print(f"  Mostrando: {len(data['results'])} de esta página")
    print(f"  Siguiente página: {'Disponible' if data['next'] else 'No hay más'}")
    print(f"  Página anterior: {'Disponible' if data['previous'] else 'Primera página'}")

# =============================================================================
# PASO 7: INFORMACIÓN DEL STOCK
# =============================================================================
print("\n\n[PASO 7] INFORMACIÓN DE INVENTARIO")
print("-" * 70)

# 7.1 Stock actual
print("\n7.1. Consultando stock disponible...")
response = requests.get(f'{API_URL}/stock/', headers=headers, params={'page_size': 5})
if response.status_code == 200:
    data = response.json()
    print(f"✓ Total items en inventario: {data['count']}")
    print(f"  Mostrando primeros 5:")
    for stock in data['results'][:5]:
        print(f"  - Producto: {stock.get('producto_nombre', 'N/A')}")
        print(f"    Stock actual: {stock['stock_actual']}")
        print(f"    Alerta: {'⚠️ BAJO' if stock.get('alerta_stock_bajo') else '✓ OK'}")

# 7.2 Alertas de stock
print("\n7.2. Verificando alertas de stock...")
response = requests.get(f'{API_URL}/stock/alertas/', headers=headers)
if response.status_code == 200:
    alertas = response.json()
    if len(alertas) > 0:
        print(f"✓ {len(alertas)} productos necesitan reposición:")
        for alerta in alertas[:3]:
            print(f"  - {alerta['descripcion']}")
            print(f"    Faltan: {alerta['faltante']} unidades")
    else:
        print("✓ No hay alertas de stock")

# 7.3 Movimientos de stock
print("\n7.3. Últimos movimientos de stock...")
response = requests.get(f'{API_URL}/movimientos-stock/', headers=headers, params={
    'page_size': 5,
    'ordering': '-fecha_hora'
})
if response.status_code == 200:
    data = response.json()
    print(f"✓ Total movimientos: {data['count']}")
    print(f"  Últimos 3 movimientos:")
    for mov in data['results'][:3]:
        print(f"  - {mov['tipo_movimiento']}: {mov['cantidad']} unidades")
        print(f"    Producto: {mov['producto_descripcion']}")
        print(f"    Stock resultante: {mov['stock_resultante']}")

# =============================================================================
# PASO 8: REFRESCAR TOKEN
# =============================================================================
print("\n\n[PASO 8] REFRESCAR TOKEN JWT")
print("-" * 70)

print("\n8.1. Refrescando token de acceso...")
response = requests.post(f'{API_URL}/auth/token/refresh/', json={
    'refresh': refresh_token
})

if response.status_code == 200:
    new_tokens = response.json()
    new_access = new_tokens['access']
    print(f"✓ Nuevo token obtenido exitosamente")
    print(f"  Nuevo Access Token: {new_access[:50]}...")
    print(f"  Nota: El refresh token se renueva automáticamente")
else:
    print(f"✗ Error al refrescar token: {response.status_code}")

# =============================================================================
# RESUMEN
# =============================================================================
print("\n\n" + "="*70)
print("RESUMEN DE OPERACIONES DEMOSTRADAS")
print("="*70)
print("""
✓ Autenticación JWT (login y refresh)
✓ Consultas GET simples y con detalles
✓ Búsqueda de texto
✓ Filtrado por campos
✓ Ordenamiento de resultados
✓ Acciones personalizadas (stock crítico, ventas del día, estadísticas)
✓ Consultas de datos relacionados (clientes con hijos)
✓ Navegación con paginación
✓ Alertas de inventario
✓ Movimientos de stock

PRÓXIMOS PASOS:
1. Prueba los endpoints en Swagger UI: http://127.0.0.1:8000/swagger/
2. Explora ReDoc para documentación detallada: http://127.0.0.1:8000/redoc/
3. Usa estos ejemplos en tu aplicación móvil o frontend
4. Consulta los permisos por rol en api_permissions.py
""")

print("\n✨ Demo completada exitosamente!\n")
