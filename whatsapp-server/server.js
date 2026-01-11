// ============================================================================
// SERVIDOR WHATSAPP PARA CANTITITA
// Basado en whatsapp-web.js
// Costo: $0 GRATIS
// ⚠️ NO OFICIAL - Solo usar con número secundario
// ============================================================================

const { Client, LocalAuth } = require('whatsapp-web.js');
const express = require('express');
const qrcode = require('qrcode-terminal');

const app = express();
app.use(express.json());

// ============================================================================
// CONFIGURACIÓN DEL CLIENTE WHATSAPP
// ============================================================================

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

// ============================================================================
// EVENTOS DEL CLIENTE
// ============================================================================

// Evento: QR Code generado
client.on('qr', (qr) => {
    console.log('\n📱 ============================================');
    console.log('   ESCANEA ESTE QR CON WHATSAPP (NÚMERO SECUNDARIO)');
    console.log('============================================\n');
    qrcode.generate(qr, { small: true });
    console.log('\nPasos:');
    console.log('1. Abre WhatsApp en tu teléfono SECUNDARIO');
    console.log('2. Ve a: Configuración → Dispositivos vinculados');
    console.log('3. Toca "Vincular dispositivo"');
    console.log('4. Escanea el QR de arriba');
    console.log('\n⚠️  IMPORTANTE: Usa SOLO número secundario, NO el principal\n');
    
    lastQR = qr;
});

// Evento: Cliente listo
client.on('ready', () => {
    console.log('\n✅ ============================================');
    console.log('   WHATSAPP CONECTADO Y LISTO!');
    console.log('============================================\n');
    console.log('📡 Servidor escuchando en http://localhost:3000');
    console.log('🔐 Sesión guardada, no necesitarás escanear QR nuevamente\n');
    
    clientReady = true;
    lastQR = null;
});

// Evento: Autenticación exitosa
client.on('authenticated', () => {
    console.log('🔐 Autenticación exitosa - Sesión guardada');
});

// Evento: Autenticación fallida
client.on('auth_failure', (message) => {
    console.error('❌ Fallo de autenticación:', message);
    clientReady = false;
});

// Evento: Desconexión
client.on('disconnected', (reason) => {
    console.log('❌ WhatsApp desconectado:', reason);
    console.log('⚠️  Intentando reconectar...');
    clientReady = false;
});

// Evento: Mensaje recibido (opcional - para logs)
client.on('message', (message) => {
    console.log(`📩 Mensaje recibido de ${message.from}: ${message.body.substring(0, 50)}...`);
});

// Iniciar cliente
console.log('🚀 Iniciando servidor WhatsApp...');
client.initialize();

// ============================================================================
// TEMPLATES DE MENSAJES
// ============================================================================

const templates = {
    'saldo_bajo': (params) => {
        return `⚠️ *ALERTA: Saldo Bajo*

Tarjeta: ${params.tarjeta || 'N/A'}
Saldo actual: Gs. ${params.saldo || '0'}

Por favor, recargue su tarjeta lo antes posible para continuar utilizando el servicio.

_Cantina Tita_`;
    },
    
    'recarga_exitosa': (params) => {
        return `✅ *Recarga Exitosa*

Monto recargado: Gs. ${params.monto || '0'}
Nuevo saldo: Gs. ${params.saldo_nuevo || '0'}
Fecha: ${params.fecha || new Date().toLocaleDateString('es-PY')}

¡Gracias por su recarga!

_Cantina Tita_`;
    },
    
    'cuenta_pendiente': (params) => {
        return `💰 *Cuenta Pendiente*

Cliente: ${params.cliente || 'N/A'}
Monto pendiente: Gs. ${params.monto || '0'}
${params.vencimiento ? `Vencimiento: ${params.vencimiento}` : ''}

Por favor, regularice su cuenta a la brevedad.

_Cantina Tita_`;
    },
    
    'compra_realizada': (params) => {
        return `🛒 *Compra Realizada*

Producto: ${params.producto || 'N/A'}
Cantidad: ${params.cantidad || '1'}
Total: Gs. ${params.total || '0'}
Saldo restante: Gs. ${params.saldo_restante || '0'}

_Cantina Tita_`;
    }
};

