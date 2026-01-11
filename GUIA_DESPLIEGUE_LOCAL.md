# GUÍA DE DESPLIEGUE EN SERVIDOR LOCAL
## Sistema de Gestión de Cantina Escolar "Tita"

**Versión**: 1.0  
**Fecha**: 10 de Enero de 2026  
**Configuración**: Servidor Windows local con acceso en red

---

## 📋 REQUISITOS PREVIOS

### Hardware Mínimo
- **Procesador**: Intel Core i3 o equivalente
- **RAM**: 4 GB (8 GB recomendado)
- **Disco**: 20 GB libres
- **Red**: Conexión ethernet/WiFi estable

### Software Necesario
- ✅ Windows 10/11 Pro (64-bit)
- ✅ Python 3.13.x
- ✅ MySQL 8.0.x
- ✅ Git (opcional, para actualizaciones)

---

## 🚀 INSTALACIÓN PASO A PASO

### PASO 1: Instalar Python 3.13

1. Descargar desde: https://www.python.org/downloads/
2. **IMPORTANTE**: Marcar "Add Python to PATH"
3. Ejecutar instalador con "Install for all users"
4. Verificar instalación:
   ```powershell
   python --version
   # Debe mostrar: Python 3.13.x
   ```

### PASO 2: Instalar MySQL 8.0

1. Descargar MySQL Installer: https://dev.mysql.com/downloads/installer/
2. Elegir "Custom Installation"
3. Seleccionar:
   - MySQL Server 8.0.x
   - MySQL Workbench (opcional, pero recomendado)
4. Durante configuración:
   - **Root password**: L01G05S33Vice.42 (o tu contraseña)
   - Puerto: 3306 (por defecto)
   - Configuración: Development Machine
5. Verificar instalación:
   ```powershell
   mysql --version
   # Debe mostrar: mysql Ver 8.0.x
   ```

### PASO 3: Copiar archivos del proyecto

**Opción A: Desde otra PC** (recomendado)
```powershell
# Copiar carpeta completa desde la PC actual
# Desde: D:\anteproyecto20112025
# Hacia: D:\cantina_servidor\
```

**Opción B: Desde repositorio Git**
```powershell
cd D:\
git clone [URL_DEL_REPOSITORIO] cantina_servidor
cd cantina_servidor
```

### PASO 4: Crear base de datos MySQL

1. Abrir MySQL Command Line o MySQL Workbench
2. Conectar como root (password: L01G05S33Vice.42)
3. Ejecutar:
   ```sql
   CREATE DATABASE cantinatitadb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   SHOW DATABASES;
   -- Debe aparecer cantinatitadb en la lista
   ```

### PASO 5: Restaurar backup de base de datos

**Si tienes backup existente**:
```powershell
# Copiar archivo de backup a D:\backups_cantina\
mysql -u root -pL01G05S33Vice.42 cantinatitadb < D:\backups_cantina\backup_completo.sql
```

**Si es instalación nueva** (sin datos):
```powershell
cd D:\cantina_servidor
python manage.py migrate
python crear_datos_iniciales.py
```

### PASO 6: Crear entorno virtual de Python

```powershell
cd D:\cantina_servidor

# Crear virtual environment
python -m venv .venv

# Activar virtual environment
.\.venv\Scripts\Activate.ps1

# Tu prompt debe cambiar a: (.venv) PS D:\cantina_servidor>
```

### PASO 7: Instalar dependencias Python

```powershell
# Asegúrate de que el entorno virtual esté activado
pip install --upgrade pip

# Instalar todas las dependencias
pip install -r requirements.txt

# Verificar instalaciones críticas
pip list | Select-String "Django|mysqlclient|djangorestframework"
```

**Dependencias principales**:
- Django==5.2.8
- mysqlclient==2.2.4
- djangorestframework==3.15.1
- python-decouple==3.8
- Pillow==11.0.0
- reportlab==4.2.5
- openpyxl==3.1.5

### PASO 8: Configurar variables de entorno (.env)

