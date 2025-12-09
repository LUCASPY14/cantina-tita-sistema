"""
Vistas para gestión de clientes y portal web de clientes
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.core.mail import send_mail
from django.conf import settings
import bcrypt
from datetime import datetime, timedelta
from decimal import Decimal

from .models import (
    Cliente, UsuariosWebClientes, Hijo, Tarjeta, CargasSaldo,
    Ventas, DetalleVenta, SuscripcionesAlmuerzo, RegistroConsumoAlmuerzo,
    PagosAlmuerzoMensual, ListaPrecios, TipoCliente
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
    
    return render(request, 'pos/gestionar_clientes.html', context)


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
                
                return redirect('pos:gestionar_clientes')
                
        except Exception as e:
            messages.error(request, f'Error al crear cliente: {str(e)}')
    
    # GET - Mostrar formulario
    listas_precios = ListaPrecios.objects.all()
    tipos_cliente = TipoCliente.objects.all()
    
    context = {
        'listas_precios': listas_precios,
        'tipos_cliente': tipos_cliente,
    }
    
    return render(request, 'pos/crear_cliente.html', context)


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
            from django.conf import settings
            
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
                return redirect('pos:portal_dashboard')
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
        'RECAPTCHA_PUBLIC_KEY': settings.RECAPTCHA_PUBLIC_KEY
    }
    if request.method == 'POST':
        usuario = request.POST.get('usuario', '').strip()
        if usuario:
            fecha_limite = timezone.now() - timedelta(minutes=15)
            intentos_recientes = IntentoLogin.objects.filter(
                usuario=usuario,
                exitoso=False,
                fecha_intento__gte=fecha_limite
            ).count()
            context['mostrar_captcha'] = intentos_recientes >= 2
    
    return render(request, 'portal/login.html', context)


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
    return redirect('pos:portal_login')


def portal_dashboard_view(request):
    """Dashboard del portal de clientes"""
    
    # Verificar sesión
    cliente_id = request.session.get('cliente_id')
    if not cliente_id:
        return redirect('pos:portal_login')
    
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
        return redirect('pos:portal_login')
    
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
        return redirect('pos:portal_login')
    
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