// ============================================================================
// API ENDPOINTS
// ============================================================================

// GET /status - Verificar estado del servicio
app.get('/status', (req, res) => {
    res.json({
        ready: clientReady,
        hasQR: lastQR !== null,
        timestamp: new Date().toISOString(),
        uptime: process.uptime()
    });
});

// GET /qr - Obtener QR code (si existe)
app.get('/qr', (req, res) => {
    if (lastQR) {
        res.json({ 
            qr: lastQR,
            message: 'Escanea este QR con WhatsApp'
        });
    } else if (clientReady) {
        res.json({ 
            message: 'Ya autenticado, no se necesita QR',
            ready: true
        });
    } else {
        res.status(503).json({ 
            error: 'QR no disponible aún, espera unos segundos'
        });
    }
});

// POST /send - Enviar mensaje de texto simple
app.post('/send', async (req, res) => {
    try {
        if (!clientReady) {
            return res.status(503).json({
                success: false,
                error: 'WhatsApp no está conectado. Verifica el estado en /status'
            });
        }

        const { phone, message } = req.body;

        if (!phone || !message) {
            return res.status(400).json({
                success: false,
                error: 'Se requieren los campos: phone y message'
            });
        }

        // Normalizar número (formato: 595981234567@c.us)
        let phoneNumber = phone.replace(/\D/g, ''); // Solo dígitos
        
        // Agregar código de país si no está
        if (!phoneNumber.startsWith('595')) {
            phoneNumber = '595' + phoneNumber;
        }
        
        if (!phoneNumber.includes('@')) {
            phoneNumber = phoneNumber + '@c.us';
        }

        console.log(`📤 Enviando mensaje a ${phoneNumber}...`);

        // Enviar mensaje
        const result = await client.sendMessage(phoneNumber, message);

        console.log(`✅ Mensaje enviado exitosamente a ${phone}`);

        res.json({
            success: true,
            messageId: result.id._serialized,
            timestamp: result.timestamp,
            to: phone
        });

    } catch (error) {
        console.error('❌ Error enviando mensaje:', error.message);
        res.status(500).json({
            success: false,
            error: error.message,
            details: 'Verifica que el número sea válido'
        });
    }
});

