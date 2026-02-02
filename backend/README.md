# Backend - Cantina Tita Sistema

## Django API Backend

### Tecnologías
- Django 5.2.8
- Django REST Framework
- MySQL
- JWT Authentication

### Configuración

1. **Crear entorno virtual:**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
```

2. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

3. **Variables de entorno:**
Crear archivo `.env` con:
```
SECRET_KEY=tu-secret-key
DEBUG=True
DATABASE_URL=mysql://usuario:password@localhost/cantina_db
```

4. **Migrar base de datos:**
```bash
python manage.py migrate
```

5. **Crear superusuario:**
```bash
python manage.py createsuperuser
```

6. **Ejecutar servidor:**
```bash
python manage.py runserver 0.0.0.0:8000
```

### API Endpoints
- `/api/` - API REST endpoints
- `/admin/` - Django Admin
- `/api/docs/` - Documentación API (Swagger)

### Apps
- `gestion` - Gestión general del sistema
- `pos` - Punto de venta