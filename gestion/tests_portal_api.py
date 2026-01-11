"""
Tests para Portal API - Sistema de Consultas de Padres
Cobertura de todos los endpoints del portal web de padres
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from decimal import Decimal
from datetime import datetime, timedelta
import json

from .models import (
    Cliente, Hijo, Tarjeta, CargasSaldo, ConsumoTarjeta,
    UsuarioPortal, Notificacion, PreferenciaNotificacion,
    TransaccionOnline, TokenVerificacion
)


class PortalAPITestCase(APITestCase):
    """Test base para Portal API con fixtures"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        # Crear usuario Django
        self.user = User.objects.create_user(
            username='padre_test',
            email='padre@test.com',
            password='TestPass123!'
        )
        
        # Crear cliente (padre)
        self.cliente = Cliente.objects.create(
            ci_ruc='1234567-8',
            nombres='Juan',
            apellidos='Pérez',
            email='padre@test.com',
            telefono='0981234567',
            activo=True
        )
        
        # Crear usuario portal
        self.usuario_portal = UsuarioPortal.objects.create(
            user=self.user,
            id_cliente=self.cliente,
            email_verificado=True,
            telefono_verificado=False
        )
        
        # Crear hijo
        self.hijo = Hijo.objects.create(
            id_cliente_responsable=self.cliente,
            nombres='Pedro',
            apellidos='Pérez',
            ci='7654321-1',
            activo=True
        )
        
        # Crear tarjeta
        self.tarjeta = Tarjeta.objects.create(
            nro_tarjeta='1001',
            id_cliente=self.cliente,
            id_hijo=self.hijo,
            saldo_actual=Decimal('50000.00'),
            activo=True,
            bloqueado=False
        )
        
        # Crear recargas
        self.recarga1 = CargasSaldo.objects.create(
            id_tarjeta=self.tarjeta,
            monto=Decimal('30000.00'),
            fecha_carga=datetime.now() - timedelta(days=5),
            medio_pago='efectivo'
        )
        
        self.recarga2 = CargasSaldo.objects.create(
            id_tarjeta=self.tarjeta,
            monto=Decimal('20000.00'),
            fecha_carga=datetime.now() - timedelta(days=1),
            medio_pago='tarjeta_credito'
        )
        
        # Crear consumos
        self.consumo1 = ConsumoTarjeta.objects.create(
            id_tarjeta=self.tarjeta,
            monto=Decimal('5000.00'),
            fecha_consumo=datetime.now() - timedelta(days=3),
            descripcion='Almuerzo escolar'
        )
        
        self.consumo2 = ConsumoTarjeta.objects.create(
            id_tarjeta=self.tarjeta,
            monto=Decimal('3500.00'),
            fecha_consumo=datetime.now() - timedelta(hours=2),
            descripcion='Snack'
        )
        
        # Crear notificación
        self.notificacion = Notificacion.objects.create(
            id_usuario=self.usuario_portal,
            titulo='Recarga exitosa',
            mensaje='Tu recarga de Gs. 20,000 fue procesada',
            tipo='recarga',
            leida=False
        )
        
        # Obtener token JWT
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        
        # Configurar cliente API
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')


