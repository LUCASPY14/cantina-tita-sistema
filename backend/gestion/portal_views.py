
# PORTAL VIEWS - Sistema de portal para padres

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from .models import *

# ========================= AUTENTICACIÓN PORTAL =========================

def portal_login(request):
    """Login específico del portal"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('gestion:portal_dashboard')
        else:
            messages.error(request, 'Credenciales incorrectas')
    
    return render(request, 'apps/portal/login.html')

@login_required
def portal_logout(request):
    """Logout del portal"""
    logout(request)
    return redirect('gestion:portal_login')

@login_required
def portal_dashboard(request):
    """Dashboard principal del portal"""
    # Obtener información del usuario
    tarjetas = Tarjeta.objects.filter(cliente__user=request.user)
    
    context = {
        'tarjetas': tarjetas,
        'total_saldo': sum(t.saldo for t in tarjetas)
    }
    return render(request, 'apps/portal/dashboard.html', context)

@login_required
def portal_perfil(request):
    """Perfil del usuario del portal"""
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name')
        request.user.last_name = request.POST.get('last_name')
        request.user.email = request.POST.get('email')
        request.user.save()
        messages.success(request, 'Perfil actualizado exitosamente')
    
    return render(request, 'apps/portal/perfil.html')

@login_required
def portal_cambiar_password(request):
    """Cambiar contraseña del portal"""
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        
        if request.user.check_password(current_password):
            request.user.set_password(new_password)
            request.user.save()
            messages.success(request, 'Contraseña cambiada exitosamente')
            return redirect('gestion:portal_login')
        else:
            messages.error(request, 'Contraseña actual incorrecta')
    
    return render(request, 'apps/portal/cambiar_password.html')

# ========================= 2FA (Placeholders) =========================

@login_required
def portal_configurar_2fa(request):
    """Configurar autenticación de 2 factores"""
    return render(request, 'apps/portal/2fa/configurar.html')

@login_required
def portal_verificar_2fa(request):
    """Verificar código 2FA"""
    return render(request, 'apps/portal/2fa/verificar.html')

@login_required
def portal_activar_2fa(request):
    """Activar 2FA"""
    return JsonResponse({'success': True, 'message': '2FA activado'})

@login_required
def portal_deshabilitar_2fa(request):
    """Deshabilitar 2FA"""
    return JsonResponse({'success': True, 'message': '2FA deshabilitado'})

def portal_restablecer_password(request):
    """Restablecer contraseña"""
    return render(request, 'apps/portal/restablecer_password.html')

@login_required
def portal_revocar_terminos(request):
    """Revocar términos y condiciones"""
    return JsonResponse({'success': True, 'message': 'Términos revocados'})

# ========================= GESTIÓN DE HIJOS =========================

@login_required
def portal_mis_hijos(request):
    """Lista de hijos del usuario"""
    hijos = Cliente.objects.filter(padre=request.user)
    return render(request, 'apps/portal/hijos/mis_hijos.html', {
        'hijos': hijos
    })

@login_required
def portal_consumos_hijo(request, hijo_id):
    """Consumos de un hijo específico"""
    hijo = get_object_or_404(Cliente, pk=hijo_id, padre=request.user)
    # Obtener consumos (placeholder)
    consumos = []
    
    return render(request, 'apps/portal/hijos/consumos.html', {
        'hijo': hijo,
        'consumos': consumos
    })

@login_required
def portal_restricciones_hijo(request, hijo_id):
    """Configurar restricciones de un hijo"""
    hijo = get_object_or_404(Cliente, pk=hijo_id, padre=request.user)
    
    return render(request, 'apps/portal/hijos/restricciones.html', {
        'hijo': hijo
    })

# ========================= RECARGAS Y PAGOS =========================

@login_required
def portal_cargar_saldo(request):
    """Cargar saldo a tarjetas"""
    if request.method == 'POST':
        # Lógica de carga de saldo
        messages.success(request, 'Recarga procesada exitosamente')
        return redirect('gestion:portal_dashboard')
    
    tarjetas = Tarjeta.objects.filter(cliente__user=request.user)
    return render(request, 'apps/portal/recargas/cargar_saldo.html', {
        'tarjetas': tarjetas
    })

@login_required
def portal_pagos(request):
    """Historial de pagos"""
    pagos = []  # Placeholder
    return render(request, 'apps/portal/pagos/historial.html', {
        'pagos': pagos
    })

@login_required
def portal_recargas(request):
    """Historial de recargas"""
    recargas = CargasSaldo.objects.filter(
        tarjeta__cliente__user=request.user
    ).order_by('-fecha')
    
    return render(request, 'apps/portal/recargas/historial.html', {
        'recargas': recargas
    })

@login_required
def portal_recargar_tarjeta(request, tarjeta_id):
    """Recargar tarjeta específica"""
    tarjeta = get_object_or_404(Tarjeta, pk=tarjeta_id, cliente__user=request.user)
    
    if request.method == 'POST':
        monto = request.POST.get('monto')
        # Procesar recarga
        messages.success(request, f'Recarga de Gs. {monto} procesada')
        return redirect('gestion:portal_dashboard')
    
    return render(request, 'apps/portal/recargas/recargar_tarjeta.html', {
        'tarjeta': tarjeta
    })

@login_required
def portal_notificaciones_saldo(request):
    """Configurar notificaciones de saldo"""
    return render(request, 'apps/portal/configuracion/notificaciones.html')

# ========================= APIs PORTAL =========================

@login_required
def api_portal_movimientos(request):
    """API para obtener movimientos"""
    movimientos = []  # Placeholder
    return JsonResponse({'movimientos': movimientos})

@login_required
def api_portal_saldo(request):
    """API para obtener saldo actual"""
    tarjetas = Tarjeta.objects.filter(cliente__user=request.user)
    saldo_total = sum(t.saldo for t in tarjetas)
    
    return JsonResponse({'saldo': float(saldo_total)})
