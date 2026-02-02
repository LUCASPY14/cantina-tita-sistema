"""
Utilidades de Seguridad y Auditoría
"""
from django.utils import timezone
from django.db import transaction, models
from datetime import timedelta
import secrets
import json
import requests

from .models import (
    IntentoLogin, AuditoriaOperacion, TokenRecuperacion, BloqueoCuenta,
    PatronAcceso, AnomaliaDetectada, SesionActiva, Intento2Fa, RenovacionSesion
)


def obtener_geolocalizacion_ip(ip_address):
    """
    Obtener ubicación geográfica de una IP usando ipapi.co
    Retorna: (ciudad, pais) o (None, None) si falla
    """
    # IPs locales/privadas no se gelocalizan
    if ip_address in ['127.0.0.1', 'localhost'] or ip_address.startswith('192.168.') or ip_address.startswith('10.'):
        return 'Local', 'Local'
    
    try:
        response = requests.get(
            f'https://ipapi.co/{ip_address}/json/',
            timeout=2  # Timeout corto para no bloquear el login
        )
        if response.status_code == 200:
            data = response.json()
            ciudad = data.get('city', 'Desconocida')
            pais = data.get('country_name', 'Desconocido')
            return ciudad, pais
    except Exception as e:
        print(f"Error obteniendo geolocalización: {e}")
    
    return None, None


