#!/usr/bin/env python
"""
Prueba rápida del servidor
"""
import requests
import time

def test_server():
    print('🔍 Probando servidor Django...')
    time.sleep(3)  # Esperar que el servidor inicie

    tests = [
        ('http://localhost:8000/', 'Home'),
        ('http://localhost:8000/admin/', 'Admin'),
        ('http://localhost:8000/clientes/login/', 'Portal Login'),
        ('http://localhost:8000/clientes/', 'Portal Clientes'),
        ('http://localhost:8000/api/v1/', 'API REST'),
        ('http://localhost:8000/swagger/', 'Swagger'),
    ]

    passed = 0
    total = len(tests)

    for url, name in tests:
        try:
            response = requests.get(url, timeout=10, allow_redirects=True)
            if response.status_code < 400:
                print(f'✅ {name}: {response.status_code}')
                passed += 1
            else:
                print(f'❌ {name}: {response.status_code}')
        except Exception as e:
            print(f'❌ {name}: ERROR - {str(e)[:50]}...')

    print(f'\n📊 Resultado: {passed}/{total} pruebas pasaron')
    if passed == total:
        print('🎉 ¡Todas las funcionalidades están funcionando!')
    else:
        print('⚠️ Algunas funcionalidades necesitan revisión')

if __name__ == "__main__":
    test_server()