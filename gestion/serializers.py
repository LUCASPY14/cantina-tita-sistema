"""
Serializers para la API REST del sistema Cantina Tita
Convierte modelos Django a JSON y viceversa
"""

from rest_framework import serializers
from decimal import Decimal
from django.db.models import Sum, Count
from .models import (
    # Ventas
    Ventas, DetalleVenta, PagosVenta,
    # Productos
    Producto, Categoria, StockUnico, PreciosPorLista,
    # Clientes y Tarjetas
    Cliente, Hijo, Tarjeta, CargasSaldo, ConsumoTarjeta,
    # Cuenta Corriente
    CtaCorriente,
    # Empleados
    Empleado, TipoRolGeneral,
    # Proveedores y Compras
    Proveedor, Compras, DetalleCompra,
    # Documentos
    DocumentosTributarios, TiposPago,
    # Movimientos
    MovimientosStock,
)


# =============================================================================
# SERIALIZERS DE CATEGORÍAS Y PRODUCTOS
# =============================================================================

class CategoriaSerializer(serializers.ModelSerializer):
    """Serializer para categorías de productos"""
    subcategorias = serializers.SerializerMethodField()
    total_productos = serializers.SerializerMethodField()
    
    class Meta:
        model = Categoria
        fields = ['id_categoria', 'nombre', 'activo', 'id_categoria_padre', 
                  'subcategorias', 'total_productos']
        read_only_fields = ['id_categoria']
    
    def get_subcategorias(self, obj):
        if hasattr(obj, 'subcategorias'):
            return obj.subcategorias.count()
        return 0
    
    def get_total_productos(self, obj):
        if hasattr(obj, 'productos'):
            return obj.productos.filter(activo=True).count()
        return 0


class ProductoListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listados de productos"""
    categoria_nombre = serializers.CharField(source='id_categoria.nombre', read_only=True)
    stock_actual = serializers.SerializerMethodField()
    precio_actual = serializers.SerializerMethodField()
    
    class Meta:
        model = Producto
        fields = ['id_producto', 'codigo', 'descripcion', 'categoria_nombre',
                  'stock_minimo', 'stock_actual', 'precio_actual', 'activo']
    
    def get_stock_actual(self, obj):
        try:
            stock = StockUnico.objects.get(id_producto=obj)
            return float(stock.stock_actual)
        except StockUnico.DoesNotExist:
            return 0.0
    
    def get_precio_actual(self, obj):
        try:
            # Obtener precio de lista default (ID_Lista = 1)
            precio = PreciosPorLista.objects.filter(
                id_producto=obj, 
                id_lista_id=1
            ).first()
            if precio:
                return float(precio.precio_unitario_neto)
        except:
            pass
        return 0.0


class ProductoDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para un producto específico"""
    categoria = CategoriaSerializer(source='id_categoria', read_only=True)
    stock_info = serializers.SerializerMethodField()
    precios = serializers.SerializerMethodField()
    
    class Meta:
        model = Producto
        fields = '__all__'
    
    def get_stock_info(self, obj):
        try:
            stock = StockUnico.objects.get(id_producto=obj)
            return {
                'stock_actual': float(stock.stock_actual),
                'fecha_actualizacion': stock.fecha_ultima_actualizacion
            }
        except StockUnico.DoesNotExist:
            return None
    
    def get_precios(self, obj):
        precios = PreciosPorLista.objects.filter(id_producto=obj).select_related('id_lista')
        return [
            {
                'lista': precio.id_lista.nombre_lista,
                'precio': float(precio.precio_unitario_neto)
            }
            for precio in precios
        ]


# =============================================================================
# SERIALIZERS DE CLIENTES Y TARJETAS
# =============================================================================

class ClienteSerializer(serializers.ModelSerializer):
    """Serializer para clientes"""
    nombre_completo = serializers.SerializerMethodField()
    total_hijos = serializers.SerializerMethodField()
    saldo_cuenta_corriente = serializers.SerializerMethodField()
    
    class Meta:
        model = Cliente
        fields = ['id_cliente', 'nombres', 'apellidos', 'nombre_completo',
                  'ruc_ci', 'telefono', 'email', 'direccion', 'activo',
                  'total_hijos', 'saldo_cuenta_corriente']
        read_only_fields = ['id_cliente']
    
    def get_nombre_completo(self, obj):
        return f"{obj.nombres} {obj.apellidos}"
    
    def get_total_hijos(self, obj):
        return Hijo.objects.filter(id_cliente_responsable=obj, activo=True).count()
    
    def get_saldo_cuenta_corriente(self, obj):
        saldo = CtaCorriente.objects.filter(id_cliente=obj).aggregate(
            total=Sum('monto')
        )['total']
        return float(saldo) if saldo else 0.0


