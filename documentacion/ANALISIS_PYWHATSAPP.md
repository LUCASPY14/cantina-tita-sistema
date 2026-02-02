# 🐍 PyWhatsApp y Alternativas en Python
## Análisis de Librerías Python para WhatsApp

---

## ⚠️ ADVERTENCIA IMPORTANTE

**PyWhatsApp NO es una librería oficial**. Existen varias librerías Python para WhatsApp, pero **TODAS son no oficiales** y usan WhatsApp Web reverse-engineered.

---

## 📦 LIBRERÍAS PYTHON DISPONIBLES

### **1. PyWhatKit** ⭐⭐⭐

**La más popular para Python**

#### **Características:**
- ✅ Fácil de usar (3 líneas de código)
- ✅ Instalación simple: `pip install pywhatkit`
- ✅ No requiere servidor externo
- ✅ Documentación abundante
- ❌ **NO OFICIAL** - Usa WhatsApp Web
- ❌ Abre WhatsApp Web en el navegador (visible)
- ❌ Requiere escanear QR manualmente
- ❌ No puede enviar mensajes inmediatos (delay 2 minutos)
- ❌ **RIESGO DE BAN**

#### **Instalación:**
```bash
pip install pywhatkit
```

#### **Código de ejemplo:**
```python
import pywhatkit as kit
from datetime import datetime

# Enviar mensaje a una hora específica (no inmediato)
# Formato: hora en 24h
kit.sendwhatmsg(
    phone_no="+595981234567",
    message="Hola desde PyWhatKit",
    time_hour=15,  # 3 PM
    time_min=30,   # 30 minutos
    wait_time=20   # Espera 20 segundos después de abrir
)

# Enviar mensaje instantáneo (abre navegador)
kit.sendwhatmsg_instantly(
    phone_no="+595981234567",
    message="Mensaje instantáneo",
    wait_time=15,
    tab_close=True  # Cierra pestaña después de enviar
)
```

#### **Integración con Django:**
```python
# gestion/notificaciones.py

import pywhatkit as kit
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def enviar_whatsapp_pywhatkit(telefono, mensaje):
    """
    Enviar WhatsApp usando PyWhatKit
    
    ⚠️ LIMITACIONES:
    - Abre navegador visible
    - Requiere WhatsApp Web escaneado
    - No puede enviar inmediatamente (delay 2 min)
    - No apto para producción
    
    Args:
        telefono (str): +595981234567
        mensaje (str): Texto del mensaje
    
    Returns:
        bool: True si se programó correctamente
    """
    try:
        # Normalizar teléfono
        if not telefono.startswith('+'):
            telefono = '+' + telefono.replace(' ', '').replace('-', '')
        
        # Obtener hora actual + 2 minutos (mínimo delay)
        now = datetime.now()
        send_time = now + timedelta(minutes=2)
        
        # Programar envío
        kit.sendwhatmsg(
            phone_no=telefono,
            message=mensaje,
            time_hour=send_time.hour,
            time_min=send_time.minute,
            wait_time=20,
            tab_close=True,
            close_time=3
        )
        
        logger.info(f"WhatsApp PyWhatKit programado a {telefono} para {send_time}")
        return True
        
    except Exception as e:
        logger.error(f"Error PyWhatKit: {str(e)}")
        return False


def enviar_whatsapp_pywhatkit_instantaneo(telefono, mensaje):
    """
    Enviar WhatsApp instantáneo (abre navegador ahora)
    
    ⚠️ MUY LIMITADO - Solo para testing personal
    """
    try:
        if not telefono.startswith('+'):
            telefono = '+' + telefono.replace(' ', '').replace('-', '')
        
        kit.sendwhatmsg_instantly(
            phone_no=telefono,
            message=mensaje,
            wait_time=15,
            tab_close=True,
            close_time=3
        )
        
        logger.info(f"WhatsApp PyWhatKit enviado instantáneamente a {telefono}")
        return True
        
    except Exception as e:
        logger.error(f"Error PyWhatKit instantáneo: {str(e)}")
        return False
```

#### **Ventajas de PyWhatKit:**
- ✅ Instalación trivial: `pip install pywhatkit`
- ✅ Código muy simple (3-4 líneas)
- ✅ No requiere servidor Node.js
- ✅ Gratis completamente
- ✅ Funciona en Windows/Linux/Mac

#### **Desventajas de PyWhatKit:**
- ❌ **Abre navegador visible** (no es silencioso)
- ❌ No puede enviar mensajes inmediatos (delay mínimo 2 minutos)
- ❌ Requiere que WhatsApp Web esté escaneado en navegador
- ❌ **NO OFICIAL** - Riesgo de ban
- ❌ No apto para producción (interfiere con usuario)
- ❌ No funciona en servidores sin GUI
- ❌ No soporta imágenes/multimedia fácilmente

#### **Caso de uso:**
- 🟢 Scripts personales
- 🟢 Automatización básica en PC local
- 🟢 Envío de mensajes programados
- 🔴 **NO USAR EN PRODUCCIÓN**
- 🔴 **NO USAR EN SERVIDOR**

