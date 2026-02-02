# 📧 Configuración de SMTP para Emails Reales

**Fecha:** 8 de Diciembre de 2025  
**Sistema:** Cantina Tita v1.0  
**Tiempo estimado:** 15-20 minutos

---

## ✅ SMTP ACTIVADO EN EL CÓDIGO

La configuración SMTP ya está activa en `settings.py`. Ahora solo necesitas configurar las credenciales en tu archivo `.env`.

---

## 🎯 OPCIONES DE SERVICIO SMTP

### Opción 1: Gmail (Gratis) ⭐ Recomendado para desarrollo

**Ventajas:**
- ✅ Gratis
- ✅ Fácil de configurar
- ✅ 500 emails/día

**Limitaciones:**
- ⚠️ No recomendado para producción a gran escala
- ⚠️ Requiere App Password (no la contraseña normal)

**Pasos de configuración:**

1. **Generar App Password de Gmail:**
   ```
   a. Ir a: https://myaccount.google.com/apppasswords
   b. Iniciar sesión con tu cuenta Gmail
   c. Nombre de la app: "Cantina Tita Sistema"
   d. Copiar la contraseña de 16 caracteres (ej: "abcd efgh ijkl mnop")
   ```

2. **Configurar archivo `.env`:**
   ```bash
   # Copiar .env.example a .env si no existe
   cp .env.example .env
   
   # Editar .env con tus credenciales
   nano .env  # o usa tu editor favorito
   ```

3. **Agregar en `.env`:**
   ```bash
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=tu_email@gmail.com
   EMAIL_HOST_PASSWORD=abcd efgh ijkl mnop
   ```

4. **Probar configuración:**
   ```bash
   # Activar entorno virtual
   .venv\Scripts\Activate.ps1
   
   # Abrir shell de Django
   python manage.py shell
   ```
   
   ```python
   # En el shell de Python
   from django.core.mail import send_mail
   
   send_mail(
       subject='Test desde Cantina Tita',
       message='Este es un email de prueba. ¡Funciona! 🎉',
       from_email='noreply@cantinatita.com',
       recipient_list=['tu_email@gmail.com'],
       fail_silently=False,
   )
   # Si devuelve 1, el email se envió correctamente
   ```

---

### Opción 2: SendGrid (Gratis) ⭐ Recomendado para producción

**Ventajas:**
- ✅ 100 emails/día gratis (sin tarjeta)
- ✅ 40,000 emails primer mes con tarjeta
- ✅ APIs avanzadas (templates, analytics)
- ✅ Mejor deliverability que Gmail

**Pasos de configuración:**

1. **Crear cuenta SendGrid:**
   ```
   a. Ir a: https://sendgrid.com/
   b. Sign Up (gratis)
   c. Verificar email
   ```

2. **Generar API Key:**
   ```
   a. Dashboard → Settings → API Keys
   b. Create API Key
   c. Nombre: "Cantina Tita"
   d. Permisos: Full Access (o solo Mail Send)
   e. Copiar API Key (empieza con "SG.")
   ```

3. **Configurar en `.env`:**
   ```bash
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.sendgrid.net
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=apikey
   EMAIL_HOST_PASSWORD=SG.tu_api_key_de_sendgrid_aqui
   ```

4. **Verificar dominio (opcional pero recomendado):**
   ```
   a. SendGrid → Settings → Sender Authentication
   b. Authenticate Your Domain
   c. Seguir instrucciones (agregar DNS records)
   d. Mejora reputación y evita spam
   ```

---

### Opción 3: Amazon SES (Para alto volumen)

**Ventajas:**
- ✅ $0.10 por 1,000 emails
- ✅ Escalable infinitamente
- ✅ Integración con AWS

**Limitaciones:**
- ⚠️ Requiere cuenta AWS
- ⚠️ Configuración más compleja

**Pasos:**
1. Crear cuenta AWS
2. Habilitar Amazon SES
3. Verificar dominio/email
4. Obtener SMTP credentials
5. Configurar en `.env`:
   ```bash
   EMAIL_HOST=email-smtp.us-east-1.amazonaws.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=tu_aws_smtp_username
   EMAIL_HOST_PASSWORD=tu_aws_smtp_password
   ```

---

## 🧪 PRUEBAS

### Test 1: Email simple
```python
python manage.py shell

from django.core.mail import send_mail
send_mail('Test', 'Mensaje', 'noreply@cantinatita.com', ['destino@example.com'])
```

### Test 2: Recuperación de contraseña
1. Ir a: http://localhost:8000/seguridad/recuperar-contrasena/
2. Ingresar email de un usuario existente
3. Revisar inbox del email ingresado
4. Debe llegar email con token de recuperación

