"""
Modelo para aceptación de términos y condiciones de saldo negativo

Este módulo contiene el modelo para registrar la aceptación
de términos legales por parte de los padres.

Autor: CantiTita
Fecha: 2026-01-12
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class AceptacionTerminosSaldoNegativo(models.Model):
    """
    Registro de aceptación de términos y condiciones
    para uso de saldo negativo
    """
    
    # Relaciones
    nro_tarjeta = models.ForeignKey(
        'Tarjeta',
        on_delete=models.CASCADE,
        db_column='nro_tarjeta',
        related_name='aceptaciones_terminos'
    )
    
    id_cliente = models.ForeignKey(
        'Cliente',
        on_delete=models.CASCADE,
        db_column='id_cliente',
        related_name='aceptaciones_terminos'
    )
    
    # Datos de aceptación
    fecha_aceptacion = models.DateTimeField(
        default=timezone.now,
        db_column='fecha_aceptacion'
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        db_column='ip_address',
        help_text='IP desde donde se aceptaron los términos'
    )
    
    user_agent = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        db_column='user_agent',
        help_text='Navegador usado'
    )
    
    # Contenido del documento aceptado
    version_terminos = models.CharField(
        max_length=20,
        default='1.0',
        db_column='version_terminos',
        help_text='Versión del documento de términos aceptado'
    )
    
    contenido_aceptado = models.TextField(
        db_column='contenido_aceptado',
        help_text='Texto completo de los términos aceptados'
    )
    
    # Firma digital (opcional)
    firma_digital = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        db_column='firma_digital',
        help_text='Hash SHA256 del contenido + timestamp'
    )
    
    # Flags
    activo = models.BooleanField(
        default=True,
        db_column='activo',
        help_text='Si esta aceptación está vigente'
    )
    
    revocado = models.BooleanField(
        default=False,
        db_column='revocado',
        help_text='Si el cliente revocó su aceptación'
    )
    
    fecha_revocacion = models.DateTimeField(
        null=True,
        blank=True,
        db_column='fecha_revocacion'
    )
    
    # Auditoría
    id_usuario_portal = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='id_usuario_portal',
        related_name='aceptaciones_terminos',
        help_text='Usuario del portal que aceptó'
    )
    
    class Meta:
        db_table = 'aceptacion_terminos_saldo_negativo'
        verbose_name = 'Aceptación de Términos'
        verbose_name_plural = 'Aceptaciones de Términos'
        indexes = [
            models.Index(fields=['nro_tarjeta', 'activo']),
            models.Index(fields=['id_cliente']),
            models.Index(fields=['fecha_aceptacion']),
        ]
    
    def __str__(self):
        return f"Aceptación {self.nro_tarjeta} - {self.fecha_aceptacion.strftime('%d/%m/%Y')}"
    
    def revocar(self):
        """Revocar la aceptación de términos"""
        self.revocado = True
        self.activo = False
        self.fecha_revocacion = timezone.now()
        self.save()
    
    def generar_firma_digital(self):
        """Generar hash SHA256 como firma digital"""
        import hashlib
        
        data = f"{self.nro_tarjeta.nro_tarjeta}|{self.contenido_aceptado}|{self.fecha_aceptacion.isoformat()}"
        firma = hashlib.sha256(data.encode()).hexdigest()
        
        self.firma_digital = firma
        self.save(update_fields=['firma_digital'])
        
        return firma


# Agregar este modelo al archivo models.py existente
# O importarlo desde aquí en models.py:
# from gestion.terminos_legales import AceptacionTerminosSaldoNegativo
