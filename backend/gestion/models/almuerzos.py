# gestion/models/almuerzos.py

from django.db import models
from .base import ManagedModel
from .clientes import Hijo
from .tarjetas import Tarjeta
from pos.models import Venta as Ventas  # MIGRADO: Usar modelo de pos app
from .empleados import Empleado

class TipoAlmuerzo(ManagedModel):
    '''Tabla tipos_almuerzo - Catálogo de tipos de almuerzo'''
    id_tipo_almuerzo = models.AutoField(db_column='id_tipo_almuerzo', primary_key=True)
    nombre = models.CharField(db_column='nombre', max_length=100)
    descripcion = models.TextField(db_column='descripcion', blank=True, null=True)
    precio_unitario = models.DecimalField(db_column='precio_unitario', max_digits=10, decimal_places=2)
    incluye_plato_principal = models.BooleanField(db_column='incluye_plato_principal', default=True)
    incluye_postre = models.BooleanField(db_column='incluye_postre', default=False)
    incluye_bebida = models.BooleanField(db_column='incluye_bebida', default=False)
    fecha_creacion = models.DateTimeField(db_column='fecha_creacion', auto_now_add=True)
    activo = models.BooleanField(db_column='activo', default=True)

    class Meta(ManagedModel.Meta):
        db_table = 'tipos_almuerzo'
        verbose_name = 'Tipo de Almuerzo'
        verbose_name_plural = 'Tipos de Almuerzo'

    def __str__(self):
        return f'{self.nombre} - Gs. {self.precio_unitario:,.0f}'
    
    def get_componentes(self):
        '''Retorna lista de componentes incluidos'''
        componentes = []
        if self.incluye_plato_principal:
            componentes.append('Plato Principal')
        if self.incluye_postre:
            componentes.append('Postre')
        if self.incluye_bebida:
            componentes.append('Bebida')
        return componentes
    
    def get_componentes_display(self):
        '''Retorna string con componentes separados por coma'''
        return ', '.join(self.get_componentes())


class PlanesAlmuerzo(ManagedModel):
    '''Tabla planes_almuerzo - Planes de almuerzo disponibles'''
    id_plan_almuerzo = models.AutoField(db_column='id_plan_almuerzo', primary_key=True)
    nombre_plan = models.CharField(db_column='nombre_plan', max_length=100, unique=True)
    descripcion = models.TextField(db_column='descripcion', blank=True, null=True)
    precio_mensual = models.DecimalField(db_column='precio_mensual', max_digits=10, decimal_places=2)
    dias_semana_incluidos = models.CharField(db_column='dias_semana_incluidos', max_length=60)
    fecha_creacion = models.DateTimeField(db_column='fecha_creacion', blank=True, null=True)
    activo = models.BooleanField(db_column='activo', default=True)

    class Meta(ManagedModel.Meta):
        db_table = 'planes_almuerzo'
        verbose_name = 'Plan de Almuerzo'
        verbose_name_plural = 'Planes de Almuerzo'

    def __str__(self):
        return f'{self.nombre_plan} - Gs. {self.precio_mensual}'


class SuscripcionesAlmuerzo(ManagedModel):
    '''Tabla suscripciones_almuerzo - Suscripciones de almuerzos'''
    ESTADO_CHOICES = [
        ('Activa', 'Activa'),
        ('Suspendida', 'Suspendida'),
        ('Cancelada', 'Cancelada'),
    ]

    id_suscripcion = models.BigAutoField(db_column='id_suscripcion', primary_key=True)
    id_hijo = models.ForeignKey(
        Hijo,
        on_delete=models.PROTECT,
        db_column='id_hijo',
        related_name='suscripciones'
    )
    id_plan_almuerzo = models.ForeignKey(
        PlanesAlmuerzo,
        on_delete=models.PROTECT,
        db_column='id_plan_almuerzo'
    )
    fecha_inicio = models.DateField(db_column='fecha_inicio')
    fecha_fin = models.DateField(db_column='fecha_fin', blank=True, null=True)
    estado = models.CharField(db_column='estado', max_length=10, choices=ESTADO_CHOICES, blank=True, null=True)

    class Meta(ManagedModel.Meta):
        db_table = 'suscripciones_almuerzo'
        verbose_name = 'Suscripción de Almuerzo'
        verbose_name_plural = 'Suscripciones de Almuerzo'
        unique_together = (('id_hijo', 'id_plan_almuerzo', 'estado'),)

    def __str__(self):
        return f'{self.id_hijo.nombre_completo} - {self.id_plan_almuerzo.nombre_plan}'


