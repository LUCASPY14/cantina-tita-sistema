# 💰 ALTERNATIVAS DE BAJO COSTO A TWILIO
## Proveedores SMS y WhatsApp Económicos (< $0.01/mensaje)

---

## 📊 COMPARATIVA DE COSTOS

### **SMS - Proveedores Internacionales**

| Proveedor | Costo/SMS Paraguay | Setup | Ventajas | Desventajas |
|-----------|-------------------|-------|----------|-------------|
| **Twilio** | $0.05-0.10 | 15min | Confiable, docs | ❌ CARO |
| **Vonage (Nexmo)** | $0.03-0.05 | 20min | Más barato que Twilio | Aún costoso |
| **Plivo** | $0.02-0.04 | 15min | 30% más barato | Similar a Twilio |
| **SNS AWS** | $0.00645 | 30min | ✅ MUY BARATO | Complejo setup |
| **ClickSend** | $0.025 | 10min | Fácil API | Medio |
| **MessageBird** | $0.03 | 15min | Global | Medio |

### **SMS - Proveedores Locales Paraguay**

| Proveedor | Costo/SMS | Contacto | Ventajas | Notas |
|-----------|-----------|----------|----------|-------|
| **Tigo Business** | A consultar | 1515 | Local, pago en Gs | Requiere cuenta empresarial |
| **Personal Empresas** | A consultar | *2000 | Local, soporte | Planes mensuales |
| **Claro Empresas** | A consultar | 0800-121-000 | Local | Menor cobertura |
| **SMS Paraguay** | Consultar | smsparaguay.com.py | Especializado | Desconocido |

### **WhatsApp - Proveedores**

| Proveedor | Costo/Mensaje | Tipo | Ventajas | Desventajas |
|-----------|---------------|------|----------|-------------|
| **Meta Business API** | $0.0042-0.008 | Oficial | ✅ BARATO, oficial | Requiere aprobación 2-5 días |
| **Twilio WhatsApp** | $0.005 | Oficial | Rápido setup | Requiere Twilio |
| **360Dialog** | $0.004-0.006 | Partner oficial | ✅ MUY BARATO | Requiere aprobación |
| **WATI** | $0.005 | Partner oficial | Plataforma completa | Caro en plan mensual |
| **Gupshup** | $0.003-0.005 | Partner oficial | ✅ BARATO | Setup medio |

### **WhatsApp - Opciones No Oficiales (RIESGO)**

| Proveedor | Costo | Tipo | Ventajas | Desventajas |
|-----------|-------|------|----------|-------------|
| **Baileys** | $0 (Gratis) | No oficial | Gratis | ⚠️ Riesgo de BAN |
| **whatsapp-web.js** | $0 (Gratis) | No oficial | Gratis, Node.js | ⚠️ Riesgo de BAN |
| **WPPConnect** | $0 (Gratis) | No oficial | Gratis, fácil | ⚠️ Riesgo de BAN |

---

## 🏆 RECOMENDACIONES TOP 3

### **1. AWS SNS (SMS) - $0.00645/mensaje** ⭐⭐⭐⭐⭐

**MEJOR OPCIÓN PARA SMS - 90% MÁS BARATO QUE TWILIO**

**Ventajas:**
- ✅ Costo ultra bajo: $0.00645 por SMS a Paraguay
- ✅ Sin costos mensuales fijos
- ✅ Escalable (1 mensaje o 1 millón)
- ✅ Integración con AWS (si ya usan AWS)
- ✅ 100 SMS gratis para probar (primer año)

**Desventajas:**
- ⚠️ Setup más complejo que Twilio
- ⚠️ Requiere cuenta AWS
- ⚠️ Documentación menos amigable

**Configuración:**

