"""
Modelos del Sistema POS (Punto de Venta)
Contiene: Ventas, DetalleVenta, PagoVenta
"""
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
import sys

# Importar modelos compartidos desde gestion
from gestion.models import (
    Cliente, Hijo, TiposPago, Empleado, Producto,
    MediosPago, CierresCaja, Tarjeta
)


class Venta(models.Model):
    '''
    Modelo principal de Ventas del sistema POS
    
    Tabla: ventas
    
    Tipos de Venta:
    - CONTADO: Pago inmediato completo
    - CREDITO: Pago diferido (requiere autorización)
    
    Estados de Pago:
    - PENDIENTE: Sin pagos aplicados
    - PARCIAL: Pagos parciales aplicados
    - PAGADA: Pago completo
    
    Estados:
    - PROCESADO: Venta válida
    - ANULADO: Venta cancelada
    '''
    
    TIPO_VENTA_CHOICES = [
        ('CONTADO', 'Contado'),
        ('CREDITO', 'Crédito'),
    ]
    
    ESTADO_PAGO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('PARCIAL', 'Parcial'),
        ('PAGADA', 'Pagada'),
    ]
    
    ESTADO_CHOICES = [
        ('PROCESADO', 'Procesado'),
        ('ANULADO', 'Anulado'),
    ]

    # Campos de identificación
    id_venta = models.BigAutoField(
        db_column='ID_Venta',
        primary_key=True,
        verbose_name='ID Venta'
    )
    nro_factura_venta = models.BigIntegerField(
        db_column='Nro_Factura_Venta',
        null=True,
        blank=True,
        verbose_name='Número de Factura'
    )
    
    # Relaciones con cliente
    id_cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        db_column='ID_Cliente',
        related_name='ventas_pos',  # Cambio para evitar conflicto
        verbose_name='Cliente'
    )
    id_hijo = models.ForeignKey(
        Hijo,
        on_delete=models.PROTECT,
        db_column='ID_Hijo',
        blank=True,
        null=True,
        verbose_name='Hijo'
    )
    
    # Información de pago
    id_tipo_pago = models.ForeignKey(
        TiposPago,
        on_delete=models.PROTECT,
        db_column='ID_Tipo_Pago',
        verbose_name='Tipo de Pago'
    )
    id_empleado_cajero = models.ForeignKey(
        Empleado,
        on_delete=models.PROTECT,
        db_column='ID_Empleado_Cajero',
        related_name='ventas_pos_como_cajero',  # Cambio para evitar conflicto
        verbose_name='Cajero'
    )
    
    # Fechas y montos
    fecha = models.DateTimeField(
        db_column='Fecha',
        default=timezone.now,
        verbose_name='Fecha'
    )
    monto_total = models.BigIntegerField(
        db_column='Monto_Total',
        verbose_name='Monto Total (Gs.)'
    )
    saldo_pendiente = models.BigIntegerField(
        db_column='Saldo_Pendiente',
        blank=True,
        null=True,
        verbose_name='Saldo Pendiente (Gs.)'
    )
    
    # Estados
    estado_pago = models.CharField(
        db_column='Estado_Pago',
        max_length=10,
        choices=ESTADO_PAGO_CHOICES,
        default='PENDIENTE',
        verbose_name='Estado de Pago'
    )
    estado = models.CharField(
        db_column='Estado',
        max_length=10,
        choices=ESTADO_CHOICES,
        default='PROCESADO',
        verbose_name='Estado'
    )
    tipo_venta = models.CharField(
        db_column='Tipo_Venta',
        max_length=20,
        choices=TIPO_VENTA_CHOICES,
        verbose_name='Tipo de Venta'
    )
    
    # Campos para ventas a crédito
    autorizado_por = models.ForeignKey(
        Empleado,
        on_delete=models.PROTECT,
        db_column='Autorizado_Por',
        related_name='ventas_pos_autorizadas',  # Cambio para evitar conflicto
        blank=True,
        null=True,
        verbose_name='Autorizado Por',
        help_text='Supervisor que autorizó la venta a crédito con saldo insuficiente'
    )
    motivo_credito = models.TextField(
        db_column='Motivo_Credito',
        blank=True,
        null=True,
        verbose_name='Motivo del Crédito',
        help_text='Justificación para la venta a crédito'
    )
    
    # Facturación legal
    genera_factura_legal = models.BooleanField(
        db_column='Genera_Factura_Legal',
        default=False,
        verbose_name='Genera Factura Legal',
        help_text='True si la venta genera factura contable (solo pagos con medios externos)'
    )

    class Meta:
        managed = False  # Gestion es el propietario de estas tablas
        db_table = 'ventas'
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['fecha']),
            models.Index(fields=['id_cliente']),
            models.Index(fields=['estado']),
            models.Index(fields=['estado_pago']),
        ]

    def __str__(self):
        return f'Venta #{self.id_venta} - {self.id_cliente.nombre_completo}: Gs. {self.monto_total:,}'
    
    def clean(self):
        """Validaciones de negocio para Ventas"""
        super().clean()
        
        # Validar que saldo_pendiente <= monto_total
        if self.saldo_pendiente and self.monto_total:
            if self.saldo_pendiente > self.monto_total:
                raise ValidationError({
                    'saldo_pendiente': 'El saldo pendiente no puede ser mayor al total de la venta'
                })
        
        # Validar consistencia estado_pago con saldo
        if self.estado_pago == 'PAGADA' and self.saldo_pendiente and self.saldo_pendiente > 0:
            raise ValidationError({
                'estado_pago': 'Una venta PAGADA no puede tener saldo pendiente mayor a 0'
            })
        
        if self.estado_pago == 'PENDIENTE':
            if self.saldo_pendiente is not None and self.monto_total:
                if self.saldo_pendiente != self.monto_total:
                    raise ValidationError({
                        'estado_pago': 'Una venta PENDIENTE debe tener saldo igual al total'
                    })
        
        # Validar autorización para ventas a crédito
        if self.tipo_venta == 'CREDITO' and not self.autorizado_por:
            raise ValidationError({
                'autorizado_por': 'Las ventas a crédito requieren autorización de un supervisor'
            })
    
    def save(self, *args, **kwargs):
        """Override save para ejecutar validaciones"""
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def total_pagado(self):
        """Calcula el monto total pagado"""
        if not self.saldo_pendiente:
            return self.monto_total
        return self.monto_total - self.saldo_pendiente
    
    @property
    def porcentaje_pagado(self):
        """Calcula el porcentaje pagado"""
        if not self.monto_total:
            return 0
        return (self.total_pagado / self.monto_total) * 100


