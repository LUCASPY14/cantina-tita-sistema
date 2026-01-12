# ==================== CONFIGURACIÓN DE GUNICORN ====================
# Archivo: gunicorn_config.py
# Uso: gunicorn -c gunicorn_config.py cantinatita.wsgi:application

import multiprocessing

# Bind - IP y Puerto
bind = "127.0.0.1:8000"

# Workers - Número de procesos trabajadores
# Recomendación: (2 × núcleos de CPU) + 1
workers = multiprocessing.cpu_count() * 2 + 1

# Worker class
worker_class = "sync"

# Threads por worker (para requests I/O bound)
threads = 2

# Worker connections (para workers async)
worker_connections = 1000

# Timeout - Tiempo máximo para requests (en segundos)
timeout = 120

# Keepalive - Mantener conexiones vivas
keepalive = 5

# Logging
accesslog = "logs/gunicorn_access.log"
errorlog = "logs/gunicorn_error.log"
loglevel = "info"

# Process naming
proc_name = "cantinatita_gunicorn"

# Server mechanics
daemon = False
pidfile = "gunicorn.pid"
user = None  # Cambiar al usuario del sistema que ejecutará gunicorn
group = None  # Cambiar al grupo del sistema

# SSL (si se usa SSL directamente en Gunicorn)
# keyfile = "/path/to/ssl/key.pem"
# certfile = "/path/to/ssl/cert.pem"

# Worker reload (útil en desarrollo, desactivar en producción)
reload = False

# Max requests per worker (previene memory leaks)
max_requests = 1000
max_requests_jitter = 50

# Preload app (carga la aplicación antes de fork workers)
preload_app = True

# Temp directory
# worker_tmp_dir = "/dev/shm"  # Usar RAM para archivos temporales (Linux)

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Server hooks
def on_starting(server):
    """Ejecutado al iniciar el servidor"""
    print("=" * 60)
    print("🚀 Iniciando Cantina Tita - Servidor Gunicorn")
    print(f"Workers: {workers}")
    print(f"Threads: {threads}")
    print(f"Bind: {bind}")
    print("=" * 60)

def on_reload(server):
    """Ejecutado al recargar"""
    print("♻️  Recargando configuración...")

def when_ready(server):
    """Ejecutado cuando el servidor está listo"""
    print("✅ Servidor listo para recibir requests")

def pre_fork(server, worker):
    """Ejecutado antes de fork cada worker"""
    pass

def post_fork(server, worker):
    """Ejecutado después de fork cada worker"""
    print(f"👷 Worker {worker.pid} iniciado")

def pre_request(worker, req):
    """Ejecutado antes de cada request"""
    pass

def post_request(worker, req, environ, resp):
    """Ejecutado después de cada request"""
    pass

def worker_exit(server, worker):
    """Ejecutado cuando un worker termina"""
    print(f"👋 Worker {worker.pid} terminado")

# ==================== VARIABLES DE ENTORNO ====================
# Asegurarse de que estas variables estén configuradas en el servidor:
# export DJANGO_SETTINGS_MODULE=cantinatita.settings
# export SECRET_KEY='tu-secret-key-super-segura'
# export DATABASE_NAME='cantinatitadb'
# export DATABASE_USER='root'
# export DATABASE_PASSWORD='tu-password'
# export DATABASE_HOST='localhost'
# export DATABASE_PORT='3306'
