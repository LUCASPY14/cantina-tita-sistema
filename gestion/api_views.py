"""
ViewSets para la API REST del sistema Cantina Tita
Proporciona endpoints CRUD completos con filtros y búsqueda
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, Count, Avg
from datetime import datetime, timedelta

from .models import (
    Ventas, DetalleVenta, Producto, Categoria, Cliente, Hijo,
    Tarjeta, CargasSaldo, ConsumoTarjeta, CtaCorriente,
    Empleado, StockUnico, MovimientosStock, Proveedor
)

from .serializers import (
    VentaListSerializer, VentaDetailSerializer,
    ProductoListSerializer, ProductoDetailSerializer,
    CategoriaSerializer, ClienteSerializer, HijoSerializer,
    TarjetaSerializer, CargasSaldoSerializer, ConsumoTarjetaSerializer,
    CtaCorrienteSerializer, EmpleadoSerializer, StockSerializer,
    MovimientoStockSerializer, ProveedorSerializer
)


# =============================================================================
# VIEWSETS DE PRODUCTOS
# =============================================================================

class CategoriaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para categorías de productos
    
    list: Listar todas las categorías
    retrieve: Obtener detalle de una categoría
    create: Crear nueva categoría
    update: Actualizar categoría completa
    partial_update: Actualizar categoría parcialmente
    destroy: Eliminar categoría (soft delete)
    """
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['activo', 'id_categoria_padre']
    search_fields = ['nombre']
    ordering_fields = ['nombre', 'id_categoria']
    ordering = ['nombre']
    
    @action(detail=True, methods=['get'])
    def productos(self, request, pk=None):
        """Obtener todos los productos de una categoría"""
        categoria = self.get_object()
        productos = Producto.objects.filter(
            id_categoria=categoria,
            activo=True
        )
        serializer = ProductoListSerializer(productos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def subcategorias(self, request, pk=None):
        """Obtener subcategorías de una categoría"""
        categoria = self.get_object()
        subcategorias = Categoria.objects.filter(id_categoria_padre=categoria)
        serializer = CategoriaSerializer(subcategorias, many=True)
        return Response(serializer.data)


class ProductoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para productos
    
    list: Listar productos (usa serializer ligero)
    retrieve: Obtener detalle completo de un producto
    create: Crear nuevo producto
    update: Actualizar producto
    destroy: Eliminar producto (soft delete)
    """
    queryset = Producto.objects.select_related('id_categoria').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['activo', 'id_categoria']
    search_fields = ['codigo', 'descripcion']
    ordering_fields = ['codigo', 'descripcion', 'id_categoria']
    ordering = ['codigo']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductoDetailSerializer
        return ProductoListSerializer
    
    @action(detail=True, methods=['get'])
    def stock(self, request, pk=None):
        """Obtener stock actual del producto"""
        producto = self.get_object()
        try:
            stock = StockUnico.objects.get(id_producto=producto)
            serializer = StockSerializer(stock)
            return Response(serializer.data)
        except StockUnico.DoesNotExist:
            return Response(
                {'error': 'Stock no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def stock_critico(self, request):
        """Listar productos con stock crítico"""
        productos_criticos = []
        productos = Producto.objects.filter(activo=True)
        
        for producto in productos:
            try:
                stock = StockUnico.objects.get(id_producto=producto)
                # Validar que stock_minimo no sea None
                if producto.stock_minimo is not None and stock.stock_actual < producto.stock_minimo:
                    productos_criticos.append({
                        'id_producto': producto.id_producto,
                        'codigo': producto.codigo,
                        'descripcion': producto.descripcion,
                        'stock_actual': float(stock.stock_actual),
                        'stock_minimo': float(producto.stock_minimo),
                        'diferencia': float(producto.stock_minimo - stock.stock_actual)
                    })
            except StockUnico.DoesNotExist:
                pass
        
        return Response(productos_criticos)
    
    @action(detail=False, methods=['get'])
    def mas_vendidos(self, request):
        """Productos más vendidos (últimos 30 días)"""
        fecha_inicio = datetime.now() - timedelta(days=30)
        
        productos_vendidos = DetalleVenta.objects.filter(
            id_venta__fecha__gte=fecha_inicio,
            id_venta__estado='Completada'
        ).values(
            'id_producto__id_producto',
            'id_producto__codigo',
            'id_producto__descripcion'
        ).annotate(
            cantidad_vendida=Sum('cantidad'),
            total_ventas=Count('id_venta')
        ).order_by('-cantidad_vendida')[:20]
        
        return Response(productos_vendidos)


# =============================================================================
# VIEWSETS DE CLIENTES Y TARJETAS
# =============================================================================

class ClienteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para clientes
    """
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['activo']
    search_fields = ['nombres', 'apellidos', 'ci_ruc', 'telefono']
    ordering_fields = ['nombres', 'apellidos']
    ordering = ['apellidos', 'nombres']
    
    @action(detail=True, methods=['get'])
    def hijos(self, request, pk=None):
        """Obtener hijos del cliente"""
        cliente = self.get_object()
        hijos = Hijo.objects.filter(id_cliente_responsable=cliente)
        serializer = HijoSerializer(hijos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def cuenta_corriente(self, request, pk=None):
        """Obtener estado de cuenta corriente"""
        cliente = self.get_object()
        movimientos = CtaCorriente.objects.filter(
            id_cliente=cliente
        ).order_by('-fecha')[:50]
        
        saldo_total = CtaCorriente.objects.filter(
            id_cliente=cliente
        ).aggregate(total=Sum('monto'))['total'] or 0
        
        serializer = CtaCorrienteSerializer(movimientos, many=True)
        return Response({
            'saldo_actual': float(saldo_total),
            'movimientos': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def ventas(self, request, pk=None):
        """Obtener historial de ventas del cliente"""
        cliente = self.get_object()
        ventas = Ventas.objects.filter(id_cliente=cliente).order_by('-fecha')[:50]
        serializer = VentaListSerializer(ventas, many=True)
        return Response(serializer.data)


class TarjetaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para tarjetas de estudiantes
    """
    queryset = Tarjeta.objects.select_related('id_hijo__id_cliente_responsable').all()
    serializer_class = TarjetaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['estado']
    search_fields = ['nro_tarjeta', 'id_hijo__nombre', 'id_hijo__apellido']
    lookup_field = 'nro_tarjeta'
    
    @action(detail=True, methods=['get'])
    def consumos(self, request, nro_tarjeta=None):
        """Obtener historial de consumos de la tarjeta"""
        tarjeta = self.get_object()
        consumos = ConsumoTarjeta.objects.filter(
            nro_tarjeta=tarjeta
        ).order_by('-fecha_consumo')[:100]
        
        serializer = ConsumoTarjetaSerializer(consumos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def recargas(self, request, nro_tarjeta=None):
        """Obtener historial de recargas de la tarjeta"""
        tarjeta = self.get_object()
        recargas = CargasSaldo.objects.filter(
            nro_tarjeta=tarjeta
        ).order_by('-fecha_carga')[:50]
        
        serializer = CargasSaldoSerializer(recargas, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def recargar(self, request, nro_tarjeta=None):
        """Recargar saldo en una tarjeta"""
        tarjeta = self.get_object()
        
        # Validar datos
        monto = request.data.get('monto')
        id_cliente = request.data.get('id_cliente_origen')
        
        if not monto or not id_cliente:
            return Response(
                {'error': 'Monto e ID de cliente son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            monto = float(monto)
            if monto <= 0:
                raise ValueError("Monto debe ser positivo")
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Crear recarga
        try:
            cliente = Cliente.objects.get(id_cliente=id_cliente)
            recarga = CargasSaldo.objects.create(
                nro_tarjeta=tarjeta,
                monto_cargado=monto,
                id_cliente_origen=cliente
            )
            
            serializer = CargasSaldoSerializer(recarga)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Cliente.DoesNotExist:
            return Response(
                {'error': 'Cliente no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# =============================================================================
# VIEWSETS DE VENTAS
# =============================================================================

class VentaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para ventas
    """
    queryset = Ventas.objects.select_related('id_cliente', 'id_empleado_cajero').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estado', 'tipo_venta', 'id_tipo_pago']
    search_fields = ['id_cliente__nombres', 'id_cliente__apellidos']
    ordering_fields = ['fecha', 'monto_total']
    ordering = ['-fecha']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return VentaDetailSerializer
        return VentaListSerializer
    
    @action(detail=False, methods=['get'])
    def ventas_dia(self, request):
        """Obtener ventas del día actual"""
        hoy = datetime.now().date()
        ventas = Ventas.objects.filter(
            fecha__date=hoy
        ).order_by('-fecha')
        
        serializer = VentaListSerializer(ventas, many=True)
        
        total_dia = ventas.aggregate(total=Sum('monto_total'))['total'] or 0
        cantidad_ventas = ventas.count()
        
        return Response({
            'fecha': hoy,
            'cantidad_ventas': cantidad_ventas,
            'total_ventas': float(total_dia),
            'ventas': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Estadísticas de ventas"""
        # Parámetros de fecha
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        
        # Filtrar por rango de fechas
        ventas = Ventas.objects.all()
        
        if fecha_inicio:
            ventas = ventas.filter(fecha__gte=fecha_inicio)
        if fecha_fin:
            ventas = ventas.filter(fecha__lte=fecha_fin)
        
        # Calcular estadísticas
        stats = ventas.aggregate(
            total_ventas=Count('id_venta'),
            monto_total_sum=Sum('monto_total')
        )
        
        # Calcular promedio manualmente
        if stats['total_ventas'] and stats['total_ventas'] > 0:
            stats['monto_promedio'] = float(stats['monto_total_sum'] or 0) / stats['total_ventas']
        else:
            stats['monto_promedio'] = 0
        stats['monto_total'] = stats.pop('monto_total_sum')
        
        # Ventas por estado
        por_estado = ventas.values('estado').annotate(
            cantidad=Count('id_venta'),
            monto=Sum('monto_total')
        )
        
        # Ventas por tipo
        por_tipo = ventas.values('tipo_venta').annotate(
            cantidad=Count('id_venta'),
            monto=Sum('monto_total')
        )
        
        return Response({
            'resumen': stats,
            'por_estado': list(por_estado),
            'por_tipo': list(por_tipo)
        })


# =============================================================================
# VIEWSETS DE STOCK
# =============================================================================

class StockViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura para stock
    """
    queryset = StockUnico.objects.select_related('id_producto__id_categoria').all()
    serializer_class = StockSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['id_producto__codigo', 'id_producto__descripcion']
    ordering_fields = ['stock_actual', 'fecha_ultima_actualizacion']
    ordering = ['id_producto__codigo']
    
    @action(detail=False, methods=['get'])
    def alertas(self, request):
        """Productos con stock por debajo del mínimo"""
        alertas = []
        stocks = StockUnico.objects.select_related('id_producto').all()
        
        for stock in stocks:
            # Validar que tanto stock.id_producto como stock_minimo no sean None
            if (stock.id_producto and 
                stock.id_producto.stock_minimo is not None and 
                stock.stock_actual < stock.id_producto.stock_minimo):
                alertas.append({
                    'producto_id': stock.id_producto.id_producto,
                    'codigo': stock.id_producto.codigo,
                    'descripcion': stock.id_producto.descripcion,
                    'stock_actual': float(stock.stock_actual),
                    'stock_minimo': float(stock.id_producto.stock_minimo),
                    'faltante': float(stock.id_producto.stock_minimo - stock.stock_actual)
                })
        
        return Response(alertas)


class MovimientoStockViewSet(viewsets.ModelViewSet):
    """
    ViewSet para movimientos de stock
    """
    queryset = MovimientosStock.objects.select_related(
        'id_producto', 'id_empleado_autoriza'
    ).all()
    serializer_class = MovimientoStockSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['tipo_movimiento', 'id_producto']
    ordering_fields = ['fecha_hora']
    ordering = ['-fecha_hora']


# =============================================================================
# VIEWSETS DE EMPLEADOS
# =============================================================================

class EmpleadoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para empleados
    """
    queryset = Empleado.objects.select_related('id_rol').all()
    serializer_class = EmpleadoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['activo', 'id_rol']
    search_fields = ['nombre', 'apellido', 'usuario']
    
    @action(detail=True, methods=['get'])
    def ventas(self, request, pk=None):
        """Ventas realizadas por el empleado"""
        empleado = self.get_object()
        ventas = Ventas.objects.filter(
            id_empleado_cajero=empleado
        ).order_by('-fecha')[:100]
        
        serializer = VentaListSerializer(ventas, many=True)
        
        total = ventas.aggregate(total=Sum('monto_total'))['total'] or 0
        
        return Response({
            'empleado': EmpleadoSerializer(empleado).data,
            'cantidad_ventas': ventas.count(),
            'total_vendido': float(total),
            'ventas': serializer.data
        })


# =============================================================================
# VIEWSETS DE PROVEEDORES
# =============================================================================

class ProveedorViewSet(viewsets.ModelViewSet):
    """
    ViewSet para proveedores
    """
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['activo']
    search_fields = ['razon_social', 'ruc', 'telefono']
    ordering_fields = ['razon_social']
    ordering = ['razon_social']
