# gestion/models/ventas.py

from django.db import models
from django.core.exceptions import ValidationError
from .base import ManagedModel
from .clientes import Cliente, Hijo
from .empleados import Empleado
from .catalogos import TiposPago, MediosPago, TarifasComision
from .fiscal import CierresCaja
from .productos import Producto
# REMOVIDO: from .tarjetas import Tarjeta, CargasSaldo  # Causa ciclo


class Ventas(ManagedModel):
    '''Tabla ventas - Ventas realizadas'''
    TIPO_VENTA_CHOICES = [
        ('CONTADO', 'Contado'),
        ('CREDITO', 'Crédito'),
    ]

    id_venta = models.BigAutoField(db_column='ID_Venta', primary_key=True)
    nro_factura_venta = models.BigIntegerField(db_column='Nro_Factura_Venta', null=True, blank=True)
    id_cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        db_column='ID_Cliente',
        related_name='ventas'
    )
    id_hijo = models.ForeignKey(
        Hijo,
        on_delete=models.PROTECT,
        db_column='ID_Hijo',
        blank=True,
        null=True
    )
    id_tipo_pago = models.ForeignKey(
        TiposPago,
        on_delete=models.PROTECT,
        db_column='ID_Tipo_Pago'
    )
    id_empleado_cajero = models.ForeignKey(
        Empleado,
        on_delete=models.PROTECT,
        db_column='ID_Empleado_Cajero'
    )
    fecha = models.DateTimeField(db_column='Fecha')
    monto_total = models.BigIntegerField(db_column='Monto_Total')
    saldo_pendiente = models.BigIntegerField(db_column='Saldo_Pendiente', blank=True, null=True)
    estado_pago = models.CharField(
        db_column='Estado_Pago',
        max_length=10,
        choices=[('PENDIENTE', 'Pendiente'), ('PARCIAL', 'Parcial'), ('PAGADA', 'Pagada')],
        default='PENDIENTE'
    )
    estado = models.CharField(
        db_column='Estado',
        max_length=10,
        choices=[('PROCESADO', 'Procesado'), ('ANULADO', 'Anulado')],
        default='PROCESADO'
    )
    tipo_venta = models.CharField(db_column='Tipo_Venta', max_length=20, choices=TIPO_VENTA_CHOICES)
    autorizado_por = models.ForeignKey(
        Empleado,
        on_delete=models.PROTECT,
        db_column='Autorizado_Por',
        related_name='ventas_autorizadas',
        blank=True,
        null=True,
        help_text='Supervisor que autorizó la venta (para ventas a crédito con saldo insuficiente)'
    )
    motivo_credito = models.TextField(
        db_column='Motivo_Credito',
        blank=True,
        null=True,
        help_text='Justificación de la venta a crédito'
    )
    genera_factura_legal = models.BooleanField(
        db_column='Genera_Factura_Legal',
        default=False,
        help_text='True si la venta genera factura contable (solo pagos con medios externos)'
    )

    class Meta(ManagedModel.Meta):
        db_table = 'ventas'
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'

    def __str__(self):
        return f'Venta #{self.id_venta} - {self.id_cliente.nombre_completo}: Gs. {self.monto_total}'

    def clean(self):
        """Validaciones de negocio para Ventas"""
        
        if self.saldo_pendiente and self.monto_total:
            if self.saldo_pendiente > self.monto_total:
                raise ValidationError({
                    'saldo_pendiente': 'El saldo pendiente no puede ser mayor al total de la venta'
                })
        
        if self.estado_pago == 'PAGADA' and self.saldo_pendiente and self.saldo_pendiente > 0:
            raise ValidationError({
                'estado_pago': 'Una venta PAGADA no puede tener saldo pendiente mayor a 0'
            })
        
        if self.estado_pago == 'PENDIENTE' and self.saldo_pendiente != self.monto_total:
            raise ValidationError({
                'estado_pago': 'Una venta PENDIENTE debe tener saldo igual al total'
            })


class DetalleVenta(ManagedModel):
    '''Tabla detalle_venta - Detalle de productos vendidos'''
    id_detalle = models.BigAutoField(db_column='ID_Detalle', primary_key=True)
    id_venta = models.ForeignKey(
        Ventas,
        on_delete=models.CASCADE,
        db_column='ID_Venta',
        related_name='detalles'
    )
    id_producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        db_column='ID_Producto'
    )
    cantidad = models.DecimalField(db_column='Cantidad', max_digits=10, decimal_places=3)
    precio_unitario = models.BigIntegerField(db_column='Precio_Unitario')
    subtotal_total = models.BigIntegerField(db_column='Subtotal_Total')

    class Meta(ManagedModel.Meta):
        db_table = 'detalle_venta'
        verbose_name = 'Detalle de Venta'
        verbose_name_plural = 'Detalles de Venta'
        unique_together = (('id_venta', 'id_producto'),)

    def __str__(self):
        return f'{self.id_producto.descripcion} x {self.cantidad}'


