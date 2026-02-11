# Frontend - Cantina Tita Sistema

## Interfaz de Usuario

### Estructura Actual
- `templates/` - Templates HTML de Django (legacy)
- `static/` - Archivos CSS, JS, imágenes

### Migración a SPA (Próximos pasos)

Para convertir a una Single Page Application moderna:

#### Opción 1: React
```bash
cd frontend
npx create-react-app cantina-frontend
```

#### Opción 2: Vue.js
```bash
cd frontend  
npm create vue@latest cantina-frontend
```

#### Opción 3: Angular
```bash
cd frontend
ng new cantina-frontend
```

### Configuración API
El frontend se conectará al backend Django API en:
- **Desarrollo:** `http://localhost:8000/api/`
- **Producción:** `https://api.cantina-tita.com/api/`

### Funcionalidades a Migrar
- Dashboard administrativo
- Gestión de productos
- Punto de venta (POS)
- Reportes y estadísticas
- Portal de usuario
- Sistema de autenticación

### Assets Actuales
Los templates y assets existentes se encuentran en:
- `templates/` - Templates HTML
- `static/` - CSS, JavaScript, imágenes