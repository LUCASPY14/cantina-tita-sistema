# gestion/models/seguridad.py

from django.db import models
from django.utils import timezone
from .base import ManagedModel
from .clientes import Cliente, Hijo
from .empleados import Empleado
from .catalogos import TarifasComision
from .productos import Producto, MovimientosStock
from .tarjetas import Tarjeta

class TarjetaAutorizacion(ManagedModel):
    '''Tabla tarjetas_autorizacion - Tarjetas para autorizar operaciones críticas'''
    TIPO_AUTORIZACION_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('SUPERVISOR', 'Supervisor'),
        ('CAJERO', 'Cajero'),
    ]
    
    id_tarjeta_autorizacion = models.AutoField(db_column='ID_Tarjeta_Autorizacion', primary_key=True)
    codigo_barra = models.CharField(db_column='Codigo_Barra', max_length=50, unique=True)
    id_empleado = models.ForeignKey(
        Empleado,
        on_delete=models.SET_NULL,
        db_column='ID_Empleado',
        blank=True,
        null=True
    )
    tipo_autorizacion = models.CharField(
        db_column='Tipo_Autorizacion',
        max_length=15,
        choices=TIPO_AUTORIZACION_CHOICES,
        default='ADMIN'
    )
    puede_anular_almuerzos = models.BooleanField(db_column='Puede_Anular_Almuerzos', default=True)
    puede_anular_ventas = models.BooleanField(db_column='Puede_Anular_Ventas', default=True)
    puede_anular_recargas = models.BooleanField(db_column='Puede_Anular_Recargas', default=True)
    puede_modificar_precios = models.BooleanField(db_column='Puede_Modificar_Precios', default=False)
    activo = models.BooleanField(db_column='Activo', default=True)
    fecha_creacion = models.DateTimeField(db_column='Fecha_Creacion', auto_now_add=True)
    fecha_vencimiento = models.DateField(db_column='Fecha_Vencimiento', blank=True, null=True)
    observaciones = models.TextField(db_column='Observaciones', blank=True, null=True)
    
    class Meta(ManagedModel.Meta):
        db_table = 'tarjetas_autorizacion'
        verbose_name = 'Tarjeta de Autorización'
        verbose_name_plural = 'Tarjetas de Autorización'
    
    def __str__(self):
        empleado_info = f' - {self.id_empleado.nombre_completo}' if self.id_empleado else ''
        return f'{self.codigo_barra} ({self.get_tipo_autorizacion_display()}){empleado_info}'
    
    def tiene_permiso(self, tipo_operacion):
        '''Verifica si la tarjeta tiene permiso para una operación'''
        if not self.activo:
            return False
        
        if self.fecha_vencimiento and self.fecha_vencimiento < timezone.now().date():
            return False
        
        permisos = {
            'ANULAR_ALMUERZO': self.puede_anular_almuerzos,
            'ANULAR_VENTA': self.puede_anular_ventas,
            'ANULAR_RECARGA': self.puede_anular_recargas,
            'MODIFICAR_PRECIO': self.puede_modificar_precios,
        }
        
        return permisos.get(tipo_operacion, False)