class PagosVenta(ManagedModel):
    '''Tabla pagos_venta - Pagos aplicados a ventas'''
    id_pago_venta = models.BigAutoField(db_column='ID_Pago_Venta', primary_key=True)
    id_venta = models.ForeignKey(
        Ventas,
        on_delete=models.CASCADE,
        db_column='ID_Venta',
        related_name='pagos'
    )
    id_medio_pago = models.ForeignKey(
        MediosPago,
        on_delete=models.PROTECT,
        db_column='ID_Medio_Pago'
    )
    id_cierre = models.ForeignKey(
        CierresCaja,
        on_delete=models.PROTECT,
        db_column='ID_Cierre',
        blank=True,
        null=True
    )
    nro_tarjeta_usada = models.ForeignKey(
            'gestion.Tarjeta',  # Confirmado: referencia correcta a la app gestion
        on_delete=models.PROTECT,
        db_column='Nro_Tarjeta_Usada',
        blank=True,
        null=True
    )
    monto_aplicado = models.BigIntegerField(db_column='Monto_Aplicado')
    referencia_transaccion = models.CharField(db_column='Referencia_Transaccion', max_length=100, blank=True, null=True)
    fecha_pago = models.DateTimeField(db_column='Fecha_Pago', blank=True, null=True)
    estado = models.CharField(
        db_column='Estado',
        max_length=10,
        choices=[('PROCESADO', 'Procesado'), ('ANULADO', 'Anulado')],
        default='PROCESADO'
    )

    class Meta(ManagedModel.Meta):
        db_table = 'pagos_venta'
        verbose_name = 'Pago de Venta'
        verbose_name_plural = 'Pagos de Venta'

    def __str__(self):
        return f'Pago {self.id_pago_venta} - Venta {self.id_venta_id}: Gs. {self.monto_aplicado}'


class AplicacionPagosVentas(ManagedModel):
    '''Tabla aplicacion_pagos_ventas - Aplicación de pagos a ventas'''
    id_aplicacion = models.BigAutoField(db_column='ID_Aplicacion', primary_key=True)
    id_pago_venta = models.ForeignKey(
        PagosVenta,
        on_delete=models.CASCADE,
        db_column='ID_Pago_Venta'
    )
    id_venta = models.ForeignKey(
        Ventas,
        on_delete=models.CASCADE,
        db_column='ID_Venta'
    )
    monto_aplicado = models.BigIntegerField(db_column='Monto_Aplicado')

    class Meta(ManagedModel.Meta):
        db_table = 'aplicacion_pagos_ventas'
        verbose_name = 'Aplicación de Pago a Venta'
        verbose_name_plural = 'Aplicaciones de Pagos a Ventas'

    def __str__(self):
        return f'Aplicación {self.id_aplicacion} - Pago {self.id_pago_venta_id} a Venta {self.id_venta_id}'


class DetalleComisionVenta(ManagedModel):
    '''Tabla detalle_comision_venta - Comisiones por medio de pago'''
    id_detalle_comision = models.BigAutoField(db_column='ID_Detalle_Comision', primary_key=True)
    id_pago_venta = models.ForeignKey(
        PagosVenta,
        on_delete=models.CASCADE,
        db_column='ID_Pago_Venta',
        related_name='comisiones'
    )
    id_tarifa = models.ForeignKey(
        TarifasComision,
        on_delete=models.PROTECT,
        db_column='ID_Tarifa'
    )
    monto_comision_calculada = models.DecimalField(db_column='Monto_Comision_Calculada', max_digits=10, decimal_places=2)
    porcentaje_aplicado = models.DecimalField(db_column='Porcentaje_Aplicado', max_digits=5, decimal_places=4)

    class Meta(ManagedModel.Meta):
        db_table = 'detalle_comision_venta'
        verbose_name = 'Detalle de Comisión'
        verbose_name_plural = 'Detalles de Comisión'

    def __str__(self):
        return f'Comisión Pago {self.id_pago_venta_id}: Gs. {self.monto_comision_calculada}'