def obtener_ip_cliente(request):
    """Obtener la IP real del cliente considerando proxies"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def registrar_intento_login(usuario, request, exitoso=False, motivo_fallo=None):
    """Registrar un intento de login con geolocalización"""
    try:
        ip_address = obtener_ip_cliente(request)
        ciudad, pais = obtener_geolocalizacion_ip(ip_address)
        
        IntentoLogin.objects.create(
            usuario=usuario,
            ip_address=ip_address,
            ciudad=ciudad,
            pais=pais,
            fecha_intento=timezone.now(),
            exitoso=exitoso,
            motivo_fallo=motivo_fallo
        )
    except Exception as e:
        print(f"Error al registrar intento de login: {e}")


def verificar_cuenta_bloqueada(usuario, tipo_usuario='CLIENTE_WEB'):
    """Verificar si una cuenta está bloqueada"""
    bloqueo_activo = BloqueoCuenta.objects.filter(
        usuario=usuario,
        tipo_usuario=tipo_usuario,
        activo=True
    ).first()
    
    if bloqueo_activo:
        # Verificar si ya pasó el tiempo de desbloqueo automático
        if bloqueo_activo.fecha_desbloqueo and timezone.now() >= bloqueo_activo.fecha_desbloqueo:
            bloqueo_activo.activo = False
            bloqueo_activo.save(update_fields=['activo'])
            return False, None
        return True, bloqueo_activo.motivo
    
    return False, None


def verificar_rate_limit(usuario, request, minutos=15, max_intentos=5):
    """
    Verificar si se ha excedido el límite de intentos de login
    Retorna: (bloqueado, intentos_restantes, minutos_para_desbloqueo)
    """
    # Verificar bloqueo manual primero
    bloqueado, motivo = verificar_cuenta_bloqueada(usuario)
    if bloqueado:
        return True, 0, None, motivo
    
    # Contar intentos fallidos recientes
    tiempo_limite = timezone.now() - timedelta(minutes=minutos)
    intentos_fallidos = IntentoLogin.objects.filter(
        usuario=usuario,
        exitoso=False,
        fecha_intento__gte=tiempo_limite
    ).count()
    
    if intentos_fallidos >= max_intentos:
        # Bloquear temporalmente
        tiempo_desbloqueo = timezone.now() + timedelta(minutes=30)
        BloqueoCuenta.objects.create(
            usuario=usuario,
            tipo_usuario='CLIENTE_WEB',
            motivo=f'Demasiados intentos fallidos de login ({intentos_fallidos})',
            fecha_bloqueo=timezone.now(),
            fecha_desbloqueo=tiempo_desbloqueo,
            bloqueado_por='Sistema (Rate Limit)',
            ip_address=obtener_ip_cliente(request),
            activo=True
        )
        return True, 0, 30, 'Cuenta bloqueada temporalmente'
    
    intentos_restantes = max_intentos - intentos_fallidos
    return False, intentos_restantes, None, None


def registrar_auditoria(
    request,
    operacion,
    resultado='EXITOSO',
    tipo_usuario='CLIENTE_WEB',
    tabla_afectada=None,
    id_registro=None,
    descripcion=None,
    datos_anteriores=None,
    datos_nuevos=None,
    mensaje_error=None
):
    """Registrar una operación en la auditoría con geolocalización"""
    try:
        usuario = getattr(request, 'user', None)
        usuario_str = usuario.username if usuario and usuario.is_authenticated else 'Anónimo'
        
        # Para clientes web, obtener de la sesión
        if not usuario or not usuario.is_authenticated:
            usuario_str = request.session.get('cliente_usuario', 'Anónimo')
            id_usuario = request.session.get('cliente_id')
        else:
            id_usuario = usuario.id if hasattr(usuario, 'id') else None
        
        ip_address = obtener_ip_cliente(request)
        ciudad, pais = obtener_geolocalizacion_ip(ip_address)
        
        AuditoriaOperacion.objects.create(
            usuario=usuario_str,
            tipo_usuario=tipo_usuario,
            id_usuario=id_usuario,
            operacion=operacion,
            tabla_afectada=tabla_afectada,
            id_registro=id_registro,
            descripcion=descripcion,
            datos_anteriores=datos_anteriores,
            datos_nuevos=datos_nuevos,
            ip_address=ip_address,
            ciudad=ciudad,
            pais=pais,
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            fecha_operacion=timezone.now(),
            resultado=resultado,
            mensaje_error=mensaje_error
        )
    except Exception as e:
        print(f"Error al registrar auditoría: {e}")


def generar_token_recuperacion(cliente, request):
    """Generar un token de recuperación de contraseña"""
    try:
        # Invalidar tokens anteriores no usados
        TokenRecuperacion.objects.filter(
            id_cliente=cliente,
            usado=False
        ).update(usado=True)
        
        # Generar nuevo token
        token = secrets.token_urlsafe(32)
        fecha_expiracion = timezone.now() + timedelta(hours=24)
        
        token_obj = TokenRecuperacion.objects.create(
            id_cliente=cliente,
            token=token,
            fecha_creacion=timezone.now(),
            fecha_expiracion=fecha_expiracion,
            usado=False,
            ip_solicitud=obtener_ip_cliente(request)
        )
        
        # Registrar en auditoría
        registrar_auditoria(
            request=request,
            operacion='SOLICITUD_RECUPERACION_PASSWORD',
            tipo_usuario='CLIENTE_WEB',
            tabla_afectada='tokens_recuperacion',
            id_registro=token_obj.id_token,
            descripcion=f'Solicitud de recuperación de contraseña para cliente {cliente.nombre_completo}'
        )
        
        return token
    except Exception as e:
        print(f"Error al generar token: {e}")
        return None


def verificar_token_recuperacion(token):
    """
    Verificar si un token de recuperación es válido
    Retorna: (valido, token_obj, mensaje_error)
    """
    try:
        token_obj = TokenRecuperacion.objects.select_related('id_cliente').get(token=token)
        
        if token_obj.usado:
            return False, None, 'Este enlace ya fue utilizado'
        
        if timezone.now() > token_obj.fecha_expiracion:
            return False, None, 'Este enlace ha expirado. Solicita uno nuevo'
        
        return True, token_obj, None
        
    except TokenRecuperacion.DoesNotExist:
        return False, None, 'Enlace inválido'


def marcar_token_usado(token):
    """Marcar un token como usado"""
    try:
        TokenRecuperacion.objects.filter(token=token).update(
            usado=True,
            fecha_uso=timezone.now()
        )
        return True
    except Exception as e:
        print(f"Error al marcar token como usado: {e}")
        return False


def limpiar_intentos_login_antiguos(dias=30):
    """Limpiar intentos de login antiguos (tarea programada)"""
    fecha_limite = timezone.now() - timedelta(days=dias)
    eliminados = IntentoLogin.objects.filter(fecha_intento__lt=fecha_limite).delete()
    return eliminados[0]


def limpiar_tokens_expirados():
    """Limpiar tokens de recuperación expirados (tarea programada)"""
    eliminados = TokenRecuperacion.objects.filter(
        fecha_expiracion__lt=timezone.now()
    ).delete()
    return eliminados[0]


def enviar_notificacion_seguridad(cliente, asunto, mensaje, tipo='warning'):
    """
    Enviar notificación de seguridad por email
    
    Args:
        cliente: Objeto Cliente
        asunto: Asunto del email
        mensaje: Mensaje principal
        tipo: 'warning', 'alert', 'info'
    """
    from django.core.mail import send_mail
    from django.conf import settings
    
    if not cliente.email:
        return False
    
    iconos = {
        'warning': '⚠️',
        'alert': '🚨',
        'info': 'ℹ️'
    }
    
    icono = iconos.get(tipo, '📧')
    
    try:
        send_mail(
            subject=f'{icono} {asunto} - Cantina Tita',
            message=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[cliente.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error enviando notificación: {e}")
        return False


def notificar_login_nueva_ip(cliente, request):
    """Notificar cuando hay login desde una IP nueva"""
    ip_actual = obtener_ip_cliente(request)
    
    # Verificar si es una IP conocida (últimos 30 días)
    fecha_limite = timezone.now() - timedelta(days=30)
    login_previo = IntentoLogin.objects.filter(
        usuario=cliente.email or f"cliente_{cliente.id_cliente}",
        ip_address=ip_actual,
        exitoso=True,
        fecha_intento__gte=fecha_limite
    ).exists()
    
    if not login_previo:
        mensaje = f"""Hola {cliente.nombres},

