"""
Configuración específica para tests
"""
from .settings import *

# Indicar que estamos en modo test
TESTING = True

# Base de datos en memoria para tests rápidos
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Desactivar cache para tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Desactivar migraciones para tests más rápidos
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Password hashers simples para tests rápidos
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Desactivar debug para tests
DEBUG = False

# Email backend de consola para tests
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
