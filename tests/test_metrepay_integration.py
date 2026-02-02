"""
Script de prueba completo para integración MetrePay
Crea datos de prueba y prueba el flujo completo de pagos
"""
import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timedelta

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from gestion.models import Cliente, Tarjeta, UsuariosWebClientes, Ventas, CargasSaldo, Hijo
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory
from gestion.cliente_views import procesar_pago_metrepay, metrepay_webhook_view
from django.db import transaction
from django.utils import timezone
import json

def crear_datos_prueba_metrepay():
    """Crear datos mínimos necesarios para probar MetrePay"""
    print("🧪 CREANDO DATOS DE PRUEBA PARA METREPAY")
    print("=" * 60)

    # Buscar o crear cliente
    cliente = Cliente.objects.filter(activo=True).first()
    if not cliente:
        print("❌ No hay clientes activos en el sistema")
        return None

    print(f"✓ Cliente encontrado: {cliente.nombres} {cliente.apellidos}")

    # Buscar o crear usuario web para el cliente
    usuario_web = UsuariosWebClientes.objects.filter(id_cliente=cliente).first()
    if not usuario_web:
        # Crear usuario web básico
        usuario_web = UsuariosWebClientes.objects.create(
            id_cliente=cliente,
            usuario=f"cliente_{cliente.id_cliente}",
            password_hash="test123",  # En producción usar hash real
            activo=True
        )
        print(f"✓ Usuario web creado: {usuario_web.usuario}")

    # Buscar hijos del cliente
    hijos = Hijo.objects.filter(id_cliente_responsable=cliente, activo=True)
    if not hijos.exists():
        print("❌ El cliente no tiene hijos activos")
        return None

    # Buscar tarjeta de cualquiera de sus hijos
    tarjeta = None
    for hijo in hijos:
        tarjeta = Tarjeta.objects.filter(id_hijo=hijo, estado='Activa').first()
        if tarjeta:
            break

    if not tarjeta:
        print("❌ El cliente no tiene tarjetas activas")
        return None

    print(f"✓ Tarjeta encontrada: {tarjeta.nro_tarjeta} (Saldo: Gs. {tarjeta.saldo_actual:,})")

    return cliente, usuario_web, tarjeta

def probar_carga_saldo(cliente, usuario_web, tarjeta):
    """Probar flujo de carga de saldo"""
    print("\n💰 PROBANDO CARGA DE SALDO")
    print("-" * 40)

    # Simular request
    factory = RequestFactory()
    request = factory.post('/portal/cargar_saldo/', {
        'monto': '100000',
        'metodo_pago': 'metrepay'
    })

    # Simular sesión
    request.session = {
        'cliente_id': cliente.id_cliente,
        'cliente_usuario': f"{cliente.nombres} {cliente.apellidos}"
    }

    try:
        # Llamar a la función de procesamiento
        exito, referencia, payment_url, custom_id = procesar_pago_metrepay(
            Decimal('100000'), 'metrepay', request, tipo_pago='CARGA_SALDO'
        )

        if exito:
            print("✅ Carga de saldo iniciada:")
            print(f"   Referencia: {referencia}")
            print(f"   URL de pago: {payment_url}")
            print(f"   Custom ID: {custom_id}")

            # Simular el guardado del registro (como hace la vista real)
            with transaction.atomic():
                carga_saldo = CargasSaldo.objects.create(
                    nro_tarjeta=tarjeta,
                    id_cliente_origen=cliente,
                    fecha_carga=timezone.now(),
                    monto_cargado=Decimal('100000'),
                    referencia=referencia,
                    estado='PENDIENTE',
                    custom_identifier=custom_id,
                    pay_request_id=referencia,
                    id_nota=None  # Asegurar que no cause problemas con triggers
                )
                
                # Actualizar saldo de la tarjeta
                tarjeta.saldo_actual += 100000
                tarjeta.save()
                
            print("✅ Registro de carga creado en BD:")
            print(f"   ID Carga: {carga_saldo.id_carga}")
            print(f"   Estado: {carga_saldo.estado}")
            print(f"   Monto: Gs. {carga_saldo.monto_cargado}")
            print(f"   Nuevo saldo tarjeta: Gs. {tarjeta.saldo_actual}")

            return custom_id
        else:
            print(f"❌ Error iniciando carga: {referencia}")
            return None

    except Exception as e:
        print(f"❌ Error en carga de saldo: {str(e)}")
        return None

