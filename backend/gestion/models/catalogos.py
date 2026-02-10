# gestion/models/catalogos.py

from django.db import models
from .base import ManagedModel

class ListaPrecios(ManagedModel):
    '''Tabla listas_precios - Listas de precios para clientes'''
    id_lista = models.AutoField(db_column='id_lista', primary_key=True)
    nombre_lista = models.CharField(db_column='nombre_lista', max_length=100, unique=True)
    fecha_vigencia = models.DateField(db_column='fecha_vigencia', blank=True, null=True)
    moneda = models.CharField(db_column='moneda', max_length=3, default='PYG')
    activo = models.BooleanField(db_column='activo', default=True)

    class Meta(ManagedModel.Meta):
        db_table = 'listas_precios'
        verbose_name = 'Lista de Precios'
        verbose_name_plural = 'Listas de Precios'

    def __str__(self):
        return self.nombre_lista

class TipoCliente(ManagedModel):
    '''Tabla tipos_cliente - Tipos de cliente existentes'''
    id_tipo_cliente = models.AutoField(db_column='id_tipo_cliente', primary_key=True)
    nombre_tipo = models.CharField(db_column='nombre_tipo', max_length=50, unique=True)
    activo = models.BooleanField(db_column='activo', default=True)

    class Meta(ManagedModel.Meta):
        db_table = 'tipos_cliente'
        verbose_name = 'Tipo de Cliente'
        verbose_name_plural = 'Tipos de Cliente'

    def __str__(self):
        return self.nombre_tipo


class Categoria(ManagedModel):
    '''Tabla categorias - Categorías de productos'''
    id_categoria = models.AutoField(db_column='id_categoria', primary_key=True)
    nombre = models.CharField(db_column='nombre', max_length=100)
    id_categoria_padre = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        db_column='id_categoria_padre',
        blank=True, 
        null=True,
        related_name='subcategorias'
    )
    activo = models.BooleanField(db_column='activo', default=True)

    class Meta(ManagedModel.Meta):
        db_table = 'categorias'
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'

    def __str__(self):
        return self.nombre


class UnidadMedida(ManagedModel):
    '''Tabla unidades_medida'''
    id_unidad_medida = models.AutoField(db_column='id_unidad_de_medida', primary_key=True)
    nombre = models.CharField(db_column='nombre', max_length=50)
    abreviatura = models.CharField(db_column='abreviatura', max_length=10)
    activo = models.BooleanField(db_column='activo', default=True)

    class Meta(ManagedModel.Meta):
        db_table = 'unidades_medida'
        verbose_name = 'Unidad de Medida'
        verbose_name_plural = 'Unidades de Medida'

    def __str__(self):
        return f'{self.nombre} ({self.abreviatura})'


class Impuesto(ManagedModel):
    '''Tabla impuestos'''
    id_impuesto = models.AutoField(db_column='id_impuesto', primary_key=True)
    nombre_impuesto = models.CharField(db_column='nombre_impuesto', max_length=50, unique=True)
    porcentaje = models.DecimalField(db_column='porcentaje', max_digits=4, decimal_places=2)
    vigente_desde = models.DateField(db_column='vigente_desde')
    vigente_hasta = models.DateField(db_column='vigente_hasta', blank=True, null=True)
    activo = models.BooleanField(db_column='activo', default=True)

    class Meta(ManagedModel.Meta):
        db_table = 'impuestos'
        verbose_name = 'Impuesto'
        verbose_name_plural = 'Impuestos'

    def __str__(self):
        return f'{self.nombre_impuesto} ({self.porcentaje}%)'


class TipoRolGeneral(ManagedModel):
    '''Tabla tipos_rol_general'''
    id_rol = models.AutoField(db_column='id_rol', primary_key=True)
    nombre_rol = models.CharField(db_column='nombre_rol', max_length=50, unique=True)
    descripcion = models.CharField(db_column='descripcion', max_length=100, blank=True, null=True)
    activo = models.BooleanField(db_column='activo', default=True)

    class Meta(ManagedModel.Meta):
        db_table = 'tipos_rol_general'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.nombre_rol