### Test 3: Notificación de actividad sospechosa
Esto se dispara automáticamente cuando el sistema detecta:
- Múltiples intentos fallidos de login
- Acceso desde IP nueva
- Cambios críticos en configuración

---

## 🔍 VERIFICAR CONFIGURACIÓN ACTUAL

```python
python manage.py shell

from django.conf import settings
print(f"Backend: {settings.EMAIL_BACKEND}")
print(f"Host: {settings.EMAIL_HOST}")
print(f"Port: {settings.EMAIL_PORT}")
print(f"User: {settings.EMAIL_HOST_USER}")
print(f"TLS: {settings.EMAIL_USE_TLS}")
```

---

## 🐛 TROUBLESHOOTING

### Error: "SMTPAuthenticationError"
**Causa:** Credenciales incorrectas

**Soluciones:**
- Gmail: Verificar que usas App Password (no contraseña normal)
- SendGrid: Verificar API key completa (empieza con "SG.")
- Revisar que no hay espacios extra en `.env`

### Error: "SMTPConnectError"
**Causa:** No puede conectar al servidor SMTP

**Soluciones:**
- Verificar puerto (587 para TLS, 465 para SSL)
- Revisar firewall/antivirus
- Verificar conexión a internet

### Error: "SMTPServerDisconnected"
**Causa:** Conexión interrumpida

**Soluciones:**
- Cambiar `EMAIL_USE_TLS = True`
- Probar puerto 465 con `EMAIL_USE_SSL = True`

### Los emails no llegan
**Causa:** Filtros de spam

**Soluciones:**
- Verificar carpeta de spam
- Usar dominio verificado (SendGrid)
- Configurar SPF/DKIM records

---

## 📊 DÓNDE SE USAN LOS EMAILS

| Funcionalidad | Archivo | Descripción |
|---------------|---------|-------------|
| **Recuperación de contraseña** | `gestion/seguridad_utils.py:272` | Envía token temporal |
| **Notificación de seguridad** | `gestion/seguridad_utils.py:1050` | Actividad sospechosa |
| **Comunicación con padres** | `gestion/cliente_views.py:709` | Notificaciones generales |

---

## 🔐 SEGURIDAD

### ✅ BUENAS PRÁCTICAS:

1. **Nunca commitear credenciales:**
   ```bash
   # Verificar que .env está en .gitignore
   cat .gitignore | grep .env
   ```

2. **Usar variables de entorno:**
   - ✅ Credenciales en `.env`
   - ❌ Credenciales hardcodeadas en código

3. **Rotar credenciales:**
   - Cambiar API keys cada 3-6 meses
   - Revocar keys comprometidas inmediatamente

4. **Limitar permisos:**
   - SendGrid: Solo permisos de "Mail Send"
   - AWS: IAM role con permisos mínimos

---

## 🚀 PARA PRODUCCIÓN

### Checklist antes de deploy:

- [ ] EMAIL_BACKEND = smtp (no console)
- [ ] Credenciales en variables de entorno (no en código)
- [ ] Dominio verificado (SendGrid/SES)
- [ ] SPF record configurado
- [ ] DKIM configurado
- [ ] DMARC configurado (opcional)
- [ ] Pruebas de envío realizadas
- [ ] Monitoreo de bounce rate
- [ ] Límites de envío configurados

### Configuración recomendada para producción:

```python
# settings.py
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.sendgrid.net')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')

# Emails de sistema
DEFAULT_FROM_EMAIL = 'noreply@tudominio.com'  # Cambiar por dominio real
SERVER_EMAIL = 'server@tudominio.com'
ADMINS = [('Admin', 'admin@tudominio.com')]
```

---

## 📈 MONITOREO

### Logs de email (desarrollo):
```python
# Los emails se loguean en la consola si usas console.EmailBackend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### Logs de email (producción):
```python
# Django registra errores de email en logs
# Revisar: /var/log/django/email.log

import logging
logger = logging.getLogger('django.mail')
```

### Métricas importantes:
- **Delivery rate:** >95%
- **Bounce rate:** <5%
- **Spam rate:** <0.1%
- **Open rate:** Variable según tipo

---

## ✅ CONCLUSIÓN

**Estado actual:** ✅ SMTP CONFIGURADO EN CÓDIGO

**Para activar:**
1. Elegir servicio (Gmail/SendGrid/SES)
2. Obtener credenciales
3. Configurar `.env`
4. Probar con `send_mail()`

**Tiempo total:** 10-15 minutos

**Próximo paso:** Después de configurar, el sistema enviará emails reales en:
- Recuperación de contraseñas
- Notificaciones de seguridad
- Comunicaciones con padres

---

**Implementado:** 8 de Diciembre de 2025  
**Documentado por:** GitHub Copilot + Claude Sonnet 4.5