class LogAutorizacion(ManagedModel):
    '''Tabla log_autorizaciones - Registro de todas las autorizaciones realizadas'''
    TIPO_OPERACION_CHOICES = [
        ('ANULAR_ALMUERZO', 'Anular Almuerzo'),
        ('ANULAR_VENTA', 'Anular Venta'),
        ('ANULAR_RECARGA', 'Anular Recarga'),
        ('MODIFICAR_PRECIO', 'Modificar Precio'),
        ('OTRO', 'Otro'),
    ]
    
    RESULTADO_CHOICES = [
        ('EXITOSO', 'Exitoso'),
        ('RECHAZADO', 'Rechazado'),
        ('ERROR', 'Error'),
    ]
    
    id_log = models.BigAutoField(db_column='ID_Log', primary_key=True)
    id_tarjeta_autorizacion = models.ForeignKey(
        TarjetaAutorizacion,
        on_delete=models.CASCADE,
        db_column='ID_Tarjeta_Autorizacion'
    )
    codigo_barra = models.CharField(db_column='Codigo_Barra', max_length=50)
    tipo_operacion = models.CharField(
        db_column='Tipo_Operacion',
        max_length=20,
        choices=TIPO_OPERACION_CHOICES
    )
    id_registro_afectado = models.BigIntegerField(db_column='ID_Registro_Afectado', blank=True, null=True)
    descripcion = models.TextField(db_column='Descripcion', blank=True, null=True)
    id_usuario = models.IntegerField(db_column='ID_Usuario', blank=True, null=True)
    fecha_hora = models.DateTimeField(db_column='Fecha_Hora', auto_now_add=True)
    ip_origen = models.CharField(db_column='IP_Origen', max_length=45, blank=True, null=True)
    resultado = models.CharField(
        db_column='Resultado',
        max_length=15,
        choices=RESULTADO_CHOICES,
        default='EXITOSO'
    )
    
    class Meta(ManagedModel.Meta):
        db_table = 'log_autorizaciones'
        verbose_name = 'Log de Autorización'
        verbose_name_plural = 'Logs de Autorizaciones'
        ordering = ['-fecha_hora']
    
    def __str__(self):
        return f'{self.get_tipo_operacion_display()} - {self.fecha_hora.strftime("%d/%m/%Y %H:%M")}'


class HistorialGradoHijo(ManagedModel):
    '''Tabla historial_grados_hijos - Registro de cambios de grado'''
    MOTIVO_CHOICES = [
        ('INGRESO', 'Ingreso'),
        ('PROMOCION', 'Promoción'),
        ('CAMBIO_MANUAL', 'Cambio Manual'),
        ('REINGRESO', 'Reingreso'),
    ]
    
    id_historial = models.AutoField(db_column='ID_Historial', primary_key=True)
    id_hijo = models.ForeignKey(
        Hijo,
        on_delete=models.CASCADE,
        db_column='ID_Hijo',
        related_name='historial_grados'
    )
    grado_anterior = models.CharField(db_column='Grado_Anterior', max_length=50, blank=True, null=True)
    grado_nuevo = models.CharField(db_column='Grado_Nuevo', max_length=50)
    anio_escolar = models.IntegerField(db_column='Anio_Escolar')
    fecha_cambio = models.DateTimeField(db_column='Fecha_Cambio', auto_now_add=True)
    motivo = models.CharField(
        db_column='Motivo',
        max_length=20,
        choices=MOTIVO_CHOICES,
        default='PROMOCION'
    )
    usuario_registro = models.CharField(db_column='Usuario_Registro', max_length=100, blank=True, null=True)
    observaciones = models.TextField(db_column='Observaciones', blank=True, null=True)
    
    class Meta(ManagedModel.Meta):
        db_table = 'historial_grados_hijos'
        verbose_name = 'Historial de Grado'
        verbose_name_plural = 'Historial de Grados'
        ordering = ['-fecha_cambio']
    
    def __str__(self):
        return f'{self.id_hijo.nombre_completo} - {self.grado_nuevo} ({self.anio_escolar})'


class IntentoLogin(ManagedModel):
    '''Tabla intentos_login - Rate limiting y seguridad'''
    id_intento = models.AutoField(db_column='ID_Intento', primary_key=True)
    usuario = models.CharField(db_column='Usuario', max_length=100)
    ip_address = models.CharField(db_column='IP_Address', max_length=45)
    ciudad = models.CharField(db_column='Ciudad', max_length=100, blank=True, null=True)
    pais = models.CharField(db_column='Pais', max_length=100, blank=True, null=True)
    fecha_intento = models.DateTimeField(db_column='Fecha_Intento')
    exitoso = models.BooleanField(db_column='Exitoso', default=False)
    motivo_fallo = models.CharField(db_column='Motivo_Fallo', max_length=100, blank=True, null=True)
    
    class Meta(ManagedModel.Meta):
        db_table = 'intentos_login'
        verbose_name = 'Intento de Login'
        verbose_name_plural = 'Intentos de Login'
        ordering = ['-fecha_intento']
    
    def __str__(self):
        estado = "✓" if self.exitoso else "✗"
        ubicacion = f" ({self.ciudad}, {self.pais})" if self.ciudad and self.pais else ""
        return f'{estado} {self.usuario}{ubicacion} - {self.fecha_intento}'


