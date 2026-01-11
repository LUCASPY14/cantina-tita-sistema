# 💬 GUÍA COMPLETA: WhatsApp Económico
## Opciones de Bajo Costo para Notificaciones

---

## 📊 RANKING DE OPCIONES (De más barata a más cara)

| # | Proveedor | Costo/Mensaje | Setup | Oficial | Riesgo | Rating |
|---|-----------|---------------|-------|---------|--------|--------|
| 🥇 | **Baileys (Self-hosted)** | **$0 GRATIS** | 30min | ❌ No | ⚠️ Alto | ⭐⭐ |
| 🥈 | **Gupshup** | **$0.003** | 2-3 días | ✅ Sí | ✅ Bajo | ⭐⭐⭐⭐⭐ |
| 🥉 | **360Dialog** | **$0.004** | 2-3 días | ✅ Sí | ✅ Bajo | ⭐⭐⭐⭐⭐ |
| 4 | **Twilio WhatsApp** | **$0.005** | 1 hora | ✅ Sí | ✅ Bajo | ⭐⭐⭐⭐ |
| 5 | **Meta Business API** | **$0.0042-0.008** | 3-5 días | ✅ Sí | ✅ Bajo | ⭐⭐⭐⭐⭐ |
| 6 | **WATI** | **$0.005 + $49/mes** | 1 día | ✅ Sí | ✅ Bajo | ⭐⭐⭐ |

---

## 🥇 OPCIÓN 1: BAILEYS (Self-Hosted) - $0 GRATIS

### **¿Por qué es gratis?**
- Usa WhatsApp Web (no oficial)
- No requiere API paga
- Self-hosted (tu propio servidor)

### **⚠️ ADVERTENCIAS CRÍTICAS:**
- ❌ **NO OFICIAL** - Viola términos de servicio de WhatsApp
- ❌ **Riesgo de BAN** - Pueden banear tu número sin previo aviso
- ❌ **Inestable** - WhatsApp puede cambiar y dejar de funcionar
- ❌ **Requiere QR** - Debes escanear QR cada cierto tiempo
- ⚠️ **SOLO PARA TESTING** - No usar con más de 50 mensajes/día

### **✅ Cuándo usar:**
- Testing/desarrollo
- Volúmenes muy bajos (<20 mensajes/día)
- Presupuesto cero absoluto
- No tienes otra opción

### **Implementación Completa:**

#### **Paso 1: Crear servidor Node.js**

```bash
# Crear directorio
mkdir whatsapp-server
cd whatsapp-server

# Inicializar proyecto
npm init -y

# Instalar dependencias
npm install @whiskeysockets/baileys express qrcode-terminal
```

#### **Paso 2: Crear servidor (`server.js`)**

