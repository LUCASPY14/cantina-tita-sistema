# gestion/models/configuraciones.py
"""
Modelos para configuraciones avanzadas del sistema y personalización
"""

from django.db import models
from .base import ManagedModel
from .empleados import Empleado

class ConfiguracionSistema(ManagedModel):
    """Configuraciones generales del sistema"""
    id_config = models.AutoField(db_column='id_config', primary_key=True)
    clave = models.CharField(db_column='clave', max_length=100, unique=True)
    valor = models.TextField(db_column='valor')
    tipo_dato = models.CharField(
        db_column='tipo',
        max_length=20,
        choices=[
            ('STRING', 'Texto'),
            ('INTEGER', 'Número entero'),
            ('DECIMAL', 'Número decimal'),
            ('BOOLEAN', 'Verdadero/Falso'),
            ('JSON', 'JSON'),
            ('DATE', 'Fecha'),
            ('TIME', 'Hora'),
            ('DATETIME', 'Fecha y hora')
        ]
    )
    
    categoria = models.CharField(
        db_column='categoria',
        max_length=50,
        choices=[
            ('GENERAL', 'General'),
            ('FACTURACION', 'Facturación'),
            ('NOTIFICACIONES', 'Notificaciones'),
            ('SEGURIDAD', 'Seguridad'),
            ('INTEGRACIONES', 'Integraciones'),
            ('UI', 'Interfaz de Usuario'),
            ('REPORTES', 'Reportes'),
            ('SISTEMA', 'Sistema')
        ]
    )
    
    descripcion = models.TextField(db_column='descripcion')
    valor_por_defecto = models.TextField(db_column='valor_defecto')
    
    # Validaciones
    es_requerido = models.BooleanField(db_column='requerido', default=False)
    validacion_regex = models.CharField(db_column='validacion', max_length=500, blank=True)
    valores_permitidos = models.JSONField(
        db_column='valores_permitidos',
        default=list,
        blank=True,
        help_text='Lista de valores válidos (para select/choice)'
    )
    valor_minimo = models.CharField(db_column='valor_min', max_length=100, blank=True)
    valor_maximo = models.CharField(db_column='valor_max', max_length=100, blank=True)
    
    # Control de cambios
    requiere_reinicio = models.BooleanField(db_column='requiere_reinicio', default=False)
    solo_superuser = models.BooleanField(db_column='solo_superuser', default=False)
    
    activo = models.BooleanField(db_column='activo', default=True)
    updated_at = models.DateTimeField(db_column='updated_at', auto_now=True)
    updated_by = models.ForeignKey(
        Empleado,
        on_delete=models.SET_NULL,
        db_column='updated_by',
        null=True,
        blank=True
    )

    class Meta(ManagedModel.Meta):
        db_table = 'configuracion_sistema'
        verbose_name = 'Configuración del Sistema'
        verbose_name_plural = 'Configuraciones del Sistema'
        indexes = [
            models.Index(fields=['categoria']),
            models.Index(fields=['clave'])
        ]

    def __str__(self):
        return f'{self.clave} ({self.categoria})'

    def get_valor_typed(self):
        """Devuelve el valor convertido al tipo correcto"""
        if self.tipo_dato == 'INTEGER':
            return int(self.valor)
        elif self.tipo_dato == 'DECIMAL':
            return float(self.valor)
        elif self.tipo_dato == 'BOOLEAN':
            return self.valor.lower() in ['true', '1', 'yes', 'si']
        elif self.tipo_dato == 'JSON':
            import json
            return json.loads(self.valor)
        return self.valor