// POST /send-template - Enviar mensaje con template predefinido
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
                error: 'Se requieren los campos: phone y template',
                availableTemplates: Object.keys(templates)
            });
        }

        // Verificar que el template existe
        const templateFunc = templates[template];
        if (!templateFunc) {
            return res.status(400).json({
                success: false,
                error: `Template '${template}' no encontrado`,
                availableTemplates: Object.keys(templates)
            });
        }

        // Generar mensaje desde template
        const message = templateFunc(params || {});

        // Normalizar número
        let phoneNumber = phone.replace(/\D/g, '');
        if (!phoneNumber.startsWith('595')) {
            phoneNumber = '595' + phoneNumber;
        }
        if (!phoneNumber.includes('@')) {
            phoneNumber = phoneNumber + '@c.us';
        }

        console.log(`📤 Enviando template '${template}' a ${phoneNumber}...`);

        // Enviar mensaje
        const result = await client.sendMessage(phoneNumber, message);

        console.log(`✅ Template '${template}' enviado a ${phone}`);

        res.json({
            success: true,
            messageId: result.id._serialized,
            timestamp: result.timestamp,
            template: template,
            to: phone
        });

    } catch (error) {
        console.error('❌ Error enviando template:', error.message);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// POST /send-image - Enviar imagen con caption
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
                error: 'Se requieren los campos: phone e imageUrl'
            });
        }

        const { MessageMedia } = require('whatsapp-web.js');

        console.log(`📤 Descargando imagen de ${imageUrl}...`);

        // Descargar imagen
        const media = await MessageMedia.fromUrl(imageUrl);

        // Normalizar número
        let phoneNumber = phone.replace(/\D/g, '');
        if (!phoneNumber.startsWith('595')) {
            phoneNumber = '595' + phoneNumber;
        }
        if (!phoneNumber.includes('@')) {
            phoneNumber = phoneNumber + '@c.us';
        }

        console.log(`📤 Enviando imagen a ${phoneNumber}...`);

        // Enviar imagen con caption
        const result = await client.sendMessage(phoneNumber, media, {
            caption: caption || ''
        });

        console.log(`✅ Imagen enviada a ${phone}`);

        res.json({
            success: true,
            messageId: result.id._serialized,
            to: phone
        });

    } catch (error) {
        console.error('❌ Error enviando imagen:', error.message);
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
                error: 'Se requiere array de recipients con formato: [{phone, message}, ...]'
            });
        }

        console.log(`📤 Iniciando envío masivo a ${recipients.length} destinatarios...`);

        const results = [];
        let successCount = 0;
        let errorCount = 0;

        for (const [index, recipient] of recipients.entries()) {
            try {
                let phoneNumber = recipient.phone.replace(/\D/g, '');
                if (!phoneNumber.startsWith('595')) {
                    phoneNumber = '595' + phoneNumber;
                }
                if (!phoneNumber.includes('@')) {
                    phoneNumber = phoneNumber + '@c.us';
                }

                const result = await client.sendMessage(phoneNumber, recipient.message);

                results.push({
                    phone: recipient.phone,
                    success: true,
                    messageId: result.id._serialized
                });
                
                successCount++;
                console.log(`✅ [${index + 1}/${recipients.length}] Enviado a ${recipient.phone}`);

                // Delay entre mensajes (evitar detección como spam)
                // 2-3 segundos aleatorio
                const delay = 2000 + Math.random() * 1000;
                await new Promise(resolve => setTimeout(resolve, delay));

            } catch (error) {
                results.push({
                    phone: recipient.phone,
                    success: false,
                    error: error.message
                });
                
                errorCount++;
                console.error(`❌ [${index + 1}/${recipients.length}] Error enviando a ${recipient.phone}: ${error.message}`);
            }
        }

        console.log(`\n📊 Envío masivo completado: ${successCount} exitosos, ${errorCount} fallidos\n`);

        res.json({
            success: true,
            total: recipients.length,
            successCount: successCount,
            errorCount: errorCount,
            results: results
        });

    } catch (error) {
        console.error('❌ Error en envío masivo:', error.message);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// GET /health - Health check endpoint
app.get('/health', (req, res) => {
    res.json({
        status: 'ok',
        service: 'cantita-whatsapp-server',
        version: '1.0.0',
        whatsapp: clientReady ? 'connected' : 'disconnected'
    });
});

// GET /templates - Listar templates disponibles
app.get('/templates', (req, res) => {
    res.json({
        templates: Object.keys(templates),
        count: Object.keys(templates).length
    });
});

// ============================================================================
// INICIAR SERVIDOR
// ============================================================================

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
    console.log('\n🚀 ============================================');
    console.log('   SERVIDOR WHATSAPP INICIADO');
    console.log('============================================\n');
    console.log(`📡 Puerto: ${PORT}`);
    console.log(`🌐 URL base: http://localhost:${PORT}\n`);
    console.log('📚 Endpoints disponibles:');
    console.log(`   GET  http://localhost:${PORT}/status`);
    console.log(`   GET  http://localhost:${PORT}/qr`);
    console.log(`   GET  http://localhost:${PORT}/health`);
    console.log(`   GET  http://localhost:${PORT}/templates`);
    console.log(`   POST http://localhost:${PORT}/send`);
    console.log(`   POST http://localhost:${PORT}/send-template`);
    console.log(`   POST http://localhost:${PORT}/send-image`);
    console.log(`   POST http://localhost:${PORT}/send-bulk\n`);
    console.log('⏳ Esperando autenticación WhatsApp...\n');
});

// ============================================================================
// MANEJO DE ERRORES Y SEÑALES
// ============================================================================

process.on('unhandledRejection', (err) => {
    console.error('❌ Error no manejado:', err);
});

process.on('SIGINT', () => {
    console.log('\n\n👋 Cerrando servidor WhatsApp...');
    client.destroy().then(() => {
        console.log('✅ Cliente WhatsApp cerrado');
        process.exit(0);
    });
});

process.on('SIGTERM', () => {
    console.log('\n\n👋 Cerrando servidor WhatsApp...');
    client.destroy().then(() => {
        console.log('✅ Cliente WhatsApp cerrado');
        process.exit(0);
    });
});