```javascript
const { default: makeWASocket, useMultiFileAuthState, DisconnectReason } = require('@whiskeysockets/baileys')
const express = require('express')
const qrcode = require('qrcode-terminal')

const app = express()
app.use(express.json())

let sock
let qr = null
let isReady = false

async function connectToWhatsApp() {
    const { state, saveCreds } = await useMultiFileAuthState('auth_info_baileys')
    
    sock = makeWASocket({
        auth: state,
        printQRInTerminal: true
    })
    
    sock.ev.on('connection.update', (update) => {
        const { connection, lastDisconnect, qr: newQr } = update
        
        if (newQr) {
            qr = newQr
            console.log('QR Code generado. Escanear con WhatsApp.')
            qrcode.generate(newQr, { small: true })
        }
        
        if (connection === 'close') {
            const shouldReconnect = lastDisconnect?.error?.output?.statusCode !== DisconnectReason.loggedOut
            console.log('Conexión cerrada. Reconectando:', shouldReconnect)
            
            if (shouldReconnect) {
                connectToWhatsApp()
            }
        } else if (connection === 'open') {
            console.log('✅ Conectado a WhatsApp!')
            isReady = true
            qr = null
        }
    })
    
    sock.ev.on('creds.update', saveCreds)
}

// Endpoint para verificar estado
app.get('/status', (req, res) => {
    res.json({
        ready: isReady,
        qr: qr ? 'QR disponible en consola' : null
    })
})

// Endpoint para enviar mensaje
app.post('/send', async (req, res) => {
    const { phone, message } = req.body
    
    if (!isReady) {
        return res.status(503).json({
            success: false,
            error: 'WhatsApp no está conectado. Escanear QR primero.'
        })
    }
    
    try {
        // Formato: 595981234567@s.whatsapp.net
        let phoneNumber = phone.replace(/[^0-9]/g, '')
        if (!phoneNumber.startsWith('595')) {
            phoneNumber = '595' + phoneNumber
        }
        
        const jid = phoneNumber + '@s.whatsapp.net'
        
        await sock.sendMessage(jid, { text: message })
        
        res.json({
            success: true,
            message: 'Mensaje enviado correctamente',
            to: phoneNumber
        })
    } catch (error) {
        console.error('Error enviando mensaje:', error)
        res.status(500).json({
            success: false,
            error: error.message
        })
    }
})

// Endpoint para enviar mensaje con imagen
app.post('/send-image', async (req, res) => {
    const { phone, message, imageUrl } = req.body
    
    if (!isReady) {
        return res.status(503).json({
            success: false,
            error: 'WhatsApp no está conectado'
        })
    }
    
    try {
        let phoneNumber = phone.replace(/[^0-9]/g, '')
        if (!phoneNumber.startsWith('595')) {
            phoneNumber = '595' + phoneNumber
        }
        
        const jid = phoneNumber + '@s.whatsapp.net'
        
        await sock.sendMessage(jid, {
            image: { url: imageUrl },
            caption: message
        })
        
        res.json({ success: true })
    } catch (error) {
        res.status(500).json({ success: false, error: error.message })
    }
})

const PORT = process.env.PORT || 3000
app.listen(PORT, async () => {
    console.log(`🚀 WhatsApp Server corriendo en puerto ${PORT}`)
    await connectToWhatsApp()
})
```

#### **Paso 3: Iniciar servidor**

```bash
# Iniciar servidor
node server.js

# Se mostrará un QR en la terminal
# Escanear con WhatsApp (Configuración > Dispositivos vinculados > Vincular dispositivo)
```

#### **Paso 4: Integración con Django**

```python
# Actualizar gestion/notificaciones.py

import requests
import logging

logger = logging.getLogger(__name__)

def enviar_whatsapp_baileys(telefono, mensaje):
    """
    Enviar WhatsApp usando Baileys (GRATIS pero riesgoso)
    
    Requiere servidor Node.js corriendo en localhost:3000
    
    Args:
        telefono (str): 0981234567 o 595981234567
        mensaje (str): Texto del mensaje
    
    Returns:
        bool: True si se envió correctamente
    """
    try:
        # Limpiar teléfono
        telefono_limpio = telefono.replace('+', '').replace(' ', '').replace('-', '')
        if telefono_limpio.startswith('0'):
            telefono_limpio = '595' + telefono_limpio[1:]
        
        # Endpoint del servidor Baileys
        baileys_url = getattr(settings, 'BAILEYS_SERVER_URL', 'http://localhost:3000')
        
        response = requests.post(
            f'{baileys_url}/send',
            json={
                'phone': telefono_limpio,
                'message': mensaje
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                logger.info(f"WhatsApp Baileys enviado a {telefono}")
                return True
            else:
                logger.error(f"Error Baileys: {data.get('error')}")
                return False
        else:
            logger.error(f"Error Baileys HTTP: {response.status_code}")
            return False
        
    except Exception as e:
        logger.error(f"Error WhatsApp Baileys: {str(e)}")
        return False


def enviar_whatsapp_baileys_con_imagen(telefono, mensaje, imagen_url):
    """
    Enviar WhatsApp con imagen usando Baileys
    """
    try:
        telefono_limpio = telefono.replace('+', '').replace(' ', '').replace('-', '')
        if telefono_limpio.startswith('0'):
            telefono_limpio = '595' + telefono_limpio[1:]
        
        baileys_url = getattr(settings, 'BAILEYS_SERVER_URL', 'http://localhost:3000')
        
        response = requests.post(
            f'{baileys_url}/send-image',
            json={
                'phone': telefono_limpio,
                'message': mensaje,
                'imageUrl': imagen_url
            },
            timeout=15
        )
        
        return response.status_code == 200 and response.json().get('success')
        
    except Exception as e:
        logger.error(f"Error WhatsApp Baileys imagen: {str(e)}")
        return False
```

