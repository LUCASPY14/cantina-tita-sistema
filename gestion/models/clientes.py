# gestion/models/clientes.py

from django.db import models
from .base import ManagedModel
from .catalogos import TipoCliente, ListaPrecios

class Cliente(ManagedModel):
    '''Tabla clientes - Clientes existentes en la BD'''
    id_cliente = models.AutoField(db_column='ID_Cliente', primary_key=True)
    id_lista = models.ForeignKey(
        ListaPrecios, 
        on_delete=models.PROTECT, 
        db_column='ID_Lista'
    )
    id_tipo_cliente = models.ForeignKey(
        TipoCliente, 
        on_delete=models.PROTECT, 
        db_column='ID_Tipo_Cliente'
    )
    nombres = models.CharField(db_column='Nombres', max_length=100)
    apellidos = models.CharField(db_column='Apellidos', max_length=100)
    razon_social = models.CharField(db_column='Razon_Social', max_length=255, blank=True, null=True)
    ruc_ci = models.CharField(db_column='Ruc_CI', max_length=20, unique=True)
    direccion = models.CharField(db_column='Direccion', max_length=255, blank=True, null=True)
    ciudad = models.CharField(db_column='Ciudad', max_length=100, blank=True, null=True)
    telefono = models.CharField(db_column='Telefono', max_length=20, blank=True, null=True)
    email = models.EmailField(db_column='Email', blank=True, null=True)
    limite_credito = models.DecimalField(db_column='Limite_Credito', max_digits=12, decimal_places=2, blank=True, null=True)
    activo = models.BooleanField(db_column='Activo', default=True)
    fecha_registro = models.DateTimeField(db_column='Fecha_Registro', auto_now_add=True)

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
    id_hijo = models.AutoField(db_column='ID_Hijo', primary_key=True)
    id_cliente_responsable = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        db_column='ID_Cliente_Responsable',
        related_name='hijos'
    )
    nombre = models.CharField(db_column='Nombre', max_length=100)
    apellido = models.CharField(db_column='Apellido', max_length=100)
    fecha_nacimiento = models.DateField(db_column='Fecha_Nacimiento', blank=True, null=True)
    grado = models.CharField(db_column='Grado', max_length=50, blank=True, null=True)
    restricciones_compra = models.TextField(db_column='Restricciones_Compra', blank=True, null=True)
    foto_perfil = models.CharField(db_column='Foto_Perfil', max_length=255, blank=True, null=True)
    fecha_foto = models.DateTimeField(db_column='Fecha_Foto', blank=True, null=True)
    activo = models.BooleanField(db_column='Activo', default=True)

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
    
    id_restriccion = models.AutoField(db_column='ID_Restriccion', primary_key=True)
    id_hijo = models.ForeignKey(
        Hijo,
        on_delete=models.CASCADE,
        db_column='ID_Hijo',
        related_name='restricciones'
    )
    tipo_restriccion = models.CharField(
        db_column='Tipo_Restriccion',
        max_length=100,
        help_text='Tipo: Celíaco, Intolerancia lactosa, Alergia maní, Vegetariano, etc.'
    )
    descripcion = models.TextField(
        db_column='Descripcion',
        blank=True,
        null=True,
        help_text='Descripción detallada de la restricción'
    )
    observaciones = models.TextField(
        db_column='Observaciones',
        blank=True,
        null=True,
        help_text='Observaciones adicionales o ingredientes específicos a evitar'
    )
    severidad = models.CharField(
        db_column='Severidad',
        max_length=20,
        choices=SEVERIDAD_CHOICES,
        default='Moderada'
    )
    requiere_autorizacion = models.BooleanField(
        db_column='Requiere_Autorizacion',
        default=True,
        help_text='Si requiere autorización para consumir productos restringidos'
    )
    fecha_registro = models.DateTimeField(db_column='Fecha_Registro', auto_now_add=True)
    fecha_ultima_actualizacion = models.DateTimeField(db_column='Fecha_Ultima_Actualizacion', auto_now=True)
    activo = models.BooleanField(db_column='Activo', default=True)
    
    class Meta(ManagedModel.Meta):
        db_table = 'restricciones_hijos'
        verbose_name = 'Restricción Alimentaria'
        verbose_name_plural = 'Restricciones Alimentarias'
        ordering = ['-severidad', 'tipo_restriccion']
    
    def __str__(self):
        return f'{self.id_hijo.nombre_completo} - {self.tipo_restriccion} ({self.severidad})'