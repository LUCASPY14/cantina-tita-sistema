# ⚡ QUICK START - Mejoras Críticas
## 3 Pasos para Activar las Mejoras

---

## 🚀 INSTALACIÓN EN 3 PASOS

### PASO 1: Ejecutar Script de Instalación

**Windows (PowerShell como Administrador):**
```powershell
cd d:\anteproyecto20112025
Set-ExecutionPolicy Bypass -Scope Process -Force
.\INSTALAR_MEJORAS.ps1
```

**Linux:**
```bash
cd /var/www/cantina_project
sudo bash INSTALAR_MEJORAS.sh
```

---

### PASO 2: Instalar Redis (si no está instalado)

**Windows:**
1. Descargar: https://github.com/microsoftarchive/redis/releases
2. Ejecutar:
```powershell
redis-server --service-install redis.windows.conf
redis-server --service-start
redis-cli ping  # Debe responder: PONG
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
redis-cli ping  # Debe responder: PONG
```

---

### PASO 3: Verificar que Todo Funciona

```bash
# 1. Verificar backup
python manage.py backup_database --compress

# 2. Verificar health check
python manage.py health_check --verbose

# 3. Iniciar servidor
python manage.py runserver

# 4. Probar endpoints (en otro terminal)
curl http://localhost:8000/health/
curl http://localhost:8000/ready/
curl http://localhost:8000/alive/
```

---

## ✅ ¡LISTO!

Si todo funcionó correctamente, ahora tienes:

- ✅ **Backups automáticos** cada día a las 2:00 AM
- ✅ **Monitoring** del sistema cada hora
- ✅ **Redis cache** para mejor performance
- ✅ **Rate limiting** en APIs

---

## 🆘 ¿ALGO SALIÓ MAL?

### Redis no se conecta
```bash
# Windows
redis-server --service-stop
redis-server --service-start

# Linux
sudo systemctl restart redis-server
```

### Backup falla
- Verifica que mysqldump esté instalado: `mysqldump --version`
- Verifica credenciales en `.env`

### Permisos en Windows
Ejecuta PowerShell como **Administrador**

---

## 📚 MÁS INFORMACIÓN

Para guía completa: [GUIA_INSTALACION_MEJORAS_CRITICAS.md](GUIA_INSTALACION_MEJORAS_CRITICAS.md)

Para documentación técnica: [SESION_10_ENERO_2026.md](SESION_10_ENERO_2026.md)

---

**¿Necesitas ayuda?** Revisa la documentación completa en los archivos mencionados.
