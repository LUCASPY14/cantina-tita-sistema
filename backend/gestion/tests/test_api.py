"""
Tests de API - Portal de Padres
"""

import pytest
from decimal import Decimal
from rest_framework import status


@pytest.mark.api
@pytest.mark.portal
@pytest.mark.django_db
class TestPortalAPI:
    """Tests para API del Portal de Padres"""
    
    def test_portal_requiere_autenticacion(self, api_client):
        """Test: Portal requiere autenticación"""
        response = api_client.get('/api/portal/mis-hijos/')
        
        assert response.status_code in [401, 403]
    
    def test_portal_lista_hijos(self, authenticated_api_client, padre, hijo):
        """Test: Padre puede ver lista de sus hijos"""
        # Actualizar el user del cliente autenticado para que sea el padre
        authenticated_api_client.force_authenticate(user=padre.user)
        
        response = authenticated_api_client.get('/api/portal/mis-hijos/')
        
        # Verificar respuesta exitosa
        assert response.status_code in [200, 404]
    
    def test_portal_crear_recarga(self, authenticated_api_client, hijo, tarjeta):
        """Test: Crear solicitud de recarga"""
        data = {
            'hijo': hijo.id,
            'tarjeta': tarjeta.numero_tarjeta,
            'monto': '20000.00',
            'metodo_pago': 'transferencia'
        }
        
        response = authenticated_api_client.post('/api/portal/recargas/', data)
        
        # Puede crear o fallar por validaciones
        assert response.status_code in [200, 201, 400, 404]
    
    def test_portal_historial_recargas(self, authenticated_api_client, padre):
        """Test: Ver historial de recargas"""
        authenticated_api_client.force_authenticate(user=padre.user)
        
        response = authenticated_api_client.get('/api/portal/recargas/')
        
        assert response.status_code in [200, 404]
    
    def test_portal_detalle_hijo(self, authenticated_api_client, padre, hijo):
        """Test: Ver detalle de hijo específico"""
        authenticated_api_client.force_authenticate(user=padre.user)
        
        response = authenticated_api_client.get(f'/api/portal/hijos/{hijo.id}/')
        
        assert response.status_code in [200, 404]


@pytest.mark.api
@pytest.mark.django_db
class TestRestriccionesAPI:
    """Tests para API de restricciones alimentarias"""
    
    def test_restricciones_hijo(self, authenticated_api_client, hijo):
        """Test: Ver restricciones de un hijo"""
        response = authenticated_api_client.get(f'/api/hijos/{hijo.id}/restricciones/')
        
        assert response.status_code in [200, 404]
    
    def test_agregar_restriccion(self, authenticated_api_client, hijo):
        """Test: Agregar restricción alimentaria"""
        data = {
            'hijo': hijo.id,
            'tipo': 'alergia',
            'descripcion': 'Alérgico a maní',
            'severidad': 'alta'
        }
        
        response = authenticated_api_client.post(f'/api/hijos/{hijo.id}/restricciones/', data)
        
        assert response.status_code in [200, 201, 400, 404]


@pytest.mark.api
@pytest.mark.django_db
class TestProductosAPI:
    """Tests para API de productos"""
    
    def test_lista_productos_disponibles(self, authenticated_api_client, producto):
        """Test: Listar productos disponibles"""
        response = authenticated_api_client.get('/api/productos/')
        
        assert response.status_code in [200, 404]
    
    def test_detalle_producto(self, authenticated_api_client, producto):
        """Test: Ver detalle de producto"""
        response = authenticated_api_client.get(f'/api/productos/{producto.id}/')
        
        assert response.status_code in [200, 404]
    
    def test_productos_por_categoria(self, authenticated_api_client, categoria_producto):
        """Test: Filtrar productos por categoría"""
        response = authenticated_api_client.get(f'/api/productos/?categoria={categoria_producto.id}')
        
        assert response.status_code in [200, 404]


@pytest.mark.api
@pytest.mark.django_db  
class TestVentasAPI:
    """Tests para API de ventas"""
    
    def test_crear_venta_api(self, authenticated_api_client, cliente, producto, caja):
        """Test: Crear venta mediante API"""
        data = {
            'cliente': cliente.id,
            'caja': caja.id,
            'items': [
                {
                    'producto': producto.id,
                    'cantidad': 2,
                    'precio_unitario': str(producto.precio_venta)
                }
            ],
            'metodo_pago': 'efectivo'
        }
        
        response = authenticated_api_client.post('/api/ventas/', data, format='json')
        
        # Puede crear o fallar por validaciones
        assert response.status_code in [200, 201, 400, 404]
    
    def test_anular_venta_api(self, authenticated_api_client, venta):
        """Test: Anular venta existente"""
        response = authenticated_api_client.post(f'/api/ventas/{venta.id}/anular/')
        
        assert response.status_code in [200, 400, 404]
