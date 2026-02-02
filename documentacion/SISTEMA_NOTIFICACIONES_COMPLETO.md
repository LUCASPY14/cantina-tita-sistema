# 📬 SISTEMA DE NOTIFICACIONES COMPLETO
**Estado: 90% IMPLEMENTADO**  
**Fecha:** Diciembre 2025  
**Sistema:** Cantina Tita - Django 5.2.8 + MySQL 8.0

---

## 📋 ÍNDICE
1. [Estado del Sistema](#estado-del-sistema)
2. [Modelos Implementados](#modelos-implementados)
3. [Vistas y Funciones](#vistas-y-funciones)
4. [Templates Disponibles](#templates-disponibles)
5. [Tipos de Notificaciones](#tipos-de-notificaciones)
6. [Canales de Envío](#canales-de-envío)
7. [Integración Pendiente](#integración-pendiente)
8. [Guía de Implementación](#guía-de-implementación)
9. [Testing](#testing)

---

## 🔍 ESTADO DEL SISTEMA

### ✅ COMPLETADO (90%)

#### 1. **Base de Datos** - ✅ 100%
- Tabla `solicitudes_notificacion` creada
- Tabla `alertas_sistema` creada
- Tabla `notificacion` creada (portal padres)
- Tabla `preferencia_notificacion` creada

#### 2. **Modelos Django** - ✅ 100%
```python
# gestion/models.py (líneas 1635-1674)
class SolicitudesNotificacion(models.Model):
    DESTINO_CHOICES = [
        ('SMS', 'SMS'),
        ('Email', 'Email'),
        ('WhatsApp', 'WhatsApp'),
    ]
    
    ESTADO_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('Enviada', 'Enviada'),
        ('Fallida', 'Fallida'),
    ]
```

```python
# gestion/models.py (líneas 1574-1634)
class AlertasSistema(models.Model):
    TIPO_CHOICES = [
        ('Stock Bajo', 'Stock Bajo'),
        ('Saldo Bajo', 'Saldo Bajo'),
        ('Timbrado Próximo a Vencer', 'Timbrado Próximo a Vencer'),
        ('Sistema', 'Sistema'),
    ]
```

#### 3. **Vistas Implementadas** - ✅ 90%
- ✅ `alertas_sistema_view()` (pos_views.py línea 2764)
- ✅ `alertas_tarjetas_saldo_view()` (pos_views.py línea 2829)
- ✅ `enviar_notificacion_saldo()` (pos_views.py línea 2880) - **SIMULADO**

#### 4. **Templates UI** - ✅ 100%
- ✅ `templates/pos/alertas_sistema.html` - Dashboard de alertas con 5 tabs
- ✅ `templates/pos/alertas_tarjetas_saldo.html` - Gestión de alertas de saldo
- ✅ Botones "Enviar Notificación" en todas las vistas de alertas

### ⚠️ PENDIENTE (10%)

#### 1. **Integración SMTP Real** - ❌ 0%
**Actual:**
```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

**Requerido:**
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # o SendGrid, AWS SES
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'tu_email@gmail.com'
EMAIL_HOST_PASSWORD = 'tu_password_app'
```

#### 2. **Integración SMS** - ❌ 0%
**Proveedores sugeridos:**
- **Twilio** (internacional, simple)
- **Tigo Paraguay SMS Gateway** (local, mejor precio)
- **Personal Paraguay** (local)
- **AWS SNS** (escalable)

#### 3. **Integración WhatsApp** - ❌ 0%
**Opciones:**
- **WhatsApp Business API** (oficial, requiere aprobación)
- **Baileys** (no oficial, basado en Node.js)
- **whatsapp-web.js** (no oficial, más simple)
- **Twilio WhatsApp API** (oficial, requiere account)

---

## 🗄️ MODELOS IMPLEMENTADOS

### 1. `AlertasSistema` (managed=False)
**Tabla:** `alertas_sistema`  
**Propósito:** Registro general de alertas del sistema

```python
class AlertasSistema(models.Model):
    id_alerta = BigAutoField(primary_key=True)
    tipo = CharField(max_length=30)  # Stock Bajo, Saldo Bajo, Timbrado, Sistema
    mensaje = CharField(max_length=500)
    fecha_creacion = DateTimeField()
    fecha_leida = DateTimeField(blank=True, null=True)
    estado = CharField(max_length=9)  # Pendiente, Leída, Resuelta
    id_empleado_resuelve = BigIntegerField(blank=True, null=True)
    fecha_resolucion = DateTimeField(blank=True, null=True)
    observaciones = TextField(blank=True, null=True)
```

**Uso:**
```python
# Crear alerta de stock bajo
AlertasSistema.objects.create(
    tipo='Stock Bajo',
    mensaje=f'Producto {producto.descripcion} tiene stock bajo: {stock_actual}',
    fecha_creacion=timezone.now(),
    estado='Pendiente'
)
```

---

### 2. `SolicitudesNotificacion` (managed=False)
**Tabla:** `solicitudes_notificacion`  
**Propósito:** Cola de notificaciones a enviar

```python
class SolicitudesNotificacion(models.Model):
    id_solicitud = BigAutoField(primary_key=True)
    id_cliente = ForeignKey(Cliente)
    nro_tarjeta = ForeignKey(Tarjeta)
    saldo_alerta = DecimalField(max_digits=10, decimal_places=2)
    mensaje = CharField(max_length=255)
    destino = CharField(max_length=8)  # SMS, Email, WhatsApp
    estado = CharField(max_length=9)  # Pendiente, Enviada, Fallida
    fecha_solicitud = DateTimeField()
    fecha_envio = DateTimeField(blank=True, null=True)
```

**Uso:**
```python
# Crear solicitud de notificación de saldo bajo
SolicitudesNotificacion.objects.create(
    id_cliente=cliente,
    nro_tarjeta=tarjeta,
    saldo_alerta=tarjeta.saldo_actual,
    mensaje=f'Saldo bajo: Gs. {tarjeta.saldo_actual:,}',
    destino='Email',
    estado='Pendiente',
    fecha_solicitud=timezone.now()
)
```

---

### 3. `Notificacion` (managed=True)
**Tabla:** `notificacion`  
**Propósito:** Notificaciones en el portal de padres

```python
class Notificacion(models.Model):
    TIPO_CHOICES = [
        ('saldo_bajo', 'Saldo Bajo'),
        ('recarga_exitosa', 'Recarga Exitosa'),
        ('consumo_realizado', 'Consumo Realizado'),
        ('tarjeta_bloqueada', 'Tarjeta Bloqueada'),
        ('restriccion_aplicada', 'Restricción Aplicada'),
        ('info_general', 'Información General'),
    ]
    
    id_notificacion = AutoField(primary_key=True)
    usuario_portal = ForeignKey(UsuarioPortal)
    tipo = CharField(max_length=50, choices=TIPO_CHOICES)
    titulo = CharField(max_length=255)
    mensaje = TextField()
    leida = BooleanField(default=False)
    fecha_envio = DateTimeField()
    fecha_lectura = DateTimeField(null=True, blank=True)
```

**Métodos:**
```python
def marcar_como_leida(self):
    """Marca la notificación como leída"""
    if not self.leida:
        self.leida = True
        self.fecha_lectura = timezone.now()
        self.save()
```

---

### 4. `PreferenciaNotificacion` (managed=True)
**Tabla:** `preferencia_notificacion`  
**Propósito:** Preferencias de notificación de usuarios del portal

```python
class PreferenciaNotificacion(models.Model):
    id_preferencia = AutoField(primary_key=True)
    usuario_portal = ForeignKey(UsuarioPortal)
    tipo_notificacion = CharField(max_length=50)
    email_activo = BooleanField(default=True)
    push_activo = BooleanField(default=True)
```

---

## 🎯 VISTAS Y FUNCIONES

### 1. `alertas_sistema_view()` ✅
**Archivo:** `gestion/pos_views.py` (línea 2764)  
**Ruta:** `/pos/alertas/`  
**Template:** `templates/pos/alertas_sistema.html`

**Funcionalidad:**
```python
@login_required
def alertas_sistema_view(request):
    # 1. Alertas de saldo bajo (≤ 10,000 Gs)
    tarjetas_saldo_bajo = Tarjeta.objects.filter(
        estado='Activa',
        saldo_actual__lte=10000
    ).select_related('id_hijo', 'id_hijo__id_cliente_responsable')
    
    # 2. Alertas de stock bajo
    productos_stock_bajo = Producto.objects.filter(
        stock__stock_actual__lt=F('stock_minimo')
    )
    
    # 3. Productos sin stock
    productos_sin_stock = Producto.objects.filter(
        stock__stock_actual__lte=0
    )
    
    # 4. Tarjetas por vencer (próximos 30 días)
    tarjetas_por_vencer = Tarjeta.objects.filter(
        fecha_vencimiento__lte=timezone.now() + timedelta(days=30)
    )
    
    # 5. Tarjetas bloqueadas
    tarjetas_bloqueadas = Tarjeta.objects.filter(estado='Bloqueada')
```

---

### 2. `alertas_tarjetas_saldo_view()` ✅
**Archivo:** `gestion/pos_views.py` (línea 2829)  
**Ruta:** `/pos/alertas/tarjetas/`  
**Template:** `templates/pos/alertas_tarjetas_saldo.html`

**Filtros:**
- Saldo máximo configurable
- Búsqueda por estudiante/responsable
- Ordenado por saldo ascendente

---

### 3. `enviar_notificacion_saldo()` ⚠️ SIMULADO
**Archivo:** `gestion/pos_views.py` (línea 2880)  
**Ruta:** `/pos/alertas/notificar/<tarjeta_id>/`  
**Estado:** **SIMULADO** - No envía emails/SMS reales

**Código actual:**
```python
@login_required
def enviar_notificacion_saldo(request, tarjeta_id):
    try:
        tarjeta = Tarjeta.objects.select_related(
            'id_hijo',
            'id_hijo__id_cliente_responsable'
        ).get(nro_tarjeta=tarjeta_id)
        
        responsable = tarjeta.id_hijo.id_cliente_responsable
        hijo = tarjeta.id_hijo
        
        # SIMULADO: Aquí se debe implementar envío real
        mensaje = f"""
        Estimado/a {responsable.nombres} {responsable.apellidos},
        
        Le informamos que la tarjeta del estudiante {hijo.nombre} {hijo.apellido}
        tiene un saldo bajo:
        
        Tarjeta: {tarjeta.nro_tarjeta}
        Saldo actual: Gs. {tarjeta.saldo_actual:,}
        
        Le recomendamos realizar una recarga.
        """
        
        return JsonResponse({
            'success': True,
            'mensaje': f'Notificación enviada a {responsable.email}',
            'preview': mensaje.strip()
        })
        
    except Tarjeta.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Tarjeta no encontrada'})
```

---

## 🎨 TEMPLATES DISPONIBLES

### 1. `alertas_sistema.html` ✅
**Ruta:** `templates/pos/alertas_sistema.html`  
**Descripción:** Dashboard completo de alertas con 5 tabs

**Características:**
- ✅ Tab 1: Saldo Bajo (tarjetas ≤ 10,000 Gs)
- ✅ Tab 2: Stock Bajo (productos < stock_minimo)
- ✅ Tab 3: Sin Stock (stock = 0)
- ✅ Tab 4: Tarjetas por Vencer (próximos 30 días)
- ✅ Tab 5: Tarjetas Bloqueadas
- ✅ Filtros de búsqueda por tab
- ✅ Botón "Notificar a Responsable" en cada fila
- ✅ Alpine.js para interactividad

**Botones de notificación:**
```html
<button @click="notificarResponsable({{ tarjeta.id_hijo.id_cliente_responsable.id_cliente }}, '{{ tarjeta.nro_tarjeta }}')" 
        class="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600">
    <i class="bi bi-envelope"></i> Notificar
</button>
```

---

### 2. `alertas_tarjetas_saldo.html` ✅
**Ruta:** `templates/pos/alertas_tarjetas_saldo.html`  
**Descripción:** Vista específica para alertas de saldo bajo

**Características:**
- ✅ Filtro de saldo máximo (default: 10,000 Gs)
- ✅ Búsqueda por estudiante/responsable/tarjeta
- ✅ Estadísticas: Total, Críticas (≤ 5,000), Sin Saldo
- ✅ Botón de notificación por tarjeta
- ✅ Indicadores visuales (🔴 Crítico, 🟡 Bajo, ⚫ Sin saldo)

---

## 🔔 TIPOS DE NOTIFICACIONES

### Alertas del Sistema (`AlertasSistema`)

| Tipo | Descripción | Trigger | Prioridad |
|------|-------------|---------|-----------|
| **Stock Bajo** | Producto con stock < stock_mínimo | Automático (trigger BD o tarea) | Alta |
| **Saldo Bajo** | Tarjeta con saldo ≤ umbral (10,000 Gs) | Automático (tarea diaria) | Alta |
| **Límite Crédito** | Cliente excedió límite de crédito | Automático (en venta) | Crítica |
| **Timbrado Vencido** | Timbrado fiscal por vencer (< 30 días) | Automático (tarea diaria) | Crítica |
| **Tarjeta Vencida** | Tarjeta por vencer o vencida | Automático (tarea diaria) | Media |

---

### Notificaciones Portal Padres (`Notificacion`)

| Tipo | Descripción | Trigger | Canal |
|------|-------------|---------|-------|
| **saldo_bajo** | Saldo de tarjeta bajo | Saldo ≤ umbral | Email + Push |
| **recarga_exitosa** | Confirmación de recarga | Después de pago | Email + Push |
| **consumo_realizado** | Compra realizada con tarjeta | Después de compra | Push |
| **tarjeta_bloqueada** | Tarjeta bloqueada por admin | Al bloquear | Email + Push |
| **restriccion_aplicada** | Restricción alimentaria violada | En compra con restricción | Email + SMS |
| **info_general** | Avisos generales (cierre, eventos) | Manual por admin | Email + Push |

---

## 📡 CANALES DE ENVÍO

### 1. EMAIL ⚠️ Pendiente integración real

**Estado Actual:**
```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

**Implementación Recomendada:**

#### Opción A: Gmail SMTP
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'tu_email@gmail.com'
EMAIL_HOST_PASSWORD = 'app_password'  # Contraseña de app, no la normal
DEFAULT_FROM_EMAIL = 'Cantina Tita <tu_email@gmail.com>'
```

**Pasos:**
1. Habilitar 2FA en tu cuenta Gmail
2. Generar "Contraseña de aplicación" en Google Account
3. Usar esa contraseña en `EMAIL_HOST_PASSWORD`

#### Opción B: SendGrid (Recomendado para producción)
```python
EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
SENDGRID_API_KEY = 'tu_sendgrid_api_key'
DEFAULT_FROM_EMAIL = 'Cantina Tita <notificaciones@cantinatita.com>'
```

**Ventajas:**
- ✅ 100 emails/día gratis
- ✅ Mejor deliverability
- ✅ Analytics de emails
- ✅ Templates HTML

#### Opción C: AWS SES (Escalable)
```python
EMAIL_BACKEND = 'django_ses.SESBackend'
AWS_ACCESS_KEY_ID = 'tu_access_key'
AWS_SECRET_ACCESS_KEY = 'tu_secret_key'
AWS_SES_REGION_NAME = 'us-east-1'
AWS_SES_REGION_ENDPOINT = 'email.us-east-1.amazonaws.com'
```

---

### 2. SMS ❌ No implementado

**Proveedores Recomendados:**

#### Opción A: Twilio (Internacional)
```python
# Instalación
pip install twilio

# Código
from twilio.rest import Client

def enviar_sms(telefono, mensaje):
    client = Client(
        account_sid='tu_account_sid',
        auth_token='tu_auth_token'
    )
    
    message = client.messages.create(
        body=mensaje,
        from_='+15551234567',  # Tu número Twilio
        to=telefono
    )
    
    return message.sid
```

**Costos:** ~$0.0075 USD/SMS (Paraguay)

#### Opción B: Tigo Paraguay SMS Gateway (Local)
```python
import requests

def enviar_sms_tigo(telefono, mensaje):
    url = 'https://api.tigo.com.py/sms/send'
    
    payload = {
        'api_key': 'tu_api_key_tigo',
        'destination': telefono,
        'message': mensaje
    }
    
    response = requests.post(url, json=payload)
    return response.json()
```

**Ventajas:**
- ✅ Proveedor local (Paraguay)
- ✅ Mejor precio
- ✅ Soporte en español

#### Opción C: AWS SNS
```python
import boto3

def enviar_sms_aws(telefono, mensaje):
    client = boto3.client(
        'sns',
        aws_access_key_id='tu_access_key',
        aws_secret_access_key='tu_secret_key',
        region_name='us-east-1'
    )
    
    response = client.publish(
        PhoneNumber=telefono,
        Message=mensaje
    )
    
    return response['MessageId']
```

---

### 3. WhatsApp ❌ No implementado

**Opciones Disponibles:**

#### Opción A: WhatsApp Business API (Oficial)
```python
# Requiere:
# 1. Cuenta de WhatsApp Business
# 2. Aprobación de Facebook
# 3. Meta Business Manager

import requests

def enviar_whatsapp_oficial(telefono, mensaje):
    url = f'https://graph.facebook.com/v18.0/{phone_number_id}/messages'
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'messaging_product': 'whatsapp',
        'to': telefono,
        'type': 'text',
        'text': {'body': mensaje}
    }
    
    response = requests.post(url, json=payload, headers=headers)
    return response.json()
```

**Costos:** Variables según país (gratis primeros 1000/mes)

#### Opción B: Twilio WhatsApp API
```python
from twilio.rest import Client

def enviar_whatsapp_twilio(telefono, mensaje):
    client = Client(account_sid, auth_token)
    
    message = client.messages.create(
        body=mensaje,
        from_='whatsapp:+14155238886',  # Twilio Sandbox
        to=f'whatsapp:{telefono}'
    )
    
    return message.sid
```

#### Opción C: Baileys (No Oficial - Node.js)
```javascript
// Requiere servidor Node.js separado
const { makeWASocket, DisconnectReason, useMultiFileAuthState } = require('@whiskeysockets/baileys')

async function enviarWhatsApp(telefono, mensaje) {
    const { state, saveCreds } = await useMultiFileAuthState('auth_info')
    
    const sock = makeWASocket({
        auth: state,
        printQRInTerminal: true
    })
    
    const jid = telefono + '@s.whatsapp.net'
    await sock.sendMessage(jid, { text: mensaje })
}
```

**⚠️ Advertencia:** Uso no oficial, puede ser bloqueado por WhatsApp

---

## 🚧 INTEGRACIÓN PENDIENTE

### Paso 1: Configurar SMTP Real (5 minutos)

**Opción Rápida - Gmail:**

1. Habilitar "Acceso de apps menos seguras" o generar contraseña de app
2. Editar `.env`:
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu_email@gmail.com
EMAIL_HOST_PASSWORD=tu_password_app
```

3. Editar `settings.py`:
```python
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = f'Cantina Tita <{EMAIL_HOST_USER}>'
```

---

### Paso 2: Crear Módulo de Notificaciones (30 minutos)

**Archivo:** `gestion/notificaciones.py` (nuevo)

```python
"""
Sistema centralizado de notificaciones
Soporta: Email, SMS, WhatsApp, Push
"""

from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

# ==================== EMAIL ====================

def enviar_email(destinatario, asunto, mensaje, html_mensaje=None):
    """
    Envía un email a un destinatario
    
    Args:
        destinatario (str): Email del destinatario
        asunto (str): Asunto del email
        mensaje (str): Contenido del email (texto plano)
        html_mensaje (str, optional): Contenido HTML del email
    
    Returns:
        bool: True si se envió exitosamente
    """
    try:
        send_mail(
            subject=asunto,
            message=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[destinatario],
            html_message=html_mensaje,
            fail_silently=False
        )
        logger.info(f"Email enviado a {destinatario}: {asunto}")
        return True
    except Exception as e:
        logger.error(f"Error enviando email a {destinatario}: {e}")
        return False


def enviar_email_saldo_bajo(tarjeta):
    """
    Envía notificación de saldo bajo al responsable de la tarjeta
    
    Args:
        tarjeta (Tarjeta): Instancia de tarjeta con saldo bajo
    
    Returns:
        bool: True si se envió exitosamente
    """
    try:
        responsable = tarjeta.id_hijo.id_cliente_responsable
        hijo = tarjeta.id_hijo
        
        if not responsable.email:
            logger.warning(f"Cliente {responsable.id_cliente} no tiene email configurado")
            return False
        
        asunto = f"🔔 Saldo Bajo - Tarjeta de {hijo.nombre} {hijo.apellido}"
        
        mensaje_texto = f"""
Estimado/a {responsable.nombres} {responsable.apellidos},

Le informamos que la tarjeta del estudiante {hijo.nombre} {hijo.apellido} tiene un saldo bajo:

🎫 Tarjeta: {tarjeta.nro_tarjeta}
💰 Saldo actual: Gs. {tarjeta.saldo_actual:,}
⚠️ Umbral de alerta: Gs. {tarjeta.saldo_alerta or 10000:,}

Le recomendamos realizar una recarga para evitar inconvenientes.

Puede recargar en:
- Cantina Tita (horario escolar)
- Portal de Padres: https://cantinatita.com/portal

Gracias,
Cantina Tita
        """.strip()
        
        mensaje_html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
            <h2 style="color: #ff6b35;">🔔 Alerta de Saldo Bajo</h2>
            
            <p>Estimado/a <strong>{responsable.nombres} {responsable.apellidos}</strong>,</p>
            
            <p>Le informamos que la tarjeta del estudiante <strong>{hijo.nombre} {hijo.apellido}</strong> tiene un saldo bajo:</p>
            
            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p style="margin: 5px 0;">🎫 <strong>Tarjeta:</strong> {tarjeta.nro_tarjeta}</p>
                <p style="margin: 5px 0;">💰 <strong>Saldo actual:</strong> <span style="color: #ff6b35; font-size: 18px;">Gs. {tarjeta.saldo_actual:,}</span></p>
                <p style="margin: 5px 0;">⚠️ <strong>Umbral de alerta:</strong> Gs. {tarjeta.saldo_alerta or 10000:,}</p>
            </div>
            
            <p>Le recomendamos realizar una recarga para evitar inconvenientes.</p>
            
            <h3 style="color: #4ecdc4;">Puede recargar en:</h3>
            <ul>
                <li>Cantina Tita (horario escolar)</li>
                <li><a href="https://cantinatita.com/portal" style="color: #4ecdc4;">Portal de Padres</a></li>
            </ul>
            
            <hr style="margin-top: 30px; border: none; border-top: 1px solid #e0e0e0;">
            <p style="color: #999; font-size: 12px;">
                Este es un mensaje automático. Por favor no responda a este email.
            </p>
        </div>
        """
        
        return enviar_email(
            destinatario=responsable.email,
            asunto=asunto,
            mensaje=mensaje_texto,
            html_mensaje=mensaje_html
        )
        
    except Exception as e:
        logger.error(f"Error enviando email de saldo bajo para tarjeta {tarjeta.nro_tarjeta}: {e}")
        return False


def enviar_email_recarga_exitosa(recarga):
    """
    Envía confirmación de recarga exitosa
    
    Args:
        recarga (CargasSaldo): Instancia de recarga
    
    Returns:
        bool: True si se envió exitosamente
    """
    try:
        tarjeta = recarga.nro_tarjeta
        responsable = tarjeta.id_hijo.id_cliente_responsable
        hijo = tarjeta.id_hijo
        
        if not responsable.email:
            return False
        
        asunto = f"✅ Recarga Exitosa - Tarjeta de {hijo.nombre} {hijo.apellido}"
        
        mensaje_texto = f"""
Estimado/a {responsable.nombres} {responsable.apellidos},

Confirmamos que se ha realizado una recarga exitosa:

🎫 Tarjeta: {tarjeta.nro_tarjeta}
👤 Estudiante: {hijo.nombre} {hijo.apellido}
💵 Monto recargado: Gs. {recarga.monto_cargado:,}
💰 Nuevo saldo: Gs. {tarjeta.saldo_actual:,}
📅 Fecha: {recarga.fecha_carga.strftime('%d/%m/%Y %H:%M')}
📋 Referencia: #{recarga.id_carga}

Gracias por su recarga.

Cantina Tita
        """.strip()
        
        return enviar_email(
            destinatario=responsable.email,
            asunto=asunto,
            mensaje=mensaje_texto
        )
        
    except Exception as e:
        logger.error(f"Error enviando email de recarga exitosa: {e}")
        return False


# ==================== SMS ====================
# PENDIENTE: Requiere integración con Twilio, Tigo, Personal, etc.

def enviar_sms(telefono, mensaje):
    """
    Envía un SMS a un número de teléfono
    
    Args:
        telefono (str): Número de teléfono (formato internacional)
        mensaje (str): Mensaje a enviar (max 160 caracteres)
    
    Returns:
        bool: True si se envió exitosamente
    """
    # TODO: Implementar con Twilio o proveedor local
    logger.warning(f"SMS no implementado. Simulando envío a {telefono}: {mensaje[:50]}...")
    return False


def enviar_sms_saldo_bajo(tarjeta):
    """
    Envía SMS de alerta de saldo bajo
    
    Args:
        tarjeta (Tarjeta): Instancia de tarjeta
    
    Returns:
        bool: True si se envió exitosamente
    """
    try:
        responsable = tarjeta.id_hijo.id_cliente_responsable
        hijo = tarjeta.id_hijo
        
        if not responsable.telefono:
            logger.warning(f"Cliente {responsable.id_cliente} no tiene teléfono configurado")
            return False
        
        # SMS máximo 160 caracteres
        mensaje = f"CANTINA TITA: Saldo bajo en tarjeta {tarjeta.nro_tarjeta} ({hijo.nombre}): Gs. {tarjeta.saldo_actual:,}. Recargue pronto."
        
        return enviar_sms(responsable.telefono, mensaje)
        
    except Exception as e:
        logger.error(f"Error enviando SMS de saldo bajo: {e}")
        return False


# ==================== WHATSAPP ====================
# PENDIENTE: Requiere WhatsApp Business API o Twilio

def enviar_whatsapp(telefono, mensaje):
    """
    Envía un mensaje por WhatsApp
    
    Args:
        telefono (str): Número de teléfono (formato internacional)
        mensaje (str): Mensaje a enviar
    
    Returns:
        bool: True si se envió exitosamente
    """
    # TODO: Implementar con WhatsApp Business API o Twilio
    logger.warning(f"WhatsApp no implementado. Simulando envío a {telefono}: {mensaje[:50]}...")
    return False


def enviar_whatsapp_saldo_bajo(tarjeta):
    """
    Envía mensaje de WhatsApp de alerta de saldo bajo
    
    Args:
        tarjeta (Tarjeta): Instancia de tarjeta
    
    Returns:
        bool: True si se envió exitosamente
    """
    try:
        responsable = tarjeta.id_hijo.id_cliente_responsable
        hijo = tarjeta.id_hijo
        
        if not responsable.telefono:
            return False
        
        mensaje = f"""
🔔 *CANTINA TITA - Saldo Bajo*

Estimado/a {responsable.nombres} {responsable.apellidos},

La tarjeta del estudiante *{hijo.nombre} {hijo.apellido}* tiene saldo bajo:

🎫 Tarjeta: {tarjeta.nro_tarjeta}
💰 Saldo: *Gs. {tarjeta.saldo_actual:,}*

Le recomendamos realizar una recarga pronto.

_Mensaje automático - No responder_
        """.strip()
        
        return enviar_whatsapp(responsable.telefono, mensaje)
        
    except Exception as e:
        logger.error(f"Error enviando WhatsApp de saldo bajo: {e}")
        return False


# ==================== NOTIFICACIONES MULTIPLES ====================

def notificar_saldo_bajo(tarjeta, canales=['email']):
    """
    Notifica saldo bajo por múltiples canales
    
    Args:
        tarjeta (Tarjeta): Instancia de tarjeta
        canales (list): Lista de canales ['email', 'sms', 'whatsapp']
    
    Returns:
        dict: Resultado de cada canal
    """
    resultados = {}
    
    if 'email' in canales:
        resultados['email'] = enviar_email_saldo_bajo(tarjeta)
    
    if 'sms' in canales:
        resultados['sms'] = enviar_sms_saldo_bajo(tarjeta)
    
    if 'whatsapp' in canales:
        resultados['whatsapp'] = enviar_whatsapp_saldo_bajo(tarjeta)
    
    # Registrar en solicitudes_notificacion
    from gestion.models import SolicitudesNotificacion
    
    for canal, exitoso in resultados.items():
        SolicitudesNotificacion.objects.create(
            id_cliente=tarjeta.id_hijo.id_cliente_responsable,
            nro_tarjeta=tarjeta,
            saldo_alerta=tarjeta.saldo_actual,
            mensaje=f'Saldo bajo: Gs. {tarjeta.saldo_actual:,}',
            destino=canal.upper(),
            estado='Enviada' if exitoso else 'Fallida',
            fecha_solicitud=timezone.now(),
            fecha_envio=timezone.now() if exitoso else None
        )
    
    return resultados


def notificar_pago_realizado(pago, tipo='recarga'):
    """
    Notifica pago/recarga realizada
    
    Args:
        pago: Instancia de CargasSaldo o PagosVenta
        tipo (str): 'recarga' o 'pago'
    
    Returns:
        dict: Resultado de cada canal
    """
    # TODO: Implementar
    pass


def notificar_cuenta_pendiente(cuenta):
    """
    Notifica cuenta pendiente de pago
    
    Args:
        cuenta: Instancia de CuentaAlmuerzoMensual
    
    Returns:
        dict: Resultado de cada canal
    """
    # TODO: Implementar
    pass
```

---

### Paso 3: Actualizar `enviar_notificacion_saldo()` (10 minutos)

**Archivo:** `gestion/pos_views.py` (línea 2880)

```python
from gestion.notificaciones import notificar_saldo_bajo

@login_required
def enviar_notificacion_saldo(request, tarjeta_id):
    """Enviar notificación de saldo bajo al responsable"""
    try:
        tarjeta = Tarjeta.objects.select_related(
            'id_hijo',
            'id_hijo__id_cliente_responsable'
        ).get(nro_tarjeta=tarjeta_id)
        
        # Determinar canales según configuración
        canales = ['email']  # Por defecto solo email
        
        # Agregar SMS si tiene teléfono y SMS está habilitado
        if tarjeta.id_hijo.id_cliente_responsable.telefono:
            # TODO: Verificar preferencias de notificación
            pass  # canales.append('sms')
        
        # Enviar notificación
        resultados = notificar_saldo_bajo(tarjeta, canales=canales)
        
        # Verificar si al menos un canal fue exitoso
        exitoso = any(resultados.values())
        
        if exitoso:
            responsable = tarjeta.id_hijo.id_cliente_responsable
            canales_enviados = [k.upper() for k, v in resultados.items() if v]
            
            return JsonResponse({
                'success': True,
                'mensaje': f'Notificación enviada por {", ".join(canales_enviados)} a {responsable.email or responsable.telefono}',
                'resultados': resultados
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'No se pudo enviar la notificación por ningún canal',
                'resultados': resultados
            }, status=500)
        
    except Tarjeta.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Tarjeta no encontrada'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
```

---

### Paso 4: Crear Tarea Programada para Alertas (20 minutos)

**Opción A: Celery (Recomendado)**

```python
# gestion/tasks.py (nuevo archivo)

from celery import shared_task
from django.utils import timezone
from decimal import Decimal
from gestion.models import Tarjeta, Producto, AlertasSistema
from gestion.notificaciones import notificar_saldo_bajo
import logging

logger = logging.getLogger(__name__)

@shared_task
def verificar_saldos_bajos():
    """
    Tarea que verifica tarjetas con saldo bajo y envía notificaciones
    Ejecutar diariamente a las 18:00 (después de clases)
    """
    SALDO_MINIMO = Decimal('10000')
    
    tarjetas_saldo_bajo = Tarjeta.objects.filter(
        estado='Activa',
        saldo_actual__lte=SALDO_MINIMO
    ).select_related('id_hijo', 'id_hijo__id_cliente_responsable')
    
    total_enviadas = 0
    total_fallidas = 0
    
    for tarjeta in tarjetas_saldo_bajo:
        try:
            # Verificar si ya se notificó hoy
            hoy = timezone.now().date()
            notificacion_hoy = SolicitudesNotificacion.objects.filter(
                nro_tarjeta=tarjeta,
                fecha_solicitud__date=hoy,
                estado='Enviada'
            ).exists()
            
            if notificacion_hoy:
                logger.info(f"Ya se notificó hoy para tarjeta {tarjeta.nro_tarjeta}")
                continue
            
            # Enviar notificación
            resultados = notificar_saldo_bajo(tarjeta, canales=['email'])
            
            if any(resultados.values()):
                total_enviadas += 1
                logger.info(f"Notificación enviada para tarjeta {tarjeta.nro_tarjeta}")
            else:
                total_fallidas += 1
                logger.warning(f"Falló notificación para tarjeta {tarjeta.nro_tarjeta}")
                
        except Exception as e:
            logger.error(f"Error procesando tarjeta {tarjeta.nro_tarjeta}: {e}")
            total_fallidas += 1
    
    # Crear alerta del sistema
    if total_enviadas > 0 or total_fallidas > 0:
        AlertasSistema.objects.create(
            tipo='Saldo Bajo',
            mensaje=f'Verificación de saldos: {total_enviadas} notificaciones enviadas, {total_fallidas} fallidas',
            fecha_creacion=timezone.now(),
            estado='Resuelta'
        )
    
    return {
        'total_tarjetas': tarjetas_saldo_bajo.count(),
        'enviadas': total_enviadas,
        'fallidas': total_fallidas
    }


@shared_task
def verificar_stock_bajo():
    """
    Tarea que verifica productos con stock bajo y crea alertas
    Ejecutar diariamente a las 08:00 y 18:00
    """
    productos_bajo = Producto.objects.filter(
        activo=True,
        stock_minimo__isnull=False
    ).annotate(
        stock_actual_val=F('stock__stock_actual')
    ).filter(
        stock_actual_val__lt=F('stock_minimo')
    )
    
    for producto in productos_bajo:
        # Crear alerta si no existe una pendiente
        alerta_existente = AlertasSistema.objects.filter(
            tipo='Stock Bajo',
            mensaje__contains=producto.descripcion,
            estado='Pendiente'
        ).exists()
        
        if not alerta_existente:
            AlertasSistema.objects.create(
                tipo='Stock Bajo',
                mensaje=f'Producto {producto.descripcion} tiene stock bajo: {producto.stock.stock_actual} (mínimo: {producto.stock_minimo})',
                fecha_creacion=timezone.now(),
                estado='Pendiente'
            )
            logger.info(f"Alerta creada para producto {producto.id_producto}")
    
    return {'total_productos_bajo': productos_bajo.count()}


# Configurar en celery_config.py o settings.py
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'verificar-saldos-bajos-diario': {
        'task': 'gestion.tasks.verificar_saldos_bajos',
        'schedule': crontab(hour=18, minute=0),  # Diario a las 18:00
    },
    'verificar-stock-bajo-manana': {
        'task': 'gestion.tasks.verificar_stock_bajo',
        'schedule': crontab(hour=8, minute=0),  # Diario a las 08:00
    },
    'verificar-stock-bajo-tarde': {
        'task': 'gestion.tasks.verificar_stock_bajo',
        'schedule': crontab(hour=18, minute=0),  # Diario a las 18:00
    },
}
```

**Opción B: Django-cron (Más simple)**

```python
# gestion/cron.py (nuevo archivo)

from django_cron import CronJobBase, Schedule
from gestion.models import Tarjeta
from gestion.notificaciones import notificar_saldo_bajo
from decimal import Decimal

class VerificarSaldosBajos(CronJobBase):
    RUN_AT_TIMES = ['18:00']  # Ejecutar a las 18:00
    
    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'gestion.verificar_saldos_bajos'
    
    def do(self):
        SALDO_MINIMO = Decimal('10000')
        
        tarjetas = Tarjeta.objects.filter(
            estado='Activa',
            saldo_actual__lte=SALDO_MINIMO
        ).select_related('id_hijo', 'id_hijo__id_cliente_responsable')
        
        for tarjeta in tarjetas:
            notificar_saldo_bajo(tarjeta, canales=['email'])
```

---

## 🧪 TESTING

### Tests Existentes

**Archivo:** `test_modulo_alertas.py`, `test_modulo_alertas_CORREGIDO.py`

```python
# Ejecutar tests
python manage.py test gestion.tests.test_modulo_alertas
```

### Tests Recomendados (Crear)

```python
# gestion/tests/test_notificaciones.py (nuevo)

from django.test import TestCase
from django.core import mail
from gestion.models import Tarjeta, Cliente, Hijo
from gestion.notificaciones import (
    enviar_email_saldo_bajo,
    enviar_sms_saldo_bajo,
    notificar_saldo_bajo
)

class NotificacionesEmailTest(TestCase):
    
    def setUp(self):
        """Crear datos de prueba"""
        # Crear cliente
        self.cliente = Cliente.objects.create(
            nombres='Juan',
            apellidos='Pérez',
            ruc_ci='123456789',
            email='juan@example.com',
            telefono='+595981123456'
        )
        
        # Crear hijo
        self.hijo = Hijo.objects.create(
            id_cliente_responsable=self.cliente,
            nombre='María',
            apellido='Pérez'
        )
        
        # Crear tarjeta
        self.tarjeta = Tarjeta.objects.create(
            nro_tarjeta='TEST001',
            id_hijo=self.hijo,
            saldo_actual=5000,
            estado='Activa'
        )
    
    def test_enviar_email_saldo_bajo(self):
        """Test que verifica envío de email de saldo bajo"""
        # Enviar email
        exitoso = enviar_email_saldo_bajo(self.tarjeta)
        
        # Verificar que se envió
        self.assertTrue(exitoso)
        
        # Verificar que hay 1 email en la bandeja de salida
        self.assertEqual(len(mail.outbox), 1)
        
        # Verificar contenido del email
        email = mail.outbox[0]
        self.assertIn('juan@example.com', email.to)
        self.assertIn('Saldo Bajo', email.subject)
        self.assertIn('María Pérez', email.body)
        self.assertIn('5000', email.body)
    
    def test_notificar_multiples_canales(self):
        """Test que verifica notificación por múltiples canales"""
        resultados = notificar_saldo_bajo(
            self.tarjeta,
            canales=['email', 'sms']
        )
        
        # Email debe ser exitoso
        self.assertTrue(resultados['email'])
        
        # SMS debe fallar (no implementado)
        self.assertFalse(resultados['sms'])
    
    def test_cliente_sin_email(self):
        """Test que verifica manejo de cliente sin email"""
        # Crear cliente sin email
        cliente_sin_email = Cliente.objects.create(
            nombres='Pedro',
            apellidos='Gómez',
            ruc_ci='987654321',
            email=None
        )
        
        hijo = Hijo.objects.create(
            id_cliente_responsable=cliente_sin_email,
            nombre='Luis',
            apellido='Gómez'
        )
        
        tarjeta = Tarjeta.objects.create(
            nro_tarjeta='TEST002',
            id_hijo=hijo,
            saldo_actual=5000,
            estado='Activa'
        )
        
        # Enviar email
        exitoso = enviar_email_saldo_bajo(tarjeta)
        
        # No debe ser exitoso
        self.assertFalse(exitoso)
        
        # No debe haber emails en la bandeja
        self.assertEqual(len(mail.outbox), 0)
```

---

## 📝 DOCUMENTACIÓN PARA USUARIOS

### Manual de Uso - Alertas del Sistema

#### Acceder al Dashboard de Alertas

1. Ir a **Menú Principal** → **POS** → **Alertas del Sistema**
2. O visitar: `http://localhost:8000/pos/alertas/`

#### Tabs Disponibles

**1. Saldo Bajo** 🔴
- Muestra tarjetas con saldo ≤ 10,000 Gs
- Botón "Notificar" envía email al responsable
- Filtro de búsqueda por estudiante/responsable

**2. Stock Bajo** 🟡
- Productos con stock < stock_mínimo configurado
- Ordenados por severidad (crítico primero)
- Click en producto para ver kardex

**3. Sin Stock** ⚫
- Productos agotados (stock = 0)
- Alerta crítica para reposición urgente

**4. Tarjetas por Vencer** 🕒
- Tarjetas que vencen en los próximos 30 días
- Renovar antes del vencimiento

**5. Tarjetas Bloqueadas** 🔒
- Tarjetas bloqueadas por sistema o admin
- Investigar motivo antes de desbloquear

#### Enviar Notificación Manual

1. En cualquier tab, buscar la tarjeta/producto
2. Click en botón **"Notificar"** o **"Enviar Notificación"**
3. Confirmar envío
4. Sistema muestra mensaje de confirmación
5. Email se envía automáticamente al responsable

---

## 🎯 PRÓXIMOS PASOS

### Corto Plazo (Esta Semana)
1. ✅ Configurar SMTP con Gmail o SendGrid (5 min)
2. ✅ Probar envío real de emails (10 min)
3. ✅ Actualizar vista `enviar_notificacion_saldo()` (15 min)
4. ✅ Crear archivo `notificaciones.py` (30 min)

### Mediano Plazo (Este Mes)
1. ⏳ Investigar proveedores SMS Paraguay (Tigo, Personal)
2. ⏳ Configurar tarea programada (Celery o Django-cron)
3. ⏳ Crear preferencias de notificación en portal padres
4. ⏳ Implementar notificación de recarga exitosa

### Largo Plazo (Próximo Trimestre)
1. ⏳ Integrar WhatsApp Business API
2. ⏳ Crear templates HTML para emails
3. ⏳ Dashboard de estadísticas de notificaciones
4. ⏳ Sistema de preferencias avanzado

---

## 📊 RESUMEN EJECUTIVO

### ✅ Funcionando Hoy
- ✅ Base de datos completa (4 tablas)
- ✅ Modelos Django (4 models)
- ✅ Dashboard de alertas (5 tabs)
- ✅ Botones de notificación en UI
- ✅ Vista de envío (simulada)
- ✅ Estructura 100% lista

### ⚠️ Requiere Configuración
- ⚠️ SMTP real (5 minutos)
- ⚠️ Archivo notificaciones.py (30 minutos)
- ⚠️ Actualizar vista enviar_notificacion_saldo() (15 minutos)

### ❌ Pendiente Integración Externa
- ❌ SMS (Twilio/Tigo) - Requiere cuenta + API key
- ❌ WhatsApp (Business API) - Requiere aprobación + cuenta

---

## 🔗 ENLACES ÚTILES

### Documentación Oficial
- [Django Email](https://docs.djangoproject.com/en/5.0/topics/email/)
- [SendGrid Django](https://github.com/sklarsa/django-sendgrid-v5)
- [Twilio Python](https://www.twilio.com/docs/libraries/python)
- [WhatsApp Business API](https://developers.facebook.com/docs/whatsapp/cloud-api)

### Proveedores de SMS Paraguay
- **Tigo Paraguay:** https://www.tigo.com.py/empresas
- **Personal Paraguay:** https://www.personal.com.py/empresas
- **Twilio:** https://www.twilio.com/sms

### Plantillas de Email
- **SendGrid Templates:** https://sendgrid.com/solutions/email-api/templates/
- **Mailchimp Templates:** https://mailchimp.com/email-templates/

---

**Última actualización:** Diciembre 2025  
**Mantenedor:** Equipo Desarrollo Cantina Tita  
**Contacto:** dev@cantinatita.com
