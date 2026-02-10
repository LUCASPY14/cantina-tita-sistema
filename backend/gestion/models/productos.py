# gestion/models/productos.py

from django.db import models
from .base import ManagedModel
from .catalogos import Categoria, UnidadMedida, Impuesto, ListaPrecios
from .empleados import Empleado


class Producto(ManagedModel):
    '''Tabla productos - Productos existentes en la BD'''
    id_producto = models.AutoField(db_column='id_producto', primary_key=True)
    id_categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        db_column='id_categoria',
        related_name='productos'
    )
    id_unidad_medida = models.ForeignKey(
        UnidadMedida,
        on_delete=models.SET_NULL,  # Cambiado a SET_NULL porque en MySQL dice YES (permite NULL)
        db_column='id_unidad_de_medida',  # Nombre exacto de la columna
        blank=True,
        null=True
    )
    id_impuesto = models.ForeignKey(
        Impuesto,
        on_delete=models.PROTECT,
        db_column='id_impuesto'
    )
    codigo_barra = models.CharField(
        db_column='codigo_barra',
        max_length=50,
        unique=True,
        blank=True,
        null=True  # En MySQL dice YES (permite NULL)
    )
    descripcion = models.CharField(db_column='descripcion', max_length=255)
    stock_minimo = models.DecimalField(
        db_column='stock_minimo',
        max_digits=10,
        decimal_places=3,
        default=0
    )
    permite_stock_negativo = models.BooleanField(
        db_column='permite_stock_negativo',
        default=False
    )
    activo = models.BooleanField(db_column='activo', default=True)

    class Meta(ManagedModel.Meta):
        db_table = 'productos'
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        indexes = [
            models.Index(fields=['descripcion']),  # En MySQL dice MUL (índice múltiple)
        ]

    def __str__(self):
        return self.descripcion


class StockUnico(ManagedModel):
    '''Tabla stock_unico - Stock de productos'''
    id_stock_unico = models.AutoField(db_column='id_stock_unico', primary_key=True)
    id_producto = models.OneToOneField(
        Producto,
        on_delete=models.CASCADE,
        db_column='id_producto',
        related_name='stock'
    )
    cantidad = models.DecimalField(db_column='cantidad', max_digits=10, decimal_places=3, default=0)
    fecha_ultima_actualizacion = models.DateTimeField(db_column='fecha_ultima_actualizacion', auto_now=True)

    class Meta(ManagedModel.Meta):
        db_table = 'stock_unico'
        verbose_name = 'Stock'
        verbose_name_plural = 'Stocks'

    def __str__(self):
        return f'{self.id_producto.descripcion}: {self.cantidad}'


class PreciosPorLista(ManagedModel):
    '''Tabla precios_por_lista - Precios de productos por lista'''
    id_precio = models.AutoField(db_column='id_precio', primary_key=True)
    id_producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        db_column='id_producto',
        related_name='precios_lista'
    )
    id_lista_precios = models.ForeignKey(
        ListaPrecios,
        on_delete=models.CASCADE,
        db_column='id_lista',
        related_name='precios_productos'
    )
    precio_venta = models.DecimalField(db_column='precio_unitario_neto', max_digits=20, decimal_places=0)
    fecha_vigencia = models.DateTimeField(db_column='fecha_vigencia')

    class Meta(ManagedModel.Meta):
        db_table = 'precios_por_lista'
        verbose_name = 'Precio por Lista'
        verbose_name_plural = 'Precios por Lista'
        unique_together = ['id_producto', 'id_lista_precios']

    def __str__(self):
        return f'{self.id_producto.descripcion} - {self.id_lista_precios.nombre}: {self.precio_venta}'


class CostosHistoricos(ManagedModel):
    '''Tabla costos_historicos - Historial de costos de productos'''
    id_costo_historico = models.BigAutoField(db_column='id_costo_historico', primary_key=True)
    id_producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        db_column='id_producto',
        related_name='costos_historicos'
    )
    id_compra = models.ForeignKey(
        'gestion.Compras',  # CAMBIADO: referencia correcta a la app gestion
        on_delete=models.SET_NULL,
        db_column='id_compra',
        blank=True,
        null=True
    )
    costo_unitario_neto = models.DecimalField(db_column='costo_unitario_neto', max_digits=10, decimal_places=2)
    fecha_compra = models.DateTimeField(db_column='fecha_compra')

    class Meta(ManagedModel.Meta):
        db_table = 'costos_historicos'
        verbose_name = 'Costo Histórico'
        verbose_name_plural = 'Costos Históricos'

    def __str__(self):
        return f'{self.id_producto.descripcion}: Gs. {self.costo_unitario_neto} ({self.fecha_compra})'


