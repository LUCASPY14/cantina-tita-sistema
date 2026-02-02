import subprocess
import sys

def run_makemigrations():
    """Ejecuta makemigrations respondiendo automáticamente"""
    cmd = [sys.executable, "manage.py", "makemigrations", "gestion"]
    responses = []
    for _ in range(5):
        responses.extend(["1", ""])  # "1" para la opción, "" para Enter
    input_text = "\n".join(responses)
    print("🔧 Ejecutando makemigrations con respuestas automáticas...")
    try:
        result = subprocess.run(
            cmd,
            input=input_text,
            text=True,
            capture_output=True,
            timeout=30
        )
        print("✅ Makemigrations completado")
        print("Salida:", result.stdout)
        if result.stderr:
            print("Errores:", result.stderr)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("❌ Timeout - El proceso tardó demasiado")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("=== RESOLVIENDO MÚLTIPLES MIGRACIONES CON auto_now_add ===")
    print("\n📋 Modelos detectados:")
    print("   1. Notificacion - ✅ Completado")
    print("   2. PreferenciaNotificacion - ⏳ Pendiente")
    print("   3. [Posibles otros modelos]")
    print("\n⚡ Ejecutando solución automática...")
    if run_makemigrations():
        print("\n✅ ¡Todas las migraciones creadas!")
        print("\n🔧 Ahora aplica las migraciones:")
        print("   python manage.py migrate gestion")
    else:
        print("\n❌ Hubo un problema. Hazlo manualmente:")
        print("""
   Para CADA modelo que aparezca:
   1. Selecciona opción: 1
   2. Presiona Enter para usar timezone.now
   3. Repite para el siguiente modelo
        """)

if __name__ == '__main__':
    main()