class AuditoriaOperacion(ManagedModel):
    '''Tabla auditoria_operaciones - Logging completo del sistema'''
    TIPO_USUARIO_CHOICES = [
        ('EMPLEADO', 'Empleado'),
        ('CLIENTE_WEB', 'Cliente Web'),
        ('ADMIN', 'Administrador'),
    ]
    
    RESULTADO_CHOICES = [
        ('EXITOSO', 'Exitoso'),
        ('FALLIDO', 'Fallido'),
    ]
    
    id_auditoria = models.AutoField(db_column='ID_Auditoria', primary_key=True)
    usuario = models.CharField(db_column='Usuario', max_length=100)
    tipo_usuario = models.CharField(db_column='Tipo_Usuario', max_length=20, choices=TIPO_USUARIO_CHOICES)
    id_usuario = models.IntegerField(db_column='ID_Usuario', blank=True, null=True)
    operacion = models.CharField(db_column='Operacion', max_length=100)
    tabla_afectada = models.CharField(db_column='Tabla_Afectada', max_length=100, blank=True, null=True)
    id_registro = models.IntegerField(db_column='ID_Registro', blank=True, null=True)
    descripcion = models.TextField(db_column='Descripcion', blank=True, null=True)
    datos_anteriores = models.JSONField(db_column='Datos_Anteriores', blank=True, null=True)
    datos_nuevos = models.JSONField(db_column='Datos_Nuevos', blank=True, null=True)
    ip_address = models.CharField(db_column='IP_Address', max_length=45, blank=True, null=True)
    ciudad = models.CharField(db_column='Ciudad', max_length=100, blank=True, null=True)
    pais = models.CharField(db_column='Pais', max_length=100, blank=True, null=True)
    user_agent = models.TextField(db_column='User_Agent', blank=True, null=True)
    fecha_operacion = models.DateTimeField(db_column='Fecha_Operacion')
    resultado = models.CharField(db_column='Resultado', max_length=20, choices=RESULTADO_CHOICES)
    mensaje_error = models.TextField(db_column='Mensaje_Error', blank=True, null=True)
    
    class Meta(ManagedModel.Meta):
        db_table = 'auditoria_operaciones'
        verbose_name = 'Auditoría de Operación'
        verbose_name_plural = 'Auditoría de Operaciones'
        ordering = ['-fecha_operacion']
    
    def __str__(self):
        ubicacion = f" ({self.ciudad}, {self.pais})" if self.ciudad and self.pais else ""
        return f'{self.operacion} por {self.usuario}{ubicacion} - {self.fecha_operacion}'


class AuditoriaEmpleados(ManagedModel):
    '''Tabla auditoria_empleados - Auditoría de acciones de empleados'''
    id_auditoria = models.BigAutoField(db_column='ID_Auditoria', primary_key=True)
    id_empleado = models.ForeignKey(
        Empleado,
        on_delete=models.SET_NULL,
        db_column='ID_Empleado',
        related_name='auditorias',
        null=True,
        blank=True
    )
    fecha_cambio = models.DateTimeField(db_column='Fecha_Cambio')
    campo_modificado = models.CharField(db_column='Campo_Modificado', max_length=50)
    valor_anterior = models.TextField(db_column='Valor_Anterior', blank=True, null=True)
    valor_nuevo = models.TextField(db_column='Valor_Nuevo', blank=True, null=True)
    ip_origen = models.CharField(db_column='IP_Origen', max_length=45, blank=True, null=True)

    class Meta(ManagedModel.Meta):
        db_table = 'auditoria_empleados'
        verbose_name = 'Auditoría de Empleado'
        verbose_name_plural = 'Auditorías de Empleados'

    def __str__(self):
        return f'{self.id_empleado.nombre_completo} - {self.campo_modificado} ({self.fecha_cambio})'