class DetalleVenta(models.Model):
    '''
    Detalle de productos vendidos en cada venta
    
    Tabla: detalle_venta
    
    Almacena los productos individuales de cada venta con su cantidad,
    precio unitario al momento de la venta y subtotal.
    '''
    
    id_detalle = models.BigAutoField(
        db_column='ID_Detalle',
        primary_key=True,
        verbose_name='ID Detalle'
    )
    id_venta = models.ForeignKey(
        Venta,
        on_delete=models.CASCADE,
        db_column='ID_Venta',
        related_name='detalles',
        verbose_name='Venta'
    )
    id_producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        db_column='ID_Producto',
        related_name='detalles_venta_pos',  # Cambio para evitar conflicto
        verbose_name='Producto'
    )
    cantidad = models.DecimalField(
        db_column='Cantidad',
        max_digits=10,
        decimal_places=3,
        verbose_name='Cantidad'
    )
    precio_unitario = models.BigIntegerField(
        db_column='Precio_Unitario',
        verbose_name='Precio Unitario (Gs.)'
    )
    subtotal_total = models.BigIntegerField(
        db_column='Subtotal_Total',
        verbose_name='Subtotal (Gs.)'
    )

    class Meta:
        managed = False  # Gestion es el propietario de estas tablas
        db_table = 'detalle_venta'
        verbose_name = 'Detalle de Venta'
        verbose_name_plural = 'Detalles de Venta'
        unique_together = (('id_venta', 'id_producto'),)
        indexes = [
            models.Index(fields=['id_venta']),
            models.Index(fields=['id_producto']),
        ]

    def __str__(self):
        return f'{self.id_producto.descripcion} x {self.cantidad} = Gs. {self.subtotal_total:,}'
    
    def clean(self):
        """Validaciones de negocio"""
        super().clean()
        
        # Validar cantidad positiva
        if self.cantidad and self.cantidad <= 0:
            raise ValidationError({
                'cantidad': 'La cantidad debe ser mayor a 0'
            })
        
        # Validar precio positivo
        if self.precio_unitario and self.precio_unitario <= 0:
            raise ValidationError({
                'precio_unitario': 'El precio unitario debe ser mayor a 0'
            })
        
        # Validar cálculo de subtotal
        if self.cantidad and self.precio_unitario:
            subtotal_calculado = int(float(self.cantidad) * self.precio_unitario)
            if self.subtotal_total and self.subtotal_total != subtotal_calculado:
                raise ValidationError({
                    'subtotal_total': f'El subtotal no coincide con cantidad x precio. Esperado: {subtotal_calculado}'
                })
    
    def save(self, *args, **kwargs):
        """Override save para calcular subtotal automáticamente"""
        if self.cantidad and self.precio_unitario and not self.subtotal_total:
            self.subtotal_total = int(float(self.cantidad) * self.precio_unitario)
        self.full_clean()
        super().save(*args, **kwargs)


