# 🚀 Guía Completa de Deployment - Cantina Tita

**Actualizado:** 4 de Febrero 2026  
**Versión:** 1.0  
**Estado del Proyecto:** Score 9.8/10 | 188 Tests Passing

---

## 📋 Tabla de Contenidos

1. [Pre-requisitos](#pre-requisitos)
2. [Verificación Pre-Deployment](#verificación-pre-deployment)
3. [Opción A: Railway (Recomendado - Más Simple)](#opción-a-railway-recomendado)
4. [Opción B: Render (Alternativa Gratuita)](#opción-b-render)
5. [Opción C: VPS con Gunicorn + Nginx](#opción-c-vps-digitalocean-linode-aws)
6. [Opción D: Servidor Local con DynDNS](#opción-d-servidor-local)
7. [Post-Deployment](#post-deployment)
8. [Monitoreo y Mantenimiento](#monitoreo-y-mantenimiento)

---

## Pre-requisitos

### ✅ Antes de Empezar

- [x] **Código en GitHub** - Repositorio actualizado con último commit
- [x] **Tests pasando** - 188 tests (43 unit + 145 E2E)
- [x] **`.env.production` configurado** - Ver [entorno/.env.production](../entorno/.env.production)
- [x] **Backup de base de datos** - `python backend/manage.py backup_database`
- [x] **Verificación de seguridad** - `python verificar_produccion.py`

### 📦 Dependencias del Proyecto

```txt
# backend/requirements.txt ya incluye todo:
Django==5.2.8
gunicorn==21.2.0
psycopg2-binary==2.9.9  # o mysqlclient para MySQL
python-decouple==3.8
whitenoise==6.6.0
# ... y más
```

---

## Verificación Pre-Deployment

### 🔍 Ejecutar Script de Verificación

```bash
# Verificar configuración de producción
python verificar_produccion.py

# Debe mostrar: ✅ LISTO PARA PRODUCCIÓN
```

**Si aparecen errores:**

```bash
# ❌ ALLOWED_HOSTS solo tiene localhost
# Solución: Editar entorno/.env.production
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com,IP-SERVIDOR

# ❌ DB_PASSWORD es placeholder
# Solución: Generar password seguro
DB_PASSWORD=K8m!Qp2@Wx7#Lz9$Nv4%

# ❌ EMAIL_HOST_PASSWORD es placeholder
# Solución: Obtener App Password de Gmail
# Ver guía en entorno/.env.production líneas 60-80
```

### 🧪 Verificar Django

```bash
# Con configuración de producción
cd backend
python manage.py check --deploy

# Debe mostrar: System check identified no issues (0 silenced).
# Warnings de SSL/HTTPS son normales hasta instalar certificado
```

---

## Opción A: Railway (Recomendado)

**Ventajas:**
- ✅ Deploy en 5-10 minutos
- ✅ SSL automático y gratuito
- ✅ Base de datos MySQL incluida (gratis hasta 512MB)
- ✅ $5/mes crédito gratis
- ✅ CI/CD automático desde GitHub

### 📝 Pasos

#### 1. Crear Cuenta y Proyecto

```bash
# 1. Ir a: https://railway.app
# 2. "Start a New Project" → "Deploy from GitHub"
# 3. Conectar repositorio: LUCASPY14/cantina-tita-sistema
# 4. Seleccionar branch: development o main
```

#### 2. Configurar Variables de Entorno

```bash
# En Railway Dashboard → Variables
# Copiar desde entorno/.env.production:

SECRET_KEY=ytwiv_3&n)z9d-f6r&+m@lf=p3qic+-0b8xv)&!dc0k3))zp^7
DEBUG=False
ALLOWED_HOSTS=.railway.app,cantitatita.com

DB_NAME=railway
DB_USER=root
DB_PASSWORD=<generado automáticamente por Railway>
DB_HOST=<generado automáticamente>
DB_PORT=3306

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password-16-caracteres

# SSL (Railway lo maneja automáticamente)
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
```

#### 3. Configurar Base de Datos MySQL

```bash
# En Railway Dashboard:
# 1. "+ New" → "Database" → "Add MySQL"
# 2. Railway crea DB automáticamente
# 3. Copiar credenciales a Variables de entorno
# 4. Variables se auto-configuran como DATABASE_URL
```

#### 4. Crear `railway.json` (Opcional)

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "cd backend && python manage.py migrate && python manage.py collectstatic --noinput && gunicorn cantina_project.wsgi:application --bind 0.0.0.0:$PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### 5. Crear `Procfile`

```procfile
web: cd backend && gunicorn cantina_project.wsgi:application --bind 0.0.0.0:$PORT
release: cd backend && python manage.py migrate && python manage.py collectstatic --noinput
```

#### 6. Deploy

```bash
# Railway detecta cambios automáticamente
# Cada push a GitHub → Auto-deploy

# O deploy manual:
railway up
```

#### 7. Dominio Personalizado

```bash
# En Railway Dashboard → Settings → Domains
# 1. Agregar dominio: cantitatita.com
# 2. Configurar DNS (en tu proveedor):
#    CNAME: cantitatita.com → tu-app.railway.app
# 3. Railway genera certificado SSL automáticamente
```

**URL Final:** `https://tu-proyecto.railway.app` o `https://cantitatita.com`

---

## Opción B: Render

**Similar a Railway, 100% gratuito** (con limitaciones)

### 📝 Pasos

#### 1. Crear Cuenta

```bash
# 1. Ir a: https://render.com
# 2. Sign up con GitHub
# 3. "New" → "Web Service"
```

#### 2. Conectar Repositorio

```bash
# 1. Seleccionar: LUCASPY14/cantina-tita-sistema
# 2. Branch: development
# 3. Name: cantina-tita
# 4. Region: Oregon (US West)
# 5. Build Command: cd backend && pip install -r requirements.txt
# 6. Start Command: cd backend && gunicorn cantina_project.wsgi:application
```

#### 3. Variables de Entorno

```bash
# En Render Dashboard → Environment
# Agregar las mismas que Railway (ver arriba)

# IMPORTANTE en Render:
PYTHON_VERSION=3.13
```

#### 4. Base de Datos

```bash
# Render no incluye MySQL gratuito, usar PostgreSQL:
# 1. "New" → "PostgreSQL"
# 2. Copiar DATABASE_URL generada

# O usar MySQL externo (PlanetScale gratis):
# https://planetscale.com
```

#### 5. Deploy

```bash
# Render auto-deploya en cada push a GitHub
# Ver logs en Dashboard
```

**URL Final:** `https://cantina-tita.onrender.com`

---

## Opción C: VPS (DigitalOcean, Linode, AWS)

**Para control total y escalabilidad**

### 📝 Requisitos

- VPS con Ubuntu 22.04 LTS (mínimo 1GB RAM, 1 CPU)
- IP pública
- Dominio (opcional pero recomendado)

### 🚀 Setup Completo

#### 1. Conectar al VPS

```bash
ssh root@tu-ip-servidor

# Crear usuario no-root
adduser cantina
usermod -aG sudo cantina
su - cantina
```

#### 2. Instalar Dependencias

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Python 3.11+
sudo apt install python3 python3-pip python3-venv -y

# MySQL
sudo apt install mysql-server -y
sudo mysql_secure_installation

# Nginx
sudo apt install nginx -y

# Git
sudo apt install git -y
```

#### 3. Configurar MySQL

```bash
sudo mysql

# En MySQL:
CREATE DATABASE cantitatitadb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'cantina_user'@'localhost' IDENTIFIED BY 'TU_PASSWORD_SEGURO_AQUI';
GRANT ALL PRIVILEGES ON cantitatitadb.* TO 'cantina_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### 4. Clonar Proyecto

```bash
cd /var/www
sudo git clone https://github.com/LUCASPY14/cantina-tita-sistema.git
sudo chown -R cantina:cantina cantina-tita-sistema
cd cantina-tita-sistema
```

#### 5. Configurar Entorno Virtual

```bash
python3 -m venv .venv
source .venv/bin/activate

cd backend
pip install -r requirements.txt
```

#### 6. Configurar .env.production

```bash
cd ../entorno
cp .env.example .env.production
nano .env.production

# Completar todas las variables (ver template)
# Asegurarse de:
# - DB_PASSWORD con password real de MySQL
# - SECRET_KEY única
# - DEBUG=False
# - ALLOWED_HOSTS con IP/dominio del servidor
```

#### 7. Migraciones y Static Files

```bash
cd ../backend
python manage.py migrate
python manage.py collectstatic --noinput

# Crear superusuario
python manage.py createsuperuser
```

#### 8. Configurar Gunicorn como Servicio

```bash
sudo nano /etc/systemd/system/gunicorn.service
```

```ini
[Unit]
Description=Gunicorn daemon for Cantina Tita
After=network.target

[Service]
User=cantina
Group=www-data
WorkingDirectory=/var/www/cantina-tita-sistema
Environment="PATH=/var/www/cantina-tita-sistema/.venv/bin"
ExecStart=/var/www/cantina-tita-sistema/.venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/var/www/cantina-tita-sistema/gunicorn.sock \
          --chdir /var/www/cantina-tita-sistema/backend \
          cantina_project.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
# Activar y arrancar
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
sudo systemctl status gunicorn
```

#### 9. Configurar Nginx

```bash
sudo nano /etc/nginx/sites-available/cantitatita
```

```nginx
server {
    listen 80;
    server_name cantitatita.com www.cantitatita.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /var/www/cantina-tita-sistema/backend/staticfiles/;
    }

    location /media/ {
        alias /var/www/cantina-tita-sistema/backend/media/;
    }

    location / {
        proxy_pass http://unix:/var/www/cantina-tita-sistema/gunicorn.sock;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Activar sitio
sudo ln -s /etc/nginx/sites-available/cantitatita /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 10. Instalar SSL (Certbot)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d cantitatita.com -d www.cantitatita.com

# Actualizar .env.production con SSL activado
# Reiniciar Gunicorn
sudo systemctl restart gunicorn
```

**Ver guía completa de SSL:** [docs/SSL_SETUP.md](SSL_SETUP.md)

---

## Opción D: Servidor Local

**Para desarrollo o uso interno (sin internet público)**

### 📝 Pasos Rápidos

```bash
# 1. Configurar .env.production localmente
cp entorno/.env.example entorno/.env.production
# Editar con valores locales

# 2. Ejecutar con Gunicorn
source .venv/bin/activate
cd backend
gunicorn cantina_project.wsgi:application --bind 0.0.0.0:8000

# 3. Acceder desde red local
# http://192.168.1.100:8000 (tu IP local)
```

**Para acceso desde internet:**
1. Configurar DynDNS (No-IP, DuckDNS)
2. Port Forwarding en router (80 → 8000, 443 → 8443)
3. Instalar certificado SSL con Certbot

**Ver guía completa:** [docs/SSL_SETUP.md#opción-c-servidor-local](SSL_SETUP.md#opción-c-servidor-local-con-dyndns)

---

## Post-Deployment

### ✅ Checklist Post-Deploy

```bash
# 1. Verificar que el sitio carga
curl -I https://tu-dominio.com
# Debe devolver: HTTP/2 200

# 2. Probar login de admin
# https://tu-dominio.com/admin
# Usuario y password creados con createsuperuser

# 3. Verificar HTTPS
# https://www.ssllabs.com/ssltest/
# Debe dar grado A o A+

# 4. Probar funcionalidades críticas:
# - Login de usuarios
# - Registro de venta (POS)
# - Portal de padres
# - Envío de emails
# - Recarga de tarjetas

# 5. Configurar backups automáticos
```

### 📊 Configurar Backups Automáticos

```bash
# VPS: Cron job para backup diario
crontab -e

# Agregar (backup diario a las 2am):
0 2 * * * /var/www/cantina-tita-sistema/.venv/bin/python /var/www/cantina-tita-sistema/backend/manage.py backup_database --compress --notify

# Railway/Render: Usar Railway Volumes o servicio externo (S3, Backblaze)
```

### 🔔 Configurar Monitoreo (Opcional)

**Opción 1: Sentry (Errores)**
```bash
pip install sentry-sdk

# En settings.py:
import sentry_sdk
sentry_sdk.init(
    dsn="tu-sentry-dsn",
    traces_sample_rate=0.1,
    environment="production",
)
```

**Opción 2: UptimeRobot (Uptime)**
```bash
# Gratis: https://uptimerobot.com
# Configurar check cada 5 minutos
# Alertas por email si el sitio cae
```

---

## Monitoreo y Mantenimiento

### 📈 Logs y Debugging

```bash
# VPS - Ver logs de Gunicorn
sudo journalctl -u gunicorn -f

# VPS - Ver logs de Nginx
sudo tail -f /var/log/nginx/error.log

# Railway/Render - Ver en Dashboard → Logs
```

### 🔄 Actualizaciones

```bash
# VPS
cd /var/www/cantina-tita-sistema
git pull origin development
source .venv/bin/activate
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn

# Railway/Render - Auto-deploy con cada git push
```

### 🧪 Testing en Producción

```bash
# Ejecutar tests contra base de datos de prueba
python manage.py test --settings=cantina_project.settings_test

# Verificar performance
python manage.py test tests.test_performance
```

---

## 🆘 Solución de Problemas

### ❌ Error: "Bad Gateway 502"

```bash
# Verificar Gunicorn está corriendo
sudo systemctl status gunicorn

# Reiniciar
sudo systemctl restart gunicorn

# Ver logs
sudo journalctl -u gunicorn -n 50
```

### ❌ Error: "DisallowedHost"

```bash
# Editar .env.production
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com,IP-SERVIDOR

# Reiniciar aplicación
sudo systemctl restart gunicorn
```

### ❌ Error: "Static files not loading"

```bash
# Recolectar static files
cd backend
python manage.py collectstatic --noinput

# Verificar permisos
sudo chown -R www-data:www-data staticfiles/
sudo chmod -R 755 staticfiles/
```

### ❌ Error: "Can't connect to MySQL"

```bash
# Verificar MySQL está corriendo
sudo systemctl status mysql

# Verificar credenciales en .env.production
# Probar conexión:
mysql -u cantina_user -p cantitatitadb
```

---

## 📚 Referencias

- **Documentación Django Deployment:** https://docs.djangoproject.com/en/5.0/howto/deployment/
- **Gunicorn Docs:** https://docs.gunicorn.org/
- **Nginx Docs:** https://nginx.org/en/docs/
- **Railway Docs:** https://docs.railway.app/
- **Render Docs:** https://render.com/docs

---

## ✅ Checklist Final

- [ ] Código deployado correctamente
- [ ] Base de datos migrada
- [ ] Static files servidos
- [ ] HTTPS funcionando (si aplica)
- [ ] Admin panel accesible
- [ ] Funcionalidades críticas probadas
- [ ] Backups configurados
- [ ] Monitoreo configurado (opcional)
- [ ] Documentación actualizada
- [ ] Usuarios notificados del lanzamiento

**🎉 ¡Felicitaciones! Tu sistema está en producción.**

---

**Soporte:** Para problemas, crear issue en GitHub o revisar logs del servidor.
