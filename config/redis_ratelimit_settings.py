"""
Configuración de Redis Cache y Rate Limiting
Agregar al settings.py
"""

# =============================================================================
# REDIS CACHE CONFIGURATION
# =============================================================================

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'IGNORE_EXCEPTIONS': True,  # No fallar si Redis no está disponible
        },
        'KEY_PREFIX': 'cantina',
        'TIMEOUT': 300,  # 5 minutos por defecto
    },
    # Cache separado para sesiones
    'sessions': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/2',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'session',
        'TIMEOUT': 86400,  # 24 horas
    },
}

# Usar Redis para sesiones
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'sessions'

# =============================================================================
# CACHE SETTINGS
# =============================================================================

# Cache para vistas
CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 300
CACHE_MIDDLEWARE_KEY_PREFIX = 'views'

# Cache timeouts personalizados
CACHE_TIMEOUTS = {
    'dashboard': 60,           # 1 minuto
    'productos': 300,          # 5 minutos
    'categorias': 600,         # 10 minutos
    'reportes': 1800,          # 30 minutos
    'saldos': 30,              # 30 segundos
    'estadisticas': 180,       # 3 minutos
}

# =============================================================================
# RATE LIMITING CONFIGURATION
# =============================================================================

# django-ratelimit configuración
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'

# Límites por tipo de endpoint
RATELIMIT_RATES = {
    # Autenticación (más restrictivo)
    'login': '5/h',           # 5 intentos por hora
    'register': '3/h',         # 3 registros por hora
    'password_reset': '3/h',   # 3 resets por hora
    
    # APIs generales
    'api_read': '100/h',       # 100 lecturas por hora
    'api_write': '50/h',       # 50 escrituras por hora
    
    # APIs críticas
    'venta': '200/h',          # 200 ventas por hora
    'recarga': '30/h',         # 30 recargas por hora
    
    # Portal padres
    'portal': '60/h',          # 60 requests por hora
    
    # Admin
    'admin': '1000/h',         # 1000 requests por hora
}

# Mensaje de error cuando se excede el rate limit
RATELIMIT_VIEW = 'gestion.views.rate_limit_exceeded'

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'cantina.log'),
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'errors.log'),
            'maxBytes': 10485760,
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'security.log'),
            'maxBytes': 10485760,
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['error_file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'gestion': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}

# Crear directorio de logs si no existe
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)
