# ==================== GUÍA DE DESPLIEGUE - CANTINA TITA ====================

## REQUISITOS PREVIOS

1. **Sistema Operativo**: Ubuntu 20.04/22.04 LTS o similar
2. **Python**: 3.9 o superior
3. **MySQL**: 8.0.x
4. **Nginx**: 1.18 o superior
5. **Git**: Para clonar el repositorio

---

## PASO 1: PREPARAR EL SERVIDOR

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
sudo apt install python3 python3-pip python3-venv mysql-server nginx git -y

# Instalar MySQL connector
sudo apt install libmysqlclient-dev pkg-config -y

# Crear usuario del sistema para la aplicación
sudo useradd -m -s /bin/bash cantitatita
```

---

## PASO 2: CONFIGURAR MYSQL

```bash
# Acceder a MySQL
sudo mysql -u root -p

# Crear base de datos y usuario
CREATE DATABASE cantitatitadb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'cantitatita_user'@'localhost' IDENTIFIED BY 'TuPasswordSegura123!';
GRANT ALL PRIVILEGES ON cantitatitadb.* TO 'cantitatita_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;

# Importar dump de la base de datos (si existe)
mysql -u cantitatita_user -p cantitatitadb < /path/to/backup.sql
```

---

## PASO 3: CLONAR Y CONFIGURAR PROYECTO

```bash
# Ir al directorio web
cd /var/www

# Clonar repositorio (o copiar archivos)
sudo git clone https://github.com/tu-usuario/cantitatita.git
# O copiar archivos: sudo cp -r /source/cantitatita /var/www/

# Cambiar propietario
sudo chown -R cantitatita:cantitatita /var/www/cantitatita

# Cambiar a usuario cantitatita
sudo su - cantitatita
cd /var/www/cantitatita

# Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# Actualizar pip
pip install --upgrade pip

# Instalar dependencias
pip install -r requirements.txt
```

---

## PASO 4: CONFIGURAR VARIABLES DE ENTORNO

```bash
# Crear archivo de variables de entorno
nano /var/www/cantitatita/.env

# Contenido del archivo .env:
SECRET_KEY=genera-una-clave-secreta-super-segura-aqui-con-50-caracteres-minimo
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com,192.168.100.10

DATABASE_ENGINE=django.db.backends.mysql
DATABASE_NAME=cantitatitadb
DATABASE_USER=cantitatita_user
DATABASE_PASSWORD=TuPasswordSegura123!
DATABASE_HOST=localhost
DATABASE_PORT=3306

# Configuración SMTP (opcional, para emails)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password

# Guardar y cerrar (Ctrl+O, Enter, Ctrl+X)
```

---

## PASO 5: CONFIGURAR DJANGO

```bash
# Asegurar que estás en el entorno virtual
source /var/www/cantitatita/.venv/bin/activate

# Migraciones de base de datos
python manage.py makemigrations
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Recolectar archivos estáticos
python manage.py collectstatic --noinput

# Crear directorio de logs
mkdir -p /var/www/cantitatita/logs
chmod 755 /var/www/cantitatita/logs
```

---

## PASO 6: INSTALAR Y CONFIGURAR GUNICORN

```bash
# Instalar Gunicorn (si no está en requirements.txt)
pip install gunicorn

# Probar que Gunicorn funciona
gunicorn --bind 127.0.0.1:8000 cantitatita.wsgi:application

# Si funciona correctamente, presionar Ctrl+C para detener
```

**Copiar archivo de configuración de Gunicorn:**

```bash
# El archivo gunicorn_config.py ya está en el proyecto
# Verificar que existe
ls -l /var/www/cantitatita/gunicorn_config.py
```

---

## PASO 7: CONFIGURAR SYSTEMD SERVICE

```bash
# Salir del usuario cantitatita
exit

# Copiar archivo de servicio
sudo cp /var/www/cantitatita/deployment/cantitatita.service /etc/systemd/system/

# Editar el archivo si es necesario (ajustar rutas, usuario, passwords)
sudo nano /etc/systemd/system/cantitatita.service

# Recargar systemd
sudo systemctl daemon-reload

# Habilitar servicio para inicio automático
sudo systemctl enable cantitatita

# Iniciar servicio
sudo systemctl start cantitatita

# Verificar estado
sudo systemctl status cantitatita

# Ver logs en tiempo real
sudo journalctl -u cantitatita -f
```

---

## PASO 8: CONFIGURAR NGINX

```bash
# Copiar configuración de Nginx
sudo cp /var/www/cantitatita/deployment/nginx.conf /etc/nginx/sites-available/cantitatita

