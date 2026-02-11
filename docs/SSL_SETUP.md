# 🔒 Guía de Instalación de Certificado SSL

**Actualizado:** 4 de Febrero 2026  
**Propósito:** Habilitar HTTPS en tu servidor de producción  
**Tiempo estimado:** 15-30 minutos (según método)

---

## 📋 Índice

1. [Opción A: Railway/Render (Automático)](#opción-a-railwayrender-automático)
2. [Opción B: VPS con Certbot (Let's Encrypt)](#opción-b-vps-con-certbot-lets-encrypt)
3. [Opción C: Servidor Local con DynDNS](#opción-c-servidor-local-con-dyndns)
4. [Verificación y Activación](#verificación-y-activación)
5. [Solución de Problemas](#solución-de-problemas)

---

## Opción A: Railway/Render (Automático)

### ✅ **Railway**

Railway genera certificados SSL **automáticamente** cuando despliegas:

```bash
# 1. Desplegar proyecto
railway up

# 2. Asignar dominio personalizado (opcional)
railway domain add cantitatita.com

# 3. SSL se configura automáticamente
# Railway genera certificado y redirige HTTP → HTTPS
```

**Configuración .env.production:**
```bash
# Railway configura SSL automáticamente
ALLOWED_HOSTS=.railway.app,cantitatita.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
```

**Verificación:**
- URL de Railway: `https://tu-proyecto.railway.app` (SSL activo por defecto)
- Dominio custom: Railway gestiona certificado automáticamente

---

### ✅ **Render**

Similar a Railway, Render incluye SSL gratuito:

```bash
# 1. Conectar repositorio GitHub
# 2. Crear Web Service
# 3. Configurar dominio personalizado en Dashboard
# 4. Render instala certificado SSL automáticamente
```

**Configuración .env.production:**
```bash
ALLOWED_HOSTS=.onrender.com,cantitatita.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
```

---

## Opción B: VPS con Certbot (Let's Encrypt)

### 📦 **Requisitos Previos**

- VPS con IP pública (DigitalOcean, Linode, AWS, etc.)
- Dominio apuntando a tu servidor (A record configurado)
- Nginx o Apache instalado
- Puertos 80 y 443 abiertos en firewall

---

### 🚀 **Instalación Paso a Paso (Ubuntu/Debian)**

#### 1. Instalar Certbot

```bash
# Actualizar sistema
sudo apt update
sudo apt upgrade -y

# Instalar Certbot y plugin de Nginx
sudo apt install certbot python3-certbot-nginx -y

# Para Apache, usar:
# sudo apt install certbot python3-certbot-apache -y
```

#### 2. Configurar Nginx (antes de obtener certificado)

```bash
# Crear configuración básica de Nginx
sudo nano /etc/nginx/sites-available/cantinatita

# Pegar esta configuración:
```

```nginx
server {
    listen 80;
    server_name cantitatita.com www.cantitatita.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /var/www/cantitatita/staticfiles/;
    }

    location /media/ {
        alias /var/www/cantitatita/media/;
    }
}
```

```bash
# Activar sitio
sudo ln -s /etc/nginx/sites-available/cantinatita /etc/nginx/sites-enabled/

# Verificar configuración
sudo nginx -t

# Recargar Nginx
sudo systemctl reload nginx
```

#### 3. Obtener Certificado SSL con Certbot

```bash
# Método automático (recomendado)
sudo certbot --nginx -d cantitatita.com -d www.cantitatita.com

# Certbot te preguntará:
# 1. Email para notificaciones: tu-email@example.com
# 2. Aceptar términos: Yes
# 3. ¿Redireccionar HTTP → HTTPS?: 2 (Redirect)
```

**Salida esperada:**
```
Congratulations! You have successfully enabled HTTPS on cantitatita.com and www.cantitatita.com

IMPORTANT NOTES:
- Congratulations! Your certificate has been saved at:
  /etc/letsencrypt/live/cantitatita.com/fullchain.pem
- Your certificate will expire on 2026-05-05. To obtain a new certificate, run certbot again.
```

#### 4. Verificar Renovación Automática

```bash
# Certbot instala un cron job para renovar automáticamente
# Verificar que funciona:
sudo certbot renew --dry-run

# Si funciona, verás:
# Congratulations, all simulated renewals succeeded
```

#### 5. Actualizar .env.production

```bash
cd /var/www/cantitatita/entorno
nano .env.production
```

```bash
# Activar todas las configuraciones SSL
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000

ALLOWED_HOSTS=cantitatita.com,www.cantitatita.com,TU_IP_PUBLICA
```

#### 6. Reiniciar Aplicación

```bash
# Reiniciar Gunicorn
sudo systemctl restart gunicorn

# Verificar que funciona
curl -I https://cantitatita.com
# Debe devolver: HTTP/2 200
```

---

### 🔄 **Configuración Final de Nginx (después de Certbot)**

Certbot modifica automáticamente tu Nginx config. Debería verse así:

```nginx
server {
    listen 80;
    server_name cantitatita.com www.cantitatita.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name cantitatita.com www.cantitatita.com;

    ssl_certificate /etc/letsencrypt/live/cantitatita.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/cantitatita.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
    }

    location /static/ {
        alias /var/www/cantitatita/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/www/cantitatita/media/;
        expires 7d;
    }
}
```

---

## Opción C: Servidor Local con DynDNS

### 🏠 **Setup para Servidor en Casa**

#### 1. Configurar DynDNS (Dominio Dinámico)

**Servicios gratuitos recomendados:**
- No-IP: https://www.noip.com (30 días gratis, luego confirmar mensualmente)
- Duck DNS: https://www.duckdns.org (gratis siempre)
- FreeDNS: https://freedns.afraid.org

**Ejemplo con No-IP:**

```bash
# 1. Registrarse en No-IP
# 2. Crear hostname: cantitatita.ddns.net
# 3. Instalar cliente DynDNS en tu servidor:

sudo apt install noip2
sudo noip2 -C  # Configurar con tus credenciales
sudo systemctl enable noip2
sudo systemctl start noip2
```

#### 2. Configurar Router (Port Forwarding)

```
Acceder al panel de tu router (192.168.1.1 o 192.168.0.1)

Port Forwarding:
- Puerto externo: 80 → IP interna: 192.168.1.100 Puerto: 80
- Puerto externo: 443 → IP interna: 192.168.1.100 Puerto: 443

NOTA: Algunos ISP bloquean puerto 80, usar puerto alternativo (8080) si es necesario
```

#### 3. Obtener Certificado SSL con Certbot

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtener certificado (método standalone)
sudo certbot certonly --standalone -d cantitatita.ddns.net

# O si Nginx ya está corriendo:
sudo certbot --nginx -d cantitatita.ddns.net
```

#### 4. Configurar Renovación Automática

Let's Encrypt requiere que tu dominio sea accesible desde internet para renovar.

```bash
# Verificar que tu dominio es accesible
curl http://cantitatita.ddns.net

# Si funciona, configurar cron para renovación
sudo crontab -e

# Agregar (renueva cada lunes a las 3am):
0 3 * * 1 certbot renew --quiet && systemctl reload nginx
```

---

## Verificación y Activación

### ✅ **Checklist de Verificación**

```bash
# 1. Verificar certificado instalado
sudo certbot certificates

# 2. Probar HTTPS
curl -I https://tu-dominio.com

# 3. Verificar redirección HTTP → HTTPS
curl -I http://tu-dominio.com
# Debe devolver: 301 Moved Permanently

# 4. Test completo con SSL Labs
# Ir a: https://www.ssllabs.com/ssltest/
# Ingresar tu dominio y esperar análisis (debe dar A o A+)
```

### 🔧 **Activar Configuraciones SSL en Django**

```bash
# Editar .env.production
nano entorno/.env.production

# Cambiar a:
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000

# Reiniciar aplicación
sudo systemctl restart gunicorn

# Verificar con Django
python backend/manage.py check --deploy
# No debe haber warnings de SSL
```

---

## Solución de Problemas

### ❌ **Error: "Challenge failed for domain"**

**Causa:** Certbot no puede verificar que controlas el dominio.

**Solución:**
```bash
# 1. Verificar que el dominio apunta a tu IP
nslookup cantitatita.com

# 2. Verificar que puerto 80 está abierto
sudo ufw status
sudo ufw allow 80
sudo ufw allow 443

# 3. Verificar Nginx está corriendo
sudo systemctl status nginx

# 4. Reintentar con método standalone
sudo systemctl stop nginx
sudo certbot certonly --standalone -d cantitatita.com
sudo systemctl start nginx
```

---

### ❌ **Error: "Too many certificates already issued"**

**Causa:** Let's Encrypt limita a 5 certificados por dominio por semana.

**Solución:**
```bash
# Usar staging environment para pruebas
sudo certbot --nginx --staging -d cantitatita.com

# Cuando funcione, obtener certificado real
sudo certbot --nginx --force-renewal -d cantitatita.com
```

---

### ❌ **Error: "mixed content" en navegador**

**Causa:** Tienes recursos (CSS/JS/imágenes) cargándose por HTTP.

**Solución:**
```python
# En settings.py, agregar:
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

```nginx
# En Nginx, verificar header:
proxy_set_header X-Forwarded-Proto https;
```

---

## 📚 Referencias

- **Let's Encrypt:** https://letsencrypt.org/getting-started/
- **Certbot:** https://certbot.eff.org/
- **Django SSL:** https://docs.djangoproject.com/en/5.0/topics/security/#ssl-https
- **SSL Labs Test:** https://www.ssllabs.com/ssltest/
- **Mozilla SSL Config Generator:** https://ssl-config.mozilla.org/

---

## ✅ Siguiente Paso

Después de instalar SSL exitosamente:

1. ✅ Verificar con SSL Labs (debe dar A o A+)
2. ✅ Actualizar `.env.production` con configuraciones SSL
3. ✅ Ejecutar `python manage.py check --deploy` (0 warnings SSL)
4. ✅ Probar login y formularios con HTTPS
5. ✅ Configurar renovación automática
6. ✅ Documentar certificados y fechas de renovación

**¿Listo?** → [Continuar con Deployment Completo](DEPLOYMENT_GUIDE.md)
