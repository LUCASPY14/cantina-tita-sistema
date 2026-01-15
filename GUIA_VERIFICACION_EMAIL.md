# 📧 Guía de Verificación de Email - Portal de Padres

## 🎯 Descripción General

El sistema tiene un mecanismo de verificación de email para asegurar que los usuarios del Portal de Padres sean propietarios legítimos de las direcciones de correo que registran.

---

## 🔄 Flujo Automático de Verificación

### 1. **Registro del Usuario**
Cuando se crea un `UsuarioPortal`:
- `email_verificado` = `False` (por defecto)
- Se genera automáticamente una contraseña = RUC/CI del cliente

### 2. **Envío de Email de Verificación**
```python
from gestion.portal_views import enviar_email_verificacion

# Enviar email de verificación
enviar_email_verificacion(usuario_portal)
```

El sistema:
- Crea un `TokenVerificacion` único y seguro (32 bytes)
- Establece expiración de 24 horas
- Envía email con enlace: `http://127.0.0.1:8000/portal/verificar-email/{token}/`

### 3. **Usuario Hace Click en el Enlace**
- Accede a: `/portal/verificar-email/<token>/`
- El sistema valida el token (no expirado, no usado)
- Marca `email_verificado = True`
- Marca el token como `usado = True`
- Redirige al login con mensaje de éxito

---

## 🛠️ Métodos de Verificación

### **MÉTODO 1: Admin Manual (Desarrollo/Testing) ⚡ RÁPIDO**

**Pasos:**

1. Acceder al admin: http://127.0.0.1:8000/admin/gestion/usuarioportal/

2. **Seleccionar usuarios** (checkboxes en columna izquierda)

3. En el desplegable **"Acción"**, elegir: **"✅ Marcar email como verificado"**

4. Click en **"Ir"**

✅ **Resultado**: Emails verificados instantáneamente

**Ventajas:**
- Inmediato
- No requiere configuración de email
- Ideal para testing local

**Desventajas:**
- No hay validación real del email
- No cumple con mejores prácticas de seguridad

---

### **MÉTODO 2: Reenvío de Email (Admin) 📧**

**Nueva acción agregada al admin:**

1. Acceder al admin: http://127.0.0.1:8000/admin/gestion/usuarioportal/

2. **Seleccionar usuarios NO verificados**

3. En el desplegable **"Acción"**, elegir: **"📧 Reenviar email de verificación"**

4. Click en **"Ir"**

✅ **Resultado**: 
- Se crea nuevo token de verificación
- Se envía email al usuario
- Usuario recibe enlace de verificación

**Ventajas:**
- Proceso real de verificación
- Usuario valida su email
- Registro de tokens en BD

**Configuración Actual:**
```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

📝 **IMPORTANTE**: Con `console.EmailBackend`, los emails se muestran en la consola/terminal, **NO se envían realmente**.

---

### **MÉTODO 3: Script de Prueba 🔧**

**Ejecutar:**
```powershell
D:/anteproyecto20112025/.venv/Scripts/python.exe test_envio_email_verificacion.py
```

**Funcionalidad:**
- Lista usuarios sin verificar
- Permite enviar email a uno o todos
- Muestra el contenido del email en consola

**Ejemplo de salida:**
```
======================================================================
📧 TEST DE ENVÍO DE EMAIL DE VERIFICACIÓN
======================================================================

Usuarios sin verificar: 2

1. ventas@abc.com.py - Cliente: MARCOS LOPEZ
2. carmen.rodriguez@example.com - Cliente: CARMEN RODRIGUEZ

----------------------------------------------------------------------

¿Desea enviar email de verificación? (s/n o número específico): 1

📤 Enviando email a: ventas@abc.com.py...

✓ Email enviado correctamente

📧 Configuración actual:
   - Backend: django.core.mail.backends.console.EmailBackend
   - El email se muestra en la consola (no se envía realmente)
   - Para producción, configurar SMTP en settings.py
```

---

### **MÉTODO 4: Envío Programático (Código Python) 💻**

**Desde Django shell o código:**

```python
from gestion.models import UsuarioPortal
from gestion.portal_views import enviar_email_verificacion

# Obtener usuario
usuario = UsuarioPortal.objects.get(email='ejemplo@email.com')

# Enviar email de verificación
if enviar_email_verificacion(usuario):
    print(f"✓ Email enviado a {usuario.email}")
else:
    print(f"✗ Error al enviar email")
```

---

## 🔐 Estructura de Tokens

### Modelo `TokenVerificacion`:

```python
class TokenVerificacion(models.Model):
    usuario_portal = ForeignKey(UsuarioPortal)
    token = CharField(max_length=100, unique=True)  # 32 bytes URL-safe
    tipo = CharField(max_length=50)  # 'email_verification'
    usado = BooleanField(default=False)
    creado_en = DateTimeField(auto_now_add=True)
    expira_en = DateTimeField()  # +24 horas desde creación