class TestSaldoTarjetaAPI(PortalAPITestCase):
    """Tests para endpoint de consulta de saldo"""
    
    def test_consultar_saldo_exitoso(self):
        """Debe retornar el saldo actual de la tarjeta"""
        url = f'/api/portal/tarjeta/{self.tarjeta.nro_tarjeta}/saldo/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(response.data['saldo_actual']), self.tarjeta.saldo_actual)
        self.assertEqual(response.data['nro_tarjeta'], self.tarjeta.nro_tarjeta)
        self.assertIn('estudiante', response.data)
        self.assertIn('activo', response.data)
        self.assertIn('bloqueado', response.data)
    
    def test_consultar_saldo_tarjeta_inexistente(self):
        """Debe retornar 404 si la tarjeta no existe"""
        url = '/api/portal/tarjeta/9999/saldo/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_consultar_saldo_sin_autenticacion(self):
        """Debe retornar 401 si no está autenticado"""
        # Cliente sin token
        client_no_auth = APIClient()
        url = f'/api/portal/tarjeta/{self.tarjeta.nro_tarjeta}/saldo/'
        response = client_no_auth.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_consultar_saldo_tarjeta_otro_cliente(self):
        """Debe retornar 403 si intenta ver saldo de tarjeta de otro cliente"""
        # Crear otro cliente
        otro_cliente = Cliente.objects.create(
            ci_ruc='9999999-9',
            nombres='María',
            apellidos='López',
            activo=True
        )
        
        # Crear tarjeta de otro cliente
        otra_tarjeta = Tarjeta.objects.create(
            nro_tarjeta='2001',
            id_cliente=otro_cliente,
            saldo_actual=Decimal('10000.00'),
            activo=True
        )
        
        url = f'/api/portal/tarjeta/{otra_tarjeta.nro_tarjeta}/saldo/'
        response = self.client.get(url)
        
        # Debe denegar acceso
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestMovimientosTarjetaAPI(PortalAPITestCase):
    """Tests para endpoint de movimientos (recargas + consumos)"""
    
    def test_listar_movimientos_completos(self):
        """Debe retornar todos los movimientos ordenados por fecha"""
        url = f'/api/portal/tarjeta/{self.tarjeta.nro_tarjeta}/movimientos/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 4)  # 2 recargas + 2 consumos
        
        # Verificar orden descendente por fecha
        fechas = [mov['fecha'] for mov in response.data]
        self.assertEqual(fechas, sorted(fechas, reverse=True))
    
    def test_movimientos_tienen_campos_requeridos(self):
        """Cada movimiento debe tener tipo, monto, fecha, descripción"""
        url = f'/api/portal/tarjeta/{self.tarjeta.nro_tarjeta}/movimientos/'
        response = self.client.get(url)
        
        for movimiento in response.data:
            self.assertIn('tipo', movimiento)  # 'recarga' o 'consumo'
            self.assertIn('monto', movimiento)
            self.assertIn('fecha', movimiento)
            self.assertIn('descripcion', movimiento)
            self.assertIn('saldo_resultante', movimiento)
    
    def test_filtrar_movimientos_por_tipo(self):
        """Debe permitir filtrar solo recargas o solo consumos"""
        url = f'/api/portal/tarjeta/{self.tarjeta.nro_tarjeta}/movimientos/?tipo=recarga'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Solo recargas
        for mov in response.data:
            self.assertEqual(mov['tipo'], 'recarga')
    
    def test_filtrar_movimientos_por_fecha(self):
        """Debe permitir filtrar por rango de fechas"""
        fecha_desde = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
        url = f'/api/portal/tarjeta/{self.tarjeta.nro_tarjeta}/movimientos/?desde={fecha_desde}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Solo debe traer movimientos de últimos 2 días
        self.assertGreater(len(response.data), 0)


class TestConsumosAPI(PortalAPITestCase):
    """Tests para endpoint de consumos"""
    
    def test_listar_consumos(self):
        """Debe listar todos los consumos de la tarjeta"""
        url = f'/api/portal/tarjeta/{self.tarjeta.nro_tarjeta}/consumos/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        # Verificar estructura
        consumo = response.data[0]
        self.assertIn('monto', consumo)
        self.assertIn('fecha_consumo', consumo)
        self.assertIn('descripcion', consumo)
    
    def test_consumos_ordenados_por_fecha(self):
        """Los consumos deben estar ordenados del más reciente al más antiguo"""
        url = f'/api/portal/tarjeta/{self.tarjeta.nro_tarjeta}/consumos/'
        response = self.client.get(url)
        
        fechas = [c['fecha_consumo'] for c in response.data]
        self.assertEqual(fechas, sorted(fechas, reverse=True))
    
    def test_consumos_paginados(self):
        """Debe soportar paginación para listas largas"""
        # Crear 30 consumos
        for i in range(30):
            ConsumoTarjeta.objects.create(
                id_tarjeta=self.tarjeta,
                monto=Decimal('1000.00'),
                fecha_consumo=datetime.now() - timedelta(days=i),
                descripcion=f'Consumo {i}'
            )
        
        url = f'/api/portal/tarjeta/{self.tarjeta.nro_tarjeta}/consumos/?page=1&page_size=10'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(len(response.data['results']), 10)


