# 🆓 OPCIONES WHATSAPP AUTOMATIZADAS COSTO $0
## Soluciones Gratuitas para Notificaciones Automáticas

---

## ⚠️ ADVERTENCIA CRÍTICA

**TODAS las opciones $0 automatizadas son NO OFICIALES**

- ❌ Usan ingeniería inversa de WhatsApp Web
- ❌ Violan Términos de Servicio de WhatsApp
- ❌ **RIESGO DE BAN PERMANENTE**
- ⚠️ Solo usar con **número secundario de prueba**
- ⚠️ **NO usar número principal de negocio**

---

## 🎯 OPCIONES COSTO $0 + AUTOMATIZADAS

### **1. whatsapp-web.js** ⭐⭐⭐⭐⭐

**La más popular y estable**

#### **Características:**
- ✅ **Más popular** (13k+ stars GitHub)
- ✅ Muy estable y mantenida
- ✅ Documentación excelente
- ✅ Comunidad grande
- ✅ Soporta multimedia
- ✅ Webhooks y eventos
- ❌ NO OFICIAL - Riesgo ban
- ❌ Requiere servidor Node.js

#### **Instalación:**
```bash
# Crear carpeta para servidor WhatsApp
mkdir whatsapp-server
cd whatsapp-server

# Inicializar proyecto Node.js
npm init -y

# Instalar dependencias
npm install whatsapp-web.js express qrcode-terminal
```

