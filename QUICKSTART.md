# 🚀 QUICK START - Sistema de Gestión de Cantina

Guía de inicio rápido para poner el proyecto en marcha en <30 minutos.

---

## ⚡ Inicio Rápido (Recomendado)

### Opción 1: Docker (Más Fácil) 🐳

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/cantina-sistema.git
cd cantina-sistema

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# 3. Iniciar con Docker
make docker-build    # Construir imágenes (solo primera vez)
make docker-up       # Iniciar todos los servicios

# ¡Listo! 🎉
# Django: http://localhost:8000
# Nginx: http://localhost
```

**Servicios incluidos:**
- ✅ MySQL 8.0
- ✅ Redis 7
- ✅ Django + Gunicorn
- ✅ Nginx
- ✅ Celery Worker
- ✅ Celery Beat

---

### Opción 2: Local Development

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/cantina-sistema.git
cd cantina-sistema

# 2. Setup completo automatizado
make setup           # Crea venv + instala dependencias

# 3. Configurar .env
cp .env.example .env
# Editar con tus credenciales MySQL

# 4. Iniciar desarrollo
make dev             # Django + Vite concurrentes

# ¡Listo! 🎉
# Backend: http://localhost:8000
# Frontend: http://localhost:5173
```

---

## 📋 Prerequisitos

### Para Docker (Opción 1)
- Docker Desktop 20.10+
- Git

### Para Local (Opción 2)
- Python 3.12+
- MySQL 8.0
- Node.js 18+
- Git

---

## 🔧 Configuración de .env

Variables mínimas requeridas:

```bash
# Django
SECRET_KEY=tu-secret-key-aqui
DEBUG=True

# Base de Datos
DB_NAME=cantina_titadb
DB_USER=root
DB_PASSWORD=tu_password
DB_HOST=localhost  # o 'db' si usas Docker
DB_PORT=3306

# Email (opcional para desarrollo)
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=tu_email@gmail.com
EMAIL_HOST_PASSWORD=tu_app_password
```

Ver [.env.example](.env.example) para todas las variables disponibles (80+ documentadas).

---

## 📚 Comandos Útiles

### Desarrollo

```bash
make dev              # Iniciar Django + Vite
make dev-backend      # Solo Django
make dev-frontend     # Solo Vite
make shell            # Django shell
```

### Base de Datos

```bash
make migrate          # Ejecutar migraciones
make makemigrations   # Crear migraciones
make dbshell          # MySQL shell
```

### Testing

```bash
make test             # Ejecutar tests
make test-coverage    # Tests + coverage
make lint             # Linters (flake8, eslint)
```

### Docker

```bash
make docker-build     # Construir imágenes
make docker-up        # Iniciar contenedores
make docker-down      # Detener contenedores
make docker-logs      # Ver logs
make docker-shell     # Shell en container
```

### Utilidades

```bash
make clean            # Limpiar cache
make backup-db        # Backup de BD
make help             # Ver todos los comandos
```

Ver [Makefile](Makefile) para la lista completa de 40+ comandos.

---

## 🗂️ Estructura del Proyecto

```
cantina-sistema/
├── backend/              # Django API
│   ├── cantina_project/  # Settings
│   ├── gestion/          # App principal (101 modelos)
│   └── requirements.txt
├── frontend/             # Frontend Vite + Tailwind
│   ├── templates/        # 50 templates HTML
│   ├── src/              # TypeScript source
│   └── package.json
├── scripts/              # Scripts organizados
│   ├── setup/
│   ├── database/
│   ├── maintenance/
│   ├── audit/
│   └── dev/
├── docs/                 # Documentación
├── deployment/           # Nginx, systemd
├── docker/               # Docker configs
├── .env.example          # Variables documentadas
├── Dockerfile
├── docker-compose.yml
├── Makefile              # 40+ comandos
└── README.md
```

---

## 🎯 Próximos Pasos

1. **Explorar la API**
   - http://localhost:8000/api/
   - http://localhost:8000/admin/

2. **Ver Documentación**
   - [README principal](README.md)
   - [Guía de desarrollo](docs/README.md)
   - [Sprints completados](SPRINT1_COMPLETADO.md)

3. **Configurar servicios opcionales**
   - Facturación electrónica SIFEN
   - WhatsApp notifications
   - Tigo Money payments

4. **Iniciar desarrollo**
   - Ver [CONTRIBUTING.md](CONTRIBUTING.md) (próximamente)
   - Revisar [issues abiertos](https://github.com/tu-usuario/cantina-sistema/issues)

---

## 🆘 Solución de Problemas

### Puerto 8000 ocupado
```bash
# Cambiar puerto en .env
DJANGO_PORT=8001

# Reiniciar
make docker-down
make docker-up
```

### Error de conexión MySQL
```bash
# Verificar que MySQL está corriendo
make docker-ps

# Ver logs
make docker-logs-django

# Reiniciar servicios
make docker-restart
```

### Error al instalar dependencias
```bash
# Limpiar y reinstalar
make clean
make setup
```

---

## 📞 Soporte

- 📧 Email: soporte@cantina.com
- 📝 Issues: https://github.com/tu-usuario/cantina-sistema/issues
- 📖 Docs: [docs/README.md](docs/README.md)

---

**¿Listo para comenzar?** 🚀

```bash
make docker-up  # Si usas Docker
# o
make dev        # Si usas desarrollo local
```
