"""
Script de prueba para integración con MetrePay API
Basado en colección de Postman proporcionada
"""
import os
import requests
from datetime import datetime

# Configuración
METREPAY_BASE_URL = "https://test.metrepay.com/api"
API_TOKEN = os.getenv('METREPAY_API_TOKEN', 'solicitar_token_real')

class MetrePayClient:
    def __init__(self, api_token, base_url=METREPAY_BASE_URL):
        self.api_token = api_token
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Api-Token': self.api_token,
            'Content-Type': 'application/json'
        })

    def crear_pago_unico(self, label, amount, handle_value, handle_label,
                        custom_identifier, redirect_url=None):
        """Crear un link de pago único"""
        endpoint = f"{self.base_url}/saleitems/add"

        payload = {
            "label": label,
            "amount": int(amount),
            "handleValue": handle_value,
            "handleLabel": handle_label,
            "customIdentifier": custom_identifier,
            "singlePayment": True,
            "creditAndDebitCard": True,
        }

        if redirect_url:
            payload["redirectUrl"] = redirect_url

        try:
            response = self.session.post(endpoint, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            return {
                'success': True,
                'payment_id': data.get('id') or data.get('paymentId'),
                'payment_url': data.get('paymentUrl') or data.get('url'),
                'status': data.get('status'),
                'data': data
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'response': getattr(e.response, 'text', '') if hasattr(e, 'response') else ''
            }

    def consultar_pago(self, payment_id):
        """Consultar estado de un pago"""
        endpoint = f"{self.base_url}/payrequests/{payment_id}"

        try:
            response = self.session.get(endpoint, timeout=30)
            response.raise_for_status()
            data = response.json()
            return {
                'success': True,
                'status': data.get('status'),
                'amount': data.get('amount'),
                'paid': data.get('paid', False),
                'data': data
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e)
            }

def probar_metrepay():
    """Función de prueba"""
    client = MetrePayClient(API_TOKEN)

    print("=== PRUEBA DE METREPAY API ===")
    print(f"URL Base: {METREPAY_BASE_URL}")
    print(f"Token configurado: {'Sí' if API_TOKEN != 'solicitar_token_real' else 'No'}")
    print()

    # Probar creación de pago único
    print("1. Creando pago único de prueba...")
    resultado = client.crear_pago_unico(
        label="Carga de saldo - Portal Web",
        amount=50000,
        handle_value="cliente_prueba@cantina.com",
        handle_label="Cliente de Prueba",
        custom_identifier="CARGA-001",
        redirect_url="https://cantina-tita.com/portal/pago_exitoso/"
    )

    if resultado['success']:
        print("✅ Pago único creado:")
        print(f"   ID: {resultado['payment_id']}")
        print(f"   URL: {resultado['payment_url']}")
        print(f"   Estado: {resultado['status']}")

        # Consultar estado
        if resultado['payment_id']:
            print("\n2. Consultando estado del pago...")
            consulta = client.consultar_pago(resultado['payment_id'])
            if consulta['success']:
                print(f"✅ Estado actual: {consulta['status']}")
                print(f"   Monto: {consulta['amount']}")
                print(f"   Pagado: {consulta['paid']}")
            else:
                print(f"❌ Error consultando: {consulta['error']}")
    else:
        print(f"❌ Error creando pago: {resultado['error']}")
        if 'response' in resultado:
            print(f"   Respuesta: {resultado['response']}")

if __name__ == "__main__":
    probar_metrepay()