```python
# pip install boto3

import boto3
from django.conf import settings

def enviar_sms_aws(telefono, mensaje):
    """
    Enviar SMS usando AWS SNS - $0.00645/mensaje
    
    Args:
        telefono (str): +595981234567
        mensaje (str): Texto del mensaje
    
    Returns:
        bool: True si se envió correctamente
    """
    try:
        sns_client = boto3.client(
            'sns',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name='us-east-1'  # o tu región preferida
        )
        
        response = sns_client.publish(
            PhoneNumber=telefono,
            Message=mensaje,
            MessageAttributes={
                'AWS.SNS.SMS.SenderID': {
                    'DataType': 'String',
                    'StringValue': 'CantiTita'
                },
                'AWS.SNS.SMS.SMSType': {
                    'DataType': 'String',
                    'StringValue': 'Transactional'  # Más confiable que 'Promotional'
                }
            }
        )
        
        logger.info(f"SMS AWS enviado a {telefono}: {response['MessageId']}")
        return True
        
    except Exception as e:
        logger.error(f"Error AWS SNS: {str(e)}")
        return False
```

**Configuración `.env`:**
```ini
# AWS SNS Configuration (SMS)
SMS_PROVIDER=aws_sns
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_SNS_REGION=us-east-1

# Costo estimado: $0.00645/SMS a Paraguay
# 1000 SMS = $6.45 USD (~Gs. 45,000)
```

**Cálculo de costos:**
- 100 SMS/día x 30 días = 3,000 SMS/mes
- 3,000 x $0.00645 = **$19.35/mes** (~Gs. 135,000)
- **VS Twilio:** 3,000 x $0.08 = $240/mes (~Gs. 1,680,000)
- **AHORRO: $220/mes (92% menos)**

---

### **2. Meta WhatsApp Business API - $0.0042/mensaje** ⭐⭐⭐⭐⭐

**MEJOR OPCIÓN PARA WHATSAPP - OFICIAL Y MUY BARATO**

**Ventajas:**
- ✅ Costo ultra bajo: $0.0042-0.008 por mensaje
- ✅ Oficial de Meta (sin riesgo de ban)
- ✅ Mensajes con multimedia (imágenes, PDFs)
- ✅ Plantillas pre-aprobadas
- ✅ Analytics integrados

**Desventajas:**
- ⚠️ Requiere aprobación (2-5 días)
- ⚠️ Número dedicado (no puede ser personal)
- ⚠️ Plantillas deben aprobarse previamente

**Configuración:**

```python
# pip install requests

import requests
from django.conf import settings

def enviar_whatsapp_meta(telefono, mensaje):
    """
    Enviar WhatsApp usando Meta Business API - $0.0042/mensaje
    
    Args:
        telefono (str): +595981234567
        mensaje (str): Texto del mensaje
    
    Returns:
        bool: True si se envió correctamente
    """
    try:
        url = f"https://graph.facebook.com/v18.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
        
        headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # Opción 1: Mensaje de texto simple
        payload = {
            "messaging_product": "whatsapp",
            "to": telefono.replace('+', ''),
            "type": "text",
            "text": {
                "body": mensaje
            }
        }
        
        # Opción 2: Usar plantilla pre-aprobada (más barato)
        # payload = {
        #     "messaging_product": "whatsapp",
        #     "to": telefono.replace('+', ''),
        #     "type": "template",
        #     "template": {
        #         "name": "saldo_bajo",  # Nombre de tu plantilla aprobada
        #         "language": {"code": "es"},
        #         "components": [
        #             {
        #                 "type": "body",
        #                 "parameters": [
        #                     {"type": "text", "text": "5000"}  # Saldo
        #                 ]
        #             }
        #         ]
        #     }
        # }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            logger.info(f"WhatsApp Meta enviado a {telefono}")
            return True
        else:
            logger.error(f"Error Meta API: {response.status_code} - {response.text}")
            return False
        
    except Exception as e:
        logger.error(f"Error WhatsApp Meta: {str(e)}")
        return False
```

