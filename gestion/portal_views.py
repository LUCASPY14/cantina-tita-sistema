# Portal de Padres - Vistas
# Sistema de autenticación y dashboard para padres

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.http import JsonResponse
import secrets
import json
from datetime import timedelta

from .models import (
    UsuarioPortal, Cliente, TokenVerificacion,
    Notificacion, PreferenciaNotificacion, Tarjeta, TransaccionOnline
)
from .portal_forms import (
    RegistroForm, LoginForm, RecuperarPasswordForm,
    CambiarPasswordForm, ActualizarPerfilForm
)


# ========== DECORADORES ==========

def login_required_portal(view_func):
    """Decorador para requerir autenticación en el portal"""
    def wrapper(request, *args, **kwargs):
        usuario_id = request.session.get('portal_usuario_id')
        if not usuario_id:
            messages.warning(request, 'Debe iniciar sesión para acceder')
            return redirect('portal_login')
        
        try:
            usuario = UsuarioPortal.objects.get(id_usuario_portal=usuario_id, activo=True)
            request.usuario_portal = usuario
        except UsuarioPortal.DoesNotExist:
            request.session.flush()
            messages.error(request, 'Sesión inválida')
            return redirect('portal_login')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


# ========== UTILIDADES ==========

def generar_token():
    """Genera un token seguro de 32 bytes"""
    return secrets.token_urlsafe(32)


