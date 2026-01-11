"""
ViewSets para la API REST del sistema Cantina Tita
Proporciona endpoints CRUD completos con filtros y búsqueda
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response as DRFResponse
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, Count, Avg, F
from datetime import datetime, timedelta
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# drf-spectacular para OpenAPI 3.0
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from .models import (
    Ventas, DetalleVenta, Producto, Categoria, Cliente, Hijo,
    Tarjeta, CargasSaldo, ConsumoTarjeta,
    Empleado, StockUnico, MovimientosStock, Proveedor
)

from .serializers import (
    VentaListSerializer, VentaDetailSerializer,
    ProductoListSerializer, ProductoDetailSerializer,
    CategoriaSerializer, ClienteSerializer, HijoSerializer,
    TarjetaSerializer, CargasSaldoSerializer, ConsumoTarjetaSerializer,
    EmpleadoSerializer, StockSerializer,
    MovimientoStockSerializer, ProveedorSerializer
)

from .pagination import StandardPagination, LargePagination, SmallPagination, ReportPagination


# =============================================================================
# VIEWSETS DE PRODUCTOS
# =============================================================================

@extend_schema_view(
    list=extend_schema(
        summary="Listar categorías",
        description="Obtiene todas las categorías de productos con opción de filtrar por estado (activo/inactivo) y categoría padre.",
        tags=['Productos']
    ),
    retrieve=extend_schema(
        summary="Obtener categoría",
        description="Obtiene el detalle de una categoría específica por ID.",
        tags=['Productos']
    ),
    create=extend_schema(
        summary="Crear categoría",
        description="Crea una nueva categoría de productos.",
        tags=['Productos']
    ),
    update=extend_schema(
        summary="Actualizar categoría",
        description="Actualiza una categoría existente.",
        tags=['Productos']
    ),
    destroy=extend_schema(
        summary="Eliminar categoría",
        description="Elimina una categoría del sistema.",
        tags=['Productos']
    ),
)
class CategoriaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para categorías de productos.
    
    Permite gestionar las categorías de productos del sistema:
    - Listar todas las categorías con filtros y búsqueda
    - Crear, actualizar y eliminar categorías
    - Obtener productos por categoría
    """
    queryset = Categoria.objects.select_related('id_categoria_padre').all()
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['activo', 'id_categoria_padre']
    search_fields = ['nombre']
    ordering_fields = ['nombre', 'id_categoria']
    ordering = ['nombre']
    
    @extend_schema(
        summary="Obtener productos de la categoría",
        description="Obtiene todos los productos activos que pertenecen a esta categoría.",
        responses={200: ProductoListSerializer(many=True)},
        tags=['Productos']
    )
    @action(detail=True, methods=['get'])
    def productos(self, request, pk=None):
        """Obtener todos los productos de una categoría"""
        categoria = self.get_object()
        productos = Producto.objects.filter(
            id_categoria=categoria,
            activo=True
        ).select_related('id_categoria')
        serializer = ProductoListSerializer(productos, many=True)
        return Response(serializer.data)


# API root público (no requiere autenticación) — mantiene permisos globales intactos
@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """Raíz pública de la API v1 que devuelve información mínima."""
    print('DEBUG: api_root called')
    return DRFResponse({
        'message': 'Cantina Tita API v1',
        'documentation': '/swagger/'
    })
    
    @extend_schema(
        summary="Obtener subcategorías",
        description="Obtiene las categorías hijas que tienen como padre esta categoría.",
        responses={200: CategoriaSerializer(many=True)},
        tags=['Productos']
    )
    @action(detail=True, methods=['get'])
    def subcategorias(self, request, pk=None):
        """Obtener subcategorías de una categoría"""
        categoria = self.get_object()
        subcategorias = Categoria.objects.filter(id_categoria_padre=categoria)
        serializer = CategoriaSerializer(subcategorias, many=True)
        return Response(serializer.data)


class ProductoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para productos del inventario.
    
    Permite gestionar el catálogo de productos:
    - Listar productos con filtros por categoría y estado
    - Búsqueda por código o descripción
    - Ver stock actual y movimientos
    - Crear, actualizar y eliminar productos
    """
    queryset = Producto.objects.select_related('id_categoria').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['activo', 'id_categoria']
    search_fields = ['codigo_barra', 'descripcion']
    ordering_fields = ['codigo_barra', 'descripcion', 'id_categoria']
    ordering = ['descripcion']
    pagination_class = LargePagination  # 50 items por página
    
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
        """Listar productos con stock crítico (OPTIMIZADO - 1 query)"""
        # Query optimizado usando join con select_related
        productos_criticos = Producto.objects.filter(
            activo=True,
            stock_minimo__isnull=False
        ).select_related('stock').exclude(
            stock__stock_actual__gte=F('stock_minimo')
        ).values(
            'id_producto',
            'codigo_barra',
            'descripcion',
            'stock__stock_actual',
            'stock_minimo'
        ).annotate(
            stock_actual=F('stock__stock_actual'),
            diferencia=F('stock_minimo') - F('stock__stock_actual')
        )
        
        # Formatear respuesta
        resultado = [
            {
                'id_producto': p['id_producto'],
                'codigo': p['codigo_barra'] or 'N/A',
                'descripcion': p['descripcion'],
                'stock_actual': float(p['stock_actual'] or 0),
                'stock_minimo': float(p['stock_minimo']),
                'diferencia': float(p['diferencia'] or 0)
            }
            for p in productos_criticos
        ]
        
        return Response(resultado)
    
    @action(detail=False, methods=['get'])
    def mas_vendidos(self, request):
        """Productos más vendidos (últimos 30 días)"""
        fecha_inicio = datetime.now() - timedelta(days=30)
        
        productos_vendidos = DetalleVenta.objects.filter(
            id_venta__fecha__gte=fecha_inicio,
            id_venta__estado='Completada'
        ).values(
            'id_producto__id_producto',
            'id_producto__codigo_barra',
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
    ViewSet para clientes del sistema.
    
    Permite gestionar clientes y sus operaciones:
    - Listar clientes con búsqueda por nombre, CI/RUC, teléfono
    - Ver hijos asociados a cada cliente
    - Consultar cuenta corriente y ventas pendientes
    - Ver historial de ventas y estadísticas
    """
    queryset = Cliente.objects.select_related('id_tipo_cliente').prefetch_related('hijos').all()
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['activo']
    search_fields = ['nombres', 'apellidos', 'ci_ruc', 'telefono']
    ordering_fields = ['nombres', 'apellidos']
    ordering = ['apellidos', 'nombres']
    pagination_class = StandardPagination  # 25 items por página
    
    @swagger_auto_schema(
        operation_description="Obtiene la lista de hijos asociados a un cliente",
        responses={200: HijoSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def hijos(self, request, pk=None):
        """Obtener hijos del cliente"""
        cliente = self.get_object()
        hijos = Hijo.objects.filter(
            id_cliente_responsable=cliente
        ).select_related('id_cliente_responsable')
        serializer = HijoSerializer(hijos, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="Obtiene el estado de cuenta corriente del cliente con saldo pendiente",
        responses={
            200: openapi.Response(
                description="Estado de cuenta",
                examples={
                    'application/json': {
                        'saldo_actual': 150000.00,
                        'ventas_pendientes': []
                    }
                }
            )
        }
    )
    @action(detail=True, methods=['get'])
    def cuenta_corriente(self, request, pk=None):
        """Obtener estado de cuenta corriente (saldo pendiente en ventas)"""
        cliente = self.get_object()
        
        # Obtener ventas con saldo pendiente (1 query optimizado)
        ventas_pendientes = Ventas.objects.filter(
            id_cliente=cliente,
            estado_pago__in=['PENDIENTE', 'PARCIAL']
        ).select_related(
            'id_cliente', 'id_empleado_cajero', 'id_tipo_pago'
        ).prefetch_related(
            'detalleventa_set__id_producto'
        ).order_by('-fecha')[:50]
        
        # Calcular saldo total usando Python para evitar query duplicada
        saldo_total = sum(v.saldo_pendiente or 0 for v in ventas_pendientes)
        
        serializer = VentaListSerializer(ventas_pendientes, many=True)
        return Response({
            'saldo_actual': float(saldo_total),
            'ventas_pendientes': serializer.data
        })
    
    @swagger_auto_schema(
        operation_description="Obtiene el historial de ventas del cliente (hasta 50 últimas)",
        responses={200: VentaListSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def ventas(self, request, pk=None):
        """Obtener historial de ventas del cliente"""
        cliente = self.get_object()
        ventas = Ventas.objects.filter(
            id_cliente=cliente
        ).select_related(
            'id_cliente', 'id_empleado_cajero', 'id_tipo_pago'
        ).prefetch_related(
            'detalleventa_set__id_producto__id_categoria',
            'pagos__id_medio_pago'
        ).order_by('-fecha')[:50]
        serializer = VentaListSerializer(ventas, many=True)
        return Response(serializer.data)


class TarjetaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para tarjetas estudiantiles.
    
    Gestiona las tarjetas de los estudiantes:
    - Listar tarjetas con filtros por estado
    - Búsqueda por número de tarjeta o nombre del hijo
    - Ver saldo actual de la tarjeta
    - Consultar historial de consumos y recargas
    - Realizar recargas de saldo
    """
    queryset = Tarjeta.objects.select_related('id_hijo__id_cliente_responsable').all()
    serializer_class = TarjetaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['estado']
    search_fields = ['nro_tarjeta', 'id_hijo__nombre', 'id_hijo__apellido']
    lookup_field = 'nro_tarjeta'
    pagination_class = StandardPagination  # 25 items por página
    
    @swagger_auto_schema(
        operation_description="Obtiene el historial de consumos de la tarjeta (hasta 100 últimos)",
        responses={200: ConsumoTarjetaSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def consumos(self, request, nro_tarjeta=None):
        """Obtener historial de consumos de la tarjeta"""
        tarjeta = self.get_object()
        consumos = ConsumoTarjeta.objects.filter(
            nro_tarjeta=tarjeta
        ).select_related('nro_tarjeta__id_hijo').order_by('-fecha_consumo')[:100]
        
        serializer = ConsumoTarjetaSerializer(consumos, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="Obtiene el historial de recargas de saldo de la tarjeta (hasta 50 últimas)",
        responses={200: CargasSaldoSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def recargas(self, request, nro_tarjeta=None):
        """Obtener historial de recargas de la tarjeta"""
        tarjeta = self.get_object()
        recargas = CargasSaldo.objects.filter(
            nro_tarjeta=tarjeta
        ).select_related('nro_tarjeta__id_hijo', 'id_empleado_cajero').order_by('-fecha_carga')[:50]
        
        serializer = CargasSaldoSerializer(recargas, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="Realiza una recarga de saldo en la tarjeta",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['monto', 'id_cliente_origen'],
            properties={
                'monto': openapi.Schema(type=openapi.TYPE_NUMBER, description='Monto a recargar'),
                'id_cliente_origen': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID del cliente que realiza la recarga'),
            }
        ),
        responses={
            201: CargasSaldoSerializer(),
            400: "Datos inválidos"
        }
    )
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
    ViewSet para ventas del sistema.
    
    Gestiona las operaciones de venta:
    - Listar ventas con filtros por estado, tipo, y método de pago
    - Ver detalles completos de cada venta
    - Consultar ventas del día actual
    - Obtener estadísticas de ventas por período
    """
    queryset = Ventas.objects.select_related(
        'id_cliente',
        'id_empleado_cajero',
        'id_tipo_pago',
        'id_hijo'
    ).prefetch_related(
        'detalleventa_set__id_producto',
        'pagos__id_medio_pago'
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estado', 'tipo_venta', 'id_tipo_pago']
    search_fields = ['id_cliente__nombres', 'id_cliente__apellidos']
    ordering_fields = ['fecha', 'monto_total']
    ordering = ['-fecha']
    pagination_class = StandardPagination  # 25 items por página
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return VentaDetailSerializer
        return VentaListSerializer
    
    @swagger_auto_schema(
        operation_description="Obtiene todas las ventas realizadas en el día actual con totales",
        responses={
            200: openapi.Response(
                description="Ventas del día",
                examples={
                    'application/json': {
                        'fecha': '2025-12-03',
                        'cantidad_ventas': 45,
                        'total_ventas': 1250000.00,
                        'ventas': []
                    }
                }
            )
        }
    )
    @action(detail=False, methods=['get'])
    def ventas_dia(self, request):
        """Obtener ventas del día actual (OPTIMIZADO)"""
        hoy = datetime.now().date()
        ventas = Ventas.objects.filter(
            fecha__date=hoy
        ).select_related(
            'id_cliente',
            'id_empleado_cajero',
            'id_tipo_pago'
        ).prefetch_related(
            'detalleventa_set__id_producto'
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
    
    @swagger_auto_schema(
        operation_description="Obtiene estadísticas de ventas por período",
        manual_parameters=[
            openapi.Parameter(
                'fecha_inicio',
                openapi.IN_QUERY,
                description="Fecha de inicio (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE
            ),
            openapi.Parameter(
                'fecha_fin',
                openapi.IN_QUERY,
                description="Fecha de fin (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE
            ),
        ],
        responses={
            200: openapi.Response(
                description="Estadísticas calculadas",
                examples={
                    'application/json': {
                        'total_ventas': 5000000.00,
                        'cantidad_ventas': 120,
                        'promedio_venta': 41666.67,
                        'ventas_pendientes': 15
                    }
                }
            )
        }
    )
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
    ViewSet de solo lectura para consultar stock.
    
    Permite:
    - Listar stock actual de todos los productos
    - Búsqueda por código o descripción de producto
    - Ver alertas de stock bajo
    - Consultar movimientos de stock
    """
    queryset = StockUnico.objects.select_related('id_producto__id_categoria').all()
    serializer_class = StockSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['id_producto__codigo', 'id_producto__descripcion']
    ordering_fields = ['stock_actual', 'fecha_ultima_actualizacion']
    ordering = ['id_producto__codigo']
    
    @swagger_auto_schema(
        operation_description="Obtiene productos con stock bajo (menor al stock mínimo configurado)",
        responses={200: StockSerializer(many=True)}
    )
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
                    'codigo': stock.id_producto.codigo_barra or 'N/A',
                    'descripcion': stock.id_producto.descripcion,
                    'stock_actual': float(stock.stock_actual),
                    'stock_minimo': float(stock.id_producto.stock_minimo),
                    'faltante': float(stock.id_producto.stock_minimo - stock.stock_actual)
                })
        
        return Response(alertas)


class MovimientoStockViewSet(viewsets.ModelViewSet):
    """
    ViewSet para registrar movimientos de stock.
    
    Permite:
    - Listar movimientos de entrada y salida
    - Filtrar por tipo de movimiento y producto
    - Registrar nuevos ajustes de stock
    - Ver historial de movimientos
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
    ViewSet para empleados del sistema.
    
    Gestiona los empleados y cajeros:
    - Listar empleados con filtros por rol y estado
    - Ver ventas realizadas por cada empleado
    - Gestionar usuarios y permisos
    """
    queryset = Empleado.objects.select_related('id_rol').all()
    serializer_class = EmpleadoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['activo', 'id_rol']
    search_fields = ['nombre', 'apellido', 'usuario']
    
    @swagger_auto_schema(
        operation_description="Obtiene las ventas realizadas por el empleado (hasta 100 últimas)",
        responses={200: VentaListSerializer(many=True)}
    )
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
    ViewSet para proveedores.
    
    Gestiona los proveedores del sistema:
    - Listar proveedores activos
    - Búsqueda por razón social, RUC o teléfono
    - Ver compras realizadas a cada proveedor
    """
    queryset = Proveedor.objects.prefetch_related('compras_set').all()
    serializer_class = ProveedorSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['activo']
    search_fields = ['razon_social', 'ruc', 'telefono']
    ordering_fields = ['razon_social']
    ordering = ['razon_social']
