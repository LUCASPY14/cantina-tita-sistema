# gestion/models/integraciones.py
"""
Modelos para integraciones con APIs externas y servicios
"""

from django.db import models
from .base import ManagedModel
from .empleados import Empleado

class ProveedorApi(ManagedModel):
    """Proveedores de APIs externa"""
    id_proveedor = models.AutoField(db_column='id_proveedor', primary_key=True)
    nombre = models.CharField(db_column='nombre', max_length=100)
    descripcion = models.TextField(db_column='descripcion')
    
    tipo_servicio = models.CharField(
        db_column='tipo_servicio',
        max_length=30,
        choices=[
            ('PAGOS', 'Procesador de Pagos'),
            ('SMS', 'Servicio SMS'),
            ('EMAIL', 'Servicio Email'),
            ('FACTURACION', 'Facturación Electrónica'),
            ('LOGISTICA', 'Logística'),
            ('ANALYTICS', 'Analytics'),
            ('OTRO', 'Otro')
        ]
    )
    
    url_base = models.URLField(db_column='url_base')
    version_api = models.CharField(db_column='version', max_length=20, blank=True)
    documentacion_url = models.URLField(db_column='documentacion', blank=True, null=True)
    
    # Configuraciones de autenticación
    tipo_autenticacion = models.CharField(
        db_column='tipo_auth',
        max_length=20,
        choices=[
            ('API_KEY', 'API Key'),
            ('OAUTH', 'OAuth'),
            ('BEARER', 'Bearer Token'),
            ('BASIC', 'Basic Auth'),
            ('CUSTOM', 'Custom')
        ]
    )
    
    config_autenticacion = models.JSONField(
        db_column='config_auth',
        default=dict,
        help_text='Configuración específica de autenticación (sin credenciales sensibles)'
    )
    
    # Configuraciones generales
    timeout_segundos = models.IntegerField(db_column='timeout', default=30)
    max_reintentos = models.IntegerField(db_column='max_reintentos', default=3)
    
    activo = models.BooleanField(db_column='activo', default=True)
    created_at = models.DateTimeField(db_column='created_at', auto_now_add=True)

    class Meta(ManagedModel.Meta):
        db_table = 'proveedores_api'
        verbose_name = 'Proveedor de API'
        verbose_name_plural = 'Proveedores de API'

    def __str__(self):
        return f'{self.nombre} ({self.tipo_servicio})'


class CredencialApi(ManagedModel):
    """Credenciales seguras para APIs"""
    id_credencial = models.AutoField(db_column='id_credencial', primary_key=True)
    proveedor = models.ForeignKey(
        ProveedorApi,
        on_delete=models.CASCADE,
        db_column='id_proveedor',
        related_name='credenciales'
    )
    
    ambiente = models.CharField(
        db_column='ambiente',
        max_length=20,
        choices=[
            ('DESARROLLO', 'Desarrollo'),
            ('PRUEBAS', 'Pruebas'),
            ('PRODUCCION', 'Producción')
        ]
    )
    
    # Credenciales encriptadas
    api_key_encrypted = models.TextField(db_column='api_key', blank=True, null=True)
    secret_encrypted = models.TextField(db_column='secret', blank=True, null=True)
    token_encrypted = models.TextField(db_column='token', blank=True, null=True)
    
    # Configuración adicional por ambiente
    configuracion_json = models.JSONField(db_column='configuracion', default=dict)
    
    fecha_expiracion = models.DateTimeField(db_column='fecha_expiracion', null=True, blank=True)
    ultima_actualizacion = models.DateTimeField(db_column='updated_at', auto_now=True)
    activo = models.BooleanField(db_column='activo', default=True)

    class Meta(ManagedModel.Meta):
        db_table = 'credenciales_api'
        verbose_name = 'Credencial de API'
        verbose_name_plural = 'Credenciales de API'
        unique_together = [['proveedor', 'ambiente']]

    def __str__(self):
        return f'{self.proveedor.nombre} - {self.ambiente}'