class PerfilUsuario(ManagedModel):
    """Perfiles de personalización por usuario"""
    id_perfil = models.AutoField(db_column='id_perfil', primary_key=True)
    empleado = models.OneToOneField(
        Empleado,
        on_delete=models.CASCADE,
        db_column='id_empleado',
        related_name='perfil'
    )
    
    # Configuraciones de interfaz
    tema_ui = models.CharField(
        db_column='tema',
        max_length=20,
        choices=[
            ('CLARO', 'Tema Claro'),
            ('OSCURO', 'Tema Oscuro'),
            ('AUTO', 'Automático')
        ],
        default='CLARO'
    )
    
    idioma = models.CharField(
        db_column='idioma',
        max_length=10,
        choices=[
            ('ES', 'Español'),
            ('EN', 'English'),
            ('PT', 'Português')
        ],
        default='ES'
    )
    
    zona_horaria = models.CharField(
        db_column='timezone',
        max_length=50,
        default='America/Asuncion'
    )
    
    # Configuraciones de dashboard
    dashboard_config = models.JSONField(
        db_column='dashboard_config',
        default=dict,
        help_text='Configuración de widgets y layout del dashboard'
    )
    
    menu_colapsado = models.BooleanField(db_column='menu_colapsado', default=False)
    
    # Configuraciones de notificaciones
    notif_email_activo = models.BooleanField(db_column='notif_email', default=True)
    notif_push_activo = models.BooleanField(db_column='notif_push', default=True)
    notif_desktop_activo = models.BooleanField(db_column='notif_desktop', default=False)
    
    # Configuraciones de reportes
    formato_fecha_preferido = models.CharField(
        db_column='formato_fecha',
        max_length=20,
        choices=[
            ('DD/MM/YYYY', 'DD/MM/YYYY'),
            ('MM/DD/YYYY', 'MM/DD/YYYY'),
            ('YYYY-MM-DD', 'YYYY-MM-DD')
        ],
        default='DD/MM/YYYY'
    )
    
    moneda_preferida = models.CharField(
        db_column='moneda',
        max_length=10,
        choices=[
            ('PYG', 'Guaraníes (Gs.)'),
            ('USD', 'Dólares ($)'),
            ('EUR', 'Euros (€)')
        ],
        default='PYG'
    )
    
    # Configuraciones avanzadas
    configuraciones_adicionales = models.JSONField(
        db_column='config_adicional',
        default=dict,
        blank=True
    )
    
    created_at = models.DateTimeField(db_column='created_at', auto_now_add=True)
    updated_at = models.DateTimeField(db_column='updated_at', auto_now=True)

    class Meta(ManagedModel.Meta):
        db_table = 'perfiles_usuario'
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'

    def __str__(self):
        return f'Perfil de {self.empleado.nombre}'


class PlantillaTarea(ManagedModel):
    """Plantillas de tareas automatizadas"""
    id_plantilla = models.AutoField(db_column='id_plantilla', primary_key=True)
    nombre = models.CharField(db_column='nombre', max_length=100)
    descripcion = models.TextField(db_column='descripcion')
    
    tipo_tarea = models.CharField(
        db_column='tipo_tarea',
        max_length=30,
        choices=[
            ('BACKUP', 'Backup de datos'),
            ('REPORTE', 'Generación de reportes'),
            ('LIMPIEZA', 'Limpieza de datos'),
            ('NOTIFICACION', 'Envío de notificaciones'),
            ('IMPORTACION', 'Importación de datos'),
            ('EXPORTACION', 'Exportación de datos'),
            ('MANTENIMIENTO', 'Mantenimiento del sistema')
        ]
    )
    
    # Configuración de ejecución
    comando_ejecutar = models.TextField(db_column='comando')  # Python script, function, etc.
    parametros = models.JSONField(db_column='parametros', default=dict)
    
    # Programación
    frecuencia = models.CharField(
        db_column='frecuencia',
        max_length=20,
        choices=[
            ('MANUAL', 'Manual'),
            ('MINUTELY', 'Cada minuto'),
            ('HOURLY', 'Cada hora'),
            ('DAILY', 'Diario'),
            ('WEEKLY', 'Semanal'),
            ('MONTHLY', 'Mensual'),
            ('CRON', 'Expresión Cron')
        ]
    )
    
    cron_expresion = models.CharField(
        db_column='cron',
        max_length=100,
        blank=True,
        help_text='Para frecuencia tipo CRON'
    )
    
    # Control de ejecución
    timeout_segundos = models.IntegerField(db_column='timeout', default=300)
    max_reintentos = models.IntegerField(db_column='max_reintentos', default=3)
    
    # Notificaciones
    notificar_exito = models.BooleanField(db_column='notif_exito', default=False)
    notificar_error = models.BooleanField(db_column='notif_error', default=True)
    destinatarios_notif = models.ManyToManyField(
        Empleado,
        through='DestinatarioTarea',
        related_name='tareas_suscritas'
    )
    
    activo = models.BooleanField(db_column='activo', default=True)
    created_by = models.ForeignKey(
        Empleado,
        on_delete=models.SET_NULL,
        db_column='created_by',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(db_column='created_at', auto_now_add=True)

    class Meta(ManagedModel.Meta):
        db_table = 'plantillas_tarea'
        verbose_name = 'Plantilla de Tarea'
        verbose_name_plural = 'Plantillas de Tareas'

    def __str__(self):
        return f'{self.nombre} ({self.tipo_tarea}) - {self.frecuencia}'


class DestinatarioTarea(ManagedModel):
    """Destinatarios de notificaciones de tareas"""
    id_destinatario = models.AutoField(db_column='id_destinatario', primary_key=True)
    plantilla = models.ForeignKey(PlantillaTarea, on_delete=models.CASCADE, db_column='id_plantilla')
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, db_column='id_empleado')
    notificar_inicio = models.BooleanField(db_column='notif_inicio', default=False)
    notificar_fin = models.BooleanField(db_column='notif_fin', default=True)
    notificar_error = models.BooleanField(db_column='notif_error', default=True)

    class Meta(ManagedModel.Meta):
        db_table = 'destinatarios_tarea'
        unique_together = [['plantilla', 'empleado']]