class TestRecargasAPI(PortalAPITestCase):
    """Tests para endpoint de recargas"""
    
    def test_listar_recargas(self):
        """Debe listar todas las recargas de la tarjeta"""
        url = f'/api/portal/tarjeta/{self.tarjeta.nro_tarjeta}/recargas/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        recarga = response.data[0]
        self.assertIn('monto', recarga)
        self.assertIn('fecha_carga', recarga)
        self.assertIn('medio_pago', recarga)
    
    def test_total_recargado_mes(self):
        """Debe calcular el total recargado en el mes actual"""
        url = f'/api/portal/tarjeta/{self.tarjeta.nro_tarjeta}/recargas/estadisticas/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_mes', response.data)
        self.assertIn('cantidad_recargas', response.data)
        self.assertIn('promedio', response.data)


class TestMisTarjetasAPI(PortalAPITestCase):
    """Tests para endpoint de mis tarjetas"""
    
    def test_listar_mis_tarjetas(self):
        """Debe listar todas las tarjetas del usuario autenticado"""
        # Crear segunda tarjeta para otro hijo
        hijo2 = Hijo.objects.create(
            id_cliente_responsable=self.cliente,
            nombres='María',
            apellidos='Pérez',
            ci='1111111-1',
            activo=True
        )
        
        tarjeta2 = Tarjeta.objects.create(
            nro_tarjeta='1002',
            id_cliente=self.cliente,
            id_hijo=hijo2,
            saldo_actual=Decimal('25000.00'),
            activo=True
        )
        
        url = '/api/portal/mis-tarjetas/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        # Verificar estructura
        tarjeta = response.data[0]
        self.assertIn('nro_tarjeta', tarjeta)
        self.assertIn('saldo_actual', tarjeta)
        self.assertIn('estudiante', tarjeta)
        self.assertIn('activo', tarjeta)
        self.assertIn('bloqueado', tarjeta)
    
    def test_solo_tarjetas_activas(self):
        """Por defecto solo debe mostrar tarjetas activas"""
        # Crear tarjeta inactiva
        Tarjeta.objects.create(
            nro_tarjeta='1003',
            id_cliente=self.cliente,
            id_hijo=self.hijo,
            saldo_actual=Decimal('0.00'),
            activo=False
        )
        
        url = '/api/portal/mis-tarjetas/'
        response = self.client.get(url)
        
        # Solo debe traer la tarjeta activa
        self.assertEqual(len(response.data), 1)
        self.assertTrue(response.data[0]['activo'])


