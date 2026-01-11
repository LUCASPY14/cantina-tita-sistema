# 🌐 MAPA DE URLs DEL SISTEMA
## Sistema de Gestión de Cantina Escolar "Tita"

**Servidor**: http://192.168.100.10:8000  
**Fecha**: 10 de Enero de 2026

---

## 📍 URLs PRINCIPALES

### 🔐 Administración
```
http://192.168.100.10:8000/admin/
```
- Panel de administración Django
- Gestión de todos los modelos
- Requiere usuario superadministrador
- **Crear usuario**: `python manage.py createsuperuser`

### 👨‍👩‍👧 Portal de Padres/Clientes
```
http://192.168.100.10:8000/clientes/
```
- Dashboard de padres de familia
- Consulta de saldo y consumos
- Recargas online
- Configuración de restricciones
- Reportes descargables

**URLs específicas**:
- Login: `/clientes/login/`
- Registro: `/clientes/registro/`
- Dashboard: `/clientes/dashboard/`
- Recuperar password: `/clientes/recuperar-password/`

### 🛒 POS (Punto de Venta)
```
http://192.168.100.10:8000/pos/
```
- Interfaz de cajero
- Registro de ventas
- Búsqueda de productos
- Cobro con efectivo/tarjeta
- Impresión de tickets

### 📊 Dashboard Unificado
```
http://192.168.100.10:8000/dashboard/
```
- Estadísticas generales
- Gráficos de ventas
- Estado de stock
- Métricas del día

**URLs específicas**:
- Detalle ventas: `/dashboard/ventas/`
- Detalle stock: `/dashboard/stock/`
- Invalidar cache: `/dashboard/invalidar-cache/`

---

## 🔌 API REST

### Base API v1
```
http://192.168.100.10:8000/api/v1/
```

### Documentación Interactiva
```
📖 Swagger UI:  http://192.168.100.10:8000/api/docs/
📖 ReDoc:       http://192.168.100.10:8000/api/redoc/
📋 Schema:      http://192.168.100.10:8000/api/schema/
```

### Endpoints Principales

#### Productos
```
GET    /api/v1/productos/              # Listar productos
GET    /api/v1/productos/{id}/         # Detalle producto
POST   /api/v1/productos/              # Crear producto
PUT    /api/v1/productos/{id}/         # Actualizar producto
DELETE /api/v1/productos/{id}/         # Eliminar producto
```

#### Clientes
```
GET    /api/v1/clientes/               # Listar clientes
GET    /api/v1/clientes/{id}/          # Detalle cliente
POST   /api/v1/clientes/               # Crear cliente
```

#### Ventas
```
GET    /api/v1/ventas/                 # Listar ventas
POST   /api/v1/ventas/                 # Crear venta
GET    /api/v1/ventas/{id}/            # Detalle venta
```

#### Tarjetas
```
GET    /api/v1/tarjetas/               # Listar tarjetas
POST   /api/v1/tarjetas/               # Crear tarjeta
GET    /api/v1/tarjetas/{id}/saldo/   # Consultar saldo
POST   /api/v1/tarjetas/{id}/recarga/ # Recargar tarjeta
```

#### Stock
```
GET    /api/v1/stock/                  # Estado de stock
GET    /api/v1/stock/bajo/             # Productos con stock bajo
```

#### Autenticación (JWT)
```
POST   /api/v1/auth/token/             # Obtener token
POST   /api/v1/auth/token/refresh/     # Refrescar token
POST   /api/v1/auth/token/verify/      # Verificar token
```

---

## 📋 Reportes

### Base Reportes
```
http://192.168.100.10:8000/reportes/
```

### Reportes Específicos
```
GET /reportes/ventas/diario/           # Reporte ventas del día
GET /reportes/ventas/mensual/          # Reporte ventas mensual
GET /reportes/stock/valorizado/        # Stock valorizado
GET /reportes/clientes/cuenta-corriente/  # Cuenta corriente
GET /reportes/productos/mas-vendidos/  # Top productos
GET /reportes/cajeros/resumen/         # Resumen por cajero
```

---

## 🔧 Herramientas de Desarrollo