class EndpointApi(ManagedModel):
    """Endpoints específicos de APIs"""
    id_endpoint = models.AutoField(db_column='id_endpoint', primary_key=True)
    proveedor = models.ForeignKey(
        ProveedorApi,
        on_delete=models.CASCADE,
        db_column='id_proveedor',
        related_name='endpoints'
    )
    
    nombre = models.CharField(db_column='nombre', max_length=100)
    descripcion = models.TextField(db_column='descripcion')
    path = models.CharField(db_column='path', max_length=200)  # /api/v1/payments
    metodo_http = models.CharField(
        db_column='metodo',
        max_length=10,
        choices=[
            ('GET', 'GET'),
            ('POST', 'POST'),
            ('PUT', 'PUT'),
            ('DELETE', 'DELETE'),
            ('PATCH', 'PATCH')
        ]
    )
    
    # Configuración del endpoint
    headers_requeridos = models.JSONField(db_column='headers', default=dict)
    parametros_requeridos = models.JSONField(db_column='parametros', default=dict)
    schema_request = models.JSONField(db_column='schema_request', default=dict)
    schema_response = models.JSONField(db_column='schema_response', default=dict)
    
    # Configuraciones específicas
    cache_duracion = models.IntegerField(
        db_column='cache_segundos',
        default=0,
        help_text='0 = sin cache'
    )
    requiere_auth = models.BooleanField(db_column='requiere_auth', default=True)
    
    activo = models.BooleanField(db_column='activo', default=True)

    class Meta(ManagedModel.Meta):
        db_table = 'endpoints_api'
        verbose_name = 'Endpoint de API'
        verbose_name_plural = 'Endpoints de API'

    def __str__(self):
        return f'{self.proveedor.nombre} - {self.metodo_http} {self.path}'


class LogLlamadaApi(ManagedModel):
    """Log de llamadas a APIs externas"""
    id_log = models.AutoField(db_column='id_log', primary_key=True)
    endpoint = models.ForeignKey(
        EndpointApi,
        on_delete=models.SET_NULL,
        db_column='id_endpoint',
        null=True,
        blank=True
    )
    
    # Datos de la llamada
    timestamp = models.DateTimeField(db_column='timestamp', auto_now_add=True)
    metodo_http = models.CharField(db_column='metodo', max_length=10)
    url_completa = models.URLField(db_column='url', max_length=500)
    
    # Request
    headers_request = models.JSONField(db_column='headers_req', default=dict)
    payload_request = models.TextField(db_column='payload_req', blank=True, null=True)
    
    # Response
    status_code = models.IntegerField(db_column='status_code')
    headers_response = models.JSONField(db_column='headers_res', default=dict)
    payload_response = models.TextField(db_column='payload_res', blank=True, null=True)
    
    # Métricas
    tiempo_respuesta_ms = models.IntegerField(db_column='tiempo_ms')
    bytes_enviados = models.IntegerField(db_column='bytes_sent', null=True, blank=True)
    bytes_recibidos = models.IntegerField(db_column='bytes_received', null=True, blank=True)
    
    # Error handling
    exitoso = models.BooleanField(db_column='exitoso', default=True)
    mensaje_error = models.TextField(db_column='error_msg', blank=True, null=True)
    intento_numero = models.IntegerField(db_column='intento', default=1)
    
    # Contexto
    usuario_sistema = models.ForeignKey(
        Empleado,
        on_delete=models.SET_NULL,
        db_column='id_empleado',
        null=True,
        blank=True
    )
    ip_origen = models.GenericIPAddressField(db_column='ip_origen', null=True, blank=True)
    contexto_adicional = models.JSONField(db_column='contexto', default=dict)

    class Meta(ManagedModel.Meta):
        db_table = 'log_llamadas_api'
        verbose_name = 'Log de Llamada API'
        verbose_name_plural = 'Logs de Llamadas API'
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['exitoso']),
            models.Index(fields=['endpoint', 'timestamp'])
        ]

    def __str__(self):
        status = "✅" if self.exitoso else "❌"
        return f'{status} {self.metodo_http} {self.url_completa} ({self.status_code}) - {self.timestamp.strftime("%d/%m/%Y %H:%M")}'


