# gestion/models/tarjetas.py

from django.db import models
from .base import ManagedModel
from .clientes import Hijo, Cliente
from .empleados import Empleado
# REMOVIDO: from .ventas import NotasCreditoCliente  # Causa ciclo


class Tarjeta(ManagedModel):
    '''Tabla tarjetas - Tarjetas de hijos'''
    ESTADO_CHOICES = [
        ('Activa', 'Activa'),
        ('Bloqueada', 'Bloqueada'),
        ('Vencida', 'Vencida'),
    ]

    nro_tarjeta = models.CharField(db_column='nro_tarjeta', max_length=20, primary_key=True)
    id_hijo = models.OneToOneField(
        Hijo,
        on_delete=models.PROTECT,
        db_column='id_hijo',
        unique=True
    )
    saldo_actual = models.DecimalField(
        db_column='saldo_actual', 
        max_digits=12, 
        decimal_places=2, 
        default=0
    )
    estado = models.CharField(db_column='estado', max_length=20, choices=ESTADO_CHOICES, default='Activa')
    fecha_vencimiento = models.DateField(db_column='fecha_vencimiento', blank=True, null=True)
    saldo_alerta = models.DecimalField(db_column='saldo_alerta', max_digits=10, decimal_places=2, blank=True, null=True)
    fecha_creacion = models.DateTimeField(db_column='fecha_creacion', auto_now_add=True)
    
    # Campos para autorización de saldo negativo
    permite_saldo_negativo = models.BooleanField(
        db_column='permite_saldo_negativo',
        default=False,
        help_text='Indica si la tarjeta puede tener saldo negativo con autorización'
    )
    limite_credito = models.DecimalField(
        db_column='limite_credito',
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Monto máximo de crédito (saldo negativo) permitido en guaraníes'
    )
    notificar_saldo_bajo = models.BooleanField(
        db_column='notificar_saldo_bajo',
        default=True,
        help_text='Enviar notificaciones cuando el saldo está bajo o negativo'
    )
    ultima_notificacion_saldo = models.DateTimeField(
        db_column='ultima_notificacion_saldo',
        blank=True,
        null=True,
        help_text='Fecha de la última notificación de saldo enviada'
    )

    class Meta(ManagedModel.Meta):
        db_table = 'tarjetas'
        verbose_name = 'Tarjeta'
        verbose_name_plural = 'Tarjetas'

    def __str__(self):
        return f'{self.nro_tarjeta} - {self.id_hijo.nombre_completo}'


class CargasSaldo(ManagedModel):
    '''Tabla cargas_saldo - Cargas de saldo a tarjetas'''
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('CONFIRMADO', 'Confirmado'),
        ('CANCELADO', 'Cancelado'),
        ('ERROR', 'Error')
    ]

    id_carga = models.BigAutoField(db_column='id_carga', primary_key=True)
    nro_tarjeta = models.ForeignKey(
        Tarjeta,
        on_delete=models.PROTECT,
        db_column='nro_tarjeta'
    )
    id_cliente_origen = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        db_column='id_cliente_origen',
        related_name='cargas_origen',
        blank=True,
        null=True
    )
    id_nota = models.ForeignKey(
            'gestion.NotasCreditoCliente',  # Confirmado: referencia correcta a la app gestion
        on_delete=models.PROTECT,
        db_column='id_nota',
        blank=True,
        null=True
    )
    fecha_carga = models.DateTimeField(db_column='fecha_carga')
    monto_cargado = models.DecimalField(db_column='monto_cargado', max_digits=12, decimal_places=2)
    referencia = models.CharField(db_column='referencia', max_length=100, blank=True, null=True)

    # Campos adicionales para integración MetrePay
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='PENDIENTE',
        help_text='Estado de la transacción con MetrePay'
    )
    pay_request_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='ID de transacción de MetrePay'
    )
    tx_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='ID de transacción (txId) de MetrePay'
    )
    fecha_confirmacion = models.DateTimeField(
        blank=True,
        null=True,
        help_text='Fecha de confirmación del pago'
    )
    custom_identifier = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Identificador único para MetrePay'
    )

    class Meta(ManagedModel.Meta):
        db_table = 'cargas_saldo'
        verbose_name = 'Carga de Saldo'
        verbose_name_plural = 'Cargas de Saldo'

    def __str__(self):
        return f'Carga #{self.id_carga} - Tarjeta {self.nro_tarjeta}: Gs. {self.monto_cargado}'


class ConsumoTarjeta(ManagedModel):
    '''Tabla consumos_tarjeta - Historial de consumos con tarjeta'''
    id_consumo = models.BigAutoField(db_column='id_consumo', primary_key=True)
    nro_tarjeta = models.ForeignKey(
        Tarjeta,
        on_delete=models.PROTECT,
        db_column='nro_tarjeta',
        related_name='consumos'
    )
    fecha_consumo = models.DateTimeField(db_column='fecha_consumo')
    monto_consumido = models.DecimalField(
        db_column='monto_consumido', 
        max_digits=12, 
        decimal_places=2
    )
    detalle = models.CharField(db_column='detalle', max_length=200, blank=True, null=True)
    saldo_anterior = models.DecimalField(
        db_column='saldo_anterior', 
        max_digits=12, 
        decimal_places=2
    )
    saldo_posterior = models.DecimalField(
        db_column='saldo_posterior', 
        max_digits=12, 
        decimal_places=2
    )
    id_empleado_registro = models.ForeignKey(
        Empleado,
        on_delete=models.SET_NULL,
        db_column='id_empleado_registro',
        blank=True,
        null=True,
        related_name='consumos_registrados'
    )

    class Meta(ManagedModel.Meta):
        db_table = 'consumos_tarjeta'
        verbose_name = 'Consumo con Tarjeta'
        verbose_name_plural = 'Consumos con Tarjeta'
        ordering = ['-fecha_consumo']

    def __str__(self):
        return f'Consumo {self.nro_tarjeta} - Gs. {self.monto_consumido:,.0f}'