```

**Validación del token:**
```python
def es_valido(self):
    return not self.usado and timezone.now() < self.expira_en
```

---

## 📨 Configuración de Email para Producción

### **Opción 1: Gmail (Development/Testing)**

```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'tu-email@gmail.com'
EMAIL_HOST_PASSWORD = 'tu-app-password'  # App Password de Google
DEFAULT_FROM_EMAIL = 'Portal Padres <tu-email@gmail.com>'
```

### **Opción 2: SendGrid (Producción)**

```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = 'tu-sendgrid-api-key'
DEFAULT_FROM_EMAIL = 'noreply@cantinatita.com'
```

### **Opción 3: Mailgun**

```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'postmaster@tu-dominio.mailgun.org'
EMAIL_HOST_PASSWORD = 'tu-mailgun-password'
DEFAULT_FROM_EMAIL = 'Portal Padres <noreply@cantinatita.com>'
```

---

## 🧪 Testing Local (Sin SMTP)

**Opción 1: Console Backend (Actual)**
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```
📺 Los emails se imprimen en la terminal donde corre `runserver`

**Opción 2: File Backend**
```python
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = BASE_DIR / 'sent_emails'
```
📁 Los emails se guardan como archivos en `sent_emails/`

**Opción 3: MailHog (Docker)**
```bash
docker run -d -p 1025:1025 -p 8025:8025 mailhog/mailhog
```
```python
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
```
🌐 Ver emails en: http://localhost:8025

---

## 📊 Consultas Útiles

### **Verificar estado de usuarios:**
```python
from gestion.models import UsuarioPortal

# Total de usuarios
total = UsuarioPortal.objects.count()

# Usuarios verificados
verificados = UsuarioPortal.objects.filter(email_verificado=True).count()

# Usuarios sin verificar
sin_verificar = UsuarioPortal.objects.filter(email_verificado=False).count()

print(f"Total: {total}")
print(f"Verificados: {verificados} ({verificados/total*100:.1f}%)")
print(f"Sin verificar: {sin_verificar} ({sin_verificar/total*100:.1f}%)")
```

### **Ver tokens pendientes:**
```python
from gestion.models import TokenVerificacion
from django.utils import timezone

# Tokens válidos (no usados, no expirados)
tokens_validos = TokenVerificacion.objects.filter(
    usado=False,
    expira_en__gt=timezone.now()
)

for token in tokens_validos:
    print(f"{token.usuario_portal.email} - Expira: {token.expira_en}")
```

### **Limpiar tokens expirados:**
```python
from gestion.models import TokenVerificacion
from django.utils import timezone

# Eliminar tokens expirados
tokens_expirados = TokenVerificacion.objects.filter(
    expira_en__lt=timezone.now()
)
count = tokens_expirados.count()
tokens_expirados.delete()

print(f"✓ {count} tokens expirados eliminados")
```

---

## 🚀 Recomendaciones

### **Para Desarrollo:**
1. Usar verificación manual desde admin (Método 1)
2. O usar `console.EmailBackend` y copiar el enlace de la consola

### **Para Testing:**
1. Usar MailHog o Mailtrap
2. Configurar `test_envio_email_verificacion.py`

### **Para Producción:**
1. Configurar SMTP real (Gmail, SendGrid, Mailgun)
2. Usar dominio propio en `DEFAULT_FROM_EMAIL`
3. Implementar rate limiting en envío de emails
4. Agregar tarea programada para limpiar tokens expirados
5. Considerar agregar reenvío automático si usuario no verifica

---

## 📞 URLs Relacionadas

- **Verificación**: `/portal/verificar-email/<token>/`
- **Admin Usuarios Portal**: `/admin/gestion/usuarioportal/`
- **Portal Login**: `/portal/login/`
- **Portal Registro**: `/portal/registro/` (si existe)

---

## 🔍 Troubleshooting

### **Email no llega:**
1. Verificar configuración SMTP en `settings.py`
2. Revisar consola/terminal si usa `console.EmailBackend`
3. Verificar que `SITE_URL` sea correcto
4. Revisar logs de Django

### **Token inválido:**
1. Verificar que no haya expirado (24 horas)
2. Confirmar que no se haya usado ya
3. Generar nuevo token reenviando email

### **Usuario ya verificado:**
1. Revisar campo `email_verificado` en admin
2. No es necesario verificar nuevamente

---

## 📝 Código Fuente

- **Modelo**: `gestion/models.py` - Línea 3258 (`TokenVerificacion`)
- **Vistas**: `gestion/portal_views.py` - Línea 260 (`verificar_email_view`)
- **Admin**: `gestion/admin.py` - Línea 578 (`UsuarioPortalAdmin`)
- **URLs**: `gestion/portal_urls.py` - Línea 12
