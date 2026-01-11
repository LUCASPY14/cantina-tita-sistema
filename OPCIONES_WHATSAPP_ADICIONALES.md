# 📱 OPCIONES WHATSAPP PARA CANTINA TITA
## Análisis Completo de Proveedores para Notificaciones

---

## 🎯 OPCIONES YA ANALIZADAS (Resumen)

| Proveedor | Costo/msg | Oficial | Recomendación |
|-----------|-----------|---------|---------------|
| **Gupshup** | $0.003 | ✅ | ⭐⭐⭐⭐⭐ MEJOR PRECIO |
| **360Dialog** | $0.004 | ✅ | ⭐⭐⭐⭐ Bueno |
| **Twilio** | $0.005 | ✅ | ⭐⭐⭐ Conocido |
| **Meta Business** | $0.006 | ✅ | ⭐⭐⭐⭐ Premium |
| **Baileys** | $0 | ❌ | ⭐⭐ Solo testing |

---

## 🆕 OPCIONES ADICIONALES PARA CONSIDERAR

### **1. Vonage (ex-Nexmo)** 💼

**Empresa:** Vonage Holdings (USA)  
**API WhatsApp:** Oficial Meta Partner  
**Costo:** $0.0042 - $0.008/mensaje (según país)

#### **Características:**
- ✅ API REST sencilla
- ✅ Partner oficial de Meta
- ✅ Buena documentación
- ✅ SDK Python disponible
- ✅ Dashboard completo
- ⚠️ Caro en Paraguay ($0.007/msg)
- ⚠️ Requiere verificación business

#### **Código Python:**
```python
# pip install vonage

import vonage
from django.conf import settings

def enviar_whatsapp_vonage(telefono, mensaje):
    """
    Enviar WhatsApp vía Vonage API
    
    Costo: $0.007/mensaje (Paraguay)
    Setup: 3-5 días aprobación
    """
    try:
        client = vonage.Client(
            key=settings.VONAGE_API_KEY,
            secret=settings.VONAGE_API_SECRET
        )
        
        # Formatear número
        if not telefono.startswith('+'):
            telefono = '+' + telefono.replace(' ', '').replace('-', '')
        
        # Enviar mensaje
        response = client.messages.send_message({
            "from": settings.VONAGE_WHATSAPP_NUMBER,
            "to": telefono,
            "channel": "whatsapp",
            "message_type": "text",
            "text": mensaje
        })
        
        if response["messages"][0]["status"] == "accepted":
            logger.info(f"WhatsApp Vonage enviado a {telefono}")
            return True
        return False
        
    except Exception as e:
        logger.error(f"Error Vonage WhatsApp: {str(e)}")
        return False


def enviar_whatsapp_vonage_template(telefono, template_name, parameters):
    """
    Enviar template pre-aprobado
    """
    try:
        client = vonage.Client(
            key=settings.VONAGE_API_KEY,
            secret=settings.VONAGE_API_SECRET
        )
        
        response = client.messages.send_message({
            "from": settings.VONAGE_WHATSAPP_NUMBER,
            "to": telefono,
            "channel": "whatsapp",
            "message_type": "custom",
            "custom": {
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {"code": "es"},
                    "components": parameters
                }
            }
        })
        
        return response["messages"][0]["status"] == "accepted"
        
    except Exception as e:
        logger.error(f"Error template Vonage: {str(e)}")
        return False
```

#### **Configuración .env:**
```ini
# Vonage WhatsApp
WHATSAPP_PROVIDER=vonage
VONAGE_API_KEY=tu_api_key
VONAGE_API_SECRET=tu_api_secret
VONAGE_WHATSAPP_NUMBER=595981234567

# Costo: $0.007/mensaje (Paraguay)
# Setup: 3-5 días
```

#### **Ventajas:**
- ✅ API sencilla y bien documentada
- ✅ SDK Python oficial
- ✅ Soporte multi-canal (SMS, voz, video)
- ✅ Dashboard analytics completo

#### **Desventajas:**
- ❌ Más caro que Gupshup ($0.007 vs $0.003)
- ❌ Requiere verificación business
- ❌ No tan enfocado en LATAM

---

### **2. MessageBird** 🐦

**Empresa:** MessageBird (Holanda)  
**API WhatsApp:** Oficial Meta Partner  
**Costo:** $0.0045 - $0.01/mensaje