class EjecucionTarea(ManagedModel):
    """Historial de ejecuciones de tareas"""
    id_ejecucion = models.AutoField(db_column='id_ejecucion', primary_key=True)
    plantilla = models.ForeignKey(
        PlantillaTarea,
        on_delete=models.CASCADE,
        db_column='id_plantilla',
        related_name='ejecuciones'
    )
    
    fecha_inicio = models.DateTimeField(db_column='fecha_inicio', auto_now_add=True)
    fecha_fin = models.DateTimeField(db_column='fecha_fin', null=True, blank=True)
    duracion_segundos = models.IntegerField(db_column='duracion_seg', null=True, blank=True)
    
    estado = models.CharField(
        db_column='estado',
        max_length=20,
        choices=[
            ('INICIADO', 'Iniciado'),
            ('EJECUTANDO', 'Ejecutando'),
            ('COMPLETADO', 'Completado'),
            ('ERROR', 'Error'),
            ('TIMEOUT', 'Timeout'),
            ('CANCELADO', 'Cancelado')
        ]
    )
    
    resultado = models.TextField(db_column='resultado', blank=True, null=True)
    mensaje_error = models.TextField(db_column='error_msg', blank=True, null=True)
    logs_ejecucion = models.TextField(db_column='logs', blank=True, null=True)
    
    # Metadatos
    pid_proceso = models.IntegerField(db_column='pid', null=True, blank=True)
    servidor = models.CharField(db_column='servidor', max_length=100, blank=True)
    parametros_usados = models.JSONField(db_column='parametros', default=dict)
    
    ejecutado_por = models.ForeignKey(
        Empleado,
        on_delete=models.SET_NULL,
        db_column='ejecutado_por',
        null=True,
        blank=True,
        help_text='NULL si fue automático'
    )

    class Meta(ManagedModel.Meta):
        db_table = 'ejecuciones_tarea'
        verbose_name = 'Ejecución de Tarea'
        verbose_name_plural = 'Ejecuciones de Tareas'
        indexes = [
            models.Index(fields=['fecha_inicio']),
            models.Index(fields=['estado']),
            models.Index(fields=['plantilla', 'fecha_inicio'])
        ]

    def __str__(self):
        return f'{self.plantilla.nombre} - {self.estado} ({self.fecha_inicio.strftime("%d/%m/%Y %H:%M")})'


class CacheConfiguracion(ManagedModel):
    """Configuración de caché por funcionalidad"""
    id_cache = models.AutoField(db_column='id_cache', primary_key=True)
    clave = models.CharField(db_column='clave', max_length=100, unique=True)
    descripcion = models.TextField(db_column='descripcion')
    
    # Configuración del cache
    ttl_segundos = models.IntegerField(db_column='ttl_segundos', default=300)  # 5 minutos
    max_size_mb = models.IntegerField(db_column='max_size_mb', default=10)
    
    tipo_cache = models.CharField(
        db_column='tipo_cache',
        max_length=20,
        choices=[
            ('MEMORIA', 'Memoria'),
            ('REDIS', 'Redis'),
            ('DATABASE', 'Base de datos'),
            ('FILE', 'Archivo')
        ]
    )
    
    # Estrategia de invalidación
    invalidacion_automatica = models.BooleanField(db_column='auto_invalidate', default=True)
    eventos_invalidacion = models.JSONField(
        db_column='eventos_invalid',
        default=list,
        help_text='Eventos que invalidan este cache'
    )
    
    activo = models.BooleanField(db_column='activo', default=True)
    
    # Estadísticas
    hits = models.BigIntegerField(db_column='hits', default=0)
    misses = models.BigIntegerField(db_column='misses', default=0)
    ultima_limpieza = models.DateTimeField(db_column='ultima_limpieza', null=True, blank=True)

    class Meta(ManagedModel.Meta):
        db_table = 'cache_configuracion'
        verbose_name = 'Configuración de Cache'
        verbose_name_plural = 'Configuraciones de Cache'

    def __str__(self):
        hit_rate = (self.hits / (self.hits + self.misses) * 100) if (self.hits + self.misses) > 0 else 0
        return f'{self.clave} ({hit_rate:.1f}% hit rate)'