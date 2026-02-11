"""
Modelo de Notificaciones para el sistema
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class NotificacionSistema(models.Model):
    """
    Modelo para almacenar notificaciones del sistema
    """
    TIPO_CHOICES = [
        ('info', 'Información'),
        ('success', 'Éxito'),
        ('warning', 'Advertencia'),
        ('error', 'Error'),
        ('venta', 'Venta'),
        ('recarga', 'Recarga'),
        ('stock', 'Stock Bajo'),
        ('sistema', 'Sistema'),
    ]
    
    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('critica', 'Crítica'),
    ]
    
    # Destinatario
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notificaciones',
        help_text='Usuario que recibe la notificación'
    )
    
    # Contenido
    titulo = models.CharField(
        max_length=200,
        help_text='Título corto de la notificación'
    )
    
    mensaje = models.TextField(
        help_text='Mensaje completo de la notificación'
    )
    
    # Clasificación
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='info',
        help_text='Tipo de notificación'
    )
    
    prioridad = models.CharField(
        max_length=20,
        choices=PRIORIDAD_CHOICES,
        default='media',
        help_text='Prioridad de la notificación'
    )
    
    # Metadata
    icono = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text='Clase de ícono FontAwesome (ej: fa-bell)'
    )
    
    url = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text='URL de acción al hacer clic'
    )
    
    # Estado
    leida = models.BooleanField(
        default=False,
        help_text='¿La notificación ha sido leída?'
    )
    
    fecha_leida = models.DateTimeField(
        blank=True,
        null=True,
        help_text='Fecha y hora en que se leyó'
    )
    
    # Timestamps
    creada_en = models.DateTimeField(
        auto_now_add=True,
        help_text='Fecha de creación'
    )
    
    expira_en = models.DateTimeField(
        blank=True,
        null=True,
        help_text='Fecha de expiración (opcional)'
    )
    
    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-creada_en']
        indexes = [
            models.Index(fields=['usuario', '-creada_en']),
            models.Index(fields=['usuario', 'leida']),
            models.Index(fields=['tipo', '-creada_en']),
        ]
    
    def __str__(self):
        return f"{self.titulo} - {self.usuario.username}"
    
    def marcar_como_leida(self):
        """Marca la notificación como leída"""
        if not self.leida:
            self.leida = True
            self.fecha_leida = timezone.now()
            self.save(update_fields=['leida', 'fecha_leida'])
    
    def esta_expirada(self):
        """Verifica si la notificación ha expirado"""
        if self.expira_en:
            return timezone.now() > self.expira_en
        return False
    
    @staticmethod
    def crear_notificacion(usuario, titulo, mensaje, tipo='info', prioridad='media', **kwargs):
        """
        Método helper para crear notificaciones fácilmente
        
        Uso:
            Notificacion.crear_notificacion(
                usuario=request.user,
                titulo="Nueva venta",
                mensaje="Se realizó una venta de ₲ 50.000",
                tipo='venta',
                url='/pos/ventas/123/'
            )
        """
        return NotificacionSistema.objects.create(
            usuario=usuario,
            titulo=titulo,
            mensaje=mensaje,
            tipo=tipo,
            prioridad=prioridad,
            **kwargs
        )
    
    @staticmethod
    def get_no_leidas(usuario):
        """Obtiene todas las notificaciones no leídas de un usuario"""
        return NotificacionSistema.objects.filter(
            usuario=usuario,
            leida=False
        ).exclude(
            expira_en__lt=timezone.now()  # Excluir expiradas
        )
    
    @staticmethod
    def count_no_leidas(usuario):
        """Cuenta las notificaciones no leídas"""
        return NotificacionSistema.get_no_leidas(usuario).count()
    
    def to_dict(self):
        """Convierte la notificación a diccionario para JSON"""
        return {
            'id': self.id,
            'titulo': self.titulo,
            'mensaje': self.mensaje,
            'tipo': self.tipo,
            'prioridad': self.prioridad,
            'icono': self.icono or self._get_icono_default(),
            'url': self.url,
            'leida': self.leida,
            'creada_en': self.creada_en.isoformat(),
            'hace': self._tiempo_transcurrido(),
        }
    
    def _get_icono_default(self):
        """Retorna el ícono por defecto según el tipo"""
        iconos = {
            'info': 'fa-info-circle',
            'success': 'fa-check-circle',
            'warning': 'fa-exclamation-triangle',
            'error': 'fa-times-circle',
            'venta': 'fa-cash-register',
            'recarga': 'fa-credit-card',
            'stock': 'fa-box',
            'sistema': 'fa-server',
        }
        return iconos.get(self.tipo, 'fa-bell')
    
    def _tiempo_transcurrido(self):
        """Calcula el tiempo transcurrido desde la creación"""
        ahora = timezone.now()
        delta = ahora - self.creada_en
        
        if delta.days > 0:
            return f"hace {delta.days} día{'s' if delta.days > 1 else ''}"
        elif delta.seconds >= 3600:
            horas = delta.seconds // 3600
            return f"hace {horas} hora{'s' if horas > 1 else ''}"
        elif delta.seconds >= 60:
            minutos = delta.seconds // 60
            return f"hace {minutos} minuto{'s' if minutos > 1 else ''}"
        else:
            return "hace un momento"


class ConfiguracionNotificacionesSistema(models.Model):
    """
    Configuración de notificaciones por usuario
    """
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='config_notificaciones'
    )
    
    # Tipos de notificaciones habilitadas
    notif_ventas = models.BooleanField(
        default=True,
        verbose_name='Notificaciones de Ventas'
    )
    
    notif_recargas = models.BooleanField(
        default=True,
        verbose_name='Notificaciones de Recargas'
    )
    
    notif_stock = models.BooleanField(
        default=True,
        verbose_name='Notificaciones de Stock Bajo'
    )
    
    notif_sistema = models.BooleanField(
        default=True,
        verbose_name='Notificaciones del Sistema'
    )
    
    # Push notifications
    push_habilitado = models.BooleanField(
        default=False,
        verbose_name='Push Notifications Habilitadas'
    )
    
    push_subscription = models.JSONField(
        blank=True,
        null=True,
        verbose_name='Subscription de Push',
        help_text='Datos de suscripción del navegador'
    )
    
    # Preferencias
    solo_criticas = models.BooleanField(
        default=False,
        verbose_name='Solo Notificaciones Críticas',
        help_text='Recibir solo notificaciones de prioridad alta/crítica'
    )
    
    sonido_habilitado = models.BooleanField(
        default=True,
        verbose_name='Sonido de Notificaciones'
    )
    
    class Meta:
        verbose_name = 'Configuración de Notificaciones'
        verbose_name_plural = 'Configuraciones de Notificaciones'
    
    def __str__(self):
        return f"Config Notif - {self.usuario.username}"
    
    @staticmethod
    def get_or_create_for_user(usuario):
        """Obtiene o crea la configuración para un usuario"""
        config, created = ConfiguracionNotificacionesSistema.objects.get_or_create(
            usuario=usuario
        )
        return config
