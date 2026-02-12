# 🍽️ Cantina TITA - Sistema Premium de Gestión

[![Python](https://img.shields.io/badge/Python-3.13.9-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-5.2.8-green.svg)](https://djangoproject.com)
[![Vite](https://img.shields.io/badge/Vite-5.4.21-purple.svg)](https://vitejs.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-Ready-blue.svg)](https://typescriptlang.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Sistema integral de gestión para cantinas escolares con interfaz moderna, funcionalidades completas de punto de venta, gestión de inventarios, administración de tarjetas recargables y analytics avanzados.

## ✨ Características Premium

### 🎨 **Diseño Moderno & Responsive**
- **Glassmorphism Design**: Interfaz con efectos de cristal y transparencias
- **Animaciones Premium**: Transiciones suaves y efectos visuales avanzados
- **Mobile-First**: Optimizado para dispositivos móviles y tablets
- **Accesibilidad**: Cumple con estándares WCAG 2.1
- **PWA Ready**: Instalable como aplicación móvil

### 🚀 **Tecnologías de Vanguardia**

#### Backend
- **Django 5.2.8**: Framework web robusto y escalable
- **MySQL**: Base de datos relacional optimizada
- **Python 3.13.9**: Lenguaje moderno y eficiente
- **40+ Modelos**: Sistema completo de gestión empresarial

#### Frontend  
- **Vite 5.4.21**: Build tool ultra-rápido con HMR
- **TypeScript**: Tipado estático para mayor robustez
- **Tailwind CSS + DaisyUI**: Framework CSS utility-first
- **Alpine.js**: Reactividad ligera y eficiente
- **HTMX**: Interacciones HTTP dinámicas

### 📊 **Funcionalidades Empresariales**

#### Sistema POS Avanzado
- ✅ Ventas rápidas con interfaz intuitiva
- ✅ Gestión de productos por categorías
- ✅ Calculadora automática de precios
- ✅ Historial completo de transacciones
- ✅ Impresión de tickets y recibos
- ✅ Modo offline para pagos de emergencia

#### Gestión de Inventarios
- ✅ Control de stock en tiempo real
- ✅ Alertas automáticas de stock mínimo
- ✅ Gestión de proveedores y compras
- ✅ Reportes de movimientos de inventario
- ✅ Códigos de barras y QR
- ✅ Sistema de lotes y vencimientos

#### Tarjetas Recargables
- ✅ Sistema de créditos estudiantiles
- ✅ Recargas automáticas y manuales
- ✅ Límites de gasto personalizables
- ✅ Historial de consumos por estudiante
- ✅ Integración con sistemas escolares
- ✅ Reportes para padres y tutores

#### Portal Web Institucional
- ✅ Página web responsive para la institución
- ✅ Menús semanales y nutricionales
- ✅ Noticias y anuncios
- ✅ Galería de fotos
- ✅ Contacto y ubicación
- ✅ Integración con redes sociales

#### Dashboard Analytics
- ✅ Métricas de ventas en tiempo real
- ✅ Gráficos interactivos de rendimiento
- ✅ Análisis de productos más vendidos
- ✅ Reportes de rentabilidad
- ✅ Estadísticas de usuarios activos
- ✅ Exportación de datos (PDF, Excel)

#### Administración Completa
- ✅ 40+ modelos registrados en Django Admin
- ✅ Gestión de usuarios y permisos
- ✅ Configuración de sistema
- ✅ Auditoría y logs de seguridad
- ✅ Backup automático de datos
- ✅ Notificaciones en tiempo real

## 🚀 Inicio Rápido

### Prerequisitos
- Python 3.8+ (recomendado 3.13.9)
- Node.js 16+ (recomendado 20+)
- MySQL 8.0+
- Git

### Clonación e Instalación

```bash
# Clonar repositorio
git clone https://github.com/tuusuario/cantina-tita.git
cd cantina-tita

# Ejecutar script de desarrollo premium (recomendado)
python dev-premium.py
# O en Windows PowerShell:
.\dev-premium.ps1
```

### Instalación Manual

#### Backend (Django)
```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 8000
```

#### Frontend (Vite)
```bash
cd frontend  
npm install
npm run dev
```

## 📱 URLs de Desarrollo

Una vez iniciados los servidores:

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Backend Django** | http://localhost:8000/ | API y administración |
| **Admin Django** | http://localhost:8000/admin/ | Panel administrativo |
| **Frontend Vite** | http://localhost:5173/ | Aplicación principal |
| **Demo Premium** | http://localhost:5173/demo-premium.html | Showcase de componentes |
| **Demo Mobile** | http://localhost:5173/demo-mobile.html | Interfaz móvil |

## 🎨 Componentes Premium Disponibles

### Glassmorphism Cards
```html
<div class="glass-card p-6">
    <!-- Contenido con efecto de cristal -->
</div>
```

### Botones Premium
```html
<button class="btn-premium ripple">
    <i class="fas fa-star"></i>
    Botón Premium
</button>
```

### Inputs con Efectos
```html
<input type="text" class="input-premium" placeholder="Input premium...">
```

### Notificaciones Avanzadas
```html
<div class="notification-premium notification-success">
    <p>¡Operación exitosa!</p>
</div>
```

### Loaders Animados
```html
<div class="loader-premium"></div>
```

## 📊 Estructura del Proyecto

```
cantina-tita/
├── 📁 backend/               # Django Backend
│   ├── 📁 gestion/          # App principal
│   │   ├── 📄 models.py     # 40+ modelos de negocio
│   │   ├── 📄 admin.py      # Configuración admin completa
│   │   ├── 📄 views.py      # Vistas y API endpoints
│   │   └── 📄 urls.py       # Enrutamiento
│   ├── 📁 pos/              # Sistema POS
│   ├── 📁 portal/           # Portal web
│   └── 📄 settings.py       # Configuración Django
├── 📁 frontend/             # Vite Frontend
│   ├── 📁 src/
│   │   ├── 📁 styles/       # CSS premium
│   │   │   └── 📄 main.css  # Componentes glassmorphism
│   │   ├── 📁 js/           # TypeScript modules
│   │   └── 📁 assets/       # Recursos estáticos
│   ├── 📁 templates/        # Templates HTML
│   ├── 📄 package.json      # Dependencias NPM
│   ├── 📄 vite.config.ts    # Configuración Vite
│   ├── 📄 demo-premium.html # Demo componentes
│   └── 📄 demo-mobile.html  # Demo móvil
├── 📄 dev-premium.py        # Script desarrollo Python
├── 📄 dev-premium.ps1       # Script desarrollo PowerShell
└── 📄 README.md             # Esta documentación
```

## 🌟 Modelos de Negocio Implementados

### Core Business (40+ modelos)
- **Usuarios**: Estudiantes, Profesores, Personal
- **Productos**: Inventario, Categorías, Precios
- **Ventas**: Transacciones, Tickets, Pagos
- **Proveedores**: Compras, Facturas, Créditos
- **Finanzas**: Cuentas, Movimientos, Reportes
- **Operaciones**: Turnos, Cajas, Auditoria
- **Portal Web**: Contenidos, Noticias, Galería
- **Comunicaciones**: Notificaciones, Mensajes
- **Analytics**: Métricas, KPIs, Dashboards

### Relaciones Especializadas
- **Sistema de Hijos**: Gestión familiar integrada
- **Almuerzos Avanzados**: Menús, Nutricional
- **Seguridad**: Logs, Auditoría, Permisos
- **Promociones**: Ofertas, Descuentos, Campañas

## 💡 Características Técnicas Avanzadas

### Performance
- **Hot Module Replacement (HMR)**: Recarga instantánea en desarrollo
- **Code Splitting**: Optimización automática de bundles
- **Tree Shaking**: Eliminación de código no utilizado
- **CSS Purging**: Optimización de estilos
- **Image Optimization**: Compresión automática

### Seguridad
- **CSRF Protection**: Protección contra ataques de sitio cruzado
- **SQL Injection Prevention**: Consultas parametrizadas
- **Input Sanitization**: Validación y limpieza de datos
- **Session Security**: Manejo seguro de sesiones
- **Password Hashing**: Encriptación robusta

### Escalabilidad  
- **Database Indexing**: Índices optimizados para consultas
- **Query Optimization**: Consultas eficientes con select_related
- **Caching Strategy**: Sistema de caché en múltiples niveles
- **Load Balancing Ready**: Preparado para balanceadores
- **Database Migrations**: Actualizaciones sin tiempo de inactividad

## 📱 Soporte Mobile

### Progressive Web App (PWA)
- **Instalable**: Se puede instalar como app nativa
- **Offline First**: Funciona sin conexión
- **Push Notifications**: Notificaciones en tiempo real
- **Service Workers**: Cache inteligente
- **App Manifest**: Configuración completa PWA

### Responsive Design
- **Breakpoints**: xs, sm, md, lg, xl, 2xl
- **Touch Optimized**: Controles táctiles optimizados
- **Swipe Gestures**: Gestos naturally móviles
- **Keyboard Navigation**: Accesible por teclado
- **Screen Reader**: Compatible con lectores de pantalla

## 🔧 Comandos de Desarrollo

### Django Management
```bash
# Migraciones
python manage.py makemigrations
python manage.py migrate

# Usuarios
python manage.py createsuperuser
python manage.py shell

# Datos
python manage.py loaddata fixtures/sample_data.json
python manage.py dumpdata > backup.json

# Servidor
python manage.py runserver 8000
python manage.py collectstatic
```

### Frontend Development
```bash
# Instalación
npm install
npm audit fix

# Desarrollo
npm run dev          # Servidor desarrollo
npm run build        # Build producción
npm run preview      # Preview build
npm run lint         # Linting
npm run type-check   # Verificación TypeScript
```

### Testing
```bash
# Backend tests
python manage.py test
pytest --coverage

# Frontend tests  
npm run test
npm run test:coverage
npm run test:e2e
```

## 🚀 Deployment

### Producción
```bash
# Build frontend
cd frontend
npm run build

# Django settings
export DJANGO_SETTINGS_MODULE=proyecto.settings.production
python manage.py collectstatic --noinput
python manage.py migrate

# Gunicorn
gunicorn proyecto.wsgi:application --bind 0.0.0.0:8000
```

### Docker
```bash
# Construir imagen
docker-compose build

# Iniciar servicios
docker-compose up -d

# Migraciones
docker-compose exec web python manage.py migrate
```

## 📈 Métricas y Analytics

### KPIs Implementados
- **Ventas por día/semana/mes**
- **Productos más vendidos**
- **Horarios de mayor actividad**
- **Usuarios más activos**
- **Rentabilidad por categoría**
- **Eficiencia operacional**

### Reportes Disponibles
- **📊 Dashboard ejecutivo**
- **📈 Análisis de ventas**
- **📦 Control de inventario**
- **💰 Estados financieros**
- **👥 Análisis de usuarios**
- **📱 Métricas de engagement**

## 🛠️ Personalización

### Temas y Estilos
```css
/* Variables CSS personalizables */
:root {
  --gradient-primary: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
  --gradient-secondary: linear-gradient(135deg, #4ECDC4 0%, #36999F 100%);
  --shadow-premium: 0 10px 40px rgba(0, 0, 0, 0.1);
}
```

### Configuración Empresarial
```python
# settings.py - Personalizar para tu institución
BUSINESS_CONFIG = {
    'SCHOOL_NAME': 'Tu Institución',
    'LOGO_URL': '/static/img/logo.png',
    'THEME_COLOR': '#FF6B35',
    'CONTACT_EMAIL': 'contacto@tuinstitucion.edu',
    'PHONE': '+595 21 123-456',
}
```

## 🤝 Contribución

1. **Fork** el repositorio
2. **Crea** una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. **Commit** tus cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. **Push** a la rama (`git push origin feature/nueva-funcionalidad`)
5. **Abre** un Pull Request

### Estándares de Código
- **Python**: PEP 8, Black formatter
- **TypeScript**: ESLint + Prettier
- **CSS**: BEM methodology
- **Git**: Conventional commits

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## 👏 Créditos

### Stack Tecnológico
- **Django**: Framework web para Python
- **Vite**: Build tool moderno y rápido
- **Tailwind CSS**: Framework CSS utility-first
- **DaisyUI**: Componentes para Tailwind CSS
- **Alpine.js**: Framework JavaScript minimalista
- **HTMX**: Interacciones HTTP modernas

### Diseño e Inspiración
- **Glassmorphism**: Tendencia de diseño moderna
- **Material Design**: Principios de Google
- **Human Interface Guidelines**: Apple
- **Accessibility**: Estándares WCAG 2.1

## 📞 Soporte

- **📧 Email**: cantina.tita.dev@gmail.com
- **📱 WhatsApp**: +595 21 123-4567
- **🌐 Web**: https://cantina-tita.edu.py
- **📋 Issues**: [GitHub Issues](https://github.com/tuusuario/cantina-tita/issues)

---

<div align="center">

**Hecho con ❤️ para instituciones educativas**

[🚀 Demo Live](https://cantina-tita-demo.herokuapp.com) • [📖 Docs](https://docs.cantina-tita.com) • [💬 Community](https://discord.gg/cantina-tita)

</div>