class AuditoriaComisiones(ManagedModel):
    '''Tabla auditoria_comisiones - Auditoría de cálculos de comisiones'''
    id_auditoria = models.BigAutoField(db_column='ID_Auditoria', primary_key=True)
    id_tarifa = models.ForeignKey(
        TarifasComision,
        on_delete=models.SET_NULL,
        db_column='ID_Tarifa',
        null=True,
        blank=True
    )
    fecha_cambio = models.DateTimeField(db_column='Fecha_Cambio')
    campo_modificado = models.CharField(db_column='Campo_Modificado', max_length=50)
    valor_anterior = models.DecimalField(db_column='Valor_Anterior', max_digits=10, decimal_places=4, blank=True, null=True)
    valor_nuevo = models.DecimalField(db_column='Valor_Nuevo', max_digits=10, decimal_places=4, blank=True, null=True)
    id_empleado_modifico = models.ForeignKey(
        Empleado,
        on_delete=models.SET_NULL,
        db_column='ID_Empleado_Modifico',
        blank=True,
        null=True
    )

    class Meta(ManagedModel.Meta):
        db_table = 'auditoria_comisiones'
        verbose_name = 'Auditoría de Comisión'
        verbose_name_plural = 'Auditorías de Comisiones'

    def __str__(self):
        return f'Auditoría Comisión #{self.id_tarifa_id}'


class AuditoriaUsuariosWeb(ManagedModel):
    '''Tabla auditoria_usuarios_web - Auditoría de usuarios web'''
    id_auditoria = models.BigAutoField(db_column='ID_Auditoria', primary_key=True)
    id_cliente = models.ForeignKey(
        Cliente,
        on_delete=models.SET_NULL,
        db_column='ID_Cliente',
        related_name='auditorias_web',
        null=True,
        blank=True
    )
    fecha_cambio = models.DateTimeField(db_column='Fecha_Cambio')
    campo_modificado = models.CharField(db_column='Campo_Modificado', max_length=50)
    valor_anterior = models.TextField(db_column='Valor_Anterior', blank=True, null=True)
    valor_nuevo = models.TextField(db_column='Valor_Nuevo', blank=True, null=True)
    ip_origen = models.CharField(db_column='IP_Origen', max_length=45, blank=True, null=True)

    class Meta(ManagedModel.Meta):
        db_table = 'auditoria_usuarios_web'
        verbose_name = 'Auditoría de Usuario Web'
        verbose_name_plural = 'Auditorías de Usuarios Web'

    def __str__(self):
        return f'{self.id_cliente.nombre_completo} - {self.campo_modificado} ({self.fecha_cambio})'


class TokenRecuperacion(ManagedModel):
    '''Tabla tokens_recuperacion - Tokens para reset de contraseña'''
    id_token = models.AutoField(db_column='ID_Token', primary_key=True)
    id_cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        db_column='ID_Cliente'
    )
    token = models.CharField(db_column='Token', max_length=64, unique=True)
    fecha_creacion = models.DateTimeField(db_column='Fecha_Creacion')
    fecha_expiracion = models.DateTimeField(db_column='Fecha_Expiracion')
    usado = models.BooleanField(db_column='Usado', default=False)
    fecha_uso = models.DateTimeField(db_column='Fecha_Uso', blank=True, null=True)
    ip_solicitud = models.CharField(db_column='IP_Solicitud', max_length=45, blank=True, null=True)
    
    class Meta(ManagedModel.Meta):
        db_table = 'tokens_recuperacion'
        verbose_name = 'Token de Recuperación'
        verbose_name_plural = 'Tokens de Recuperación'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f'Token para {self.id_cliente.nombre_completo} - {self.fecha_creacion}'