#### **Paso 5: Configuración `.env`**

```ini
# WhatsApp Baileys (Gratis - Self-hosted)
WHATSAPP_PROVIDER=baileys
BAILEYS_SERVER_URL=http://localhost:3000

# Costo: $0/mensaje (GRATIS)
# Límite recomendado: 20-50 mensajes/día
# ⚠️ ADVERTENCIA: No oficial, riesgo de ban
```

#### **Paso 6: Mantener servidor corriendo (PM2)**

```bash
# Instalar PM2 (gestor de procesos)
npm install -g pm2

# Iniciar servidor con PM2
pm2 start server.js --name whatsapp-server

# Ver logs
pm2 logs whatsapp-server

# Reiniciar automáticamente si se cae
pm2 startup
pm2 save
```

### **Ventajas de Baileys:**
- ✅ Completamente gratis
- ✅ Sin límites de mensajes (en teoría)
- ✅ Soporte para multimedia (imágenes, videos, PDFs)
- ✅ No requiere aprobación de Meta
- ✅ Setup en 30 minutos

### **Desventajas de Baileys:**
- ❌ NO OFICIAL - Viola TOS de WhatsApp
- ❌ Riesgo de ban permanente del número
- ❌ Requiere servidor Node.js corriendo 24/7
- ❌ Necesita escanear QR periódicamente
- ❌ Puede dejar de funcionar sin aviso
- ❌ No hay soporte oficial

### **Costo Real:**
- Mensajes: **$0** (gratis)
- Servidor: **$5-10/mes** (VPS o servidor local)
- **Total: $5-10/mes** (si cuentas hosting)

---

## 🥈 OPCIÓN 2: GUPSHUP - $0.003/mensaje

### **LA MÁS BARATA OFICIAL** ⭐⭐⭐⭐⭐

**¿Por qué tan barato?**
- Partner oficial de WhatsApp desde hace años
- Gran volumen = precios menores
- Enfocados en mercados emergentes

### **Características:**
- ✅ **Oficial** - Partner de WhatsApp
- ✅ **Muy barato** - $0.003/mensaje (40% más barato que Meta)
- ✅ **Sin riesgo** - Cuenta oficial, no hay bans
- ✅ **Multimedia** - Imágenes, videos, documentos
- ✅ **Plantillas** - Sistema de templates pre-aprobados
- ✅ **API REST** - Fácil integración

### **Implementación Completa:**

#### **Paso 1: Registro en Gupshup**

1. Ir a: https://www.gupshup.io/
2. Crear cuenta (Sign Up)
3. Verificar email
4. Completar perfil de empresa
5. Solicitar activación de WhatsApp Business API

#### **Paso 2: Configuración inicial**

1. En dashboard, ir a "WhatsApp"
2. Registrar número telefónico
3. Esperar aprobación (24-72 horas)
4. Obtener API Key

#### **Paso 3: Crear plantillas (templates)**

```
Ejemplo de plantilla "saldo_bajo":

Hola {{1}},

La tarjeta de {{2}} tiene saldo bajo.

Saldo actual: Gs. {{3}}

Por favor recargue pronto.

Gracias,
Cantina Tita
```

Variables:
- {{1}} = Nombre del padre
- {{2}} = Nombre del hijo
- {{3}} = Saldo actual

#### **Paso 4: Integración con Django**

