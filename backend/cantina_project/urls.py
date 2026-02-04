"""
URL configuration for cantina_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from gestion import cliente_views
from gestion.cantina_admin import cantina_admin_site
from gestion.auth_views import CustomLoginView, CustomLogoutView, dashboard_redirect
from gestion.health_views import health_check, readiness_check, liveness_check
from gestion.dashboard_views import (
    dashboard_unificado, dashboard_ventas_detalle, 
    dashboard_stock_detalle, invalidar_cache_dashboard
)
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# drf-spectacular para documentación OpenAPI 3.0
from drf_spectacular.views import (
    SpectacularAPIView, 
    SpectacularSwaggerView, 
    SpectacularRedocView
)

# Configuración de Swagger/OpenAPI
schema_view = get_schema_view(
    openapi.Info(
        title="Cantina Tita API",
        default_version='v1',
        description="""
        API REST para el Sistema de Gestión de Cantina Tita
        
        ## Funcionalidades principales:
        - Gestión de productos y categorías
        - Control de ventas y pagos
        - Sistema de tarjetas estudiantiles
        - Recargas y consumos
        - Gestión de stock e inventario
        - Control de clientes y cuenta corriente
        - Administración de empleados
        - Reportes y estadísticas
        
        ## Autenticación:
        Usa JWT (JSON Web Tokens) para autenticación.
        1. Obtén un token en `/api/v1/auth/token/`
        2. Incluye el token en el header: `Authorization: Bearer {token}`
        """,
        terms_of_service="https://www.cantinatita.com/terms/",
        contact=openapi.Contact(email="contacto@cantinatita.com"),
        license=openapi.License(name="Propietario"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Health Checks (monitoring)
    path('health/', health_check, name='health_check'),
    path('ready/', readiness_check, name='readiness_check'),
    path('alive/', liveness_check, name='liveness_check'),
    
    # Dashboard Unificado
    path('dashboard/', dashboard_unificado, name='dashboard_unificado'),
    path('dashboard/ventas/', dashboard_ventas_detalle, name='dashboard_ventas_detalle'),
    path('dashboard/stock/', dashboard_stock_detalle, name='dashboard_stock_detalle'),
    path('dashboard/invalidar-cache/', invalidar_cache_dashboard, name='invalidar_cache_dashboard'),
    
    # Autenticación
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('', dashboard_redirect, name='home'),
    
    # Admin personalizado
    path('admin/', cantina_admin_site.urls),
    
    # POS (Punto de Venta) - Nueva interfaz
    path('pos/', include('gestion.pos_urls')),
    
    # Portal de Padres
    path('portal/', include('portal_urls')),
    
    # Portal de Clientes
    path('clientes/', include('gestion.cliente_urls')),
    
    # API REST v1
    path('api/v1/', include('gestion.api_urls')),
    
    # API POS (Punto de Venta)
    path('api/pos/', include('pos.urls')),
    
    # Documentación OpenAPI 3.0 (drf-spectacular) - RECOMENDADO
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Documentación de la API (Swagger/OpenAPI 2.0 - drf_yasg LEGACY)
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', 
            schema_view.without_ui(cache_timeout=0), 
            name='schema-json'),
    path('swagger/', 
         schema_view.with_ui('swagger', cache_timeout=0), 
         name='schema-swagger-ui'),
    path('redoc/', 
         schema_view.with_ui('redoc', cache_timeout=0), 
         name='schema-redoc'),
    
    # URLs de reportes y vistas
    path('reportes/', include('gestion.urls')),
]

# Django Debug Toolbar (solo en modo DEBUG)
if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls')),
    ]
    # Servir archivos media en desarrollo
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