class MediosPago(ManagedModel):
    '''Tabla medios_pago - Medios de pago'''
    id_medio_pago = models.AutoField(db_column='id_medio_pago', primary_key=True)
    descripcion = models.CharField(db_column='descripcion', max_length=50, unique=True)
    genera_comision = models.BooleanField(db_column='genera_comision', default=False)
    requiere_validacion = models.BooleanField(db_column='requiere_validacion', default=False)
    activo = models.BooleanField(db_column='activo', default=True)

    class Meta(ManagedModel.Meta):
        db_table = 'medios_pago'
        verbose_name = 'Medio de Pago'
        verbose_name_plural = 'Medios de Pago'

    def __str__(self):
        return self.descripcion


class TarifasComision(ManagedModel):
    '''Tabla tarifas_comision - Tarifas de comisión por medio de pago'''
    id_tarifa = models.AutoField(db_column='id_tarifa', primary_key=True)
    id_medio_pago = models.ForeignKey(
        MediosPago,
        on_delete=models.CASCADE,
        db_column='id_medio_pago',
        related_name='tarifas'
    )
    fecha_inicio_vigencia = models.DateTimeField(db_column='fecha_inicio_vigencia')
    fecha_fin_vigencia = models.DateTimeField(db_column='fecha_fin_vigencia', blank=True, null=True)
    porcentaje_comision = models.DecimalField(db_column='porcentaje_comision', max_digits=5, decimal_places=4)
    monto_fijo_comision = models.DecimalField(db_column='monto_fijo_comision', max_digits=10, decimal_places=2, blank=True, null=True)
    activo = models.BooleanField(db_column='activo', default=True)

    class Meta(ManagedModel.Meta):
        db_table = 'tarifas_comision'
        verbose_name = 'Tarifa de Comisión'
        verbose_name_plural = 'Tarifas de Comisión'

    def __str__(self):
        return f'{self.id_medio_pago.descripcion}: {self.porcentaje_comision}%'


class TiposPago(ManagedModel):
    '''Tabla tipos_pago - Tipos de pago'''
    id_tipo_pago = models.AutoField(db_column='id_tipo_pago', primary_key=True)
    descripcion = models.CharField(db_column='descripcion', max_length=50, unique=True)
    activo = models.BooleanField(db_column='activo', default=True)

    class Meta(ManagedModel.Meta):
        db_table = 'tipos_pago'
        verbose_name = 'Tipo de Pago'
        verbose_name_plural = 'Tipos de Pago'

    def __str__(self):
        return self.descripcion


class Grado(ManagedModel):
    '''Tabla grados - Catálogo de niveles educativos'''
    id_grado = models.AutoField(db_column='id_grado', primary_key=True)
    nombre_grado = models.CharField(db_column='nombre_grado', max_length=50, unique=True)
    nivel = models.IntegerField(db_column='nivel')
    orden_visualizacion = models.IntegerField(db_column='orden_visualizacion')
    es_ultimo_grado = models.BooleanField(db_column='es_ultimo_grado', default=False)
    activo = models.BooleanField(db_column='activo', default=True)
    fecha_creacion = models.DateTimeField(db_column='fecha_creacion', auto_now_add=True)

    class Meta(ManagedModel.Meta):
        db_table = 'grados'
        verbose_name = 'Grado'
        verbose_name_plural = 'Grados'
        ordering = ['orden_visualizacion']

    def __str__(self):
        return self.nombre_grado

    def siguiente_grado(self):
        '''Retorna el siguiente grado en la secuencia'''
        siguiente = Grado.objects.filter(
            nivel=self.nivel + 1,
            activo=True
        ).first()
        return siguiente