```python
# gestion/notificaciones.py

import requests
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def enviar_whatsapp_gupshup(telefono, mensaje, template_id=None, params=None):
    """
    Enviar WhatsApp usando Gupshup - $0.003/mensaje
    
    Configurar en .env:
    WHATSAPP_PROVIDER=gupshup
    GUPSHUP_API_KEY=tu_api_key
    GUPSHUP_APP_NAME=tu_app_name
    
    Args:
        telefono (str): 595981234567
        mensaje (str): Mensaje de texto (si no usa template)
        template_id (str): ID de plantilla pre-aprobada
        params (list): Parámetros para la plantilla
    
    Returns:
        bool: True si se envió correctamente
    """
    try:
        api_key = getattr(settings, 'GUPSHUP_API_KEY', None)
        app_name = getattr(settings, 'GUPSHUP_APP_NAME', None)
        
        if not all([api_key, app_name]):
            logger.error("Configuración de Gupshup incompleta")
            return False
        
        # Limpiar teléfono
        telefono_limpio = telefono.replace('+', '').replace(' ', '').replace('-', '')
        if telefono_limpio.startswith('0'):
            telefono_limpio = '595' + telefono_limpio[1:]
        
        url = "https://api.gupshup.io/sm/api/v1/msg"
        
        headers = {
            "apikey": api_key,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        # Opción 1: Mensaje simple (puede requerir aprobación)
        if not template_id:
            payload = {
                "channel": "whatsapp",
                "source": app_name,
                "destination": telefono_limpio,
                "message": json.dumps({"type": "text", "text": mensaje})
            }
        
        # Opción 2: Template pre-aprobado (recomendado)
        else:
            template_params = params or []
            payload = {
                "channel": "whatsapp",
                "source": app_name,
                "destination": telefono_limpio,
                "message": json.dumps({
                    "type": "template",
                    "template": {
                        "id": template_id,
                        "params": template_params
                    }
                })
            }
        
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                logger.info(f"WhatsApp Gupshup enviado a {telefono}: {data.get('messageId')}")
                return True
            else:
                logger.error(f"Error Gupshup: {data}")
                return False
        else:
            logger.error(f"Error Gupshup HTTP: {response.status_code} - {response.text}")
            return False
        
    except Exception as e:
        logger.error(f"Error WhatsApp Gupshup: {str(e)}")
        return False


def notificar_saldo_bajo_gupshup(tarjeta):
    """
    Notificar saldo bajo usando plantilla de Gupshup
    """
    try:
        responsable = tarjeta.id_hijo.id_cliente_responsable
        hijo = tarjeta.id_hijo
        
        if not responsable.telefono:
            logger.warning(f"Cliente {responsable.id_cliente} no tiene teléfono")
            return False
        
        # Usar template pre-aprobado "saldo_bajo"
        # Las plantillas tienen variables {{1}}, {{2}}, etc.
        params = [
            responsable.nombres,  # {{1}}
            f"{hijo.nombre} {hijo.apellido}",  # {{2}}
            f"{tarjeta.saldo_actual:,.0f}"  # {{3}}
        ]
        
        return enviar_whatsapp_gupshup(
            responsable.telefono,
            mensaje=None,  # No se usa con templates
            template_id="saldo_bajo",  # ID de tu plantilla
            params=params
        )
        
    except Exception as e:
        logger.error(f"Error notificar_saldo_bajo_gupshup: {str(e)}")
        return False


def enviar_whatsapp_gupshup_con_imagen(telefono, mensaje, imagen_url):
    """
    Enviar WhatsApp con imagen usando Gupshup
    """
    try:
        api_key = getattr(settings, 'GUPSHUP_API_KEY', None)
        app_name = getattr(settings, 'GUPSHUP_APP_NAME', None)
        
        telefono_limpio = telefono.replace('+', '').replace(' ', '').replace('-', '')
        if telefono_limpio.startswith('0'):
            telefono_limpio = '595' + telefono_limpio[1:]
        
        url = "https://api.gupshup.io/sm/api/v1/msg"
        
        headers = {
            "apikey": api_key,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        payload = {
            "channel": "whatsapp",
            "source": app_name,
            "destination": telefono_limpio,
            "message": json.dumps({
                "type": "image",
                "originalUrl": imagen_url,
                "previewUrl": imagen_url,
                "caption": mensaje
            })
        }
        
        response = requests.post(url, headers=headers, data=payload, timeout=15)
        
        return response.status_code == 200 and response.json().get('status') == 'success'
        
    except Exception as e:
        logger.error(f"Error Gupshup imagen: {str(e)}")
        return False
```

#### **Paso 5: Configuración `.env`**

```ini
# Gupshup WhatsApp (Más barato oficial)
WHATSAPP_PROVIDER=gupshup
GUPSHUP_API_KEY=tu_api_key_aqui
GUPSHUP_APP_NAME=CantiTita

# Costo: $0.003/mensaje (~Gs. 21 por mensaje)
# 200 mensajes/día = $18/mes (~Gs. 126,000/mes)
# 50% más barato que Meta o Twilio ✅
```