class PagosAlmuerzoMensual(ManagedModel):
    '''Tabla pagos_almuerzo_mensual - Pagos mensuales de almuerzos'''
    ESTADO_CHOICES = [
        ('Pagado', 'Pagado'),
        ('Pendiente', 'Pendiente'),
        ('Vencido', 'Vencido'),
    ]

    id_pago_almuerzo = models.BigAutoField(db_column='id_pago_almuerzo', primary_key=True)
    id_suscripcion = models.ForeignKey(
        SuscripcionesAlmuerzo,
        on_delete=models.PROTECT,
        db_column='id_suscripcion',
        related_name='pagos'
    )
    fecha_pago = models.DateTimeField(db_column='fecha_pago')
    monto_pagado = models.DecimalField(db_column='monto_pagado', max_digits=10, decimal_places=2)
    mes_pagado = models.DateField(db_column='mes_pagado')
    id_venta = models.OneToOneField(
        Ventas,
        on_delete=models.SET_NULL,
        db_column='id_venta',
        blank=True,
        null=True
    )
    estado = models.CharField(db_column='estado', max_length=9, choices=ESTADO_CHOICES, blank=True, null=True)

    class Meta(ManagedModel.Meta):
        db_table = 'pagos_almuerzo_mensual'
        verbose_name = 'Pago de Almuerzo Mensual'
        verbose_name_plural = 'Pagos de Almuerzo Mensual'
        unique_together = (('id_suscripcion', 'mes_pagado'),)

    def __str__(self):
        return f'Pago {self.mes_pagado} - {self.id_suscripcion.id_hijo.nombre_completo}'