class HistoricoPrecios(ManagedModel):
    '''Tabla historico_precios - Historial de precios de productos'''
    # NOTA: Este modelo necesita revisión - mysqls table structure differs significantly
    id_historico_precio = models.BigAutoField(db_column='id_historico', primary_key=True)  # MySQL: id_historico
    # id_precio (campo falta en modelo Django)
    id_producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        db_column='id_producto',
        related_name='historico_precios'
    )
    # id_lista (campo falta en modelo Django)
    precio_venta_anterior = models.DecimalField(db_column='precio_anterior', max_digits=12, decimal_places=2)  # MySQL: precio_anterior
    precio_venta_nuevo = models.DecimalField(db_column='precio_nuevo', max_digits=12, decimal_places=2)  # MySQL: precio_nuevo
    fecha_cambio = models.DateTimeField(db_column='fecha_cambio')
    # motivo = models.CharField(db_column='motivo', max_length=255, blank=True, null=True)  # Campo no existe en MySQL
    id_empleado_autoriza = models.ForeignKey(
        Empleado,
        on_delete=models.PROTECT,
        db_column='id_empleado_modifico',  # MySQL: id_empleado_modifico
        blank=True,
        null=True,
        related_name='historico_precios_modificados'
    )

    class Meta(ManagedModel.Meta):
        db_table = 'historico_precios'
        verbose_name = 'Histórico de Precios'
        verbose_name_plural = 'Históricos de Precios'

    def __str__(self):
        return f'{self.id_producto.descripcion}: {self.precio_venta_anterior} -> {self.precio_venta_nuevo}'


class MovimientosStock(ManagedModel):
    '''Tabla movimientos_stock - Movimientos de stock'''
    TIPO_MOVIMIENTO_CHOICES = [
        ('Entrada', 'Entrada'),
        ('Salida', 'Salida'),
        ('Ajuste', 'Ajuste'),
    ]

    id_movimientostock = models.BigAutoField(db_column='id_movimientostock', primary_key=True)
    id_producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        db_column='id_producto',
        related_name='movimientos'
    )
    id_empleado_autoriza = models.ForeignKey(
        Empleado,
        on_delete=models.PROTECT,
        db_column='id_empleado_autoriza'
    )
    id_venta = models.ForeignKey(
        'pos.Venta',  # ACTUALIZADO: referencia al modelo migrado en pos app
        on_delete=models.SET_NULL,
        db_column='id_venta',
        blank=True,
        null=True
    )
    id_compra = models.ForeignKey(
        'gestion.Compras',  # CAMBIADO: referencia correcta a la app gestion
        on_delete=models.SET_NULL,
        db_column='id_compra',
        blank=True,
        null=True
    )
    fecha_hora = models.DateTimeField(db_column='fecha_hora')
    tipo_movimiento = models.CharField(db_column='tipo_movimiento', max_length=7, choices=TIPO_MOVIMIENTO_CHOICES)
    cantidad = models.DecimalField(db_column='cantidad', max_digits=10, decimal_places=3)
    stock_resultante = models.DecimalField(
        db_column='stock_resultante', 
        max_digits=10, 
        decimal_places=3,
        default=0,
        help_text='Se calcula automáticamente por el trigger trg_stock_unico_after_movement'
    )
    referencia_documento = models.CharField(db_column='referencia_documento', max_length=50, blank=True, null=True)

    class Meta(ManagedModel.Meta):
        db_table = 'movimientos_stock'
        verbose_name = 'Movimiento de Stock'
        verbose_name_plural = 'Movimientos de Stock'

    def __str__(self):
        return f'{self.tipo_movimiento}: {self.id_producto.descripcion} ({self.cantidad})'