### **Cálculo de Costos Gupshup:**

| Volumen/Día | Mensajes/Mes | Costo/Mes | Costo/Año |
|-------------|--------------|-----------|-----------|
| 50 mensajes | 1,500 | $4.50 | $54 |
| 100 mensajes | 3,000 | $9 | $108 |
| 200 mensajes | 6,000 | $18 | $216 |
| 500 mensajes | 15,000 | $45 | $540 |

### **Ventajas de Gupshup:**
- ✅ MÁS BARATO oficial ($0.003)
- ✅ Partner de WhatsApp (sin riesgo)
- ✅ API simple y documentada
- ✅ Soporte para multimedia
- ✅ Templates pre-aprobados
- ✅ Analytics incluido
- ✅ Sin costos mensuales fijos

### **Desventajas de Gupshup:**
- ⚠️ Requiere aprobación (2-3 días)
- ⚠️ Templates deben aprobarse
- ⚠️ Interfaz menos moderna que Meta

---

## 🥉 OPCIÓN 3: 360DIALOG - $0.004/mensaje

### **SEGUNDA MÁS BARATA + MEJOR SOPORTE**

### **Implementación:**

```python
def enviar_whatsapp_360dialog(telefono, mensaje):
    """
    Enviar WhatsApp usando 360Dialog - $0.004/mensaje
    
    Configurar en .env:
    WHATSAPP_PROVIDER=dialog_360
    DIALOG_360_API_KEY=tu_api_key
    """
    try:
        api_key = getattr(settings, 'DIALOG_360_API_KEY', None)
        
        if not api_key:
            logger.error("API Key de 360Dialog no configurada")
            return False
        
        telefono_limpio = telefono.replace('+', '').replace(' ', '')
        if telefono_limpio.startswith('0'):
            telefono_limpio = '595' + telefono_limpio[1:]
        
        url = "https://waba.360dialog.io/v1/messages"
        
        headers = {
            "D360-API-KEY": api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "to": telefono_limpio,
            "type": "text",
            "text": {"body": mensaje}
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 201:
            logger.info(f"WhatsApp 360Dialog enviado a {telefono}")
            return True
        else:
            logger.error(f"Error 360Dialog: {response.status_code} - {response.text}")
            return False
        
    except Exception as e:
        logger.error(f"Error 360Dialog: {str(e)}")
        return False
```

**Costo:** $0.004/mensaje (~$24/mes para 200 mensajes/día)

---

## 📊 COMPARATIVA FINAL

### **Costos para 200 mensajes/día (6,000/mes):**

| Proveedor | Costo/Mensaje | Costo/Mes | Oficial | Setup |
|-----------|---------------|-----------|---------|-------|
| **Baileys** | $0 + hosting | ~$5-10 | ❌ | 30min |
| **Gupshup** ⭐ | **$0.003** | **$18** | ✅ | 2-3 días |
| **360Dialog** | $0.004 | $24 | ✅ | 2-3 días |
| **Twilio WA** | $0.005 | $30 | ✅ | 1 hora |
| **Meta API** | $0.006 | $36 | ✅ | 3-5 días |

### **Ahorro anual (vs Twilio):**

**Gupshup vs Twilio:**
- Twilio: $30/mes x 12 = $360/año
- Gupshup: $18/mes x 12 = $216/año
- **AHORRO: $144/año (40%)**

**Baileys vs Twilio:**
- Twilio: $360/año
- Baileys: $60-120/año (solo hosting)
- **AHORRO: $240-300/año (70-80%)**
- **PERO:** ⚠️ Riesgo de ban

---

## 🎯 RECOMENDACIÓN FINAL

### **Para Cantina Tita:**

**ESCENARIO 1: Presupuesto limitado + Volumen medio (100-200 msg/día)**
```
✅ GUPSHUP - $0.003/mensaje
Costo: $18/mes
Oficial, confiable, económico
```

**ESCENARIO 2: Presupuesto muy ajustado + Volumen bajo (<50 msg/día)**
```
⚠️ BAILEYS (con precaución)
Costo: $5-10/mes (hosting)
Solo para testing o emergencia
RIESGO: Ban del número
```

