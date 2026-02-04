"""
Views y ViewSets para la API REST del sistema POS
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import Venta, DetalleVenta, PagoVenta
from .serializers import (
    VentaSerializer, VentaCreateSerializer, VentaResumenSerializer,
    DetalleVentaSerializer, PagoVentaSerializer
)


@extend_schema_view(
    list=extend_schema(
        summary="Listar ventas",
        description="Obtiene lista paginada de todas las ventas con filtros opcionales",
        tags=['POS - Ventas']
    ),
    retrieve=extend_schema(
        summary="Obtener venta",
        description="Obtiene detalle completo de una venta específica con sus detalles y pagos",
        tags=['POS - Ventas']
    ),
    create=extend_schema(
        summary="Crear venta",
        description="Crea una nueva venta con detalles y pagos opcionales en una sola transacción",
        tags=['POS - Ventas']
    ),
    update=extend_schema(
        summary="Actualizar venta",
        description="Actualiza una venta existente",
        tags=['POS - Ventas']
    ),
    partial_update=extend_schema(
        summary="Actualizar parcialmente venta",
        description="Actualiza campos específicos de una venta",
        tags=['POS - Ventas']
    ),
    destroy=extend_schema(
        summary="Anular venta",
        description="Marca una venta como ANULADA (soft delete)",
        tags=['POS - Ventas']
    ),
)
class VentaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Ventas del sistema POS
    
    Endpoints:
    - GET /api/pos/ventas/ - Listar ventas
    - POST /api/pos/ventas/ - Crear venta
    - GET /api/pos/ventas/{id}/ - Obtener venta
    - PUT /api/pos/ventas/{id}/ - Actualizar venta
    - PATCH /api/pos/ventas/{id}/ - Actualizar parcialmente
    - DELETE /api/pos/ventas/{id}/ - Anular venta
    - GET /api/pos/ventas/estadisticas/ - Estadísticas
    - GET /api/pos/ventas/del_dia/ - Ventas del día
    - POST /api/pos/ventas/{id}/anular/ - Anular venta
    - POST /api/pos/ventas/{id}/agregar_pago/ - Agregar pago
    """
    queryset = Venta.objects.select_related(
        'id_cliente', 'id_hijo', 'id_empleado_cajero', 'autorizado_por'
    ).prefetch_related('detalles', 'pagos')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estado', 'estado_pago', 'tipo_venta', 'id_cliente', 'id_empleado_cajero']
    search_fields = ['nro_factura_venta', 'id_cliente__nombre_completo', 'id_hijo__nombre_completo']
    ordering_fields = ['fecha', 'monto_total', 'id_venta']
    ordering = ['-fecha']
    
    def get_serializer_class(self):
        """Seleccionar serializer según la acción"""
        if self.action == 'create':
            return VentaCreateSerializer
        elif self.action == 'list':
            return VentaResumenSerializer
        return VentaSerializer
    
    def destroy(self, request, *args, **kwargs):
        """Anular venta (soft delete)"""
        venta = self.get_object()
        venta.estado = 'ANULADO'
        venta.save()
        return Response({'mensaje': f'Venta #{venta.id_venta} anulada exitosamente'})
    
    @extend_schema(
        summary="Estadísticas de ventas",
        description="Obtiene estadísticas generales de ventas (totales, promedios, etc.)",
        tags=['POS - Ventas'],
        parameters=[
            OpenApiParameter('fecha_desde', OpenApiTypes.DATE, description='Fecha inicial (YYYY-MM-DD)'),
            OpenApiParameter('fecha_hasta', OpenApiTypes.DATE, description='Fecha final (YYYY-MM-DD)'),
        ]
    )
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Obtener estadísticas de ventas"""
        # Filtros de fecha
        fecha_desde = request.query_params.get('fecha_desde')
        fecha_hasta = request.query_params.get('fecha_hasta')
        
        queryset = self.get_queryset().filter(estado='PROCESADO')
        
        if fecha_desde:
            queryset = queryset.filter(fecha__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha__lte=fecha_hasta)
        
        # Calcular estadísticas
        stats = queryset.aggregate(
            total_ventas=Count('id_venta'),
            total_monto=Sum('monto_total'),
            total_saldo_pendiente=Sum('saldo_pendiente'),
        )
        
        # Estadísticas por tipo de venta
        stats_por_tipo = queryset.values('tipo_venta').annotate(
            cantidad=Count('id_venta'),
            monto=Sum('monto_total')
        )
        
        # Estadísticas por estado de pago
        stats_por_estado = queryset.values('estado_pago').annotate(
            cantidad=Count('id_venta'),
            monto=Sum('monto_total')
        )
        
        return Response({
            'generales': stats,
            'por_tipo_venta': list(stats_por_tipo),
            'por_estado_pago': list(stats_por_estado),
            'periodo': {
                'desde': fecha_desde,
                'hasta': fecha_hasta,
            }
        })
    
    @extend_schema(
        summary="Ventas del día",
        description="Obtiene todas las ventas realizadas en el día actual",
        tags=['POS - Ventas']
    )
    @action(detail=False, methods=['get'])
    def del_dia(self, request):
        """Obtener ventas del día actual"""
        hoy = timezone.now().date()
        ventas_hoy = self.get_queryset().filter(
            fecha__date=hoy,
            estado='PROCESADO'
        )
        
        serializer = self.get_serializer(ventas_hoy, many=True)
        
        # Estadísticas del día
        stats = ventas_hoy.aggregate(
            total_ventas=Count('id_venta'),
            total_monto=Sum('monto_total'),
        )
        
        return Response({
            'fecha': hoy,
            'ventas': serializer.data,
            'estadisticas': stats
        })
    
    @extend_schema(
        summary="Anular venta",
        description="Marca una venta como ANULADA y revierte sus efectos",
        tags=['POS - Ventas']
    )
    @action(detail=True, methods=['post'])
    def anular(self, request, pk=None):
        """Anular una venta específica"""
        venta = self.get_object()
        
        if venta.estado == 'ANULADO':
            return Response(
                {'error': 'La venta ya está anulada'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Anular venta y sus pagos
        venta.estado = 'ANULADO'
        venta.save()
        
        venta.pagos.update(estado='ANULADO')
        
        return Response({
            'mensaje': f'Venta #{venta.id_venta} anulada exitosamente',
            'venta': VentaSerializer(venta).data
        })
    
    @extend_schema(
        summary="Agregar pago a venta",
        description="Agrega un pago a una venta existente",
        tags=['POS - Ventas'],
        request=PagoVentaSerializer
    )
    @action(detail=True, methods=['post'])
    def agregar_pago(self, request, pk=None):
        """Agregar un pago a una venta"""
        venta = self.get_object()
        
        if venta.estado == 'ANULADO':
            return Response(
                {'error': 'No se puede agregar pago a una venta anulada'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if venta.estado_pago == 'PAGADA':
            return Response(
                {'error': 'La venta ya está completamente pagada'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Crear pago
        pago_serializer = PagoVentaSerializer(data=request.data)
        if pago_serializer.is_valid():
            pago = pago_serializer.save(id_venta=venta)
            
            # Actualizar saldo de venta
            venta.saldo_pendiente -= pago.monto_aplicado
            
            # Actualizar estado de pago
            if venta.saldo_pendiente <= 0:
                venta.estado_pago = 'PAGADA'
                venta.saldo_pendiente = 0
            elif venta.saldo_pendiente < venta.monto_total:
                venta.estado_pago = 'PARCIAL'
            
            venta.save()
            
            return Response({
                'mensaje': 'Pago agregado exitosamente',
                'pago': pago_serializer.data,
                'venta': VentaSerializer(venta).data
            })
        
        return Response(pago_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(
        summary="Listar detalles de venta",
        description="Obtiene lista de detalles de ventas",
        tags=['POS - Detalles']
    ),
    retrieve=extend_schema(
        summary="Obtener detalle de venta",
        description="Obtiene un detalle específico de venta",
        tags=['POS - Detalles']
    ),
)
class DetalleVentaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para Detalles de Venta (solo lectura)
    
    Los detalles se crean junto con la venta, no individualmente.
    """
    queryset = DetalleVenta.objects.select_related('id_venta', 'id_producto')
    serializer_class = DetalleVentaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['id_venta', 'id_producto']
    ordering = ['id_detalle']