#### **Características:**
- ✅ Multi-canal (SMS, WhatsApp, Voice)
- ✅ API REST moderna
- ✅ Python SDK disponible
- ✅ Buena documentación
- ⚠️ Precio medio-alto
- ⚠️ Enfocado en Europa

#### **Código Python:**
```python
# pip install messagebird

import messagebird
from django.conf import settings

def enviar_whatsapp_messagebird(telefono, mensaje):
    """
    Enviar WhatsApp vía MessageBird
    
    Costo: $0.0045/mensaje
    Setup: 2-4 días
    """
    try:
        client = messagebird.Client(settings.MESSAGEBIRD_API_KEY)
        
        # Formatear número
        if not telefono.startswith('+'):
            telefono = '+' + telefono.replace(' ', '').replace('-', '')
        
        # Enviar mensaje
        message = client.conversation_send(
            channel_id=settings.MESSAGEBIRD_CHANNEL_ID,
            to=telefono,
            type='text',
            content={'text': mensaje}
        )
        
        logger.info(f"WhatsApp MessageBird enviado: {message.id}")
        return True
        
    except messagebird.client.ErrorException as e:
        logger.error(f"Error MessageBird: {e}")
        return False
```

#### **Ventajas:**
- ✅ API moderna y limpia
- ✅ Multi-canal integrado
- ✅ Buen soporte

#### **Desventajas:**
- ❌ Precio medio ($0.0045 vs $0.003 Gupshup)
- ❌ Menos presencia en LATAM

---

### **3. Infobip** 🌐

**Empresa:** Infobip (Croacia)  
**API WhatsApp:** Oficial Meta Partner  
**Costo:** $0.005 - $0.015/mensaje (según volumen)

#### **Características:**
- ✅ Partner oficial Meta
- ✅ Presencia en LATAM
- ✅ API completa
- ✅ Soporte en español
- ⚠️ Precio según volumen
- ⚠️ Mínimo mensual a veces requerido

#### **Código Python:**
```python
import requests
import json
from django.conf import settings

def enviar_whatsapp_infobip(telefono, mensaje):
    """
    Enviar WhatsApp vía Infobip
    
    Costo: $0.005 - $0.015/mensaje (según volumen)
    Setup: 3-7 días
    """
    try:
        url = f"{settings.INFOBIP_BASE_URL}/whatsapp/1/message/text"
        headers = {
            "Authorization": f"App {settings.INFOBIP_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "from": settings.INFOBIP_SENDER,
            "to": telefono.replace('+', ''),
            "messageId": f"cantita-{int(time.time())}",
            "content": {
                "text": mensaje
            },
            "callbackData": "Notificacion CantiTita"
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"WhatsApp Infobip enviado: {data}")
            return True
        return False
        
    except Exception as e:
        logger.error(f"Error Infobip: {str(e)}")
        return False
```

#### **Ventajas:**
- ✅ Buena presencia LATAM
- ✅ Soporte en español
- ✅ API robusta

#### **Desventajas:**
- ❌ Precio según volumen (puede ser caro)
- ❌ A veces requiere mínimo mensual

---

### **4. Ultramsg** 💰

**Empresa:** Ultramsg (UAE)  
**Tipo:** Servicio no oficial  
**Costo:** $0.001 - $0.002/mensaje

#### **Características:**
- ⚠️ **NO OFICIAL** (usa WhatsApp Web)
- ✅ MUY BARATO ($0.001/msg)
- ✅ API REST simple
- ✅ No requiere aprobación Meta
- ✅ Setup instantáneo (escanear QR)
- ❌ Riesgo de ban
- ❌ Menos confiable

