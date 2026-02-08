# gestion/models/compras.py

from django.db import models
from .base import ManagedModel
from .empleados import Empleado
from .catalogos import MediosPago
from .productos import Producto  # CAMBIADO: Importación directa
# REMOVIDO: from .ventas import PagosVenta  # Para evitar ciclos de importación


class Proveedor(ManagedModel):
    '''Tabla proveedores'''
    id_proveedor = models.AutoField(db_column='ID_Proveedor', primary_key=True)
    ruc = models.CharField(db_column='RUC', max_length=20, unique=True)
    razon_social = models.CharField(db_column='Razon_Social', max_length=255)
    telefono = models.CharField(db_column='Telefono', max_length=20, blank=True, null=True)
    email = models.EmailField(db_column='Email', blank=True, null=True)
    direccion = models.CharField(db_column='Direccion', max_length=255, blank=True, null=True)
    ciudad = models.CharField(db_column='Ciudad', max_length=100, blank=True, null=True)
    activo = models.BooleanField(db_column='Activo', default=True)
    fecha_registro = models.DateTimeField(db_column='Fecha_Registro', auto_now_add=True)

    class Meta(ManagedModel.Meta):
        db_table = 'proveedores'
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'

    def __str__(self):
        return self.razon_social


class Compras(ManagedModel):
    '''Tabla compras - Compras a proveedores'''
    id_compra = models.BigAutoField(db_column='ID_Compra', primary_key=True)
    id_proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.PROTECT,
        db_column='ID_Proveedor',
        related_name='compras'
    )
    fecha = models.DateTimeField(db_column='Fecha')
    monto_total = models.DecimalField(db_column='Monto_Total', max_digits=12, decimal_places=2)
    saldo_pendiente = models.DecimalField(db_column='Saldo_Pendiente', max_digits=12, decimal_places=2, blank=True, null=True)
    estado_pago = models.CharField(
        db_column='Estado_Pago',
        max_length=10,
        choices=[('PENDIENTE', 'Pendiente'), ('PARCIAL', 'Parcial'), ('PAGADA', 'Pagada')],
        default='PENDIENTE'
    )
    nro_factura = models.CharField(db_column='Nro_Factura', max_length=50, blank=True, null=True)
    observaciones = models.TextField(db_column='Observaciones', blank=True, null=True)

    class Meta(ManagedModel.Meta):
        db_table = 'compras'
        verbose_name = 'Compra'
        verbose_name_plural = 'Compras'

    def __str__(self):
        return f'Compra #{self.id_compra} - {self.id_proveedor.razon_social}'


class DetalleCompra(ManagedModel):
    '''Tabla detalle_compra - Detalle de productos comprados'''
    id_detalle = models.BigAutoField(db_column='ID_Detalle', primary_key=True)
    id_compra = models.ForeignKey(
        Compras,
        on_delete=models.CASCADE,
        db_column='ID_Compra',
        related_name='detalles'
    )
    id_producto = models.ForeignKey(
        Producto,  # CAMBIADO: de 'productos.Producto' a Producto (importado)
        on_delete=models.PROTECT,
        db_column='ID_Producto'
    )
    costo_unitario_neto = models.DecimalField(db_column='Costo_Unitario_Neto', max_digits=10, decimal_places=2)
    cantidad = models.DecimalField(db_column='Cantidad', max_digits=8, decimal_places=3)
    subtotal_neto = models.DecimalField(db_column='Subtotal_Neto', max_digits=12, decimal_places=2)
    monto_iva = models.DecimalField(db_column='Monto_IVA', max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta(ManagedModel.Meta):
        db_table = 'detalle_compra'
        verbose_name = 'Detalle de Compra'
        verbose_name_plural = 'Detalles de Compra'
        unique_together = (('id_compra', 'id_producto'),)

    def __str__(self):
        return f'{self.id_producto.descripcion} x {self.cantidad}'


class PagosProveedores(ManagedModel):
    '''Tabla pagos_proveedores - Pagos realizados a proveedores'''
    id_pago_proveedor = models.BigAutoField(db_column='ID_Pago_Proveedor', primary_key=True)
    id_compra = models.ForeignKey(
        Compras,
        on_delete=models.PROTECT,
        db_column='ID_Compra',
        related_name='pagos'
    )
    monto_aplicado = models.DecimalField(db_column='Monto_Aplicado', max_digits=12, decimal_places=2)
    fecha_pago = models.DateTimeField(db_column='Fecha_Pago')
    id_medio_pago = models.ForeignKey(
        MediosPago,
        on_delete=models.PROTECT,
        db_column='ID_Medio_Pago'
    )
    referencia_transaccion = models.CharField(db_column='Referencia_Transaccion', max_length=100, blank=True, null=True)
    estado = models.CharField(
        db_column='Estado',
        max_length=10,
        choices=[('PROCESADO', 'Procesado'), ('ANULADO', 'Anulado')],
        default='PROCESADO'
    )
    observaciones = models.TextField(db_column='Observaciones', blank=True, null=True)
    fecha_creacion = models.DateTimeField(db_column='Fecha_Creacion', auto_now_add=True)

    class Meta(ManagedModel.Meta):
        db_table = 'pagos_proveedores'
        verbose_name = 'Pago a Proveedor'
        verbose_name_plural = 'Pagos a Proveedores'

    def __str__(self):
        return f'Pago #{self.id_pago_proveedor} - Compra {self.id_compra_id}: Gs. {self.monto_aplicado}'


class AplicacionPagosCompras(ManagedModel):
    '''Tabla aplicacion_pagos_compras - Aplicación de pagos a compras'''
    id_aplicacion = models.BigAutoField(db_column='ID_Aplicacion', primary_key=True)
    id_pago_proveedor = models.ForeignKey(
        PagosProveedores,
        on_delete=models.CASCADE,
        db_column='ID_Pago_Proveedor'
    )
    id_compra = models.ForeignKey(
        Compras,
        on_delete=models.CASCADE,
        db_column='ID_Compra'
    )
    monto_aplicado = models.DecimalField(db_column='Monto_Aplicado', max_digits=12, decimal_places=2)

    class Meta(ManagedModel.Meta):
        db_table = 'aplicacion_pagos_compras'
        verbose_name = 'Aplicación de Pago a Compra'
        verbose_name_plural = 'Aplicaciones de Pagos a Compras'

    def __str__(self):
        return f'Aplicación {self.id_aplicacion} - Pago {self.id_pago_proveedor_id} a Compra {self.id_compra_id}'


class NotasCreditoProveedor(ManagedModel):
    '''Tabla notas_credito_proveedor - Notas de crédito de proveedores'''
    ESTADO_CHOICES = [
        ('EMITIDA', 'Emitida'),
        ('APLICADA', 'Aplicada'),
        ('ANULADA', 'Anulada'),
    ]

    id_nota_proveedor = models.BigAutoField(db_column='ID_Nota_Proveedor', primary_key=True)
    nro_factura_compra = models.BigIntegerField(db_column='Nro_Factura_Compra', blank=True, null=True)
    id_proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.PROTECT,
        db_column='ID_Proveedor',
        related_name='notas_credito'
    )
    id_compra_original = models.ForeignKey(
        Compras,
        on_delete=models.SET_NULL,
        db_column='ID_Compra_Original',
        blank=True,
        null=True
    )
    fecha = models.DateTimeField(db_column='Fecha')
    monto_total = models.DecimalField(db_column='Monto_Total', max_digits=12, decimal_places=2)
    observacion = models.CharField(db_column='Observacion', max_length=255, blank=True, null=True)
    estado = models.CharField(db_column='Estado', max_length=10, choices=ESTADO_CHOICES, default='EMITIDA')
    fecha_creacion = models.DateTimeField(db_column='Fecha_Creacion', auto_now_add=True)

    class Meta(ManagedModel.Meta):
        db_table = 'notas_credito_proveedor'
        verbose_name = 'Nota de Crédito Proveedor'
        verbose_name_plural = 'Notas de Crédito Proveedores'

    def __str__(self):
        return f'NC Proveedor #{self.id_nota_proveedor} - {self.id_proveedor.razon_social}: Gs. {self.monto_total}'