El archivo `.env` ya debe existir. Verificar/actualizar:

```dotenv
# Base de datos
DB_NAME=cantinatitadb
DB_USER=root
DB_PASSWORD=L01G05S33Vice.42
DB_HOST=localhost
DB_PORT=3306

# Django
SECRET_KEY=wywfXkXzURUBroxWGSdL7uIDlmPi_hpJMFTc7vgpOgJ0c76bfhKWE-nwCcBdtKzDa6k
DEBUG=False

# Email (Gmail)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu_email@gmail.com
EMAIL_HOST_PASSWORD=abcdefghijklmnop  # 16 caracteres de App Password
```

**Para obtener App Password de Gmail**: Ver [GUIA_APP_PASSWORD_GMAIL.md](GUIA_APP_PASSWORD_GMAIL.md)

### PASO 9: Ejecutar configuración automática

```powershell
# Esto configurará: IP local, firewall, HTTPS
python configurar_servidor_local.py
```

El script preguntará:
- ✅ Configurar Gmail SMTP (ingresa App Password)
- ✅ Configurar ALLOWED_HOSTS (automático con IP local)
- ✅ Configurar Firewall (puertos 8000, 80, 443)
- ⏸️ Activar HTTPS (recomendado: NO para pruebas iniciales)

### PASO 10: Recopilar archivos estáticos

```powershell
python manage.py collectstatic --noinput
```

Debe copiar ~211 archivos a `staticfiles/`

### PASO 11: Verificar seguridad

```powershell
python auditoria_seguridad.py
```

**Resultado esperado**:
```
Total verificaciones: 27
Correctas: 27 ✅
Warnings: 0
Críticos: 0
```

---

## 🔧 CONFIGURACIÓN DE RED LOCAL

### Obtener IP local del servidor

```powershell
ipconfig | Select-String "IPv4"
```

Ejemplo de salida:
```
IPv4 Address: 192.168.100.10
```

Esta será la IP para acceder desde otras PCs.

### Configurar firewall de Windows

**Opción A: Automático** (recomendado)
```powershell
python configurar_servidor_local.py
# Seleccionar "s" en configuración de firewall
```

**Opción B: Manual**
```powershell
# Ejecutar PowerShell como Administrador
netsh advfirewall firewall add rule name="Django Server Port 8000" dir=in action=allow protocol=TCP localport=8000
netsh advfirewall firewall add rule name="HTTP Port 80" dir=in action=allow protocol=TCP localport=80
netsh advfirewall firewall add rule name="HTTPS Port 443" dir=in action=allow protocol=TCP localport=443
```

### Actualizar ALLOWED_HOSTS en settings.py

Ya debería estar configurado automáticamente:
```python
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver', '192.168.100.10']
```

Si tu IP cambia, edita [cantina_project/settings.py](cantina_project/settings.py) línea 30.

---

## ▶️ INICIAR EL SERVIDOR

### Desarrollo (para pruebas)

```powershell
# Activar entorno virtual
.\.venv\Scripts\Activate.ps1

# Iniciar servidor en todas las interfaces
python manage.py runserver 0.0.0.0:8000
```

**Acceso**:
- Desde esta PC: http://127.0.0.1:8000
- Desde otra PC: http://192.168.100.10:8000

### Producción (24/7 con Gunicorn)

1. **Instalar Gunicorn**:
   ```powershell
   pip install gunicorn
   ```

2. **Crear archivo de servicio** `start_server.bat`:
   ```batch
   @echo off
   cd D:\cantina_servidor
   call .venv\Scripts\activate.bat
   gunicorn cantina_project.wsgi:application --bind 0.0.0.0:8000 --workers 4 --log-file logs/gunicorn.log
   ```

3. **Ejecutar**:
   ```powershell
   .\start_server.bat
   ```

4. **Configurar como servicio de Windows** (opcional):
   - Usar NSSM (Non-Sucking Service Manager)
   - Descargar: https://nssm.cc/download
   - Configurar servicio para inicio automático

