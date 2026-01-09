"""
Vistas para gestión de clientes y portal web de clientes
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.db import transaction
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.core.mail import send_mail
from django.conf import settings
import bcrypt
import requests
import json
from datetime import datetime, timedelta
from decimal import Decimal

from .models import (
    Cliente, UsuariosWebClientes, Hijo, Tarjeta, CargasSaldo,
    Ventas, DetalleVenta, SuscripcionesAlmuerzo, RegistroConsumoAlmuerzo,
    PagosAlmuerzoMensual, ListaPrecios, TipoCliente, IntentoLogin
)
from .seguridad_utils import (
    registrar_intento_login, verificar_rate_limit, registrar_auditoria,
    generar_token_recuperacion, verificar_token_recuperacion, marcar_token_usado,
    verificar_cuenta_bloqueada, notificar_login_nueva_ip, notificar_cuenta_bloqueada,
    notificar_intentos_sospechosos, registrar_sesion_activa, cerrar_sesion,
    detectar_multiples_sesiones, actualizar_patron_acceso, detectar_anomalias_acceso,
    configurar_2fa_usuario, activar_2fa_usuario, verificar_codigo_2fa,
    verificar_2fa_requerido, deshabilitar_2fa_usuario, generar_qr_code_2fa,
    verificar_acceso_horario, registrar_intento_2fa, verificar_rate_limit_2fa,
    renovar_token_sesion, verificar_user_agent_consistente, enviar_alerta_anomalia_critica,
    calcular_tiempo_bloqueo_exponencial
)


# Función auxiliar para registrar auditoría sin request (para webhooks)
def registrar_auditoria_sistema(operacion, descripcion, tabla_afectada=None, id_registro=None):
    """Registrar auditoría para operaciones del sistema (sin request)"""
    from .models import AuditoriaOperacion
    from django.utils import timezone
    
    try:
        AuditoriaOperacion.objects.create(
            usuario='SISTEMA',
            tipo_usuario='CLIENTE_WEB',
            operacion=operacion,
            tabla_afectada=tabla_afectada,
            id_registro=id_registro,
            descripcion=descripcion,
            fecha_operacion=timezone.now(),
            ip_address='WEBHOOK',
            user_agent='MetrePay Webhook',
            resultado='EXITOSO'
        )
    except Exception as e:
        print(f"Error registrando auditoría del sistema: {e}")


# ============================================================================
# GESTIÓN DE CLIENTES (Admin)
# ============================================================================

@login_required
def gestionar_clientes_view(request):
    """Vista para listar y gestionar clientes"""
    
    # Filtros
    busqueda = request.GET.get('q', '')
    solo_sin_usuario = request.GET.get('sin_usuario', '')
    
    clientes = Cliente.objects.select_related('id_tipo_cliente', 'id_lista').all()
    
    if busqueda:
        clientes = clientes.filter(
            Q(nombres__icontains=busqueda) |
            Q(apellidos__icontains=busqueda) |
            Q(ruc_ci__icontains=busqueda) |
            Q(email__icontains=busqueda)
        )
    
    if solo_sin_usuario:
        # Clientes sin usuario web
        clientes = clientes.filter(usuario_web__isnull=True)
    
    # Paginación
    paginator = Paginator(clientes, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'busqueda': busqueda,
        'solo_sin_usuario': solo_sin_usuario,
    }
    
    return render(request, 'clientes/gestionar_clientes.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def crear_cliente_view(request):
    """Vista para crear un nuevo cliente con usuario web opcional"""
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Crear cliente
                cliente = Cliente.objects.create(
                    id_lista_id=request.POST.get('id_lista'),
                    id_tipo_cliente_id=request.POST.get('id_tipo_cliente'),
                    nombres=request.POST.get('nombres'),
                    apellidos=request.POST.get('apellidos'),
                    razon_social=request.POST.get('razon_social', ''),
                    ruc_ci=request.POST.get('ruc_ci'),
                    direccion=request.POST.get('direccion', ''),
                    ciudad=request.POST.get('ciudad', ''),
                    telefono=request.POST.get('telefono', ''),
                    email=request.POST.get('email', ''),
                    limite_credito=request.POST.get('limite_credito') or None,
                    activo=True
                )
                
                # Crear usuario web si se proporcionó
                crear_usuario = request.POST.get('crear_usuario_web')
                if crear_usuario:
                    usuario = request.POST.get('usuario')
                    contrasena = request.POST.get('contrasena')
                    
                    if usuario and contrasena:
                        # Hash de contraseña con bcrypt
                        contrasena_hash = bcrypt.hashpw(
                            contrasena.encode('utf-8'),
                            bcrypt.gensalt()
                        ).decode('utf-8')
                        
                        UsuariosWebClientes.objects.create(
                            id_cliente=cliente,
                            usuario=usuario,
                            contrasena_hash=contrasena_hash,
                            activo=True
                        )
                        
                        messages.success(request, f'Cliente y usuario web creados exitosamente. Usuario: {usuario}')
                    else:
                        messages.warning(request, 'Cliente creado pero usuario web no fue configurado (faltan datos)')
                else:
                    messages.success(request, 'Cliente creado exitosamente')
                
                    return redirect('clientes:gestionar_clientes')
                
        except Exception as e:
            messages.error(request, f'Error al crear cliente: {str(e)}')
    
    # GET - Mostrar formulario
    listas_precios = ListaPrecios.objects.all()
    tipos_cliente = TipoCliente.objects.all()
    
    context = {
        'listas_precios': listas_precios,
        'tipos_cliente': tipos_cliente,
    }
    
    return render(request, 'clientes/crear_cliente.html', context)


@login_required
@require_http_methods(["POST"])
def crear_usuario_web_cliente(request, cliente_id):
    """Crear usuario web para un cliente existente"""
    
    try:
        cliente = get_object_or_404(Cliente, pk=cliente_id)
        
        # Verificar si ya tiene usuario
        if hasattr(cliente, 'usuario_web'):
            return JsonResponse({
                'success': False,
                'error': 'Este cliente ya tiene un usuario web asignado'
            })
        
        usuario = request.POST.get('usuario')
        contrasena = request.POST.get('contrasena')
        
        if not usuario or not contrasena:
            return JsonResponse({
                'success': False,
                'error': 'Usuario y contraseña son requeridos'
            })
        
        # Verificar que el usuario no exista
        if UsuariosWebClientes.objects.filter(usuario=usuario).exists():
            return JsonResponse({
                'success': False,
                'error': 'El nombre de usuario ya está en uso'
            })
        
        # Hash de contraseña
        contrasena_hash = bcrypt.hashpw(
            contrasena.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
        
        # Crear usuario web
        usuario_web = UsuariosWebClientes.objects.create(
            id_cliente=cliente,
            usuario=usuario,
            contrasena_hash=contrasena_hash,
            activo=True
        )
        
        return JsonResponse({
            'success': True,
            'mensaje': f'Usuario web creado: {usuario}'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


# ============================================================================
# PORTAL WEB DE CLIENTES
# ============================================================================

def portal_login_view(request):
    """Vista de login para clientes con rate limiting, CAPTCHA y auditoría"""
    print('DEBUG: enter portal_login_view, method=', request.method)
    try:
        from django_recaptcha.fields import ReCaptchaField
        from django import forms
        from datetime import timedelta

        # Determinar si mostrar CAPTCHA (después de 2 intentos fallidos en 15 min)
        mostrar_captcha = False
        if request.method == 'GET':
            usuario_intento = request.GET.get('u', '')
            if usuario_intento:
                fecha_limite = timezone.now() - timedelta(minutes=15)
                intentos_recientes = IntentoLogin.objects.filter(
                    usuario=usuario_intento,
                    exitoso=False,
                    fecha_intento__gte=fecha_limite
                ).count()
                mostrar_captcha = intentos_recientes >= 2

        if request.method == 'POST':
            usuario = request.POST.get('usuario', '').strip()
            contrasena = request.POST.get('contrasena', '')

            if not usuario or not contrasena:
                messages.error(request, 'Usuario y contraseña son requeridos')
                return render(request, 'portal/login.html', {'mostrar_captcha': mostrar_captcha})

            # Verificar si debe mostrar CAPTCHA
            fecha_limite = timezone.now() - timedelta(minutes=15)
            intentos_recientes = IntentoLogin.objects.filter(
                usuario=usuario,
                exitoso=False,
                fecha_intento__gte=fecha_limite
            ).count()

            requiere_captcha = intentos_recientes >= 2

            # Validar CAPTCHA si es necesario
            if requiere_captcha:
                from django_recaptcha.client import RecaptchaResponse
                from django_recaptcha.client import submit as recaptcha_submit

                recaptcha_response = request.POST.get('g-recaptcha-response', '')
                if not recaptcha_response:
                    messages.error(request, 'Por favor completa el CAPTCHA')
                    return render(request, 'portal/login.html', {'mostrar_captcha': True})

                # Verificar CAPTCHA
                ip_address = request.META.get('REMOTE_ADDR')
                result = recaptcha_submit(
                    recaptcha_response,
                    settings.RECAPTCHA_PRIVATE_KEY,
                    ip_address
                )

                if not result.is_valid:
                    messages.error(request, 'CAPTCHA inválido. Por favor inténtalo de nuevo.')
                    return render(request, 'portal/login.html', {'mostrar_captcha': True})

            # Verificar rate limiting
            bloqueado, intentos_restantes, minutos_bloqueo, motivo = verificar_rate_limit(usuario, request)

            if bloqueado:
                if minutos_bloqueo:
                    messages.error(request, f'Cuenta bloqueada temporalmente por {minutos_bloqueo} minutos. Demasiados intentos fallidos.')

                    # Notificar por email si hay un cliente asociado
                    try:
                        usuario_web = UsuariosWebClientes.objects.select_related('id_cliente').get(usuario=usuario)
                        notificar_cuenta_bloqueada(usuario_web.id_cliente, request, 'Demasiados intentos fallidos')
                    except UsuariosWebClientes.DoesNotExist:
                        pass
                else:
                    messages.error(request, f'Cuenta bloqueada: {motivo}')
                registrar_intento_login(usuario, request, exitoso=False, motivo_fallo='Cuenta bloqueada')
                return render(request, 'portal/login.html', {'mostrar_captcha': requiere_captcha})

            try:
                usuario_web = UsuariosWebClientes.objects.select_related('id_cliente').get(
                    usuario=usuario,
                    activo=True
                )

                # Verificar contraseña
                if bcrypt.checkpw(contrasena.encode('utf-8'), usuario_web.contrasena_hash.encode('utf-8')):
                    # Verificar restricciones horarias PRIMERO
                    puede_acceder, mensaje_restriccion = verificar_acceso_horario(usuario, 'CLIENTE_WEB')
                    if not puede_acceder:
                        registrar_intento_login(usuario, request, exitoso=False, motivo_fallo='Acceso fuera de horario')
                        messages.error(request, mensaje_restriccion)
                        return render(request, 'portal/login.html', {'mostrar_captcha': requiere_captcha})

                    # Contraseña correcta - verificar si requiere 2FA
                    if verificar_2fa_requerido(usuario, 'CLIENTE_WEB'):
                        # Guardar datos temporales para después del 2FA
                        request.session['2fa_pendiente'] = True
                        request.session['2fa_usuario'] = usuario
                        request.session['2fa_cliente_id'] = usuario_web.id_cliente.id_cliente

                        # Registrar intento exitoso (password correcto)
                        registrar_intento_login(usuario, request, exitoso=True)

                        # Auditoría
                        registrar_auditoria(
                            request=request,
                            operacion='LOGIN_PASSWORD_OK',
                            tipo_usuario='CLIENTE_WEB',
                            descripcion=f'Password correcto, esperando 2FA para {usuario}'
                        )

                        # Redirigir a verificación 2FA
                        return redirect('pos:verificar_2fa')

                    # No requiere 2FA o no está activo - login completo
                    # Login exitoso
                    registrar_intento_login(usuario, request, exitoso=True)

                    # Análisis de patrones y anomalías
                    actualizar_patron_acceso(usuario, 'CLIENTE_WEB', request)
                    tiene_anomalias, anomalias = detectar_anomalias_acceso(usuario, request)

                    # Detectar múltiples sesiones
                    multiples, num_sesiones = detectar_multiples_sesiones(usuario)
                    if multiples:
                        messages.warning(request, f'⚠️ Tienes {num_sesiones} sesiones activas simultáneas')

                    # Registrar sesión activa
                    registrar_sesion_activa(usuario, 'CLIENTE_WEB', request.session.session_key, request)

                    # Notificar si es una IP nueva
                    notificar_login_nueva_ip(usuario_web.id_cliente, request)

                    # Actualizar último acceso
                    usuario_web.ultimo_acceso = timezone.now()
                    usuario_web.save(update_fields=['ultimo_acceso'])

                    # Guardar en sesión
                    request.session['cliente_id'] = usuario_web.id_cliente.id_cliente
                    request.session['cliente_usuario'] = usuario_web.usuario

                    # Auditoría
                    registrar_auditoria(
                        request=request,
                        operacion='LOGIN_PORTAL',
                        tipo_usuario='CLIENTE_WEB',
                        descripcion=f'Login exitoso al portal de clientes'
                    )

                    mensaje_bienvenida = f'¡Bienvenido {usuario_web.id_cliente.nombres}!'
                    if tiene_anomalias:
                        mensaje_bienvenida += ' ⚠️ Se detectaron accesos inusuales.'

                    messages.success(request, mensaje_bienvenida)
                    return redirect('clientes:portal_dashboard')
                else:
                    # Contraseña incorrecta
                    registrar_intento_login(usuario, request, exitoso=False, motivo_fallo='Contraseña incorrecta')

                    # Notificar si hay 3 o más intentos fallidos
                    if intentos_restantes <= 2:
                        notificar_intentos_sospechosos(usuario_web.id_cliente, request, 5 - intentos_restantes)
                        messages.error(request, f'Contraseña incorrecta. Te quedan {intentos_restantes} intentos antes del bloqueo.')
                    else:
                        messages.error(request, 'Contraseña incorrecta')

            except UsuariosWebClientes.DoesNotExist:
                # Usuario no foundrado
                registrar_intento_login(usuario, request, exitoso=False, motivo_fallo='Usuario no existe')
                messages.error(request, 'Usuario no encontrado o inactivo')

        # GET request o después de error
        context = {
            'RECAPTCHA_PUBLIC_KEY': getattr(settings, 'RECAPTCHA_PUBLIC_KEY', '')
        }

        # Determinar si mostrar CAPTCHA para GET o POST (se comparte la lógica)
        usuario_para_context = ''
        if request.method == 'POST':
            usuario_para_context = request.POST.get('usuario', '').strip()
        else:
            usuario_para_context = request.GET.get('u', '')

        if usuario_para_context:
            fecha_limite = timezone.now() - timedelta(minutes=15)
            intentos_recientes = IntentoLogin.objects.filter(
                usuario=usuario_para_context,
                exitoso=False,
                fecha_intento__gte=fecha_limite
            ).count()
            context['mostrar_captcha'] = intentos_recientes >= 2

        print('DEBUG: portal_login_view about to render portal/login.html, context_keys=', list(context.keys()))
        return render(request, 'portal/login.html', context)

    except Exception as _exc:
        import traceback
        print('ERROR in portal_login_view:', _exc)
        traceback.print_exc()
        # Asegurar que la vista retorne un HttpResponse en caso de error (temporal)
        err_context = {
            'RECAPTCHA_PUBLIC_KEY': getattr(settings, 'RECAPTCHA_PUBLIC_KEY', ''),
            'mostrar_captcha': False,
            'error_internal': str(_exc)
        }
        return render(request, 'portal/login.html', err_context)

    # (return handled inside try or in except fallback)


def portal_logout_view(request):
    """Cerrar sesión del portal de clientes"""
    cliente_usuario = request.session.get('cliente_usuario', 'Desconocido')
    session_key = request.session.session_key
    
    # Cerrar sesión activa
    if session_key:
        cerrar_sesion(session_key)
    
    # Auditoría
    registrar_auditoria(
        request=request,
        operacion='LOGOUT_PORTAL',
        tipo_usuario='CLIENTE_WEB',
        descripcion=f'Cierre de sesión del portal'
    )
    
    request.session.flush()
    messages.success(request, 'Sesión cerrada exitosamente')
    return redirect('clientes:portal_login')


def portal_dashboard_view(request):
    """Dashboard del portal de clientes"""
    
    # Verificar sesión
    cliente_id = request.session.get('cliente_id')
    if not cliente_id:
        # Redirigir a login usando URL directa
        response = HttpResponse()
        response.status_code = 302
        response['Location'] = '/clientes/login/'
        return response
    
    cliente_usuario = request.session.get('cliente_usuario', 'Desconocido')
    
    # Verificar consistencia de User-Agent (prevenir session hijacking)
    es_consistente, mensaje_alerta = verificar_user_agent_consistente(request, cliente_usuario)
    if not es_consistente:
        # Cerrar sesión por seguridad
        request.session.flush()
        messages.error(request, mensaje_alerta)
        # Enviar alerta crítica
        enviar_alerta_anomalia_critica(
            cliente_usuario,
            'CAMBIO_USER_AGENT',
            'Posible secuestro de sesión detectado - User-Agent cambió durante sesión activa',
            request
        )
        return redirect('/clientes/login/')
    
    cliente = get_object_or_404(Cliente, pk=cliente_id)
    
    # Obtener hijos
    hijos = Hijo.objects.filter(id_cliente_responsable=cliente).prefetch_related('tarjetas')
    
    # Calcular saldos totales
    saldo_total = Tarjeta.objects.filter(
        id_hijo__id_cliente_responsable=cliente
    ).aggregate(total=Sum('saldo'))['total'] or Decimal('0')
    
    # Consumos recientes (últimos 30 días)
    fecha_desde = timezone.now() - timedelta(days=30)
    consumos_recientes = Ventas.objects.filter(
        id_tarjeta__id_hijo__id_cliente_responsable=cliente,
        fecha_venta__gte=fecha_desde
    ).select_related('id_tarjeta__id_hijo').order_by('-fecha_venta')[:10]
    
    # Almuerzos del mes actual
    mes_actual = timezone.now().month
    anio_actual = timezone.now().year
    
    almuerzos_mes = RegistroConsumoAlmuerzo.objects.filter(
        id_hijo__id_cliente_responsable=cliente,
        fecha_consumo__month=mes_actual,
        fecha_consumo__year=anio_actual,
        estado='CONSUMIDO'
    ).count()
    
    context = {
        'cliente': cliente,
        'hijos': hijos,
        'saldo_total': saldo_total,
        'consumos_recientes': consumos_recientes,
        'almuerzos_mes': almuerzos_mes,
    }
    
    return render(request, 'portal/dashboard.html', context)


def portal_consumos_hijo_view(request, hijo_id):
    """Ver consumos detallados de un hijo"""
    
    cliente_id = request.session.get('cliente_id')
    if not cliente_id:
        return redirect('pos:portal_login')
    
    hijo = get_object_or_404(
        Hijo,
        pk=hijo_id,
        id_cliente_responsable_id=cliente_id
    )
    
    # Filtros
    fecha_desde = request.GET.get('desde')
    fecha_hasta = request.GET.get('hasta')
    
    # Consumos en cantina (ventas)
    ventas = Ventas.objects.filter(
        id_tarjeta__id_hijo=hijo
    ).select_related('id_tarjeta', 'id_empleado')
    
    if fecha_desde:
        ventas = ventas.filter(fecha_venta__gte=fecha_desde)
    if fecha_hasta:
        ventas = ventas.filter(fecha_venta__lte=fecha_hasta)
    
    ventas = ventas.order_by('-fecha_venta')
    
    # Almuerzos
    almuerzos = RegistroConsumoAlmuerzo.objects.filter(
        id_hijo=hijo
    )
    
    if fecha_desde:
        almuerzos = almuerzos.filter(fecha_consumo__gte=fecha_desde)
    if fecha_hasta:
        almuerzos = almuerzos.filter(fecha_consumo__lte=fecha_hasta)
    
    almuerzos = almuerzos.order_by('-fecha_consumo')
    
    # Paginación
    paginator = Paginator(list(ventas) + list(almuerzos), 30)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'hijo': hijo,
        'page_obj': page_obj,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
    }
    
    return render(request, 'portal/consumos_hijo.html', context)


def portal_recargas_view(request):
    """Ver historial de recargas"""
    
    cliente_id = request.session.get('cliente_id')
    if not cliente_id:
        return redirect('clientes:portal_login')
    
    recargas = CargasSaldo.objects.filter(
        id_tarjeta__id_hijo__id_cliente_responsable_id=cliente_id
    ).select_related('id_tarjeta__id_hijo', 'id_empleado').order_by('-fecha_carga')
    
    # Paginación
    paginator = Paginator(recargas, 30)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    
    return render(request, 'portal/recargas.html', context)


def portal_cambiar_password_view(request):
    """Cambiar contraseña del cliente con auditoría"""
    
    cliente_id = request.session.get('cliente_id')
    if not cliente_id:
        return redirect('pos:portal_login')
    
    if request.method == 'POST':
        password_actual = request.POST.get('password_actual')
        password_nueva = request.POST.get('password_nueva')
        password_confirmar = request.POST.get('password_confirmar')
        
        try:
            usuario_web = UsuariosWebClientes.objects.get(id_cliente_id=cliente_id)
            
            # Verificar contraseña actual
            if not bcrypt.checkpw(password_actual.encode('utf-8'), usuario_web.contrasena_hash.encode('utf-8')):
                messages.error(request, 'La contraseña actual es incorrecta')
                registrar_auditoria(
                    request=request,
                    operacion='CAMBIO_PASSWORD_FALLIDO',
                    tipo_usuario='CLIENTE_WEB',
                    resultado='FALLIDO',
                    descripcion='Intento fallido de cambio de contraseña',
                    mensaje_error='Contraseña actual incorrecta'
                )
                return redirect('pos:portal_cambiar_password')
            
            # Verificar que las contraseñas nuevas coincidan
            if password_nueva != password_confirmar:
                messages.error(request, 'Las contraseñas nuevas no coinciden')
                return redirect('pos:portal_cambiar_password')
            
            # Validar longitud mínima
            if len(password_nueva) < 8:
                messages.error(request, 'La contraseña debe tener al menos 8 caracteres')
                return redirect('pos:portal_cambiar_password')
            
            # Validar complejidad
            if not any(c.isupper() for c in password_nueva):
                messages.error(request, 'La contraseña debe contener al menos una mayúscula')
                return redirect('pos:portal_cambiar_password')
            
            if not any(c.islower() for c in password_nueva):
                messages.error(request, 'La contraseña debe contener al menos una minúscula')
                return redirect('pos:portal_cambiar_password')
            
            if not any(c.isdigit() for c in password_nueva):
                messages.error(request, 'La contraseña debe contener al menos un número')
                return redirect('pos:portal_cambiar_password')
            
            # Hash de la nueva contraseña
            nuevo_hash = bcrypt.hashpw(
                password_nueva.encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8')
            
            # Actualizar contraseña
            usuario_web.contrasena_hash = nuevo_hash
            usuario_web.save(update_fields=['contrasena_hash'])
            
            # Auditoría exitosa
            registrar_auditoria(
                request=request,
                operacion='CAMBIO_PASSWORD',
                tipo_usuario='CLIENTE_WEB',
                tabla_afectada='usuarios_web_clientes',
                id_registro=usuario_web.id_cliente.id_cliente,
                descripcion=f'Cambio de contraseña exitoso para {usuario_web.usuario}'
            )
            
            messages.success(request, 'Contraseña actualizada exitosamente')
            return redirect('pos:portal_dashboard')
            
        except UsuariosWebClientes.DoesNotExist:
            messages.error(request, 'Usuario no encontrado')
            return redirect('pos:portal_login')
    
    return render(request, 'portal/cambiar_password.html')


def portal_restricciones_hijo_view(request, hijo_id):
    """Gestionar restricciones de compra para un hijo"""
    
    cliente_id = request.session.get('cliente_id')
    if not cliente_id:
        return redirect('pos:portal_login')
    
    hijo = get_object_or_404(
        Hijo,
        pk=hijo_id,
        id_cliente_responsable_id=cliente_id
    )
    
    if request.method == 'POST':
        restricciones_anterior = hijo.restricciones_compra
        restricciones = request.POST.get('restricciones', '').strip()
        hijo.restricciones_compra = restricciones if restricciones else None
        hijo.save(update_fields=['restricciones_compra'])
        
        # Auditoría
        registrar_auditoria(
            request=request,
            operacion='ACTUALIZAR_RESTRICCIONES',
            tipo_usuario='CLIENTE_WEB',
            tabla_afectada='hijos',
            id_registro=hijo.id_hijo,
            descripcion=f'Actualización de restricciones para {hijo.nombre_completo}',
            datos_anteriores={'restricciones': restricciones_anterior},
            datos_nuevos={'restricciones': restricciones}
        )
        
        messages.success(request, 'Restricciones actualizadas exitosamente')
        return redirect('pos:portal_dashboard')
    
    context = {
        'hijo': hijo,
    }
    
    return render(request, 'portal/restricciones_hijo.html', context)


def portal_recuperar_password_view(request):
    """Solicitar recuperación de contraseña"""
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        
        if not email:
            messages.error(request, 'Por favor ingrese su email')
            return render(request, 'portal/recuperar_password.html')
        
        try:
            # Buscar cliente por email
            cliente = Cliente.objects.get(email__iexact=email)
            
            # Verificar que tenga usuario web
            try:
                usuario_web = UsuariosWebClientes.objects.get(id_cliente=cliente)
                
                # Generar token
                token = generar_token_recuperacion(cliente, request)
                
                if token:
                    # Construir URL de recuperación
                    reset_url = request.build_absolute_uri(f'/pos/portal/reset-password/{token}/')
                    
                    # Enviar email (simulado por ahora - configurar SMTP en producción)
                    try:
                        send_mail(
                            subject='Recuperación de Contraseña - Cantina Tita',
                            message=f'''Hola {cliente.nombres},

Has solicitado recuperar tu contraseña del portal de clientes.

Haz clic en el siguiente enlace para crear una nueva contraseña:
{reset_url}

Este enlace expira en 24 horas.

Si no solicitaste este cambio, ignora este mensaje.

Saludos,
Equipo Cantina Tita''',
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[email],
                            fail_silently=False,
                        )
                        messages.success(request, f'Se ha enviado un enlace de recuperación a {email}')
                    except Exception as e:
                        # Si falla el email, mostrar el enlace (solo para desarrollo)
                        messages.warning(request, f'Email no configurado. Enlace de recuperación: {reset_url}')
                        print(f"Error enviando email: {e}")
                else:
                    messages.error(request, 'Error al generar el enlace de recuperación')
                    
            except UsuariosWebClientes.DoesNotExist:
                messages.error(request, 'Este cliente no tiene acceso al portal web')
                
        except Cliente.DoesNotExist:
            # No revelar si el email existe o no (seguridad)
            messages.success(request, f'Si el email {email} está registrado, recibirás un enlace de recuperación')
        
        return redirect('pos:portal_login')
    
    return render(request, 'portal/recuperar_password.html')


def portal_reset_password_view(request, token):
    """Restablecer contraseña con token"""
    
    # Verificar token
    valido, token_obj, mensaje_error = verificar_token_recuperacion(token)
    
    if not valido:
        messages.error(request, mensaje_error)
        return redirect('pos:portal_login')
    
    if request.method == 'POST':
        password_nueva = request.POST.get('password_nueva')
        password_confirmar = request.POST.get('password_confirmar')
        
        # Validaciones
        if password_nueva != password_confirmar:
            messages.error(request, 'Las contraseñas no coinciden')
            return render(request, 'portal/reset_password.html', {'token': token})
        
        if len(password_nueva) < 8:
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres')
            return render(request, 'portal/reset_password.html', {'token': token})
        
        if not any(c.isupper() for c in password_nueva):
            messages.error(request, 'Debe contener al menos una mayúscula')
            return render(request, 'portal/reset_password.html', {'token': token})
        
        if not any(c.islower() for c in password_nueva):
            messages.error(request, 'Debe contener al menos una minúscula')
            return render(request, 'portal/reset_password.html', {'token': token})
        
        if not any(c.isdigit() for c in password_nueva):
            messages.error(request, 'Debe contener al menos un número')
            return render(request, 'portal/reset_password.html', {'token': token})
        
        try:
            # Obtener usuario web
            usuario_web = UsuariosWebClientes.objects.get(id_cliente=token_obj.id_cliente)
            
            # Hash de la nueva contraseña
            nuevo_hash = bcrypt.hashpw(
                password_nueva.encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8')
            
            # Actualizar contraseña
            usuario_web.contrasena_hash = nuevo_hash
            usuario_web.save(update_fields=['contrasena_hash'])
            
            # Marcar token como usado
            marcar_token_usado(token)
            
            # Auditoría
            registrar_auditoria(
                request=request,
                operacion='RESET_PASSWORD',
                tipo_usuario='CLIENTE_WEB',
                tabla_afectada='usuarios_web_clientes',
                id_registro=usuario_web.id_cliente.id_cliente,
                descripcion=f'Recuperación de contraseña completada para {usuario_web.usuario}'
            )
            
            messages.success(request, '¡Contraseña actualizada! Ya puedes iniciar sesión')
            return redirect('pos:portal_login')
            
        except UsuariosWebClientes.DoesNotExist:
            messages.error(request, 'Usuario no encontrado')
            return redirect('pos:portal_login')
    
    context = {
        'token': token,
        'cliente': token_obj.id_cliente
    }
    
    return render(request, 'portal/reset_password.html', context)


# ============================================================================
# AUTENTICACIÓN 2FA (Two-Factor Authentication)
# ============================================================================

def configurar_2fa_view(request):
    """Vista para configurar 2FA para el cliente"""
    if 'cliente_id' not in request.session:
        return redirect('pos:portal_login')
    
    cliente_usuario = request.session.get('cliente_usuario')
    
    # Verificar si ya tiene 2FA activo
    if verificar_2fa_requerido(cliente_usuario, 'CLIENTE_WEB'):
        context = {
            'paso': 'ya_activo'
        }
        return render(request, 'portal/configurar_2fa.html', context)
    
    # Generar configuración 2FA
    secret_key, backup_codes, qr_uri = configurar_2fa_usuario(cliente_usuario, 'CLIENTE_WEB')
    
    if not secret_key:
        messages.error(request, 'Error al generar configuración 2FA')
        return redirect('pos:portal_dashboard')
    
    # Generar imagen QR
    qr_code_data = generar_qr_code_2fa(qr_uri)
    
    context = {
        'paso': 'generar',
        'secret_key': secret_key,
        'backup_codes': backup_codes,
        'qr_code_data': qr_code_data
    }
    
    return render(request, 'portal/configurar_2fa.html', context)


def activar_2fa_view(request):
    """Activar 2FA después de verificar el primer código"""
    if request.method != 'POST':
        return redirect('pos:configurar_2fa')
    
    if 'cliente_id' not in request.session:
        return redirect('pos:portal_login')
    
    cliente_usuario = request.session.get('cliente_usuario')
    codigo = request.POST.get('codigo', '').strip()
    
    if len(codigo) != 6 or not codigo.isdigit():
        messages.error(request, 'Código inválido. Debe ser de 6 dígitos numéricos')
        return redirect('pos:configurar_2fa')
    
    # Intentar activar 2FA
    if activar_2fa_usuario(cliente_usuario, 'CLIENTE_WEB', codigo):
        # Auditoría
        registrar_auditoria(
            request=request,
            operacion='ACTIVAR_2FA',
            tipo_usuario='CLIENTE_WEB',
            descripcion=f'2FA activado para {cliente_usuario}'
        )
        messages.success(request, '✅ ¡2FA activado exitosamente! Tu cuenta ahora está más segura')
        return redirect('pos:portal_dashboard')
    else:
        messages.error(request, 'Código incorrecto. Por favor verifica el código en tu aplicación')
        return redirect('pos:configurar_2fa')


def verificar_2fa_view(request):
    """Vista para verificar código 2FA después del login"""
    if request.method != 'POST':
        return render(request, 'portal/verificar_2fa.html')
    
    # Verificar que hay una sesión pendiente de 2FA
    if '2fa_pendiente' not in request.session:
        messages.error(request, 'Sesión expirada. Por favor inicia sesión nuevamente')
        return redirect('pos:portal_login')
    
    cliente_usuario = request.session.get('2fa_usuario')
    codigo = request.POST.get('codigo', '').strip()
    
    # Validar formato del código (6 dígitos TOTP o 8 dígitos backup)
    if not codigo.isdigit() or len(codigo) not in [6, 8]:
        messages.error(request, 'Código inválido')
        return render(request, 'portal/verificar_2fa.html')
    
    # Verificar rate limiting 2FA
    bloqueado, intentos_restantes, mensaje_bloqueo = verificar_rate_limit_2fa(cliente_usuario, 'CLIENTE_WEB')
    if bloqueado:
        messages.error(request, mensaje_bloqueo)
        # Enviar alerta crítica
        enviar_alerta_anomalia_critica(
            cliente_usuario,
            'INTENTOS_2FA_EXCESIVOS',
            f'Usuario {cliente_usuario} bloqueado por demasiados intentos fallidos de 2FA',
            request
        )
        return render(request, 'portal/verificar_2fa.html')
    
    # Determinar tipo de código
    tipo_codigo = 'TOTP' if len(codigo) == 6 else 'BACKUP'
    
    # Verificar código
    if verificar_codigo_2fa(cliente_usuario, 'CLIENTE_WEB', codigo):
        # Código correcto - registrar intento exitoso
        registrar_intento_2fa(cliente_usuario, 'CLIENTE_WEB', request, codigo, exitoso=True, tipo_codigo=tipo_codigo)
        
        cliente_id = request.session.get('2fa_cliente_id')
        
        # Limpiar datos temporales
        del request.session['2fa_pendiente']
        del request.session['2fa_usuario']
        del request.session['2fa_cliente_id']
        
        # Establecer sesión completa
        request.session['cliente_id'] = cliente_id
        request.session['cliente_usuario'] = cliente_usuario
        
        # Renovar token de sesión para prevenir session fixation
        renovar_token_sesion(request, cliente_usuario)
        
        # Auditoría
        registrar_auditoria(
            request=request,
            operacion='VERIFICAR_2FA',
            tipo_usuario='CLIENTE_WEB',
            descripcion=f'Verificación 2FA exitosa para {cliente_usuario} ({tipo_codigo})'
        )
        
        messages.success(request, 'Verificación exitosa. ¡Bienvenido!')
        return redirect('pos:portal_dashboard')
    else:
        # Código incorrecto - registrar intento fallido
        registrar_intento_2fa(cliente_usuario, 'CLIENTE_WEB', request, codigo, exitoso=False, tipo_codigo=tipo_codigo)
        
        # Mostrar intentos restantes
        if intentos_restantes > 1:
            messages.error(request, f'Código incorrecto. Te quedan {intentos_restantes} intentos')
        else:
            messages.error(request, f'Código incorrecto. Te queda {intentos_restantes} intento antes del bloqueo')
        
        return render(request, 'portal/verificar_2fa.html')


def deshabilitar_2fa_view(request):
    """Deshabilitar 2FA para el usuario actual"""
    if request.method != 'POST':
        return redirect('pos:portal_dashboard')
    
    if 'cliente_id' not in request.session:
        return redirect('pos:portal_login')
    
    cliente_usuario = request.session.get('cliente_usuario')
    
    if deshabilitar_2fa_usuario(cliente_usuario, 'CLIENTE_WEB'):
        # Auditoría
        registrar_auditoria(
            request=request,
            operacion='DESHABILITAR_2FA',
            tipo_usuario='CLIENTE_WEB',
            descripcion=f'2FA deshabilitado para {cliente_usuario}'
        )
        messages.warning(request, '⚠️ 2FA deshabilitado. Tu cuenta es menos segura ahora')
    else:
        messages.error(request, 'No se pudo deshabilitar 2FA')
    
    return redirect('pos:portal_dashboard')


# ============================================================================
# FUNCIONALIDADES DE CARGA DE SALDO Y PAGOS CON METREPAY
# ============================================================================

def portal_cargar_saldo_view(request):
    """Vista para cargar saldo a tarjetas de hijos usando MetrePay"""
    
    cliente_id = request.session.get('cliente_id')
    if not cliente_id:
        return redirect('pos:portal_login')
    
    cliente = get_object_or_404(Cliente, pk=cliente_id)
    
    # Obtener hijos con tarjetas activas
    hijos_con_tarjetas = Hijo.objects.filter(
        id_cliente_responsable=cliente,
        activo=True
    ).select_related('tarjetas').filter(tarjetas__estado='Activa')
    
    if request.method == 'POST':
        hijo_id = request.POST.get('hijo_id')
        monto = request.POST.get('monto')
        metodo_pago = request.POST.get('metodo_pago')  # 'tarjeta_credito', 'tarjeta_debito', etc.
        
        try:
            hijo = Hijo.objects.get(pk=hijo_id, id_cliente_responsable=cliente)
            tarjeta = hijo.tarjetas.first()  # Asumiendo una tarjeta por hijo
            
            if not tarjeta:
                messages.error(request, 'El hijo seleccionado no tiene una tarjeta activa')
                return redirect('pos:portal_cargar_saldo')
            
            monto_decimal = Decimal(monto)
            if monto_decimal <= 0:
                messages.error(request, 'El monto debe ser mayor a 0')
                return redirect('pos:portal_cargar_saldo')
            
            # Aquí integrar con MetrePay API
            # Por ahora, simular la transacción
            exito, referencia, payment_url, custom_id = procesar_pago_metrepay(monto_decimal, metodo_pago, request)
            
            if exito:
                # Crear registro de carga de saldo
                with transaction.atomic():
                    carga_saldo = CargasSaldo.objects.create(
                        nro_tarjeta=tarjeta,
                        id_cliente_origen=cliente,
                        fecha_carga=timezone.now(),
                        monto_cargado=monto_decimal,
                        referencia=referencia,
                        estado='PENDIENTE',
                        custom_identifier=custom_id,
                        pay_request_id=referencia  # Temporal hasta confirmación
                    )
                    
                    # Actualizar saldo de la tarjeta
                    tarjeta.saldo_actual += int(monto_decimal)
                    tarjeta.save()
                
                messages.success(request, f'Saldo cargado exitosamente. Nuevo saldo: Gs. {tarjeta.saldo_actual:,}')
                
                # Auditoría
                registrar_auditoria(
                    request=request,
                    operacion='CARGA_SALDO',
                    tipo_usuario='CLIENTE_WEB',
                    descripcion=f'Carga de Gs. {monto_decimal} a tarjeta {tarjeta.nro_tarjeta}'
                )

                # Mostrar URL de pago si está disponible
                if payment_url:
                    messages.info(request, f'Complete el pago en: <a href="{payment_url}" target="_blank">{payment_url}</a>')
            else:
                messages.error(request, 'Error al procesar el pago. Intente nuevamente.')
                
        except Hijo.DoesNotExist:
            messages.error(request, 'Hijo no encontrado')
        except Exception as e:
            messages.error(request, f'Error inesperado: {str(e)}')
        
        return redirect('pos:portal_cargar_saldo')
    
    context = {
        'cliente': cliente,
        'hijos_con_tarjetas': hijos_con_tarjetas,
    }
    
    return render(request, 'portal/cargar_saldo.html', context)


def portal_pagos_view(request):
    """Vista para realizar pagos de deudas pendientes usando MetrePay"""
    
    cliente_id = request.session.get('cliente_id')
    if not cliente_id:
        return redirect('pos:portal_login')
    
    cliente = get_object_or_404(Cliente, pk=cliente_id)
    
    # Obtener deudas pendientes (ventas con saldo pendiente)
    deudas = Ventas.objects.filter(
        id_cliente=cliente,
        saldo_pendiente__gt=0
    ).select_related('id_tarjeta__id_hijo').order_by('-fecha_venta')
    
    total_deuda = deudas.aggregate(total=Sum('saldo_pendiente'))['total'] or Decimal('0')
    
    if request.method == 'POST':
        venta_ids = request.POST.getlist('venta_ids')
        monto_total = Decimal(request.POST.get('monto_total', '0'))
        metodo_pago = request.POST.get('metodo_pago')
        
        if not venta_ids:
            messages.error(request, 'Seleccione al menos una deuda para pagar')
            return redirect('pos:portal_pagos')
        
        # Verificar que el monto no exceda la deuda total
        if monto_total > total_deuda:
            messages.error(request, 'El monto a pagar no puede exceder la deuda total')
            return redirect('pos:portal_pagos')
        
        # Procesar pago con MetrePay
        exito, referencia, payment_url, custom_id = procesar_pago_metrepay(monto_total, metodo_pago, request, tipo_pago='PAGO_DEUDAS', venta_ids=venta_ids)
        
        if exito:
            with transaction.atomic():
                # Actualizar cada venta seleccionada
                for venta_id in venta_ids:
                    try:
                        venta = Ventas.objects.get(pk=venta_id, id_cliente=cliente, saldo_pendiente__gt=0)
                        # Aquí lógica para distribuir el pago entre las ventas
                        # Por simplicidad, asumir pago completo de las seleccionadas
                        venta.saldo_pendiente = 0
                        venta.estado_pago = 'PAGADA'
                        venta.save()
                    except Ventas.DoesNotExist:
                        continue
                
                # Crear registro de pago (si hay un modelo para esto)
                # PagosCliente.objects.create(...)  # Si existe
                
            messages.success(request, f'Pago procesado exitosamente. Total pagado: Gs. {monto_total:,}')
            
            # Mostrar URL de pago si está disponible
            if payment_url:
                messages.info(request, f'Complete el pago en: <a href="{payment_url}" target="_blank">{payment_url}</a>')
            
            # Auditoría
            registrar_auditoria(
                request=request,
                operacion='PAGO_DEUDAS',
                tipo_usuario='CLIENTE_WEB',
                descripcion=f'Pago de Gs. {monto_total} por {len(venta_ids)} deudas'
            )
        else:
            messages.error(request, 'Error al procesar el pago. Intente nuevamente.')
        
        return redirect('pos:portal_pagos')
    
    context = {
        'cliente': cliente,
        'deudas': deudas,
        'total_deuda': total_deuda,
    }
    
    return render(request, 'portal/pagos.html', context)


def procesar_pago_metrepay(monto, metodo_pago, request, tipo_pago='CARGA_SALDO', venta_ids=None):
    """
    Función para procesar pagos con MetrePay API
    Basado en colección de Postman proporcionada
    Retorna (exito, referencia, payment_url)
    """
    try:
        # Configuración de MetrePay (debería estar en settings)
        METREPAY_BASE_URL = getattr(settings, 'METREPAY_BASE_URL', 'https://test.metrepay.com/api')
        METREPAY_API_TOKEN = getattr(settings, 'METREPAY_API_TOKEN', '')

        if not METREPAY_API_TOKEN:
            # Simular éxito para desarrollo
            import uuid
            referencia = f"SIM-{uuid.uuid4().hex[:8].upper()}"
            payment_url = f"https://test.metrepay.com/pay/{referencia}"
            if tipo_pago == 'CARGA_SALDO':
                custom_id = f"CARGA-{timezone.now().strftime('%Y%m%d%H%M%S')}"
            else:
                venta_ids_str = ','.join(map(str, venta_ids or []))
                custom_id = f"PAGO-{venta_ids_str}"
            return True, referencia, payment_url, custom_id

        # Cliente MetrePay simplificado
        headers = {
            'Api-Token': METREPAY_API_TOKEN,
            'Content-Type': 'application/json',
        }

        # Preparar datos del cliente
        cliente = request.session.get('cliente_usuario', 'Cliente')

        # Generar customIdentifier según el tipo de pago
        if tipo_pago == 'CARGA_SALDO':
            custom_id = f"CARGA-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        elif tipo_pago == 'PAGO_DEUDAS':
            venta_ids_str = ','.join(map(str, venta_ids or []))
            custom_id = f"PAGO-{venta_ids_str}"
        else:
            custom_id = f"OTRO-{timezone.now().strftime('%Y%m%d%H%M%S')}"

        # Crear pago único usando endpoint /saleitems/add
        payload = {
            "label": f"{'Carga de saldo' if tipo_pago == 'CARGA_SALDO' else 'Pago de deudas'} - {cliente}",
            "amount": int(monto),  # MetrePay espera integer
            "handleValue": f"{cliente}@cantina.com",
            "handleLabel": cliente,
            "customIdentifier": custom_id,
            "singlePayment": True,
            "creditAndDebitCard": True,
            "redirectUrl": request.build_absolute_uri('/portal/pago_exitoso/'),
        }

        endpoint = f'{METREPAY_BASE_URL}/saleitems/add'

        response = requests.post(
            endpoint,
            json=payload,
            headers=headers,
            timeout=30
        )

        if response.status_code in [200, 201]:
            data = response.json()
            # Adaptar según respuesta real de MetrePay
            payment_id = data.get('id') or data.get('paymentId') or f'MP-{timezone.now().strftime("%Y%m%d%H%M%S")}'
            payment_url = data.get('paymentUrl') or data.get('url') or f"https://test.metrepay.com/pay/{payment_id}"
            return True, payment_id, payment_url, custom_id
        else:
            print(f"Error MetrePay: {response.status_code} - {response.text}")
            return False, None, None, None

    except Exception as e:
        print(f"Error procesando pago MetrePay: {str(e)}")
        return False, None, None, None


# ============================================================================
# VISTAS DE CALLBACK PARA METREPAY
# ============================================================================

def portal_pago_exitoso_view(request):
    """Vista para mostrar confirmación de pago exitoso"""
    cliente_id = request.session.get('cliente_id')
    if not cliente_id:
        return redirect('pos:portal_login')

    cliente = get_object_or_404(Cliente, pk=cliente_id)

    # Obtener parámetros de la URL si MetrePay los envía
    payment_id = request.GET.get('payment_id', '')
    status = request.GET.get('status', '')

    context = {
        'cliente': cliente,
        'payment_id': payment_id,
        'status': status,
        'mensaje': 'Su pago está siendo procesado. Recibirá una confirmación cuando se complete.'
    }

    return render(request, 'portal/pago_exitoso.html', context)


def portal_pago_cancelado_view(request):
    """Vista para mostrar cancelación de pago"""
    cliente_id = request.session.get('cliente_id')
    if not cliente_id:
        return redirect('pos:portal_login')

    cliente = get_object_or_404(Cliente, pk=cliente_id)

    context = {
        'cliente': cliente,
        'mensaje': 'El pago ha sido cancelado. Puede intentar nuevamente cuando desee.'
    }

    return render(request, 'portal/pago_cancelado.html', context)


# ============================================================================
# WEBHOOKS PARA RECIBIR NOTIFICACIONES DE METREPAY
# ============================================================================

@require_http_methods(["POST"])
def metrepay_webhook_view(request):
    """
    Endpoint para recibir notificaciones de MetrePay
    Procesa confirmaciones de pago exitoso
    """
    try:
        # Verificar que sea una petición POST
        if request.method != 'POST':
            return JsonResponse({'error': 'Método no permitido'}, status=405)

        # Obtener datos del webhook
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)

        # Validar estructura del webhook
        event = data.get('event')
        if not event:
            return JsonResponse({'error': 'Evento no especificado'}, status=400)

        # Procesar solo eventos de pago exitoso
        if event == 'PAYMENT_SUCCESS':
            return procesar_webhook_pago_exitoso(data)
        else:
            # Otros eventos pueden ser ignorados o logged
            print(f"Evento no procesado: {event}")
            return JsonResponse({'status': 'Evento no procesado'}, status=200)

    except Exception as e:
        print(f"Error procesando webhook: {str(e)}")
        return JsonResponse({'error': 'Error interno del servidor'}, status=500)


def procesar_webhook_pago_exitoso(data):
    """
    Procesa notificación de pago exitoso desde MetrePay
    """
    try:
        webhook_data = data.get('data', {})

        # Extraer campos importantes
        pay_request_id = webhook_data.get('payRequestId')
        custom_identifier = webhook_data.get('customIdentifier')
        amount = webhook_data.get('amount')
        status_id = webhook_data.get('statusId')
        currency = webhook_data.get('currency')
        tx_id = webhook_data.get('txId')  # Nuevo campo txId

        # Validar campos requeridos
        if not all([pay_request_id, custom_identifier, amount, status_id]):
            return JsonResponse({'error': 'Campos requeridos faltantes'}, status=400)

        # Verificar que el pago esté confirmado (status_id = 200)
        if status_id != 200:
            print(f"Pago no confirmado. Status: {status_id}")
            return JsonResponse({'status': 'Pago no confirmado'}, status=200)

        # Procesar según el tipo de transacción basado en customIdentifier
        if custom_identifier.startswith('CARGA-'):
            # Es una carga de saldo
            return procesar_carga_saldo_confirmada(webhook_data, tx_id)
        elif custom_identifier.startswith('PAGO-'):
            # Es un pago de deudas
            return procesar_pago_deudas_confirmado(webhook_data, tx_id)
        else:
            print(f"Tipo de transacción no reconocido: {custom_identifier}")
            return JsonResponse({'status': 'Tipo de transacción no reconocido'}, status=200)

    except Exception as e:
        print(f"Error procesando pago exitoso: {str(e)}")
        return JsonResponse({'error': 'Error procesando pago'}, status=500)


def procesar_carga_saldo_confirmada(webhook_data, tx_id=None):
    """
    Procesa confirmación de carga de saldo
    """
    try:
        custom_identifier = webhook_data.get('customIdentifier')
        amount = Decimal(webhook_data.get('amount', '0'))
        pay_request_id = webhook_data.get('payRequestId')

        # Buscar la carga de saldo pendiente por custom_identifier
        try:
            carga_saldo = CargasSaldo.objects.get(
                custom_identifier=custom_identifier,
                estado='PENDIENTE'
            )
        except CargasSaldo.DoesNotExist:
            # Si no encuentra por custom_identifier, buscar por payRequestId si está almacenado
            try:
                carga_saldo = CargasSaldo.objects.get(
                    pay_request_id=pay_request_id,
                    estado='PENDIENTE'
                )
            except CargasSaldo.DoesNotExist:
                print(f"Carga de saldo no encontrada: {custom_identifier}")
                return JsonResponse({'status': 'Carga de saldo no encontrada'}, status=200)

        # Actualizar estado de la carga de saldo
        with transaction.atomic():
            carga_saldo.estado = 'CONFIRMADO'
            carga_saldo.fecha_confirmacion = timezone.now()
            carga_saldo.pay_request_id = pay_request_id
            if tx_id:
                carga_saldo.tx_id = tx_id  # Guardar tx_id si está disponible
            carga_saldo.save()

            # Actualizar saldo de la tarjeta
            tarjeta = carga_saldo.nro_tarjeta
            tarjeta.saldo_actual += int(amount)
            tarjeta.save()

            # Registrar auditoría
            registrar_auditoria_sistema(
                operacion='CARGA_SALDO_CONFIRMADO',
                descripcion=f'Carga confirmada: Gs. {amount} - ID: {pay_request_id} - TxID: {tx_id or "N/A"}',
                tabla_afectada='cargas_saldo',
                id_registro=carga_saldo.id_carga
            )

        print(f"Carga de saldo confirmada: {custom_identifier} - Gs. {amount} - TxID: {tx_id or 'N/A'}")
        return JsonResponse({'status': 'Carga de saldo confirmada'}, status=200)

    except Exception as e:
        print(f"Error procesando carga de saldo: {str(e)}")
        return JsonResponse({'error': 'Error procesando carga de saldo'}, status=500)


def procesar_pago_deudas_confirmado(webhook_data, tx_id=None):
    """
    Procesa confirmación de pago de deudas
    """
    try:
        custom_identifier = webhook_data.get('customIdentifier')
        amount = Decimal(webhook_data.get('amount', '0'))
        pay_request_id = webhook_data.get('payRequestId')

        # Extraer IDs de ventas del custom_identifier (formato: PAGO-venta1,venta2,venta3)
        try:
            venta_ids_str = custom_identifier.replace('PAGO-', '')
            venta_ids = [int(vid) for vid in venta_ids_str.split(',') if vid.isdigit()]
        except (ValueError, AttributeError):
            print(f"Formato de custom_identifier inválido: {custom_identifier}")
            return JsonResponse({'status': 'Formato inválido'}, status=200)

        # Procesar cada venta
        total_procesado = Decimal('0')

        with transaction.atomic():
            for venta_id in venta_ids:
                try:
                    venta = Ventas.objects.get(pk=venta_id, saldo_pendiente__gt=0)

                    # Calcular cuánto pagar de esta venta
                    # Por simplicidad, distribuir proporcionalmente
                    restante = amount - total_procesado
                    if restante <= 0:
                        break

                    pago_esta_venta = min(restante, venta.saldo_pendiente)
                    venta.saldo_pendiente -= pago_esta_venta
                    venta.estado_pago = 'PAGADA' if venta.saldo_pendiente == 0 else 'PARCIAL'
                    venta.save()

                    total_procesado += pago_esta_venta

                except Ventas.DoesNotExist:
                    continue

            # Registrar auditoría
            registrar_auditoria_sistema(
                operacion='PAGO_DEUDAS_CONFIRMADO',
                descripcion=f'Pago confirmado: Gs. {amount} - Ventas: {venta_ids} - TxID: {tx_id or "N/A"}',
                tabla_afectada='ventas'
            )

        print(f"Pago de deudas confirmado: {custom_identifier} - Gs. {amount} - TxID: {tx_id or 'N/A'}")
        return JsonResponse({'status': 'Pago de deudas confirmado'}, status=200)

    except Exception as e:
        print(f"Error procesando pago de deudas: {str(e)}")
        return JsonResponse({'error': 'Error procesando pago de deudas'}, status=500)


# ============================================================================
# WEBHOOKS PARA TIGO MONEY
# ============================================================================

@require_http_methods(["POST"])
def tigo_money_webhook_view(request):
    """
    Endpoint para recibir notificaciones de Tigo Money
    Procesa confirmaciones de pago exitoso
    """
    try:
        # Verificar que sea una petición POST
        if request.method != 'POST':
            return JsonResponse({'error': 'Método no permitido'}, status=405)

        # Obtener datos del webhook
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)

        # Validar estructura del webhook
        status = data.get('status')
        transaction_id = data.get('transactionId')
        
        if not transaction_id:
            return JsonResponse({'error': 'Transaction ID no especificado'}, status=400)

        # Procesar solo pagos completados
        if status == 'COMPLETED':
            return procesar_webhook_tigo_money_exitoso(data)
        elif status == 'FAILED':
            print(f"Pago Tigo Money fallido: {transaction_id}")
            return JsonResponse({'status': 'Pago fallido procesado'}, status=200)
        elif status == 'CANCELLED':
            print(f"Pago Tigo Money cancelado: {transaction_id}")
            return JsonResponse({'status': 'Pago cancelado procesado'}, status=200)
        else:
            print(f"Estado no procesado: {status}")
            return JsonResponse({'status': 'Estado no procesado'}, status=200)

    except Exception as e:
        print(f"Error procesando webhook Tigo Money: {str(e)}")
        return JsonResponse({'error': 'Error interno del servidor'}, status=500)


def procesar_webhook_tigo_money_exitoso(data):
    """
    Procesa notificación de pago exitoso desde Tigo Money
    """
    try:
        # Extraer campos del webhook
        transaction_id = data.get('transactionId')
        amount = Decimal(str(data.get('amount', '0')))
        phone_number = data.get('phoneNumber')
        custom_identifier = data.get('metadata', {}).get('customer', {}).get('custom_id')

        # Validar campos requeridos
        if not all([transaction_id, amount]):
            return JsonResponse({'error': 'Campos requeridos faltantes'}, status=400)

        print(f"📱 Webhook Tigo Money: {transaction_id} - Gs. {amount}")

        # Procesar según el tipo de transacción basado en customIdentifier
        if custom_identifier and custom_identifier.startswith('CARGA-'):
            return procesar_carga_saldo_tigo_confirmada(data)
        elif custom_identifier and custom_identifier.startswith('PAGO-'):
            return procesar_pago_deudas_tigo_confirmado(data)
        else:
            print(f"Tipo de transacción no reconocido: {custom_identifier}")
            return JsonResponse({'status': 'Tipo de transacción no reconocido'}, status=200)

    except Exception as e:
        print(f"Error procesando pago Tigo Money exitoso: {str(e)}")
        return JsonResponse({'error': 'Error procesando pago'}, status=500)


def procesar_carga_saldo_tigo_confirmada(webhook_data):
    """
    Procesa confirmación de carga de saldo via Tigo Money
    """
    try:
        transaction_id = webhook_data.get('transactionId')
        amount = Decimal(str(webhook_data.get('amount', '0')))
        custom_identifier = webhook_data.get('metadata', {}).get('customer', {}).get('custom_id')

        # Buscar la carga de saldo pendiente
        try:
            carga_saldo = CargasSaldo.objects.get(
                custom_identifier=custom_identifier,
                estado='PENDIENTE'
            )
        except CargasSaldo.DoesNotExist:
            print(f"Carga de saldo Tigo Money no encontrada: {custom_identifier}")
            return JsonResponse({'status': 'Carga de saldo no encontrada'}, status=200)

        # Actualizar estado de la carga de saldo
        with transaction.atomic():
            carga_saldo.estado = 'CONFIRMADO'
            carga_saldo.fecha_confirmacion = timezone.now()
            carga_saldo.pay_request_id = transaction_id
            carga_saldo.save()

            # Actualizar saldo de la tarjeta
            tarjeta = carga_saldo.nro_tarjeta
            tarjeta.saldo_actual += int(amount)
            tarjeta.save()

            # Registrar auditoría
            registrar_auditoria_sistema(
                operacion='CARGA_SALDO_TIGO_CONFIRMADO',
                descripcion=f'Carga confirmada via Tigo Money: Gs. {amount} - ID: {transaction_id}',
                tabla_afectada='cargas_saldo',
                id_registro=carga_saldo.id_carga
            )

        print(f"✅ Carga de saldo Tigo Money confirmada: {custom_identifier} - Gs. {amount}")
        return JsonResponse({'status': 'Carga de saldo confirmada'}, status=200)

    except Exception as e:
        print(f"Error procesando carga de saldo Tigo Money: {str(e)}")
        return JsonResponse({'error': 'Error procesando carga de saldo'}, status=500)


def procesar_pago_deudas_tigo_confirmado(webhook_data):
    """
    Procesa confirmación de pago de deudas via Tigo Money
    """
    try:
        transaction_id = webhook_data.get('transactionId')
        amount = Decimal(str(webhook_data.get('amount', '0')))
        custom_identifier = webhook_data.get('metadata', {}).get('customer', {}).get('custom_id')

        # Extraer IDs de ventas del custom_identifier
        try:
            venta_ids_str = custom_identifier.replace('PAGO-', '')
            venta_ids = [int(vid) for vid in venta_ids_str.split(',') if vid.isdigit()]
        except (ValueError, AttributeError):
            print(f"Formato de custom_identifier inválido: {custom_identifier}")
            return JsonResponse({'status': 'Formato inválido'}, status=200)

        # Procesar cada venta
        total_procesado = Decimal('0')

        with transaction.atomic():
            for venta_id in venta_ids:
                try:
                    venta = Ventas.objects.get(pk=venta_id, saldo_pendiente__gt=0)

                    restante = amount - total_procesado
                    if restante <= 0:
                        break

                    pago_esta_venta = min(restante, venta.saldo_pendiente)
                    venta.saldo_pendiente -= pago_esta_venta
                    venta.estado_pago = 'PAGADA' if venta.saldo_pendiente == 0 else 'PARCIAL'
                    venta.save()

                    total_procesado += pago_esta_venta

                except Ventas.DoesNotExist:
                    continue

            # Registrar auditoría
            registrar_auditoria_sistema(
                operacion='PAGO_DEUDAS_TIGO_CONFIRMADO',
                descripcion=f'Pago confirmado via Tigo Money: Gs. {amount} - Ventas: {venta_ids} - ID: {transaction_id}',
                tabla_afectada='ventas'
            )

        print(f"✅ Pago de deudas Tigo Money confirmado: {custom_identifier} - Gs. {amount}")
        return JsonResponse({'status': 'Pago de deudas confirmado'}, status=200)

    except Exception as e:
        print(f"Error procesando pago de deudas Tigo Money: {str(e)}")
        return JsonResponse({'error': 'Error procesando pago de deudas'}, status=500)

