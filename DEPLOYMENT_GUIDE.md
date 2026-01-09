# 🚀 Guía de Deployment - Cantina Tita

## 📋 Checklist Pre-Deployment

### 1. Configuración de Entorno (.env)

#### 1.1 Crear archivo `.env` desde `.env.production`
```bash
cp .env.production .env
```

#### 1.2 Configurar variables críticas

**⚠️ IMPORTANTE: Cambiar estos valores en producción**

```env
# Django
SECRET_KEY=<generar_nueva_clave>  # Ver comando abajo
DEBUG=False  # NUNCA True en producción

# Base de Datos
DB_NAME=cantinatitadb
DB_USER=cantina_user  # NO usar root
DB_PASSWORD=<contraseña_segura>
DB_HOST=localhost
DB_PORT=3306

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=notificaciones@cantinatita.com.py
EMAIL_HOST_PASSWORD=<app_password_16_caracteres>

# reCAPTCHA (obtener en https://www.google.com/recaptcha/admin)
RECAPTCHA_PUBLIC_KEY=<clave_produccion>
RECAPTCHA_PRIVATE_KEY=<clave_produccion>

# MetrePay
METREPAY_API_TOKEN=<token_real_produccion>
METREPAY_BASE_URL=https://api.metrepay.com
```

### 2. Generar SECRET_KEY

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3. Configurar SMTP (Gmail)

#### Opción 1: Gmail App Password (Recomendado)
1. Ir a: https://myaccount.google.com/apppasswords
2. Iniciar sesión
3. Crear "Contraseña de aplicación" → Nombre: "Cantina Tita"
4. Copiar password de 16 caracteres en `.env`

#### Opción 2: SendGrid (100 emails/día gratis)
1. Registrarse: https://sendgrid.com
2. Crear API Key
3. Configurar en `.env`:
```env
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.tu_api_key
```

### 4. Base de Datos

#### 4.1 Crear usuario MySQL (NO usar root)
```sql
CREATE USER 'cantina_user'@'localhost' IDENTIFIED BY 'TU_PASSWORD_SEGURO';
GRANT ALL PRIVILEGES ON cantinatitadb.* TO 'cantina_user'@'localhost';
FLUSH PRIVILEGES;
```

#### 4.2 Aplicar migraciones
```bash
python manage.py migrate
```

#### 4.3 Crear superusuario
```bash
python manage.py createsuperuser
```

### 5. Archivos Estáticos

```bash
python manage.py collectstatic --noinput
```

### 6. Configurar HTTPS (Producción)

#### 6.1 Actualizar `settings.py` para HTTPS
```python
# En producción, agregar en settings.py:
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
```

#### 6.2 Actualizar ALLOWED_HOSTS
```python
ALLOWED_HOSTS = [
    'cantinatita.com.py',
    'www.cantinatita.com.py',
    'IP_DEL_SERVIDOR'
]
```

### 7. Servidor Web

#### Opción A: Gunicorn (Recomendado)
```bash
pip install gunicorn
gunicorn cantina_project.wsgi:application --bind 0.0.0.0:8000
```

#### Opción B: uWSGI
```bash
pip install uwsgi
uwsgi --http :8000 --module cantina_project.wsgi
```

### 8. Nginx (Proxy Reverso)

```nginx
server {
    listen 80;
    server_name cantinatita.com.py www.cantinatita.com.py;

    location /static/ {
        alias /ruta/a/static/;
    }

    location /media/ {
        alias /ruta/a/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 9. Supervisor (Mantener servidor corriendo)

Crear `/etc/supervisor/conf.d/cantina.conf`:
```ini
[program:cantina_tita]
command=/ruta/a/.venv/bin/gunicorn cantina_project.wsgi:application --bind 0.0.0.0:8000
directory=/ruta/a/proyecto
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/cantina_tita.log
```

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start cantina_tita
```

### 10. Backup Automático

Crear script `/home/backup_cantina.sh`:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
mysqldump -u cantina_user -p'PASSWORD' cantinatitadb > /backups/cantina_$DATE.sql
gzip /backups/cantina_$DATE.sql

# Eliminar backups mayores a 30 días
find /backups -name "cantina_*.sql.gz" -mtime +30 -delete
```

Agregar a crontab:
```bash
crontab -e
# Backup diario a las 2 AM
0 2 * * * /home/backup_cantina.sh
```

## 🧪 Testing Pre-Deployment

### 1. Tests Unitarios
```bash
python manage.py test
```

### 2. Verificar Sistema
```bash
python manage.py check --deploy
```

### 3. Probar SMTP
```bash
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Mensaje de prueba', 'from@example.com', ['to@example.com'])
```

## 📊 Monitoreo Post-Deployment

### 1. Logs
```bash
# Logs de Django
tail -f /var/log/cantina_tita.log

# Logs de Nginx
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log
```

### 2. Health Check
Crear endpoint `/health/` para monitoreo:
```python
# En urls.py
path('health/', lambda request: JsonResponse({'status': 'ok'}))
```

## ⚠️ Troubleshooting

### Error: Static files no se cargan
```bash
python manage.py collectstatic --clear
sudo chmod -R 755 /ruta/static/
```

### Error: 502 Bad Gateway (Nginx)
```bash
# Verificar que Gunicorn esté corriendo
ps aux | grep gunicorn
sudo supervisorctl status cantina_tita
```

### Error: Can't connect to MySQL
```bash
# Verificar permisos de usuario
mysql -u cantina_user -p
SHOW GRANTS FOR 'cantina_user'@'localhost';
```

## 🔒 Seguridad Adicional

### 1. Firewall (UFW)
```bash
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

### 2. Fail2Ban (Protección contra brute force)
```bash
sudo apt install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. SSL/TLS (Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d cantinatita.com.py -d www.cantinatita.com.py
```

## 📞 Contactos de Emergencia

- **Desarrollador:** [Tu nombre/contacto]
- **Hosting:** [Proveedor/contacto]
- **Dominio:** [Registrador/contacto]
- **Base de Datos:** [Admin/contacto]

## ✅ Checklist Final

- [ ] SECRET_KEY generado y único
- [ ] DEBUG=False
- [ ] ALLOWED_HOSTS configurado
- [ ] BASE DE DATOS con usuario no-root
- [ ] SMTP configurado y probado
- [ ] reCAPTCHA con claves de producción
- [ ] HTTPS habilitado (SSL/TLS)
- [ ] Static files recolectados
- [ ] Migraciones aplicadas
- [ ] Superusuario creado
- [ ] Gunicorn corriendo
- [ ] Nginx configurado
- [ ] Supervisor configurado
- [ ] Backup automático configurado
- [ ] Firewall habilitado
- [ ] Logs monitoreados
- [ ] Tests pasando

---

**Última actualización:** Enero 2026
