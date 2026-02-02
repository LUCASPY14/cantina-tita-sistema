# 🔧 PROBLEMAS RESUELTOS - Servidor Local
**Fecha**: 10 de Enero de 2026, 21:50

---

## ❌ PROBLEMAS DETECTADOS EN LOGS

### 1. Archivos estáticos no se servían (404)
```
WARNING "GET /static/admin/css/base.css HTTP/1.1" 404 179
WARNING "GET /static/admin/js/theme.js HTTP/1.1" 404 179
```

**Causa**: DEBUG=False no sirve archivos estáticos automáticamente

**Solución aplicada**: 
- ✅ Cambiado DEBUG=True en `.env` para pruebas locales
- Archivos estáticos ahora se sirven desde `/static/`

### 2. Error 500 en login
```
ERROR "POST /admin/login/?next=/admin/ HTTP/1.1" 500 145
```

**Causa probable**: 
- Email SMTP configurado incorrectamente (contraseña de 12 caracteres vs 16)
- Con DEBUG=True verás el error real en el navegador

**Solución pendiente**:
- Obtener App Password correcta de Gmail (16 caracteres)
- Ver: [GUIA_APP_PASSWORD_GMAIL.md](GUIA_APP_PASSWORD_GMAIL.md)

### 3. URLs incorrectas (404)
```
WARNING "GET /portal HTTP/1.1" 404 179
WARNING "GET /api HTTP/1.1" 404 179
```

**Causa**: URLs mal documentadas

**Solución**: Usar las URLs correctas

---

## ✅ URLs CORRECTAS DEL SISTEMA

### Panel de Administración
```
✅ http://192.168.100.10:8000/admin/
```

### Portal de Clientes (Padres)
```
❌ http://192.168.100.10:8000/portal       (INCORRECTO)
✅ http://192.168.100.10:8000/clientes/     (CORRECTO)
```

### API REST
```
❌ http://192.168.100.10:8000/api          (INCORRECTO)
✅ http://192.168.100.10:8000/api/v1/      (CORRECTO)
```

### Documentación API
```
✅ http://192.168.100.10:8000/api/docs/    (Swagger UI)
✅ http://192.168.100.10:8000/api/redoc/   (ReDoc)
✅ http://192.168.100.10:8000/api/schema/  (OpenAPI Schema)
```

### POS (Punto de Venta)
```
✅ http://192.168.100.10:8000/pos/
```

### Dashboard
```
✅ http://192.168.100.10:8000/dashboard/
```

---

## 🔐 CONFIGURACIÓN ACTUALIZADA

### .env (Cambios aplicados)

**ANTES**:
```dotenv
DEBUG=False  # No servía archivos estáticos
```

**AHORA**:
```dotenv
DEBUG=True   # Sirve archivos estáticos automáticamente
```

> **Nota**: Cuando migres a producción real con nginx/Apache, volver a DEBUG=False

---

## 📋 PRUEBAS ACTUALIZADAS

### 1. Desde esta PC
```bash
# Admin
http://127.0.0.1:8000/admin/

# Portal Clientes
http://127.0.0.1:8000/clientes/

# API
http://127.0.0.1:8000/api/v1/
http://127.0.0.1:8000/api/docs/
```

### 2. Desde otra PC en la red
```bash
# Admin
http://192.168.100.10:8000/admin/

# Portal Clientes
http://192.168.100.10:8000/clientes/

# API
http://192.168.100.10:8000/api/v1/productos/
http://192.168.100.10:8000/api/docs/
```

### 3. Login Admin

**Credenciales** (si no tienes usuario):
```bash
# Crear superusuario
python manage.py createsuperuser
```

**URL Login**:
```
http://192.168.100.10:8000/admin/
```

---

## 🐛 DEBUGGING

Con DEBUG=True ahora verás:

1. **Errores detallados**: Stack trace completo en el navegador
2. **Archivos estáticos**: Se sirven automáticamente desde `/static/`
3. **Debug toolbar**: Disponible en `/__debug__/`
4. **SQL queries**: Visibles en debug toolbar

### Ver error 500 real

Vuelve a intentar login en:
```
http://192.168.100.10:8000/admin/
```

Si falla, verás el error completo en el navegador.

---

## ⚙️ CONFIGURACIÓN PRODUCCIÓN vs DESARROLLO

### DESARROLLO (actual - para pruebas)
```dotenv
DEBUG=True
# Pros: Sirve archivos estáticos, errores detallados
# Contras: Menos seguro, más lento
```

### PRODUCCIÓN (cuando migres a servidor real)
```dotenv
DEBUG=False
# + Instalar whitenoise o configurar nginx
# + Ejecutar: python manage.py collectstatic
```

**Instalar whitenoise** (recomendado para producción):
```bash
pip install whitenoise
```

Agregar a `settings.py`:
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Agregar aquí
    ...
]
```

---

## 📝 PRÓXIMOS PASOS

1. ✅ **Servidor reiniciado** con DEBUG=True
2. 🔄 **Probar nuevamente desde navegador**:
   - http://192.168.100.10:8000/admin/
   - http://192.168.100.10:8000/clientes/
   - http://192.168.100.10:8000/api/docs/

3. ⏰ **Ver error real de login** (si persiste)
4. ⏰ **Corregir App Password Gmail** (si el error es de email)
5. 📚 **Actualizar documentación** con URLs correctas

---

## 🆘 SI PERSISTE ERROR 500 EN LOGIN

El error probablemente es uno de estos:

### A. Error de Email (más probable)
```python
# En settings.py, cambiar temporalmente:
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

Esto imprimirá emails en consola en lugar de enviarlos.

### B. Error de Base de Datos
```bash
# Ejecutar migraciones
python manage.py migrate
```

### C. Error de Usuario
```bash
# Crear superusuario
python manage.py createsuperuser
# Usuario: admin
# Email: admin@example.com
# Password: tu_contraseña
```

---

**Última actualización**: 10 de Enero de 2026, 21:50  
**Estado**: Servidor reiniciado con DEBUG=True  
**Siguiente acción**: Probar http://192.168.100.10:8000/admin/