---

## 🧪 PRUEBAS DE FUNCIONAMIENTO

### 1. Verificar acceso a Django Admin

```
http://192.168.100.10:8000/admin
```

**Credenciales** (usuario administrador):
- Usuario: admin
- Contraseña: [la que configuraste]

### 2. Verificar Portal de Padres

```
http://192.168.100.10:8000/portal
```

### 3. Verificar API REST

```
http://192.168.100.10:8000/api/productos/
```

Debe retornar JSON con lista de productos.

### 4. Prueba desde otra PC

Desde cualquier PC en la misma red:

1. Abrir navegador
2. Ir a: `http://192.168.100.10:8000`
3. Debe cargar la página principal

**Si no funciona**:
- Verificar que firewall esté configurado
- Hacer ping: `ping 192.168.100.10`
- Verificar que el servidor esté corriendo

### 5. Prueba de envío de email

```powershell
python -c "from django.core.mail import send_mail; send_mail('Prueba', 'Mensaje', 'lucaspy14@gmail.com', ['otro_email@gmail.com']); print('Email enviado!')"
```

---

## 🔐 CONFIGURACIÓN SSL/HTTPS (Opcional)

### Opción A: Certificado Autofirmado (solo para pruebas)

1. **Instalar OpenSSL**:
   - Descargar: https://slproweb.com/products/Win32OpenSSL.html
   - Instalar Win64 OpenSSL

2. **Generar certificado**:
   ```powershell
   cd D:\cantina_servidor\certs
   openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
   ```

3. **Configurar Django**:
   ```powershell
   pip install django-sslserver
   python manage.py runsslserver 0.0.0.0:8000 --certificate certs/cert.pem --key certs/key.pem
   ```

### Opción B: Let's Encrypt (producción real)

Requiere:
- Dominio público (ejemplo: cantina-tita.edu.py)
- Puerto 80 abierto a internet
- Servidor web nginx/Apache

Pasos:
1. Instalar nginx o Apache
2. Instalar certbot
3. Ejecutar: `certbot --nginx -d cantina-tita.edu.py`
4. Configurar auto-renovación

**Ver**: [GUIA_SSL_LETSENCRYPT.md](GUIA_SSL_LETSENCRYPT.md) (próximamente)

---

## 📊 MANTENIMIENTO Y MONITOREO

### Backup Automático

Ya está configurado con tarea programada:
```powershell
& "D:\cantina_servidor\scripts\configurar_tarea_programada.ps1"
```

Backups diarios en: `D:\backups_cantina\`

### Ver Logs del Sistema

```powershell
# Logs de Django
Get-Content D:\cantina_servidor\logs\cantina.log -Tail 50

# Logs de seguridad
Get-Content D:\cantina_servidor\logs\security.log -Tail 50

# Logs de SQL
Get-Content D:\cantina_servidor\logs\sql.log -Tail 50
```

### Optimización de Base de Datos

**Mensual**:
```powershell
python ejecutar_optimizacion_bd.py
```

**Verificar índices**:
```powershell
python verificar_indices_explain.py
```

### Auditoría de Seguridad

**Semanal**:
```powershell
python auditoria_seguridad.py
```

Revisar: `logs/auditoria_seguridad_*.json`

---

## 🛠️ SOLUCIÓN DE PROBLEMAS

### Error: "No module named 'MySQLdb'"

```powershell
pip uninstall mysqlclient
pip install mysqlclient==2.2.4
```

Si falla, instalar Visual C++ Build Tools.

### Error: "Access denied for user 'root'@'localhost'"

1. Verificar contraseña en `.env`
2. Conectar manualmente a MySQL:
   ```powershell
   mysql -u root -p
   # Ingresa la contraseña
   ```
3. Si funciona, el problema es el archivo `.env`

### Error: "Port 8000 is already in use"

```powershell
# Ver qué proceso usa el puerto
netstat -ano | Select-String ":8000"