class DetalleNotaCreditoProveedor(ManagedModel):
    '''Tabla detalle_nota_credito_proveedor - Detalle de notas de crédito a proveedores'''
    id_detalle_nc_proveedor = models.BigAutoField(db_column='ID_Detalle_NC_Proveedor', primary_key=True)
    id_nota_proveedor = models.ForeignKey(
        NotasCreditoProveedor,
        on_delete=models.CASCADE,
        db_column='ID_Nota_Proveedor',
        related_name='detalles'
    )
    id_producto = models.ForeignKey(
        Producto,  # CAMBIADO: de 'productos.Producto' a Producto (importado)
        on_delete=models.PROTECT,
        db_column='ID_Producto'
    )
    cantidad = models.DecimalField(db_column='Cantidad', max_digits=10, decimal_places=3)
    precio_unitario = models.DecimalField(db_column='Precio_Unitario', max_digits=12, decimal_places=2)
    subtotal = models.DecimalField(db_column='Subtotal', max_digits=12, decimal_places=2)

    class Meta(ManagedModel.Meta):
        db_table = 'detalle_nota_credito_proveedor'
        verbose_name = 'Detalle NC Proveedor'
        verbose_name_plural = 'Detalles NC Proveedores'

    def __str__(self):
        return f'{self.id_producto.descripcion} x {self.cantidad}'


class ConciliacionPagos(ManagedModel):
    '''Tabla conciliacion_pagos - Conciliación de pagos con entidades'''
    id_conciliacion = models.BigAutoField(db_column='ID_Conciliacion', primary_key=True)
    id_pago_venta = models.OneToOneField(
            'pos.PagoVenta',  # ACTUALIZADO: referencia al modelo migrado en pos app
        on_delete=models.CASCADE,
        db_column='ID_Pago_Venta'
    )
    fecha_acreditacion = models.DateTimeField(db_column='Fecha_Acreditacion', blank=True, null=True)
    fecha_conciliacion = models.DateTimeField(db_column='Fecha_Conciliacion')
    estado = models.CharField(
        db_column='Estado', 
        max_length=20, 
        choices=[
            ('PENDIENTE', 'Pendiente'),
            ('ACREDITADO', 'Acreditado'),
            ('RECHAZADO', 'Rechazado'),
            ('CONCILIADO', 'Conciliado')
        ],
        default='PENDIENTE'
    )
    monto_acreditado = models.DecimalField(db_column='Monto_Acreditado', max_digits=12, decimal_places=2, blank=True, null=True)
    observaciones = models.TextField(db_column='Observaciones', blank=True, null=True)
    fecha_creacion = models.DateTimeField(db_column='Fecha_Creacion', auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(db_column='Fecha_Actualizacion', auto_now=True)

    class Meta(ManagedModel.Meta):
        db_table = 'conciliacion_pagos'
        verbose_name = 'Conciliación de Pago'
        verbose_name_plural = 'Conciliaciones de Pagos'
        ordering = ['-fecha_conciliacion']

    def __str__(self):
        return f'Conciliación {self.id_conciliacion} - Pago Venta {self.id_pago_venta_id}'