Se ha detectado un inicio de sesión en tu cuenta desde una IP nueva:

IP: {ip_actual}
Fecha: {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}

Si fuiste tú, puedes ignorar este mensaje.
Si no reconoces esta actividad, cambia tu contraseña inmediatamente.

Saludos,
Equipo Cantina Tita"""
        
        enviar_notificacion_seguridad(
            cliente,
            'Inicio de sesión desde nueva ubicación',
            mensaje,
            tipo='warning'
        )


def notificar_cuenta_bloqueada(cliente, request, motivo):
    """Notificar cuando una cuenta es bloqueada"""
    ip_actual = obtener_ip_cliente(request)
    
    mensaje = f"""Hola {cliente.nombres},

Tu cuenta ha sido BLOQUEADA temporalmente.

Motivo: {motivo}
IP: {ip_actual}
Fecha: {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}

Tu cuenta se desbloqueará automáticamente en 30 minutos.

Si no fuiste tú, contacta inmediatamente con la administración.

Saludos,
Equipo Cantina Tita"""
    
    enviar_notificacion_seguridad(
        cliente,
        '🚨 Cuenta Bloqueada',
        mensaje,
        tipo='alert'
    )


def notificar_intentos_sospechosos(cliente, request, intentos_fallidos):
    """Notificar cuando hay múltiples intentos fallidos"""
    ip_actual = obtener_ip_cliente(request)
    
    mensaje = f"""Hola {cliente.nombres},

Se han detectado múltiples intentos de inicio de sesión fallidos en tu cuenta.

Intentos fallidos: {intentos_fallidos}
IP: {ip_actual}
Fecha: {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}

Si fuiste tú, verifica que estés usando la contraseña correcta.
Si no fuiste tú, tu cuenta puede estar bajo ataque. Considera cambiar tu contraseña.

IMPORTANTE: Después de 5 intentos fallidos, tu cuenta será bloqueada por 30 minutos.