class CuentaAlmuerzoMensual(ManagedModel):
    '''Tabla cuentas_almuerzo_mensual - Cuentas mensuales de almuerzo'''
    FORMA_COBRO_CHOICES = [
        ('CONTADO_ANTICIPADO', 'Contado Anticipado'),
        ('CREDITO_MENSUAL', 'Crédito Mensual'),
    ]
    
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('PARCIAL', 'Parcial'),
        ('PAGADO', 'Pagado'),
    ]

    id_cuenta = models.BigAutoField(db_column='id_cuenta', primary_key=True)
    id_hijo = models.ForeignKey(
        Hijo,
        on_delete=models.PROTECT,
        db_column='id_hijo'
    )
    anio = models.IntegerField(db_column='anio')
    mes = models.SmallIntegerField(db_column='mes')
    cantidad_almuerzos = models.IntegerField(db_column='cantidad_almuerzos', default=0)
    monto_total = models.DecimalField(db_column='monto_total', max_digits=10, decimal_places=2, default=0)
    forma_cobro = models.CharField(db_column='forma_cobro', max_length=20, choices=FORMA_COBRO_CHOICES)
    monto_pagado = models.DecimalField(db_column='monto_pagado', max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(db_column='estado', max_length=10, choices=ESTADO_CHOICES, default='PENDIENTE')
    fecha_generacion = models.DateField(db_column='fecha_generacion')
    fecha_actualizacion = models.DateTimeField(db_column='fecha_actualizacion', auto_now=True)
    observaciones = models.TextField(db_column='observaciones', blank=True, null=True)

    class Meta(ManagedModel.Meta):
        db_table = 'cuentas_almuerzo_mensual'
        verbose_name = 'Cuenta Mensual de Almuerzo'
        verbose_name_plural = 'Cuentas Mensuales de Almuerzo'
        unique_together = [['id_hijo', 'anio', 'mes']]
        ordering = ['-anio', '-mes']

    def __str__(self):
        return f'{self.id_hijo.nombre_completo} - {self.mes}/{self.anio}'
    
    @property
    def saldo_pendiente(self):
        return self.monto_total - self.monto_pagado
    
    @property
    def nombre_mes(self):
        meses = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        return meses[self.mes] if 1 <= self.mes <= 12 else ''


class RegistroConsumoAlmuerzo(ManagedModel):
    '''Tabla registro_consumo_almuerzo - Registro diario de almuerzos'''
    id_registro_consumo = models.BigAutoField(db_column='id_registro_consumo', primary_key=True)
    id_hijo = models.ForeignKey(
        Hijo,
        on_delete=models.PROTECT,
        db_column='id_hijo'
    )
    nro_tarjeta = models.ForeignKey(
        Tarjeta,
        on_delete=models.PROTECT,
        db_column='nro_tarjeta',
        blank=True,
        null=True,
        related_name='registros_almuerzo'
    )
    id_tipo_almuerzo = models.ForeignKey(
        TipoAlmuerzo,
        on_delete=models.PROTECT,
        db_column='id_tipo_almuerzo',
        blank=True,
        null=True
    )
    fecha_consumo = models.DateField(db_column='fecha_consumo', auto_now_add=True)
    costo_almuerzo = models.DecimalField(db_column='costo_almuerzo', max_digits=10, decimal_places=2, blank=True, null=True)
    marcado_en_cuenta = models.BooleanField(db_column='marcado_en_cuenta', default=False)
    id_suscripcion = models.BigIntegerField(db_column='id_suscripcion', blank=True, null=True)
    hora_registro = models.TimeField(db_column='hora_registro', auto_now_add=True)

    class Meta(ManagedModel.Meta):
        db_table = 'registro_consumo_almuerzo'
        verbose_name = 'Registro de Almuerzo'
        verbose_name_plural = 'Registros de Almuerzos'
        ordering = ['-fecha_consumo', '-hora_registro']

    def __str__(self):
        return f'{self.id_hijo.nombre_completo} - {self.fecha_consumo}'


class PagoCuentaAlmuerzo(ManagedModel):
    '''Tabla pagos_cuentas_almuerzo - Pagos de cuentas de almuerzo'''
    MEDIO_PAGO_CHOICES = [
        ('EFECTIVO', 'Efectivo'),
        ('DEBITO', 'Débito'),
        ('CREDITO', 'Crédito'),
        ('TRANSFERENCIA', 'Transferencia'),
        ('OTRO', 'Otro'),
    ]

    id_pago = models.BigAutoField(db_column='id_pago', primary_key=True)
    id_cuenta = models.ForeignKey(
        CuentaAlmuerzoMensual,
        on_delete=models.PROTECT,
        db_column='id_cuenta',
        related_name='pagos'
    )
    fecha_pago = models.DateTimeField(db_column='fecha_pago', auto_now_add=True)
    medio_pago = models.CharField(db_column='medio_pago', max_length=15, choices=MEDIO_PAGO_CHOICES)
    monto = models.DecimalField(db_column='monto', max_digits=10, decimal_places=2)
    referencia = models.CharField(db_column='referencia', max_length=50, blank=True, null=True)
    observaciones = models.TextField(db_column='observaciones', blank=True, null=True)
    id_empleado_registro = models.ForeignKey(
        Empleado,
        on_delete=models.SET_NULL,
        db_column='id_empleado_registro',
        blank=True,
        null=True
    )

    class Meta(ManagedModel.Meta):
        db_table = 'pagos_cuentas_almuerzo'
        verbose_name = 'Pago de Cuenta de Almuerzo'
        verbose_name_plural = 'Pagos de Cuentas de Almuerzo'
        ordering = ['-fecha_pago']

    def __str__(self):
        return f'Pago #{self.id_pago} - Gs. {self.monto:,.0f}'