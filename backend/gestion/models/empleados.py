# gestion/models/empleados.py

from django.db import models
from .base import ManagedModel
from .catalogos import TipoRolGeneral

class Empleado(ManagedModel):
    '''Tabla empleados'''
    id_empleado = models.AutoField(db_column='ID_Empleado', primary_key=True)
    id_rol = models.ForeignKey(
        TipoRolGeneral, 
        on_delete=models.PROTECT, 
        db_column='ID_Rol'
    )
    nombre = models.CharField(db_column='Nombre', max_length=100)
    apellido = models.CharField(db_column='Apellido', max_length=100)
    usuario = models.CharField(db_column='Usuario', max_length=50, unique=True)
    contrasena_hash = models.CharField(db_column='Contrasena_Hash', max_length=60)
    fecha_ingreso = models.DateTimeField(db_column='Fecha_Ingreso', auto_now_add=True)
    direccion = models.CharField(db_column='Direccion', max_length=255, blank=True, null=True)
    ciudad = models.CharField(db_column='Ciudad', max_length=100, blank=True, null=True)
    pais = models.CharField(db_column='Pais', max_length=100, blank=True, null=True)
    telefono = models.CharField(db_column='Telefono', max_length=20, blank=True, null=True)
    email = models.EmailField(db_column='Email', blank=True, null=True)
    activo = models.BooleanField(db_column='Activo', default=True)
    fecha_baja = models.DateTimeField(db_column='Fecha_Baja', blank=True, null=True)

    class Meta(ManagedModel.Meta):
        db_table = 'empleados'
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'

    def __str__(self):
        return f'{self.apellido}, {self.nombre}'

    @property
    def nombre_completo(self):
        return f'{self.nombre} {self.apellido}'