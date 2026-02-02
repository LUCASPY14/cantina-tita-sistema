# gestion/models/promociones.py

from django.db import models
from .base import ManagedModel
from .productos import Producto
from .catalogos import Categoria
from .ventas import Ventas

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
    
    id_promocion = models.AutoField(db_column='ID_Promocion', primary_key=True)
    nombre = models.CharField(db_column='Nombre', max_length=200)
    descripcion = models.TextField(db_column='Descripcion', blank=True, null=True)
    tipo_promocion = models.CharField(
        db_column='Tipo_Promocion',
        max_length=25,
        choices=TIPO_CHOICES
    )
    valor_descuento = models.DecimalField(
        db_column='Valor_Descuento',
        max_digits=10,
        decimal_places=2,
        help_text='Porcentaje (10.00 = 10%) o monto fijo (5000 = Gs. 5000)'
    )
    fecha_inicio = models.DateField(db_column='Fecha_Inicio')
    fecha_fin = models.DateField(db_column='Fecha_Fin', blank=True, null=True)
    hora_inicio = models.TimeField(db_column='Hora_Inicio', blank=True, null=True)
    hora_fin = models.TimeField(db_column='Hora_Fin', blank=True, null=True)
    dias_semana = models.JSONField(
        db_column='Dias_Semana',
        blank=True,
        null=True,
        help_text='Array de días [1=Lun, 2=Mar, 3=Mie, 4=Jue, 5=Vie, 6=Sab, 7=Dom]'
    )
    aplica_a = models.CharField(
        db_column='Aplica_A',
        max_length=20,
        choices=APLICA_CHOICES
    )
    min_cantidad = models.IntegerField(
        db_column='Min_Cantidad',
        default=1,
        help_text='Cantidad mínima de productos para aplicar'
    )
    monto_minimo = models.DecimalField(
        db_column='Monto_Minimo',
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text='Monto mínimo de compra para aplicar'
    )
    max_usos_cliente = models.IntegerField(
        db_column='Max_Usos_Cliente',
        blank=True,
        null=True,
        help_text='Máximo de usos por cliente/estudiante'
    )
    max_usos_total = models.IntegerField(
        db_column='Max_Usos_Total',
        blank=True,
        null=True,
        help_text='Máximo de usos totales'
    )
    usos_actuales = models.IntegerField(db_column='Usos_Actuales', default=0)
    requiere_codigo = models.BooleanField(db_column='Requiere_Codigo', default=False)
    codigo_promocion = models.CharField(
        db_column='Codigo_Promocion',
        max_length=50,
        blank=True,
        null=True,
        unique=True
    )
    prioridad = models.IntegerField(
        db_column='Prioridad',
        default=1,
        help_text='Orden de aplicación (1=Mayor prioridad)'
    )
    activo = models.BooleanField(db_column='Activo', default=True)
    fecha_creacion = models.DateTimeField(db_column='Fecha_Creacion', auto_now_add=True)
    usuario_creacion = models.CharField(db_column='Usuario_Creacion', max_length=100, blank=True, null=True)
    
    class Meta(ManagedModel.Meta):
        db_table = 'promociones'
        verbose_name = 'Promoción'
        verbose_name_plural = 'Promociones'
        ordering = ['prioridad', '-fecha_inicio']
    
    def __str__(self):
        return f'{self.nombre} ({self.get_tipo_promocion_display()})'


class ProductoPromocion(ManagedModel):
    '''Tabla productos_promocion - Productos incluidos en promoción'''
    id_producto_promocion = models.AutoField(db_column='ID_Producto_Promocion', primary_key=True)
    id_promocion = models.ForeignKey(
        Promocion,
        on_delete=models.CASCADE,
        db_column='ID_Promocion',
        related_name='productos_promocion'
    )
    id_producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        db_column='ID_Producto',
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
    id_categoria_promocion = models.AutoField(db_column='ID_Categoria_Promocion', primary_key=True)
    id_promocion = models.ForeignKey(
        Promocion,
        on_delete=models.CASCADE,
        db_column='ID_Promocion',
        related_name='categorias_promocion'
    )
    id_categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        db_column='ID_Categoria',
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
    id_aplicacion = models.AutoField(db_column='ID_Aplicacion', primary_key=True)
    id_venta = models.ForeignKey(
        Ventas,
        on_delete=models.CASCADE,
        db_column='ID_Venta',
        related_name='promociones_aplicadas'
    )
    id_promocion = models.ForeignKey(
        Promocion,
        on_delete=models.PROTECT,
        db_column='ID_Promocion',
        related_name='aplicaciones'
    )
    monto_descontado = models.DecimalField(
        db_column='Monto_Descontado',
        max_digits=10,
        decimal_places=2
    )
    fecha_aplicacion = models.DateTimeField(db_column='Fecha_Aplicacion', auto_now_add=True)
    
    class Meta(ManagedModel.Meta):
        db_table = 'promociones_aplicadas'
        verbose_name = 'Promoción Aplicada'
        verbose_name_plural = 'Promociones Aplicadas'
    
    def __str__(self):
        return f'Venta #{self.id_venta.id_venta} - {self.id_promocion.nombre} (-Gs. {self.monto_descontado:,.0f})'