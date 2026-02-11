# gestion/models/promociones.py

from django.db import models
from .base import ManagedModel
from .productos import Producto
from .catalogos import Categoria
from pos.models import Venta as Ventas  # MIGRADO: Usar modelo de pos app

class Promocion(ManagedModel):
    '''Tabla promociones - Sistema de promociones y descuentos'''
    TIPO_CHOICES = [
        ('DESCUENTO_PORCENTAJE', 'Descuento Porcentaje'),
        ('DESCUENTO_MONTO', 'Descuento Monto Fijo'),
        ('PRECIO_FIJO', 'Precio Fijo'),
        ('NXM', 'N x M (ej: 2x1, 3x2)'),
        ('COMBO', 'Combo de Productos'),
    ]
    
    APLICA_CHOICES = [
        ('PRODUCTO', 'Producto Específico'),
        ('CATEGORIA', 'Categoría'),
        ('TOTAL_VENTA', 'Total de Venta'),
        ('ESTUDIANTE_GRADO', 'Grado de Estudiante'),
    ]
    
    id_promocion = models.AutoField(db_column='id_promocion', primary_key=True)
    nombre = models.CharField(db_column='nombre', max_length=200)
    descripcion = models.TextField(db_column='descripcion', blank=True, null=True)
    tipo_promocion = models.CharField(
        db_column='tipo_promocion',
        max_length=25,
        choices=TIPO_CHOICES
    )
    valor_descuento = models.DecimalField(
        db_column='valor_descuento',
        max_digits=10,
        decimal_places=2,
        help_text='Porcentaje (10.00 = 10%) o monto fijo (5000 = Gs. 5000)'
    )
    fecha_inicio = models.DateField(db_column='fecha_inicio')
    fecha_fin = models.DateField(db_column='fecha_fin', blank=True, null=True)
    hora_inicio = models.TimeField(db_column='hora_inicio', blank=True, null=True)
    hora_fin = models.TimeField(db_column='hora_fin', blank=True, null=True)
    dias_semana = models.JSONField(
        db_column='dias_semana',
        blank=True,
        null=True,
        help_text='Array de días [1=Lun, 2=Mar, 3=Mie, 4=Jue, 5=Vie, 6=Sab, 7=Dom]'
    )
    aplica_a = models.CharField(
        db_column='aplica_a',
        max_length=20,
        choices=APLICA_CHOICES
    )
    min_cantidad = models.IntegerField(
        db_column='min_cantidad',
        default=1,
        help_text='Cantidad mínima de productos para aplicar'
    )
    monto_minimo = models.DecimalField(
        db_column='monto_minimo',
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text='Monto mínimo de compra para aplicar'
    )
    max_usos_cliente = models.IntegerField(
        db_column='max_usos_cliente',
        blank=True,
        null=True,
        help_text='Máximo de usos por cliente/estudiante'
    )
    max_usos_total = models.IntegerField(
        db_column='max_usos_total',
        blank=True,
        null=True,
        help_text='Máximo de usos totales'
    )
    usos_actuales = models.IntegerField(db_column='usos_actuales', default=0)
    requiere_codigo = models.BooleanField(db_column='requiere_codigo', default=False)
    codigo_promocion = models.CharField(
        db_column='codigo_promocion',
        max_length=50,
        blank=True,
        null=True,
        unique=True
    )
    prioridad = models.IntegerField(
        db_column='prioridad',
        default=1,
        help_text='Orden de aplicación (1=Mayor prioridad)'
    )
    activo = models.BooleanField(db_column='activo', default=True)
    fecha_creacion = models.DateTimeField(db_column='fecha_creacion', auto_now_add=True)
    usuario_creacion = models.CharField(db_column='usuario_creacion', max_length=100, blank=True, null=True)
    
    class Meta(ManagedModel.Meta):
        db_table = 'promociones'
        verbose_name = 'Promoción'
        verbose_name_plural = 'Promociones'
        ordering = ['prioridad', '-fecha_inicio']
    
    def __str__(self):
        return f'{self.nombre} ({self.get_tipo_promocion_display()})'


class ProductoPromocion(ManagedModel):
    '''Tabla productos_promocion - Productos incluidos en promoción'''
    id_producto_promocion = models.AutoField(db_column='id_producto_promocion', primary_key=True)
    id_promocion = models.ForeignKey(
        Promocion,
        on_delete=models.CASCADE,
        db_column='id_promocion',
        related_name='productos_promocion'
    )
    id_producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        db_column='id_producto',
        related_name='promociones_producto'
    )
    
    class Meta(ManagedModel.Meta):
        db_table = 'productos_promocion'
        verbose_name = 'Producto en Promoción'
        verbose_name_plural = 'Productos en Promoción'
        unique_together = [['id_promocion', 'id_producto']]
    
    def __str__(self):
        return f'{self.id_promocion.nombre} - {self.id_producto.descripcion}'


class CategoriaPromocion(ManagedModel):
    '''Tabla categorias_promocion - Categorías incluidas en promoción'''
    id_categoria_promocion = models.AutoField(db_column='id_categoria_promocion', primary_key=True)
    id_promocion = models.ForeignKey(
        Promocion,
        on_delete=models.CASCADE,
        db_column='id_promocion',
        related_name='categorias_promocion'
    )
    id_categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        db_column='id_categoria',
        related_name='promociones_categoria'
    )
    
    class Meta(ManagedModel.Meta):
        db_table = 'categorias_promocion'
        verbose_name = 'Categoría en Promoción'
        verbose_name_plural = 'Categorías en Promoción'
        unique_together = [['id_promocion', 'id_categoria']]
    
    def __str__(self):
        return f'{self.id_promocion.nombre} - {self.id_categoria.nombre}'


class PromocionAplicada(ManagedModel):
    '''Tabla promociones_aplicadas - Registro de promociones aplicadas en ventas'''
    id_aplicacion = models.AutoField(db_column='id_aplicacion', primary_key=True)
    id_venta = models.ForeignKey(
        Ventas,
        on_delete=models.CASCADE,
        db_column='id_venta',
        related_name='promociones_aplicadas'
    )
    id_promocion = models.ForeignKey(
        Promocion,
        on_delete=models.PROTECT,
        db_column='id_promocion',
        related_name='aplicaciones'
    )
    monto_descontado = models.DecimalField(
        db_column='monto_descontado',
        max_digits=10,
        decimal_places=2
    )
    fecha_aplicacion = models.DateTimeField(db_column='fecha_aplicacion', auto_now_add=True)
    
    class Meta(ManagedModel.Meta):
        db_table = 'promociones_aplicadas'
        verbose_name = 'Promoción Aplicada'
        verbose_name_plural = 'Promociones Aplicadas'
    
    def __str__(self):
        return f'Venta #{self.id_venta.id_venta} - {self.id_promocion.nombre} (-Gs. {self.monto_descontado:,.0f})'