# gestion/models/analytics.py
"""
Modelos para analytics, reportes y métricas del sistema
"""

from django.db import models
from .base import ManagedModel
from .empleados import Empleado
from .clientes import Cliente
from .productos import Producto
from pos.models import Venta

class ReporteTemplate(ManagedModel):
    """Plantillas de reportes predefinidos"""
    id_template = models.AutoField(db_column='id_template', primary_key=True)
    nombre = models.CharField(db_column='nombre', max_length=100)
    descripcion = models.TextField(db_column='descripcion', blank=True, null=True)
    query_sql = models.TextField(db_column='query_sql')
    parametros_json = models.JSONField(db_column='parametros', default=dict, blank=True)
    tipo_reporte = models.CharField(
        db_column='tipo_reporte',
        max_length=20,
        choices=[
            ('VENTAS', 'Ventas'),
            ('PRODUCTOS', 'Productos'),
            ('CLIENTES', 'Clientes'),
            ('FINANCIERO', 'Financiero'),
            ('OPERATIVO', 'Operativo')
        ]
    )
    frecuencia_auto = models.CharField(
        db_column='frecuencia',
        max_length=20,
        choices=[
            ('MANUAL', 'Manual'),
            ('DIARIO', 'Diario'),
            ('SEMANAL', 'Semanal'),
            ('MENSUAL', 'Mensual')
        ],
        default='MANUAL'
    )
    activo = models.BooleanField(db_column='activo', default=True)
    created_at = models.DateTimeField(db_column='created_at', auto_now_add=True)
    created_by = models.ForeignKey(
        Empleado,
        on_delete=models.SET_NULL,
        db_column='created_by',
        null=True,
        blank=True
    )

    class Meta(ManagedModel.Meta):
        db_table = 'reporte_templates'
        verbose_name = 'Plantilla de Reporte'
        verbose_name_plural = 'Plantillas de Reportes'

    def __str__(self):
        return f'{self.nombre} ({self.tipo_reporte})'


class KpiMetrica(ManagedModel):
    """KPIs y métricas del negocio"""
    id_kpi = models.AutoField(db_column='id_kpi', primary_key=True)
    nombre = models.CharField(db_column='nombre', max_length=100)
    descripcion = models.TextField(db_column='descripcion')
    formula = models.TextField(db_column='formula')  # Fórmula o query para calcular
    unidad_medida = models.CharField(db_column='unidad', max_length=20)  # %, Gs., unidades, etc.
    valor_objetivo = models.DecimalField(
        db_column='valor_objetivo', 
        max_digits=15, 
        decimal_places=2, 
        blank=True, 
        null=True
    )
    categoria = models.CharField(
        db_column='categoria',
        max_length=30,
        choices=[
            ('VENTAS', 'Ventas'),
            ('RENTABILIDAD', 'Rentabilidad'),
            ('CLIENTES', 'Clientes'),
            ('OPERACIONES', 'Operaciones'),
            ('CALIDAD', 'Calidad')
        ]
    )
    frecuencia_calculo = models.CharField(
        db_column='frecuencia',
        max_length=20,
        choices=[
            ('TIEMPO_REAL', 'Tiempo Real'),
            ('DIARIO', 'Diario'),
            ('SEMANAL', 'Semanal'),
            ('MENSUAL', 'Mensual')
        ]
    )
    activo = models.BooleanField(db_column='activo', default=True)

    class Meta(ManagedModel.Meta):
        db_table = 'kpi_metricas'
        verbose_name = 'KPI Métrica'
        verbose_name_plural = 'KPI Métricas'

    def __str__(self):
        return f'{self.nombre} ({self.categoria})'


class ValorKpi(ManagedModel):
    """Valores históricos de KPIs"""
    id_valor = models.AutoField(db_column='id_valor', primary_key=True)
    kpi = models.ForeignKey(
        KpiMetrica,
        on_delete=models.CASCADE,
        db_column='id_kpi',
        related_name='valores'
    )
    fecha = models.DateField(db_column='fecha')
    valor = models.DecimalField(db_column='valor', max_digits=15, decimal_places=2)
    notas = models.TextField(db_column='notas', blank=True, null=True)
    calculado_automaticamente = models.BooleanField(db_column='auto_calc', default=True)
    created_at = models.DateTimeField(db_column='created_at', auto_now_add=True)

    class Meta(ManagedModel.Meta):
        db_table = 'valores_kpi'
        verbose_name = 'Valor KPI'
        verbose_name_plural = 'Valores KPI'
        unique_together = [['kpi', 'fecha']]

    def __str__(self):
        return f'{self.kpi.nombre}: {self.valor} ({self.fecha})'