#### **Código Python:**
```python
import requests
from django.conf import settings

def enviar_whatsapp_ultramsg(telefono, mensaje):
    """
    Enviar WhatsApp vía Ultramsg
    
    ⚠️ NO OFICIAL - Riesgo de ban
    Costo: $0.001/mensaje (ultra barato)
    Setup: Instantáneo (escanear QR)
    """
    try:
        # Normalizar teléfono (sin +)
        telefono_limpio = telefono.replace('+', '').replace(' ', '').replace('-', '')
        
        url = f"https://api.ultramsg.com/{settings.ULTRAMSG_INSTANCE_ID}/messages/chat"
        params = {
            "token": settings.ULTRAMSG_TOKEN,
            "to": telefono_limpio,
            "body": mensaje,
            "priority": "10"  # 1-10, mayor = más rápido
        }
        
        response = requests.post(url, data=params)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("sent") == "true":
                logger.info(f"WhatsApp Ultramsg enviado a {telefono}")
                return True
        return False
        
    except Exception as e:
        logger.error(f"Error Ultramsg: {str(e)}")
        return False


def enviar_whatsapp_ultramsg_imagen(telefono, mensaje, imagen_url):
    """
    Enviar imagen con caption
    """
    try:
        telefono_limpio = telefono.replace('+', '').replace(' ', '').replace('-', '')
        
        url = f"https://api.ultramsg.com/{settings.ULTRAMSG_INSTANCE_ID}/messages/image"
        params = {
            "token": settings.ULTRAMSG_TOKEN,
            "to": telefono_limpio,
            "image": imagen_url,
            "caption": mensaje
        }
        
        response = requests.post(url, data=params)
        return response.status_code == 200
        
    except Exception as e:
        logger.error(f"Error Ultramsg imagen: {str(e)}")
        return False
```

#### **Planes de Ultramsg:**
```
Plan Básico:    $0.002/mensaje + $5/mes
Plan Standard:  $0.0015/mensaje + $15/mes
Plan Premium:   $0.001/mensaje + $30/mes

Para 200 msg/día (6,000/mes):
- Básico:    $17/mes ($5 + $12)
- Standard:  $24/mes ($15 + $9)
- Premium:   $36/mes ($30 + $6)
```

#### **Ventajas:**
- ✅ **ULTRA BARATO** ($0.001/msg)
- ✅ Setup instantáneo (solo escanear QR)
- ✅ API REST simple
- ✅ Soporta multimedia (imágenes, PDFs)
- ✅ No requiere verificación business

#### **Desventajas:**
- ❌ **NO OFICIAL** (usa WhatsApp Web)
- ❌ **Riesgo de ban** del número
- ❌ Menos estable que APIs oficiales
- ❌ Requiere mantener sesión activa

#### **Caso de uso:**
- 🟢 Testing/desarrollo
- 🟢 Proyectos pequeños (< 100 msg/día)
- 🔴 NO recomendado para número principal
- 🟡 Considerar para número secundario

---

### **5. Maytapi** 🔧

**Empresa:** Maytapi (Turquía)  
**Tipo:** WhatsApp Cloud API + Web API  
**Costo:** $0.001 - $0.003/mensaje

#### **Características:**
- ⚠️ Ofrece API oficial Y no oficial
- ✅ Muy barato en modo no oficial
- ✅ API REST moderna
- ✅ Webhook support
- ❌ Modo no oficial = riesgo ban

#### **Código Python:**
```python
import requests
from django.conf import settings

def enviar_whatsapp_maytapi(telefono, mensaje):
    """
    Enviar WhatsApp vía Maytapi
    
    Costo: 
    - Modo oficial: $0.003/mensaje
    - Modo no oficial: $0.001/mensaje (riesgo ban)
    """
    try:
        url = f"https://api.maytapi.com/api/{settings.MAYTAPI_PRODUCT_ID}/{settings.MAYTAPI_PHONE_ID}/sendMessage"
        headers = {
            "x-maytapi-key": settings.MAYTAPI_API_KEY,
            "Content-Type": "application/json"
        }
        
        payload = {
            "to_number": telefono,
            "type": "text",
            "message": mensaje
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"WhatsApp Maytapi enviado: {data}")
            return True
        return False
        
    except Exception as e:
        logger.error(f"Error Maytapi: {str(e)}")
        return False
```

#### **Planes:**
```
WhatsApp Web API (No oficial):
- Free:     1000 msg/mes GRATIS (⚠️ riesgo ban)
- Starter:  $10/mes = 10,000 msgs
- Pro:      $25/mes = 50,000 msgs

WhatsApp Cloud API (Oficial):
- $0.003/mensaje + $15/mes
```

---

### **6. WA.me Links** 🔗

**Tipo:** Links directos (sin API)  
**Costo:** $0 (GRATIS)

#### **Concepto:**
No es un servicio API, sino usar links `wa.me` para que el cliente inicie conversación.