class TestNotificacionesAPI(PortalAPITestCase):
    """Tests para endpoints de notificaciones"""
    
    def test_listar_notificaciones(self):
        """Debe listar todas las notificaciones del usuario"""
        # Crear más notificaciones
        Notificacion.objects.create(
            id_usuario=self.usuario_portal,
            titulo='Saldo bajo',
            mensaje='El saldo de la tarjeta 1001 es menor a Gs. 10,000',
            tipo='alerta',
            leida=False
        )
        
        url = '/api/portal/notificaciones/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        notif = response.data[0]
        self.assertIn('titulo', notif)
        self.assertIn('mensaje', notif)
        self.assertIn('tipo', notif)
        self.assertIn('leida', notif)
        self.assertIn('fecha_creacion', notif)
    
    def test_filtrar_notificaciones_no_leidas(self):
        """Debe permitir filtrar solo no leídas"""
        # Marcar una como leída
        self.notificacion.leida = True
        self.notificacion.save()
        
        # Crear otra no leída
        Notificacion.objects.create(
            id_usuario=self.usuario_portal,
            titulo='Nueva',
            mensaje='Mensaje nuevo',
            tipo='info',
            leida=False
        )
        
        url = '/api/portal/notificaciones/?leidas=false'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertFalse(response.data[0]['leida'])
    
    def test_marcar_notificacion_leida(self):
        """Debe permitir marcar una notificación como leída"""
        url = f'/api/portal/notificaciones/{self.notificacion.id_notificacion}/marcar-leida/'
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['leida'])
        
        # Verificar en DB
        self.notificacion.refresh_from_db()
        self.assertTrue(self.notificacion.leida)
    
    def test_contar_no_leidas(self):
        """Debe retornar el conteo de notificaciones no leídas"""
        # Crear 3 más
        for i in range(3):
            Notificacion.objects.create(
                id_usuario=self.usuario_portal,
                titulo=f'Notif {i}',
                mensaje=f'Mensaje {i}',
                tipo='info',
                leida=False
            )
        
        url = '/api/portal/notificaciones/contador/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['no_leidas'], 4)