class HijoSerializer(serializers.ModelSerializer):
    """Serializer para hijos/estudiantes"""
    responsable_nombre = serializers.CharField(
        source='id_cliente_responsable.nombres', 
        read_only=True
    )
    tiene_tarjeta = serializers.SerializerMethodField()
    
    class Meta:
        model = Hijo
        fields = ['id_hijo', 'nombres', 'apellidos', 'fecha_nacimiento',
                  'id_cliente_responsable', 'responsable_nombre', 
                  'tiene_tarjeta', 'activo']
        read_only_fields = ['id_hijo']
    
    def get_tiene_tarjeta(self, obj):
        return Tarjeta.objects.filter(id_hijo=obj).exists()


class TarjetaSerializer(serializers.ModelSerializer):
    """Serializer para tarjetas"""
    id_tarjeta = serializers.IntegerField(source='nro_tarjeta', read_only=True)
    codigo_tarjeta = serializers.CharField(source='nro_tarjeta', read_only=True)
    estudiante_nombre = serializers.SerializerMethodField()
    responsable_nombre = serializers.SerializerMethodField()
    
    class Meta:
        model = Tarjeta
        fields = ['nro_tarjeta', 'id_tarjeta', 'codigo_tarjeta', 'id_hijo', 
                  'estudiante_nombre', 'responsable_nombre', 'saldo_actual', 
                  'estado', 'fecha_creacion', 'fecha_vencimiento']
        read_only_fields = ['nro_tarjeta', 'id_tarjeta', 'codigo_tarjeta', 'saldo_actual']
    
    def get_estudiante_nombre(self, obj):
        if obj.id_hijo:
            return f"{obj.id_hijo.nombre} {obj.id_hijo.apellido}"
        return None
    
    def get_responsable_nombre(self, obj):
        if obj.id_hijo and obj.id_hijo.id_cliente_responsable:
            return obj.id_hijo.id_cliente_responsable.nombre_completo
        return None


class CargasSaldoSerializer(serializers.ModelSerializer):
    """Serializer para recargas de tarjeta"""
    tarjeta_info = serializers.SerializerMethodField()
    cliente_nombre = serializers.CharField(
        source='id_cliente_origen.nombres', 
        read_only=True
    )
    
    class Meta:
        model = CargasSaldo
        fields = ['id_carga', 'nro_tarjeta', 'tarjeta_info', 
                  'monto_cargado', 'fecha_carga', 'id_cliente_origen',
                  'cliente_nombre']
        read_only_fields = ['id_carga', 'fecha_carga']
    
    def get_tarjeta_info(self, obj):
        if obj.nro_tarjeta and obj.nro_tarjeta.id_hijo:
            return {
                'estudiante': f"{obj.nro_tarjeta.id_hijo.nombre} {obj.nro_tarjeta.id_hijo.apellido}",
                'saldo_actual': float(obj.nro_tarjeta.saldo_actual)
            }
        return None


class ConsumoTarjetaSerializer(serializers.ModelSerializer):
    """Serializer para consumos de tarjeta"""
    tarjeta_info = serializers.SerializerMethodField()
    
    class Meta:
        model = ConsumoTarjeta
        fields = ['id_consumo', 'nro_tarjeta', 'tarjeta_info',
                  'fecha_consumo', 'monto_consumido', 'detalle',
                  'saldo_anterior', 'saldo_posterior']
        read_only_fields = ['id_consumo', 'fecha_consumo', 
                            'saldo_anterior', 'saldo_posterior']
    
    def get_tarjeta_info(self, obj):
        if obj.nro_tarjeta and obj.nro_tarjeta.id_hijo:
            return {
                'nro_tarjeta': obj.nro_tarjeta.nro_tarjeta,
                'estudiante': f"{obj.nro_tarjeta.id_hijo.nombre} {obj.nro_tarjeta.id_hijo.apellido}"
            }
        return None


# =============================================================================
# SERIALIZERS DE VENTAS
# =============================================================================

class DetalleVentaSerializer(serializers.ModelSerializer):
    """Serializer para detalle de venta"""
    producto_codigo = serializers.CharField(source='id_producto.codigo', read_only=True)
    producto_descripcion = serializers.CharField(source='id_producto.descripcion', read_only=True)
    
    class Meta:
        model = DetalleVenta
        fields = ['id_detalle', 'id_producto', 'producto_codigo', 
                  'producto_descripcion', 'cantidad', 'precio_unitario_total',
                  'subtotal_total', 'monto_iva']


class VentaListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listados de ventas"""
    cliente_nombre = serializers.SerializerMethodField()
    cajero_nombre = serializers.CharField(
        source='id_empleado_cajero.nombre', 
        read_only=True
    )
    tipo_pago_descripcion = serializers.CharField(
        source='id_tipo_pago.descripcion',
        read_only=True
    )
    
    class Meta:
        model = Ventas
        fields = ['id_venta', 'fecha', 'cliente_nombre', 'cajero_nombre',
                  'tipo_venta', 'tipo_pago_descripcion', 'monto_total', 'estado']
    
    def get_cliente_nombre(self, obj):
        if obj.id_cliente:
            return f"{obj.id_cliente.nombres} {obj.id_cliente.apellidos}"
        return None


class VentaDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para una venta específica"""
    cliente = ClienteSerializer(source='id_cliente', read_only=True)
    detalles = DetalleVentaSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()
    
    class Meta:
        model = Ventas
        fields = '__all__'
    
    def get_total_items(self, obj):
        return obj.detalles.count()


# =============================================================================
# SERIALIZERS DE CUENTA CORRIENTE
# =============================================================================

class CtaCorrienteSerializer(serializers.ModelSerializer):
    """Serializer para movimientos de cuenta corriente"""
    cliente_nombre = serializers.SerializerMethodField()
    
    class Meta:
        model = CtaCorriente
        fields = ['id_movimiento', 'id_cliente', 'cliente_nombre',
                  'tipo_movimiento', 'monto', 'fecha', 'descripcion',
                  'referencia_doc']
        read_only_fields = ['id_movimiento', 'fecha']
    
    def get_cliente_nombre(self, obj):
        if obj.id_cliente:
            return f"{obj.id_cliente.nombres} {obj.id_cliente.apellidos}"
        return None


# =============================================================================
# SERIALIZERS DE EMPLEADOS
# =============================================================================

class EmpleadoSerializer(serializers.ModelSerializer):
    """Serializer para empleados"""
    nombre_completo = serializers.SerializerMethodField()
    rol_nombre = serializers.CharField(source='id_rol.nombre_rol', read_only=True)
    
    def get_nombre_completo(self, obj):
        """Retorna nombre completo del empleado"""
        return f"{obj.nombre} {obj.apellido}".strip()
    
    class Meta:
        model = Empleado
        fields = ['id_empleado', 'nombre', 'apellido', 'nombre_completo', 'usuario',
                  'id_rol', 'rol_nombre', 'telefono', 'email', 'activo']
        read_only_fields = ['id_empleado', 'contrasena_hash']
        extra_kwargs = {
            'contrasena_hash': {'write_only': True}
        }


# =============================================================================
# SERIALIZERS DE STOCK
# =============================================================================

class StockSerializer(serializers.ModelSerializer):
    """Serializer para stock de productos"""
    producto_codigo = serializers.CharField(source='id_producto.codigo', read_only=True)
    producto_descripcion = serializers.CharField(source='id_producto.descripcion', read_only=True)
    stock_minimo = serializers.DecimalField(
        source='id_producto.stock_minimo',
        max_digits=10,
        decimal_places=3,
        read_only=True
    )
    alerta_stock_bajo = serializers.SerializerMethodField()
    
    class Meta:
        model = StockUnico
        fields = ['id_producto', 'producto_codigo', 'producto_descripcion',
                  'stock_actual', 'stock_minimo', 'fecha_ultima_actualizacion',
                  'alerta_stock_bajo']
    
    def get_alerta_stock_bajo(self, obj):
        if obj.id_producto:
            return obj.stock_actual < obj.id_producto.stock_minimo
        return False


class MovimientoStockSerializer(serializers.ModelSerializer):
    """Serializer para movimientos de stock"""
    producto_descripcion = serializers.CharField(
        source='id_producto.descripcion',
        read_only=True
    )
    empleado_nombre = serializers.CharField(
        source='id_empleado_autoriza.nombre',
        read_only=True
    )
    
    class Meta:
        model = MovimientosStock
        fields = ['id_movimientostock', 'id_producto', 'producto_descripcion',
                  'tipo_movimiento', 'cantidad', 'stock_resultante',
                  'fecha_hora', 'id_empleado_autoriza', 'empleado_nombre',
                  'referencia_documento']
        read_only_fields = ['id_movimientostock', 'fecha_hora']


# =============================================================================
# SERIALIZERS DE PROVEEDORES Y COMPRAS
# =============================================================================

class ProveedorSerializer(serializers.ModelSerializer):
    """Serializer para proveedores"""
    nombre_proveedor = serializers.CharField(source='razon_social', read_only=True)
    total_compras = serializers.SerializerMethodField()
    
    class Meta:
        model = Proveedor
        fields = ['id_proveedor', 'razon_social', 'nombre_proveedor', 'ruc', 
                  'telefono', 'email', 'direccion', 'activo', 'total_compras']
        read_only_fields = ['id_proveedor']
    
    def get_total_compras(self, obj):
        return Compras.objects.filter(id_proveedor=obj).count()
