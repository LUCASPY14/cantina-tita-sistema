# Guía de Instalación - Mejoras Críticas
# Cantina POS System

## 📋 REQUISITOS

### Redis (Windows)
1. Descargar Redis para Windows:
   https://github.com/microsoftarchive/redis/releases

2. Instalar Redis como servicio:
   ```powershell
   redis-server --service-install redis.windows.conf
   redis-server --service-start
   ```

3. Verificar instalación:
   ```powershell
   redis-cli ping
   # Debe responder: PONG
   ```

### Redis (Linux/Ubuntu)
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
redis-cli ping
```

---

## 🚀 PASO 1: INSTALAR DEPENDENCIAS

### Windows
```powershell
cd d:\anteproyecto20112025
pip install -r requirements_mejoras_criticas.txt
```

### Linux
```bash
cd /var/www/cantina_project
pip3 install -r requirements_mejoras_criticas.txt
```

---

## ⚙️ PASO 2: CONFIGURAR SETTINGS.PY

### Agregar al final de settings.py:

```python
# Importar configuración de Redis y Rate Limiting
import sys
config_path = os.path.join(BASE_DIR, 'config')
if config_path not in sys.path:
    sys.path.insert(0, config_path)

# Si quieres usar Redis (recomendado)
try:
    from redis_ratelimit_settings import CACHES, LOGGING
    # Las variables CACHES y LOGGING reemplazarán las existentes
except ImportError:
    pass  # Usar configuración por defecto
```

### O copiar manualmente:
1. Abrir: `config/redis_ratelimit_settings.py`
2. Copiar secciones CACHES, LOGGING al `settings.py`
3. Reemplazar configuración existente

---

## 🔧 PASO 3: AGREGAR HEALTH CHECK URLS

### En `cantina_project/urls.py`:

```python
from gestion.health_views import health_check, readiness_check, liveness_check

urlpatterns = [
    # ... urls existentes ...
    
    # Health checks
    path('health/', health_check, name='health_check'),
    path('ready/', readiness_check, name='readiness_check'),
    path('alive/', liveness_check, name='liveness_check'),
]
```

---

## 📦 PASO 4: CONFIGURAR BACKUP AUTOMÁTICO

### Windows:
```powershell
# Ejecutar como Administrador
cd d:\anteproyecto20112025\scripts
.\schedule_backup_windows.ps1
```

### Linux:
```bash
sudo bash scripts/schedule_backup_linux.sh
```

### Probar backup manual:
```bash
python manage.py backup_database --compress --keep-days=30 --notify
```

---

## 🏥 PASO 5: CONFIGURAR MONITORING

### Agregar tarea programada para health checks:

#### Windows (PowerShell como Admin):
```powershell
$TaskName = "Cantina_HealthCheck"
$BatchFile = "d:\anteproyecto20112025\scripts\run_healthcheck.bat"

# Crear script batch
@"
@echo off
cd /d d:\anteproyecto20112025
python manage.py health_check --notify >> logs\healthcheck.log 2>&1
"@ | Out-File -FilePath $BatchFile -Encoding ASCII

# Crear tarea (cada hora)
$Trigger = New-ScheduledTaskTrigger -Once -At "00:00" -RepetitionInterval (New-TimeSpan -Hours 1)
$Action = New-ScheduledTaskAction -Execute $BatchFile
Register-ScheduledTask -TaskName $TaskName -Trigger $Trigger -Action $Action -User "SYSTEM"
```

#### Linux (crontab):
```bash
# Ejecutar health check cada hora
crontab -e
# Agregar:
0 * * * * cd /var/www/cantina_project && python3 manage.py health_check --notify >> logs/healthcheck.log 2>&1
```

### Probar health check manual:
```bash
python manage.py health_check --notify --verbose
```

---

## 🔐 PASO 6: APLICAR RATE LIMITING

### Proteger endpoints críticos:

#### Ejemplo en views.py:
```python
from gestion.ratelimit_utils import ratelimit_venta, ratelimit_login, ratelimit_api

@ratelimit_login
def login_view(request):
    # ... código existente ...
    pass

@ratelimit_venta
def procesar_venta(request):
    # ... código existente ...
    pass

@ratelimit_api
def api_productos(request):
    # ... código existente ...
    pass