#### **Servidor Node.js Completo:**
```javascript
// whatsapp-server/server.js

const { Client, LocalAuth } = require('whatsapp-web.js');
const express = require('express');
const qrcode = require('qrcode-terminal');

const app = express();
app.use(express.json());

// Configurar cliente WhatsApp con autenticación persistente
const client = new Client({
    authStrategy: new LocalAuth({
        clientId: "cantita-whatsapp",
        dataPath: "./whatsapp-session"
    }),
    puppeteer: {
        headless: true,
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-accelerated-2d-canvas',
            '--no-first-run',
            '--no-zygote',
            '--disable-gpu'
        ]
    }
});

// Estado del cliente
let clientReady = false;
let lastQR = null;

// Evento: QR Code generado
client.on('qr', (qr) => {
    console.log('📱 Escanea este QR con WhatsApp:');
    qrcode.generate(qr, { small: true });
    lastQR = qr;
});

// Evento: Cliente listo
client.on('ready', () => {
    console.log('✅ WhatsApp conectado y listo!');
    clientReady = true;
    lastQR = null;
});

// Evento: Autenticación exitosa
client.on('authenticated', () => {
    console.log('🔐 Autenticación exitosa');
});

// Evento: Desconexión
client.on('disconnected', (reason) => {
    console.log('❌ WhatsApp desconectado:', reason);
    clientReady = false;
});

// Iniciar cliente
client.initialize();

// ============================================================================
// API ENDPOINTS
// ============================================================================

// GET /status - Verificar estado
app.get('/status', (req, res) => {
    res.json({
        ready: clientReady,
        hasQR: lastQR !== null,
        timestamp: new Date().toISOString()
    });
});

// GET /qr - Obtener QR code (si existe)
app.get('/qr', (req, res) => {
    if (lastQR) {
        res.json({ qr: lastQR });
    } else if (clientReady) {
        res.json({ message: 'Ya autenticado, no se necesita QR' });
    } else {
        res.status(503).json({ error: 'QR no disponible aún' });
    }
});

// POST /send - Enviar mensaje de texto
app.post('/send', async (req, res) => {
    try {
        if (!clientReady) {
            return res.status(503).json({
                success: false,
                error: 'WhatsApp no está conectado'
            });
        }

        const { phone, message } = req.body;

        if (!phone || !message) {
            return res.status(400).json({
                success: false,
                error: 'Se requieren phone y message'
            });
        }

        // Normalizar número (formato: 595981234567@c.us)
        let phoneNumber = phone.replace(/\D/g, ''); // Solo dígitos
        if (!phoneNumber.includes('@')) {
            phoneNumber = phoneNumber + '@c.us';
        }

        // Enviar mensaje
        const result = await client.sendMessage(phoneNumber, message);

        console.log(`✅ Mensaje enviado a ${phone}`);

        res.json({
            success: true,
            messageId: result.id._serialized,
            timestamp: result.timestamp
        });

    } catch (error) {
        console.error('❌ Error enviando mensaje:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// POST /send-image - Enviar imagen
app.post('/send-image', async (req, res) => {
    try {
        if (!clientReady) {
            return res.status(503).json({
                success: false,
                error: 'WhatsApp no está conectado'
            });
        }

        const { phone, imageUrl, caption } = req.body;

        if (!phone || !imageUrl) {
            return res.status(400).json({
                success: false,
                error: 'Se requieren phone e imageUrl'
            });
        }

        const { MessageMedia } = require('whatsapp-web.js');

        // Descargar imagen
        const media = await MessageMedia.fromUrl(imageUrl);

        let phoneNumber = phone.replace(/\D/g, '');
        if (!phoneNumber.includes('@')) {
            phoneNumber = phoneNumber + '@c.us';
        }

        // Enviar imagen con caption
        const result = await client.sendMessage(phoneNumber, media, {
            caption: caption || ''
        });

        console.log(`✅ Imagen enviada a ${phone}`);

        res.json({
            success: true,
            messageId: result.id._serialized
        });

    } catch (error) {
        console.error('❌ Error enviando imagen:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// POST /send-template - Enviar mensaje formateado
app.post('/send-template', async (req, res) => {
    try {
        if (!clientReady) {
            return res.status(503).json({
                success: false,
                error: 'WhatsApp no está conectado'
            });
        }

        const { phone, template, params } = req.body;

        if (!phone || !template) {
            return res.status(400).json({
                success: false,
                error: 'Se requieren phone y template'
            });
        }

        // Templates predefinidos
        const templates = {
            'saldo_bajo': (p) => `⚠️ *ALERTA: Saldo Bajo*\n\nTarjeta: ${p.tarjeta}\nSaldo actual: Gs. ${p.saldo}\n\nPor favor, recargue su tarjeta lo antes posible.\n\n_CantiTita_`,
            
            'recarga_exitosa': (p) => `✅ *Recarga Exitosa*\n\nMonto: Gs. ${p.monto}\nNuevo saldo: Gs. ${p.saldo_nuevo}\nFecha: ${p.fecha}\n\n¡Gracias por su recarga!\n\n_CantiTita_`,
            
            'cuenta_pendiente': (p) => `💰 *Cuenta Pendiente*\n\nCliente: ${p.cliente}\nMonto pendiente: Gs. ${p.monto}\nVencimiento: ${p.vencimiento}\n\nPor favor, regularice su cuenta.\n\n_CantiTita_`
        };

        const templateFunc = templates[template];
        if (!templateFunc) {
            return res.status(400).json({
                success: false,
                error: `Template '${template}' no encontrado`
            });
        }

        const message = templateFunc(params || {});

        let phoneNumber = phone.replace(/\D/g, '');
        if (!phoneNumber.includes('@')) {
            phoneNumber = phoneNumber + '@c.us';
        }

        const result = await client.sendMessage(phoneNumber, message);

        console.log(`✅ Template '${template}' enviado a ${phone}`);

        res.json({
            success: true,
            messageId: result.id._serialized,
            template: template
        });

    } catch (error) {
        console.error('❌ Error enviando template:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// POST /send-bulk - Enviar a múltiples destinatarios
app.post('/send-bulk', async (req, res) => {
    try {
        if (!clientReady) {
            return res.status(503).json({
                success: false,
                error: 'WhatsApp no está conectado'
            });
        }

        const { recipients } = req.body; // Array de {phone, message}

        if (!recipients || !Array.isArray(recipients)) {
            return res.status(400).json({
                success: false,
                error: 'Se requiere array de recipients'
            });
        }

        const results = [];

        for (const recipient of recipients) {
            try {
                let phoneNumber = recipient.phone.replace(/\D/g, '');
                if (!phoneNumber.includes('@')) {
                    phoneNumber = phoneNumber + '@c.us';
                }

                const result = await client.sendMessage(phoneNumber, recipient.message);

                results.push({
                    phone: recipient.phone,
                    success: true,
                    messageId: result.id._serialized
                });

                // Delay entre mensajes (evitar detección)
                await new Promise(resolve => setTimeout(resolve, 2000));

            } catch (error) {
                results.push({
                    phone: recipient.phone,
                    success: false,
                    error: error.message
                });
            }
        }

        console.log(`✅ Envío masivo completado: ${results.length} mensajes`);

        res.json({
            success: true,
            total: recipients.length,
            results: results
        });

    } catch (error) {
        console.error('❌ Error en envío masivo:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// Iniciar servidor
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`🚀 Servidor WhatsApp escuchando en puerto ${PORT}`);
    console.log(`📡 Endpoints disponibles:`);
    console.log(`   GET  http://localhost:${PORT}/status`);
    console.log(`   GET  http://localhost:${PORT}/qr`);
    console.log(`   POST http://localhost:${PORT}/send`);
    console.log(`   POST http://localhost:${PORT}/send-image`);
    console.log(`   POST http://localhost:${PORT}/send-template`);
    console.log(`   POST http://localhost:${PORT}/send-bulk`);
});

