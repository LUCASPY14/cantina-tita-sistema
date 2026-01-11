# 🚀 GUÍA DE INSTALACIÓN - WHATSAPP-WEB.JS

## ✅ PASO A PASO

### **1. Instalar Node.js** (si no lo tienes)

```bash
# Descargar e instalar desde: https://nodejs.org/
# Versión recomendada: v18 o superior

# Verificar instalación:
node --version
npm --version
```

---

### **2. Instalar dependencias del servidor WhatsApp**

```bash
# Ir a la carpeta del servidor
cd whatsapp-server

# Instalar dependencias
npm install

# Esto instalará:
# - whatsapp-web.js (cliente WhatsApp)
# - express (servidor HTTP)
# - qrcode-terminal (mostrar QR en consola)
```

---

### **3. Iniciar servidor por primera vez**

```bash
# Dentro de whatsapp-server/
node server.js
```

**Verás algo como:**
```
🚀 Iniciando servidor WhatsApp...
🚀 ============================================
   SERVIDOR WHATSAPP INICIADO
============================================

📡 Puerto: 3000
🌐 URL base: http://localhost:3000

📚 Endpoints disponibles:
   GET  http://localhost:3000/status
   GET  http://localhost:3000/qr
   ...

⏳ Esperando autenticación WhatsApp...

📱 ============================================
   ESCANEA ESTE QR CON WHATSAPP (NÚMERO SECUNDARIO)
============================================

[QR CODE APARECERÁ AQUÍ]
```

---

### **4. Escanear QR con WhatsApp**

**⚠️ IMPORTANTE: Usar SOLO número secundario (NO el principal)**

1. **Consigue un chip secundario** ($5-10 en Paraguay)
2. **Activa WhatsApp** en ese número
3. En WhatsApp del número secundario:
   - Ve a: **Configuración → Dispositivos vinculados**
   - Toca: **Vincular dispositivo**
   - **Escanea el QR** que aparece en la consola
4. ✅ Verás: **"WhatsApp conectado y listo!"**

**Sesión guardada:** No necesitarás escanear QR nuevamente

---

### **5. Probar que funciona**

```bash
# En otra terminal (PowerShell)

# Verificar estado
Invoke-RestMethod -Uri "http://localhost:3000/status"
# Debería mostrar: "ready": true

# Enviar mensaje de prueba (cambia el número)
$body = @{
    phone = "+595981234567"
    message = "Prueba desde CantiTita"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:3000/send" -Method POST -Body $body -ContentType "application/json"
```

---

### **6. Mantener servidor corriendo (24/7)**

#### **Opción A: PM2 (Recomendado - Windows/Linux)**

```bash
# Instalar PM2 globalmente
npm install -g pm2

# Iniciar servidor con PM2
cd whatsapp-server
pm2 start server.js --name whatsapp-cantita

# Ver logs
pm2 logs whatsapp-cantita

# Ver estado
pm2 status

# Detener
pm2 stop whatsapp-cantita

# Reiniciar
pm2 restart whatsapp-cantita

# Auto-inicio al reiniciar PC
pm2 startup
pm2 save
```

#### **Opción B: Dejar terminal abierta (Simple)**

```bash
# Simplemente dejar la terminal corriendo
cd whatsapp-server
node server.js

# No cerrar la ventana
```

---

### **7. Configurar Django**

**Archivo: `.env`**
```ini
# Agregar estas líneas
WHATSAPP_PROVIDER=whatsapp-web-js
WHATSAPP_SERVER_URL=http://localhost:3000
CANTITA_WHATSAPP_CONTACTO=+595987654321
```

Ya está configurado en `cantina_project/settings.py` ✅

---

### **8. Probar desde Django**

```python
# En Django shell
python manage.py shell

from gestion.whatsapp_client import whatsapp_client

# Verificar conexión
whatsapp_client.check_status()
# True

# Enviar mensaje de prueba
whatsapp_client.send_message('+595981234567', 'Hola desde Django!')
# True

# Enviar con template
whatsapp_client.send_template(
    '+595981234567',
    'saldo_bajo',
    {'tarjeta': '12345', 'saldo': '5,000'}
)
# True
```