```

#### O usar decorador genérico:
```python
from gestion.ratelimit_utils import ratelimit

@ratelimit(max_requests=10, window_seconds=60)
def my_view(request):
    pass
```

---

## 📊 PASO 7: IMPLEMENTAR CACHE

### Usar CacheManager en views:

```python
from gestion.cache_utils import CacheManager

def dashboard_view(request):
    user_id = request.user.id
    
    # Intentar obtener del cache
    data = CacheManager.get_dashboard_data(user_id)
    
    if data is None:
        # Generar datos
        data = {
            'ventas': get_ventas_hoy(),
            'productos': get_productos_mas_vendidos(),
            # ... más datos ...
        }
        
        # Guardar en cache (60 segundos)
        CacheManager.set_dashboard_data(user_id, data, timeout=60)
    
    return render(request, 'dashboard.html', data)
```

### Invalidar cache cuando se modifiquen datos:

```python
from gestion.cache_utils import CacheManager

def crear_producto(request):
    # ... crear producto ...
    
    # Invalidar cache de productos
    CacheManager.invalidate_productos()
    
    return redirect('productos')
```

---

## ✅ PASO 8: VERIFICAR INSTALACIÓN

### 1. Verificar Redis:
```bash
redis-cli ping
# Debe responder: PONG
```

### 2. Verificar Cache Django:
```bash
python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test', 'ok', 10)
>>> cache.get('test')
'ok'
>>> exit()
```

### 3. Probar Health Check:
```bash
python manage.py health_check --verbose
```

### 4. Probar Backup:
```bash
python manage.py backup_database --compress
```

### 5. Verificar endpoints:
```bash
# Health check
curl http://localhost:8000/health/

# Readiness
curl http://localhost:8000/ready/

# Liveness
curl http://localhost:8000/alive/
```

---

## 📈 MONITOREO CONTINUO

### Logs a revisar:
- `logs/cantina.log` - Logs generales
- `logs/errors.log` - Errores
- `logs/security.log` - Eventos de seguridad
- `logs/backup.log` - Backups
- `logs/healthcheck.log` - Health checks

### Comandos útiles:

```bash
# Ver logs en tiempo real
tail -f logs/cantina.log

# Buscar errores
grep ERROR logs/errors.log

# Ver últimos backups
ls -lth backups/ | head -10

# Verificar espacio en disco
df -h

# Verificar memoria
free -h

# Verificar procesos de Redis
ps aux | grep redis
```

---

## 🚨 TROUBLESHOOTING

### Redis no se conecta:
```bash
# Windows
redis-server --service-stop
redis-server --service-start

# Linux
sudo systemctl restart redis-server
sudo systemctl status redis-server
```

### Logs no se crean:
```bash
# Crear directorio de logs
mkdir -p logs
chmod 755 logs
```

### Backup falla:
- Verificar que mysqldump esté en el PATH
- Verificar credenciales de MySQL en .env
- Verificar permisos en carpeta backups/

---

## 📝 CONFIGURACIÓN FINAL

### Archivo `.env` debe tener:
```
# Base de datos
DB_NAME=cantinatitadb
DB_USER=root
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=3306

# Email para notificaciones
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu_email@gmail.com
EMAIL_HOST_PASSWORD=tu_app_password
```

---

## ✅ CHECKLIST DE VERIFICACIÓN

- [ ] Redis instalado y corriendo
- [ ] Dependencias Python instaladas
- [ ] Settings.py actualizado con Redis
- [ ] Health check endpoints funcionando
- [ ] Backup automático programado
- [ ] Health check programado cada hora
- [ ] Rate limiting aplicado a endpoints críticos
- [ ] Cache implementado en vistas principales
- [ ] Logs configurados y rotando
- [ ] Directorio backups/ creado
- [ ] Directorio logs/ creado
- [ ] Variables de entorno configuradas
- [ ] Emails de notificación funcionando

---

## 🎯 PRÓXIMOS PASOS

1. Monitorear logs durante 48 horas
2. Verificar que backups se ejecutan correctamente
3. Revisar health checks cada día
4. Ajustar umbrales de rate limiting según uso real
5. Optimizar timeouts de cache según patrones de uso

---

**¡Mejoras críticas instaladas!** 🚀
