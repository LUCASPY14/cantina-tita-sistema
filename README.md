# Sistema de Gestión de Cantina - Django 🇵🇾

Sistema de gestión completo para administrar una cantina escolar desarrollado con Python/Django y MySQL, configurado para Paraguay.

## 🏗️ Arquitectura Backend/Frontend

```
├── backend/          # Django API Backend
│   ├── cantina_project/   # Configuración Django
│   ├── gestion/          # App de gestión
│   ├── pos/             # App punto de venta
│   └── requirements.txt  # Dependencias Python
├── frontend/         # Frontend Web
│   ├── templates/       # Templates HTML 
│   ├── static/         # CSS, JS, imágenes
│   └── package.json    # Configuración frontend
└── docs/            # Documentación
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

Ver [README_DER.md](README_DER.md) y [RESUMEN_DER_MODULOS.md](RESUMEN_DER_MODULOS.md) para más detalles.

## Características

### Sistema Existente (101 Tablas)
- **Sistema de Tarjetas**: Tarjetas recargables para estudiantes
- **Planes de Almuerzo**: Suscripciones mensuales con control de asistencia
- **Facturación Electrónica**: Integración con SIFEN (Paraguay)
- **Cuenta Corriente**: Control de crédito para clientes
- **Gestión de Comisiones**: Cálculo automático por medios de pago
- **Control de Cajas**: Múltiples cajas con cierres diarios
- **Auditoría Completa**: Logs de todas las operaciones
- **Sistema Multi-Lista de Precios**: Diferentes precios por tipo de cliente
- **Seguridad 2FA**: Autenticación de dos factores
- **Notificaciones**: Sistema de alertas y notificaciones
- **Gestión de Stock**: Control de inventario con alertas
- **Promociones**: Sistema de descuentos y ofertas

### Funcionalidades Django Integradas

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