#### **Código Python:**
```python
from django.conf import settings
from django.core.mail import send_mail

def generar_link_whatsapp(telefono, mensaje_predefinido=""):
    """
    Generar link wa.me para click-to-chat
    
    Costo: $0 GRATIS
    Limitación: Cliente debe hacer click
    """
    # Limpiar teléfono
    telefono_limpio = telefono.replace('+', '').replace(' ', '').replace('-', '')
    
    # Generar link
    if mensaje_predefinido:
        from urllib.parse import quote
        mensaje_encoded = quote(mensaje_predefinido)
        link = f"https://wa.me/{telefono_limpio}?text={mensaje_encoded}"
    else:
        link = f"https://wa.me/{telefono_limpio}"
    
    return link


def enviar_email_con_link_whatsapp(cliente):
    """
    Enviar email con link para que cliente contacte por WhatsApp
    
    Combinación: Email (gratis) + WhatsApp link (gratis)
    """
    try:
        if not cliente.responsable.email:
            return False
        
        mensaje_wa = f"Hola, soy {cliente.responsable.nombre} de CantiTita"
        link_whatsapp = generar_link_whatsapp(
            settings.CANTITA_WHATSAPP,
            mensaje_wa
        )
        
        html_message = f"""
        <html>
        <body>
            <h2>Cuenta pendiente - {cliente.nombre}</h2>
            <p>Estimado/a {cliente.responsable.nombre},</p>
            <p>Su cuenta tiene un saldo pendiente de <strong>Gs. {cliente.saldo_pendiente:,}</strong></p>
            
            <p>Para consultas, puede contactarnos:</p>
            
            <a href="{link_whatsapp}" 
               style="background-color: #25D366; color: white; padding: 15px 30px; 
                      text-decoration: none; border-radius: 5px; display: inline-block;">
                💬 Contactar por WhatsApp
            </a>
            
            <p>O responder este email.</p>
        </body>
        </html>
        """
        
        send_mail(
            subject='Cuenta Pendiente - CantiTita',
            message='Ver email en HTML',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[cliente.responsable.email],
            html_message=html_message
        )
        
        logger.info(f"Email con link WhatsApp enviado a {cliente.responsable.email}")
        return True
        
    except Exception as e:
        logger.error(f"Error enviando email con link: {str(e)}")
        return False
```

#### **Ventajas:**
- ✅ **GRATIS** (sin costo alguno)
- ✅ No requiere API ni cuenta
- ✅ No riesgo de ban
- ✅ Funciona siempre

#### **Desventajas:**
- ❌ Cliente debe hacer click
- ❌ No es automatizado
- ❌ No envía mensaje directo

#### **Caso de uso:**
- 🟢 Complementar emails con opción WhatsApp
- 🟢 Links en facturas PDF
- 🟢 Firma de emails
- 🟢 Botones en sitio web

---

### **7. WATI (WhatsApp Team Inbox)** 👥

**Empresa:** WATI (India/Singapore)  
**Tipo:** Plataforma + API oficial  
**Costo:** $49/mes + $0.005/mensaje

#### **Características:**
- ✅ API oficial Meta
- ✅ Dashboard team inbox
- ✅ Multi-usuario
- ✅ Templates manager
- ⚠️ Costo fijo mensual alto
- ⚠️ Más caro que Gupshup

#### **Código Python:**
```python
import requests
from django.conf import settings

def enviar_whatsapp_wati(telefono, template_name, parameters):
    """
    Enviar WhatsApp vía WATI
    
    Costo: $49/mes + $0.005/mensaje
    Setup: 2-3 días
    """
    try:
        url = "https://live-server-<region>.wati.io/api/v1/sendTemplateMessage"
        headers = {
            "Authorization": f"Bearer {settings.WATI_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "whatsappNumber": telefono.replace('+', ''),
            "template_name": template_name,
            "broadcast_name": "CantiTita Notificaciones",
            "parameters": parameters
        }
        
        response = requests.post(url, headers=headers, json=payload)
        return response.status_code == 200
        
    except Exception as e:
        logger.error(f"Error WATI: {str(e)}")
        return False
```

#### **Planes:**
```
Starter:  $49/mes  + $0.005/msg = ~$79/mes (200 msg/día)
Pro:      $99/mes  + $0.005/msg
Business: $299/mes + $0.004/msg
```

#### **Ventajas:**
- ✅ Dashboard team inbox muy bueno
- ✅ Multi-agente
- ✅ Chatbot builder incluido

#### **Desventajas:**
- ❌ Costo fijo alto ($49/mes)
- ❌ Más caro total que Gupshup
- ❌ Sobrecalificado para solo notificaciones