// Manejo de errores
process.on('unhandledRejection', (err) => {
    console.error('❌ Error no manejado:', err);
});
```

#### **Package.json completo:**
```json
{
  "name": "cantita-whatsapp-server",
  "version": "1.0.0",
  "description": "WhatsApp server for CantiTita notifications",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js"
  },
  "keywords": ["whatsapp", "notifications"],
  "author": "CantiTita",
  "license": "MIT",
  "dependencies": {
    "whatsapp-web.js": "^1.23.0",
    "express": "^4.18.2",
    "qrcode-terminal": "^0.12.0"
  },
  "devDependencies": {
    "nodemon": "^3.0.2"
  }
}
```

#### **Integración Django:**
```python
# gestion/whatsapp_client.py

import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class WhatsAppWebClient:
    """
    Cliente para servidor whatsapp-web.js
    
    Costo: $0 GRATIS
    Riesgo: ⚠️ BAN (solo usar número secundario)
    """
    
    def __init__(self):
        self.base_url = getattr(settings, 'WHATSAPP_SERVER_URL', 'http://localhost:3000')
    
    def check_status(self):
        """Verificar si WhatsApp está conectado"""
        try:
            response = requests.get(f"{self.base_url}/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get('ready', False)
            return False
        except Exception as e:
            logger.error(f"Error verificando estado WhatsApp: {e}")
            return False
    
    def send_message(self, phone, message):
        """
        Enviar mensaje de texto
        
        Args:
            phone (str): Número con formato +595981234567
            message (str): Texto del mensaje
        
        Returns:
            bool: True si envío exitoso
        """
        try:
            # Verificar conexión
            if not self.check_status():
                logger.error("WhatsApp no está conectado")
                return False
            
            # Normalizar teléfono
            phone_clean = phone.replace('+', '').replace(' ', '').replace('-', '')
            
            # Enviar mensaje
            response = requests.post(
                f"{self.base_url}/send",
                json={
                    'phone': phone_clean,
                    'message': message
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    logger.info(f"✅ WhatsApp enviado a {phone}")
                    return True
            
            logger.error(f"Error enviando WhatsApp: {response.text}")
            return False
            
        except Exception as e:
            logger.error(f"Excepción enviando WhatsApp: {e}")
            return False
    
    def send_template(self, phone, template_name, params):
        """
        Enviar mensaje con template predefinido
        
        Args:
            phone (str): Número de teléfono
            template_name (str): 'saldo_bajo', 'recarga_exitosa', 'cuenta_pendiente'
            params (dict): Parámetros del template
        
        Returns:
            bool: True si envío exitoso
        """
        try:
            if not self.check_status():
                logger.error("WhatsApp no está conectado")
                return False
            
            phone_clean = phone.replace('+', '').replace(' ', '').replace('-', '')
            
            response = requests.post(
                f"{self.base_url}/send-template",
                json={
                    'phone': phone_clean,
                    'template': template_name,
                    'params': params
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    logger.info(f"✅ Template '{template_name}' enviado a {phone}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error enviando template: {e}")
            return False
    
    def send_bulk(self, recipients):
        """
        Enviar múltiples mensajes
        
        Args:
            recipients (list): Lista de dicts con 'phone' y 'message'
        
        Returns:
            dict: Resultados del envío
        """
        try:
            if not self.check_status():
                logger.error("WhatsApp no está conectado")
                return {'success': False, 'error': 'WhatsApp no conectado'}
            
            response = requests.post(
                f"{self.base_url}/send-bulk",
                json={'recipients': recipients},
                timeout=len(recipients) * 5  # 5 seg por mensaje
            )
            
            if response.status_code == 200:
                return response.json()
            
            return {'success': False, 'error': response.text}
            
        except Exception as e:
            logger.error(f"Error en envío masivo: {e}")
            return {'success': False, 'error': str(e)}


# Instancia global
whatsapp_client = WhatsAppWebClient()


def enviar_whatsapp_gratis(telefono, mensaje):
    """
    Enviar WhatsApp usando servidor local (GRATIS)
    
    ⚠️ SOLO USAR CON NÚMERO SECUNDARIO
    Costo: $0
    Riesgo: BAN permanente
    """
    return whatsapp_client.send_message(telefono, mensaje)


def notificar_saldo_bajo_whatsapp_gratis(tarjeta):
    """
    Notificar saldo bajo usando WhatsApp gratis
    """
    try:
        responsable = tarjeta.cliente.responsable
        
        if not responsable.telefono:
            return False
        
        success = whatsapp_client.send_template(
            phone=responsable.telefono,
            template_name='saldo_bajo',
            params={
                'tarjeta': tarjeta.numero_tarjeta,
                'saldo': f"{tarjeta.saldo:,}"
            }
        )
        
        return success
        
    except Exception as e:
        logger.error(f"Error notificando saldo bajo: {e}")
        return False
```

#### **Configuración Django settings.py:**
```python
# settings.py

# WhatsApp Server (whatsapp-web.js)
WHATSAPP_SERVER_URL = 'http://localhost:3000'  # Cambiar a IP servidor si remoto
```

#### **Iniciar el servidor:**
```bash
# En carpeta whatsapp-server/
npm start

# O con auto-reload:
npm run dev
```

#### **Primera vez - Escanear QR:**
```bash
# Ejecutar servidor
node server.js

# Verás un QR en consola
# Abre WhatsApp en tu teléfono
# Ve a: Configuración → Dispositivos vinculados → Vincular dispositivo
# Escanea el QR

# ✅ Ahora el servidor queda autenticado permanentemente
```

#### **Ventajas whatsapp-web.js:**
- ✅ **GRATIS** 100%
- ✅ Muy estable (13k+ stars, mantenido activamente)
- ✅ Autenticación persistente (solo escanear QR 1 vez)
- ✅ Soporta imágenes, PDFs, ubicación
- ✅ Eventos en tiempo real
- ✅ Comunidad grande (muchos ejemplos)
- ✅ Templates personalizados
- ✅ Envío masivo con delays

#### **Desventajas:**
- ❌ **NO OFICIAL** - Riesgo ban
- ❌ Requiere servidor Node.js corriendo 24/7
- ❌ Consume ~300MB RAM
- ❌ Si cierras servidor, pierdes sesión

#### **Mitigación de riesgos:**
- ⚠️ **Solo usar número secundario/de prueba**
- ⚠️ Limitar a **<50 mensajes/día**
- ⚠️ Delays de 2-3 seg entre mensajes
- ⚠️ No enviar spam
- ⚠️ Monitorear conexión

---

### **2. Venom-bot** ⭐⭐⭐⭐

**Alternativa con más features**

#### **Características:**
- ✅ Similar a whatsapp-web.js pero más features
- ✅ Interfaz más limpia
- ✅ Mejor manejo de sesiones
- ✅ Soporte oficial para Docker
- ❌ NO OFICIAL - Riesgo ban

#### **Instalación:**
```bash
npm install venom-bot express
```

#### **Servidor básico:**
```javascript
// server-venom.js

const venom = require('venom-bot');
const express = require('express');

const app = express();
app.use(express.json());

let client = null;

// Crear sesión
venom
    .create({
        session: 'cantita-session',
        headless: true,
        useChrome: false,
        logQR: true
    })
    .then((clientInstance) => {
        client = clientInstance;
        console.log('✅ Venom-bot listo!');
    })
    .catch((error) => {
        console.error('❌ Error:', error);
    });

// POST /send
app.post('/send', async (req, res) => {
    try {
        if (!client) {
            return res.status(503).json({ error: 'Cliente no listo' });
        }

        const { phone, message } = req.body;
        
        // Formato: 595981234567@c.us
        const phoneNumber = phone.replace(/\D/g, '') + '@c.us';
        
        await client.sendText(phoneNumber, message);
        
        res.json({ success: true });
        
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.listen(3000, () => {
    console.log('🚀 Servidor Venom-bot en puerto 3000');
});
```

#### **Ventajas Venom-bot:**
- ✅ API más completa
- ✅ Mejor documentación que Baileys
- ✅ Docker support oficial

#### **Desventajas:**
- ❌ Menos popular que whatsapp-web.js
- ❌ Mismo riesgo de ban

---

### **3. WPPConnect** ⭐⭐⭐⭐

**Fork mejorado de whatsapp-web.js**

#### **Características:**
- ✅ Fork de whatsapp-web.js con mejoras
- ✅ Multi-sesión (múltiples números)
- ✅ Dashboard web incluido
- ✅ Webhooks avanzados
- ❌ NO OFICIAL - Riesgo ban

#### **Instalación:**
```bash
npm install @wppconnect-team/wppconnect express
```

#### **Servidor:**
```javascript
// server-wppconnect.js

const wppconnect = require('@wppconnect-team/wppconnect');
const express = require('express');

const app = express();
app.use(express.json());

let client = null;

// Crear cliente
wppconnect
    .create({
        session: 'cantita',
        catchQR: (base64Qr, asciiQR) => {
            console.log('QR Code:');
            console.log(asciiQR);
        },
        statusFind: (statusSession, session) => {
            console.log('Status:', statusSession);
        }
    })
    .then((clientInstance) => {
        client = clientInstance;
        console.log('✅ WPPConnect listo!');
    })
    .catch((error) => {
        console.error('❌ Error:', error);
    });

// POST /send
app.post('/send', async (req, res) => {
    try {
        if (!client) {
            return res.status(503).json({ error: 'Cliente no listo' });
        }

        const { phone, message } = req.body;
        
        await client.sendText(phone + '@c.us', message);
        
        res.json({ success: true });
        
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.listen(3000, () => {
    console.log('🚀 Servidor WPPConnect en puerto 3000');
});
```

---

### **4. Maytapi Free Tier** 💎

**1000 mensajes/mes GRATIS**

#### **Características:**
- ✅ **1000 mensajes/mes GRATIS**
- ✅ API REST (no requiere Node.js)
- ✅ Setup rápido
- ⚠️ Modo "WhatsApp Web" (no oficial)
- ⚠️ Limitado a 1000 msg/mes

#### **Código Python directo:**
```python
# gestion/whatsapp_maytapi_free.py

import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def enviar_whatsapp_maytapi_free(telefono, mensaje):
    """
    Enviar WhatsApp usando Maytapi Free Tier
    
    ✅ 1000 mensajes/mes GRATIS
    ⚠️ NO OFICIAL - Riesgo ban
    ⚠️ Solo número secundario
    
    Setup:
    1. Registrarse en https://maytapi.com
    2. Crear producto (Free tier)
    3. Escanear QR con WhatsApp
    4. Obtener Product ID y Phone ID
    """
    try:
        url = f"https://api.maytapi.com/api/{settings.MAYTAPI_PRODUCT_ID}/{settings.MAYTAPI_PHONE_ID}/sendMessage"
        
        headers = {
            "x-maytapi-key": settings.MAYTAPI_API_KEY,
            "Content-Type": "application/json"
        }
        
        payload = {
            "to_number": telefono.replace('+', '').replace(' ', ''),
            "type": "text",
            "message": mensaje
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            logger.info(f"✅ WhatsApp Maytapi Free enviado a {telefono}")
            return True
        
        logger.error(f"❌ Error Maytapi: {response.status_code} - {response.text}")
        return False
        
    except Exception as e:
        logger.error(f"❌ Excepción Maytapi: {e}")
        return False
```

#### **Configuración .env:**
```ini
# Maytapi Free (1000 msg/mes gratis)
MAYTAPI_PRODUCT_ID=tu_product_id
MAYTAPI_PHONE_ID=tu_phone_id
MAYTAPI_API_KEY=tu_api_key

# Límite: 1000 mensajes/mes
# Costo adicional: $0.001/mensaje después de 1000
```

#### **Ventajas Maytapi Free:**
- ✅ **1000 mensajes/mes gratis**
- ✅ API REST (no Node.js)
- ✅ Setup fácil (escanear QR en dashboard)
- ✅ Webhooks incluidos

#### **Desventajas:**
- ⚠️ Límite 1000 msg/mes
- ⚠️ NO OFICIAL - Riesgo ban
- ⚠️ Después de 1000 cobra $0.001/msg

---

### **5. Green API Free Plan** 🌿

**1000 mensajes/mes GRATIS**

#### **Características:**
- ✅ 1000 mensajes/mes gratis
- ✅ API REST
- ✅ Dashboard completo
- ⚠️ NO OFICIAL

#### **Código Python:**
```python
# gestion/whatsapp_greenapi.py

import requests
from django.conf import settings

def enviar_whatsapp_greenapi(telefono, mensaje):
    """
    Green API - 1000 msg/mes gratis
    
    Setup: https://green-api.com
    """
    try:
        url = f"https://api.green-api.com/waInstance{settings.GREENAPI_INSTANCE_ID}/sendMessage/{settings.GREENAPI_TOKEN}"
        
        payload = {
            "chatId": telefono.replace('+', '').replace(' ', '') + "@c.us",
            "message": mensaje
        }
        
        response = requests.post(url, json=payload, timeout=30)
        
        return response.status_code == 200
        
    except Exception as e:
        logger.error(f"Error Green API: {e}")
        return False
```

---

## 📊 COMPARACIÓN OPCIONES $0

| Opción | Costo | Límite/mes | Setup | Riesgo Ban | Python | Node.js |
|--------|-------|------------|-------|------------|--------|---------|
| **whatsapp-web.js** | $0 | ∞ | QR 1 vez | ⚠️ Alto | ✅ | ✅ |
| **Venom-bot** | $0 | ∞ | QR 1 vez | ⚠️ Alto | ✅ | ✅ |
| **WPPConnect** | $0 | ∞ | QR 1 vez | ⚠️ Alto | ✅ | ✅ |
| **Maytapi Free** | $0 | 1000 | QR web | ⚠️ Alto | ✅ | ❌ |
| **Green API Free** | $0 | 1000 | QR web | ⚠️ Alto | ✅ | ❌ |

---

## 🎯 RECOMENDACIÓN FINAL (COSTO $0)

### **🥇 MEJOR: whatsapp-web.js**

**¿Por qué?**
1. ✅ **Más estable** (13k stars, muy mantenido)
2. ✅ **Sin límites** de mensajes
3. ✅ **Documentación excelente**
4. ✅ **Comunidad grande**
5. ✅ Templates personalizados
6. ✅ Autenticación persistente

**Implementación en CantiTita:**

```bash
# 1. Crear servidor WhatsApp
mkdir whatsapp-server
cd whatsapp-server
npm init -y
npm install whatsapp-web.js express qrcode-terminal

# 2. Copiar server.js (código arriba)
# 3. Iniciar servidor
node server.js

# 4. Escanear QR con NÚMERO SECUNDARIO
# 5. Dejar corriendo 24/7
```

**Uso desde Django:**
```python
# gestion/notificaciones.py

from gestion.whatsapp_client import whatsapp_client

def notificar_saldo_bajo(tarjeta, canales=['email']):
    resultados = {}
    
    # Email
    if 'email' in canales:
        resultados['email'] = enviar_email_saldo_bajo(tarjeta)
    
    # WhatsApp GRATIS
    if 'whatsapp_gratis' in canales:
        responsable = tarjeta.cliente.responsable
        if responsable.telefono:
            success = whatsapp_client.send_template(
                phone=responsable.telefono,
                template_name='saldo_bajo',
                params={
                    'tarjeta': tarjeta.numero_tarjeta,
                    'saldo': f"{tarjeta.saldo:,}"
                }
            )
            resultados['whatsapp_gratis'] = success
    
    return resultados
```

---

### **🥈 ALTERNATIVA: Maytapi Free (si no quieres Node.js)**

**¿Por qué?**
- ✅ API REST pura (Python requests)
- ✅ No requiere servidor Node.js
- ✅ 1000 msg/mes gratis (suficiente para testing)
- ✅ Setup más rápido

**Límite:** 33 mensajes/día promedio (1000/mes)

---

## ⚙️ CONFIGURACIÓN COMPLETA DJANGO

### **settings.py:**
```python
# settings.py

# ============================================================================
# WHATSAPP - CONFIGURACIÓN
# ============================================================================

# Opción 1: whatsapp-web.js (RECOMENDADO - sin límites)
WHATSAPP_PROVIDER = 'whatsapp-web-js'  # gratis, ilimitado
WHATSAPP_SERVER_URL = 'http://localhost:3000'

# Opción 2: Maytapi Free (Alternativa - 1000 msg/mes)
# WHATSAPP_PROVIDER = 'maytapi-free'
# MAYTAPI_PRODUCT_ID = 'tu_product_id'
# MAYTAPI_PHONE_ID = 'tu_phone_id'
# MAYTAPI_API_KEY = 'tu_api_key'

# Número de contacto CantiTita (para links wa.me)
CANTITA_WHATSAPP_CONTACTO = '+595981234567'

# ⚠️ IMPORTANTE: Solo usar número SECUNDARIO para automatización
# NO usar número principal de negocio
```

### **notificaciones.py actualizado:**
```python
# gestion/notificaciones.py

from django.conf import settings
from gestion.whatsapp_client import whatsapp_client
from gestion.whatsapp_maytapi_free import enviar_whatsapp_maytapi_free
import logging

logger = logging.getLogger(__name__)

def enviar_whatsapp_auto_gratis(telefono, mensaje):
    """
    Router para WhatsApp gratis automatizado
    
    Selecciona proveedor según configuración
    """
    provider = getattr(settings, 'WHATSAPP_PROVIDER', 'whatsapp-web-js')
    
    if provider == 'whatsapp-web-js':
        return whatsapp_client.send_message(telefono, mensaje)
    
    elif provider == 'maytapi-free':
        return enviar_whatsapp_maytapi_free(telefono, mensaje)
    
    else:
        logger.warning(f"Proveedor WhatsApp no configurado: {provider}")
        return False


def notificar_saldo_bajo(tarjeta, canales=['email']):
    """
    Notificar saldo bajo - Multi-canal
    
    Canales disponibles:
    - 'email': Email SMTP (gratis)
    - 'whatsapp_gratis': WhatsApp automatizado gratis (riesgo ban)
    - 'whatsapp_link': Email con botón WhatsApp (gratis, sin riesgo)
    """
    resultados = {}
    cliente = tarjeta.cliente
    responsable = cliente.responsable
    
    # Email
    if 'email' in canales and responsable.email:
        exito = enviar_email_saldo_bajo(tarjeta)
        resultados['email'] = exito
    
    # WhatsApp automatizado gratis (⚠️ riesgo ban)
    if 'whatsapp_gratis' in canales and responsable.telefono:
        mensaje = f"⚠️ ALERTA: Saldo bajo en tarjeta {tarjeta.numero_tarjeta}\n\nSaldo actual: Gs. {tarjeta.saldo:,}\n\nPor favor, recargue su tarjeta.\n\n_CantiTita_"
        exito = enviar_whatsapp_auto_gratis(responsable.telefono, mensaje)
        resultados['whatsapp_gratis'] = exito
    
    # WhatsApp link (email con botón - sin riesgo)
    if 'whatsapp_link' in canales and responsable.email:
        exito = enviar_email_con_boton_whatsapp(
            destinatario=responsable.email,
            asunto="⚠️ Saldo Bajo - CantiTita",
            mensaje=f"Saldo actual: Gs. {tarjeta.saldo:,}"
        )
        resultados['whatsapp_link'] = exito
    
    return resultados
```

---

## 🛡️ ESTRATEGIA SEGURA (SIN RIESGO)

### **Usar NÚMERO SECUNDARIO solo para automatización:**

```python
# settings.py

# Número principal (solo manual, sin riesgo)
CANTITA_WHATSAPP_PRINCIPAL = '+595981234567'

# Número secundario (automatización, riesgo ban)
CANTITA_WHATSAPP_AUTOMATICO = '+595987654321'  # Chip barato

# Si se banea el secundario:
# 1. Comprar nuevo chip ($5-10)
# 2. Actualizar CANTITA_WHATSAPP_AUTOMATICO
# 3. Re-escanear QR
# 4. Número principal sigue seguro
```

### **Límites seguros:**
```python
# Límites para evitar detección

MAX_MENSAJES_DIA = 50  # Máximo diario
MAX_MENSAJES_HORA = 10  # Máximo por hora
DELAY_ENTRE_MENSAJES = 3  # Segundos entre mensajes

# Horario permitido
HORARIO_ENVIO_INICIO = 8  # 8 AM
HORARIO_ENVIO_FIN = 20  # 8 PM
```

---

## 📋 INSTALACIÓN PASO A PASO

### **Setup completo whatsapp-web.js:**

```bash
# 1. Crear directorio servidor
mkdir whatsapp-server
cd whatsapp-server

# 2. Inicializar Node.js
npm init -y

# 3. Instalar dependencias
npm install whatsapp-web.js express qrcode-terminal

# 4. Crear server.js
# (copiar código completo de arriba)

# 5. Iniciar servidor
node server.js

# 6. Escanear QR
# - Abre WhatsApp en teléfono SECUNDARIO
# - Ve a: Configuración → Dispositivos vinculados
# - Vincular dispositivo
# - Escanea QR en consola

# 7. ✅ Listo! Servidor queda autenticado
```

### **Mantener servidor corriendo (PM2):**

```bash
# Instalar PM2 globalmente
npm install -g pm2

# Iniciar servidor con PM2
pm2 start server.js --name whatsapp-cantita

# Ver logs
pm2 logs whatsapp-cantita

# Ver estado
pm2 status

# Auto-inicio al reiniciar PC
pm2 startup
pm2 save
```

---

## ✅ CONCLUSIÓN

### **Para CantiTita con presupuesto $0:**

**🥇 RECOMENDADO:**
```
Servidor: whatsapp-web.js (Node.js)
Número: SECUNDARIO ($5 chip)
Límite: <50 mensajes/día
Costo: $0/mes
Riesgo: Solo número secundario

✅ Automatizado 100%
✅ Sin límites técnicos
✅ Templates personalizados
⚠️ Riesgo ban aceptable (número secundario)
```

**Código Django ya listo arriba** ⬆️

¿Quieres que te ayude a instalarlo?