class WebhookEndpoint(ManagedModel):
    """Webhooks que recibimos de APIs externas"""
    id_webhook = models.AutoField(db_column='id_webhook', primary_key=True)
    proveedor = models.ForeignKey(
        ProveedorApi,
        on_delete=models.CASCADE,
        db_column='id_proveedor',
        related_name='webhooks'
    )
    
    nombre = models.CharField(db_column='nombre', max_length=100)
    descripcion = models.TextField(db_column='descripcion')
    path = models.CharField(db_column='path', max_length=200)  # /webhooks/payments/tigo
    
    # Configuración de seguridad
    requiere_verificacion = models.BooleanField(db_column='requiere_verificacion', default=True)
    secret_key = models.CharField(db_column='secret_key', max_length=255, blank=True)
    verificacion_header = models.CharField(db_column='header_verificacion', max_length=100, blank=True)
    
    # Configuración del webhook
    eventos_aceptados = models.JSONField(
        db_column='eventos',
        default=list,
        help_text='Lista de eventos que acepta este webhook'
    )
    
    # Procesamiento
    handler_function = models.CharField(
        db_column='handler_func',
        max_length=200,
        help_text='Función que procesa el webhook: app.module.function_name'
    )
    
    activo = models.BooleanField(db_column='activo', default=True)
    created_at = models.DateTimeField(db_column='created_at', auto_now_add=True)

    class Meta(ManagedModel.Meta):
        db_table = 'webhook_endpoints'
        verbose_name = 'Webhook Endpoint'
        verbose_name_plural = 'Webhook Endpoints'
        unique_together = [['proveedor', 'path']]

    def __str__(self):
        return f'{self.proveedor.nombre} - {self.path}'


class LogWebhook(ManagedModel):
    """Log de webhooks recibidos"""
    id_log = models.AutoField(db_column='id_log', primary_key=True)
    webhook = models.ForeignKey(
        WebhookEndpoint,
        on_delete=models.SET_NULL,
        db_column='id_webhook',
        null=True,
        blank=True,
        related_name='logs'
    )
    
    timestamp = models.DateTimeField(db_column='timestamp', auto_now_add=True)
    
    # Datos recibidos
    headers_recibidos = models.JSONField(db_column='headers', default=dict)
    payload_recibido = models.TextField(db_column='payload')
    evento_tipo = models.CharField(db_column='evento_tipo', max_length=100, blank=True)
    
    # Verificación
    verificacion_exitosa = models.BooleanField(db_column='verificacion_ok', default=False)
    
    # Procesamiento
    procesado_exitosamente = models.BooleanField(db_column='procesado_ok', default=False)
    tiempo_procesamiento_ms = models.IntegerField(db_column='tiempo_proc_ms', null=True, blank=True)
    mensaje_error = models.TextField(db_column='error_msg', blank=True, null=True)
    
    # Metadatos
    ip_origen = models.GenericIPAddressField(db_column='ip_origen')
    user_agent = models.TextField(db_column='user_agent', blank=True, null=True)

    class Meta(ManagedModel.Meta):
        db_table = 'log_webhooks'
        verbose_name = 'Log de Webhook'
        verbose_name_plural = 'Logs de Webhooks'
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['procesado_exitosamente']),
            models.Index(fields=['webhook', 'timestamp'])
        ]

    def __str__(self):
        status = "✅" if self.procesado_exitosamente else "❌"
        return f'{status} Webhook {self.evento_tipo} - {self.timestamp.strftime("%d/%m/%Y %H:%M")}'