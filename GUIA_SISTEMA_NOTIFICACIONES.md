# GUÍA COMPLETA: Sistema de Notificaciones - Cantina Tita
## WhatsApp, SMS y Email

---

## 📋 ÍNDICE

1. [Estado del Sistema](#estado-del-sistema)
2. [Configuración SMTP (Email)](#configuración-smtp)
3. [Configuración SMS](#configuración-sms)
4. [Configuración WhatsApp](#configuración-whatsapp)
5. [Testing](#testing)
6. [Templates Creados](#templates-creados)
7. [Notificaciones Disponibles](#notificaciones-disponibles)
8. [Uso del Sistema](#uso-del-sistema)
9. [Automatización con Celery](#automatización)
10. [Troubleshooting](#troubleshooting)

---

## ✅ ESTADO DEL SISTEMA

### **Completado (100%)**
- ✅ **Módulo de Notificaciones** (`gestion/notificaciones.py`)
  - Funciones para email, SMS y WhatsApp
  - Soporte multi-proveedor (Twilio, Tigo, Personal, Business API)
  - Logging y manejo de errores robusto
  
- ✅ **Templates de Email HTML**
  - `emails/saldo_bajo.html` - Alerta de saldo bajo
  - `emails/recarga_exitosa.html` - Confirmación de recarga
  - `emails/cuenta_pendiente.html` - Recordatorio de deuda
  
- ✅ **Vista Actualizada**
  - `pos_views.enviar_notificacion_saldo()` ahora usa el sistema real
  - Soporte multi-canal (email + SMS + WhatsApp)
  
- ✅ **Modelos de Base de Datos**
  - `SolicitudesNotificacion` - Registro de notificaciones enviadas
  - `AlertasSistema` - Alertas del sistema
  - `Notificacion` - Notificaciones del portal
  - `PreferenciaNotificacion` - Preferencias de usuario

### **Pendiente de Configuración**
- ⚠️ **SMTP**: Cambiar `EMAIL_BACKEND` de `console` a `smtp` (5 minutos)
- ⚠️ **SMS**: Configurar cuenta de proveedor (Twilio/Tigo/Personal) (1-2 horas)
- ⚠️ **WhatsApp**: Configurar API Business o Twilio (2-4 horas)

---

## 📧 CONFIGURACIÓN SMTP (EMAIL)

### **Opción 1: Gmail (Desarrollo/Testing)**

1. **Crear App Password en Gmail:**
   - Ve a: https://myaccount.google.com/security
   - Activar "Verificación en 2 pasos"
   - Generar "Contraseña de aplicación"

2. **Agregar al `.env`:**
```ini
# Email Configuration (Gmail)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu_email@gmail.com
EMAIL_HOST_PASSWORD=tu_app_password_16_digitos
DEFAULT_FROM_EMAIL=Cantina Tita <tu_email@gmail.com>
```

3. **Actualizar `settings.py`:**
```python
# Email settings
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='Cantina Tita <noreply@cantitatita.com>')
```

### **Opción 2: SendGrid (Producción - Recomendado)**

1. **Crear cuenta en SendGrid:**
   - https://sendgrid.com/ (100 emails/día gratis)
   - Verificar dominio
   - Crear API Key

2. **Instalar paquete:**
```bash
pip install sendgrid-django
```

3. **Configurar `.env`:**
```ini
# Email Configuration (SendGrid)
EMAIL_BACKEND=sendgrid_backend.SendgridBackend
SENDGRID_API_KEY=tu_sendgrid_api_key
DEFAULT_FROM_EMAIL=Cantina Tita <noreply@tudominio.com>
SENDGRID_SANDBOX_MODE_IN_DEBUG=False
```

### **Opción 3: AWS SES (Producción Escalable)**

1. **Configurar AWS SES:**
   - Crear cuenta AWS
   - Verificar email/dominio en SES
   - Crear credenciales IAM

2. **Instalar paquete:**
```bash
pip install django-ses
```

3. **Configurar `.env`:**
```ini
# Email Configuration (AWS SES)
EMAIL_BACKEND=django_ses.SESBackend
AWS_ACCESS_KEY_ID=tu_access_key
AWS_SECRET_ACCESS_KEY=tu_secret_key
AWS_SES_REGION_NAME=us-east-1
AWS_SES_REGION_ENDPOINT=email.us-east-1.amazonaws.com
DEFAULT_FROM_EMAIL=Cantina Tita <noreply@tudominio.com>
```

---

## 📱 CONFIGURACIÓN SMS

### **Opción 1: Twilio (Internacional)**

1. **Crear cuenta en Twilio:**
   - https://www.twilio.com/
   - Verificar teléfono
   - Comprar número Twilio ($1/mes)
   - Obtener Account SID y Auth Token

2. **Instalar paquete:**
```bash
pip install twilio
```

3. **Configurar `.env`:**
```ini
# SMS Configuration (Twilio)
SMS_PROVIDER=twilio
TWILIO_ACCOUNT_SID=tu_account_sid
TWILIO_AUTH_TOKEN=tu_auth_token
TWILIO_PHONE_NUMBER=+14155551234
```

4. **Costo estimado:**
   - Número: $1/mes
   - SMS a Paraguay: $0.05-0.10 por mensaje

### **Opción 2: Tigo Paraguay (Local)**

1. **Contactar Tigo Business:**
   - Teléfono: 1515 (opción empresas)
   - Email: empresas@tigo.com.py
   - Solicitar "API SMS Gateway"

2. **Configurar `.env`:**
```ini
# SMS Configuration (Tigo Paraguay)
SMS_PROVIDER=tigo
TIGO_SMS_API_KEY=tu_api_key_tigo
TIGO_SMS_API_URL=https://api.tigo.com.py/sms/send
```

3. **Ventajas:**
   - Integración local
   - Posible costo más bajo
   - Soporte en español

### **Opción 3: Personal Paraguay (Local)**

1. **Contactar Personal Empresas:**
   - Teléfono: *2000
   - Web: https://personal.com.py/empresas
   - Solicitar servicio SMS masivo

2. **Configurar `.env`:**
```ini
# SMS Configuration (Personal)
SMS_PROVIDER=personal
PERSONAL_SMS_API_KEY=tu_api_key_personal
PERSONAL_SMS_API_URL=https://api.personal.com.py/sms
```

---

## 💬 CONFIGURACIÓN WHATSAPP

### **Opción 1: WhatsApp Business API (Oficial)**

1. **Requisitos:**
   - Verificar empresa en Facebook Business Manager
   - Número telefónico dedicado (no puede usarse en WhatsApp personal)
   - Aprobación de Facebook (2-5 días)

2. **Pasos:**
   - Ir a: https://business.facebook.com/
   - Crear Business Manager
   - Agregar WhatsApp Business
   - Solicitar API access
   - Obtener Phone Number ID y Access Token

3. **Configurar `.env`:**
```ini
# WhatsApp Configuration (Business API)
WHATSAPP_PROVIDER=business_api
WHATSAPP_ACCESS_TOKEN=tu_access_token
WHATSAPP_PHONE_NUMBER_ID=tu_phone_number_id
```

4. **Ventajas:**
   - Oficial y confiable
   - Sin riesgo de ban
   - Analytics integrados

5. **Desventajas:**
   - Proceso de aprobación largo
   - Costo por mensaje (~$0.005-0.01)
   - Requiere número dedicado

### **Opción 2: Twilio WhatsApp**

1. **Crear cuenta Twilio:**
   - https://www.twilio.com/console/sms/whatsapp/sandbox
   - Activar WhatsApp Sandbox (testing gratuito)
   - Para producción: solicitar aprobación de número

2. **Configurar `.env`:**
```ini
# WhatsApp Configuration (Twilio)
WHATSAPP_PROVIDER=twilio
TWILIO_ACCOUNT_SID=tu_account_sid
TWILIO_AUTH_TOKEN=tu_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

3. **Sandbox (Testing):**
   - Los usuarios deben enviar código de activación primero
   - Ejemplo: "join <código>" al número sandbox
   - Válido solo 24 horas

4. **Producción:**
   - Solicitar número WhatsApp propio
   - Costo: $1/mes + $0.005/mensaje

### **Opción 3: Baileys (No Oficial - No Recomendado para Producción)**

⚠️ **ADVERTENCIA**: Baileys usa WhatsApp Web sin autorización oficial. Riesgo de ban.

1. **Instalar (solo para testing):**
```bash
npm install @whiskeysockets/baileys
```

2. **Implementación básica:**
```javascript
// baileys_server.js
const { default: makeWASocket } = require('@whiskeysockets/baileys')

async function sendMessage(phone, message) {
    const sock = makeWASocket({
        // configuration
    })
    await sock.sendMessage(phone + '@s.whatsapp.net', { text: message })
}
```

3. **NO USAR EN PRODUCCIÓN** - Solo para testing personal

---

## 🧪 TESTING

### **Test 1: Email (Local)**

```bash
python manage.py shell
```

```python
from gestion.models import Tarjeta
from gestion.notificaciones import enviar_email_saldo_bajo

# Buscar una tarjeta de prueba
tarjeta = Tarjeta.objects.filter(
    id_hijo__id_cliente_responsable__email__isnull=False
).first()

# Enviar email de prueba
resultado = enviar_email_saldo_bajo(tarjeta)
print(f"Email enviado: {resultado}")

# Verificar en consola (si EMAIL_BACKEND=console)
# o en el buzón de entrada (si SMTP configurado)
```

### **Test 2: SMS (con Twilio)**

```python
from gestion.notificaciones import enviar_sms

# Enviar SMS de prueba
resultado = enviar_sms('+595981234567', 'Mensaje de prueba desde Cantina Tita')
print(f"SMS enviado: {resultado}")
```

### **Test 3: Notificación Multi-Canal**

```python
from gestion.models import Tarjeta
from gestion.notificaciones import notificar_saldo_bajo

tarjeta = Tarjeta.objects.first()

# Enviar por todos los canales configurados
resultados = notificar_saldo_bajo(tarjeta, canales=['email', 'sms', 'whatsapp'])
print(f"Resultados: {resultados}")

# Verificar en base de datos
from gestion.models import SolicitudesNotificacion
notificaciones = SolicitudesNotificacion.objects.filter(nro_tarjeta=tarjeta).order_by('-id_solicitud')
for n in notificaciones[:5]:
    print(f"{n.destino}: {n.estado} - {n.fecha_solicitud}")
```

### **Test 4: Desde el Dashboard**

1. Ir a: http://localhost:8000/pos/alertas/tarjetas-saldo/
2. Buscar tarjeta con saldo bajo
3. Click en botón "📧 Notificar"
4. Verificar respuesta JSON con resultados

---

## 📄 TEMPLATES CREADOS

### **1. saldo_bajo.html**
- **Ubicación:** `gestion/templates/emails/saldo_bajo.html`
- **Uso:** Alerta de saldo bajo en tarjeta
- **Diseño:** 
  - Header rojo con icono de alerta
  - Tabla con datos del estudiante
  - Saldo actual destacado
  - Botón CTA "Realizar Recarga"
  - Footer con datos de contacto

### **2. recarga_exitosa.html**
- **Ubicación:** `gestion/templates/emails/recarga_exitosa.html`
- **Uso:** Confirmación de recarga exitosa
- **Diseño:**
  - Header verde con check
  - Monto de recarga destacado
  - Tabla con detalles de transacción
  - Nuevo saldo disponible
  - Botón "Ver Movimientos"

### **3. cuenta_pendiente.html**
- **Ubicación:** `gestion/templates/emails/cuenta_pendiente.html`
- **Uso:** Recordatorio de cuenta pendiente
- **Diseño:**
  - Header amarillo/naranja
  - Monto deudor destacado
  - Tabla con datos del cliente
  - Medios de pago disponibles
  - Advertencia de suspensión del servicio

---

## 📢 NOTIFICACIONES DISPONIBLES

### **1. Saldo Bajo**
```python
from gestion.notificaciones import notificar_saldo_bajo

# Notificar por email y SMS
notificar_saldo_bajo(tarjeta, canales=['email', 'sms'])
```

**Cuándo usar:**
- Saldo < Gs. 5,000 (configurable)
- Al consultar dashboard de alertas
- Tarea automática diaria (18:00)

### **2. Recarga Exitosa**
```python
from gestion.notificaciones import notificar_recarga_exitosa

# Notificar recarga exitosa
notificar_recarga_exitosa(recarga, canales=['email'])
```

**Cuándo usar:**
- Inmediatamente después de procesar recarga
- En vista de recargas (pos_views.py)

### **3. Cuenta Pendiente**
```python
from gestion.notificaciones import notificar_cuenta_pendiente

# Notificar deuda
notificar_cuenta_pendiente(cliente, canales=['email', 'sms'])
```

**Cuándo usar:**
- Clientes con deuda > 7 días
- Tarea automática semanal (lunes 9:00)

---

## 🚀 USO DEL SISTEMA

### **Desde Vistas (Manual)**

```python
# En gestion/pos_views.py o cualquier vista

from gestion.notificaciones import notificar_saldo_bajo, notificar_recarga_exitosa

@login_required
def procesar_recarga(request):
    # ... código de recarga ...
    
    # Notificar recarga exitosa
    if recarga.estado == 'Aprobada':
        notificar_recarga_exitosa(recarga, canales=['email'])
    
    return JsonResponse({'success': True})
```

### **Desde Signals (Automático)**

```python
# En gestion/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from gestion.models import Recargas
from gestion.notificaciones import notificar_recarga_exitosa

@receiver(post_save, sender=Recargas)
def notificar_recarga_signal(sender, instance, created, **kwargs):
    """Notificar automáticamente al crear recarga"""
    if created and instance.estado == 'Aprobada':
        notificar_recarga_exitosa(instance, canales=['email'])
```

### **Desde Management Commands**

```python
# gestion/management/commands/notificar_saldos_bajos.py

from django.core.management.base import BaseCommand
from gestion.models import Tarjeta
from gestion.notificaciones import notificar_saldo_bajo

class Command(BaseCommand):
    help = 'Notifica tarjetas con saldo bajo'

    def handle(self, *args, **options):
        tarjetas_bajas = Tarjeta.objects.filter(
            saldo_actual__lt=5000,
            activo=True
        )
        
        for tarjeta in tarjetas_bajas:
            resultados = notificar_saldo_bajo(tarjeta, canales=['email'])
            self.stdout.write(f"Tarjeta {tarjeta.nro_tarjeta}: {resultados}")
```

Ejecutar:
```bash
python manage.py notificar_saldos_bajos
```

---

## ⏰ AUTOMATIZACIÓN CON CELERY

### **1. Instalar Celery**

```bash
pip install celery redis
```

### **2. Configurar Celery**

**Crear: `gestion/celery_app.py`**
```python
from celery import Celery
from celery.schedules import crontab
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'anteproyecto.settings')

app = Celery('gestion')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Programar tareas
app.conf.beat_schedule = {
    'notificar-saldos-bajos-diario': {
        'task': 'gestion.tasks.verificar_saldos_bajos',
        'schedule': crontab(hour=18, minute=0),  # Todos los días 18:00
    },
    'notificar-cuentas-pendientes-semanal': {
        'task': 'gestion.tasks.verificar_cuentas_pendientes',
        'schedule': crontab(day_of_week=1, hour=9, minute=0),  # Lunes 9:00
    },
}
```

### **3. Crear Tareas**

**Crear: `gestion/tasks.py`**
```python
from celery import shared_task
from gestion.models import Tarjeta, Cliente
from gestion.notificaciones import notificar_saldo_bajo, notificar_cuenta_pendiente
import logging

logger = logging.getLogger(__name__)

@shared_task
def verificar_saldos_bajos():
    """Tarea diaria: Verificar y notificar saldos bajos"""
    tarjetas_bajas = Tarjeta.objects.filter(
        saldo_actual__lt=5000,
        activo=True,
        id_hijo__id_cliente_responsable__email__isnull=False
    )
    
    notificadas = 0
    for tarjeta in tarjetas_bajas:
        try:
            resultados = notificar_saldo_bajo(tarjeta, canales=['email'])
            if any(resultados.values()):
                notificadas += 1
        except Exception as e:
            logger.error(f"Error notificando tarjeta {tarjeta.nro_tarjeta}: {e}")
    
    logger.info(f"Tarea completada: {notificadas} notificaciones enviadas")
    return f"Notificadas {notificadas} de {tarjetas_bajas.count()} tarjetas"


@shared_task
def verificar_cuentas_pendientes():
    """Tarea semanal: Notificar cuentas pendientes"""
    from gestion.cuenta_corriente import calcular_saldo_cliente
    
    clientes = Cliente.objects.filter(
        activo=True,
        email__isnull=False
    )
    
    notificados = 0
    for cliente in clientes:
        saldo = calcular_saldo_cliente(cliente)
        if saldo < 0:  # Tiene deuda
            try:
                resultados = notificar_cuenta_pendiente(cliente, canales=['email'])
                if any(resultados.values()):
                    notificados += 1
            except Exception as e:
                logger.error(f"Error notificando cliente {cliente.id_cliente}: {e}")
    
    logger.info(f"Tarea completada: {notificados} notificaciones enviadas")
    return f"Notificados {notificados} clientes con deuda"
```

### **4. Ejecutar Celery**

**Terminal 1 - Redis:**
```bash
redis-server
```

**Terminal 2 - Celery Worker:**
```bash
celery -A gestion.celery_app worker -l info
```

**Terminal 3 - Celery Beat (scheduler):**
```bash
celery -A gestion.celery_app beat -l info
```

---

## 🔧 TROUBLESHOOTING

### **Problema 1: Emails no se envían**

**Síntomas:**
- `enviar_email_saldo_bajo()` retorna `True` pero no llega email

**Soluciones:**
1. Verificar `EMAIL_BACKEND` en settings.py
2. Si es `console`, los emails se imprimen en terminal
3. Verificar credenciales SMTP en `.env`
4. Revisar logs: `tail -f logs/django.log`
5. Test manual:
```python
from django.core.mail import send_mail
send_mail('Test', 'Mensaje', 'from@example.com', ['to@example.com'])
```

### **Problema 2: Error "SMTPAuthenticationError"**

**Causa:** Credenciales incorrectas o "Apps menos seguras" bloqueadas

**Solución Gmail:**
1. Activar verificación en 2 pasos
2. Generar "Contraseña de aplicación"
3. Usar esa contraseña en `EMAIL_HOST_PASSWORD`

### **Problema 3: SMS no se envían (Twilio)**

**Síntomas:**
- Error 401: Credenciales incorrectas
- Error 403: Número no verificado

**Soluciones:**
1. Verificar `TWILIO_ACCOUNT_SID` y `TWILIO_AUTH_TOKEN`
2. En cuenta trial, verificar número destino primero
3. Revisar balance de cuenta Twilio

### **Problema 4: WhatsApp devuelve error 403**

**Causa:** Access Token expirado o Phone Number ID incorrecto

**Solución:**
1. Generar nuevo token en Business Manager
2. Verificar `WHATSAPP_PHONE_NUMBER_ID`
3. Revisar permisos del token (whatsapp_business_messages)

### **Problema 5: Notificaciones duplicadas**

**Causa:** Celery ejecutando tareas múltiples veces

**Solución:**
1. Verificar solo hay un worker corriendo
2. Usar `task_acks_late=True` en configuración
3. Agregar deduplicación:
```python
from django.core.cache import cache

@shared_task
def verificar_saldos_bajos():
    lock_id = 'verificar_saldos_bajos_lock'
    if cache.get(lock_id):
        return "Tarea ya en ejecución"
    
    cache.set(lock_id, True, timeout=3600)
    try:
        # ... código de la tarea ...
    finally:
        cache.delete(lock_id)
```

---

## 📊 MONITOREO

### **Ver Notificaciones Enviadas**

```python
from gestion.models import SolicitudesNotificacion
from django.utils import timezone
from datetime import timedelta

# Últimas 24 horas
ayer = timezone.now() - timedelta(days=1)
notificaciones = SolicitudesNotificacion.objects.filter(
    fecha_solicitud__gte=ayer
).order_by('-fecha_solicitud')

for n in notificaciones:
    print(f"{n.fecha_solicitud} | {n.destino} | {n.estado} | {n.nro_tarjeta.nro_tarjeta}")
```

### **Estadísticas**

```python
from django.db.models import Count

# Por canal
stats = SolicitudesNotificacion.objects.values('destino').annotate(
    total=Count('id_solicitud')
)

# Por estado
stats_estado = SolicitudesNotificacion.objects.values('estado').annotate(
    total=Count('id_solicitud')
)

print("Por canal:", stats)
print("Por estado:", stats_estado)
```

---

## 📝 CHECKLIST DE IMPLEMENTACIÓN

### **Fase 1: Email (5-10 minutos)**
- [ ] Crear App Password en Gmail
- [ ] Agregar configuración SMTP al `.env`
- [ ] Cambiar `EMAIL_BACKEND` a SMTP en settings.py
- [ ] Test envío de email
- [ ] Verificar recepción

### **Fase 2: SMS (1-2 horas)**
- [ ] Crear cuenta en Twilio/Tigo/Personal
- [ ] Obtener credenciales API
- [ ] Agregar configuración SMS al `.env`
- [ ] Test envío de SMS
- [ ] Verificar recepción

### **Fase 3: WhatsApp (2-4 horas)**
- [ ] Decidir proveedor (Business API vs Twilio)
- [ ] Crear/aprobar cuenta
- [ ] Obtener credenciales
- [ ] Agregar configuración al `.env`
- [ ] Test envío WhatsApp
- [ ] Verificar recepción

### **Fase 4: Automatización (30 minutos)**
- [ ] Instalar Celery y Redis
- [ ] Crear `celery_app.py`
- [ ] Crear `tasks.py` con tareas programadas
- [ ] Iniciar Redis
- [ ] Iniciar Celery Worker
- [ ] Iniciar Celery Beat
- [ ] Verificar logs

### **Fase 5: Monitoreo (15 minutos)**
- [ ] Configurar logging
- [ ] Crear dashboard de monitoreo
- [ ] Configurar alertas de fallos
- [ ] Documentar procedimientos

---

## 🎯 PRÓXIMOS PASOS

1. **Configurar SMTP** (prioritario)
2. **Testear emails** en ambiente de desarrollo
3. **Investigar proveedores SMS Paraguay** (Tigo vs Personal vs Twilio)
4. **Evaluar costos** de cada proveedor
5. **Decidir estrategia WhatsApp** (oficial vs Twilio)
6. **Implementar Celery** para automatización
7. **Crear dashboard de monitoreo** de notificaciones
8. **Configurar preferencias de usuario** (portal padres)

---

## 📞 SOPORTE

- **Documentación Django Email:** https://docs.djangoproject.com/en/5.2/topics/email/
- **Twilio Docs:** https://www.twilio.com/docs
- **WhatsApp Business API:** https://developers.facebook.com/docs/whatsapp
- **Celery Docs:** https://docs.celeryq.dev/en/stable/

---

**Fecha de creación:** {{ fecha_actual }}  
**Versión:** 1.0  
**Estado:** ✅ Listo para configurar y usar
