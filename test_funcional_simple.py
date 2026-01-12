"""
Script de pruebas funcionales simples (sin migraciones)
"""
import requests
import json

BASE_URL = "http://192.168.100.10:8000"

def test_validaciones():
    """Probar que las páginas de validaciones cargan"""
    print("\n📋 PROBANDO VALIDACIONES...")
    
    urls = [
        "/pos/validaciones/cargas-pendientes/",
        "/pos/validaciones/pagos-pendientes/",
    ]
    
    for url in urls:
        try:
            response = requests.get(BASE_URL + url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {url} → OK (200)")
            elif response.status_code == 302:
                print(f"⚠️  {url} → Redirect (302) - Requiere login")
            else:
                print(f"❌ {url} → Error ({response.status_code})")
        except Exception as e:
            print(f"❌ {url} → Error: {e}")

def test_servidor():
    """Verificar que el servidor está corriendo"""
    print("\n🔌 VERIFICANDO SERVIDOR...")
    try:
        response = requests.get(BASE_URL, timeout=5)
        print(f"✅ Servidor respondiendo en {BASE_URL}")
        return True
    except:
        print(f"❌ Servidor no responde en {BASE_URL}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("PRUEBAS FUNCIONALES - CANTINA TITA")
    print("="*60)
    
    if test_servidor():
        test_validaciones()
        
        print("\n" + "="*60)
        print("✅ PRUEBAS COMPLETADAS")
        print("="*60)
        print("\n📌 PRÓXIMOS PASOS:")
        print("  1. Iniciar sesión en el sistema")
        print("  2. Ir a las URLs de validaciones")
        print("  3. Probar gestión de empleados con AJAX")
        print("  4. Verificar que no hay errores en consola")
    else:
        print("\n❌ Asegúrate de que el servidor esté corriendo:")
        print("   python manage.py runserver 192.168.100.10:8000")