Saludos,
Equipo Cantina Tita"""
    
    enviar_notificacion_seguridad(
        cliente,
        'Intentos de acceso sospechosos',
        mensaje,
        tipo='warning'
    )


def desbloquear_cuentas_automaticas():
    """Desbloquear cuentas cuyo tiempo de bloqueo ha expirado"""
    desbloqueados = BloqueoCuenta.objects.filter(
        activo=True,
        fecha_desbloqueo__lte=timezone.now()
    ).update(activo=False)
    return desbloqueados


# =============================================================================
# ANÁLISIS DE PATRONES DE ACCESO
# =============================================================================

def registrar_sesion_activa(usuario, tipo_usuario, session_key, request):
    """Registrar o actualizar sesión activa"""
    try:
        sesion, created = SesionActiva.objects.update_or_create(
            session_key=session_key,
            defaults={
                'usuario': usuario,
                'tipo_usuario': tipo_usuario,
                'ip_address': obtener_ip_cliente(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', '')[:500],
                'fecha_inicio': timezone.now() if created else models.F('fecha_inicio'),
                'ultima_actividad': timezone.now(),
                'activa': True
            }
        )
        return sesion
    except Exception as e:
        print(f"Error registrando sesión: {e}")
        return None


def cerrar_sesion(session_key):
    """Marcar sesión como inactiva"""
    try:
        SesionActiva.objects.filter(session_key=session_key).update(
            activa=False,
            ultima_actividad=timezone.now()
        )
    except Exception as e:
        print(f"Error cerrando sesión: {e}")


def detectar_multiples_sesiones(usuario):
    """Detectar si un usuario tiene múltiples sesiones activas"""
    sesiones_activas = SesionActiva.objects.filter(
        usuario=usuario,
        activa=True
    ).count()
    
    if sesiones_activas > 1:
        # Registrar anomalía
        AnomaliaDetectada.objects.create(
            usuario=usuario,
            tipo_anomalia='MULTIPLES_SESIONES',
            fecha_deteccion=timezone.now(),
            descripcion=f'Usuario con {sesiones_activas} sesiones simultáneas',
            nivel_riesgo='MEDIO',
            notificado=False
        )
        return True, sesiones_activas
    
    return False, sesiones_activas


def actualizar_patron_acceso(usuario, tipo_usuario, request):
    """Actualizar o crear patrón de acceso para el usuario"""
    import json
    from datetime import datetime
    
    ip_actual = obtener_ip_cliente(request)
    hora_actual = timezone.now().time()
    dia_semana = timezone.now().weekday() + 1  # 1=Lun, 7=Dom
    
    try:
        # Buscar patrón existente para esta IP
        patron = PatronAcceso.objects.filter(
            usuario=usuario,
            ip_address=ip_actual
        ).first()
        
        if patron:
            # Actualizar patrón existente
            patron.ultima_deteccion = timezone.now()
            patron.frecuencia_accesos += 1
            
            # Actualizar rango horario
            if patron.horario_inicio is None or hora_actual < patron.horario_inicio:
                patron.horario_inicio = hora_actual
            if patron.horario_fin is None or hora_actual > patron.horario_fin:
                patron.horario_fin = hora_actual
            
            # Actualizar días de la semana
            try:
                dias = json.loads(patron.dias_semana) if patron.dias_semana else []
            except:
                dias = []
            
            if dia_semana not in dias:
                dias.append(dia_semana)
                patron.dias_semana = json.dumps(sorted(dias))
            
            # Marcar como habitual si hay más de 5 accesos
            if patron.frecuencia_accesos >= 5:
                patron.es_habitual = True
            
            patron.save()
        else:
            # Crear nuevo patrón
            PatronAcceso.objects.create(
                usuario=usuario,
                tipo_usuario=tipo_usuario,
                ip_address=ip_actual,
                horario_inicio=hora_actual,
                horario_fin=hora_actual,
                dias_semana=json.dumps([dia_semana]),
                primera_deteccion=timezone.now(),
                ultima_deteccion=timezone.now(),
                frecuencia_accesos=1,
                es_habitual=False
            )
    except Exception as e:
        print(f"Error actualizando patrón: {e}")


def detectar_anomalias_acceso(usuario, request):
    """
    Detectar anomalías en el acceso del usuario
    Returns: (tiene_anomalias, lista_anomalias)
    """
    import json
    
    ip_actual = obtener_ip_cliente(request)
    hora_actual = timezone.now().time()
    dia_semana = timezone.now().weekday() + 1
    
    anomalias = []
    
    # 1. Verificar si es una IP nueva
    patron_ip = PatronAcceso.objects.filter(
        usuario=usuario,
        ip_address=ip_actual,
        es_habitual=True
    ).exists()
    
    if not patron_ip:
        # Verificar si tiene algún patrón habitual
        tiene_patrones = PatronAcceso.objects.filter(
            usuario=usuario,
            es_habitual=True
        ).exists()
        
        if tiene_patrones:
            AnomaliaDetectada.objects.create(
                usuario=usuario,
                tipo_anomalia='IP_NUEVA',
                ip_address=ip_actual,
                fecha_deteccion=timezone.now(),
                descripcion=f'Acceso desde IP no habitual: {ip_actual}',
                nivel_riesgo='MEDIO',
                notificado=False
            )
            anomalias.append('IP_NUEVA')
    
    # 2. Verificar horario inusual
    patrones_usuario = PatronAcceso.objects.filter(
        usuario=usuario,
        es_habitual=True
    )
    
    if patrones_usuario.exists():
        horario_valido = False
        for patron in patrones_usuario:
            # Verificar si el día está en el patrón
            try:
                dias = json.loads(patron.dias_semana) if patron.dias_semana else []
            except:
                dias = []
            
            if dia_semana in dias:
                # Verificar si la hora está en el rango
                if patron.horario_inicio and patron.horario_fin:
                    # Agregar margen de 2 horas
                    from datetime import time, timedelta, datetime
                    inicio_dt = datetime.combine(datetime.today(), patron.horario_inicio)
                    fin_dt = datetime.combine(datetime.today(), patron.horario_fin)
                    inicio_margen = (inicio_dt - timedelta(hours=2)).time()
                    fin_margen = (fin_dt + timedelta(hours=2)).time()
                    
                    if inicio_margen <= hora_actual <= fin_margen:
                        horario_valido = True
                        break
        
        if not horario_valido:
            AnomaliaDetectada.objects.create(
                usuario=usuario,
                tipo_anomalia='HORARIO_INUSUAL',
                ip_address=ip_actual,
                fecha_deteccion=timezone.now(),
                descripcion=f'Acceso en horario inusual: {hora_actual.strftime("%H:%M")}',
                nivel_riesgo='BAJO',
                notificado=False
            )
            anomalias.append('HORARIO_INUSUAL')
    
    return len(anomalias) > 0, anomalias


def obtener_anomalias_recientes(usuario=None, dias=7):
    """Obtener anomalías recientes"""
    fecha_limite = timezone.now() - timedelta(days=dias)
    
    anomalias = AnomaliaDetectada.objects.filter(
        fecha_deteccion__gte=fecha_limite
    )
    
    if usuario:
        anomalias = anomalias.filter(usuario=usuario)
    
    return anomalias.order_by('-fecha_deteccion')


def limpiar_sesiones_inactivas(horas=24):
    """Marcar como inactivas las sesiones sin actividad"""
    fecha_limite = timezone.now() - timedelta(hours=horas)
    
    actualizadas = SesionActiva.objects.filter(
        activa=True,
        ultima_actividad__lt=fecha_limite
    ).update(activa=False)
    
    return actualizadas


def limpiar_anomalias_antiguas(dias=90):
    """Eliminar anomalías antiguas"""
    fecha_limite = timezone.now() - timedelta(days=dias)
    eliminadas = AnomaliaDetectada.objects.filter(
        fecha_deteccion__lt=fecha_limite
    ).delete()
    return eliminadas[0]


# ================== AUTENTICACIÓN 2FA (Two-Factor Authentication) ==================

def generar_secret_2fa():
    """Generar una clave secreta para TOTP (Time-based One-Time Password)"""
    import pyotp
    return pyotp.random_base32()


def generar_codigos_backup():
    """Generar 8 códigos de respaldo de 8 dígitos cada uno"""
    import bcrypt
    codigos_planos = [f'{secrets.randbelow(100000000):08d}' for _ in range(8)]
    codigos_hasheados = [bcrypt.hashpw(codigo.encode(), bcrypt.gensalt()).decode() for codigo in codigos_planos]
    return codigos_planos, json.dumps(codigos_hasheados)


def configurar_2fa_usuario(usuario, tipo_usuario='CLIENTE_WEB'):
    """
    Configurar 2FA para un usuario (primera vez)
    Retorna: (secret_key, codigos_backup_planos, qr_uri)
    """
    from .models import Autenticacion2Fa
    import pyotp
    
    # Verificar si ya existe configuración
    config_existente = Autenticacion2Fa.objects.filter(
        usuario=usuario,
        tipo_usuario=tipo_usuario
    ).first()
    
    if config_existente and config_existente.habilitado:
        return None, None, None  # Ya tiene 2FA activo
    
    # Generar nueva clave secreta
    secret_key = generar_secret_2fa()
    codigos_planos, codigos_hasheados = generar_codigos_backup()
    
    # Crear URI para código QR
    totp = pyotp.TOTP(secret_key)
    qr_uri = totp.provisioning_uri(
        name=usuario,
        issuer_name='Cantina Tita Sistema POS'
    )
    
    # Guardar en DB (sin habilitar aún)
    if config_existente:
        config_existente.secret_key = secret_key
        config_existente.backup_codes = codigos_hasheados
        config_existente.habilitado = False
        config_existente.save()
    else:
        Autenticacion2Fa.objects.create(
            usuario=usuario,
            tipo_usuario=tipo_usuario,
            secret_key=secret_key,
            backup_codes=codigos_hasheados,
            habilitado=False
        )
    
    return secret_key, codigos_planos, qr_uri


def activar_2fa_usuario(usuario, tipo_usuario, codigo_verificacion):
    """
    Activar 2FA después de verificar el primer código
    Retorna: True si se activó correctamente, False si el código es inválido
    """
    from .models import Autenticacion2Fa
    import pyotp
    
    config = Autenticacion2Fa.objects.filter(
        usuario=usuario,
        tipo_usuario=tipo_usuario
    ).first()
    
    if not config:
        return False
    
    # Verificar código TOTP
    totp = pyotp.TOTP(config.secret_key)
    if totp.verify(codigo_verificacion, valid_window=1):
        config.habilitado = True
        config.fecha_activacion = timezone.now()
        config.ultima_verificacion = timezone.now()
        config.save()
        return True
    
    return False


def verificar_codigo_2fa(usuario, tipo_usuario, codigo):
    """
    Verificar código 2FA (TOTP o código de respaldo)
    Retorna: True si el código es válido
    """
    from .models import Autenticacion2Fa
    import pyotp
    import bcrypt
    
    config = Autenticacion2Fa.objects.filter(
        usuario=usuario,
        tipo_usuario=tipo_usuario,
        habilitado=True
    ).first()
    
    if not config:
        return False
    
    # Intentar verificar como código TOTP
    totp = pyotp.TOTP(config.secret_key)
    if totp.verify(codigo, valid_window=1):
        config.ultima_verificacion = timezone.now()
        config.save()
        return True
    
    # Si falla, intentar como código de respaldo
    if config.backup_codes:
        codigos_hasheados = json.loads(config.backup_codes)
        for idx, codigo_hash in enumerate(codigos_hasheados):
            if bcrypt.checkpw(codigo.encode(), codigo_hash.encode()):
                # Código válido - eliminarlo para que no se use de nuevo
                codigos_hasheados.pop(idx)
                config.backup_codes = json.dumps(codigos_hasheados)
                config.ultima_verificacion = timezone.now()
                config.save()
                return True
    
    return False


def verificar_2fa_requerido(usuario, tipo_usuario):
    """
    Verificar si el usuario tiene 2FA habilitado
    Retorna: True si 2FA está activo y debe solicitarse
    """
    from .models import Autenticacion2Fa
    
    config = Autenticacion2Fa.objects.filter(
        usuario=usuario,
        tipo_usuario=tipo_usuario,
        habilitado=True
    ).first()
    
    return config is not None


def deshabilitar_2fa_usuario(usuario, tipo_usuario):
    """Deshabilitar 2FA para un usuario (por admin o usuario mismo)"""
    from .models import Autenticacion2Fa
    
    config = Autenticacion2Fa.objects.filter(
        usuario=usuario,
        tipo_usuario=tipo_usuario
    ).first()
    
    if config:
        config.habilitado = False
        config.save()
        return True
    
    return False


def generar_qr_code_2fa(qr_uri):
    """
    Generar imagen QR en formato base64 para mostrar en navegador
    """
    import qrcode
    from io import BytesIO
    import base64
    
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qr_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convertir a base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f'data:image/png;base64,{img_str}'


# ================== RESTRICCIONES HORARIAS ==================

def verificar_acceso_horario(usuario, tipo_usuario):
    """
    Verificar si el usuario puede acceder en el horario actual
    Retorna: (puede_acceder, mensaje_error)
    """
    from .models import RestriccionHoraria
    from datetime import datetime
    
    # Obtener día y hora actuales
    ahora = timezone.now()
    dias_semana_map = {
        0: 'LUNES',
        1: 'MARTES', 
        2: 'MIERCOLES',
        3: 'JUEVES',
        4: 'VIERNES',
        5: 'SABADO',
        6: 'DOMINGO'
    }
    dia_actual = dias_semana_map[ahora.weekday()]
    hora_actual = ahora.time()
    
    # Buscar restricciones específicas del usuario
    restricciones_usuario = RestriccionHoraria.objects.filter(
        usuario=usuario,
        tipo_usuario=tipo_usuario,
        dia_semana=dia_actual,
        activo=True
    )
    
    # Si no hay restricciones específicas, buscar del tipo de usuario
    if not restricciones_usuario.exists():
        restricciones_usuario = RestriccionHoraria.objects.filter(
            usuario__isnull=True,
            tipo_usuario=tipo_usuario,
            dia_semana=dia_actual,
            activo=True
        )
    
    # Si no hay restricciones configuradas, permitir acceso
    if not restricciones_usuario.exists():
        return True, None
    
    # Verificar si la hora actual está dentro de algún rango permitido
    for restriccion in restricciones_usuario:
        if restriccion.hora_inicio <= hora_actual <= restriccion.hora_fin:
            return True, None
    
    # Fuera de horario - obtener el próximo horario permitido
    proxima_restriccion = restricciones_usuario.first()
    mensaje = f'⏰ Acceso fuera de horario permitido. Horario: {proxima_restriccion.dia_semana} {proxima_restriccion.hora_inicio.strftime("%H:%M")} - {proxima_restriccion.hora_fin.strftime("%H:%M")}'
    
    return False, mensaje


def obtener_restricciones_usuario(usuario, tipo_usuario):
    """Obtener todas las restricciones horarias de un usuario"""
    from .models import RestriccionHoraria
    
    # Primero buscar restricciones específicas
    restricciones = RestriccionHoraria.objects.filter(
        usuario=usuario,
        tipo_usuario=tipo_usuario,
        activo=True
    ).order_by('dia_semana', 'hora_inicio')
    
    # Si no hay, buscar del tipo de usuario
    if not restricciones.exists():
        restricciones = RestriccionHoraria.objects.filter(
            usuario__isnull=True,
            tipo_usuario=tipo_usuario,
            activo=True
        ).order_by('dia_semana', 'hora_inicio')
    
    return restricciones


def crear_restriccion_horaria(usuario, tipo_usuario, dia_semana, hora_inicio, hora_fin):
    """Crear una nueva restricción horaria"""
    from .models import RestriccionHoraria
    
    restriccion = RestriccionHoraria.objects.create(
        usuario=usuario if usuario else None,
        tipo_usuario=tipo_usuario,
        dia_semana=dia_semana,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        activo=True
    )
    
    return restriccion


def eliminar_restriccion_horaria(id_restriccion):
    """Eliminar (desactivar) una restricción horaria"""
    from .models import RestriccionHoraria
    
    try:
        restriccion = RestriccionHoraria.objects.get(id_restriccion=id_restriccion)
        restriccion.activo = False
        restriccion.save()
        return True
    except RestriccionHoraria.DoesNotExist:
        return False


# ================== SEGURIDAD AVANZADA - RECOMENDACIONES ==================

def registrar_intento_2fa(usuario, tipo_usuario, request, codigo, exitoso, tipo_codigo='TOTP'):
    """
    Registrar intento de verificación 2FA
    """
    try:
        ip_address = obtener_ip_cliente(request)
        ciudad, pais = obtener_geolocalizacion_ip(ip_address)
        
        # Hash del código para no almacenarlo en texto plano
        import bcrypt
        codigo_hash = bcrypt.hashpw(codigo.encode(), bcrypt.gensalt(rounds=4)).decode()[:10]
        
        Intento2Fa.objects.create(
            usuario=usuario,
            tipo_usuario=tipo_usuario,
            ip_address=ip_address,
            ciudad=ciudad,
            pais=pais,
            codigo_ingresado=codigo_hash,
            exitoso=exitoso,
            tipo_codigo=tipo_codigo
        )
    except Exception as e:
        print(f"Error al registrar intento 2FA: {e}")


def verificar_rate_limit_2fa(usuario, tipo_usuario, minutos=15, max_intentos=5):
    """
    Verificar rate limiting específico para 2FA
    Bloquear si hay muchos intentos fallidos
    Retorna: (bloqueado, intentos_restantes, mensaje)
    """
    fecha_limite = timezone.now() - timedelta(minutes=minutos)
    
    intentos_fallidos = Intento2Fa.objects.filter(
        usuario=usuario,
        tipo_usuario=tipo_usuario,
        exitoso=False,
        fecha_intento__gte=fecha_limite
    ).count()
    
    if intentos_fallidos >= max_intentos:
        # Bloquear temporalmente 2FA
        return True, 0, f'Demasiados intentos fallidos de 2FA. Espera {minutos} minutos.'
    
    return False, max_intentos - intentos_fallidos, None


def renovar_token_sesion(request, usuario):
    """
    Renovar token de sesión para prevenir session fixation
    """
    try:
        session_key_anterior = request.session.session_key
        
        # Ciclar la sesión (Django genera nuevo session_key)
        request.session.cycle_key()
        
        session_key_nuevo = request.session.session_key
        
        # Registrar renovación
        RenovacionSesion.objects.create(
            usuario=usuario,
            session_key_anterior=session_key_anterior,
            session_key_nuevo=session_key_nuevo,
            ip_address=obtener_ip_cliente(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
        )
        
        return True
    except Exception as e:
        print(f"Error al renovar sesión: {e}")
        return False


def verificar_user_agent_consistente(request, usuario):
    """
    Verificar que el User-Agent sea consistente durante la sesión
    Detecta posible secuestro de sesión
    Retorna: (es_consistente, mensaje_alerta)
    """
    try:
        user_agent_actual = request.META.get('HTTP_USER_AGENT', '')
        user_agent_sesion = request.session.get('user_agent_inicial')
        
        # Primera vez - guardar
        if not user_agent_sesion:
            request.session['user_agent_inicial'] = user_agent_actual
            return True, None
        
        # Verificar consistencia (comparación simple)
        if user_agent_actual != user_agent_sesion:
            # Crear anomalía de seguridad
            ip_actual = obtener_ip_cliente(request)
            ciudad, pais = obtener_geolocalizacion_ip(ip_actual)
            
            AnomaliaDetectada.objects.create(
                usuario=usuario,
                tipo_anomalia='CAMBIO_USER_AGENT',
                ip_address=ip_actual,
                fecha_deteccion=timezone.now(),
                descripcion=f'User-Agent cambió durante la sesión. Original: {user_agent_sesion[:50]}... Nuevo: {user_agent_actual[:50]}...',
                nivel_riesgo='ALTO',
                notificado=False
            )
            
            return False, '⚠️ Se detectó un cambio en tu navegador. Por seguridad, vuelve a iniciar sesión.'
        
        return True, None
    except Exception as e:
        print(f"Error verificando User-Agent: {e}")
        return True, None  # No bloquear si hay error


def enviar_alerta_anomalia_critica(usuario, tipo_anomalia, descripcion, request=None):
    """
    Enviar alerta inmediata por anomalía de seguridad crítica
    (email, SMS, webhook, etc.)
    """
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        
        ip_address = obtener_ip_cliente(request) if request else 'Desconocida'
        ciudad, pais = obtener_geolocalizacion_ip(ip_address) if request else (None, None)
        ubicacion = f"{ciudad}, {pais}" if ciudad and pais else "Desconocida"
        
        asunto = f'🚨 ALERTA DE SEGURIDAD CRÍTICA - {tipo_anomalia}'
        mensaje = f"""
        ALERTA DE SEGURIDAD CRÍTICA
        ============================
        
        Usuario: {usuario}
        Tipo de Anomalía: {tipo_anomalia}
        Descripción: {descripcion}
        
        Detalles:
        - IP: {ip_address}
        - Ubicación: {ubicacion}
        - Fecha/Hora: {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}
        
        Acción recomendada: Revisar inmediatamente en el dashboard de seguridad.
        
        ---
        Sistema de Seguridad Cantina Tita
        """
        
        # Enviar a administradores
        admins_emails = [admin[1] for admin in settings.ADMINS]
        if admins_emails and settings.EMAIL_BACKEND != 'django.core.mail.backends.console.EmailBackend':
            send_mail(
                subject=asunto,
                message=mensaje,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=admins_emails,
                fail_silently=True
            )
        
        # Log en consola para desarrollo
        print(f"\n{'='*60}")
        print(mensaje)
        print(f"{'='*60}\n")
        
        return True
    except Exception as e:
        print(f"Error enviando alerta crítica: {e}")
        return False


def calcular_tiempo_bloqueo_exponencial(usuario, tipo_usuario='CLIENTE_WEB'):
    """
    Calcular tiempo de bloqueo exponencial basado en intentos previos
    Retorna: minutos de bloqueo
    """
    # Contar bloqueos previos en las últimas 24 horas
    fecha_limite = timezone.now() - timedelta(hours=24)
    bloqueos_previos = BloqueoCuenta.objects.filter(
        usuario=usuario,
        tipo_usuario=tipo_usuario,
        fecha_bloqueo__gte=fecha_limite
    ).count()
    
    # Bloqueo exponencial: 5min, 15min, 30min, 1h, 2h, 4h, 8h, 24h
    tiempos_bloqueo = [5, 15, 30, 60, 120, 240, 480, 1440]
    
    if bloqueos_previos >= len(tiempos_bloqueo):
        return tiempos_bloqueo[-1]  # Máximo 24 horas
    
    return tiempos_bloqueo[bloqueos_previos]


def limpiar_intentos_2fa_antiguos(dias=30):
    """Limpiar intentos 2FA antiguos para mantener BD limpia"""
    fecha_limite = timezone.now() - timedelta(days=dias)
    eliminados = Intento2Fa.objects.filter(
        fecha_intento__lt=fecha_limite
    ).delete()
    return eliminados[0]


def obtener_estadisticas_2fa(dias=30):
    """Obtener estadísticas de uso de 2FA"""
    fecha_limite = timezone.now() - timedelta(days=dias)
    
    total_intentos = Intento2Fa.objects.filter(
        fecha_intento__gte=fecha_limite
    ).count()
    
    intentos_exitosos = Intento2Fa.objects.filter(
        fecha_intento__gte=fecha_limite,
        exitoso=True
    ).count()
    
    intentos_fallidos = total_intentos - intentos_exitosos
    
    tasa_exito = (intentos_exitosos / total_intentos * 100) if total_intentos > 0 else 0
    
    return {
        'total_intentos': total_intentos,
        'exitosos': intentos_exitosos,
        'fallidos': intentos_fallidos,
        'tasa_exito': round(tasa_exito, 2)
    }