# Editar configuración (cambiar dominio, IPs, etc.)
sudo nano /etc/nginx/sites-available/cantitatita

# Crear symlink
sudo ln -s /etc/nginx/sites-available/cantitatita /etc/nginx/sites-enabled/

# Eliminar sitio por defecto (opcional)
sudo rm /etc/nginx/sites-enabled/default

# Probar configuración de Nginx
sudo nginx -t

# Si todo está OK, reiniciar Nginx
sudo systemctl restart nginx

# Habilitar Nginx en inicio automático
sudo systemctl enable nginx
```

---

## PASO 9: CONFIGURAR FIREWALL

```bash
# Permitir HTTP y HTTPS
sudo ufw allow 'Nginx Full'

# O específicamente:
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Si SSH está bloqueado, permitir antes
sudo ufw allow 22/tcp

# Habilitar firewall
sudo ufw enable

# Ver estado
sudo ufw status
```

---

## PASO 10: CONFIGURAR SSL (OPCIONAL - RECOMENDADO)

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtener certificado SSL
sudo certbot --nginx -d tu-dominio.com -d www.tu-dominio.com

# Seguir las instrucciones en pantalla

# Certbot configurará automáticamente Nginx y agregará renovación automática
```

---

## COMANDOS ÚTILES PARA ADMINISTRACIÓN

### Reiniciar servicios:
```bash
# Reiniciar Gunicorn
sudo systemctl restart cantitatita

# Reiniciar Nginx
sudo systemctl restart nginx

# Reiniciar MySQL
sudo systemctl restart mysql
```

### Ver logs:
```bash
# Logs de Gunicorn (desde systemd)
sudo journalctl -u cantitatita -f

# Logs de Gunicorn (archivos)
tail -f /var/www/cantitatita/logs/gunicorn_error.log
tail -f /var/www/cantitatita/logs/gunicorn_access.log

# Logs de Nginx
sudo tail -f /var/log/nginx/cantitatita_access.log
sudo tail -f /var/log/nginx/cantitatita_error.log

# Logs de MySQL
sudo tail -f /var/log/mysql/error.log
```

### Actualizar aplicación:
```bash
# Cambiar a usuario cantitatita
sudo su - cantitatita
cd /var/www/cantitatita

# Activar entorno virtual
source .venv/bin/activate

# Pull de cambios (si usas git)
git pull origin main

# Instalar nuevas dependencias
pip install -r requirements.txt

# Migraciones
python manage.py migrate

# Collectstatic
python manage.py collectstatic --noinput

# Salir de usuario cantitatita
exit

# Reiniciar servicio
sudo systemctl restart cantitatita
```

---

## SEGURIDAD ADICIONAL

### 1. **Cambiar puerto SSH (recomendado)**
```bash
sudo nano /etc/ssh/sshd_config
# Cambiar Port 22 a Port 2222 (por ejemplo)
sudo systemctl restart sshd
```

### 2. **Configurar fail2ban**
```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. **Configurar backups automáticos de MySQL**
```bash
# Crear script de backup
sudo nano /usr/local/bin/backup_cantitatita.sh

# Contenido del script:
#!/bin/bash
FECHA=$(date +%Y%m%d_%H%M%S)
mysqldump -u cantitatita_user -p'TuPasswordSegura123!' cantitatitadb > /backups/cantitatita_$FECHA.sql
find /backups -name "cantitatita_*.sql" -mtime +7 -delete

# Dar permisos de ejecución
sudo chmod +x /usr/local/bin/backup_cantitatita.sh

# Agregar a crontab (backup diario a las 2 AM)
sudo crontab -e
0 2 * * * /usr/local/bin/backup_cantitatita.sh
```

---

## VERIFICACIÓN FINAL

1. **Acceder a la aplicación**: http://tu-dominio.com o http://192.168.100.10
2. **Probar login**: Usar credenciales de superusuario
3. **Verificar funcionalidades**: POS, Reportes, Portal Cliente, etc.
4. **Revisar logs**: Asegurar que no hay errores
5. **Probar rendimiento**: Hacer varias transacciones simultáneas

---

## MONITOREO Y MANTENIMIENTO

- **Logs diarios**: Revisar logs de errores
- **Backups**: Verificar que backups automáticos funcionen
- **Actualizaciones**: Mantener sistema y dependencias actualizadas
- **Certificados SSL**: Certbot renueva automáticamente, verificar que funcione
- **Espacio en disco**: Monitorear con `df -h`
- **Uso de memoria**: Monitorear con `free -h` y `htop`

---

¡Despliegue completado! 🚀