class Dashboard(ManagedModel):
    """Dashboards personalizados por usuario"""
    id_dashboard = models.AutoField(db_column='id_dashboard', primary_key=True)
    nombre = models.CharField(db_column='nombre', max_length=100)
    descripcion = models.TextField(db_column='descripcion', blank=True, null=True)
    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.CASCADE,
        db_column='id_empleado',
        related_name='dashboards'
    )
    configuracion_json = models.JSONField(db_column='configuracion', default=dict)
    es_publico = models.BooleanField(db_column='es_publico', default=False)
    predeterminado = models.BooleanField(db_column='predeterminado', default=False)
    activo = models.BooleanField(db_column='activo', default=True)
    created_at = models.DateTimeField(db_column='created_at', auto_now_add=True)
    updated_at = models.DateTimeField(db_column='updated_at', auto_now=True)

    class Meta(ManagedModel.Meta):
        db_table = 'dashboards'
        verbose_name = 'Dashboard'
        verbose_name_plural = 'Dashboards'

    def __str__(self):
        return f'{self.nombre} - {self.empleado.nombre}'


class AlertaAutomatica(ManagedModel):
    """Sistema de alertas automáticas"""
    id_alerta = models.AutoField(db_column='id_alerta', primary_key=True)
    nombre = models.CharField(db_column='nombre', max_length=100)
    descripcion = models.TextField(db_column='descripcion')
    condicion = models.TextField(db_column='condicion')  # Condición SQL o lógica
    tipo_alerta = models.CharField(
        db_column='tipo_alerta',
        max_length=20,
        choices=[
            ('STOCK_BAJO', 'Stock Bajo'),
            ('VENTA_ALTA', 'Venta Alta'),
            ('ERROR_SISTEMA', 'Error Sistema'),
            ('KPI_META', 'Meta KPI'),
            ('PERSONALIZADA', 'Personalizada')
        ]
    )
    nivel_criticidad = models.CharField(
        db_column='criticidad',
        max_length=10,
        choices=[
            ('BAJA', 'Baja'),
            ('MEDIA', 'Media'),
            ('ALTA', 'Alta'),
            ('CRITICA', 'Crítica')
        ]
    )
    frecuencia_verificacion = models.IntegerField(
        db_column='frecuencia_min',
        help_text='Minutos entre verificaciones'
    )
    destinatarios = models.ManyToManyField(
        Empleado,
        through='AlertaDestinatario',
        related_name='alertas_suscritas'
    )
    activo = models.BooleanField(db_column='activo', default=True)
    ultima_verificacion = models.DateTimeField(db_column='ultima_verificacion', blank=True, null=True)

    class Meta(ManagedModel.Meta):
        db_table = 'alertas_automaticas'
        verbose_name = 'Alerta Automática'
        verbose_name_plural = 'Alertas Automáticas'

    def __str__(self):
        return f'{self.nombre} ({self.tipo_alerta})'


class AlertaDestinatario(ManagedModel):
    """Destinatarios de alertas"""
    id_destinatario = models.AutoField(db_column='id_destinatario', primary_key=True)
    alerta = models.ForeignKey(AlertaAutomatica, on_delete=models.CASCADE, db_column='id_alerta')
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, db_column='id_empleado')
    via_email = models.BooleanField(db_column='via_email', default=True)
    via_sistema = models.BooleanField(db_column='via_sistema', default=True)
    activo = models.BooleanField(db_column='activo', default=True)

    class Meta(ManagedModel.Meta):
        db_table = 'alerta_destinatarios'
        verbose_name = 'Destinatario de Alerta'
        verbose_name_plural = 'Destinatarios de Alertas'
        unique_together = [['alerta', 'empleado']]

    def __str__(self):
        return f'{self.alerta.nombre} -> {self.empleado.nombre}'


class HistorialAlerta(ManagedModel):
    """Historial de alertas disparadas"""
    id_historial = models.AutoField(db_column='id_historial', primary_key=True)
    alerta = models.ForeignKey(
        AlertaAutomatica,
        on_delete=models.CASCADE,
        db_column='id_alerta',
        related_name='historial'
    )
    fecha_disparada = models.DateTimeField(db_column='fecha_disparada', auto_now_add=True)
    mensaje = models.TextField(db_column='mensaje')
    datos_contexto = models.JSONField(db_column='datos_contexto', default=dict)
    resuelto = models.BooleanField(db_column='resuelto', default=False)
    fecha_resolucion = models.DateTimeField(db_column='fecha_resolucion', blank=True, null=True)
    resuelto_por = models.ForeignKey(
        Empleado,
        on_delete=models.SET_NULL,
        db_column='resuelto_por',
        blank=True,
        null=True
    )

    class Meta(ManagedModel.Meta):
        db_table = 'historial_alertas'
        verbose_name = 'Historial de Alerta'
        verbose_name_plural = 'Historial de Alertas'

    def __str__(self):
        return f'{self.alerta.nombre} - {self.fecha_disparada.strftime("%d/%m/%Y %H:%M")}'