# 🚀 INICIO RÁPIDO - WHATSAPP GRATIS

## ⏱️ 10 minutos para tener WhatsApp funcionando

---

## ✅ PASO 1: Verificar Node.js (1 min)

```powershell
# Verificar instalación
node --version
npm --version

# Si NO está instalado:
# Descargar desde: https://nodejs.org/
# Instalar versión LTS
```

---

## ✅ PASO 2: Instalar Servidor (2 min)

```powershell
# Ejecutar instalador automático
.\instalar_whatsapp.ps1

# O manualmente:
cd whatsapp-server
npm install
```

---

## ✅ PASO 3: Iniciar Servidor (1 min)

```powershell
cd whatsapp-server
node server.js
```

**Verás:**
```
🚀 Iniciando servidor WhatsApp...
📱 ESCANEA ESTE QR CON WHATSAPP
[QR CODE AQUÍ]
```

---

## ✅ PASO 4: Escanear QR (2 min)

### ⚠️ IMPORTANTE: Usar SOLO número SECUNDARIO

1. **Conseguir chip secundario** (si no tienes):
   - Comprar chip prepago: $5-10
   - Activar WhatsApp en ese número

2. **En WhatsApp del chip secundario**:
   - Abrir WhatsApp
   - Ir a: **Configuración → Dispositivos vinculados**
   - Tocar: **Vincular dispositivo**
   - **Escanear QR** de la consola

3. **Verás**:
   ```
   ✅ WhatsApp conectado y listo!
   ```

---

## ✅ PASO 5: Probar (2 min)

### En PowerShell:

```powershell
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

### En Django:

```python
python manage.py shell

from gestion.whatsapp_client import whatsapp_client

# Verificar
whatsapp_client.check_status()
# True

# Enviar
whatsapp_client.send_message('+595981234567', 'Hola desde Django')
# True
```

---

## ✅ PASO 6: Mantener Corriendo (2 min)

### Opción A: PM2 (Recomendado)

```powershell
# Instalar PM2
npm install -g pm2

# Iniciar servidor
cd whatsapp-server
pm2 start server.js --name whatsapp-cantita

# Auto-inicio al reiniciar PC
pm2 startup
pm2 save

# Ver logs
pm2 logs whatsapp-cantita
```

### Opción B: Dejar terminal abierta

```powershell
# Simplemente dejar corriendo
cd whatsapp-server
node server.js

# No cerrar la ventana
```

---

## ✅ PASO 7: Configurar Django (Ya hecho ✅)

Ya está configurado en:
- `cantina_project/settings.py` ✅
- `gestion/notificaciones.py` ✅
- `gestion/whatsapp_client.py` ✅

Solo necesitas en `.env`:

```ini
WHATSAPP_PROVIDER=whatsapp-web-js
WHATSAPP_SERVER_URL=http://localhost:3000
CANTITA_WHATSAPP_CONTACTO=+595987654321
```

---

## 🎯 USO EN PRODUCCIÓN

### Enviar notificación de saldo bajo:

```python
from gestion.notificaciones import notificar_saldo_bajo
from gestion.models import Tarjeta

# Obtener tarjeta
tarjeta = Tarjeta.objects.get(nro_tarjeta='12345')

# Notificar por email + WhatsApp
resultados = notificar_saldo_bajo(
    tarjeta,
    canales=['email', 'whatsapp']
)

print(resultados)
# {'email': True, 'whatsapp': True}
```

### Enviar con template:

```python
from gestion.whatsapp_client import whatsapp_client

whatsapp_client.send_template(
    phone='+595981234567',
    template_name='saldo_bajo',
    params={
        'tarjeta': '12345',
        'saldo': '5,000'
    }
)
```

---

## 📊 ENDPOINTS DISPONIBLES

```bash
# Estado
GET http://localhost:3000/status

# QR
GET http://localhost:3000/qr

# Templates disponibles
GET http://localhost:3000/templates

# Enviar mensaje
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
  "params": {"tarjeta": "12345", "saldo": "5,000"}
}
```

---

## ⚠️ RECORDATORIOS IMPORTANTES

### ✅ Hacer:
- ✅ Usar chip secundario para automatización
- ✅ Mantener servidor corriendo (PM2)
- ✅ Límite: <50 mensajes/día
- ✅ Delay: 2-3 seg entre mensajes

### ❌ NO Hacer:
- ❌ Usar número principal de negocio
- ❌ Enviar spam
- ❌ Cerrar servidor sin PM2
- ❌ Desvincular dispositivo en WhatsApp

---

## 🆘 TROUBLESHOOTING

### Problema: QR no aparece
```powershell
# Espera 10-15 segundos
# Si no aparece, reinicia:
cd whatsapp-server
node server.js
```

### Problema: "WhatsApp no está conectado"
```powershell
# Verificar estado
curl http://localhost:3000/status

# Si ready=false, re-escanear QR
curl http://localhost:3000/qr
```

### Problema: Error al enviar
- Verificar que servidor esté corriendo
- Verificar número sea válido (+595981234567)
- Ver logs: `pm2 logs whatsapp-cantita`

---

## 💰 COSTO

- **Servidor Node.js**: $0 GRATIS
- **Mensajes WhatsApp**: $0 GRATIS
- **Chip secundario**: $5-10 una vez
- **Total mensual**: $0/mes

vs Twilio: $270/mes

**Ahorro: $3,240/año**

---

## 📚 DOCUMENTACIÓN COMPLETA

- [INSTALACION_WHATSAPP.md](INSTALACION_WHATSAPP.md) - Guía detallada
- [whatsapp-server/README.md](whatsapp-server/README.md) - Servidor
- [RESUMEN_WHATSAPP_IMPLEMENTADO.md](RESUMEN_WHATSAPP_IMPLEMENTADO.md) - Resumen técnico

---

## ✅ CHECKLIST

- [ ] Node.js instalado
- [ ] Servidor instalado (`npm install`)
- [ ] Servidor iniciado (`node server.js`)
- [ ] QR escaneado con número secundario
- [ ] PM2 configurado
- [ ] Mensaje de prueba enviado
- [ ] Integración Django probada

**¡Listo! WhatsApp gratis funcionando** 🎉

---

**¿Problemas?** Revisa logs:
```powershell
pm2 logs whatsapp-cantita
```
