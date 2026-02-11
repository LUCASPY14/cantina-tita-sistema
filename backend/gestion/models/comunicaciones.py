# gestion/models/comunicaciones.py
"""
Modelos para comunicaciones, emails y plantillas
"""

from django.db import models
from .base import ManagedModel
from .empleados import Empleado
from .clientes import Cliente

class EmailTemplate(ManagedModel):
    """Plantillas de email del sistema"""
    id_template = models.AutoField(db_column='id_template', primary_key=True)
    codigo = models.CharField(db_column='codigo', max_length=50, unique=True)
    nombre = models.CharField(db_column='nombre', max_length=100)
    descripcion = models.TextField(db_column='descripcion', blank=True, null=True)
    asunto = models.CharField(db_column='asunto', max_length=200)
    cuerpo_html = models.TextField(db_column='cuerpo_html')
    cuerpo_texto = models.TextField(db_column='cuerpo_texto', blank=True, null=True)
    
    # Variables disponibles en la plantilla
    variables_disponibles = models.JSONField(
        db_column='variables',
        default=list,
        help_text='Lista de variables que se pueden usar: {{cliente.nombre}}, {{fecha}}, etc.'
    )
    
    categoria = models.CharField(
        db_column='categoria',
        max_length=30,
        choices=[
            ('BIENVENIDA', 'Bienvenida'),
            ('NOTIFICACION', 'Notificación'),
            ('PROMOCION', 'Promoción'),
            ('FACTURACION', 'Facturación'),
            ('RECORDATORIO', 'Recordatorio'),
            ('SISTEMA', 'Sistema')
        ]
    )
    
    activo = models.BooleanField(db_column='activo', default=True)
    created_at = models.DateTimeField(db_column='created_at', auto_now_add=True)
    updated_at = models.DateTimeField(db_column='updated_at', auto_now=True)
    created_by = models.ForeignKey(
        Empleado,
        on_delete=models.SET_NULL,
        db_column='created_by',
        null=True,
        blank=True
    )

    class Meta(ManagedModel.Meta):
        db_table = 'email_templates'
        verbose_name = 'Plantilla de Email'
        verbose_name_plural = 'Plantillas de Email'

    def __str__(self):
        return f'{self.nombre} ({self.codigo})'


class EmailEnviado(ManagedModel):
    """Log de emails enviados"""
    id_email = models.AutoField(db_column='id_email', primary_key=True)
    template = models.ForeignKey(
        EmailTemplate,
        on_delete=models.SET_NULL,
        db_column='id_template',
        null=True,
        blank=True,
        related_name='emails_enviados'
    )
    
    # Datos del destinatario
    email_destinatario = models.EmailField(db_column='email_destinatario')
    nombre_destinatario = models.CharField(db_column='nombre_destinatario', max_length=100, blank=True)
    
    # Cliente asociado (si aplica)
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.SET_NULL,
        db_column='id_cliente',
        null=True,
        blank=True,
        related_name='emails_recibidos'
    )
    
    # Contenido enviado
    asunto_enviado = models.CharField(db_column='asunto', max_length=200)
    cuerpo_enviado = models.TextField(db_column='cuerpo')
    
    # Estado del envío
    estado = models.CharField(
        db_column='estado',
        max_length=20,
        choices=[
            ('PENDIENTE', 'Pendiente'),
            ('ENVIADO', 'Enviado'),
            ('ENTREGADO', 'Entregado'),
            ('REBOTADO', 'Rebotado'),
            ('ERROR', 'Error')
        ],
        default='PENDIENTE'
    )
    
    fecha_envio = models.DateTimeField(db_column='fecha_envio', auto_now_add=True)
    fecha_entrega = models.DateTimeField(db_column='fecha_entrega', null=True, blank=True)
    fecha_apertura = models.DateTimeField(db_column='fecha_apertura', null=True, blank=True)
    
    # Metadatos
    mensaje_error = models.TextField(db_column='mensaje_error', blank=True, null=True)
    intentos_envio = models.IntegerField(db_column='intentos', default=1)
    
    enviado_por = models.ForeignKey(
        Empleado,
        on_delete=models.SET_NULL,
        db_column='enviado_por',
        null=True,
        blank=True
    )

    class Meta(ManagedModel.Meta):
        db_table = 'emails_enviados'
        verbose_name = 'Email Enviado'
        verbose_name_plural = 'Emails Enviados'

    def __str__(self):
        return f'{self.asunto_enviado} -> {self.email_destinatario} ({self.estado})'


