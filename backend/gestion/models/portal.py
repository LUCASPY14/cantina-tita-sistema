# gestion/models/portal.py

from django.db import models
from django.utils import timezone
import sys
from .base import ManagedModel
from .clientes import Cliente
from .tarjetas import Tarjeta

class UsuariosWebClientes(ManagedModel):
    '''Tabla usuarios_web_clientes - Usuarios web para clientes'''
    id_cliente = models.OneToOneField(
        Cliente,
        on_delete=models.CASCADE,
        db_column='id_cliente',
        primary_key=True,
        related_name='usuario_web'
    )
    usuario = models.CharField(db_column='usuario', max_length=50, unique=True)
    contrasena_hash = models.CharField(db_column='contrasena_hash', max_length=128)
    ultimo_acceso = models.DateTimeField(db_column='ultimo_acceso', blank=True, null=True)
    activo = models.BooleanField(db_column='activo', default=True)

    class Meta(ManagedModel.Meta):
        db_table = 'usuarios_web_clientes'
        verbose_name = 'Usuario Web Cliente'
        verbose_name_plural = 'Usuarios Web Clientes'

    def __str__(self):
        return f'{self.usuario} ({self.id_cliente.nombre_completo})'


class UsuarioPortal(ManagedModel):
    """Usuario del portal web de padres
    Permite a los padres acceder al portal con email/contraseña"""
    
    id_usuario_portal = models.AutoField(db_column='id_usuario_portal', primary_key=True)
    cliente = models.OneToOneField(
        Cliente,
        on_delete=models.CASCADE,
        db_column='id_cliente',
        related_name='usuario_portal'
    )
    email = models.EmailField(db_column='email', unique=True, max_length=255)
    password_hash = models.CharField(db_column='password_hash', max_length=255)
    email_verificado = models.BooleanField(db_column='email_verificado', default=False)
    fecha_registro = models.DateTimeField(db_column='fecha_registro', auto_now_add=True)
    ultimo_acceso = models.DateTimeField(db_column='ultimo_acceso', null=True, blank=True)
    activo = models.BooleanField(db_column='activo', default=True)
    
    class Meta(ManagedModel.Meta):
        managed = True
        db_table = 'usuarios_portal'
        verbose_name = 'Usuario Portal'
        verbose_name_plural = 'Usuarios Portal'
    
    def __str__(self):
        return f'{self.email} - {self.cliente.nombres} {self.cliente.apellidos}'


class TokenVerificacion(ManagedModel):
    """Tokens para verificación de email y recuperación de contraseña"""
    
    TIPO_CHOICES = [
        ('email_verification', 'Verificación de Email'),
        ('password_reset', 'Recuperación de Contraseña'),
    ]
    
    id_token = models.AutoField(db_column='id_token', primary_key=True)
    usuario_portal = models.ForeignKey(
        UsuarioPortal,
        on_delete=models.CASCADE,
        db_column='id_usuario_portal',
        related_name='tokens'
    )
    token = models.CharField(db_column='token', max_length=100, unique=True)
    tipo = models.CharField(db_column='tipo', max_length=50, choices=TIPO_CHOICES)
    expira_en = models.DateTimeField(db_column='expira_en')
    usado = models.BooleanField(db_column='usado', default=False)
    fecha_creacion = models.DateTimeField(db_column='fecha_creacion', auto_now_add=True)
    fecha_uso = models.DateTimeField(db_column='fecha_uso', null=True, blank=True)
    
    class Meta(ManagedModel.Meta):
        managed = True
        db_table = 'tokens_verificacion'
        verbose_name = 'Token de Verificación'
        verbose_name_plural = 'Tokens de Verificación'
    
    def __str__(self):
        return f'{self.get_tipo_display()} - {self.usuario_portal.email}'
    
    def es_valido(self):
        """Verifica si el token es válido (no usado y no expirado)"""
        return not self.usado and self.expira_en > timezone.now()


class PreferenciaNotificacion(ManagedModel):
    """Preferencias de notificación de los usuarios del portal"""
    
    id_preferencia = models.AutoField(db_column='id_preferencia', primary_key=True)
    usuario_portal = models.ForeignKey(
        UsuarioPortal,
        on_delete=models.CASCADE,
        db_column='id_usuario_portal',
        related_name='preferencias_notificacion'
    )
    tipo_notificacion = models.CharField(db_column='tipo_notificacion', max_length=50)
    email_activo = models.BooleanField(db_column='email_activo', default=True)
    push_activo = models.BooleanField(db_column='push_activo', default=True)
    creado_en = models.DateTimeField(db_column='creado_en', auto_now_add=True)
    actualizado_en = models.DateTimeField(db_column='actualizado_en', auto_now=True)
    
    class Meta(ManagedModel.Meta):
        managed = True
        db_table = 'preferencia_notificacion'
        verbose_name = 'Preferencia de Notificación'
        verbose_name_plural = 'Preferencias de Notificación'
        constraints = [
            models.UniqueConstraint(
                fields=['usuario_portal', 'tipo_notificacion'],
                name='unique_usuario_tipo'
            )
        ]
    
    def __str__(self):
        return f'Preferencias de {self.usuario_portal.email} - {self.tipo_notificacion}'