class NotasCreditoCliente(ManagedModel):
    '''Tabla notas_credito_cliente - Notas de crédito emitidas'''
    ESTADO_CHOICES = [
        ('Emitida', 'Emitida'),
        ('Aplicada', 'Aplicada'),
        ('Anulada', 'Anulada'),
    ]

    id_nota = models.BigAutoField(db_column='ID_Nota', primary_key=True)
    nro_factura_venta = models.BigIntegerField(db_column='Nro_Factura_Venta')
    id_cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        db_column='ID_Cliente',
        related_name='notas_credito'
    )
    id_venta_original = models.ForeignKey(
        Ventas,
        on_delete=models.SET_NULL,
        db_column='ID_Venta_Original',
        blank=True,
        null=True
    )
    fecha = models.DateTimeField(db_column='Fecha')
    monto_total = models.DecimalField(db_column='Monto_Total', max_digits=12, decimal_places=2)
    observacion = models.CharField(db_column='Observacion', max_length=255, blank=True, null=True)
    estado = models.CharField(db_column='Estado', max_length=8, choices=ESTADO_CHOICES, blank=True, null=True)

    class Meta(ManagedModel.Meta):
        db_table = 'notas_credito_cliente'
        verbose_name = 'Nota de Crédito Cliente'
        verbose_name_plural = 'Notas de Crédito Cliente'

    def __str__(self):
        return f'NC #{self.id_nota} - {self.id_cliente.nombre_completo}: Gs. {self.monto_total}'


class DetalleNota(ManagedModel):
    '''Tabla detalle_nota - Detalle de notas de crédito'''
    id_detalle = models.BigAutoField(db_column='ID_Detalle', primary_key=True)
    id_nota = models.ForeignKey(
        NotasCreditoCliente,
        on_delete=models.CASCADE,
        db_column='ID_Nota',
        related_name='detalles'
    )
    id_producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        db_column='ID_Producto'
    )
    cantidad = models.DecimalField(db_column='Cantidad', max_digits=8, decimal_places=3)
    precio_unitario = models.DecimalField(db_column='Precio_Unitario', max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(db_column='Subtotal', max_digits=12, decimal_places=2)

    class Meta(ManagedModel.Meta):
        db_table = 'detalle_nota'
        verbose_name = 'Detalle de Nota de Crédito'
        verbose_name_plural = 'Detalles de Notas de Crédito'
        unique_together = (('id_nota', 'id_producto'),)

    def __str__(self):
        return f'{self.id_producto.descripcion} x {self.cantidad}'


class AutorizacionSaldoNegativo(ManagedModel):
    """Registro de autorizaciones de ventas con saldo negativo"""
    id_autorizacion = models.BigAutoField(db_column='id_autorizacion', primary_key=True)
    id_venta = models.ForeignKey(
        Ventas,
        on_delete=models.RESTRICT,
        db_column='id_venta',
        related_name='autorizaciones_saldo'
    )
    nro_tarjeta = models.ForeignKey(
            'gestion.Tarjeta',  # Confirmado: referencia correcta a la app gestion
        on_delete=models.CASCADE,
        db_column='nro_tarjeta',
        related_name='autorizaciones'
    )
    id_empleado_autoriza = models.ForeignKey(
        Empleado,
        on_delete=models.RESTRICT,
        db_column='id_empleado_autoriza',
        related_name='autorizaciones_realizadas'
    )
    saldo_anterior = models.BigIntegerField(db_column='saldo_anterior', help_text='Saldo antes de la venta')
    monto_venta = models.BigIntegerField(db_column='monto_venta', help_text='Monto de la venta')
    saldo_resultante = models.BigIntegerField(db_column='saldo_resultante', help_text='Saldo después de la venta (negativo)')
    motivo = models.CharField(db_column='motivo', max_length=255, help_text='Justificación de la autorización')
    fecha_autorizacion = models.DateTimeField(db_column='fecha_autorizacion', auto_now_add=True)
    fecha_regularizacion = models.DateTimeField(db_column='fecha_regularizacion', blank=True, null=True)
    id_carga_regularizacion = models.ForeignKey(
            'gestion.CargasSaldo',  # Confirmado: referencia correcta a la app gestion
        on_delete=models.SET_NULL,
        db_column='id_carga_regularizacion',
        related_name='regularizaciones',
        blank=True,
        null=True
    )
    regularizado = models.BooleanField(db_column='regularizado', default=False)
    
    class Meta(ManagedModel.Meta):
        db_table = 'autorizacion_saldo_negativo'
        verbose_name = 'Autorización de Saldo Negativo'
        verbose_name_plural = 'Autorizaciones de Saldo Negativo'
        indexes = [
            models.Index(fields=['nro_tarjeta', 'fecha_autorizacion'], name='idx_tarjeta_fecha_auth'),
            models.Index(fields=['regularizado'], name='idx_regularizado'),
            models.Index(fields=['id_empleado_autoriza'], name='idx_empleado_auth'),
        ]
    
    def __str__(self):
        return f'Autorización #{self.id_autorizacion} - {self.nro_tarjeta} - Gs. {self.saldo_resultante:,}'