# 🚀 Guía de Deployment - Cantina Tita
## Despliegue en Producción con Gunicorn + Nginx

---

## 📋 ÍNDICE

1. [Requisitos Previos](#requisitos-previos)
2. [Preparación del Servidor](#preparación-del-servidor)
3. [Instalación de Python y Dependencias](#instalación-de-python)
4. [Configuración de la Aplicación](#configuración-aplicación)
5. [Configuración de Gunicorn](#configuración-gunicorn)
6. [Configuración de Nginx](#configuración-nginx)
7. [Configuración de Systemd](#configuración-systemd)
8. [SSL/HTTPS con Let's Encrypt](#ssl-https)
9. [Monitoreo y Logs](#monitoreo-logs)
10. [Mantenimiento](#mantenimiento)

---

<a name="requisitos-previos"></a>
## 1. 📦 REQUISITOS PREVIOS

### Servidor Recomendado
- **OS**: Ubuntu 22.04 LTS o Debian 11+
- **RAM**: Mínimo 2GB (recomendado 4GB)
- **CPU**: 2 cores mínimo
- **Disco**: 20GB mínimo (recomendado 50GB)
- **Acceso**: SSH con usuario sudo

### Dominio y DNS
- Dominio registrado (ej: `cantinatita.com.py`)
- DNS apuntando al servidor (A record)

### Software Base
```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias básicas
sudo apt install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    git \
    nginx \
    mysql-server \
    supervisor \
    certbot \
    python3-certbot-nginx
```

---

<a name="preparación-del-servidor"></a>
## 2. 🔧 PREPARACIÓN DEL SERVIDOR

### 2.1 Crear Usuario para la Aplicación
```bash
# Crear usuario 'cantina'
sudo adduser cantina
sudo usermod -aG sudo cantina

# Cambiar a usuario cantina
su - cantina
```

### 2.2 Configurar Firewall
```bash
# Permitir SSH, HTTP y HTTPS
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 2.3 Configurar MySQL
```bash
# Ejecutar instalación segura
sudo mysql_secure_installation

# Crear base de datos
sudo mysql -u root -p

# En MySQL:
CREATE DATABASE cantinatitadb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'cantina_user'@'localhost' IDENTIFIED BY 'CONTRASEÑA_SEGURA_AQUI';
GRANT ALL PRIVILEGES ON cantinatitadb.* TO 'cantina_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

---

<a name="instalación-de-python"></a>
## 3. 🐍 INSTALACIÓN DE PYTHON Y DEPENDENCIAS

### 3.1 Clonar Repositorio
```bash
# Directorio de aplicación
sudo mkdir -p /var/www/cantinatita
sudo chown cantina:cantina /var/www/cantinatita
cd /var/www/cantinatita

# Clonar desde Git (o copiar archivos)
git clone https://github.com/tu-usuario/cantinatita.git .

# O subir archivos vía SCP:
# scp -r D:\anteproyecto20112025\* cantina@servidor:/var/www/cantinatita/
```

### 3.2 Crear Entorno Virtual
```bash
# Crear venv
python3.11 -m venv venv

# Activar venv
source venv/bin/activate

# Actualizar pip
pip install --upgrade pip setuptools wheel
```

### 3.3 Instalar Dependencias
```bash
# Instalar requirements
pip install -r requirements.txt

# Instalar Gunicorn
pip install gunicorn

# Instalar mysqlclient (si no está en requirements)
pip install mysqlclient

# Instalar gevent para workers async
pip install gevent
```

---

<a name="configuración-aplicación"></a>
## 4. ⚙️ CONFIGURACIÓN DE LA APLICACIÓN

### 4.1 Configurar Variables de Entorno (.env)
```bash
# Crear archivo .env
nano /var/www/cantinatita/.env
```

**Contenido del archivo .env para PRODUCCIÓN**:
```env
# Django
SECRET_KEY=GENERAR_CLAVE_SEGURA_DE_50_CARACTERES_MINIMO
DEBUG=False
ALLOWED_HOSTS=cantinatita.com.py,www.cantinatita.com.py

# Base de datos
DB_NAME=cantinatitadb
DB_USER=cantina_user
DB_PASSWORD=CONTRASEÑA_SEGURA_AQUI
DB_HOST=localhost
DB_PORT=3306

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu_email@gmail.com
EMAIL_HOST_PASSWORD=tu_app_password_aqui

# Redis (opcional, para cache/sessions)
REDIS_URL=redis://127.0.0.1:6379/0

# Seguridad HTTPS
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
X_FRAME_OPTIONS=DENY

# CSRF
CSRF_TRUSTED_ORIGINS=https://cantinatita.com.py,https://www.cantinatita.com.py
```

**Generar SECRET_KEY segura**:
```bash
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### 4.2 Configurar settings.py
Asegurar que `settings.py` use variables de entorno:
```python
from decouple import config

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')

# ... resto de configuración
```

### 4.3 Ejecutar Migraciones y Collectstatic
```bash
# Activar venv
source /var/www/cantinatita/venv/bin/activate

# Migraciones
python manage.py makemigrations
python manage.py migrate

# Recopilar archivos estáticos
python manage.py collectstatic --noinput

# Crear superusuario
python manage.py createsuperuser
```

### 4.4 Verificar Permisos
```bash
# Directorio de logs
mkdir -p /var/www/cantinatita/logs
sudo chown -R cantina:www-data /var/www/cantinatita
sudo chmod -R 755 /var/www/cantinatita
sudo chmod -R 775 /var/www/cantinatita/logs
sudo chmod -R 775 /var/www/cantinatita/media
```

---

<a name="configuración-gunicorn"></a>
## 5. 🦄 CONFIGURACIÓN DE GUNICORN

### 5.1 Crear Archivo de Configuración
```bash
nano /var/www/cantinatita/gunicorn_config.py
```

**Contenido**:
```python
"""
Configuración de Gunicorn para Cantina Tita
"""
import multiprocessing

# Directorio de trabajo
chdir = '/var/www/cantinatita'

# Socket UNIX (mejor rendimiento que TCP)
bind = 'unix:/var/www/cantinatita/gunicorn.sock'

# Workers
workers = multiprocessing.cpu_count() * 2 + 1  # Fórmula recomendada
worker_class = 'gevent'  # Async workers para mejor concurrencia
worker_connections = 1000
max_requests = 1000  # Reciclar workers cada 1000 requests
max_requests_jitter = 50

# Timeouts
timeout = 120
graceful_timeout = 30
keepalive = 2

# Logging
accesslog = '/var/www/cantinatita/logs/gunicorn_access.log'
errorlog = '/var/www/cantinatita/logs/gunicorn_error.log'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'cantitatita_gunicorn'

# Server mechanics
daemon = False  # Systemd maneja el daemonizado
pidfile = '/var/www/cantinatita/gunicorn.pid'
user = 'cantina'
group = 'www-data'
umask = 0o007

# SSL (si no usas Nginx como proxy)
# keyfile = '/etc/letsencrypt/live/cantinatita.com.py/privkey.pem'
# certfile = '/etc/letsencrypt/live/cantinatita.com.py/fullchain.pem'
```

### 5.2 Script de Inicio de Gunicorn
```bash
nano /var/www/cantinatita/start_gunicorn.sh
```

**Contenido**:
```bash
#!/bin/bash

NAME="cantitatita"
DIR=/var/www/cantinatita
USER=cantina
GROUP=www-data
WORKERS=5
BIND=unix:/var/www/cantinatita/gunicorn.sock
DJANGO_SETTINGS_MODULE=cantina_project.settings
DJANGO_WSGI_MODULE=cantina_project.wsgi
LOG_LEVEL=info

cd $DIR
source venv/bin/activate

export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DIR:$PYTHONPATH

exec gunicorn ${DJANGO_WSGI_MODULE}:application \
  --config /var/www/cantinatita/gunicorn_config.py \
  --name $NAME \
  --workers $WORKERS \
  --user=$USER \
  --group=$GROUP \
  --bind=$BIND \
  --log-level=$LOG_LEVEL \
  --log-file=-
```

```bash
# Dar permisos de ejecución
chmod +x /var/www/cantinatita/start_gunicorn.sh
```

---

<a name="configuración-nginx"></a>
## 6. 🌐 CONFIGURACIÓN DE NGINX

### 6.1 Crear Configuración del Sitio
```bash
sudo nano /etc/nginx/sites-available/cantitatita
```

**Contenido**:
```nginx
# Redirección de www a no-www
server {
    listen 80;
    listen [::]:80;
    server_name www.cantitatita.com.py;
    return 301 http://cantitatita.com.py$request_uri;
}

# Configuración principal
server {
    listen 80;
    listen [::]:80;
    server_name cantitatita.com.py;

    # Logging
    access_log /var/log/nginx/cantitatita_access.log;
    error_log /var/log/nginx/cantitatita_error.log;

    # Client body size (para uploads)
    client_max_body_size 75M;

    # Archivos estáticos
    location /static/ {
        alias /var/www/cantitatita/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Archivos media (uploads)
    location /media/ {
        alias /var/www/cantitatita/media/;
        expires 7d;
        add_header Cache-Control "public";
    }

    # Proxy a Gunicorn
    location / {
        proxy_pass http://unix:/var/www/cantinatita/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
        
        # Buffering
        proxy_buffering off;
        proxy_redirect off;
    }

    # Seguridad
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
}
```

### 6.2 Activar Sitio
```bash
# Crear symlink
sudo ln -s /etc/nginx/sites-available/cantitatita /etc/nginx/sites-enabled/

# Eliminar sitio por defecto
sudo rm /etc/nginx/sites-enabled/default

# Verificar configuración
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx
```

---

<a name="configuración-systemd"></a>
## 7. 🔄 CONFIGURACIÓN DE SYSTEMD

### 7.1 Crear Servicio Systemd
```bash
sudo nano /etc/systemd/system/cantitatita.service
```

**Contenido**:
```ini
[Unit]
Description=Cantina Tita Gunicorn Application
After=network.target mysql.service

[Service]
Type=notify
User=cantina
Group=www-data
WorkingDirectory=/var/www/cantitatita
Environment="PATH=/var/www/cantitatita/venv/bin"
EnvironmentFile=/var/www/cantitatita/.env
ExecStart=/var/www/cantitatita/venv/bin/gunicorn \
    --config /var/www/cantitatita/gunicorn_config.py \
    cantina_project.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

# Restart
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

### 7.2 Habilitar y Iniciar Servicio
```bash
# Recargar systemd
sudo systemctl daemon-reload

# Habilitar para inicio automático
sudo systemctl enable cantitatita

# Iniciar servicio
sudo systemctl start cantitatita

# Verificar estado
sudo systemctl status cantitatita

# Ver logs
sudo journalctl -u cantitatita -f
```

### 7.3 Comandos Útiles
```bash
# Reiniciar aplicación
sudo systemctl restart cantitatita

# Detener aplicación
sudo systemctl stop cantitatita

# Ver logs en tiempo real
sudo journalctl -u cantitatita -f

# Ver últimos 100 logs
sudo journalctl -u cantitatita -n 100
```

---

<a name="ssl-https"></a>
## 8. 🔒 SSL/HTTPS CON LET'S ENCRYPT

### 8.1 Instalar Certificado
```bash
# Detener Nginx temporalmente
sudo systemctl stop nginx

# Obtener certificado
sudo certbot certonly --standalone -d cantitatita.com.py -d www.cantitatita.com.py

# O con Nginx plugin (si Nginx está corriendo)
sudo certbot --nginx -d cantitatita.com.py -d www.cantitatita.com.py
```

### 8.2 Actualizar Configuración Nginx para HTTPS
```bash
sudo nano /etc/nginx/sites-available/cantitatita
```

**Agregar/Modificar**:
```nginx
# Redirigir HTTP a HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name cantitatita.com.py www.cantitatita.com.py;
    return 301 https://cantitatita.com.py$request_uri;
}

# HTTPS
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name cantitatita.com.py;

    # Certificados SSL
    ssl_certificate /etc/letsencrypt/live/cantitatita.com.py/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/cantitatita.com.py/privkey.pem;
    ssl_trusted_certificate /etc/letsencrypt/live/cantitatita.com.py/chain.pem;

    # SSL Protocols y Ciphers
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers on;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;

    # ... resto de configuración igual que antes ...
}
```

### 8.3 Renovación Automática
```bash
# Test renovación
sudo certbot renew --dry-run

# Certbot ya crea un cron job automático en /etc/cron.d/certbot
# Verificar:
sudo cat /etc/cron.d/certbot

# Forzar renovación manual si es necesario
sudo certbot renew --force-renewal
sudo systemctl reload nginx
```

---

<a name="monitoreo-logs"></a>
## 9. 📊 MONITOREO Y LOGS

### 9.1 Ubicaciones de Logs
```bash
# Logs de aplicación
/var/www/cantitatita/logs/gunicorn_access.log
/var/www/cantitatita/logs/gunicorn_error.log
/var/www/cantitatita/logs/backup.log
/var/www/cantitatita/logs/impresora.log

# Logs de Nginx
/var/log/nginx/cantitatita_access.log
/var/log/nginx/cantitatita_error.log

# Logs de Systemd
sudo journalctl -u cantitatita
```

### 9.2 Monitoreo con tail
```bash
# Ver logs en tiempo real
tail -f /var/www/cantitatita/logs/gunicorn_error.log
tail -f /var/log/nginx/cantitatita_error.log
sudo journalctl -u cantitatita -f
```

### 9.3 Logrotate (Rotar logs automáticamente)
```bash
sudo nano /etc/logrotate.d/cantitatita
```

**Contenido**:
```
/var/www/cantitatita/logs/*.log {
    daily
    rotate 30
    missingok
    compress
    delaycompress
    notifempty
    create 0640 cantina www-data
    sharedscripts
    postrotate
        systemctl reload cantitatita > /dev/null 2>&1 || true
    endscript
}
```

---

<a name="mantenimiento"></a>
## 10. 🔧 MANTENIMIENTO

### 10.1 Actualizar Aplicación
```bash
# Ir al directorio
cd /var/www/cantitatita

# Pull cambios (si usas Git)
git pull origin main

# Activar venv
source venv/bin/activate

# Actualizar dependencias
pip install -r requirements.txt --upgrade

# Migraciones
python manage.py migrate

# Collectstatic
python manage.py collectstatic --noinput

# Reiniciar servicios
sudo systemctl restart cantitatita
sudo systemctl reload nginx
```

### 10.2 Backup Automático
```bash
# Crear script de backup
nano /var/www/cantitatita/backup_produccion.sh
```

**Contenido**:
```bash
#!/bin/bash
BACKUP_DIR="/var/backups/cantitatita"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup BD
mysqldump -u cantina_user -p'PASSWORD' cantinatitadb > $BACKUP_DIR/db_$DATE.sql
gzip $BACKUP_DIR/db_$DATE.sql

# Backup media
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /var/www/cantitatita/media/

# Eliminar backups antiguos (más de 30 días)
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup completado: $DATE"
```

**Agregar a crontab**:
```bash
crontab -e

# Backup diario a las 3 AM
0 3 * * * /var/www/cantitatita/backup_produccion.sh >> /var/www/cantitatita/logs/backup.log 2>&1
```

### 10.3 Monitoreo de Recursos
```bash
# CPU y Memoria
htop

# Espacio en disco
df -h

# Uso de BD
sudo du -sh /var/lib/mysql/

# Procesos de Gunicorn
ps aux | grep gunicorn

# Estado del servicio
sudo systemctl status cantitatita nginx mysql
```

---

## ✅ CHECKLIST FINAL

- [ ] Servidor actualizado
- [ ] Usuario 'cantina' creado
- [ ] Firewall configurado (SSH, HTTP, HTTPS)
- [ ] MySQL instalado y BD creada
- [ ] Python 3.11+ y venv creado
- [ ] Dependencias instaladas
- [ ] .env configurado con valores de producción
- [ ] DEBUG=False
- [ ] SECRET_KEY única
- [ ] ALLOWED_HOSTS configurado
- [ ] Migraciones ejecutadas
- [ ] collectstatic ejecutado
- [ ] Superusuario creado
- [ ] Permisos correctos (cantina:www-data)
- [ ] Gunicorn configurado
- [ ] Nginx configurado
- [ ] Systemd service creado y habilitado
- [ ] SSL/HTTPS con Let's Encrypt
- [ ] Renovación automática de certificados
- [ ] Logs rotando con logrotate
- [ ] Backup automático configurado
- [ ] Probado desde navegador (HTTP y HTTPS)
- [ ] Probado admin (/admin/)
- [ ] Probado POS
- [ ] Probado portal padres

---

## 🆘 TROUBLESHOOTING

### Error: Bad Gateway 502
```bash
# Verificar que Gunicorn esté corriendo
sudo systemctl status cantitatita

# Ver logs
sudo journalctl -u cantitatita -n 50

# Verificar socket
ls -la /var/www/cantitatita/gunicorn.sock

# Reiniciar
sudo systemctl restart cantitatita
```

### Error: Permission Denied
```bash
# Verificar permisos
sudo chown -R cantina:www-data /var/www/cantitatita
sudo chmod -R 755 /var/www/cantitatita
sudo chmod 775 /var/www/cantitatita/logs
```

### Error: Static Files 404
```bash
# Re-ejecutar collectstatic
source /var/www/cantitatita/venv/bin/activate
python manage.py collectstatic --noinput

# Verificar ruta en Nginx
ls -la /var/www/cantitatita/staticfiles/
```

---

**Fecha**: Enero 2026  
**Versión**: 1.0  
**Autor**: Sistema Cantina Tita
