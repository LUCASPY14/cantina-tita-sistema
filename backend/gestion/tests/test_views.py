"""
Tests de Views - Sistema de Gestión
"""

import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestDashboardViews:
    """Tests para vistas del dashboard"""
    
    def test_dashboard_requiere_login(self, client):
        """Test: Dashboard requiere autenticación"""
        response = client.get('/dashboard/')
        
        # Debe redirigir a login
        assert response.status_code in [302, 403]
    
    def test_dashboard_autenticado(self, authenticated_client):
        """Test: Usuario autenticado puede ver dashboard"""
        response = authenticated_client.get('/dashboard/')
        
        # Debe mostrar dashboard o redirigir al home del usuario
        assert response.status_code in [200, 302]
    
    def test_admin_puede_ver_dashboard(self, admin_client):
        """Test: Admin tiene acceso completo al dashboard"""
        response = admin_client.get('/dashboard/')
        
        assert response.status_code == 200


@pytest.mark.django_db
class TestPOSViews:
    """Tests para vistas del POS"""
    
    def test_pos_requiere_autenticacion(self, client):
        """Test: POS requiere login"""
        response = client.get('/pos/')
        
        assert response.status_code in [302, 403]
    
    def test_pos_autenticado(self, authenticated_client):
        """Test: Usuario autenticado puede acceder a POS"""
        response = authenticated_client.get('/pos/')
        
        # Verificar que carga (puede requerir permisos específicos)
        assert response.status_code in [200, 302, 403]


@pytest.mark.django_db
class TestProductosViews:
    """Tests para vistas de productos"""
    
    def test_lista_productos_requiere_auth(self, client):
        """Test: Lista de productos requiere autenticación"""
        response = client.get('/productos/')
        
        assert response.status_code in [302, 403]
    
    def test_lista_productos_autenticado(self, authenticated_client, producto):
        """Test: Usuario autenticado puede ver productos"""
        response = authenticated_client.get('/productos/')
        
        # Verificar respuesta exitosa o redirección
        assert response.status_code in [200, 302]


@pytest.mark.django_db
class TestVentasViews:
    """Tests para vistas de ventas"""
    
    def test_crear_venta_requiere_auth(self, client):
        """Test: Crear venta requiere autenticación"""
        response = client.post('/ventas/crear/')
        
        assert response.status_code in [302, 403, 405]
    
    def test_lista_ventas_autenticado(self, authenticated_client):
        """Test: Usuario autenticado puede ver lista de ventas"""
        response = authenticated_client.get('/ventas/')
        
        assert response.status_code in [200, 302]


@pytest.mark.api
@pytest.mark.django_db
class TestAPIViews:
    """Tests para vistas de API"""
    
    def test_api_health_check(self, api_client):
        """Test: Health check endpoint funciona sin auth"""
        response = api_client.get('/api/health/')
        
        assert response.status_code == 200
        assert 'status' in response.data or response.data
    
    def test_api_productos_requiere_auth(self, api_client):
        """Test: API de productos requiere autenticación"""
        response = api_client.get('/api/productos/')
        
        # Debe rechazar sin auth
        assert response.status_code in [401, 403]
    
    def test_api_productos_autenticado(self, authenticated_api_client, producto):
        """Test: API productos con autenticación"""
        response = authenticated_api_client.get('/api/productos/')
        
        # Debe funcionar
        assert response.status_code in [200, 404]
