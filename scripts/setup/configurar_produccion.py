"""
Script para configurar el sistema para producción
Genera SECRET_KEY segura y actualiza settings.py
"""
import secrets
import os
from pathlib import Path

print("=" * 80)
print("🔐 CONFIGURACIÓN DE SEGURIDAD PARA PRODUCCIÓN")
print("=" * 80)
print()

# 1. Generar nueva SECRET_KEY
print("1️⃣  Generando nueva SECRET_KEY segura...")
nueva_secret_key = secrets.token_urlsafe(50)
print(f"   ✅ SECRET_KEY generada: {nueva_secret_key[:20]}... ({len(nueva_secret_key)} caracteres)")
print()

# 2. Leer settings.py actual
settings_path = Path('cantina_project/settings.py')
with open(settings_path, 'r', encoding='utf-8') as f:
    contenido = f.read()

# 3. Preparar cambios
cambios = []

# Cambiar DEBUG
if "DEBUG = True" in contenido:
    print("2️⃣  Configurando DEBUG = False...")
    contenido_nuevo = contenido.replace("DEBUG = True", "DEBUG = False")
    cambios.append("DEBUG = False")
else:
    print("2️⃣  DEBUG ya está en False ✅")
    contenido_nuevo = contenido

# Cambiar SECRET_KEY
print("3️⃣  Actualizando SECRET_KEY...")
import re
# Buscar la línea de SECRET_KEY
patron = r"SECRET_KEY = ['\"].*?['\"]"
if re.search(patron, contenido_nuevo):
    contenido_nuevo = re.sub(patron, f'SECRET_KEY = "{nueva_secret_key}"', contenido_nuevo)
    cambios.append("SECRET_KEY actualizada")
else:
    print("   ⚠️  No se encontró SECRET_KEY en settings.py")

# 4. Configurar ALLOWED_HOSTS si está vacío
print("4️⃣  Configurando ALLOWED_HOSTS...")
if "ALLOWED_HOSTS = []" in contenido_nuevo:
    # Agregar hosts comunes
    contenido_nuevo = contenido_nuevo.replace(
        "ALLOWED_HOSTS = []",
        "ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'cantina-tita.edu.py', 'www.cantina-tita.edu.py']"
    )
    cambios.append("ALLOWED_HOSTS configurado")
    print("   ✅ ALLOWED_HOSTS configurado")
else:
    print("   ℹ️  ALLOWED_HOSTS ya tiene valores")

# 5. Habilitar configuraciones de HTTPS (comentadas por ahora)
print("5️⃣  Configurando opciones de HTTPS...")
configuraciones_https = """
# Configuración de seguridad HTTPS
# DESCOMENTAR cuando se configure SSL/HTTPS en producción
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# SECURE_HSTS_SECONDS = 31536000  # 1 año
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_BROWSER_XSS_FILTER = True
# SECURE_CONTENT_TYPE_NOSNIFF = True  # Ya está activado
# X_FRAME_OPTIONS = 'DENY'  # Ya está configurado
"""

# Agregar al final si no existe
if "SECURE_SSL_REDIRECT" not in contenido_nuevo:
    contenido_nuevo += "\n" + configuraciones_https
    cambios.append("Configuraciones HTTPS agregadas (comentadas)")
    print("   ✅ Configuraciones HTTPS agregadas (comentadas)")
else:
    print("   ℹ️  Configuraciones HTTPS ya existen")

# 6. Configurar STATIC_ROOT si no existe
print("6️⃣  Configurando STATIC_ROOT...")
if "STATIC_ROOT" not in contenido_nuevo or "STATIC_ROOT = None" in contenido_nuevo:
    static_config = """
# Archivos estáticos para producción
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
"""
    contenido_nuevo += "\n" + static_config
    cambios.append("STATIC_ROOT configurado")
    print("   ✅ STATIC_ROOT configurado")
else:
    print("   ℹ️  STATIC_ROOT ya está configurado")

