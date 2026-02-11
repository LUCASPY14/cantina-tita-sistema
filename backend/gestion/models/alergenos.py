# gestion/models/alergenos.py

from django.db import models
from .base import ManagedModel
from .productos import Producto

class Alergeno(ManagedModel):
    '''Tabla alergenos - Catálogo de alérgenos e ingredientes restringidos'''
    SEVERIDAD_CHOICES = [
        ('CRITICO', 'Crítico'),
        ('ALTO', 'Alto'),
        ('MEDIO', 'Medio'),
        ('BAJO', 'Bajo'),
    ]
    
    id_alergeno = models.AutoField(db_column='id_alergeno', primary_key=True)
    nombre = models.CharField(db_column='nombre', max_length=100, unique=True)
    descripcion = models.TextField(db_column='descripcion', blank=True, null=True)
    palabras_clave = models.JSONField(
        db_column='palabras_clave',
        help_text='Array de palabras clave para búsqueda (ej: ["maní", "peanut", "cacahuete"])'
    )
    nivel_severidad = models.CharField(
        db_column='nivel_severidad',
        max_length=10,
        choices=SEVERIDAD_CHOICES,
        default='MEDIO'
    )
    icono = models.CharField(
        db_column='icono',
        max_length=10,
        blank=True,
        null=True,
        help_text='Emoji representativo (ej: 🥜, 🥛, 🌾)'
    )
    activo = models.BooleanField(db_column='activo', default=True)
    fecha_creacion = models.DateTimeField(db_column='fecha_creacion', auto_now_add=True)
    usuario_creacion = models.CharField(db_column='usuario_creacion', max_length=100, blank=True, null=True)
    
    class Meta(ManagedModel.Meta):
        db_table = 'alergenos'
        verbose_name = 'Alérgeno'
        verbose_name_plural = 'Alérgenos'
        ordering = ['nivel_severidad', 'nombre']
    
    def __str__(self):
        icono = f'{self.icono} ' if self.icono else ''
        return f'{icono}{self.nombre}'


class ProductoAlergeno(ManagedModel):
    '''Tabla producto_alergenos - Relación entre productos y alérgenos'''
    id_producto_alergeno = models.AutoField(db_column='id_producto_alergeno', primary_key=True)
    id_producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        db_column='id_producto',
        related_name='alergenos_producto'
    )
    id_alergeno = models.ForeignKey(
        Alergeno,
        on_delete=models.CASCADE,
        db_column='id_alergeno',
        related_name='productos_con_alergeno'
    )
    contiene = models.BooleanField(
        db_column='contiene',
        default=True,
        help_text='True: Contiene el alérgeno. False: Puede contener trazas'
    )
    observaciones = models.TextField(db_column='observaciones', blank=True, null=True)
    fecha_registro = models.DateTimeField(db_column='fecha_registro', auto_now_add=True)
    usuario_registro = models.CharField(db_column='usuario_registro', max_length=100, blank=True, null=True)
    
    class Meta(ManagedModel.Meta):
        db_table = 'producto_alergenos'
        verbose_name = 'Producto-Alérgeno'
        verbose_name_plural = 'Productos-Alérgenos'
        unique_together = [['id_producto', 'id_alergeno']]
    
    def __str__(self):
        tipo = 'Contiene' if self.contiene else 'Puede contener trazas de'
        return f'{self.id_producto.descripcion} - {tipo} {self.id_alergeno.nombre}'