class BloqueoCuenta(ManagedModel):
    '''Tabla bloqueos_cuenta - Gestión de bloqueos de seguridad'''
    TIPO_USUARIO_CHOICES = [
        ('EMPLEADO', 'Empleado'),
        ('CLIENTE_WEB', 'Cliente Web'),
    ]
    
    id_bloqueo = models.AutoField(db_column='ID_Bloqueo', primary_key=True)
    usuario = models.CharField(db_column='Usuario', max_length=100)
    tipo_usuario = models.CharField(db_column='Tipo_Usuario', max_length=20, choices=TIPO_USUARIO_CHOICES)
    motivo = models.CharField(db_column='Motivo', max_length=255)
    fecha_bloqueo = models.DateTimeField(db_column='Fecha_Bloqueo')
    fecha_desbloqueo = models.DateTimeField(db_column='Fecha_Desbloqueo', blank=True, null=True)
    bloqueado_por = models.CharField(db_column='Bloqueado_Por', max_length=100, blank=True, null=True)
    ip_address = models.CharField(db_column='IP_Address', max_length=45, blank=True, null=True)
    activo = models.BooleanField(db_column='Activo', default=True)
    
    class Meta(ManagedModel.Meta):
        db_table = 'bloqueos_cuenta'
        verbose_name = 'Bloqueo de Cuenta'
        verbose_name_plural = 'Bloqueos de Cuentas'
        ordering = ['-fecha_bloqueo']
    
    def __str__(self):
        estado = "🔒 Activo" if self.activo else "🔓 Desbloqueado"
        return f'{estado} - {self.usuario} - {self.motivo}'


class AnomaliaDetectada(ManagedModel):
    '''Tabla anomalias_detectadas - Anomalías de seguridad'''
    TIPO_ANOMALIA_CHOICES = [
        ('IP_NUEVA', 'IP Nueva'),
        ('HORARIO_INUSUAL', 'Horario Inusual'),
        ('MULTIPLES_SESIONES', 'Múltiples Sesiones'),
        ('UBICACION_SOSPECHOSA', 'Ubicación Sospechosa'),
    ]
    
    NIVEL_RIESGO_CHOICES = [
        ('BAJO', 'Bajo'),
        ('MEDIO', 'Medio'),
        ('ALTO', 'Alto'),
    ]
    
    id_anomalia = models.AutoField(db_column='ID_Anomalia', primary_key=True)
    usuario = models.CharField(db_column='Usuario', max_length=100)
    tipo_anomalia = models.CharField(db_column='Tipo_Anomalia', max_length=30, choices=TIPO_ANOMALIA_CHOICES)
    ip_address = models.CharField(db_column='IP_Address', max_length=45, blank=True, null=True)
    fecha_deteccion = models.DateTimeField(db_column='Fecha_Deteccion')
    descripcion = models.TextField(db_column='Descripcion', blank=True, null=True)
    nivel_riesgo = models.CharField(db_column='Nivel_Riesgo', max_length=10, choices=NIVEL_RIESGO_CHOICES, default='MEDIO')
    notificado = models.BooleanField(db_column='Notificado', default=False)
    
    class Meta(ManagedModel.Meta):
        db_table = 'anomalias_detectadas'
        verbose_name = 'Anomalía Detectada'
        verbose_name_plural = 'Anomalías Detectadas'
        ordering = ['-fecha_deteccion']
    
    def __str__(self):
        return f'{self.tipo_anomalia} - {self.usuario} - {self.nivel_riesgo}'


