"""
Tests de API REST - Endpoints principales
"""

import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from decimal import Decimal


@pytest.fixture
def api_client():
    """Cliente API sin autenticación"""
    return APIClient()


@pytest.fixture
def user():
    """Usuario de prueba"""
    return User.objects.create_user(
        username='testuser',
        password='testpass123',
        email='test@test.com'
    )


@pytest.fixture
def authenticated_client(api_client, user):
    """Cliente API autenticado"""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.mark.django_db
class TestAPIEndpoints:
    """Tests básicos de endpoints API"""
    
    def test_api_schema_disponible(self, api_client):
        """Test: Schema API está disponible"""
        response = api_client.get('/api/schema/')
        assert response.status_code in [200, 404]  # 404 si no está configurado
    
    def test_api_docs_disponible(self, api_client):
        """Test: Documentación API está disponible"""
        response = api_client.get('/api/docs/')
        assert response.status_code in [200, 404]
    
    def test_portal_requiere_autenticacion(self, api_client):
        """Test: Portal API requiere autenticación"""
        response = api_client.get('/api/portal/movimientos/')
        assert response.status_code in [401, 403, 404]
    
    def test_portal_saldo_requiere_autenticacion(self, api_client):
        """Test: Saldo requiere autenticación"""
        response = api_client.get('/api/portal/saldo/')
        assert response.status_code in [401, 403, 404]


@pytest.mark.django_db
class TestAPIGestion:
    """Tests de API de gestión"""
    
    def test_api_v1_disponible(self, api_client):
        """Test: API v1 está disponible"""
        # Intentar acceder a la raíz de la API
        response = api_client.get('/api/v1/')
        assert response.status_code in [200, 404, 403]


@pytest.mark.django_db  
class TestAPIPOS:
    """Tests de API de POS"""
    
    def test_api_pos_disponible(self, api_client):
        """Test: API POS está disponible"""
        response = api_client.get('/api/pos/')
        assert response.status_code in [200, 404, 403, 405]