class SmsTemplate(ManagedModel):
    """Plantillas de SMS"""
    id_template = models.AutoField(db_column='id_template', primary_key=True)
    codigo = models.CharField(db_column='codigo', max_length=50, unique=True)
    nombre = models.CharField(db_column='nombre', max_length=100)
    mensaje = models.CharField(db_column='mensaje', max_length=160)  # Límite SMS
    variables_disponibles = models.JSONField(db_column='variables', default=list)
    
    categoria = models.CharField(
        db_column='categoria',
        max_length=30,
        choices=[
            ('CONFIRMACION', 'Confirmación'),
            ('ALERTA', 'Alerta'),
            ('PROMOCION', 'Promoción'),
            ('RECORDATORIO', 'Recordatorio')
        ]
    )
    
    activo = models.BooleanField(db_column='activo', default=True)
    created_at = models.DateTimeField(db_column='created_at', auto_now_add=True)

    class Meta(ManagedModel.Meta):
        db_table = 'sms_templates'
        verbose_name = 'Plantilla de SMS'
        verbose_name_plural = 'Plantillas de SMS'

    def __str__(self):
        return f'{self.nombre} ({self.codigo})'


class SmsEnviado(ManagedModel):
    """Log de SMS enviados"""
    id_sms = models.AutoField(db_column='id_sms', primary_key=True)
    template = models.ForeignKey(
        SmsTemplate,
        on_delete=models.SET_NULL,
        db_column='id_template',
        null=True,
        blank=True
    )
    
    telefono_destinatario = models.CharField(db_column='telefono', max_length=20)
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.SET_NULL,
        db_column='id_cliente',
        null=True,
        blank=True
    )
    
    mensaje_enviado = models.CharField(db_column='mensaje', max_length=160)
    
    estado = models.CharField(
        db_column='estado',
        max_length=20,
        choices=[
            ('PENDIENTE', 'Pendiente'),
            ('ENVIADO', 'Enviado'),
            ('ENTREGADO', 'Entregado'),
            ('ERROR', 'Error')
        ],
        default='PENDIENTE'
    )
    
    fecha_envio = models.DateTimeField(db_column='fecha_envio', auto_now_add=True)
    fecha_entrega = models.DateTimeField(db_column='fecha_entrega', null=True, blank=True)
    costo = models.DecimalField(db_column='costo', max_digits=10, decimal_places=2, null=True, blank=True)
    
    enviado_por = models.ForeignKey(
        Empleado,
        on_delete=models.SET_NULL,
        db_column='enviado_por',
        null=True,
        blank=True
    )

    class Meta(ManagedModel.Meta):
        db_table = 'sms_enviados'
        verbose_name = 'SMS Enviado'
        verbose_name_plural = 'SMS Enviados'

    def __str__(self):
        return f'SMS -> {self.telefono_destinatario} ({self.estado})'


class CampanaComunicacion(ManagedModel):
    """Campañas de comunicación masiva"""
    id_campana = models.AutoField(db_column='id_campana', primary_key=True)
    nombre = models.CharField(db_column='nombre', max_length=100)
    descripcion = models.TextField(db_column='descripcion')
    
    tipo_comunicacion = models.CharField(
        db_column='tipo',
        max_length=20,
        choices=[
            ('EMAIL', 'Email'),
            ('SMS', 'SMS'),
            ('PUSH', 'Push Notification'),
            ('COMBINADO', 'Combinado')
        ]
    )
    
    # Templates a usar
    email_template = models.ForeignKey(
        EmailTemplate,
        on_delete=models.SET_NULL,
        db_column='id_email_template',
        null=True,
        blank=True
    )
    sms_template = models.ForeignKey(
        SmsTemplate,
        on_delete=models.SET_NULL,
        db_column='id_sms_template',
        null=True,
        blank=True
    )
    
    # Segmentación
    segmentacion_sql = models.TextField(
        db_column='segmentacion',
        help_text='Query SQL para seleccionar destinatarios'
    )
    
    fecha_programada = models.DateTimeField(db_column='fecha_programada', null=True, blank=True)
    fecha_enviada = models.DateTimeField(db_column='fecha_enviada', null=True, blank=True)
    
    estado = models.CharField(
        db_column='estado',
        max_length=20,
        choices=[
            ('BORRADOR', 'Borrador'),
            ('PROGRAMADA', 'Programada'),
            ('ENVIANDO', 'Enviando'),
            ('COMPLETADA', 'Completada'),
            ('CANCELADA', 'Cancelada')
        ],
        default='BORRADOR'
    )
    
    total_destinatarios = models.IntegerField(db_column='total_destinatarios', default=0)
    total_enviados = models.IntegerField(db_column='total_enviados', default=0)
    total_entregados = models.IntegerField(db_column='total_entregados', default=0)
    
    created_by = models.ForeignKey(
        Empleado,
        on_delete=models.SET_NULL,
        db_column='created_by',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(db_column='created_at', auto_now_add=True)

    class Meta(ManagedModel.Meta):
        db_table = 'campanas_comunicacion'
        verbose_name = 'Campaña de Comunicación'
        verbose_name_plural = 'Campañas de Comunicación'

    def __str__(self):
        return f'{self.nombre} ({self.tipo_comunicacion}) - {self.estado}'