class PagoVenta(models.Model):
    '''
    Pagos aplicados a ventas
    
    Tabla: pagos_venta
    
    Registra cada pago realizado para saldar una venta.
    Una venta puede tener múltiples pagos (pago parcial).
    '''
    
    ESTADO_CHOICES = [
        ('PROCESADO', 'Procesado'),
        ('ANULADO', 'Anulado'),
    ]
    
    id_pago_venta = models.BigAutoField(
        db_column='ID_Pago_Venta',
        primary_key=True,
        verbose_name='ID Pago'
    )
    id_venta = models.ForeignKey(
        Venta,
        on_delete=models.CASCADE,
        db_column='ID_Venta',
        related_name='pagos',
        verbose_name='Venta'
    )
    id_medio_pago = models.ForeignKey(
        MediosPago,
        on_delete=models.PROTECT,
        db_column='ID_Medio_Pago',
        verbose_name='Medio de Pago'
    )
    id_cierre = models.ForeignKey(
        CierresCaja,
        on_delete=models.PROTECT,
        db_column='ID_Cierre',
        blank=True,
        null=True,
        verbose_name='Cierre de Caja'
    )
    nro_tarjeta_usada = models.ForeignKey(
        Tarjeta,
        on_delete=models.PROTECT,
        db_column='Nro_Tarjeta_Usada',
        blank=True,
        null=True,
        verbose_name='Tarjeta Utilizada'
    )
    monto_aplicado = models.BigIntegerField(
        db_column='Monto_Aplicado',
        verbose_name='Monto Aplicado (Gs.)'
    )
    referencia_transaccion = models.CharField(
        db_column='Referencia_Transaccion',
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Referencia de Transacción'
    )
    fecha_pago = models.DateTimeField(
        db_column='Fecha_Pago',
        default=timezone.now,
        verbose_name='Fecha de Pago'
    )
    estado = models.CharField(
        db_column='Estado',
        max_length=10,
        choices=ESTADO_CHOICES,
        default='PROCESADO',
        verbose_name='Estado'
    )

    class Meta:
        managed = False  # Gestion es el propietario de estas tablas
        db_table = 'pagos_venta'
        verbose_name = 'Pago de Venta'
        verbose_name_plural = 'Pagos de Venta'
        ordering = ['-fecha_pago']
        indexes = [
            models.Index(fields=['id_venta']),
            models.Index(fields=['fecha_pago']),
            models.Index(fields=['estado']),
        ]

    def __str__(self):
        return f'Pago {self.id_pago_venta} - Venta #{self.id_venta.id_venta}: Gs. {self.monto_aplicado:,}'
    
    def clean(self):
        """Validaciones de negocio"""
        super().clean()
        
        # Validar monto positivo
        if self.monto_aplicado and self.monto_aplicado <= 0:
            raise ValidationError({
                'monto_aplicado': 'El monto debe ser mayor a 0'
            })
        
        # Validar que el pago no exceda el saldo pendiente
        if self.id_venta and self.monto_aplicado:
            saldo = self.id_venta.saldo_pendiente or 0
            if self.monto_aplicado > saldo:
                raise ValidationError({
                    'monto_aplicado': f'El monto ({self.monto_aplicado:,}) no puede exceder el saldo pendiente ({saldo:,})'
                })
    
    def save(self, *args, **kwargs):
        """Override save para ejecutar validaciones"""
        self.full_clean()
        super().save(*args, **kwargs)