---

### **8. Chat-API.com** 🔓

**Tipo:** Servicio no oficial  
**Costo:** $0.0015/mensaje + $39/mes

#### **Características:**
- ⚠️ NO OFICIAL (WhatsApp Web)
- ✅ API REST completa
- ✅ Webhook support
- ✅ Barato
- ❌ Riesgo de ban

#### **Código Python:**
```python
import requests
from django.conf import settings

def enviar_whatsapp_chatapi(telefono, mensaje):
    """
    Enviar WhatsApp vía Chat-API
    
    ⚠️ NO OFICIAL - Riesgo de ban
    Costo: $0.0015/mensaje + $39/mes
    """
    try:
        url = f"https://api.chat-api.com/instance{settings.CHATAPI_INSTANCE}/sendMessage"
        params = {
            "token": settings.CHATAPI_TOKEN
        }
        payload = {
            "phone": telefono.replace('+', '').replace(' ', ''),
            "body": mensaje
        }
        
        response = requests.post(url, params=params, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("sent"):
                logger.info(f"WhatsApp Chat-API enviado a {telefono}")
                return True
        return False
        
    except Exception as e:
        logger.error(f"Error Chat-API: {str(e)}")
        return False
```

---

## 📊 TABLA COMPARATIVA COMPLETA

### **Proveedores OFICIALES (Sin riesgo ban):**

| Proveedor | Costo/msg | Setup Fijo | Total 200msg/día | Región | Recomendación |
|-----------|-----------|------------|------------------|--------|---------------|
| **Gupshup** | $0.003 | $0 | **$18/mes** | 🌎 Global | ⭐⭐⭐⭐⭐ |
| **360Dialog** | $0.004 | $0 | $24/mes | 🌍 Europa | ⭐⭐⭐⭐ |
| **MessageBird** | $0.0045 | $0 | $27/mes | 🌍 Europa | ⭐⭐⭐ |
| **Twilio** | $0.005 | $0 | $30/mes | 🌎 USA | ⭐⭐⭐ |
| **Infobip** | $0.005 | $0 | $30/mes | 🌎 LATAM | ⭐⭐⭐ |
| **Meta API** | $0.006 | $0 | $36/mes | 🌎 Global | ⭐⭐⭐⭐ |
| **Vonage** | $0.007 | $0 | $42/mes | 🌎 USA | ⭐⭐ |
| **WATI** | $0.005 | **$49/mes** | $79/mes | 🌏 Asia | ⭐⭐ |

### **Proveedores NO OFICIALES (⚠️ Riesgo ban):**

| Proveedor | Costo/msg | Setup Fijo | Total 200msg/día | Riesgo | Recomendación |
|-----------|-----------|------------|------------------|--------|---------------|
| **Ultramsg Premium** | $0.001 | $30/mes | $36/mes | ⚠️ Alto | 🔶 Testing |
| **Maytapi Free** | $0 | $0 | **$0/mes** | ⚠️⚠️ Muy Alto | 🔴 Solo dev |
| **Chat-API** | $0.0015 | $39/mes | $48/mes | ⚠️ Alto | 🔶 Testing |
| **Baileys** | $0 | $10/mes | $10/mes | ⚠️⚠️ Muy Alto | 🔴 Solo dev |

### **Opción SIN COSTO:**

| Método | Costo | Automatización | Caso de uso |
|--------|-------|----------------|-------------|
| **WA.me Links** | $0 | ❌ Manual | ✅ Email buttons |

---

## 💰 ANÁLISIS DE COSTOS (6,000 mensajes/mes)

### **Scenario 1: PRODUCCIÓN - Opción MÁS BARATA OFICIAL**

```
Gupshup: $0.003 × 6,000 = $18/mes = $216/año
✅ RECOMENDADO para producción
✅ Oficial (sin riesgo)
✅ Confiable
```

### **Scenario 2: PRODUCCIÓN - Opción PREMIUM**

```
Meta Business API: $0.006 × 6,000 = $36/mes = $432/año
✅ Más confiable
✅ Mejor soporte
❌ 2x más caro que Gupshup
```

### **Scenario 3: TESTING - Opción MÁS BARATA**

```
Maytapi Free: $0 × 1,000 = $0/mes
⚠️ NO OFICIAL
⚠️ Solo para desarrollo
⚠️ Usar número de prueba
```