# Matar proceso (reemplaza PID)
taskkill /PID 1234 /F
```

### No se puede acceder desde otra PC

1. **Verificar firewall**:
   ```powershell
   netsh advfirewall firewall show rule name="Django Server Port 8000"
   ```

2. **Verificar IP del servidor**:
   ```powershell
   ipconfig | Select-String "IPv4"
   ```

3. **Hacer ping desde otra PC**:
   ```powershell
   ping 192.168.100.10
   ```

4. **Verificar que servidor esté en 0.0.0.0**:
   ```powershell
   python manage.py runserver 0.0.0.0:8000
   # NO usar: 127.0.0.1:8000
   ```

### Emails no se envían

1. Verificar App Password de Gmail (16 caracteres)
2. Ver guía: [GUIA_APP_PASSWORD_GMAIL.md](GUIA_APP_PASSWORD_GMAIL.md)
3. Probar manualmente:
   ```powershell
   python configurar_servidor_local.py
   # Seleccionar prueba de email
   ```

---

## 📱 ACCESO DESDE DISPOSITIVOS MÓVILES

El sistema es responsive y funciona en:
- ✅ Android (Chrome, Firefox)
- ✅ iOS (Safari, Chrome)
- ✅ Tablets

**URL desde móvil**:
```
http://192.168.100.10:8000/portal
```

**Requisito**: Dispositivo conectado a la misma red WiFi del servidor.

---

## 📚 DOCUMENTACIÓN ADICIONAL

- [MANUAL_PORTAL_PADRES.md](MANUAL_PORTAL_PADRES.md) - Guía para padres
- [MANUAL_ADMINISTRADORES.md](MANUAL_ADMINISTRADORES.md) - Guía para admins
- [DOCUMENTACION_API_REST.md](DOCUMENTACION_API_REST.md) - Endpoints API
- [GUIA_APP_PASSWORD_GMAIL.md](GUIA_APP_PASSWORD_GMAIL.md) - Configurar email
- [ESTADO_100_PRODUCCION.md](ESTADO_100_PRODUCCION.md) - Estado del sistema

---

## 📊 CHECKLIST DE INSTALACIÓN

Marca cada item al completarlo:

### Instalación Base
- [ ] Python 3.13 instalado y en PATH
- [ ] MySQL 8.0 instalado y funcionando
- [ ] Base de datos `cantinatitadb` creada
- [ ] Archivos del proyecto copiados a `D:\cantina_servidor\`

### Configuración Python
- [ ] Virtual environment creado (`.venv`)
- [ ] Dependencias instaladas (`requirements.txt`)
- [ ] Archivos estáticos recopilados (`collectstatic`)

### Configuración Sistema
- [ ] Archivo `.env` configurado correctamente
- [ ] Gmail App Password obtenida (16 caracteres)
- [ ] IP local configurada en `ALLOWED_HOSTS`
- [ ] CSRF_TRUSTED_ORIGINS configurado
- [ ] Firewall abierto (puertos 8000, 80, 443)

### Verificaciones
- [ ] `python auditoria_seguridad.py` → 27/27 OK
- [ ] `python manage.py migrate` → Sin errores
- [ ] Servidor inicia: `python manage.py runserver 0.0.0.0:8000`
- [ ] Acceso desde esta PC: http://127.0.0.1:8000/admin
- [ ] Acceso desde otra PC: http://[IP_LOCAL]:8000/admin
- [ ] Prueba de email exitosa

### Mantenimiento
- [ ] Backup automático configurado
- [ ] Usuario administrador creado
- [ ] Datos iniciales cargados
- [ ] Documentación revisada

---

## 📞 SOPORTE

**Soporte Técnico**: lucaspy14@gmail.com  
**Documentación**: D:\cantina_servidor\docs\  
**Logs**: D:\cantina_servidor\logs\  
**Backups**: D:\backups_cantina\

---

**Sistema**: Cantina Escolar "Tita" v1.0  
**Última actualización**: 10 de Enero de 2026  
**Estado**: Producción Ready ✅