@extend_schema_view(
    list=extend_schema(
        summary="Listar pagos de venta",
        description="Obtiene lista de pagos aplicados a ventas",
        tags=['POS - Pagos']
    ),
    retrieve=extend_schema(
        summary="Obtener pago de venta",
        description="Obtiene un pago específico de venta",
        tags=['POS - Pagos']
    ),
    create=extend_schema(
        summary="Crear pago de venta",
        description="Crea un nuevo pago para una venta",
        tags=['POS - Pagos']
    ),
)
class PagoVentaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Pagos de Venta
    
    Permite crear pagos individuales y consultar historial de pagos.
    """
    queryset = PagoVenta.objects.select_related(
        'id_venta', 'id_medio_pago', 'nro_tarjeta_usada'
    )
    serializer_class = PagoVentaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['id_venta', 'id_medio_pago', 'estado', 'id_cierre']
    ordering = ['-fecha_pago']
    
    def destroy(self, request, *args, **kwargs):
        """Anular pago (soft delete)"""
        pago = self.get_object()
        
        if pago.estado == 'ANULADO':
            return Response(
                {'error': 'El pago ya está anulado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Anular pago y actualizar venta
        pago.estado = 'ANULADO'
        pago.save()
        
        venta = pago.id_venta
        venta.saldo_pendiente += pago.monto_aplicado
        
        # Actualizar estado de pago
        if venta.saldo_pendiente >= venta.monto_total:
            venta.estado_pago = 'PENDIENTE'
        elif venta.saldo_pendiente > 0:
            venta.estado_pago = 'PARCIAL'
        
        venta.save()
        
        return Response({'mensaje': f'Pago #{pago.id_pago_venta} anulado exitosamente'})