class Notificacion(ManagedModel):
    """Notificaciones para usuarios del portal de padres"""
    
    TIPO_CHOICES = [
        ('saldo_bajo', 'Saldo Bajo'),
        ('recarga_exitosa', 'Recarga Exitosa'),
        ('consumo_realizado', 'Consumo Realizado'),
        ('tarjeta_bloqueada', 'Tarjeta Bloqueada'),
        ('restriccion_aplicada', 'Restricción Aplicada'),
        ('info_general', 'Información General'),
    ]
    
    id_notificacion = models.AutoField(db_column='id_notificacion', primary_key=True)
    usuario_portal = models.ForeignKey(
        UsuarioPortal,
        on_delete=models.CASCADE,
        db_column='id_usuario_portal',
        related_name='notificaciones'
    )
    tipo = models.CharField(db_column='tipo', max_length=50, choices=TIPO_CHOICES)
    titulo = models.CharField(db_column='titulo', max_length=255)
    mensaje = models.TextField(db_column='mensaje')
    leida = models.BooleanField(db_column='leida', default=False)
    fecha_envio = models.DateTimeField(db_column='fecha_envio', default=timezone.now)
    fecha_lectura = models.DateTimeField(db_column='fecha_lectura', null=True, blank=True)
    creado_en = models.DateTimeField(db_column='creado_en', auto_now_add=True)
    
    class Meta(ManagedModel.Meta):
        managed = True
        db_table = 'notificacion'
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-fecha_envio']
    
    def __str__(self):
        return f'{self.get_tipo_display()} - {self.usuario_portal.email} - {self.titulo}'
    
    def marcar_como_leida(self):
        """Marca la notificación como leída"""
        if not self.leida:
            self.leida = True
            self.fecha_lectura = timezone.now()
            self.save()


class NotificacionSaldo(ManagedModel):
    """Registro de notificaciones de saldo enviadas a padres"""
    
    TIPO_NOTIFICACION_CHOICES = [
        ('SALDO_BAJO', 'Saldo Bajo'),
        ('SALDO_NEGATIVO', 'Saldo Negativo'),
        ('SALDO_CRITICO', 'Saldo Crítico'),
        ('REGULARIZADO', 'Saldo Regularizado'),
    ]
    
    id_notificacion = models.BigAutoField(db_column='id_notificacion', primary_key=True)
    nro_tarjeta = models.ForeignKey(
        Tarjeta,
        on_delete=models.CASCADE,
        db_column='nro_tarjeta',
        related_name='notificaciones_saldo'
    )
    tipo_notificacion = models.CharField(
        db_column='tipo_notificacion',
        max_length=50,
        choices=TIPO_NOTIFICACION_CHOICES
    )
    saldo_actual = models.BigIntegerField(db_column='saldo_actual')
    mensaje = models.TextField(db_column='mensaje')
    enviada_email = models.BooleanField(db_column='enviada_email', default=False)
    enviada_sms = models.BooleanField(db_column='enviada_sms', default=False)
    leida = models.BooleanField(db_column='leida', default=False)
    email_destinatario = models.EmailField(db_column='email_destinatario', blank=True, null=True)
    fecha_creacion = models.DateTimeField(db_column='fecha_creacion', auto_now_add=True)
    fecha_envio = models.DateTimeField(db_column='fecha_envio', blank=True, null=True)
    
    class Meta(ManagedModel.Meta):
        managed = 'test' not in sys.argv
        db_table = 'notificacion_saldo'
        verbose_name = 'Notificación de Saldo'
        verbose_name_plural = 'Notificaciones de Saldo'
        indexes = [
            models.Index(fields=['nro_tarjeta', 'tipo_notificacion'], name='idx_tarjeta_tipo_not'),
            models.Index(fields=['leida'], name='idx_leida_not'),
            models.Index(fields=['fecha_creacion'], name='idx_fecha_creacion_not'),
        ]
    
    def __str__(self):
        return f'{self.get_tipo_notificacion_display()} - {self.nro_tarjeta} - {self.fecha_creacion.strftime("%d/%m/%Y %H:%M")}'


