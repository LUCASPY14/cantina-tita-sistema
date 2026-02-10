# gestion/models/vistas.py

from django.db import models
from .base import ManagedModel
from .clientes import Hijo

class VistaStockAlerta(ManagedModel):
    '''Vista v_stock_alerta - Productos con stock bajo'''
    id_producto = models.IntegerField(db_column='id_producto', primary_key=True)
    codigo_barra = models.CharField(db_column='codigo_barra', max_length=50, blank=True, null=True)
    descripcion = models.CharField(db_column='descripcion', max_length=255)
    categoria = models.CharField(db_column='categoria', max_length=100)
    stock_actual = models.DecimalField(db_column='stock_actual', max_digits=10, decimal_places=3)
    stock_minimo = models.DecimalField(db_column='stock_minimo', max_digits=10, decimal_places=3)
    diferencia = models.DecimalField(db_column='diferencia', max_digits=11, decimal_places=3)
    nivel_alerta = models.CharField(db_column='nivel_alerta', max_length=7)
    fecha_ultima_actualizacion = models.DateTimeField(db_column='fecha_ultima_actualizacion', blank=True, null=True)
    unidad_medida = models.CharField(db_column='unidad_medida', max_length=50)

    class Meta(ManagedModel.Meta):
        db_table = 'v_stock_alerta'
        verbose_name = 'Alerta de Stock'
        verbose_name_plural = 'Alertas de Stock'

    def __str__(self):
        return f'{self.descripcion} - {self.nivel_alerta} (Stock: {self.stock_actual})'


class VistaSaldoClientes(ManagedModel):
    '''Vista v_saldo_clientes - Saldos de cuenta corriente'''
    id_cliente = models.IntegerField(db_column='id_cliente', primary_key=True)
    nombres = models.CharField(db_column='nombres', max_length=100)
    apellidos = models.CharField(db_column='apellidos', max_length=100)
    nombre_completo = models.CharField(db_column='nombre_completo', max_length=201)
    ruc_ci = models.CharField(db_column='ruc_ci', max_length=20)
    tipo_cliente = models.CharField(db_column='tipo_cliente', max_length=50)
    saldo_actual = models.DecimalField(db_column='saldo_actual', max_digits=30, decimal_places=2)
    ultima_actualizacion = models.DateField(db_column='ultima_actualizacion', blank=True, null=True)
    total_movimientos = models.BigIntegerField(db_column='total_movimientos')

    class Meta(ManagedModel.Meta):
        db_table = 'v_saldo_clientes'
        verbose_name = 'Saldo de Cliente'
        verbose_name_plural = 'Saldos de Clientes'

    def __str__(self):
        return f'{self.nombre_completo}: Gs. {self.saldo_actual:,.0f}'


class VistaConsumosEstudiante(ManagedModel):
    '''Vista v_consumos_estudiante - Resumen de consumos por hijo'''
    id_hijo = models.OneToOneField(
        Hijo,
        on_delete=models.DO_NOTHING,
        db_column='id_hijo',
        primary_key=True,
        related_name='consumos_vista'
    )
    estudiante = models.CharField(db_column='estudiante', max_length=202)
    responsable_nombre = models.CharField(db_column='responsable_nombre', max_length=100)
    responsable_apellido = models.CharField(db_column='responsable_apellido', max_length=100)
    nro_tarjeta = models.CharField(db_column='nro_tarjeta', max_length=20)
    saldo_actual = models.BigIntegerField(db_column='saldo_actual')
    total_consumos = models.BigIntegerField(db_column='total_consumos')
    total_consumido = models.DecimalField(db_column='total_consumido', max_digits=32, decimal_places=2)
    ultimo_consumo = models.DateTimeField(db_column='ultimo_consumo')
    total_recargas = models.BigIntegerField(db_column='total_recargas')
    total_recargado = models.DecimalField(db_column='total_recargado', max_digits=32, decimal_places=2)

    class Meta(ManagedModel.Meta):
        db_table = 'v_consumos_estudiante'
        verbose_name = 'Vista: Consumos por Hijo'
        verbose_name_plural = 'Vista: Consumos por Hijo'

    def __str__(self):
        return f'{self.estudiante} - Saldo: Gs. {self.saldo_actual:,.0f}'
    
    @property
    def hijo(self):
        '''Acceso directo al objeto Hijo relacionado'''
        return self.id_hijo


