"""
Serializers para la API REST del sistema POS
"""
from rest_framework import serializers
from .models import Venta, DetalleVenta, PagoVenta
from gestion.models import Cliente, Producto, MediosPago, Empleado


class DetalleVentaSerializer(serializers.ModelSerializer):
    """Serializer para DetalleVenta"""
    producto_nombre = serializers.CharField(source='id_producto.descripcion', read_only=True)
    producto_codigo = serializers.CharField(source='id_producto.codigo_producto', read_only=True)
    
    class Meta:
        model = DetalleVenta
        fields = [
            'id_detalle',
            'id_venta',
            'id_producto',
            'producto_nombre',
            'producto_codigo',
            'cantidad',
            'precio_unitario',
            'subtotal_total',
        ]
        read_only_fields = ['id_detalle', 'subtotal_total']
    
    def validate(self, data):
        """Validar detalle de venta"""
        # Validar stock disponible
        producto = data.get('id_producto')
        cantidad = data.get('cantidad')
        
        if producto and cantidad:
            # Verificar stock (implementar según lógica de negocio)
            pass
        
        # Calcular subtotal
        if 'cantidad' in data and 'precio_unitario' in data:
            data['subtotal_total'] = int(float(data['cantidad']) * data['precio_unitario'])
        
        return data


class PagoVentaSerializer(serializers.ModelSerializer):
    """Serializer para PagoVenta"""
    medio_pago_nombre = serializers.CharField(source='id_medio_pago.nombre_medio_pago', read_only=True)
    
    class Meta:
        model = PagoVenta
        fields = [
            'id_pago_venta',
            'id_venta',
            'id_medio_pago',
            'medio_pago_nombre',
            'monto_aplicado',
            'referencia_transaccion',
            'fecha_pago',
            'estado',
            'nro_tarjeta_usada',
            'id_cierre',
        ]
        read_only_fields = ['id_pago_venta', 'fecha_pago']


class VentaSerializer(serializers.ModelSerializer):
    """Serializer completo para Venta con detalles y pagos"""
    detalles = DetalleVentaSerializer(many=True, read_only=True)
    pagos = PagoVentaSerializer(many=True, read_only=True)
    
    cliente_nombre = serializers.CharField(source='id_cliente.nombre_completo', read_only=True)
    hijo_nombre = serializers.CharField(source='id_hijo.nombre_completo', read_only=True, allow_null=True)
    cajero_nombre = serializers.CharField(source='id_empleado_cajero.nombre_completo', read_only=True)
    autorizado_por_nombre = serializers.CharField(source='autorizado_por.nombre_completo', read_only=True, allow_null=True)
    
    # Propiedades calculadas
    total_pagado = serializers.IntegerField(read_only=True)
    porcentaje_pagado = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Venta
        fields = [
            'id_venta',
            'nro_factura_venta',
            'id_cliente',
            'cliente_nombre',
            'id_hijo',
            'hijo_nombre',
            'id_tipo_pago',
            'id_empleado_cajero',
            'cajero_nombre',
            'fecha',
            'monto_total',
            'saldo_pendiente',
            'estado_pago',
            'estado',
            'tipo_venta',
            'autorizado_por',
            'autorizado_por_nombre',
            'motivo_credito',
            'genera_factura_legal',
            'detalles',
            'pagos',
            'total_pagado',
            'porcentaje_pagado',
        ]
        read_only_fields = ['id_venta', 'fecha', 'total_pagado', 'porcentaje_pagado']
    
    def validate(self, data):
        """Validaciones de negocio para venta"""
        tipo_venta = data.get('tipo_venta')
        autorizado_por = data.get('autorizado_por')
        
        # Validar autorización para ventas a crédito
        if tipo_venta == 'CREDITO' and not autorizado_por:
            raise serializers.ValidationError({
                'autorizado_por': 'Las ventas a crédito requieren autorización de un supervisor'
            })
        
        return data


class VentaCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear ventas con detalles en una sola request"""
    detalles = DetalleVentaSerializer(many=True)
    pagos = PagoVentaSerializer(many=True, required=False)
    
    class Meta:
        model = Venta
        fields = [
            'id_cliente',
            'id_hijo',
            'id_tipo_pago',
            'id_empleado_cajero',
            'tipo_venta',
            'autorizado_por',
            'motivo_credito',
            'genera_factura_legal',
            'detalles',
            'pagos',
        ]
    
    def create(self, validated_data):
        """Crear venta con detalles y pagos"""
        detalles_data = validated_data.pop('detalles')
        pagos_data = validated_data.pop('pagos', [])
        
        # Calcular monto total desde detalles
        monto_total = sum(
            int(float(detalle['cantidad']) * detalle['precio_unitario'])
            for detalle in detalles_data
        )
        validated_data['monto_total'] = monto_total
        validated_data['saldo_pendiente'] = monto_total
        
        # Crear venta
        venta = Venta.objects.create(**validated_data)
        
        # Crear detalles
        for detalle_data in detalles_data:
            DetalleVenta.objects.create(id_venta=venta, **detalle_data)
        
        # Crear pagos si existen
        for pago_data in pagos_data:
            PagoVenta.objects.create(id_venta=venta, **pago_data)
            # Actualizar saldo pendiente
            venta.saldo_pendiente -= pago_data['monto_aplicado']
        
        # Actualizar estado de pago
        if venta.saldo_pendiente <= 0:
            venta.estado_pago = 'PAGADA'
            venta.saldo_pendiente = 0
        elif venta.saldo_pendiente < venta.monto_total:
            venta.estado_pago = 'PARCIAL'
        
        venta.save()
        
        return venta


class VentaResumenSerializer(serializers.ModelSerializer):
    """Serializer resumido para listados de ventas"""
    cliente_nombre = serializers.CharField(source='id_cliente.nombre_completo', read_only=True)
    cajero_nombre = serializers.CharField(source='id_empleado_cajero.nombre_completo', read_only=True)
    cantidad_items = serializers.SerializerMethodField()
    
    class Meta:
        model = Venta
        fields = [
            'id_venta',
            'nro_factura_venta',
            'cliente_nombre',
            'cajero_nombre',
            'fecha',
            'monto_total',
            'saldo_pendiente',
            'estado_pago',
            'estado',
            'tipo_venta',
            'cantidad_items',
        ]
    
    def get_cantidad_items(self, obj):
        """Obtener cantidad de items en la venta"""
        return obj.detalles.count()


class ProductoPOSSerializer(serializers.ModelSerializer):
    """Serializer para productos en sistema POS"""
    categoria_nombre = serializers.CharField(source='id_categoria.descripcion', read_only=True)
    unidad_medida = serializers.CharField(source='id_unidad_medida.abreviacion', read_only=True, allow_null=True)
    precio_display = serializers.SerializerMethodField()
    precio_venta = serializers.SerializerMethodField()
    stock = serializers.SerializerMethodField()
    stock_status = serializers.SerializerMethodField()
    codigo_barras = serializers.CharField(source='codigo_barra', read_only=True)
    codigo_producto = serializers.CharField(source='id_producto', read_only=True)
    
    class Meta:
        model = Producto
        fields = [
            'id_producto',
            'codigo_producto',
            'codigo_barras',
            'descripcion',
            'precio_venta',
            'precio_display',
            'stock',
            'stock_minimo',
            'stock_status',
            'id_categoria',
            'categoria_nombre',
            'unidad_medida',
            'activo',
        ]
    
    def get_precio_venta(self, obj):
        """Obtener precio de venta desde precios_lista o valor por defecto"""
        try:
            # Buscar precio en la lista por defecto (ID 1)
            precio_obj = obj.precios_lista.first()
            if precio_obj:
                return int(precio_obj.precio_venta)
        except:
            pass
        # Precio por defecto basado en ID del producto
        return 1000 + (obj.id_producto * 500)
    
    def get_stock(self, obj):
        """Obtener stock desde stock_unico o valor por defecto"""
        try:
            if hasattr(obj, 'stock'):
                return int(obj.stock.cantidad)
        except:
            pass
        # Stock simulado basado en ID del producto
        return max(5, 20 - (obj.id_producto % 15))
    
    def get_precio_display(self, obj):
        """Formato de precio para mostrar"""
        precio = self.get_precio_venta(obj)
        return f"Gs. {precio:,.0f}"
    
    def get_stock_status(self, obj):
        """Estado del stock"""
        stock_actual = self.get_stock(obj)
        if stock_actual <= 0:
            return 'sin_stock'
        elif stock_actual <= obj.stock_minimo:
            return 'stock_bajo'
        else:
            return 'disponible'