class PatronAcceso(ManagedModel):
    '''Tabla patrones_acceso - Patrones habituales de acceso'''
    TIPO_USUARIO_CHOICES = [
        ('EMPLEADO', 'Empleado'),
        ('CLIENTE_WEB', 'Cliente Web'),
        ('ADMIN', 'Administrador'),
    ]
    
    id_patron = models.AutoField(db_column='ID_Patron', primary_key=True)
    usuario = models.CharField(db_column='Usuario', max_length=100)
    tipo_usuario = models.CharField(db_column='Tipo_Usuario', max_length=20, choices=TIPO_USUARIO_CHOICES)
    ip_address = models.CharField(db_column='IP_Address', max_length=45)
    horario_inicio = models.TimeField(db_column='Horario_Inicio', blank=True, null=True)
    horario_fin = models.TimeField(db_column='Horario_Fin', blank=True, null=True)
    dias_semana = models.CharField(db_column='Dias_Semana', max_length=50, blank=True, null=True)
    primera_deteccion = models.DateTimeField(db_column='Primera_Deteccion')
    ultima_deteccion = models.DateTimeField(db_column='Ultima_Deteccion')
    frecuencia_accesos = models.IntegerField(db_column='Frecuencia_Accesos', default=1)
    es_habitual = models.BooleanField(db_column='Es_Habitual', default=False)
    
    class Meta(ManagedModel.Meta):
        db_table = 'patrones_acceso'
        verbose_name = 'Patrón de Acceso'
        verbose_name_plural = 'Patrones de Acceso'
        ordering = ['-ultima_deteccion']
    
    def __str__(self):
        return f'{self.usuario} - {self.ip_address} ({self.frecuencia_accesos} accesos)'


class Autenticacion2Fa(ManagedModel):
    '''Tabla autenticacion_2fa - Autenticación de dos factores (2FA)'''
    TIPO_USUARIO_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('CAJERO', 'Cajero'),
        ('CLIENTE_WEB', 'Cliente Web'),
    ]
    
    id_2fa = models.AutoField(db_column='ID_2FA', primary_key=True)
    usuario = models.CharField(db_column='Usuario', max_length=100)
    tipo_usuario = models.CharField(db_column='Tipo_Usuario', max_length=20, choices=TIPO_USUARIO_CHOICES)
    secret_key = models.CharField(db_column='Secret_Key', max_length=32, help_text='Clave secreta TOTP codificada en Base32')
    backup_codes = models.TextField(db_column='Backup_Codes', blank=True, null=True, help_text='Códigos de respaldo JSON (array de strings hasheados)')
    habilitado = models.BooleanField(db_column='Habilitado', default=False, help_text='Si el usuario tiene 2FA activo')
    fecha_activacion = models.DateTimeField(db_column='Fecha_Activacion', blank=True, null=True, help_text='Cuando se activó por primera vez')
    ultima_verificacion = models.DateTimeField(db_column='Ultima_Verificacion', blank=True, null=True, help_text='Último uso exitoso del código')
    fecha_creacion = models.DateTimeField(db_column='Fecha_Creacion', auto_now_add=True)
    
    class Meta(ManagedModel.Meta):
        db_table = 'autenticacion_2fa'
        verbose_name = 'Autenticación 2FA'
        verbose_name_plural = 'Autenticaciones 2FA'
        unique_together = [['usuario', 'tipo_usuario']]
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        estado = "✅ Habilitado" if self.habilitado else "❌ Deshabilitado"
        return f'{self.usuario} ({self.tipo_usuario}) - 2FA {estado}'


class Intento2Fa(ManagedModel):
    '''Tabla intentos_2fa - Registro de intentos de verificación 2FA'''
    TIPO_USUARIO_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('CAJERO', 'Cajero'),
        ('CLIENTE_WEB', 'Cliente Web'),
    ]
    
    TIPO_CODIGO_CHOICES = [
        ('TOTP', 'TOTP'),
        ('BACKUP', 'Código de Respaldo'),
    ]
    
    id_intento = models.AutoField(db_column='ID_Intento', primary_key=True)
    usuario = models.CharField(db_column='Usuario', max_length=100)
    tipo_usuario = models.CharField(db_column='Tipo_Usuario', max_length=20, choices=TIPO_USUARIO_CHOICES)
    ip_address = models.CharField(db_column='IP_Address', max_length=45, blank=True, null=True)
    ciudad = models.CharField(db_column='Ciudad', max_length=100, blank=True, null=True)
    pais = models.CharField(db_column='Pais', max_length=100, blank=True, null=True)
    codigo_ingresado = models.CharField(db_column='Codigo_Ingresado', max_length=10, blank=True, null=True)
    exitoso = models.BooleanField(db_column='Exitoso', default=False)
    tipo_codigo = models.CharField(db_column='Tipo_Codigo', max_length=10, choices=TIPO_CODIGO_CHOICES, blank=True, null=True)
    fecha_intento = models.DateTimeField(db_column='Fecha_Intento', auto_now_add=True)
    
    class Meta(ManagedModel.Meta):
        db_table = 'intentos_2fa'
        verbose_name = 'Intento 2FA'
        verbose_name_plural = 'Intentos 2FA'
        ordering = ['-fecha_intento']
    
    def __str__(self):
        estado = '✓' if self.exitoso else '✗'
        ubicacion = f' ({self.ciudad}, {self.pais})' if self.ciudad and self.pais else ''
        return f'{estado} {self.usuario}{ubicacion} - {self.fecha_intento}'


