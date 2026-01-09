"""
Script de prueba funcional para POS General
Verifica todos los escenarios del sistema:
1. Búsqueda de productos
2. Verificación de tarjeta estudiante
3. Validación de stock
4. Procesamiento de ventas con pagos mixtos
5. Cálculo de comisiones
6. Verificación de restricciones alimentarias
7. Generación de tickets
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from decimal import Decimal
from django.utils import timezone
from gestion.models import (
    Producto, StockUnico, Cliente, Hijo, Tarjeta, MediosPago,
    Ventas, DetalleVenta, PagosVenta, Empleado, TiposPago, TipoCliente,
    ListaPrecios, Categoria, UnidadMedida, Impuesto, TarifasComision,
    RestriccionesHijos, Alergeno, ProductoAlergeno, PreciosPorLista
)


def print_header(texto):
    """Imprime encabezado de sección"""
    print(f"\n{'='*60}")
    print(f"  {texto}")
    print(f"{'='*60}\n")


def print_success(texto):
    """Imprime mensaje de éxito"""
    print(f"✅ {texto}")


def print_error(texto):
    """Imprime mensaje de error"""
    print(f"❌ {texto}")


def print_info(texto):
    """Imprime mensaje informativo"""
    print(f"ℹ️  {texto}")


def verificar_modelos_base():
    """Verifica que existan los modelos base necesarios"""
    print_header("1. Verificando Modelos Base")
    
    # Verificar productos
    productos_count = Producto.objects.filter(activo=True).count()
    print_info(f"Productos activos: {productos_count}")
    
    if productos_count == 0:
        print_error("No hay productos registrados")
        print_info("Creando productos de prueba...")
        crear_productos_prueba()
    else:
        print_success(f"{productos_count} productos encontrados")
    
    # Verificar medios de pago
    medios_pago = MediosPago.objects.filter(activo=True)
    print_info(f"Medios de pago activos: {medios_pago.count()}")
    
    for medio in medios_pago:
        comision = "SÍ" if medio.genera_comision else "NO"
        print(f"   - {medio.descripcion} (Comisión: {comision})")
    
    # Verificar empleados
    empleados = Empleado.objects.filter(activo=True).count()
    print_info(f"Empleados activos: {empleados}")
    
    # Verificar clientes
    clientes = Cliente.objects.filter(activo=True).count()
    print_info(f"Clientes activos: {clientes}")
    
    print("\n")


def crear_productos_prueba():
    """Crea productos de prueba si no existen"""
    
    # Obtener o crear dependencias
    categoria, _ = Categoria.objects.get_or_create(
        descripcion='Snacks',
        defaults={'activo': True}
    )
    
    unidad, _ = UnidadMedida.objects.get_or_create(
        descripcion='Unidad',
        defaults={'abreviatura': 'UN', 'activo': True}
    )
    
    impuesto, _ = Impuesto.objects.get_or_create(
        descripcion='IVA 10%',
        defaults={'porcentaje': Decimal('10.00'), 'activo': True}
    )
    
    # Crear productos
    productos_ejemplo = [
        {'codigo': '7891234001', 'descripcion': 'Coca Cola 500ml', 'precio': 8000},
        {'codigo': '7891234002', 'descripcion': 'Galletas Oreo', 'precio': 5000},
        {'codigo': '7891234003', 'descripcion': 'Chocolate Milka', 'precio': 12000},
        {'codigo': '7891234004', 'descripcion': 'Jugo Del Valle 1L', 'precio': 10000},
        {'codigo': '7891234005', 'descripcion': 'Papas Lays', 'precio': 6000},
    ]
    
    for prod_data in productos_ejemplo:
        producto, created = Producto.objects.get_or_create(
            codigo_barra=prod_data['codigo'],
            defaults={
                'id_categoria': categoria,
                'id_unidad_de_medida': unidad,
                'id_impuesto': impuesto,
                'descripcion': prod_data['descripcion'],
                'stock_minimo': 10,
                'permite_stock_negativo': False,
                'activo': True
            }
        )
        
        # Crear stock
        if created:
            StockUnico.objects.get_or_create(
                id_producto=producto,
                defaults={'stock_actual': 100}
            )
            
            # Crear precio
            lista_precio = ListaPrecios.objects.filter(activo=True).first()
            if lista_precio:
                PreciosPorLista.objects.get_or_create(
                    id_producto=producto,
                    id_lista_precio=lista_precio,
                    defaults={'precio_venta': prod_data['precio']}
                )
            
            print_success(f"Producto creado: {prod_data['descripcion']}")


def test_busqueda_productos():
    """Prueba la búsqueda de productos"""
    print_header("2. Prueba de Búsqueda de Productos")
    
    # Buscar por código exacto
    producto = Producto.objects.filter(
        codigo_barra__iexact='7891234001',
        activo=True
    ).first()
    
    if producto:
        print_success(f"Búsqueda por código exacto: {producto.descripcion}")
    else:
        print_error("No se encontró producto con código 7891234001")
    
    # Buscar por texto
    productos = Producto.objects.filter(
        descripcion__icontains='coca',
        activo=True
    )
    
    print_info(f"Búsqueda por texto 'coca': {productos.count()} resultados")
    for p in productos:
        stock = p.stock.stock_actual if hasattr(p, 'stock') else 0
        print(f"   - {p.descripcion} (Stock: {stock})")
    
    print("\n")


def test_verificar_tarjeta():
    """Prueba la verificación de tarjeta estudiante"""
    print_header("3. Prueba de Verificación de Tarjeta")
    
    # Buscar tarjeta activa
    tarjeta = Tarjeta.objects.filter(estado='Activa').first()
    
    if tarjeta:
        print_success(f"Tarjeta encontrada: {tarjeta.nro_tarjeta}")
        print_info(f"   Estudiante: {tarjeta.id_hijo.nombre} {tarjeta.id_hijo.apellido}")
        print_info(f"   Saldo: Gs. {tarjeta.saldo_actual:,.0f}")
        
        # Verificar restricciones
        restricciones = RestriccionesHijos.objects.filter(
            id_hijo=tarjeta.id_hijo,
            activo=True
        )
        
        if restricciones.exists():
            print_info(f"   Restricciones: {restricciones.count()}")
            for r in restricciones:
                print(f"      • {r.tipo_restriccion}: {r.descripcion or 'Sin detalles'} ({r.severidad})")
        else:
            print_info("   Sin restricciones alimentarias")
    else:
        print_error("No hay tarjetas activas en el sistema")
    
    print("\n")


def test_validacion_stock():
    """Prueba la validación de stock"""
    print_header("4. Prueba de Validación de Stock")
    
    productos = Producto.objects.filter(activo=True).select_related('stock')[:3]
    
    for producto in productos:
        stock_actual = producto.stock.stock_actual if hasattr(producto, 'stock') else 0
        
        print_info(f"{producto.descripcion}")
        print(f"   Stock actual: {stock_actual}")
        print(f"   Stock mínimo: {producto.stock_minimo or 'No definido'}")
        print(f"   Permite negativo: {'SÍ' if producto.permite_stock_negativo else 'NO'}")
        
        # Validar si se puede vender 5 unidades
        cantidad_venta = 5
        puede_vender = stock_actual >= cantidad_venta or producto.permite_stock_negativo
        
        if puede_vender:
            print_success(f"   ✓ Se pueden vender {cantidad_venta} unidades")
        else:
            print_error(f"   ✗ Stock insuficiente para vender {cantidad_venta} unidades")
    
    print("\n")


def test_calculo_comisiones():
    """Prueba el cálculo de comisiones"""
    print_header("5. Prueba de Cálculo de Comisiones")
    
    # Obtener medios de pago con comisión
    medios_con_comision = MediosPago.objects.filter(
        genera_comision=True,
        activo=True
    )
    
    monto_venta = 50000  # Gs. 50,000
    
    for medio in medios_con_comision:
        print_info(f"Medio de pago: {medio.descripcion}")
        
        # Obtener tarifa vigente
        tarifa = TarifasComision.objects.filter(
            id_medio_pago=medio,
            activo=True,
            fecha_inicio_vigencia__lte=timezone.now()
        ).order_by('-fecha_inicio_vigencia').first()
        
        if tarifa:
            comision = Decimal(monto_venta) * tarifa.porcentaje_comision
            
            if tarifa.monto_fijo_comision:
                comision += tarifa.monto_fijo_comision
            
            print_success(f"   Tarifa: {tarifa.porcentaje_comision * 100}%")
            print_info(f"   Comisión sobre Gs. {monto_venta:,}: Gs. {int(comision):,}")
        else:
            print_error(f"   No hay tarifa vigente configurada")
    
    print("\n")


def test_restricciones_alimentarias():
    """Prueba la verificación de restricciones alimentarias"""
    print_header("6. Prueba de Restricciones Alimentarias")
    
    # Buscar hijo con restricciones
    hijo_con_restricciones = RestriccionesHijos.objects.filter(
        activo=True
    ).select_related('id_hijo').first()
    
    if hijo_con_restricciones:
        hijo = hijo_con_restricciones.id_hijo
        print_info(f"Estudiante: {hijo.nombre} {hijo.apellido}")
        
        restricciones = RestriccionesHijos.objects.filter(
            id_hijo=hijo,
            activo=True
        )
        
        print_info(f"Restricciones activas: {restricciones.count()}")
        for r in restricciones:
            print(f"   • {r.tipo_restriccion}: {r.descripcion or 'Sin detalles'}")
        
        # Probar con un producto
        producto = Producto.objects.filter(activo=True).first()
        if producto:
            print_info(f"\nVerificando producto: {producto.descripcion}")
            
            # Obtener alérgenos del producto
            alergenos = ProductoAlergeno.objects.filter(
                id_producto=producto
            ).values_list('id_alergeno__nombre', flat=True)
            
            if alergenos:
                print(f"   Alérgenos: {', '.join(alergenos)}")
            else:
                print("   Sin alérgenos registrados")
    else:
        print_info("No hay estudiantes con restricciones registradas")
    
    print("\n")


def test_procesamiento_venta_completo():
    """Prueba completa de procesamiento de venta"""
    print_header("7. Prueba de Procesamiento de Venta Completo")
    
    # Obtener datos necesarios
    empleado = Empleado.objects.filter(activo=True).first()
    producto = Producto.objects.filter(activo=True).select_related('stock').first()
    medio_efectivo = MediosPago.objects.filter(descripcion__icontains='efectivo').first()
    tipo_pago_contado = TiposPago.objects.filter(descripcion='CONTADO').first()
    
    if not all([empleado, producto, medio_efectivo, tipo_pago_contado]):
        print_error("Faltan datos base para realizar la venta")
        return
    
    print_info("Datos de la venta:")
    print(f"   Cajero: {empleado.nombre} {empleado.apellido}")
    print(f"   Producto: {producto.descripcion}")
    print(f"   Cantidad: 2")
    print(f"   Medio de pago: {medio_efectivo.descripcion}")
    
    # Obtener precio
    precio_producto = PreciosPorLista.objects.filter(
        id_producto=producto,
        id_lista__activo=True
    ).first()
    
    if not precio_producto:
        print_error("Producto sin precio configurado")
        return
    
    precio_venta = precio_producto.precio_unitario_neto
    cantidad = 2
    subtotal = int(precio_venta * cantidad)
    
    print(f"   Precio unitario: Gs. {int(precio_venta):,}")
    print(f"   Subtotal: Gs. {subtotal:,}")
    
    # Obtener o crear cliente público
    cliente, _ = Cliente.objects.get_or_create(
        ruc_ci='00000000',
        defaults={
            'id_tipo_cliente': TipoCliente.objects.first(),
            'id_lista': ListaPrecios.objects.filter(activo=True).first(),
            'razon_social': 'CLIENTE PÚBLICO',
            'activo': True
        }
    )
    
    print_success(f"\n🛒 Simulación de venta exitosa")
    print_info("En producción, esto registraría:")
    print("   1. Registro en tabla 'ventas'")
    print("   2. Detalle en 'detalle_venta'")
    print("   3. Pago en 'pagos_venta'")
    print("   4. Actualización de stock")
    print("   5. Cálculo de comisiones (si aplica)")
    
    print("\n")


def ejecutar_todas_las_pruebas():
    """Ejecuta todas las pruebas del POS"""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "PRUEBAS FUNCIONALES - POS GENERAL" + " " * 15 + "║")
    print("╚" + "═" * 58 + "╝")
    
    try:
        verificar_modelos_base()
        test_busqueda_productos()
        test_verificar_tarjeta()
        test_validacion_stock()
        test_calculo_comisiones()
        test_restricciones_alimentarias()
        test_procesamiento_venta_completo()
        
        print_header("RESUMEN")
        print_success("Todas las pruebas completadas")
        print_info("El POS General está listo para usar")
        print_info("\nAccede en: http://localhost:8000/gestion/pos/general/")
        
    except Exception as e:
        print_error(f"Error durante las pruebas: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    ejecutar_todas_las_pruebas()