---

### **2. whatsapp-python** ⭐⭐

**Wrapper de API oficial (requiere cuenta)**

#### **Instalación:**
```bash
pip install whatsapp-python
```

#### **Código:**
```python
from whatsapp import WhatsApp

# Requiere cuenta de WhatsApp Business API
wa = WhatsApp(token="tu_token_oficial", phone_number_id="tu_phone_id")

# Enviar mensaje
wa.send_message(
    message="Hola desde Python",
    recipient_id="595981234567"
)

# Enviar con template
wa.send_template(
    template="saldo_bajo",
    recipient_id="595981234567",
    components=[
        {"type": "body", "parameters": [{"type": "text", "text": "5000"}]}
    ]
)
```

#### **Ventajas:**
- ✅ Usa API oficial de WhatsApp
- ✅ No riesgo de ban
- ✅ Código Python nativo
- ✅ Soporta templates y multimedia

#### **Desventajas:**
- ⚠️ Requiere cuenta Business API oficial
- ⚠️ Mismo costo que usar requests directamente
- ⚠️ Documentación limitada
- ⚠️ Menos flexible que requests puro

---

### **3. yowsup** ⭐

**OBSOLETA - Ya no funciona**

```bash
# NO INSTALAR - DEPRECATED
# pip install yowsup
```

**Estado:** ❌ WhatsApp cambió protocolos, ya no funciona

---

### **4. selenium-whatsapp** ⭐⭐

**Automatización con Selenium**

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def enviar_whatsapp_selenium(telefono, mensaje):
    """
    Enviar WhatsApp usando Selenium
    
    ⚠️ Aún más pesado que PyWhatKit
    """
    driver = webdriver.Chrome()
    driver.get('https://web.whatsapp.com')
    
    # Esperar a escanear QR manualmente
    input("Escanea QR y presiona Enter...")
    
    # Buscar contacto
    search_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
    search_box.click()
    search_box.send_keys(telefono)
    time.sleep(2)
    
    # Click en contacto
    contact = driver.find_element(By.XPATH, f'//span[@title="{telefono}"]')
    contact.click()
    
    # Escribir mensaje
    message_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
    message_box.send_keys(mensaje)
    
    # Enviar
    send_button = driver.find_element(By.XPATH, '//button[@data-tab="11"]')
    send_button.click()
    
    driver.quit()
```

**Ventajas:**
- ✅ Control total sobre la interfaz
- ✅ Puede hacer cualquier cosa que un humano haría

**Desventajas:**
- ❌ Muy pesado (abre navegador completo)
- ❌ Lento (varios segundos por mensaje)
- ❌ Frágil (se rompe si WhatsApp cambia diseño)
- ❌ NO apto para producción

---

## 📊 COMPARATIVA: PYTHON vs OTRAS OPCIONES

| Opción | Lenguaje | Costo | Oficial | Prod. | Facilidad |
|--------|----------|-------|---------|-------|-----------|
| **PyWhatKit** | 🐍 Python | $0 | ❌ | ❌ | ⭐⭐⭐⭐⭐ |
| **whatsapp-python** | 🐍 Python | $0.006 | ✅ | ✅ | ⭐⭐⭐⭐ |
| **Selenium WA** | 🐍 Python | $0 | ❌ | ❌ | ⭐⭐ |
| **Baileys** | Node.js | $0 | ❌ | ⚠️ | ⭐⭐⭐⭐ |
| **Gupshup** | API REST | $0.003 | ✅ | ✅ | ⭐⭐⭐⭐⭐ |
| **Meta API** | API REST | $0.006 | ✅ | ✅ | ⭐⭐⭐⭐ |

---

## 🎯 VEREDICTO SOBRE PyWhatKit

### **¿Es bueno PyWhatKit?**

**Para uso personal:** ✅ Sí
- Scripts simples en tu PC
- Enviar mensajes programados
- Automatización básica

**Para Cantina Tita (producción):** ❌ NO

**Razones:**
1. ❌ Abre navegador visible (no puede correr en servidor sin GUI)
2. ❌ No puede enviar mensajes inmediatos
3. ❌ Interfiere con el usuario
4. ❌ Riesgo de ban
5. ❌ No escalable (1 mensaje a la vez)
6. ❌ Requiere supervisión manual (escanear QR)

---

## 💡 RECOMENDACIÓN ACTUALIZADA

### **Para Cantina Tita:**

#### **Opción 1: Gupshup con Python** ⭐⭐⭐⭐⭐

```python
# Ya implementado en notificaciones.py
# Solo necesitas requests (ya instalado)

import requests

def enviar_whatsapp_gupshup(telefono, mensaje):
    """
    Usa API REST de Gupshup - $0.003/mensaje
    
    ✅ Oficial
    ✅ Funciona en servidor
    ✅ Código Python nativo
    ✅ Sin navegador
    ✅ Inmediato
    """
    url = "https://api.gupshup.io/sm/api/v1/msg"
    headers = {"apikey": settings.GUPSHUP_API_KEY}
    payload = {
        "channel": "whatsapp",
        "source": "CantiTita",
        "destination": telefono,
        "message": json.dumps({"type": "text", "text": mensaje})
    }
    response = requests.post(url, headers=headers, data=payload)
    return response.status_code == 200