### Debug Toolbar (solo con DEBUG=True)
```
http://192.168.100.10:8000/__debug__/
```
- SQL queries ejecutadas
- Templates renderizados
- Tiempo de respuesta
- Cache hits/misses

### Health Checks
```
GET /health/        # Estado general del sistema
GET /readiness/     # Sistema listo para recibir requests
GET /liveness/      # Sistema vivo
```

---

## 🚫 URLs INCORRECTAS (No usar)

### ❌ URLs Antiguas/Incorrectas
```
❌ /portal                    → ✅ /clientes/
❌ /portal/login              → ✅ /clientes/login/
❌ /api                       → ✅ /api/v1/
❌ /api/productos             → ✅ /api/v1/productos/
❌ /swagger                   → ✅ /api/docs/
```

---

## 📱 Acceso desde Dispositivos

### Desde Esta PC (Servidor)
```
http://localhost:8000/admin/
http://127.0.0.1:8000/admin/
```

### Desde Otras PCs en la Red
```
http://192.168.100.10:8000/admin/
http://192.168.100.10:8000/clientes/
http://192.168.100.10:8000/api/docs/
```

### Desde Móviles (misma WiFi)
```
http://192.168.100.10:8000/clientes/
http://192.168.100.10:8000/pos/
```

---

## 🔐 Autenticación y Permisos

### Panel Admin
- **Requiere**: Superusuario o usuario staff
- **Login**: `/admin/`
- **Crear**: `python manage.py createsuperuser`

### Portal Clientes
- **Requiere**: Usuario cliente/padre
- **Login**: `/clientes/login/`
- **Registro**: `/clientes/registro/`

### API REST
- **Requiere**: Token JWT
- **Obtener token**: 
  ```bash
  curl -X POST http://192.168.100.10:8000/api/v1/auth/token/ \
    -H "Content-Type: application/json" \
    -d '{"username": "admin", "password": "tu_password"}'
  ```
- **Usar token**:
  ```bash
  curl http://192.168.100.10:8000/api/v1/productos/ \
    -H "Authorization: Bearer TU_TOKEN_AQUI"
  ```

---

## 🧪 Pruebas Rápidas

### 1. Verificar que el servidor funciona
```bash
# Abrir navegador en:
http://192.168.100.10:8000/
# Debe redirigir a /login/
```

### 2. Probar Admin
```bash
http://192.168.100.10:8000/admin/
# Debe mostrar pantalla de login con CSS correcto
```

### 3. Probar API (sin autenticación)
```bash
# Abrir en navegador:
http://192.168.100.10:8000/api/docs/
# Debe mostrar Swagger UI con todos los endpoints
```

### 4. Probar desde otra PC
```bash
# En otra PC en la misma red:
ping 192.168.100.10
# Luego abrir:
http://192.168.100.10:8000/admin/
```

---

## 📝 Notas Importantes

### Barra final (/) en URLs
- ✅ Correcto: `/admin/`
- ❌ Evitar: `/admin` (redirige con 301)

### Case sensitive
- URLs son sensibles a mayúsculas/minúsculas
- Usar siempre minúsculas

### Archivos estáticos
- Con DEBUG=True: Se sirven automáticamente
- Con DEBUG=False: Usar whitenoise o nginx

### CORS
- Configurado para localhost y 192.168.100.10
- Para otros orígenes, agregar a CORS_ALLOWED_ORIGINS

---

## 🔗 Enlaces Rápidos

### Desde Esta PC
- [Admin](http://127.0.0.1:8000/admin/)
- [Portal Clientes](http://127.0.0.1:8000/clientes/)
- [API Docs](http://127.0.0.1:8000/api/docs/)
- [Dashboard](http://127.0.0.1:8000/dashboard/)

### Desde Otras PCs (Reemplazar IP si es diferente)
- [Admin](http://192.168.100.10:8000/admin/)
- [Portal Clientes](http://192.168.100.10:8000/clientes/)
- [API Docs](http://192.168.100.10:8000/api/docs/)
- [POS](http://192.168.100.10:8000/pos/)

---

**Última actualización**: 10 de Enero de 2026, 21:50  
**IP del servidor**: 192.168.100.10  
**Puerto**: 8000  
**DEBUG**: True (para pruebas)