### **Scenario 4: HÍBRIDO - Email + WhatsApp Link**

```
Email (Gmail SMTP): $0/mes
WA.me Links: $0/mes
Total: $0/mes

✅ Sin costo
✅ Sin riesgo ban
❌ No automatizado
✅ Bueno para complementar
```

---

## 🎯 RECOMENDACIÓN FINAL PARA CANTINA TITA

### **🥇 MEJOR OPCIÓN: Gupshup ($0.003/msg)**

**¿Por qué?**
1. ✅ **MÁS BARATO entre oficiales** ($18/mes vs $24-79 otros)
2. ✅ **Oficial** (Meta Partner - sin riesgo ban)
3. ✅ **API REST Python simple** (ya implementado)
4. ✅ **Sin costo fijo** mensual
5. ✅ **Buena documentación**
6. ✅ **Presencia global** (funciona en Paraguay)

**Código ya listo en:** `gestion/notificaciones.py`

---

### **🥈 ALTERNATIVA 1: Email + WA.me Links ($0)**

**Para presupuesto $0:**
```python
# Combinar email con botón WhatsApp
# Costo: $0
# Requiere: Click del usuario

def notificar_saldo_bajo_hibrido(tarjeta):
    # 1. Enviar email con link WhatsApp
    enviar_email_con_link_whatsapp(tarjeta.cliente)
    
    # 2. Usuario hace click y contacta
    # 3. Atención manual
```

**Ventajas:**
- ✅ $0 costo
- ✅ Sin riesgo ban
- ✅ Fácil implementar

**Desventajas:**
- ❌ No automatizado 100%
- ❌ Requiere acción del usuario

---

### **🥉 ALTERNATIVA 2: Ultramsg ($0.001/msg) + Número Secundario**

**Si quieres automatización barata:**
```python
# Usar Ultramsg SOLO con número secundario
# Costo: $36/mes (200 msg/día)
# Riesgo: Solo afecta número secundario

WHATSAPP_PRINCIPAL = "+595981234567"  # Solo manual
WHATSAPP_NOTIFICACIONES = "+595987654321"  # Ultramsg (riesgo ban)
```

**Estrategia:**
1. Número principal: Solo atención manual (sin riesgo)
2. Número secundario: Notificaciones automáticas (Ultramsg)
3. Si ban número secundario: Cambiar por otro

---

## 📋 CÓDIGO ACTUALIZADO PARA notificaciones.py