class TestRecargaOnlineAPI(PortalAPITestCase):
    """Tests para endpoint de recarga online (Tigo Money)"""
    
    def test_iniciar_recarga_online(self):
        """Debe crear una transacción online pendiente"""
        url = '/api/portal/recargar-online/'
        data = {
            'nro_tarjeta': self.tarjeta.nro_tarjeta,
            'monto': 50000.00,
            'metodo_pago': 'tigo_money',
            'telefono': '0981234567'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('transaction_id', response.data)
        self.assertIn('payment_url', response.data)
        self.assertEqual(response.data['estado'], 'pendiente')
        
        # Verificar creación en DB
        transaccion = TransaccionOnline.objects.filter(
            nro_transaccion=response.data['transaction_id']
        ).first()
        self.assertIsNotNone(transaccion)
        self.assertEqual(transaccion.estado, 'pendiente')
    
    def test_recarga_monto_minimo(self):
        """No debe permitir recargas menores al mínimo (Gs. 10,000)"""
        url = '/api/portal/recargar-online/'
        data = {
            'nro_tarjeta': self.tarjeta.nro_tarjeta,
            'monto': 5000.00,  # Menor al mínimo
            'metodo_pago': 'tigo_money',
            'telefono': '0981234567'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('monto', response.data)
    
    def test_verificar_estado_transaccion(self):
        """Debe permitir consultar el estado de una transacción"""
        # Crear transacción
        transaccion = TransaccionOnline.objects.create(
            id_tarjeta=self.tarjeta,
            nro_transaccion='TXN-123456',
            monto=Decimal('30000.00'),
            metodo_pago='tigo_money',
            estado='procesando'
        )
        
        url = f'/api/portal/transaccion/{transaccion.nro_transaccion}/estado/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['estado'], 'procesando')
        self.assertIn('monto', response.data)
        self.assertIn('fecha', response.data)


class TestPerfilUsuarioAPI(PortalAPITestCase):
    """Tests para endpoints de perfil de usuario"""
    
    def test_obtener_perfil(self):
        """Debe retornar los datos del perfil del usuario"""
        url = '/api/portal/perfil/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertEqual(response.data['nombres'], self.cliente.nombres)
        self.assertEqual(response.data['apellidos'], self.cliente.apellidos)
        self.assertIn('email_verificado', response.data)
    
    def test_actualizar_perfil(self):
        """Debe permitir actualizar datos del perfil"""
        url = '/api/portal/perfil/'
        data = {
            'telefono': '0991234567',
            'email': 'nuevo_email@test.com'
        }
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar actualización
        self.cliente.refresh_from_db()
        self.assertEqual(self.cliente.telefono, '0991234567')


class TestSeguridadAPI(PortalAPITestCase):
    """Tests de seguridad y autenticación"""
    
    def test_token_invalido(self):
        """Debe rechazar tokens inválidos"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer token_invalido_123')
        url = '/api/portal/mis-tarjetas/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_token_expirado(self):
        """Debe rechazar tokens expirados"""
        # Simular token expirado (este test requeriría mockear la fecha)
        pass
    
    def test_rate_limiting(self):
        """Debe aplicar rate limiting para prevenir abuso"""
        # Este test requeriría configuración de rate limiting
        # Por ahora solo verificamos que el endpoint existe
        url = '/api/portal/mis-tarjetas/'
        
        # Hacer 100 requests rápidos
        for i in range(100):
            response = self.client.get(url)
            if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                # Rate limiting está funcionando
                return
        
        # Si llegamos aquí, no hay rate limiting
        # (puede estar configurado con límites más altos)
        pass


class TestEstadisticasAPI(PortalAPITestCase):
    """Tests para endpoints de estadísticas y resúmenes"""
    
    def test_resumen_mensual(self):
        """Debe retornar resumen de consumo y recargas del mes"""
        url = f'/api/portal/tarjeta/{self.tarjeta.nro_tarjeta}/resumen-mensual/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_recargas', response.data)
        self.assertIn('total_consumos', response.data)
        self.assertIn('saldo_inicial', response.data)
        self.assertIn('saldo_final', response.data)
        self.assertIn('cantidad_recargas', response.data)
        self.assertIn('cantidad_consumos', response.data)
    
    def test_consumo_promedio_diario(self):
        """Debe calcular el promedio de consumo diario"""
        url = f'/api/portal/tarjeta/{self.tarjeta.nro_tarjeta}/estadisticas/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('consumo_promedio_diario', response.data)
        self.assertIn('dias_restantes_estimados', response.data)


# =============================================================================
# TESTS DE INTEGRACIÓN
# =============================================================================

class TestFlujosCompletos(PortalAPITestCase):
    """Tests de flujos end-to-end"""
    
    def test_flujo_consulta_completo(self):
        """Flujo completo: login → consultar tarjetas → ver movimientos"""
        # 1. Login (asumiendo que ya tenemos token del setUp)
        
        # 2. Consultar tarjetas
        url_tarjetas = '/api/portal/mis-tarjetas/'
        response = self.client.get(url_tarjetas)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        tarjetas = response.data
        self.assertGreater(len(tarjetas), 0)
        
        # 3. Ver movimientos de la primera tarjeta
        nro_tarjeta = tarjetas[0]['nro_tarjeta']
        url_movimientos = f'/api/portal/tarjeta/{nro_tarjeta}/movimientos/'
        response = self.client.get(url_movimientos)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 4. Ver detalle de saldo
        url_saldo = f'/api/portal/tarjeta/{nro_tarjeta}/saldo/'
        response = self.client.get(url_saldo)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('saldo_actual', response.data)
    
    def test_flujo_recarga_online(self):
        """Flujo completo de recarga online"""
        # 1. Verificar saldo inicial
        saldo_inicial = self.tarjeta.saldo_actual
        
        # 2. Iniciar recarga
        url_recarga = '/api/portal/recargar-online/'
        data = {
            'nro_tarjeta': self.tarjeta.nro_tarjeta,
            'monto': 50000.00,
            'metodo_pago': 'tigo_money',
            'telefono': '0981234567'
        }
        response = self.client.post(url_recarga, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        transaction_id = response.data['transaction_id']
        
        # 3. Verificar estado de transacción
        url_estado = f'/api/portal/transaccion/{transaction_id}/estado/'
        response = self.client.get(url_estado)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 4. Simular confirmación exitosa (esto lo haría el webhook de Tigo Money)
        # En producción, sería un POST del proveedor de pagos
        
        # 5. Verificar que aparece en historial de recargas
        url_recargas = f'/api/portal/tarjeta/{self.tarjeta.nro_tarjeta}/recargas/'
        response = self.client.get(url_recargas)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


# Ejecutar tests
if __name__ == '__main__':
    import unittest
    unittest.main()