class VistaStockCriticoAlertas(ManagedModel):
    '''Vista v_stock_critico_alertas - Productos con stock crítico'''
    id_producto = models.IntegerField(db_column='id_producto', primary_key=True)
    codigo_barra = models.CharField(db_column='codigo_barra', max_length=50)
    descripcion = models.CharField(db_column='descripcion', max_length=255)
    categoria = models.CharField(db_column='categoria', max_length=100)
    stock_actual = models.DecimalField(db_column='stock_actual', max_digits=10, decimal_places=3)
    stock_minimo = models.DecimalField(db_column='stock_minimo', max_digits=10, decimal_places=3)

    class Meta(ManagedModel.Meta):
        db_table = 'v_stock_critico_alertas'
        verbose_name = 'Vista: Stock Crítico'
        verbose_name_plural = 'Vista: Stock Crítico'

    def __str__(self):
        return f'{self.codigo_barra} - {self.descripcion}'


class VistaVentasDiaDetallado(ManagedModel):
    '''Vista v_ventas_dia_detallado - Ventas con detalles completos'''
    id_venta = models.BigIntegerField(db_column='id_venta', primary_key=True)
    fecha = models.DateTimeField(db_column='fecha')
    monto_total = models.BigIntegerField(db_column='monto_total')
    nombres = models.CharField(db_column='nombres', max_length=100)
    apellidos = models.CharField(db_column='apellidos', max_length=100)
    cliente_completo = models.CharField(db_column='cliente_completo', max_length=201)
    empleado = models.CharField(db_column='empleado', max_length=100)
    nro_timbrado = models.IntegerField(db_column='nro_timbrado')
    nro_secuencial = models.IntegerField(db_column='nro_secuencial')
    cantidad_items = models.BigIntegerField(db_column='cantidad_items')
    productos = models.TextField(db_column='productos')
    total_pagado = models.DecimalField(db_column='total_pagado', max_digits=32, decimal_places=0)
    saldo_pendiente = models.DecimalField(db_column='saldo_pendiente', max_digits=33, decimal_places=0)

    class Meta(ManagedModel.Meta):
        db_table = 'v_ventas_dia_detallado'
        verbose_name = 'Vista: Ventas del Día Detallado'
        verbose_name_plural = 'Vista: Ventas del Día Detallado'

    def __str__(self):
        return f'Venta {self.id_venta} - {self.cliente_completo}'


class VistaRecargasHistorial(ManagedModel):
    '''Vista v_recargas_historial - Historial de recargas'''
    id_carga = models.BigIntegerField(db_column='id_carga', primary_key=True)
    fecha_carga = models.DateTimeField(db_column='fecha_carga')
    monto_cargado = models.DecimalField(db_column='monto_cargado', max_digits=10, decimal_places=2)
    nro_tarjeta = models.CharField(db_column='nro_tarjeta', max_length=20)
    id_hijo = models.ForeignKey(
        Hijo,
        on_delete=models.DO_NOTHING,
        db_column='id_hijo',
        related_name='recargas_vista'
    )
    estudiante = models.CharField(db_column='estudiante', max_length=202)
    responsable = models.CharField(db_column='responsable', max_length=201)
    telefono = models.CharField(db_column='telefono', max_length=20)
    empleado_registro = models.CharField(db_column='empleado_registro', max_length=100)
    saldo_actual_tarjeta = models.BigIntegerField(db_column='saldo_actual_tarjeta')

    class Meta(ManagedModel.Meta):
        db_table = 'v_recargas_historial'
        verbose_name = 'Vista: Historial de Recargas'
        verbose_name_plural = 'Vista: Historial de Recargas'

    def __str__(self):
        return f'Recarga {self.id_carga} - {self.estudiante}'
    
    @property
    def hijo(self):
        '''Acceso directo al objeto Hijo relacionado'''
        return self.id_hijo