**Configuración `.env`:**
```ini
# Meta WhatsApp Business API
WHATSAPP_PROVIDER=meta_business
WHATSAPP_ACCESS_TOKEN=EAAxxxxxxxxxxxxxxxxxxxxxxxx
WHATSAPP_PHONE_NUMBER_ID=123456789012345

# Costo: $0.0042-0.008/mensaje (según región)
# 1000 mensajes = $4.20-8.00 USD (~Gs. 29,000-56,000)
```

**Pasos para activar:**

1. **Crear cuenta Business Manager:**
   - Ir a: https://business.facebook.com/
   - Crear cuenta de negocio
   - Verificar empresa (nombre, dirección)

2. **Agregar WhatsApp Business:**
   - En Business Manager → WhatsApp
   - Agregar número telefónico (debe ser dedicado)
   - Esperar verificación (2-5 días)

3. **Obtener credenciales:**
   - Phone Number ID
   - Access Token (permanente)

4. **Crear plantillas (opcional):**
   - Ir a plantillas en Business Manager
   - Crear plantilla "saldo_bajo"
   - Esperar aprobación (24-48 horas)

**Cálculo de costos:**
- 100 mensajes/día x 30 días = 3,000 mensajes/mes
- 3,000 x $0.006 = **$18/mes** (~Gs. 126,000)
- **VS Twilio WhatsApp:** 3,000 x $0.005 = $15/mes (similar)
- **Ventaja:** Oficial, sin riesgo de ban, multimedia

---

### **3. 360Dialog (WhatsApp Partner) - $0.004/mensaje** ⭐⭐⭐⭐

**ALTERNATIVA A META - MISMO PRECIO, MÁS FÁCIL SETUP**

**Ventajas:**
- ✅ Precio similar a Meta: $0.004-0.006
- ✅ Partner oficial de WhatsApp
- ✅ Setup más fácil que Meta directo
- ✅ Soporte técnico incluido
- ✅ Dashboard amigable

**Desventajas:**
- ⚠️ Requiere aprobación (similar a Meta)
- ⚠️ Número dedicado

**Configuración:**

```python
import requests
from django.conf import settings

def enviar_whatsapp_360dialog(telefono, mensaje):
    """
    Enviar WhatsApp usando 360Dialog - $0.004/mensaje
    
    Args:
        telefono (str): +595981234567
        mensaje (str): Texto del mensaje
    
    Returns:
        bool: True si se envió correctamente
    """
    try:
        url = f"https://waba.360dialog.io/v1/messages"
        
        headers = {
            "D360-API-KEY": settings.DIALOG_360_API_KEY,
            "Content-Type": "application/json"
        }
        
        payload = {
            "to": telefono.replace('+', ''),
            "type": "text",
            "text": {
                "body": mensaje
            }
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            logger.info(f"WhatsApp 360Dialog enviado a {telefono}")
            return True
        else:
            logger.error(f"Error 360Dialog: {response.status_code}")
            return False
        
    except Exception as e:
        logger.error(f"Error 360Dialog: {str(e)}")
        return False
```

**Configuración `.env`:**
```ini
# 360Dialog WhatsApp
WHATSAPP_PROVIDER=dialog_360
DIALOG_360_API_KEY=your_api_key_here

# Costo: $0.004-0.006/mensaje
```

**Pasos para activar:**
1. Registrarse en: https://www.360dialog.com/
2. Verificar empresa
3. Obtener API Key
4. Configurar número WhatsApp

---

## 🆓 OPCIÓN GRATUITA (CON RIESGOS)

### **Baileys + whatsapp-web.js - $0 (Gratis)** ⚠️

**Solo para testing o volúmenes muy bajos (<50 mensajes/día)**

**Ventajas:**
- ✅ Completamente gratis
- ✅ Sin límites de mensajes
- ✅ No requiere aprobación
- ✅ Setup en minutos

**Desventajas:**
- ❌ Riesgo de ban de WhatsApp
- ❌ No oficial
- ❌ Puede dejar de funcionar
- ❌ Requiere escanear QR periódicamente

