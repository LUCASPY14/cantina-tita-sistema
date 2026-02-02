# Ejemplos Prácticos de Uso del Sistema

## Acceso a Datos Existentes

### Consultar Productos
```python
from gestion.models_existentes import ProductoExistente, StockUnico, CategoriaDB

# Obtener todos los productos activos
productos = ProductoExistente.objects.filter(activo=True)

# Buscar producto por código
producto = ProductoExistente.objects.get(codigo='P001')

# Productos de una categoría específica
categoria = CategoriaDB.objects.get(nombre='Bebidas')
productos_bebidas = ProductoExistente.objects.filter(id_categoria=categoria)

# Productos con stock
productos_con_stock = ProductoExistente.objects.filter(stock__isnull=False)

# Ver stock de un producto
stock = StockUnico.objects.get(id_producto=producto)
print(f"Stock actual: {stock.stock_actual}")
```

### Consultar Clientes
```python
from gestion.models_existentes import ClienteExistente, TipoCliente, Hijo

# Todos los clientes activos
clientes = ClienteExistente.objects.filter(activo=True)

# Buscar por RUC/CI
cliente = ClienteExistente.objects.get(ruc_ci='1234567')

# Clientes de un tipo específico
tipo_estudiante = TipoCliente.objects.get(nombre_tipo='Estudiante')
estudiantes = ClienteExistente.objects.filter(id_tipo_cliente=tipo_estudiante)

# Cliente con sus hijos
cliente = ClienteExistente.objects.prefetch_related('hijos').get(ruc_ci='1234567')
for hijo in cliente.hijos.all():
    print(f"Hijo: {hijo.nombre} {hijo.apellido}")
```

### Consultar Tarjetas y Saldos
```python
from gestion.models_existentes import Tarjeta, Hijo

# Todas las tarjetas activas
tarjetas_activas = Tarjeta.objects.filter(estado='Activa')

# Tarjeta de un hijo específico
hijo = Hijo.objects.get(nombre='Juan', apellido='Pérez')
tarjeta = Tarjeta.objects.get(id_hijo=hijo)
print(f"Saldo: {tarjeta.saldo_actual}")

# Tarjetas con saldo bajo
saldo_minimo = 50000  # 50,000 Gs
tarjetas_bajo_saldo = Tarjeta.objects.filter(
    saldo_actual__lte=saldo_minimo,
    estado='Activa'
)
```

### Ver Productos con Stock Bajo
```python
from gestion.models_existentes import VistaStockAlerta

# Todos los productos con stock bajo
productos_alerta = VistaStockAlerta.objects.all()

for producto in productos_alerta:
    print(f"{producto.descripcion}: Stock={producto.stock_actual}, Mínimo={producto.stock_minimo}")
```

## Modificar Datos

### Actualizar Stock
```python
from gestion.models_existentes import ProductoExistente, StockUnico
from django.db import transaction

# Incrementar stock (compra)
@transaction.atomic
def agregar_stock(codigo_producto, cantidad):
    producto = ProductoExistente.objects.get(codigo=codigo_producto)
    stock = StockUnico.objects.get(id_producto=producto)
    stock.stock_actual += cantidad
    stock.save()
    print(f"Nuevo stock: {stock.stock_actual}")

# Decrementar stock (venta)
@transaction.atomic
def reducir_stock(codigo_producto, cantidad):
    producto = ProductoExistente.objects.get(codigo=codigo_producto)
    stock = StockUnico.objects.get(id_producto=producto)
    
    if stock.stock_actual >= cantidad:
        stock.stock_actual -= cantidad
        stock.save()
        print(f"Stock actualizado: {stock.stock_actual}")
    else:
        raise ValueError("Stock insuficiente")
```

### Actualizar Saldo de Tarjeta
```python
from gestion.models_existentes import Tarjeta
from django.db import transaction

@transaction.atomic
def recargar_tarjeta(nro_tarjeta, monto):
    tarjeta = Tarjeta.objects.get(nro_tarjeta=nro_tarjeta)
    tarjeta.saldo_actual += monto
    tarjeta.save()
    print(f"Nuevo saldo: {tarjeta.saldo_actual}")

@transaction.atomic
def descontar_tarjeta(nro_tarjeta, monto):
    tarjeta = Tarjeta.objects.get(nro_tarjeta=nro_tarjeta)
    
    if tarjeta.saldo_actual >= monto:
        tarjeta.saldo_actual -= monto
        tarjeta.save()
        print(f"Nuevo saldo: {tarjeta.saldo_actual}")
        return True
    else:
        print("Saldo insuficiente")
        return False
```

### Crear Nuevo Cliente
```python
from gestion.models_existentes import ClienteExistente, TipoCliente, ListaPrecios

def crear_cliente(nombres, apellidos, ruc_ci, tipo='Estudiante'):
    # Obtener tipo de cliente
    tipo_cliente = TipoCliente.objects.get(nombre_tipo=tipo)
    
    # Obtener lista de precios por defecto
    lista_default = ListaPrecios.objects.filter(activo=True).first()
    
    # Crear cliente
    cliente = ClienteExistente.objects.create(
        nombres=nombres,
        apellidos=apellidos,
        ruc_ci=ruc_ci,
        id_tipo_cliente=tipo_cliente,
        id_lista_por_defecto=lista_default,
        activo=True
    )
    
    print(f"Cliente creado: {cliente.nombre_completo}")
    return cliente
```