class VistaResumenCajaDiario(ManagedModel):
    '''Vista v_resumen_caja_diario - Resumen financiero diario'''
    fecha = models.DateField(db_column='fecha', primary_key=True)
    total_ventas = models.BigIntegerField(db_column='total_ventas')
    monto_total_ventas = models.DecimalField(db_column='monto_total_ventas', max_digits=32, decimal_places=0)
    total_recargas = models.BigIntegerField(db_column='total_recargas')
    monto_total_recargas = models.DecimalField(db_column='monto_total_recargas', max_digits=32, decimal_places=2)
    total_ingresos_dia = models.DecimalField(db_column='total_ingresos_dia', max_digits=33, decimal_places=2)
    total_transacciones_pago = models.BigIntegerField(db_column='total_transacciones_pago')
    total_efectivo = models.DecimalField(db_column='total_efectivo', max_digits=32, decimal_places=0)
    total_tarjeta_debito = models.DecimalField(db_column='total_tarjeta_debito', max_digits=32, decimal_places=0)
    total_tarjeta_credito = models.DecimalField(db_column='total_tarjeta_credito', max_digits=32, decimal_places=0)
    total_transferencias = models.DecimalField(db_column='total_transferencias', max_digits=32, decimal_places=0)

    class Meta(ManagedModel.Meta):
        db_table = 'v_resumen_caja_diario'
        verbose_name = 'Vista: Resumen de Caja Diario'
        verbose_name_plural = 'Vista: Resumen de Caja Diario'

    def __str__(self):
        return f'Caja {self.fecha} - Gs. {self.total_ingresos_dia:,.0f}'


class VistaNotasCreditoDetallado(ManagedModel):
    '''Vista v_notas_credito_detallado - Notas de crédito con detalles'''
    id_nota = models.BigIntegerField(db_column='id_nota', primary_key=True)
    fecha = models.DateTimeField(db_column='fecha')
    monto_total = models.DecimalField(db_column='monto_total', max_digits=12, decimal_places=2)
    estado = models.CharField(db_column='estado', max_length=20)
    observacion = models.CharField(db_column='observacion', max_length=255, blank=True, null=True)
    cliente = models.CharField(db_column='cliente', max_length=201)
    venta_original = models.BigIntegerField(db_column='venta_original', blank=True, null=True)
    fecha_venta_original = models.DateTimeField(db_column='fecha_venta_original', blank=True, null=True)
    monto_venta_original = models.DecimalField(db_column='monto_venta_original', max_digits=12, decimal_places=2, blank=True, null=True)
    cantidad_items = models.IntegerField(db_column='cantidad_items')
    productos = models.TextField(db_column='productos', blank=True, null=True)

    class Meta(ManagedModel.Meta):
        db_table = 'v_notas_credito_detallado'
        verbose_name = 'Vista: Notas de Crédito Detallado'
        verbose_name_plural = 'Vista: Notas de Crédito Detallado'

    def __str__(self):
        return f'NC {self.id_nota} - {self.cliente}'


class VistaAlmuerzosDiarios(ManagedModel):
    '''Vista v_almuerzos_diarios - Almuerzos registrados con detalles'''
    id_registro_consumo = models.BigIntegerField(db_column='id_registro_consumo', primary_key=True)
    fecha_consumo = models.DateField(db_column='fecha_consumo')
    hora_registro = models.TimeField(db_column='hora_registro')
    id_hijo = models.IntegerField(db_column='id_hijo')
    estudiante = models.CharField(db_column='estudiante', max_length=202)
    responsable_nombre = models.CharField(db_column='responsable_nombre', max_length=100)
    responsable_apellido = models.CharField(db_column='responsable_apellido', max_length=100)
    nro_tarjeta = models.CharField(db_column='nro_tarjeta', max_length=20, blank=True, null=True)
    tipo_almuerzo = models.CharField(db_column='tipo_almuerzo', max_length=100, blank=True, null=True)
    descripcion_almuerzo = models.TextField(db_column='descripcion_almuerzo', blank=True, null=True)
    costo_almuerzo = models.DecimalField(db_column='costo_almuerzo', max_digits=10, decimal_places=2, blank=True, null=True)
    marcado_en_cuenta = models.BooleanField(db_column='marcado_en_cuenta')
    origen = models.CharField(db_column='origen', max_length=11)
    id_suscripcion = models.BigIntegerField(db_column='id_suscripcion', blank=True, null=True)

    class Meta(ManagedModel.Meta):
        db_table = 'v_almuerzos_diarios'
        verbose_name = 'Vista: Almuerzos Diarios'
        verbose_name_plural = 'Vista: Almuerzos Diarios'

    def __str__(self):
        return f'{self.estudiante} - {self.fecha_consumo}'


