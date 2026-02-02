# gestion/models/base.py
from django.db import models
from django.utils import timezone
import sys

class ManagedModel(models.Model):
    """Clase base para todos los modelos con managed dinámico"""
    
    class Meta:
        abstract = True
        managed = 'test' not in sys.argv  # True para tests, False para producción