### Crear Hijo y Tarjeta
```python
from gestion.models_existentes import Hijo, Tarjeta, ClienteExistente
from datetime import date

def crear_hijo_con_tarjeta(cliente_ruc, nombre, apellido, nro_tarjeta, fecha_nacimiento=None):
    # Obtener cliente responsable
    cliente = ClienteExistente.objects.get(ruc_ci=cliente_ruc)
    
    # Crear hijo
    hijo = Hijo.objects.create(
        id_cliente_responsable=cliente,
        nombre=nombre,
        apellido=apellido,
        fecha_nacimiento=fecha_nacimiento,
        activo=True
    )
    
    # Crear tarjeta
    tarjeta = Tarjeta.objects.create(
        nro_tarjeta=nro_tarjeta,
        id_hijo=hijo,
        saldo_actual=0,
        estado='Activa',
        saldo_alerta=50000  # 50,000 Gs
    )
    
    print(f"Hijo y tarjeta creados: {hijo.nombre} {hijo.apellido} - Tarjeta: {nro_tarjeta}")
    return hijo, tarjeta
```

### Crear Producto
```python
from gestion.models_existentes import ProductoExistente, CategoriaDB, UnidadMedida, Impuesto, StockUnico

def crear_producto(codigo, descripcion, categoria_nombre, stock_minimo=10):
    # Obtener referencias
    categoria = CategoriaDB.objects.get(nombre=categoria_nombre)
    unidad = UnidadMedida.objects.get(nombre='Unidad')
    impuesto = Impuesto.objects.get(nombre_impuesto='IVA 10%')
    
    # Crear producto
    producto = ProductoExistente.objects.create(
        codigo=codigo,
        descripcion=descripcion,
        id_categoria=categoria,
        id_unidad=unidad,
        id_impuesto=impuesto,
        stock_minimo=stock_minimo,
        activo=True
    )
    
    # Crear registro de stock
    stock = StockUnico.objects.create(
        id_producto=producto,
        stock_actual=0
    )
    
    print(f"Producto creado: {producto.codigo} - {producto.descripcion}")
    return producto
```

## Consultas Avanzadas

### Reportes
```python
from django.db.models import Sum, Count, Avg
from gestion.models_existentes import ProductoExistente, StockUnico

# Productos por categoría
reporte = ProductoExistente.objects.values(
    'id_categoria__nombre'
).annotate(
    total=Count('id_producto'),
    stock_total=Sum('stock__stock_actual')
)

for item in reporte:
    print(f"{item['id_categoria__nombre']}: {item['total']} productos, Stock: {item['stock_total']}")

# Stock total valorizado (necesitaría precios)
productos = ProductoExistente.objects.select_related('stock').filter(activo=True)
```

### Búsqueda Avanzada
```python
from django.db.models import Q

# Buscar productos por código o descripción
busqueda = 'coca'
productos = ProductoExistente.objects.filter(
    Q(codigo__icontains=busqueda) | Q(descripcion__icontains=busqueda),
    activo=True
)

# Clientes con límite de crédito alto
clientes_premium = ClienteExistente.objects.filter(
    limite_credito__gt=1000000,  # Más de 1 millón
    activo=True
).order_by('-limite_credito')
```

## Shell Interactivo

```bash
# Abrir shell de Django
python manage.py shell
```

```python
# En el shell
from gestion.models_existentes import *

# Contar registros
print(f"Clientes: {ClienteExistente.objects.count()}")
print(f"Productos: {ProductoExistente.objects.count()}")
print(f"Tarjetas: {Tarjeta.objects.count()}")

# Ver primer registro de cada tabla
print(ClienteExistente.objects.first())
print(ProductoExistente.objects.first())
print(Tarjeta.objects.first())
```

## Scripts de Mantenimiento

### Verificar Integridad
```python
from gestion.models_existentes import ProductoExistente, StockUnico

# Productos sin stock
productos_sin_stock = ProductoExistente.objects.filter(
    activo=True,
    stock__isnull=True
)

if productos_sin_stock.exists():
    print("⚠️ Productos sin registro de stock:")
    for p in productos_sin_stock:
        print(f"  - {p.codigo}: {p.descripcion}")
        # Crear registro de stock
        StockUnico.objects.create(id_producto=p, stock_actual=0)
```

### Alertas de Reposición
```python
from gestion.models_existentes import VistaStockAlerta

def generar_alertas_reposicion():
    productos = VistaStockAlerta.objects.all()
    
    if productos.exists():
        print("⚠️ PRODUCTOS QUE NECESITAN REPOSICIÓN:")
        print("=" * 60)
        for p in productos:
            faltante = p.stock_minimo - p.stock_actual
            print(f"{p.codigo:10} {p.descripcion:30} Stock: {p.stock_actual:6.2f} Faltante: {faltante:6.2f}")
    else:
        print("✅ Todos los productos tienen stock adecuado")
```

## Panel de Administración

### Acceso
1. Crear superusuario:
   ```bash
   python manage.py createsuperuser
   ```

2. Iniciar servidor:
   ```bash
   python manage.py runserver
   ```

3. Acceder a:
   - http://127.0.0.1:8000/admin

### Funcionalidades Disponibles
- ✅ Ver y editar clientes existentes
- ✅ Gestionar productos y stock
- ✅ Administrar tarjetas y saldos
- ✅ Consultar empleados
- ✅ Ver alertas de stock bajo
- ✅ Gestionar categorías y proveedores
- ✅ Crear nuevos registros

### Búsqueda en el Admin
El admin permite buscar por:
- Clientes: nombre, apellido, RUC/CI, email
- Productos: código, descripción
- Tarjetas: número de tarjeta, nombre del hijo
- Empleados: nombre, apellido, usuario, email