**Configuración (Node.js):**

```javascript
// baileys_server.js
const { default: makeWASocket, useMultiFileAuthState } = require('@whiskeysockets/baileys')
const express = require('express')

const app = express()
app.use(express.json())

let sock

async function connectToWhatsApp() {
    const { state, saveCreds } = await useMultiFileAuthState('auth_info')
    
    sock = makeWASocket({
        auth: state,
        printQRInTerminal: true  // Escanear QR al iniciar
    })
    
    sock.ev.on('creds.update', saveCreds)
}

// Endpoint para enviar mensaje
app.post('/send', async (req, res) => {
    const { phone, message } = req.body
    
    try {
        await sock.sendMessage(phone + '@s.whatsapp.net', { text: message })
        res.json({ success: true })
    } catch (error) {
        res.status(500).json({ success: false, error: error.message })
    }
})

app.listen(3000, () => {
    console.log('WhatsApp server running on port 3000')
    connectToWhatsApp()
})
```

**Integración con Django:**

```python
import requests

def enviar_whatsapp_baileys(telefono, mensaje):
    """
    Enviar WhatsApp usando Baileys (gratis pero riesgoso)
    
    Args:
        telefono (str): 595981234567 (sin +)
        mensaje (str): Texto del mensaje
    
    Returns:
        bool: True si se envió correctamente
    """
    try:
        response = requests.post(
            'http://localhost:3000/send',
            json={
                'phone': telefono.replace('+', ''),
                'message': mensaje
            },
            timeout=10
        )
        
        return response.status_code == 200
        
    except Exception as e:
        logger.error(f"Error Baileys: {str(e)}")
        return False
```

**⚠️ ADVERTENCIA:** Meta puede banear el número sin previo aviso. **NO USAR EN PRODUCCIÓN**.

---

## 📋 TABLA RESUMEN - MEJOR PRECIO/VALOR

| Proveedor | Costo/Mensaje | Tipo | Recomendado Para | Rating |
|-----------|---------------|------|------------------|--------|
| **AWS SNS** | $0.00645 | SMS | ✅ PRODUCCIÓN | ⭐⭐⭐⭐⭐ |
| **Meta Business API** | $0.0042-0.008 | WhatsApp | ✅ PRODUCCIÓN | ⭐⭐⭐⭐⭐ |
| **360Dialog** | $0.004-0.006 | WhatsApp | PRODUCCIÓN | ⭐⭐⭐⭐ |
| **Plivo** | $0.02-0.04 | SMS | Medio volumen | ⭐⭐⭐ |
| **ClickSend** | $0.025 | SMS | Fácil setup | ⭐⭐⭐ |
| **Baileys** | $0 (Gratis) | WhatsApp | ⚠️ Solo testing | ⭐⭐ |

---

## 💡 ESTRATEGIA RECOMENDADA

### **Para Cantina Tita:**

**1. Fase 1: Email (GRATIS - Ya implementado)**
- ✅ Gmail SMTP (500 emails/día gratis)
- ✅ SendGrid (100 emails/día gratis)
- **Costo:** $0/mes
- **Para:** Notificaciones principales

**2. Fase 2: SMS (Bajo costo)**
- ✅ **AWS SNS** para SMS críticos
- **Costo:** $0.00645/SMS
- **Estimado:** 100 SMS/día = $19/mes
- **Para:** Alertas urgentes (saldo bajo)

**3. Fase 3: WhatsApp (Muy bajo costo)**
- ✅ **Meta Business API** oficial
- **Costo:** $0.006/mensaje
- **Estimado:** 200 mensajes/día = $36/mes
- **Para:** Confirmaciones de recarga, cuenta pendiente

**Total estimado:**
- Email: $0
- SMS (100/día): $19/mes
- WhatsApp (200/día): $36/mes
- **TOTAL: $55/mes (~Gs. 385,000)**