def enviar_email_verificacion(usuario_portal):
    """Envía email de verificación al usuario"""
    # Crear token de verificación
    token_obj = TokenVerificacion.objects.create(
        usuario_portal=usuario_portal,
        token=generar_token(),
        tipo='email_verification',
        expira_en=timezone.now() + timedelta(hours=24)
    )
    
    # URL de verificación
    url_verificacion = f"{settings.SITE_URL}/portal/verificar-email/{token_obj.token}/"
    
    # Enviar email
    asunto = 'Verifica tu correo electrónico - Portal de Padres'
    mensaje = f"""
    Hola,
    
    Gracias por registrarte en el Portal de Padres.
    
    Para completar tu registro, verifica tu correo electrónico haciendo clic en el siguiente enlace:
    
    {url_verificacion}
    
    Este enlace expira en 24 horas.
    
    Si no solicitaste esta cuenta, puedes ignorar este correo.
    
    Saludos,
    Equipo del Portal de Padres
    """
    
    try:
        send_mail(
            asunto,
            mensaje,
            settings.DEFAULT_FROM_EMAIL,
            [usuario_portal.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error enviando email: {e}")
        return False


def enviar_email_recuperacion(usuario_portal):
    """Envía email para recuperar contraseña"""
    # Crear token de recuperación
    token_obj = TokenVerificacion.objects.create(
        usuario_portal=usuario_portal,
        token=generar_token(),
        tipo='password_reset',
        expira_en=timezone.now() + timedelta(hours=2)
    )
    
    # URL de recuperación
    url_recuperacion = f"{settings.SITE_URL}/portal/restablecer-password/{token_obj.token}/"
    
    # Enviar email
    asunto = 'Recuperación de contraseña - Portal de Padres'
    mensaje = f"""
    Hola,
    
    Recibimos una solicitud para restablecer la contraseña de tu cuenta.
    
    Para crear una nueva contraseña, haz clic en el siguiente enlace:
    
    {url_recuperacion}
    
    Este enlace expira en 2 horas.
    
    Si no solicitaste esto, puedes ignorar este correo de forma segura.
    
    Saludos,
    Equipo del Portal de Padres
    """
    
    try:
        send_mail(
            asunto,
            mensaje,
            settings.DEFAULT_FROM_EMAIL,
            [usuario_portal.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error enviando email: {e}")
        return False


# ========== VISTAS DE AUTENTICACIÓN ==========

@require_http_methods(["GET", "POST"])
def registro_view(request):
    """Vista de registro de nuevos usuarios"""
    # Si ya está autenticado, redirigir al dashboard
    if request.session.get('portal_usuario_id'):
        return redirect('portal_dashboard')
    
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Buscar cliente por RUC/CI
                    ruc_ci = form.cleaned_data['ruc_ci']
                    try:
                        cliente = Cliente.objects.get(ruc_ci=ruc_ci)
                    except Cliente.DoesNotExist:
                        messages.error(request, 'No se encontró un cliente con ese RUC/CI')
                        return render(request, 'portal/registro.html', {'form': form})
                    
                    # Crear usuario del portal
                    usuario_portal = UsuarioPortal.objects.create(
                        cliente=cliente,
                        email=form.cleaned_data['email'],
                        password_hash=make_password(form.cleaned_data['password']),
                        email_verificado=False,
                        fecha_registro=timezone.now(),
                        activo=True,
                        creado_en=timezone.now(),
                        actualizado_en=timezone.now()
                    )
                    
                    # Enviar email de verificación
                    if enviar_email_verificacion(usuario_portal):
                        messages.success(
                            request,
                            'Registro exitoso. Revisa tu correo para verificar tu cuenta.'
                        )
                    else:
                        messages.warning(
                            request,
                            'Cuenta creada, pero hubo un error al enviar el email de verificación. '
                            'Contacta al administrador.'
                        )
                    
                    return redirect('portal_login')
                    
            except Exception as e:
                messages.error(request, f'Error al crear la cuenta: {str(e)}')
    else:
        form = RegistroForm()
    
    return render(request, 'portal/registro.html', {'form': form})


@require_http_methods(["GET", "POST"])
def login_view(request):
    """Vista de inicio de sesión"""
    # Si ya está autenticado, redirigir al dashboard
    if request.session.get('portal_usuario_id'):
        return redirect('portal_dashboard')
    
    if request.method == 'POST':
        print(f"[LOGIN DEBUG] POST recibido: {request.POST.dict()}")
        form = LoginForm(request.POST)
        
        print(f"[LOGIN DEBUG] Formulario válido: {form.is_valid()}")
        if not form.is_valid():
            print(f"[LOGIN DEBUG] Errores del formulario: {form.errors}")
        
        if form.is_valid():
            usuario = form.cleaned_data['usuario']
            recordarme = form.cleaned_data.get('recordarme', False)
            
            print(f"[LOGIN DEBUG] Usuario autenticado: {usuario.email}")
            
            # Crear sesión
            request.session['portal_usuario_id'] = usuario.id_usuario_portal
            request.session['portal_email'] = usuario.email
            
            # Configurar duración de sesión
            if recordarme:
                request.session.set_expiry(604800)  # 7 días
            else:
                request.session.set_expiry(0)  # Hasta cerrar navegador
            
            # Actualizar último acceso
            usuario.ultimo_acceso = timezone.now()
            usuario.save(update_fields=['ultimo_acceso'])
            
            messages.success(request, f'Bienvenido, {usuario.email}')
            print(f"[LOGIN DEBUG] Redirigiendo a portal_dashboard")
            return redirect('portal_dashboard')
    else:
        form = LoginForm()
    
    return render(request, 'portal/login.html', {'form': form})


@require_http_methods(["GET"])
def logout_view(request):
    """Vista de cierre de sesión"""
    request.session.flush()
    messages.info(request, 'Sesión cerrada correctamente')
    return redirect('portal_login')


@require_http_methods(["GET"])
def verificar_email_view(request, token):
    """Vista para verificar email con token"""
    try:
        token_obj = TokenVerificacion.objects.get(
            token=token,
            tipo='email_verification',
            usado=False
        )
        
        # Verificar si el token expiró
        if not token_obj.es_valido():
            messages.error(request, 'El enlace de verificación ha expirado')
            return redirect('portal_login')
        
        # Marcar email como verificado
        usuario = token_obj.usuario_portal
        usuario.email_verificado = True
        usuario.save(update_fields=['email_verificado'])
        
        # Marcar token como usado
        token_obj.usado = True
        token_obj.save(update_fields=['usado'])
        
        messages.success(request, 'Email verificado correctamente. Ya puedes iniciar sesión.')
        return redirect('portal_login')
        
    except TokenVerificacion.DoesNotExist:
        messages.error(request, 'Enlace de verificación inválido')
        return redirect('portal_login')


@require_http_methods(["GET", "POST"])
def recuperar_password_view(request):
    """Vista para solicitar recuperación de contraseña"""
    if request.method == 'POST':
        form = RecuperarPasswordForm(request.POST)
        
        if form.is_valid():
            email = form.cleaned_data['email']
            usuario = UsuarioPortal.objects.get(email=email)
            
            if enviar_email_recuperacion(usuario):
                messages.success(
                    request,
                    'Hemos enviado un enlace de recuperación a tu correo electrónico'
                )
            else:
                messages.error(
                    request,
                    'Hubo un error al enviar el correo. Intenta nuevamente.'
                )
            
            return redirect('portal_login')
    else:
        form = RecuperarPasswordForm()
    
    return render(request, 'portal/recuperar_password.html', {'form': form})


@require_http_methods(["GET", "POST"])
def restablecer_password_view(request, token):
    """Vista para restablecer contraseña con token"""
    try:
        token_obj = TokenVerificacion.objects.get(
            token=token,
            tipo='password_reset',
            usado=False
        )
        
        # Verificar si el token expiró
        if not token_obj.es_valido():
            messages.error(request, 'El enlace de recuperación ha expirado')
            return redirect('portal_recuperar_password')
        
        if request.method == 'POST':
            form = CambiarPasswordForm(request.POST)
            
            if form.is_valid():
                # Actualizar contraseña
                usuario = token_obj.usuario_portal
                usuario.password_hash = make_password(form.cleaned_data['password'])
                usuario.save(update_fields=['password_hash'])
                
                # Marcar token como usado
                token_obj.usado = True
                token_obj.save(update_fields=['usado'])
                
                messages.success(request, 'Contraseña actualizada correctamente')
                return redirect('portal_login')
        else:
            form = CambiarPasswordForm()
        
        return render(request, 'portal/restablecer_password.html', {
            'form': form,
            'token': token
        })
        
    except TokenVerificacion.DoesNotExist:
        messages.error(request, 'Enlace de recuperación inválido')
        return redirect('portal_recuperar_password')


# ========== DASHBOARD ==========

@login_required_portal
def dashboard_view(request):
    """Vista principal del dashboard"""
    usuario = request.usuario_portal
    cliente = usuario.cliente
    
    # Obtener todas las tarjetas del cliente
    tarjetas = Tarjeta.objects.filter(
        id_hijo__id_cliente=cliente
    ).select_related('id_hijo').order_by('-saldo_actual')
    
    # Calcular totales
    total_tarjetas = tarjetas.count()
    saldo_total = sum(t.saldo_actual for t in tarjetas)
    
    # Obtener notificaciones no leídas
    notificaciones = usuario.notificaciones.filter(leida=False).order_by('-fecha_envio')[:5]
    
    # Obtener últimas transacciones
    ultimas_transacciones = usuario.transacciones.all().order_by('-fecha_transaccion')[:10]
    
    context = {
        'usuario': usuario,
        'cliente': cliente,
        'tarjetas': tarjetas,
        'total_tarjetas': total_tarjetas,
        'saldo_total': saldo_total,
        'notificaciones': notificaciones,
        'ultimas_transacciones': ultimas_transacciones,
    }
    
    return render(request, 'portal/dashboard.html', context)


@login_required_portal
def mis_hijos_view(request):
    """Vista para ver y gestionar hijos y tarjetas"""
    usuario = request.usuario_portal
    cliente = usuario.cliente
    
    # Obtener hijos con sus tarjetas
    from .models import Hijo
    hijos = Hijo.objects.filter(id_cliente=cliente).prefetch_related('tarjetas')
    
    context = {
        'usuario': usuario,
        'hijos': hijos,
    }
    
    return render(request, 'portal/mis_hijos.html', context)


@login_required_portal
def perfil_view(request):
    """Vista para ver y editar perfil"""
    usuario = request.usuario_portal
    
    if request.method == 'POST':
        form = ActualizarPerfilForm(request.POST)
        if form.is_valid():
            # Aquí se actualizaría el perfil
            messages.success(request, 'Perfil actualizado correctamente')
            return redirect('portal_perfil')
    else:
        form = ActualizarPerfilForm(initial={
            'email': usuario.email,
        })
    
    context = {
        'usuario': usuario,
        'form': form,
    }
    
    return render(request, 'portal/perfil.html', context)


# ========== RECARGAS DE SALDO ==========

@login_required_portal
@require_http_methods(["GET", "POST"])
def recargar_tarjeta_view(request, nro_tarjeta):
    """Vista para recargar saldo de una tarjeta"""
    usuario = request.usuario_portal
    
    # Verificar que la tarjeta pertenece al usuario
    try:
        tarjeta = Tarjeta.objects.select_related('id_hijo__id_cliente').get(
            nro_tarjeta=nro_tarjeta
        )
        
        if tarjeta.id_hijo.id_cliente != usuario.cliente:
            messages.error(request, 'No tiene permiso para recargar esta tarjeta')
            return redirect('portal_mis_hijos')
    except Tarjeta.DoesNotExist:
        messages.error(request, 'Tarjeta no encontrada')
        return redirect('portal_mis_hijos')
    
    if request.method == 'POST':
        monto = request.POST.get('monto')
        metodo_pago = request.POST.get('metodo_pago')
        telefono = request.POST.get('telefono', '')
        
        # Validaciones
        try:
            monto = int(monto)
            if monto < 1000:
                messages.error(request, 'El monto mínimo es 1.000 Guaraníes')
                return redirect('portal_recargar_tarjeta', nro_tarjeta=nro_tarjeta)
            
            if monto > 1000000:
                messages.error(request, 'El monto máximo es 1.000.000 Guaraníes')
                return redirect('portal_recargar_tarjeta', nro_tarjeta=nro_tarjeta)
            
            if monto % 1000 != 0:
                messages.error(request, 'El monto debe ser múltiplo de 1.000')
                return redirect('portal_recargar_tarjeta', nro_tarjeta=nro_tarjeta)
        except (ValueError, TypeError):
            messages.error(request, 'Monto inválido')
            return redirect('portal_recargar_tarjeta', nro_tarjeta=nro_tarjeta)
        
        if metodo_pago not in ['metrepay', 'tigo_money']:
            messages.error(request, 'Método de pago no válido')
            return redirect('portal_recargar_tarjeta', nro_tarjeta=nro_tarjeta)
        
        # Guardar datos en sesión para el webhook
        request.session['recarga_pendiente'] = {
            'nro_tarjeta': nro_tarjeta,
            'monto': monto,
            'metodo_pago': metodo_pago,
            'usuario_portal_id': usuario.id_usuario_portal
        }
        
        # Procesar según método de pago
        if metodo_pago == 'metrepay':
            from .cliente_views import procesar_pago_metrepay
            
            exito, referencia, payment_url, custom_id = procesar_pago_metrepay(
                monto=monto,
                metodo_pago='metrepay',
                request=request,
                tipo_pago='CARGA_SALDO_PORTAL'
            )
            
            if exito:
                # Crear transacción pendiente
                TransaccionOnline.objects.create(
                    nro_tarjeta=tarjeta,
                    usuario_portal=usuario,
                    monto=monto,
                    metodo_pago='metrepay',
                    estado='pendiente',
                    referencia_pago=referencia,
                    id_transaccion_externa=custom_id,
                    fecha_transaccion=timezone.now(),
                    creado_en=timezone.now(),
                    actualizado_en=timezone.now()
                )
                
                messages.info(request, 'Redirigiendo a MetrePay...')
                return redirect(payment_url)
            else:
                messages.error(request, f'Error al procesar el pago: {referencia}')
        
        elif metodo_pago == 'tigo_money':
            if not telefono:
                messages.error(request, 'Debe ingresar el número de teléfono Tigo')
                return redirect('portal_recargar_tarjeta', nro_tarjeta=nro_tarjeta)
            
            from .tigo_money_gateway import procesar_pago_tigo_money
            
            exito, referencia, mensaje, transaction_id = procesar_pago_tigo_money(
                telefono=telefono,
                monto=monto,
                descripcion=f'Recarga tarjeta {nro_tarjeta[-4:]}',
                request=request,
                tipo_pago='CARGA_SALDO_PORTAL'
            )
            
            if exito:
                # Crear transacción pendiente
                TransaccionOnline.objects.create(
                    nro_tarjeta=tarjeta,
                    usuario_portal=usuario,
                    monto=monto,
                    metodo_pago='tigo_money',
                    estado='pendiente',
                    referencia_pago=referencia,
                    id_transaccion_externa=transaction_id,
                    datos_extra=json.dumps({'telefono': telefono}),
                    fecha_transaccion=timezone.now(),
                    creado_en=timezone.now(),
                    actualizado_en=timezone.now()
                )
                
                messages.success(request, mensaje)
                messages.info(request, f'Referencia de pago: {referencia}')
                return redirect('portal_estado_recarga', referencia=referencia)
            else:
                messages.error(request, f'Error: {mensaje}')
    
    # Montos sugeridos
    montos_sugeridos = [5000, 10000, 20000, 50000, 100000]
    
    context = {
        'usuario': usuario,
        'tarjeta': tarjeta,
        'hijo': tarjeta.id_hijo,
        'montos_sugeridos': montos_sugeridos,
    }
    
    return render(request, 'portal/recargar_tarjeta.html', context)


@login_required_portal
def estado_recarga_view(request, referencia):
    """Vista para ver el estado de una recarga"""
    usuario = request.usuario_portal
    
    try:
        transaccion = TransaccionOnline.objects.select_related(
            'nro_tarjeta__id_hijo'
        ).get(
            referencia_pago=referencia,
            usuario_portal=usuario
        )
        
        context = {
            'usuario': usuario,
            'transaccion': transaccion,
            'tarjeta': transaccion.nro_tarjeta,
        }
        
        return render(request, 'portal/estado_recarga.html', context)
    except TransaccionOnline.DoesNotExist:
        messages.error(request, 'Transacción no encontrada')
        return redirect('portal_dashboard')


@require_http_methods(["GET"])
def pago_exitoso_view(request):
    """Vista de confirmación de pago exitoso (redirect desde MetrePay)"""
    # Obtener datos de la sesión
    recarga_pendiente = request.session.get('recarga_pendiente')
    
    if recarga_pendiente:
        nro_tarjeta = recarga_pendiente.get('nro_tarjeta')
        monto = recarga_pendiente.get('monto')
        
        # Limpiar sesión
        del request.session['recarga_pendiente']
        
        messages.success(
            request,
            f'Pago procesado. Se acreditarán ₲ {monto:,.0f} a la tarjeta {nro_tarjeta} una vez confirmado.'
        )
    else:
        messages.info(request, 'Pago procesado correctamente')
    
    # Si está autenticado en el portal, redirigir al dashboard
    if request.session.get('portal_usuario_id'):
        return redirect('portal_dashboard')
    else:
        return redirect('portal_login')


@require_http_methods(["GET"])
def pago_cancelado_view(request):
    """Vista cuando el pago es cancelado"""
    # Limpiar sesión
    if 'recarga_pendiente' in request.session:
        del request.session['recarga_pendiente']
    
    messages.warning(request, 'El pago fue cancelado')
    
    if request.session.get('portal_usuario_id'):
        return redirect('portal_dashboard')
    else:
        return redirect('portal_login')