**ESCENARIO 3: Presupuesto normal + Quieres lo mejor**
```
✅ META BUSINESS API - $0.006/mensaje
Costo: $36/mes
Más confiable, mejor soporte
```

---

## 🔧 CÓDIGO ACTUALIZADO PARA NOTIFICACIONES.PY

```python
# Agregar al final de gestion/notificaciones.py

# Actualizar función principal enviar_whatsapp()
def enviar_whatsapp(telefono, mensaje):
    """Envía WhatsApp usando el proveedor configurado"""
    
    # Normalizar teléfono
    if telefono.startswith('0'):
        telefono = '+595' + telefono[1:]
    elif not telefono.startswith('+'):
        telefono = '+595' + telefono
    
    provider = getattr(settings, 'WHATSAPP_PROVIDER', 'gupshup')
    
    if provider == 'gupshup':
        return enviar_whatsapp_gupshup(telefono, mensaje)
    elif provider == 'dialog_360':
        return enviar_whatsapp_360dialog(telefono, mensaje)
    elif provider == 'baileys':
        return enviar_whatsapp_baileys(telefono, mensaje)
    elif provider == 'meta_business':
        return enviar_whatsapp_meta_business(telefono, mensaje)
    elif provider == 'twilio':
        return enviar_whatsapp_twilio(telefono, mensaje)
    else:
        logger.error(f"Proveedor WhatsApp desconocido: {provider}")
        return False
```

---

## 📝 CONFIGURACIÓN .ENV RECOMENDADA

```ini
# ==================== OPCIÓN 1: GUPSHUP (MÁS BARATO) ====================
WHATSAPP_PROVIDER=gupshup
GUPSHUP_API_KEY=tu_api_key_aqui
GUPSHUP_APP_NAME=CantiTita

# Costo: $0.003/mensaje
# 200 msg/día = $18/mes (~Gs. 126,000/mes)
# ✅ Recomendado para producción económica

# ==================== OPCIÓN 2: BAILEYS (GRATIS CON RIESGO) ====================
# WHATSAPP_PROVIDER=baileys
# BAILEYS_SERVER_URL=http://localhost:3000

# Costo: $0/mensaje (solo hosting $5-10/mes)
# ⚠️ Solo para testing o volúmenes muy bajos
# ⚠️ Riesgo de ban del número

# ==================== OPCIÓN 3: 360DIALOG ====================
# WHATSAPP_PROVIDER=dialog_360
# DIALOG_360_API_KEY=tu_api_key

# Costo: $0.004/mensaje
# 200 msg/día = $24/mes
```

---

## 🚀 PRÓXIMOS PASOS

### **Si eliges GUPSHUP (Recomendado):**

1. ✅ Registrarse en https://www.gupshup.io/
2. ✅ Verificar cuenta empresarial (2-3 días)
3. ✅ Crear templates de mensajes
4. ✅ Obtener API Key
5. ✅ Agregar código a notificaciones.py
6. ✅ Configurar .env
7. ✅ Testing con 10 mensajes gratis
8. ✅ Producción

**Tiempo total:** 3-4 días (esperando aprobación)

### **Si eliges BAILEYS (Solo testing):**

1. ✅ Instalar Node.js y dependencias (30 min)
2. ✅ Crear servidor WhatsApp (30 min)
3. ✅ Escanear QR con WhatsApp (5 min)
4. ✅ Integrar con Django (15 min)
5. ✅ Testing con mensajes de prueba
6. ⚠️ Monitorear por bans

**Tiempo total:** 1-2 horas

---

## 💰 AHORRO ESTIMADO ANUAL

**Cantina Tita - 200 mensajes/día:**

| Proveedor | Costo Anual | vs Twilio | Ahorro |
|-----------|-------------|-----------|--------|
| Baileys | $60-120 | $360 | **$240-300** (70-80%) |
| Gupshup | $216 | $360 | **$144** (40%) |
| 360Dialog | $288 | $360 | **$72** (20%) |

**RECOMENDACIÓN: GUPSHUP**
- Balance perfecto entre costo y confiabilidad
- Oficial (sin riesgo de ban)
- $144 de ahorro anual
- API simple

---

**Conclusión:** Usa **Gupshup** para producción económica y confiable, o **Baileys** solo para testing con precaución.
