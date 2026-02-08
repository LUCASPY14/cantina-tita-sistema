# 🔗 Guía de Integración Frontend-Backend

Esta guía explica cómo trabajar con la integración completa entre el frontend (Vite + TypeScript) y el backend (Django + MySQL) del Sistema Cantina Tita.

## 🏗️ Arquitectura del Sistema

```
┌─────────────────┐    Proxy    ┌──────────────────┐    MySQL    ┌───────────────┐
│   Frontend      │ ──── /api ──│    Backend       │ ── 3306 ── │   Database    │
│   Vite :3000    │             │  Django :8000    │           │  cantinatitadb│
└─────────────────┘             └──────────────────┘           └───────────────┘
```

### Stack Tecnológico

**Frontend:**
- ⚡ Vite 5.x (bundler)
- 📘 TypeScript (tipado)
- 🎨 Tailwind CSS (estilos)
- 🔮 Alpine.js (reactividad)
- 🌐 HTMX (interactividad)

**Backend:**
- 🐍 Django 5.2.8
- 🗄️ MySQL 8.0
- 🔌 Django REST Framework
- 🔐 JWT Authentication
- 📖 OpenAPI/Swagger

## 🚀 Inicio Rápido

### Método 1: Script Windows (.bat)
```bash
./dev.bat
```

### Método 2: PowerShell
```powershell
# Desarrollo completo
./dev.ps1

# Solo backend
./dev.ps1 -Backend

# Solo frontend  
./dev.ps1 -Frontend

# Instalar dependencias
./dev.ps1 -Setup

# Ayuda
./dev.ps1 -Help
```

### Método 3: NPM Scripts
```bash
# Desarrollo completo (recomendado)
npm run dev

# Solo backend
npm run dev:only-backend

# Solo frontend
npm run dev:only-frontend

# Verificar backend
npm run check
```

## 🔌 Configuración de API

### Endpoints Principales

| Endpoint | Descripción | Proxy |
|----------|-------------|-------|
| `/health/` | Health check del sistema | ✅ |
| `/api/v1/` | API REST principal | ✅ |
| `/api/pos/` | API Punto de Venta | ✅ |
| `/admin/` | Django Admin | ✅ |
| `/api/docs/` | Documentación Swagger | ✅ |

### Configuración del Proxy

El frontend está configurado para redirigir automáticamente las peticiones:

```javascript
// vite.config.ts
server: {
  proxy: {
    '/api': 'http://localhost:8000',
    '/admin': 'http://localhost:8000'
  }
}
```

### Cliente API TypeScript

```typescript
// Uso del cliente API
import { api } from '@/utils/api'

// GET request
const productos = await api.get('/v1/productos/');

// POST request
const venta = await api.post('/pos/ventas/', ventaData);
```

## 🛠️ Desarrollo

### Estructura de Archivos

```
frontend/
├── src/
│   ├── main.ts          # Aplicación principal
│   ├── pos.ts           # Sistema POS
│   ├── portal.ts        # Portal de padres
│   ├── admin.ts         # Administración
│   ├── utils/api.ts     # Cliente API
│   ├── types/api.ts     # Tipos TypeScript
│   └── components/      # Componentes reutilizables
├── demo-*.html          # Páginas de demo
└── vite.config.ts       # Configuración Vite

backend/
├── cantina_project/
│   ├── settings.py      # Configuración Django
│   └── urls.py          # Rutas principales
├── gestion/             # App principal
├── pos/                 # App Punto de Venta
└── requirements.txt     # Dependencias Python
```

### Flujo de Trabajo Desarrollo

1. **Iniciar entorno completo:**
   ```bash
   ./dev.ps1
   ```

2. **Acceder a las interfaces:**
   - 🎨 Frontend: http://localhost:3000/
   - 📡 Backend: http://localhost:8000/
   - 🔧 Django Admin: http://localhost:8000/admin/
   - 📖 API Docs: http://localhost:8000/api/docs/

3. **Páginas de prueba disponibles:**
   - `/test-connection.html` - Pruebas básicas de conexión
   - `/demo-integration.html` - Demo de integración completa
   - `/demo-pos.html` - Sistema POS funcional

### CORS y Seguridad

El backend está configurado para permitir conexiones desde:
- `http://localhost:3000` (Vite)
- `http://localhost:5173` (Vite alternativo)

## 🧪 Testing

### Testing Frontend
```bash
cd frontend
npm test           # Vitest
npm run test:ui    # UI de testing
npm run e2e        # Playwright E2E
```

### Testing Backend
```bash
cd backend
python manage.py test
```

## 📦 Build y Despliegue

### Build Frontend
```bash
npm run build                # Build producción
npm run build:watch          # Build con watch mode
```

### Verificaciones
```bash
npm run typecheck           # Verificar TypeScript
npm run check              # Verificar Django
```

## 🔧 Configuración Avanzada

### Variables de Entorno

Crear `.env` en el directorio raíz:
```env
# Django
SECRET_KEY=tu-secret-key
DEBUG=True
DATABASE_URL=mysql://user:pass@localhost:3306/cantinatitadb

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Customización del Proxy

Para modificar las rutas del proxy, editar `frontend/vite.config.ts`:

```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      secure: false
    },
    '/custom-endpoint': 'http://localhost:8000'
  }
}
```

## 🐛 Troubleshooting

### Problemas Comunes

1. **Error "Module not found 'django'"**
   ```bash
   # Activar entorno virtual
   .venv\Scripts\activate
   ```

2. **Puerto 3000 o 8000 ocupado**
   ```bash
   # Encontrar proceso y terminar
   netstat -ano | findstr :3000
   taskkill /PID [PID] /F
   ```

3. **Error de CORS**
   - Verificar que el backend esté en puerto 8000
   - Revisar `CORS_ALLOWED_ORIGINS` en settings.py

4. **Dependencias faltantes**
   ```bash
   ./dev.ps1 -Setup
   ```

### Logs y Debug

- **Frontend**: Abrir DevTools → Console
- **Backend**: Ver terminal de Django
- **Base de datos**: Verificar con `python manage.py dbshell`

## 📚 Recursos Adicionales

- [Documentación Django](https://docs.djangoproject.com/)
- [Documentación Vite](https://vitejs.dev/)
- [Alpine.js Guide](https://alpinejs.dev/)
- [HTMX Documentation](https://htmx.org/docs/)
- [Tailwind CSS](https://tailwindcss.com/docs)

## 🤝 Contribución

1. Asegúrate de que todas las pruebas pasen
2. Mantén la documentación actualizada
3. Sigue las convenciones de código establecidas
4. Prueba en ambos entornos (development/production)

---

🏪 **Sistema Cantina Tita** - Integración Frontend-Backend Completada ✅