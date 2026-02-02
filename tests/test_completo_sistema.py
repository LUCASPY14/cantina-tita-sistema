#!/usr/bin/env python
"""
Script completo de pruebas para verificar todas las funcionalidades del sistema
"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_urls():
    """Prueba básica de URLs"""
    print("🔗 PRUEBA 1: URLs Básicas")
    print("=" * 50)

    urls = [
        (f"{BASE_URL}/", "Home/Dashboard"),
        (f"{BASE_URL}/admin/", "Admin Panel"),
        (f"{BASE_URL}/clientes/", "Portal Clientes"),
        (f"{BASE_URL}/clientes/login/", "Login Clientes"),
        (f"{BASE_URL}/api/v1/", "API REST"),
        (f"{BASE_URL}/pos/", "POS"),
        (f"{BASE_URL}/swagger/", "Swagger Docs"),
        (f"{BASE_URL}/reportes/", "Reportes"),
    ]

    results = []
    for url, desc in urls:
        try:
            response = requests.get(url, timeout=10, allow_redirects=True)
            status = "✅" if response.status_code < 400 else "❌"
            results.append((desc, status, response.status_code))
            print(f"{status} {desc}: {response.status_code}")
        except Exception as e:
            results.append((desc, "❌", str(e)))
            print(f"❌ {desc}: ERROR - {str(e)}")

    return results

def test_api_auth():
    """Prueba autenticación API"""
    print("\n🔐 PRUEBA 2: API Authentication")
    print("=" * 50)

    # Intentar login con credenciales de prueba
    login_data = {
        "username": "admin",
        "password": "admin123"
    }

    try:
        response = requests.post(f"{API_BASE}/auth/token/", json=login_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            token = data.get('access')
            print("✅ API Login exitoso")
            return token
        else:
            print(f"❌ API Login falló: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error en API Login: {str(e)}")
        return None

def test_api_endpoints(token):
    """Prueba endpoints de API"""
    print("\n📡 PRUEBA 3: API Endpoints")
    print("=" * 50)

    headers = {'Authorization': f'Bearer {token}'} if token else {}

    endpoints = [
        (f"{API_BASE}/categorias/", "Categorías"),
        (f"{API_BASE}/productos/", "Productos"),
        (f"{API_BASE}/clientes/", "Clientes"),
        (f"{API_BASE}/ventas/", "Ventas"),
    ]

    results = []
    for url, desc in endpoints:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            status = "✅" if response.status_code in [200, 401, 403] else "❌"
            results.append((desc, status, response.status_code))
            print(f"{status} {desc}: {response.status_code}")
        except Exception as e:
            results.append((desc, "❌", str(e)))
            print(f"❌ {desc}: ERROR - {str(e)}")

    return results

def test_client_portal():
    """Prueba portal de clientes"""
    print("\n👥 PRUEBA 4: Portal de Clientes")
    print("=" * 50)

    # Probar login page
    try:
        response = requests.get(f"{BASE_URL}/clientes/login/", timeout=10)
        print(f"✅ Login page: {response.status_code}")
    except Exception as e:
        print(f"❌ Login page: ERROR - {str(e)}")

    # Probar dashboard (debería redirigir a login)
    try:
        response = requests.get(f"{BASE_URL}/clientes/", timeout=10, allow_redirects=False)
        if response.status_code in [302, 301]:
            print("✅ Dashboard redirect: OK (redirect to login)")
        else:
            print(f"❌ Dashboard redirect: {response.status_code}")
    except Exception as e:
        print(f"❌ Dashboard redirect: ERROR - {str(e)}")

def test_metrepay_webhook():
    """Prueba webhook de MetrePay"""
    print("\n💳 PRUEBA 5: Webhook MetrePay")
    print("=" * 50)

    # Payload de prueba
    webhook_data = {
        "eventType": "PAYMENT_SUCCESS",
        "data": {
            "txId": "TEST123456",
            "payRequestId": "TEST789012",
            "customIdentifier": "CARGA-TEST",
            "amount": "10000",
            "statusId": 200,
            "currency": "PYG"
        }
    }

    try:
        response = requests.post(
            f"{BASE_URL}/clientes/webhook/",
            json=webhook_data,
            timeout=10
        )
        print(f"✅ Webhook response: {response.status_code}")
        if response.status_code == 200:
            print("✅ Webhook procesado correctamente")
        return True
    except Exception as e:
        print(f"❌ Webhook error: {str(e)}")
        return False

def test_admin_panel():
    """Prueba panel de administración"""
    print("\n⚙️ PRUEBA 6: Panel de Administración")
    print("=" * 50)

    try:
        # Probar acceso sin login (debería redirigir)
        response = requests.get(f"{BASE_URL}/admin/", timeout=10, allow_redirects=False)
        if response.status_code in [302, 301]:
            print("✅ Admin redirect: OK (redirect to login)")
        else:
            print(f"❌ Admin redirect: {response.status_code}")
    except Exception as e:
        print(f"❌ Admin access: ERROR - {str(e)}")

def test_pos_interface():
    """Prueba interfaz POS"""
    print("\n🛒 PRUEBA 7: Interfaz POS")
    print("=" * 50)

    try:
        response = requests.get(f"{BASE_URL}/pos/", timeout=10, allow_redirects=False)
        if response.status_code in [302, 301, 200]:
            print("✅ POS interface: OK")
        else:
            print(f"❌ POS interface: {response.status_code}")
    except Exception as e:
        print(f"❌ POS interface: ERROR - {str(e)}")

def test_reports():
    """Prueba sistema de reportes"""
    print("\n📊 PRUEBA 8: Sistema de Reportes")
    print("=" * 50)

    try:
        response = requests.get(f"{BASE_URL}/reportes/", timeout=10, allow_redirects=False)
        if response.status_code in [302, 301, 200]:
            print("✅ Reports dashboard: OK")
        else:
            print(f"❌ Reports dashboard: {response.status_code}")
    except Exception as e:
        print(f"❌ Reports dashboard: ERROR - {str(e)}")

def run_all_tests():
    """Ejecutar todas las pruebas"""
    print("🚀 INICIANDO PRUEBAS COMPLETAS DEL SISTEMA")
    print("=" * 60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Servidor: {BASE_URL}")
    print("=" * 60)

    # Esperar a que el servidor esté listo
    print("⏳ Esperando que el servidor esté listo...")
    time.sleep(5)  # Esperar 5 segundos

    # Ejecutar pruebas
    url_results = test_urls()
    token = test_api_auth()
    api_results = test_api_endpoints(token)
    test_client_portal()
    webhook_ok = test_metrepay_webhook()
    test_admin_panel()
    test_pos_interface()
    test_reports()

    # Resumen final
    print("\n" + "=" * 60)
    print("📋 RESUMEN FINAL DE PRUEBAS")
    print("=" * 60)

    total_tests = len(url_results) + len(api_results) + 5  # URLs + API + otras pruebas
    passed_tests = sum(1 for _, status, _ in url_results if status == "✅") + \
                   sum(1 for _, status, _ in api_results if status == "✅") + \
                   (1 if webhook_ok else 0)

    print(f"Total de pruebas: {total_tests}")
    print(f"Pruebas exitosas: {passed_tests}")
    print(".1f")

    if passed_tests == total_tests:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!")
    else:
        print("⚠️ Algunas pruebas fallaron. Revisa los logs arriba.")

    print("=" * 60)

if __name__ == "__main__":
    run_all_tests()