**VS Twilio todo:**
- SMS (100/día): $240/mes
- WhatsApp (200/día): $30/mes
- **TOTAL: $270/mes (~Gs. 1,890,000)**

**AHORRO: $215/mes (80% menos)**

---

## 🔧 ACTUALIZACIÓN DE CÓDIGO

Actualizar `gestion/notificaciones.py` para soportar AWS SNS y Meta:

```python
# Agregar al archivo existente

# ==================== AWS SNS (SMS) ====================

def enviar_sms_aws_sns(telefono, mensaje):
    """
    Enviar SMS usando AWS SNS - $0.00645/mensaje
    
    Configurar en .env:
    SMS_PROVIDER=aws_sns
    AWS_ACCESS_KEY_ID=tu_key
    AWS_SECRET_ACCESS_KEY=tu_secret
    AWS_SNS_REGION=us-east-1
    """
    try:
        import boto3
        
        sns_client = boto3.client(
            'sns',
            aws_access_key_id=getattr(settings, 'AWS_ACCESS_KEY_ID', None),
            aws_secret_access_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY', None),
            region_name=getattr(settings, 'AWS_SNS_REGION', 'us-east-1')
        )
        
        # Normalizar teléfono
        if not telefono.startswith('+'):
            telefono = '+' + telefono
        
        response = sns_client.publish(
            PhoneNumber=telefono,
            Message=mensaje,
            MessageAttributes={
                'AWS.SNS.SMS.SenderID': {
                    'DataType': 'String',
                    'StringValue': 'CantiTita'
                },
                'AWS.SNS.SMS.SMSType': {
                    'DataType': 'String',
                    'StringValue': 'Transactional'
                }
            }
        )
        
        logger.info(f"SMS AWS enviado a {telefono}: {response['MessageId']}")
        return True
        
    except Exception as e:
        logger.error(f"Error AWS SNS: {str(e)}")
        return False


# ==================== META WHATSAPP ====================

def enviar_whatsapp_meta_business(telefono, mensaje):
    """
    Enviar WhatsApp usando Meta Business API - $0.0042/mensaje
    
    Configurar en .env:
    WHATSAPP_PROVIDER=meta_business
    WHATSAPP_ACCESS_TOKEN=tu_token
    WHATSAPP_PHONE_NUMBER_ID=tu_phone_id
    """
    try:
        import requests
        
        access_token = getattr(settings, 'WHATSAPP_ACCESS_TOKEN', None)
        phone_number_id = getattr(settings, 'WHATSAPP_PHONE_NUMBER_ID', None)
        
        if not all([access_token, phone_number_id]):
            logger.error("Configuración de Meta WhatsApp incompleta")
            return False
        
        url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Limpiar teléfono
        telefono_limpio = telefono.replace('+', '').replace(' ', '')
        
        payload = {
            "messaging_product": "whatsapp",
            "to": telefono_limpio,
            "type": "text",
            "text": {"body": mensaje}
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            logger.info(f"WhatsApp Meta enviado a {telefono}")
            return True
        else:
            logger.error(f"Error Meta API: {response.status_code} - {response.text}")
            return False
        
    except Exception as e:
        logger.error(f"Error WhatsApp Meta: {str(e)}")
        return False


# Actualizar función enviar_sms() para soportar AWS SNS
def enviar_sms(telefono, mensaje):
    """Envía SMS usando el proveedor configurado"""
    
    # Normalizar teléfono
    if telefono.startswith('0'):
        telefono = '+595' + telefono[1:]
    elif not telefono.startswith('+'):
        telefono = '+595' + telefono
    
    if SMS_PROVIDER == 'aws_sns':
        return enviar_sms_aws_sns(telefono, mensaje)
    elif SMS_PROVIDER == 'twilio':
        return enviar_sms_twilio(telefono, mensaje)
    elif SMS_PROVIDER == 'tigo':
        return enviar_sms_tigo(telefono, mensaje)
    elif SMS_PROVIDER == 'personal':
        return enviar_sms_personal(telefono, mensaje)
    else:
        logger.error(f"Proveedor SMS desconocido: {SMS_PROVIDER}")
        return False


# Actualizar función enviar_whatsapp()
def enviar_whatsapp(telefono, mensaje):
    """Envía WhatsApp usando el proveedor configurado"""
    
    # Normalizar teléfono
    if telefono.startswith('0'):
        telefono = '+595' + telefono[1:]
    elif not telefono.startswith('+'):
        telefono = '+595' + telefono
    
    if WHATSAPP_PROVIDER == 'meta_business':
        return enviar_whatsapp_meta_business(telefono, mensaje)
    elif WHATSAPP_PROVIDER == 'business_api':
        return enviar_whatsapp_business_api(telefono, mensaje)  # Mismo que meta
    elif WHATSAPP_PROVIDER == 'twilio':
        return enviar_whatsapp_twilio(telefono, mensaje)
    else:
        logger.error(f"Proveedor WhatsApp desconocido: {WHATSAPP_PROVIDER}")
        return False
```

