"""
URLs de la API REST v1
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from .api_views import (
    CategoriaViewSet,
    ProductoViewSet,
    ClienteViewSet,
    TarjetaViewSet,
    VentaViewSet,
    StockViewSet,
    MovimientoStockViewSet,
    EmpleadoViewSet,
    ProveedorViewSet,
)
from django.http import JsonResponse


def api_root_plain(request):
    """Root público simple para `/api/v1/` (evita permisos DRF)."""
    return JsonResponse({'message': 'Cantina Tita API v1', 'documentation': '/swagger/'})

# Router principal
router = DefaultRouter()

# Registrar ViewSets
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'productos', ProductoViewSet, basename='producto')
router.register(r'clientes', ClienteViewSet, basename='cliente')
router.register(r'tarjetas', TarjetaViewSet, basename='tarjeta')
router.register(r'ventas', VentaViewSet, basename='venta')
router.register(r'stock', StockViewSet, basename='stock')
router.register(r'movimientos-stock', MovimientoStockViewSet, basename='movimiento-stock')
router.register(r'empleados', EmpleadoViewSet, basename='empleado')
router.register(r'proveedores', ProveedorViewSet, basename='proveedor')

urlpatterns = [
    # Autenticación JWT
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Endpoints de la API
    path('', api_root_plain, name='api-root'),
    path('', include(router.urls)),
]