class VistaCuentasAlmuerzoDetallado(ManagedModel):
    '''Vista v_cuentas_almuerzo_detallado - Cuentas mensuales con detalles'''
    id_cuenta = models.BigIntegerField(db_column='id_cuenta', primary_key=True)
    id_hijo = models.IntegerField(db_column='id_hijo')
    estudiante = models.CharField(db_column='estudiante', max_length=202)
    responsable_nombre = models.CharField(db_column='responsable_nombre', max_length=100)
    responsable_apellido = models.CharField(db_column='responsable_apellido', max_length=100)
    responsable_telefono = models.CharField(db_column='responsable_telefono', max_length=20, blank=True, null=True)
    anio = models.IntegerField(db_column='anio')
    mes = models.SmallIntegerField(db_column='mes')
    cantidad_almuerzos = models.IntegerField(db_column='cantidad_almuerzos')
    monto_total = models.DecimalField(db_column='monto_total', max_digits=10, decimal_places=2)
    forma_cobro = models.CharField(db_column='forma_cobro', max_length=20)
    monto_pagado = models.DecimalField(db_column='monto_pagado', max_digits=10, decimal_places=2)
    saldo_pendiente = models.DecimalField(db_column='saldo_pendiente', max_digits=11, decimal_places=2)
    estado = models.CharField(db_column='estado', max_length=10)
    fecha_generacion = models.DateField(db_column='fecha_generacion')
    fecha_actualizacion = models.DateTimeField(db_column='fecha_actualizacion')
    cantidad_pagos = models.BigIntegerField(db_column='cantidad_pagos')

    class Meta(ManagedModel.Meta):
        db_table = 'v_cuentas_almuerzo_detallado'
        verbose_name = 'Vista: Cuentas de Almuerzo Detallado'
        verbose_name_plural = 'Vista: Cuentas de Almuerzo Detallado'

    def __str__(self):
        return f'{self.estudiante} - {self.mes}/{self.anio}'


class VistaReporteMensualSeparado(ManagedModel):
    '''Vista v_reporte_mensual_separado - Reporte mensual: almuerzos vs tarjeta'''
    id_hijo = models.IntegerField(db_column='id_hijo', primary_key=True)
    estudiante = models.CharField(db_column='estudiante', max_length=202)
    nro_tarjeta = models.CharField(db_column='nro_tarjeta', max_length=20, blank=True, null=True)
    saldo_tarjeta_actual = models.BigIntegerField(db_column='saldo_tarjeta_actual', blank=True, null=True)
    almuerzos_mes_actual = models.DecimalField(db_column='almuerzos_mes_actual', max_digits=23, decimal_places=0)
    total_almuerzos_mes = models.DecimalField(db_column='total_almuerzos_mes', max_digits=32, decimal_places=2)
    consumos_tarjeta_mes = models.DecimalField(db_column='consumos_tarjeta_mes', max_digits=32, decimal_places=2)
    cargas_tarjeta_mes = models.DecimalField(db_column='cargas_tarjeta_mes', max_digits=32, decimal_places=2)

    class Meta(ManagedModel.Meta):
        db_table = 'v_reporte_mensual_separado'
        verbose_name = 'Vista: Reporte Mensual Separado'
        verbose_name_plural = 'Vista: Reportes Mensuales Separados'

    def __str__(self):
        return f'{self.estudiante} - Mes Actual'