# WhatsApp Server - CantiTita

Servidor Node.js para envío de mensajes WhatsApp usando whatsapp-web.js

## 🚀 Instalación

```bash
npm install
```

## ▶️ Iniciar servidor

```bash
# Modo desarrollo (con auto-reload)
npm run dev

# Modo producción
npm start
```

## 📱 Primera vez - Autenticación

1. Ejecuta: `npm start`
2. Verás un QR en la consola
3. Abre WhatsApp en tu teléfono SECUNDARIO (NO principal)
4. Ve a: Configuración → Dispositivos vinculados
5. Escanea el QR
6. ✅ Listo! La sesión se guarda automáticamente

## 🔧 Mantener servidor corriendo (24/7)

### Con PM2 (Recomendado)

```bash
# Instalar PM2
npm install -g pm2

# Iniciar
pm2 start server.js --name whatsapp-cantita

# Ver logs
pm2 logs whatsapp-cantita

# Estado
pm2 status

# Auto-inicio al reiniciar PC
pm2 startup
pm2 save
```

## 📡 Endpoints

### GET /status
Verificar estado del servidor

```bash
curl http://localhost:3000/status
```

### GET /qr
Obtener QR code (si no autenticado)

```bash
curl http://localhost:3000/qr
```

### POST /send
Enviar mensaje simple

```bash
curl -X POST http://localhost:3000/send \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+595981234567",
    "message": "Hola desde CantiTita"
  }'
```

### POST /send-template
Enviar con template predefinido

```bash
curl -X POST http://localhost:3000/send-template \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+595981234567",
    "template": "saldo_bajo",
    "params": {
      "tarjeta": "12345",
      "saldo": "5,000"
    }
  }'
```

### POST /send-image
Enviar imagen con caption

```bash
curl -X POST http://localhost:3000/send-image \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+595981234567",
    "imageUrl": "https://ejemplo.com/imagen.jpg",
    "caption": "Descripción de la imagen"
  }'
```

### POST /send-bulk
Envío masivo

```bash
curl -X POST http://localhost:3000/send-bulk \
  -H "Content-Type: application/json" \
  -d '{
    "recipients": [
      {"phone": "+595981111111", "message": "Mensaje 1"},
      {"phone": "+595982222222", "message": "Mensaje 2"}
    ]
  }'
```

### GET /templates
Listar templates disponibles

```bash
curl http://localhost:3000/templates
```

## 📋 Templates disponibles

- `saldo_bajo`: Alerta de saldo bajo en tarjeta
- `recarga_exitosa`: Confirmación de recarga
- `cuenta_pendiente`: Recordatorio de cuenta pendiente
- `compra_realizada`: Confirmación de compra

## ⚠️ ADVERTENCIAS

- **NO OFICIAL**: Usa ingeniería inversa de WhatsApp Web
- **Solo usar con número SECUNDARIO**: NO usar número principal de negocio
- **Límite recomendado**: <50 mensajes/día
- **Riesgo de BAN**: El número usado puede ser baneado por WhatsApp
- **Consumo**: ~300MB RAM

## 💰 Costo

- Servidor Node.js: **$0 GRATIS**
- Mensajes WhatsApp: **$0 GRATIS**
- Total: **$0/mes**

## 🔐 Seguridad

- La sesión se guarda en `whatsapp-session/`
- **NO compartir** esta carpeta (contiene credenciales)
- Incluida en `.gitignore` automáticamente

## 📦 Dependencias

- `whatsapp-web.js`: Cliente WhatsApp Web
- `express`: Servidor HTTP
- `qrcode-terminal`: Mostrar QR en consola

## 🆘 Soporte

Ver logs en tiempo real:
```bash
pm2 logs whatsapp-cantita
```

Reiniciar servidor:
```bash
pm2 restart whatsapp-cantita
```

Ver estado:
```bash
pm2 status
```