```python
# gestion/notificaciones.py

import requests
import json
from django.conf import settings
from django.core.mail import send_mail
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# WHATSAPP - GUPSHUP (RECOMENDADO - $0.003/msg)
# ============================================================================

def enviar_whatsapp_gupshup(telefono, mensaje, template_id=None, params=None):
    """
    Enviar WhatsApp vía Gupshup (MÁS BARATO OFICIAL)
    
    Costo: $0.003/mensaje
    Oficial: ✅ Meta Partner
    Setup: 2-3 días aprobación
    """
    try:
        url = "https://api.gupshup.io/sm/api/v1/msg"
        headers = {"apikey": settings.GUPSHUP_API_KEY}
        
        # Normalizar teléfono
        if not telefono.startswith('+'):
            telefono = '+' + telefono.replace(' ', '').replace('-', '')
        
        # Construir payload
        if template_id:
            # Template pre-aprobado
            message_payload = {
                "type": "template",
                "template": {
                    "id": template_id,
                    "params": params or []
                }
            }
        else:
            # Mensaje de texto simple
            message_payload = {
                "type": "text",
                "text": mensaje
            }
        
        payload = {
            "channel": "whatsapp",
            "source": settings.GUPSHUP_APP_NAME,
            "destination": telefono,
            "message": json.dumps(message_payload),
            "src.name": settings.GUPSHUP_APP_NAME
        }
        
        response = requests.post(url, headers=headers, data=payload)
        
        if response.status_code == 200 or response.status_code == 202:
            logger.info(f"✅ WhatsApp Gupshup enviado a {telefono}")
            return True
        else:
            logger.error(f"❌ Error Gupshup: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error Gupshup WhatsApp: {str(e)}")
        return False


# ============================================================================
# WHATSAPP - ULTRAMSG (ALTERNATIVA BARATA NO OFICIAL - $0.001/msg)
# ============================================================================

def enviar_whatsapp_ultramsg(telefono, mensaje):
    """
    Enviar WhatsApp vía Ultramsg (ULTRA BARATO pero NO OFICIAL)
    
    ⚠️ NO OFICIAL - Riesgo de ban
    Costo: $0.001/mensaje
    Setup: Instantáneo (escanear QR)
    
    RECOMENDACIÓN: Solo usar con número secundario para testing
    """
    try:
        # Normalizar teléfono (sin +)
        telefono_limpio = telefono.replace('+', '').replace(' ', '').replace('-', '')
        
        url = f"https://api.ultramsg.com/{settings.ULTRAMSG_INSTANCE_ID}/messages/chat"
        params = {
            "token": settings.ULTRAMSG_TOKEN,
            "to": telefono_limpio,
            "body": mensaje,
            "priority": "10"
        }
        
        response = requests.post(url, data=params)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("sent") == "true":
                logger.info(f"✅ WhatsApp Ultramsg enviado a {telefono}")
                return True
        
        logger.error(f"❌ Error Ultramsg: {response.status_code} - {response.text}")
        return False
        
    except Exception as e:
        logger.error(f"❌ Error Ultramsg: {str(e)}")
        return False


# ============================================================================
# WHATSAPP - WA.ME LINKS (GRATIS - $0)
# ============================================================================

def generar_link_whatsapp(telefono, mensaje_predefinido=""):
    """
    Generar link wa.me para click-to-chat
    
    Costo: $0 GRATIS
    Automatización: No (requiere click del usuario)
    
    Caso de uso: Incluir en emails, PDFs, sitio web
    """
    from urllib.parse import quote
    
    # Limpiar teléfono
    telefono_limpio = telefono.replace('+', '').replace(' ', '').replace('-', '')
    
    # Generar link
    if mensaje_predefinido:
        mensaje_encoded = quote(mensaje_predefinido)
        link = f"https://wa.me/{telefono_limpio}?text={mensaje_encoded}"
    else:
        link = f"https://wa.me/{telefono_limpio}"
    
    return link


def enviar_email_con_boton_whatsapp(destinatario, asunto, mensaje, telefono_whatsapp=None):
    """
    Enviar email con botón de contacto WhatsApp
    
    Costo: $0 (Email SMTP gratis + Link gratis)
    Automatización: Parcial (email automático, WhatsApp manual)
    
    Estrategia híbrida: Email + opción WhatsApp
    """
    try:
        if not telefono_whatsapp:
            telefono_whatsapp = settings.CANTITA_WHATSAPP_CONTACTO
        
        mensaje_wa_predefinido = "Hola CantiTita, necesito ayuda con mi cuenta"
        link_whatsapp = generar_link_whatsapp(telefono_whatsapp, mensaje_wa_predefinido)
        
        html_message = f"""
        <html>
        <head>
            <style>
                .whatsapp-button {{
                    background-color: #25D366;
                    color: white;
                    padding: 15px 30px;
                    text-decoration: none;
                    border-radius: 8px;
                    display: inline-block;
                    font-weight: bold;
                    margin-top: 20px;
                }}
                .whatsapp-button:hover {{
                    background-color: #128C7E;
                }}
            </style>
        </head>
        <body>
            <h2>{asunto}</h2>
            <p>{mensaje}</p>
            
            <p>¿Necesita ayuda? Contáctenos:</p>
            
            <a href="{link_whatsapp}" class="whatsapp-button">
                💬 Contactar por WhatsApp
            </a>
            
            <p style="margin-top: 20px; color: #666;">
                O responda este email directamente.
            </p>
        </body>
        </html>
        """
        
        send_mail(
            subject=asunto,
            message=mensaje,  # Versión texto plano
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[destinatario],
            html_message=html_message
        )
        
        logger.info(f"✅ Email con botón WhatsApp enviado a {destinatario}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error enviando email con botón WhatsApp: {str(e)}")
        return False


# ============================================================================
# ROUTER PRINCIPAL - SELECCIÓN AUTOMÁTICA DE PROVEEDOR
# ============================================================================

def enviar_whatsapp(telefono, mensaje, template_id=None, params=None):
    """
    Router principal para enviar WhatsApp
    
    Selecciona automáticamente el proveedor según configuración
    """
    provider = getattr(settings, 'WHATSAPP_PROVIDER', 'gupshup').lower()
    
    if provider == 'gupshup':
        return enviar_whatsapp_gupshup(telefono, mensaje, template_id, params)
    elif provider == 'ultramsg':
        return enviar_whatsapp_ultramsg(telefono, mensaje)
    elif provider == 'link':
        # Modo link: No envía, solo retorna link
        return generar_link_whatsapp(telefono, mensaje)
    else:
        logger.warning(f"Proveedor WhatsApp no configurado: {provider}")
        return False


def notificar_saldo_bajo(tarjeta, canales=['email']):
    """
    Notificar saldo bajo - Multi-canal
    
    Canales disponibles: 'email', 'whatsapp', 'whatsapp_link'
    """
    resultados = {}
    cliente = tarjeta.cliente
    responsable = cliente.responsable
    
    saldo_actual = tarjeta.saldo
    mensaje = f"Saldo bajo en tarjeta {tarjeta.numero_tarjeta}: Gs. {saldo_actual:,}"
    
    # Email
    if 'email' in canales and responsable.email:
        exito = enviar_email_saldo_bajo(tarjeta)
        resultados['email'] = exito
    
    # WhatsApp automático (Gupshup/Ultramsg)
    if 'whatsapp' in canales and responsable.telefono:
        exito = enviar_whatsapp(responsable.telefono, mensaje)
        resultados['whatsapp'] = exito
    
    # WhatsApp link (Email con botón WhatsApp - $0)
    if 'whatsapp_link' in canales and responsable.email:
        exito = enviar_email_con_boton_whatsapp(
            destinatario=responsable.email,
            asunto="⚠️ Saldo Bajo - CantiTita",
            mensaje=mensaje
        )
        resultados['whatsapp_link'] = exito
    
    return resultados
```

