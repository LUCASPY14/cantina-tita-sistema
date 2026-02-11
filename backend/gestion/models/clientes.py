# gestion/models/clientes.py

from django.db import models
from .base import ManagedModel
from .catalogos import TipoCliente, ListaPrecios

class Cliente(ManagedModel):
    '''Tabla clientes - Clientes existentes en la BD'''
    id_cliente = models.AutoField(db_column='id_cliente', primary_key=True)
    id_lista = models.ForeignKey(
        ListaPrecios, 
        on_delete=models.PROTECT, 
        db_column='id_lista'
    )
    id_tipo_cliente = models.ForeignKey(
        TipoCliente, 
        on_delete=models.PROTECT, 
        db_column='id_tipo_cliente'
    )
    nombres = models.CharField(db_column='nombres', max_length=100)
    apellidos = models.CharField(db_column='apellidos', max_length=100)
    razon_social = models.CharField(db_column='razon_social', max_length=255, blank=True, null=True)
    ruc_ci = models.CharField(db_column='ruc_ci', max_length=20, unique=True)
    direccion = models.CharField(db_column='direccion', max_length=255, blank=True, null=True)
    ciudad = models.CharField(db_column='ciudad', max_length=100, blank=True, null=True)
    telefono = models.CharField(db_column='telefono', max_length=20, blank=True, null=True)
    email = models.EmailField(db_column='email', blank=True, null=True)
    limite_credito = models.DecimalField(db_column='limite_credito', max_digits=12, decimal_places=2, blank=True, null=True)
    activo = models.BooleanField(db_column='activo', default=True)
    fecha_registro = models.DateTimeField(db_column='fecha_registro', auto_now_add=True)

    class Meta(ManagedModel.Meta):
        db_table = 'clientes'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return f'{self.apellidos}, {self.nombres} ({self.ruc_ci})'

    @property
    def nombre_completo(self):
        return f'{self.nombres} {self.apellidos}'


class Hijo(ManagedModel):
    '''Tabla hijos - Hijos de clientes para control de almuerzos'''
    id_hijo = models.AutoField(db_column='id_hijo', primary_key=True)
    id_cliente_responsable = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        db_column='id_cliente_responsable',
        related_name='hijos'
    )
    nombre = models.CharField(db_column='nombre', max_length=100)
    apellido = models.CharField(db_column='apellido', max_length=100)
    fecha_nacimiento = models.DateField(db_column='fecha_nacimiento', blank=True, null=True)
    grado = models.CharField(db_column='grado', max_length=50, blank=True, null=True)
    # restricciones_compra = models.TextField(db_column='restricciones_compra', blank=True, null=True)  # Columna no existe en MySQL
    foto_perfil = models.CharField(db_column='foto_perfil', max_length=255, blank=True, null=True)
    fecha_foto = models.DateTimeField(db_column='fecha_foto', blank=True, null=True)
    activo = models.BooleanField(db_column='activo', default=True)

    class Meta(ManagedModel.Meta):
        db_table = 'hijos'
        verbose_name = 'Hijo'
        verbose_name_plural = 'Hijos'

    def __str__(self):
        return f'{self.apellido}, {self.nombre}'

    @property
    def nombre_completo(self):
        return f'{self.nombre} {self.apellido}'
    
    @property
    def tiene_foto(self):
        return bool(self.foto_perfil)


class RestriccionesHijos(ManagedModel):
    '''Tabla restricciones_hijos - Restricciones alimentarias de hijos'''
    SEVERIDAD_CHOICES = [
        ('Leve', 'Leve'),
        ('Moderada', 'Moderada'),
        ('Severa', 'Severa'),
        ('Crítica', 'Crítica'),
    ]
    
    id_restriccion = models.AutoField(db_column='id_restriccion', primary_key=True)
    id_hijo = models.ForeignKey(
        Hijo,
        on_delete=models.CASCADE,
        db_column='id_hijo',
        related_name='restricciones'
    )
    tipo_restriccion = models.CharField(
        db_column='tipo_restriccion',
        max_length=100,
        help_text='Tipo: Celíaco, Intolerancia lactosa, Alergia maní, Vegetariano, etc.'
    )
    descripcion = models.TextField(
        db_column='descripcion',
        blank=True,
        null=True,
        help_text='Descripción detallada de la restricción'
    )
    observaciones = models.TextField(
        db_column='observaciones',
        blank=True,
        null=True,
        help_text='Observaciones adicionales o ingredientes específicos a evitar'
    )
    severidad = models.CharField(
        db_column='severidad',
        max_length=20,
        choices=SEVERIDAD_CHOICES,
        default='Moderada'
    )
    requiere_autorizacion = models.BooleanField(
        db_column='requiere_autorizacion',
        default=True,
        help_text='Si requiere autorización para consumir productos restringidos'
    )
    fecha_registro = models.DateTimeField(db_column='fecha_registro', auto_now_add=True)
    fecha_ultima_actualizacion = models.DateTimeField(db_column='fecha_ultima_actualizacion', auto_now=True)
    activo = models.BooleanField(db_column='activo', default=True)
    
    class Meta(ManagedModel.Meta):
        db_table = 'restricciones_hijos'
        verbose_name = 'Restricción Alimentaria'
        verbose_name_plural = 'Restricciones Alimentarias'
        ordering = ['-severidad', 'tipo_restriccion']
    
    def __str__(self):
        return f'{self.id_hijo.nombre_completo} - {self.tipo_restriccion} ({self.severidad})'