```

**Ventajas vs PyWhatKit:**
- ✅ API REST pura (Python requests)
- ✅ No requiere navegador
- ✅ Funciona en servidor
- ✅ Oficial (sin riesgo ban)
- ✅ Escalable (miles de mensajes)
- ✅ Inmediato (sin delays)
- ✅ Costo ultra bajo ($0.003)

#### **Opción 2: whatsapp-python (wrapper oficial)** ⭐⭐⭐⭐

```python
# pip install whatsapp-python

from whatsapp import WhatsApp

wa = WhatsApp(
    token=settings.WHATSAPP_ACCESS_TOKEN,
    phone_number_id=settings.WHATSAPP_PHONE_NUMBER_ID
)

wa.send_message(
    message="Saldo bajo: Gs. 5,000",
    recipient_id="595981234567"
)
```

**Ventajas:**
- ✅ Código Python más limpio
- ✅ Oficial (Meta Business API)
- ✅ Funciona en servidor
- ✅ Sin navegador

**Desventajas:**
- ⚠️ Más caro ($0.006 vs $0.003 Gupshup)
- ⚠️ Requiere aprobación Meta

---

## 🔧 CÓDIGO COMPARATIVO

### **PyWhatKit (NO recomendado para producción):**

```python
import pywhatkit as kit

# ❌ Abre navegador
# ❌ Delay mínimo 2 minutos
# ❌ No funciona en servidor
kit.sendwhatmsg("+595981234567", "Mensaje", 15, 30)
```

### **Gupshup con Python (RECOMENDADO):**

```python
import requests
import json

# ✅ No abre navegador
# ✅ Instantáneo
# ✅ Funciona en servidor
# ✅ Más barato ($0.003)

url = "https://api.gupshup.io/sm/api/v1/msg"
headers = {"apikey": "tu_api_key"}
payload = {
    "channel": "whatsapp",
    "source": "CantiTita",
    "destination": "595981234567",
    "message": json.dumps({"type": "text", "text": "Mensaje"})
}
response = requests.post(url, headers=headers, data=payload)
```

**Resultado:** Mismo Python, pero con API REST (ya tienes `requests` instalado)

---

## 📝 TABLA FINAL DE DECISIÓN

### **Escenarios de uso:**

| Necesidad | Mejor Opción | Alternativa |
|-----------|--------------|-------------|
| **Producción Cantina Tita** | ✅ Gupshup API | Meta Business API |
| **Testing rápido local** | PyWhatKit | Baileys |
| **Script personal PC** | PyWhatKit | Selenium |
| **Servidor sin GUI** | ❌ NO PyWhatKit | ✅ Gupshup |
| **Costo $0 absoluto** | Baileys (Node.js) | PyWhatKit (local) |
| **Python puro + Oficial** | whatsapp-python | Gupshup |

---

## ✅ CONCLUSIÓN SOBRE PyWhatKit

### **¿Usar PyWhatKit?**

**SÍ, si:**
- ✅ Solo para scripts personales en tu PC
- ✅ Tienes GUI/navegador disponible
- ✅ No te importa que abra navegador
- ✅ Solo testing/desarrollo local
- ✅ Menos de 10 mensajes/día

**NO, si:**
- ❌ Necesitas para producción
- ❌ Quieres correr en servidor
- ❌ Necesitas envío inmediato
- ❌ Quieres enviar muchos mensajes
- ❌ No quieres riesgo de ban

---

## 🎯 RECOMENDACIÓN FINAL PARA CANTINA TITA

### **Usa Gupshup con Python requests** ⭐⭐⭐⭐⭐

```python
# YA IMPLEMENTADO en gestion/notificaciones.py
# Solo configura en .env:

WHATSAPP_PROVIDER=gupshup
GUPSHUP_API_KEY=tu_api_key
GUPSHUP_APP_NAME=CantiTita
```

**¿Por qué?**
1. ✅ Código Python nativo (solo `requests`)
2. ✅ Funciona en servidor Django
3. ✅ Oficial (sin riesgo ban)
4. ✅ MÁS BARATO ($0.003 vs $0.006 Meta)
5. ✅ Sin navegador/GUI necesario
6. ✅ Escalable (miles de mensajes)
7. ✅ Ya está implementado en tu código

**PyWhatKit NO cumple ninguno de estos requisitos para producción.**

---

## 📚 CÓDIGO YA LISTO

El código de Gupshup **ya está implementado** en:
- `gestion/notificaciones.py` (función `enviar_whatsapp_gupshup()`)
- Solo necesitas registrarte en Gupshup y obtener API Key

**No necesitas PyWhatKit ni ninguna librería extra.**

---

**RESUMEN:** PyWhatKit es bueno para scripts personales, pero **NO apto para Cantina Tita**. Usa **Gupshup** (ya implementado, oficial, más barato).