# 7. Crear backup del settings.py actual
print()
print("7️⃣  Creando backup de configuración actual...")
backup_path = Path('cantina_project/settings.py.backup_antes_produccion')
with open(backup_path, 'w', encoding='utf-8') as f:
    f.write(contenido)
print(f"   ✅ Backup guardado: {backup_path}")

# 8. Guardar nuevo settings.py
print()
print("8️⃣  Guardando nueva configuración...")
with open(settings_path, 'w', encoding='utf-8') as f:
    f.write(contenido_nuevo)
print(f"   ✅ Archivo actualizado: {settings_path}")

# 9. Crear archivo .env de ejemplo con la SECRET_KEY
print()
print("9️⃣  Creando archivo .env.example...")
env_content = f"""# Archivo de configuración de entorno para producción
# Copiar este archivo a .env y completar los valores

# Django
SECRET_KEY={nueva_secret_key}
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,cantina-tita.edu.py

# Base de datos
DB_NAME=cantinatitadb
DB_USER=root
DB_PASSWORD=tu_password_aqui
DB_HOST=localhost
DB_PORT=3306

# Email (SMTP)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=cantina.tita@gmail.com
EMAIL_HOST_PASSWORD=tu_app_password_aqui
EMAIL_USE_TLS=True

# Ekuatia (Facturación Electrónica)
EKUATIA_API_KEY=tu_api_key_aqui
EKUATIA_MODO=testing  # cambiar a 'production' cuando esté listo

# Configuración HTTPS (descomentar cuando SSL esté configurado)
# SECURE_SSL_REDIRECT=True
# SESSION_COOKIE_SECURE=True
# CSRF_COOKIE_SECURE=True
"""

with open('.env.example', 'w', encoding='utf-8') as f:
    f.write(env_content)
print("   ✅ Archivo .env.example creado")

# 10. Resumen
print()
print("=" * 80)
print("📊 RESUMEN DE CAMBIOS")
print("=" * 80)
for i, cambio in enumerate(cambios, 1):
    print(f"{i}. ✅ {cambio}")

print()
print("=" * 80)
print("🎯 CONFIGURACIÓN PARA PRODUCCIÓN LISTA")
print("=" * 80)
print()
print("📋 PRÓXIMOS PASOS MANUALES:")
print()
print("1. 🔐 SEGURIDAD:")
print("   • Verificar que DEBUG=False en settings.py")
print("   • Guardar SECRET_KEY en lugar seguro (gestor de contraseñas)")
print("   • NO subir SECRET_KEY a repositorio Git")
print()
print("2. 🌐 HTTPS:")
print("   • Configurar certificado SSL")
print("   • Descomentar líneas de SECURE_* en settings.py")
print("   • Probar que redirige HTTP → HTTPS")
print()
print("3. 📧 EMAIL:")
print("   • Ejecutar: python configurar_smtp.py")
print("   • Probar envío de email de prueba")
print()
print("4. 🗂️ ARCHIVOS ESTÁTICOS:")
print("   • Ejecutar: python manage.py collectstatic")
print("   • Configurar nginx/Apache para servir /static/")
print()
print("5. 🔄 BACKUP:")
print("   • Ejecutar: python configurar_backup_tareas.py")
print("   • Verificar tarea programada en Windows")
print()
print("6. 🧪 TESTING:")
print("   • Ejecutar: python auditoria_seguridad.py")
print("   • Verificar que no haya problemas críticos")
print()
print("7. 📝 DOCUMENTACIÓN:")
print("   • Leer: MANUAL_ADMINISTRADORES.md")
print("   • Leer: GUIA_DESPLIEGUE_PRODUCCION.md")
print()
print("=" * 80)
print()
print("⚠️  IMPORTANTE:")
print("   • Hacer backup completo antes de desplegar")
print("   • Probar en entorno de staging primero")
print("   • Monitorear logs después del despliegue")
print()
print("✅ Configuración completada exitosamente")
print("=" * 80)
