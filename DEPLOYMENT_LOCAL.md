# 🚀 Deployment Local - Guía Rápida

**Fecha:** 4 de Febrero 2026  
**Configuración:** Servidor Local (192.168.100.10)  
**Estado:** ✅ Configuración completada

---

## ✅ Configuración Actual

```
✓ SECRET_KEY: Segura (50 chars)
✓ DEBUG: False (producción)
✓ ALLOWED_HOSTS: 192.168.100.10, localhost, 127.0.0.1
✓ Email: Gmail configurado
✓ reCAPTCHA: Claves de producción
⚠ SSL: Desactivado (OK para servidor local)
⚠ DB User: root (cambiar a cantina_user recomendado)
```

---

## 🎯 Deployment Local en 3 Pasos

### PASO 1: Migrar Base de Datos

```powershell
# Activar entorno virtual
.\.venv\Scripts\activate

# Copiar .env.production como .env (temporal para pruebas)
Copy-Item entorno\.env.production entorno\.env.local

# Aplicar migraciones
cd backend
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Recolectar archivos estáticos
python manage.py collectstatic --noinput
```

### PASO 2: Ejecutar con Gunicorn

```powershell
# Opción A: Gunicorn (producción)
gunicorn cantina_project.wsgi:application --bind 0.0.0.0:8000 --workers 3

# Opción B: Django development server (solo testing)
python manage.py runserver 0.0.0.0:8000
```

### PASO 3: Probar Desde Otro Dispositivo

```
URL: http://192.168.100.10:8000
Admin: http://192.168.100.10:8000/admin
```

---

## 🔧 Crear Usuario MySQL Específico (Recomendado)

```sql
-- Conectar a MySQL
mysql -u root -p

-- Crear usuario
CREATE USER 'cantina_user'@'localhost' IDENTIFIED BY 'L01G05S33Vice.42';
GRANT ALL PRIVILEGES ON cantitatitadb.* TO 'cantina_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

Luego actualizar `entorno/.env.production`:
```bash
DB_USER=cantina_user
```

---

## 🌐 Opcional: SSL con Let's Encrypt (Servidor Local)

Si quieres acceso HTTPS desde internet:

### 1. Configurar DynDNS

```powershell
# Instalar cliente No-IP (Windows)
# Descargar de: https://www.noip.com/download
# Registrar dominio: cantitatita.ddns.net
```

### 2. Port Forwarding en Router

```
Router > Port Forwarding:
- Puerto externo: 80 → IP interna: 192.168.100.10 Puerto: 80
- Puerto externo: 443 → IP interna: 192.168.100.10 Puerto: 443
```

### 3. Instalar Certbot (Windows)

```powershell
# Descargar Certbot para Windows
# https://certbot.eff.org/instructions?ws=other&os=windows

# Obtener certificado
certbot certonly --standalone -d cantitatita.ddns.net
```

### 4. Configurar Gunicorn con SSL

```powershell
gunicorn cantina_project.wsgi:application `
  --bind 0.0.0.0:443 `
  --workers 3 `
  --certfile C:\Certbot\live\cantitatita.ddns.net\fullchain.pem `
  --keyfile C:\Certbot\live\cantitatita.ddns.net\privkey.pem
```

---

## ✅ Checklist de Verificación

### Antes de Usar en Producción

- [ ] Migraciones aplicadas sin errores
- [ ] Superusuario creado
- [ ] Static files recolectados
- [ ] Gunicorn arranca sin errores
- [ ] Admin panel accesible: http://192.168.100.10:8000/admin
- [ ] Login funciona
- [ ] POS funciona (crear venta de prueba)
- [ ] Portal de padres funciona
- [ ] Emails se envían correctamente
- [ ] reCAPTCHA se muestra en formularios

### Testing Inicial

```powershell
# Ejecutar tests
cd backend
python manage.py test

# Verificar deployment
python manage.py check --deploy
```

---

## 🆘 Solución de Problemas

### Error: "DisallowedHost at /"

```powershell
# Verificar ALLOWED_HOSTS en .env
# Debe incluir la IP desde donde accedes
```

### Error: "No module named 'gunicorn'"

```powershell
pip install gunicorn
```

### Error: "Can't connect to MySQL"

```powershell
# Verificar que MySQL está corriendo
# Verificar credenciales en .env.production
```

### Static files no cargan

```powershell
python manage.py collectstatic --noinput
# Verificar STATIC_ROOT en settings.py
```

---

## 📊 Siguiente Paso

Si todo funciona correctamente:

1. **Documentar configuración** - Crear archivo con IPs, puertos, credenciales
2. **Capacitar usuarios** - Personal de cantina y padres
3. **Monitoreo** - Revisar logs diariamente la primera semana
4. **Backups** - Configurar backup automático diario

---

## 🎉 ¡Listo!

Tu sistema ya está corriendo en el servidor local. 

**URL de acceso:** http://192.168.100.10:8000

Para deployment en internet real (Railway/VPS):
- Ver: `docs/DEPLOYMENT_GUIDE.md`
- Railway es la opción más simple (15 minutos)
