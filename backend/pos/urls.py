"""
URLs de la app POS
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VentaViewSet, DetalleVentaViewSet, PagoVentaViewSet, ProductoPOSViewSet

app_name = 'pos_api'

# Router para ViewSets
router = DefaultRouter()
router.register(r'ventas', VentaViewSet, basename='venta')
router.register(r'detalles', DetalleVentaViewSet, basename='detalle-venta')
router.register(r'pagos', PagoVentaViewSet, basename='pago-venta')
router.register(r'productos', ProductoPOSViewSet, basename='producto-pos')

urlpatterns = [
    path('', include(router.urls)),
]