class SesionActiva(ManagedModel):
    '''Tabla sesiones_activas - Control de sesiones activas'''
    TIPO_USUARIO_CHOICES = [
        ('EMPLEADO', 'Empleado'),
        ('CLIENTE_WEB', 'Cliente Web'),
        ('ADMIN', 'Administrador'),
    ]
    
    id_sesion = models.AutoField(db_column='ID_Sesion', primary_key=True)
    usuario = models.CharField(db_column='Usuario', max_length=100)
    tipo_usuario = models.CharField(db_column='Tipo_Usuario', max_length=20, choices=TIPO_USUARIO_CHOICES)
    session_key = models.CharField(db_column='Session_Key', max_length=255, unique=True)
    ip_address = models.CharField(db_column='IP_Address', max_length=45, blank=True, null=True)
    user_agent = models.TextField(db_column='User_Agent', blank=True, null=True)
    fecha_inicio = models.DateTimeField(db_column='Fecha_Inicio')
    ultima_actividad = models.DateTimeField(db_column='Ultima_Actividad')
    activa = models.BooleanField(db_column='Activa', default=True)
    
    class Meta(ManagedModel.Meta):
        db_table = 'sesiones_activas'
        verbose_name = 'Sesión Activa'
        verbose_name_plural = 'Sesiones Activas'
        ordering = ['-ultima_actividad']
    
    def __str__(self):
        estado = "🟢 Activa" if self.activa else "🔴 Cerrada"
        return f'{estado} - {self.usuario} - {self.ip_address}'


class RestriccionHoraria(ManagedModel):
    '''Tabla restricciones_horarias - Control de acceso por horarios'''
    TIPO_USUARIO_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('CAJERO', 'Cajero'),
        ('CLIENTE_WEB', 'Cliente Web'),
    ]
    
    DIA_SEMANA_CHOICES = [
        ('LUNES', 'Lunes'),
        ('MARTES', 'Martes'),
        ('MIERCOLES', 'Miércoles'),
        ('JUEVES', 'Jueves'),
        ('VIERNES', 'Viernes'),
        ('SABADO', 'Sábado'),
        ('DOMINGO', 'Domingo'),
    ]
    
    id_restriccion = models.AutoField(db_column='ID_Restriccion', primary_key=True)
    usuario = models.CharField(db_column='Usuario', max_length=100, blank=True, null=True, help_text='Usuario específico (NULL = aplica a tipo_usuario)')
    tipo_usuario = models.CharField(db_column='Tipo_Usuario', max_length=20, choices=TIPO_USUARIO_CHOICES)
    dia_semana = models.CharField(db_column='Dia_Semana', max_length=20, choices=DIA_SEMANA_CHOICES)
    hora_inicio = models.TimeField(db_column='Hora_Inicio', help_text='Hora de inicio permitida')
    hora_fin = models.TimeField(db_column='Hora_F fin', help_text='Hora de fin permitida')
    activo = models.BooleanField(db_column='Activo', default=True, help_text='Si la restricción está activa')
    fecha_creacion = models.DateTimeField(db_column='Fecha_Creacion', auto_now_add=True)
    
    class Meta(ManagedModel.Meta):
        db_table = 'restricciones_horarias'
        verbose_name = 'Restricción Horaria'
        verbose_name_plural = 'Restricciones Horarias'
        ordering = ['dia_semana', 'hora_inicio']
    
    def __str__(self):
        destino = self.usuario if self.usuario else f'Todos {self.tipo_usuario}'
        return f'{destino} - {self.dia_semana} {self.hora_inicio}-{self.hora_fin}'