---

## 📝 CONFIGURACIÓN `.env` RECOMENDADA

```ini
# ==================== EMAIL (GRATIS) ====================
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu_email@gmail.com
EMAIL_HOST_PASSWORD=tu_app_password
DEFAULT_FROM_EMAIL=Cantina Tita <tu_email@gmail.com>

# ==================== SMS (AWS SNS - MÁS BARATO) ====================
SMS_PROVIDER=aws_sns
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_SNS_REGION=us-east-1

# Costo: $0.00645/SMS (~Gs. 45 por SMS)
# 100 SMS/día = $19/mes (~Gs. 133,000/mes)

# ==================== WHATSAPP (META - MÁS BARATO) ====================
WHATSAPP_PROVIDER=meta_business
WHATSAPP_ACCESS_TOKEN=EAAxxxxxxxxxxxxxxxxxxxxxxxxxx
WHATSAPP_PHONE_NUMBER_ID=123456789012345

# Costo: $0.006/mensaje (~Gs. 42 por mensaje)
# 200 mensajes/día = $36/mes (~Gs. 252,000/mes)

# ==================== TOTAL ESTIMADO ====================
# Email: $0/mes (500/día gratis con Gmail)
# SMS: $19/mes (100/día con AWS SNS)
# WhatsApp: $36/mes (200/día con Meta)
# TOTAL: $55/mes (~Gs. 385,000/mes)
#
# VS Twilio: $270/mes (~Gs. 1,890,000/mes)
# AHORRO: $215/mes (80% menos) ✅
```

---

## 🎯 RESUMEN EJECUTIVO

### **Mejores Opciones de Bajo Costo:**

1. **SMS:** AWS SNS - $0.00645/mensaje (92% más barato que Twilio)
2. **WhatsApp:** Meta Business API - $0.006/mensaje (oficial y barato)
3. **Email:** Gmail SMTP - $0 (gratis hasta 500/día)

### **Costo Total Estimado:**
- **$55/mes** para 100 SMS + 200 WhatsApp + emails ilimitados
- **VS $270/mes** con Twilio
- **AHORRO: 80%**

### **Próximos Pasos:**

1. ✅ **Configurar AWS SNS** (30 min)
   - Crear cuenta AWS
   - Obtener credenciales IAM
   - Instalar `boto3`

2. ✅ **Configurar Meta WhatsApp** (2-5 días)
   - Crear Business Manager
   - Verificar empresa
   - Obtener Phone Number ID y Token

3. ✅ **Actualizar código** (15 min)
   - Agregar funciones AWS/Meta a notificaciones.py
   - Configurar `.env`
   - Testing

---

**Total Ahorro Anual:** $2,580/año (~Gs. 18,060,000/año) ✅