---

## ⚙️ CONFIGURACIÓN .env RECOMENDADA

### **Opción 1: Gupshup (RECOMENDADO)**
```ini
# WhatsApp - Gupshup (MÁS BARATO OFICIAL)
WHATSAPP_PROVIDER=gupshup
GUPSHUP_API_KEY=tu_api_key_aqui
GUPSHUP_APP_NAME=CantiTita

# Costo: $0.003/mensaje
# 200 msg/día = $18/mes
# ✅ Oficial (sin riesgo ban)
```

### **Opción 2: Email + WA.me Links (GRATIS)**
```ini
# WhatsApp - Links gratuitos
WHATSAPP_PROVIDER=link
CANTITA_WHATSAPP_CONTACTO=+595981234567

# Costo: $0/mes
# Requiere: Click del usuario
# ✅ Sin costo ni riesgo
```

### **Opción 3: Ultramsg (BARATO NO OFICIAL)**
```ini
# WhatsApp - Ultramsg (NO OFICIAL)
WHATSAPP_PROVIDER=ultramsg
ULTRAMSG_INSTANCE_ID=instance12345
ULTRAMSG_TOKEN=tu_token_aqui

# Costo: $0.001/mensaje + $30/mes = $36/mes (200 msg/día)
# ⚠️ Riesgo ban - Solo usar número secundario
```

---

## 📊 DECISIÓN FINAL

### **Para 200 mensajes/día (6,000/mes):**

| Opción | Costo/mes | Oficial | Automatizado | Recomendación |
|--------|-----------|---------|--------------|---------------|
| **Gupshup** | $18 | ✅ | ✅ | ⭐⭐⭐⭐⭐ MEJOR |
| **Email + WA Links** | $0 | ✅ | ⚠️ Parcial | ⭐⭐⭐⭐ Si $0 budget |
| **Ultramsg (num. 2°)** | $36 | ❌ | ✅ | ⭐⭐⭐ Testing |
| **Meta Business** | $36 | ✅ | ✅ | ⭐⭐⭐ Premium |
| **WATI** | $79 | ✅ | ✅ | ⭐⭐ Sobrecalificado |

---

## ✅ SIGUIENTE PASO

1. **Decidir estrategia:**
   - **Producción económica:** Registrarse en Gupshup → $18/mes
   - **Presupuesto $0:** Usar Email + WA.me Links → $0/mes
   - **Testing:** Probar Ultramsg con número secundario → $36/mes

2. **Implementar:**
   - Código ya está listo en `notificaciones.py`
   - Solo configurar `.env` con provider elegido
   - Probar con 10 mensajes test

3. **Monitorear costos:**
   - Revisar facturas mensuales
   - Ajustar si volumen cambia

**¿Qué opción prefieres?**