---

### **9. Usar en notificaciones**

```python
from gestion.notificaciones import notificar_saldo_bajo
from gestion.models import Tarjeta

# Obtener tarjeta
tarjeta = Tarjeta.objects.first()

# Notificar por email + WhatsApp
resultados = notificar_saldo_bajo(
    tarjeta,
    canales=['email', 'whatsapp']
)

print(resultados)
# {'email': True, 'whatsapp': True}
```

---

## 📊 VERIFICACIÓN

### **Endpoints disponibles:**

```bash
# Estado del servidor
GET http://localhost:3000/status

# QR code (si no autenticado)
GET http://localhost:3000/qr

# Health check
GET http://localhost:3000/health

# Templates disponibles
GET http://localhost:3000/templates

# Enviar mensaje simple
POST http://localhost:3000/send
{
  "phone": "+595981234567",
  "message": "Hola"
}

# Enviar template
POST http://localhost:3000/send-template
{
  "phone": "+595981234567",
  "template": "saldo_bajo",
  "params": {
    "tarjeta": "12345",
    "saldo": "5,000"
  }
}

# Enviar imagen
POST http://localhost:3000/send-image
{
  "phone": "+595981234567",
  "imageUrl": "https://ejemplo.com/imagen.jpg",
  "caption": "Texto de la imagen"
}

# Envío masivo
POST http://localhost:3000/send-bulk
{
  "recipients": [
    {"phone": "+595981111111", "message": "Mensaje 1"},
    {"phone": "+595982222222", "message": "Mensaje 2"}
  ]
}
```

---

## ⚠️ ADVERTENCIAS IMPORTANTES

### **1. Solo usar número SECUNDARIO**
- ❌ NO usar número principal de negocio
- ✅ Comprar chip barato ($5-10) para automatización
- Si se banea: Simplemente cambiar chip

### **2. Límites recomendados**
- Máximo: **50 mensajes/día**
- Delay entre mensajes: **2-3 segundos**
- No enviar spam

### **3. Servidor debe estar corriendo**
- WhatsApp solo funciona si servidor está activo
- Usar PM2 para mantenerlo corriendo
- Consumo RAM: ~300MB

### **4. Sesión se pierde si:**
- Cierras WhatsApp en el teléfono vinculado
- Desvinculas el dispositivo
- Solución: Re-escanear QR

---

## 🆘 TROUBLESHOOTING

### **Problema: QR no aparece**
```bash
# Espera 10-15 segundos
# Si no aparece, reinicia servidor:
pm2 restart whatsapp-cantita
```

### **Problema: "WhatsApp no está conectado"**
```bash
# Verificar estado
curl http://localhost:3000/status

# Si ready=false, necesitas escanear QR nuevamente
curl http://localhost:3000/qr
```

### **Problema: Error al enviar mensaje**
- Verificar que número sea válido (+595981234567)
- Verificar que WhatsApp esté activo en ese número
- Verificar que servidor esté corriendo

### **Problema: Servidor se cierra solo**
```bash
# Usar PM2 en lugar de node directamente
pm2 start server.js --name whatsapp-cantita
pm2 save
```

---

## ✅ RESUMEN

1. ✅ Instalar Node.js
2. ✅ `cd whatsapp-server && npm install`
3. ✅ `node server.js`
4. ✅ Escanear QR con número secundario
5. ✅ `pm2 start server.js --name whatsapp-cantita`
6. ✅ Configurar `.env`: `WHATSAPP_PROVIDER=whatsapp-web-js`
7. ✅ Probar desde Django: `whatsapp_client.send_message(...)`
8. ✅ Listo! Costo: $0/mes

---

**¿Necesitas ayuda?** Revisa los logs:
```bash
pm2 logs whatsapp-cantita
```