class RenovacionSesion(ManagedModel):
    '''Tabla renovaciones_sesion - Auditoría de renovaciones de tokens'''
    id_renovacion = models.AutoField(db_column='ID_Renovacion', primary_key=True)
    usuario = models.CharField(db_column='Usuario', max_length=100)
    session_key_anterior = models.CharField(db_column='Session_Key_Anterior', max_length=255, blank=True, null=True)
    session_key_nuevo = models.CharField(db_column='Session_Key_Nuevo', max_length=255, blank=True, null=True)
    ip_address = models.CharField(db_column='IP_Address', max_length=45, blank=True, null=True)
    user_agent = models.TextField(db_column='User_Agent', blank=True, null=True)
    fecha_renovacion = models.DateTimeField(db_column='Fecha_Renovacion', auto_now_add=True)
    
    class Meta(ManagedModel.Meta):
        db_table = 'renovaciones_sesion'
        verbose_name = 'Renovación de Sesión'
        verbose_name_plural = 'Renovaciones de Sesión'
        ordering = ['-fecha_renovacion']
    
    def __str__(self):
        return f'{self.usuario} - {self.fecha_renovacion}'


class AjustesInventario(ManagedModel):
    '''Tabla ajustes_inventario - Ajustes de inventario'''
    TIPO_AJUSTE_CHOICES = [
        ('Reconteo', 'Reconteo'),
        ('Merma', 'Merma'),
        ('Robo', 'Robo'),
        ('Daño', 'Daño'),
        ('Otro', 'Otro'),
    ]

    ESTADO_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('Aprobado', 'Aprobado'),
        ('Rechazado', 'Rechazado'),
    ]

    id_ajuste = models.BigAutoField(db_column='ID_Ajuste', primary_key=True)
    id_empleado_responsable = models.ForeignKey(
        Empleado,
        on_delete=models.PROTECT,
        db_column='ID_Empleado_Responsable'
    )
    fecha_hora = models.DateTimeField(db_column='Fecha_Hora')
    tipo_ajuste = models.CharField(db_column='Tipo_Ajuste', max_length=8, choices=TIPO_AJUSTE_CHOICES)
    motivo = models.CharField(db_column='Motivo', max_length=255)
    estado = models.CharField(db_column='Estado', max_length=10, choices=ESTADO_CHOICES)

    class Meta(ManagedModel.Meta):
        db_table = 'ajustes_inventario'
        verbose_name = 'Ajuste de Inventario'
        verbose_name_plural = 'Ajustes de Inventario'

    def __str__(self):
        return f'Ajuste #{self.id_ajuste} - {self.tipo_ajuste}'


class DetalleAjuste(ManagedModel):
    '''Tabla detalle_ajuste - Detalle de ajustes de inventario'''
    id_detalle = models.BigAutoField(db_column='ID_Detalle', primary_key=True)
    id_ajuste = models.ForeignKey(
        AjustesInventario,
        on_delete=models.CASCADE,
        db_column='ID_Ajuste',
        related_name='detalles'
    )
    id_producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        db_column='ID_Producto'
    )
    id_movimientostock = models.OneToOneField(
        MovimientosStock,
        on_delete=models.CASCADE,
        db_column='ID_MovimientoStock'
    )
    cantidad_ajustada = models.DecimalField(db_column='Cantidad_Ajustada', max_digits=8, decimal_places=3)

    class Meta(ManagedModel.Meta):
        db_table = 'detalle_ajuste'
        verbose_name = 'Detalle de Ajuste'
        verbose_name_plural = 'Detalles de Ajuste'
        unique_together = (('id_ajuste', 'id_producto'),)

    def __str__(self):
        return f'Ajuste {self.id_ajuste_id}: {self.id_producto.descripcion} ({self.cantidad_ajustada})'