def probar_pago_deudas(cliente, usuario_web, tarjeta):
    """Probar flujo de pago de deudas"""
    print("\n💳 PROBANDO PAGO DE DEUDAS")
    print("-" * 40)

    # Crear una venta pendiente para el cliente
    try:
        venta = Ventas.objects.filter(
            id_cliente=cliente,
            saldo_pendiente__gt=0
        ).first()

        if not venta:
            print("⚠ No hay ventas pendientes. Creando una venta de prueba...")

            # Crear una venta pendiente (esto requiere más configuración)
            print("⚠ Para probar pagos de deudas, necesitas ventas pendientes reales")
            print("   Puedes crearlas desde el POS o ejecutar otras pruebas primero")
            return None

        print(f"✓ Venta pendiente encontrada: ID {venta.id_venta} - Saldo: Gs. {venta.saldo_pendiente}")

        # Simular request
        factory = RequestFactory()
        request = factory.post('/portal/pagar_deudas/', {
            'venta_ids': str(venta.id_venta),
            'metodo_pago': 'metrepay'
        })

        request.session = {
            'cliente_id': cliente.id_cliente,
            'cliente_usuario': f"{cliente.nombres} {cliente.apellidos}"
        }

        try:
            exito, referencia, payment_url, custom_id = procesar_pago_metrepay(
                venta.saldo_pendiente, 'metrepay', request,
                tipo_pago='PAGO_DEUDAS', venta_ids=[venta.id_venta]
            )

            if exito:
                print("✅ Pago de deudas iniciado:")
                print(f"   Referencia: {referencia}")
                print(f"   URL de pago: {payment_url}")
                print(f"   Custom ID: {custom_id}")
                return custom_id
            else:
                print(f"❌ Error iniciando pago: {referencia}")
                return None

        except Exception as e:
            print(f"❌ Error en pago de deudas: {str(e)}")
            return None

    except Exception as e:
        print(f"❌ Error buscando ventas: {str(e)}")
        return None

def probar_webhook(custom_id_carga=None, custom_id_pago=None):
    """Probar procesamiento de webhook"""
    print("\n🔗 PROBANDO WEBHOOK DE CONFIRMACIÓN")
    print("-" * 40)

    # Simular request de webhook
    factory = RequestFactory()

    # Probar webhook para carga de saldo
    if custom_id_carga:
        webhook_data_carga = {
            "event": "PAYMENT_SUCCESS",
            "data": {
                "payRequestId": "MP-TEST-123",
                "customIdentifier": custom_id_carga,
                "amount": "100000",
                "statusId": 200,
                "currency": "PYG"
            }
        }

        request = factory.post('/api/webhooks/metrepay/',
                              data=json.dumps(webhook_data_carga),
                              content_type='application/json')

        try:
            response = metrepay_webhook_view(request)
            if hasattr(response, 'status_code') and response.status_code == 200:
                print("✅ Webhook de carga de saldo procesado correctamente")
            else:
                print(f"❌ Error en webhook de carga: {response}")
        except Exception as e:
            print(f"❌ Error procesando webhook de carga: {str(e)}")

    # Probar webhook para pago de deudas
    if custom_id_pago:
        webhook_data_pago = {
            "event": "PAYMENT_SUCCESS",
            "data": {
                "payRequestId": "MP-TEST-456",
                "customIdentifier": custom_id_pago,
                "amount": "50000",
                "statusId": 200,
                "currency": "PYG"
            }
        }

        request = factory.post('/api/webhooks/metrepay/',
                              data=json.dumps(webhook_data_pago),
                              content_type='application/json')

        try:
            response = metrepay_webhook_view(request)
            if hasattr(response, 'status_code') and response.status_code == 200:
                print("✅ Webhook de pago de deudas procesado correctamente")
            else:
                print(f"❌ Error en webhook de pago: {response}")
        except Exception as e:
            print(f"❌ Error procesando webhook de pago: {str(e)}")

def ejecutar_pruebas():
    """Ejecutar todas las pruebas"""
    print("🚀 INICIANDO PRUEBAS COMPLETAS DE METREPAY")
    print("=" * 60)

    # Crear datos de prueba
    datos = crear_datos_prueba_metrepay()
    if not datos:
        print("❌ No se pudieron crear datos de prueba")
        return

    cliente, usuario_web, tarjeta = datos

    # Probar carga de saldo
    custom_id_carga = probar_carga_saldo(cliente, usuario_web, tarjeta)

    # Probar pago de deudas
    custom_id_pago = probar_pago_deudas(cliente, usuario_web, tarjeta)

    # Probar webhooks
    probar_webhook(custom_id_carga, custom_id_pago)

    print("\n" + "=" * 60)
    print("✅ PRUEBAS COMPLETADAS")
    print("=" * 60)
    print("\n📋 RESUMEN:")
    print("- Modo simulado: Sin token API configurado")
    print("- Para producción: Configurar METREPAY_API_TOKEN en .env")
    print("- Webhook URL: https://tudominio.com/api/webhooks/metrepay/")

if __name__ == "__main__":
    ejecutar_pruebas()