# Sistema de Gestión de Cantina 🇵🇾

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2.8-green.svg)](https://www.djangoproject.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3-blue.svg)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC.svg)](https://tailwindcss.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)
[![Tests](https://img.shields.io/badge/Tests-Passing-success.svg)](https://github.com/tu-usuario/cantina/actions)
[![Coverage](https://img.shields.io/badge/Coverage-70%25-yellowgreen.svg)](https://codecov.io/gh/tu-usuario/cantina)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style](https://img.shields.io/badge/Code_Style-Black-000000.svg)](https://github.com/psf/black)

Sistema completo de gestión para cantina escolar con facturación electrónica SIFEN, portal de padres, POS avanzado y más. Desarrollado con Django 5.2, TypeScript, Tailwind CSS y MySQL.

---

## 📋 Tabla de Contenidos

- [Quick Start](#-quick-start)
- [Características](#-características)
- [Stack Tecnológico](#%EF%B8%8F-stack-tecnológico)
- [Arquitectura](#%EF%B8%8F-arquitectura)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Testing](#-testing)
- [Documentación](#-documentación)
- [Contribuir](#-contribuir)
- [Licencia](#-licencia)

---

## 🚀 Quick Start

```bash
# Con Docker (Recomendado)
make docker-up        # Inicia todos los servicios
# Django: http://localhost:8000

# Sin Docker
make setup            # Setup completo
make dev              # Django + Vite
```

Ver [QUICKSTART.md](QUICKSTART.md) para guía completa.

## 🏗️ Arquitectura Backend/Frontend

```
├── backend/          # Django API Backend
│   ├── cantina_project/   # Configuración Django
│   ├── gestion/          # App de gestión (101 modelos)
│   ├── pos/             # App punto de venta
│   └── requirements.txt  # 22 dependencias Python
├── frontend/         # Frontend Moderno (Vite + TypeScript)
│   ├── templates/       # 50 templates HTML (WCAG AA)
│   ├── src/            # TypeScript source
│   ├── static/         # CSS, JS, imágenes
│   └── package.json    # 24 dependencias Node
├── scripts/          # Scripts organizados
│   ├── setup/
│   ├── database/
│   ├── maintenance/
│   ├── audit/
│   └── dev/
├── docker/           # Docker configs
├── Dockerfile        # Python 3.12
├── docker-compose.yml # 6 servicios
├── Makefile          # 40+ comandos
└── docs/            # 74+ documentos
```

## 🇵🇾 Configuración Regional

- **País:** Paraguay
- **Idioma:** Español (es-PY)
- **Zona horaria:** America/Asuncion
- **Moneda:** Guaraníes (Gs.)
- **Formato de fecha:** DD/MM/AAAA
- **Separador de miles:** punto (.)
- **IVA:** 10% (general) / 5% (reducido)

Ver [CONFIGURACION_PARAGUAY.md](CONFIGURACION_PARAGUAY.md) para detalles completos.

## ⚠️ IMPORTANTE: Base de Datos Existente

Este proyecto está **integrado con una base de datos MySQL existente** que contiene:
- **101 tablas** con datos operativos
- **11 vistas** de consulta
- Sistema completo de gestión de cantina en producción

**Los modelos Django están configurados para trabajar con las tablas existentes sin modificarlas.**

Ver [INTEGRACION_BD.md](INTEGRACION_BD.md) para documentación completa de la estructura.

## 📊 Diagramas DER

El proyecto incluye **Diagramas Entidad-Relación** completos y organizados por módulos funcionales:

- **22 módulos funcionales** que cubren las 101 tablas (100% cobertura)
- **44 diagramas PNG** (Lógicos y Físicos)
- **Índice HTML interactivo** con visor modal

### Ver DER:
- **Local**: Abre [diagramas_der_modulos/index_modulos.html](diagramas_der_modulos/index_modulos.html)
- **Online**: https://raw.githack.com/LUCASPY14/cantina-tita-sistema/main/diagramas_der_modulos/index_modulos.html

## ✨ Características

### 🎯 Módulos Principales

- **🛒 POS (Punto de Venta)**
  - Interfaz táctil optimizada
  - Búsqueda rápida de productos
  - Múltiples métodos de pago
  - Facturación electrónica SIFEN
  - Control de caja en tiempo real

- **💳 Sistema de Tarjetas**
  - Tarjetas prepago recargables
  - Saldos en tiempo real
  - Autorización de saldo insuficiente
  - Historial de consumos
  - Alertas de saldo bajo

- **👨‍👩‍👧 Portal de Padres**
  - Consulta de saldos
  - Solicitud de recargas online
  - Historial de consumos
  - Restricciones alimentarias
  - Notificaciones WhatsApp

- **🏫 Gestión de Almuerzos**
  - Planes mensuales
  - Control de asistencia
  - Programación de menús
  - Reportes de consumo

- **💰 Cuenta Corriente**
  - Control de crédito por cliente
  - Pagos parciales
  - Estados de cuenta
  - Notas de crédito

- **📊 Reportes Gerenciales**
  - Ventas por período
  - Productos más vendidos
  - Cierre de cajas
  - Estado de stock
  - Exportación a Excel

### 🔒 Seguridad

- ✅ Autenticación JWT
- ✅ Permisos granulares por rol
- ✅ Rate limiting en API
- ✅ CSRF protection
- ✅ HTTPS configurado
- ✅ Headers de seguridad (CSP, HSTS)
- ✅ 2FA opcional

### 🌐 Configuración Regional (Paraguay)

- **Idioma:** Español (es-PY)
- **Zona horaria:** America/Asuncion
- **Moneda:** Guaraníes (₲)
- **Formato fecha:** DD/MM/AAAA
- **IVA:** 10% (general) / 5% (reducido)

---

## 🏗️ Arquitectura

### Frontend Moderno:
- **🎨 Tailwind CSS 3.4** - Framework CSS utility-first
- **⚡ Vite 5.1** - Build tool ultrarrápido con HMR
- **📝 TypeScript 5.3** - Tipado estático para JavaScript
- **🎭 Alpine.js 3.13** - Framework reactivo ligero
- **🔄 HTMX 1.9** - HTML dinámico sin complejidad
- **📦 PostCSS** - Procesador CSS con autoprefixer

### Backend API-First:
- **🐍 Django 5.2.8** - Framework web robusto
- **🔌 Django REST Framework** - API REST completa
- **🔐 JWT Authentication** - Autenticación segura
- **📊 OpenAPI/Swagger** - Documentación automática
- **🗃️ MySQL 8.0** - Base de datos existente (101 tablas)

### DevOps & Tooling:
- **🏗️ GitHub Actions** - CI/CD automatizado
- **📋 ESLint + TypeScript** - Code quality
- **🔄 Hot Module Replacement** - Desarrollo sin recargas
- **📱 PWA Ready** - Progressive Web App

## � Docker Setup (Nuevo!)

El proyecto ahora incluye Docker completo para desarrollo y producción:

```bash
# Iniciar todos los servicios
make docker-up

# Servicios incluidos:
# - MySQL 8.0
# - Redis 7
# - Django + Gunicorn
# - Nginx
# - Celery Worker
# - Celery Beat
```

Ver [docker-compose.yml](docker-compose.yml) y [SPRINT3_COMPLETADO.md](SPRINT3_COMPLETADO.md).

## 🛠️ Comandos Make (Automatización)

```bash
# Setup
make setup              # Setup completo (<30 min)
make setup-env          # Crear .env

# Desarrollo
make dev                # Django + Vite
make shell              # Django shell
make dbshell            # MySQL shell

# Testing
make test               # Ejecutar tests
make test-coverage      # Tests + coverage
make lint               # Linters

# Docker
make docker-build       # Construir imágenes
make docker-up          # Iniciar servicios
make docker-logs        # Ver logs

# Utilidades
make clean              # Limpiar cache
make backup-db          # Backup BD
make help               # Ver todos los comandos
```

Ver [Makefile](Makefile) para 40+ comandos disponibles.

## �🛠️ Desarrollo Integrado

### Scripts de desarrollo:
```bash
# Servidor integrado (Django + Vite)
python dev_server.py
# o alternativamente:
./dev.bat     # Windows  
./dev.sh      # Linux/Mac

# Solo backend
cd backend && python manage.py runserver

# Solo frontend
cd frontend && npm run dev

# Build producción
cd frontend && npm run build
```

### URLs de desarrollo:
- 🐍 **Django:** http://localhost:8000
- ⚡ **Vite:** http://localhost:3000  
- 📚 **Admin:** http://localhost:8000/admin/
- 🔗 **API:** http://localhost:8000/api/
- 📖 **Docs:** http://localhost:8000/api/docs/

## Requisitos

- Python 3.10 o superior
- MySQL 8.0 o superior
- MySQL Workbench (opcional, para gestión de BD)

## Instalación

1. **Clonar o descargar el proyecto**

2. **Configurar el entorno virtual** (ya configurado en `.venv`)

3. **Instalar dependencias**:
```bash
D:/anteproyecto20112025/.venv/Scripts/python.exe -m pip install -r requirements.txt
```

4. **Configurar la base de datos**:
   - Edita el archivo `.env` con tus credenciales de MySQL:
   ```
   DB_NAME=cantinatitadb
   DB_USER=root
   DB_PASSWORD=tu_contraseña_mysql
   DB_HOST=localhost
   DB_PORT=3306
   ```

5. **Crear las migraciones**:
```bash
D:/anteproyecto20112025/.venv/Scripts/python.exe manage.py makemigrations
```

6. **Aplicar las migraciones a la base de datos**:
```bash
D:/anteproyecto20112025/.venv/Scripts/python.exe manage.py migrate
```

7. **Crear un superusuario para acceder al admin**:
```bash
D:/anteproyecto20112025/.venv/Scripts/python.exe manage.py createsuperuser
```

8. **Ejecutar el servidor de desarrollo**:
```bash
D:/anteproyecto20112025/.venv/Scripts/python.exe manage.py runserver
```

9. **Acceder al panel de administración**:
   - URL: http://127.0.0.1:8000/admin
   - Usa las credenciales del superusuario creado

## Modelos del Sistema

### Categoria
Clasificación de productos (bebidas, alimentos, snacks, etc.)

### Producto
- Código único
- Nombre y descripción
- Categoría
- Precio
- Control de stock con alertas de reposición
- Estado activo/inactivo

### Cliente
- Código único
- Datos personales
- Tipo (estudiante, profesor, personal, externo)
- Crédito disponible
- Historial de compras

### Venta
- Número de venta único
- Cliente (opcional)
- Detalles de productos
- Métodos de pago (efectivo, tarjeta, crédito, transferencia)
- Estados (pendiente, completada, cancelada)

### Proveedor
- Datos fiscales (RFC)
- Información de contacto
- Historial de compras

### CompraProveedor
- Control de adquisiciones
- Seguimiento de recepciones
- Estados de compra

## Estructura del Proyecto

```
anteproyecto20112025/
├── .venv/                      # Entorno virtual de Python
├── cantina_project/            # Configuración del proyecto Django
│   ├── settings.py            # Configuración principal
│   ├── urls.py                # URLs del proyecto
│   └── wsgi.py                # Configuración WSGI
├── gestion/                    # Aplicación principal
│   ├── models.py              # Modelos de datos
│   ├── admin.py               # Configuración del admin
│   ├── views.py               # Vistas (pendiente)
│   └── urls.py                # URLs de la app (pendiente)
├── .env                       # Variables de entorno (NO subir a git)
├── .env.example              # Ejemplo de variables de entorno
├── .gitignore                # Archivos ignorados por git
├── manage.py                 # Script de gestión de Django
├── requirements.txt          # Dependencias del proyecto
└── README.md                 # Este archivo
```

## Uso del Panel de Administración

1. Ingresa a http://127.0.0.1:8000/admin
2. Inicia sesión con tu superusuario
3. Podrás gestionar:
   - Categorías de productos
   - Productos e inventario
   - Clientes
   - Ventas y detalles
   - Proveedores
   - Compras a proveedores

## Próximos Pasos

- [x] Crear modelos Django para las 101 tablas
- [x] Generar DER completo y por módulos
- [x] Configurar panel de administración
- [ ] Crear vistas personalizadas para el frontend
- [ ] Implementar API REST con Django REST Framework
- [ ] Agregar reportes y estadísticas
- [ ] Implementar sistema de permisos por rol
- [ ] Agregar dashboard con gráficas
- [ ] Implementar sistema de notificaciones en tiempo real

## 📚 Documentación Adicional

- [README_DER.md](README_DER.md) - Guía de generación de diagramas DER
- [RESUMEN_DER_MODULOS.md](RESUMEN_DER_MODULOS.md) - Descripción detallada de los 22 módulos
- [INTEGRACION_BD.md](INTEGRACION_BD.md) - Integración con base de datos existente
- [CONFIGURACION_PARAGUAY.md](CONFIGURACION_PARAGUAY.md) - Configuración regional paraguaya
- [INSTALACION_GRAPHVIZ.md](INSTALACION_GRAPHVIZ.md) - Instalación de Graphviz para DER

## Tecnologías Utilizadas

- **Backend**: Python 3.13 + Django 5.2
- **Base de Datos**: MySQL 8.0
- **Gestión de Dependencias**: pip
- **Variables de Entorno**: python-decouple
- **Diagramas DER**: SQLAlchemy 2.0 + Graphviz 14.1
- **API REST**: Django REST Framework
- **Gestión de Imágenes**: Pillow
- **Reportes**: openpyxl, xlsxwriter

## 📁 Estructura del Proyecto

```
anteproyecto20112025/
├── .venv/                      # Entorno virtual de Python
├── cantina_project/            # Configuración del proyecto Django
│   ├── settings.py            # Configuración principal
│   ├── urls.py                # URLs del proyecto
│   └── wsgi.py                # Configuración WSGI
├── gestion/                    # Aplicación principal
│   ├── models.py              # Modelos de datos (101 tablas)
│   ├── admin.py               # Configuración del admin
│   ├── views.py               # Vistas
│   └── urls.py                # URLs de la app
├── diagramas_der/             # DER completos (global)
│   ├── DER_Logico_cantinatitadb.png
│   ├── DER_Fisico_cantinatitadb.png
│   └── index.html
├── diagramas_der_modulos/     # DER por módulos (22 módulos)
│   ├── 01_Autenticacion_Django_Logico.png
│   ├── 01_Autenticacion_Django_Fisico.png
│   ├── ... (44 archivos PNG)
│   └── index_modulos.html
├── generar_der_completo.py    # Generador DER global
├── generar_der_por_modulos_completo.py  # Generador DER modular
├── .env                       # Variables de entorno (NO subir a git)
├── .env.example              # Ejemplo de variables de entorno
├── .gitignore                # Archivos ignorados por git
├── manage.py                 # Script de gestión de Django
├── requirements.txt          # Dependencias principales
├── requirements_der.txt      # Dependencias para generación DER
└── README.md                 # Este archivo
```

## 🔧 Herramientas de Desarrollo

### Generación de Diagramas DER

El proyecto incluye scripts para generar diagramas entidad-relación:

```bash
# DER completo (todas las tablas en un solo diagrama)
.\.venv\Scripts\python.exe generar_der_completo.py

# DER por módulos (22 módulos funcionales)
.\.venv\Scripts\python.exe generar_der_por_modulos_completo.py
```

Ver [README_DER.md](README_DER.md) para instrucciones detalladas.

## Soporte

Para cualquier duda o problema, revisa la documentación oficial de Django: https://docs.djangoproject.com/