class SolicitudesNotificacion(ManagedModel):
    '''Tabla solicitudes_notificacion - Solicitudes de notificación'''
    DESTINO_CHOICES = [
        ('SMS', 'SMS'),
        ('Email', 'Email'),
        ('WhatsApp', 'WhatsApp'),
    ]

    ESTADO_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('Enviada', 'Enviada'),
        ('Fallida', 'Fallida'),
    ]

    id_solicitud = models.BigAutoField(db_column='id_solicitud', primary_key=True)
    id_cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        db_column='id_cliente',
        related_name='notificaciones'
    )
    nro_tarjeta = models.ForeignKey(
        Tarjeta,
        on_delete=models.CASCADE,
        db_column='nro_tarjeta'
    )
    saldo_alerta = models.DecimalField(db_column='saldo_alerta', max_digits=10, decimal_places=2)
    mensaje = models.CharField(db_column='mensaje', max_length=255)
    destino = models.CharField(db_column='destino', max_length=8, choices=DESTINO_CHOICES)
    estado = models.CharField(db_column='estado', max_length=9, choices=ESTADO_CHOICES, blank=True, null=True)
    fecha_solicitud = models.DateTimeField(db_column='fecha_solicitud')
    fecha_envio = models.DateTimeField(db_column='fecha_envio', blank=True, null=True)

    class Meta(ManagedModel.Meta):
        db_table = 'solicitudes_notificacion'
        verbose_name = 'Solicitud de Notificación'
        verbose_name_plural = 'Solicitudes de Notificación'

    def __str__(self):
        return f'{self.id_cliente.nombre_completo} - {self.destino} - {self.estado}'


class TransaccionOnline(ManagedModel):
    """Transacciones de pago online realizadas desde el portal de padres"""
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('completado', 'Completado'),
        ('fallido', 'Fallido'),
        ('cancelado', 'Cancelado'),
    ]
    
    METODO_PAGO_CHOICES = [
        ('metrepay', 'MetrePay'),
        ('tigo_money', 'Tigo Money'),
    ]
    
    id_transaccion = models.AutoField(db_column='id_transaccion', primary_key=True)
    nro_tarjeta = models.ForeignKey(
        Tarjeta,
        on_delete=models.SET_NULL,
        db_column='nro_tarjeta',
        to_field='nro_tarjeta',
        related_name='transacciones_online',
        null=True,
        blank=True
    )
    usuario_portal = models.ForeignKey(
        UsuarioPortal,
        on_delete=models.SET_NULL,
        db_column='id_usuario_portal',
        related_name='transacciones',
        null=True,
        blank=True
    )
    monto = models.BigIntegerField(db_column='monto')
    metodo_pago = models.CharField(db_column='metodo_pago', max_length=20, choices=METODO_PAGO_CHOICES)
    estado = models.CharField(db_column='estado', max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    referencia_pago = models.CharField(db_column='referencia_pago', max_length=255, null=True, blank=True)
    id_transaccion_externa = models.CharField(db_column='id_transaccion_externa', max_length=255, null=True, blank=True)
    datos_extra = models.TextField(db_column='datos_extra', null=True, blank=True)
    fecha_transaccion = models.DateTimeField(db_column='fecha_transaccion')
    creado_en = models.DateTimeField(db_column='creado_en', auto_now_add=True)
    actualizado_en = models.DateTimeField(db_column='actualizado_en', auto_now=True)
    
    class Meta(ManagedModel.Meta):
        managed = True
        db_table = 'transaccion_online'
        verbose_name = 'Transacción Online'
        verbose_name_plural = 'Transacciones Online'
        ordering = ['-fecha_transaccion']
    
    def __str__(self):
        return f'Transacción #{self.id_transaccion} - {self.get_metodo_pago_display()} - Gs. {self.monto:,.0f}'


class AlertasSistema(ManagedModel):
    '''Tabla alertas_sistema - Alertas del sistema'''
    TIPO_CHOICES = [
        ('Stock Bajo', 'Stock Bajo'),
        ('Saldo Bajo', 'Saldo Bajo'),
        ('Timbrado Próximo a Vencer', 'Timbrado Próximo a Vencer'),
        ('Sistema', 'Sistema'),
    ]

    ESTADO_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('Leída', 'Leída'),
        ('Resuelta', 'Resuelta'),
    ]

    id_alerta = models.BigAutoField(db_column='id_alerta', primary_key=True)
    tipo = models.CharField(db_column='tipo', max_length=30, choices=TIPO_CHOICES)
    mensaje = models.CharField(db_column='mensaje', max_length=500)
    fecha_creacion = models.DateTimeField(db_column='fecha_creacion')
    fecha_leida = models.DateTimeField(db_column='fecha_leida', blank=True, null=True)
    estado = models.CharField(db_column='estado', max_length=9, choices=ESTADO_CHOICES, blank=True, null=True)
    id_empleado_resuelve = models.BigIntegerField(db_column='id_empleado_resuelve', blank=True, null=True)
    fecha_resolucion = models.DateTimeField(db_column='fecha_resolucion', blank=True, null=True)
    observaciones = models.TextField(db_column='observaciones', blank=True, null=True)

    class Meta(ManagedModel.Meta):
        db_table = 'alertas_sistema'
        verbose_name = 'Alerta del Sistema'
        verbose_name_plural = 'Alertas del Sistema'

    def __str__(self):
        return f'{self.tipo} - {self.estado}'