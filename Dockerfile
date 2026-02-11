# Dockerfile para Django Backend
FROM python:3.12-slim

# Metadata
LABEL maintainer="Cantina Tita Sistema"
LABEL description="Django Backend para Sistema de Gestión de Cantina"
LABEL version="1.0.0"

# Variables de entorno para Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    netcat-traditional \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements y instalar dependencias Python
COPY backend/requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install gunicorn

# Copiar código de la aplicación
COPY backend/ .

# Crear directorios necesarios
RUN mkdir -p /app/media /app/staticfiles /app/logs && \
    chmod -R 755 /app/media /app/staticfiles /app/logs

# Script de entrada para esperar por MySQL
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Exponer puerto
EXPOSE 8000

# Usuario no-root para seguridad
RUN useradd -m -u 1000 django && \
    chown -R django:django /app
USER django

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Punto de entrada
ENTRYPOINT ["/entrypoint.sh"]

# Comando por defecto
CMD ["gunicorn", "cantina_project.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120"]
