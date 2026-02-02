"""
Vistas para validación de pagos pendientes (transferencias bancarias)
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum, Q
from django.utils import timezone
from decimal import Decimal
import re

from .models import (
    Cliente, Ventas, RegistroConsumoAlmuerzo,
    PagoCuentaAlmuerzo, UsuarioPortal
)
from .seguridad_utils import registrar_auditoria
from .permisos import solo_gerente_o_superior


@solo_gerente_o_superior
def validar_pagos_pendientes(request):
    """
    Vista para mostrar y validar pagos pendientes por transferencia bancaria.
    Los pagos pendientes se identifican por tener motivo_credito con código de transferencia.
    Acceso: Gerentes y Administradores
    """
    
    # Buscar ventas con motivo_credito de pago pendiente
    ventas_pendientes = Ventas.objects.filter(
        motivo_credito__icontains='PAGO_PENDIENTE_TRANSFERENCIA:'
    ).select_related('id_cliente', 'id_hijo').order_by('-fecha')
    
    # Agrupar por código de confirmación
    pagos_agrupados = {}
    
    for venta in ventas_pendientes:
        # Extraer código de transferencia del motivo_credito
        match = re.search(r'PAGO_PENDIENTE_TRANSFERENCIA:(\S+)', venta.motivo_credito or '')
        if match:
            codigo = match.group(1)
            
            if codigo not in pagos_agrupados:
                pagos_agrupados[codigo] = {
                    'codigo_confirmacion': codigo,
                    'cliente_nombre': venta.id_cliente.nombre_completo,
                    'cliente_ruc': venta.id_cliente.ruc_ci,
                    'cliente_email': getattr(UsuarioPortal.objects.filter(
                        cliente=venta.id_cliente
                    ).first(), 'email', 'N/D'),
                    'fecha_registro': venta.fecha,
                    'monto_total': Decimal('0'),
                    'cantidad_ventas': 0,
                    'cantidad_almuerzos': 0,
                    'cantidad_items': 0,
                    'items': [],
                    'venta_ids': [],
                    'almuerzo_ids': []
                }
            
            pagos_agrupados[codigo]['monto_total'] += venta.saldo_pendiente
            pagos_agrupados[codigo]['cantidad_ventas'] += 1
            pagos_agrupados[codigo]['cantidad_items'] += 1
            pagos_agrupados[codigo]['venta_ids'].append(venta.id_venta)
            pagos_agrupados[codigo]['items'].append({
                'tipo': 'venta',
                'fecha': venta.fecha,
                'hijo': venta.id_hijo.nombre_completo if venta.id_hijo else 'N/D',
                'descripcion': f'Venta #{venta.id_venta}',
                'monto': venta.saldo_pendiente
            })
    
    # Buscar almuerzos pendientes (esto requeriría agregar un campo similar)
    # Por ahora solo mostramos ventas
    
    # Convertir a lista ordenada por fecha descendente
    pagos_pendientes = sorted(
        pagos_agrupados.values(),
        key=lambda x: x['fecha_registro'],
        reverse=True
    )
    
    # Calcular estadísticas
    total_pendientes = len(pagos_pendientes)
    monto_total_pendiente = sum(p['monto_total'] for p in pagos_pendientes)
    total_items = sum(p['cantidad_items'] for p in pagos_pendientes)
    
    context = {
        'pagos_pendientes': pagos_pendientes,
        'total_pendientes': total_pendientes,
        'monto_total_pendiente': monto_total_pendiente,
        'total_items': total_items,
    }
    
    return render(request, 'gestion/validar_pagos.html', context)


@solo_gerente_o_superior
def validar_pago_action(request):
    """
    Procesar la aprobación o rechazo de un pago pendiente
    Acceso: Gerentes y Administradores
    """
    if request.method != 'POST':
        return redirect('gestion:validar_pagos_pendientes')
    
    codigo_confirmacion = request.POST.get('codigo_confirmacion')
    accion = request.POST.get('accion')  # 'aprobar' o 'rechazar'
    
    if not codigo_confirmacion or not accion:
        messages.error(request, 'Datos incompletos para procesar la acción')
        return redirect('gestion:validar_pagos_pendientes')
    
    try:
        with transaction.atomic():
            # Buscar todas las ventas con este código
            ventas = Ventas.objects.filter(
                motivo_credito__icontains=f'PAGO_PENDIENTE_TRANSFERENCIA:{codigo_confirmacion}'
            )
            
            # Buscar almuerzos relacionados (si los hubiera guardados)
            # Por ahora trabajamos solo con ventas
            
            if not ventas.exists():
                messages.error(request, f'No se encontraron registros con el código {codigo_confirmacion}')
                return redirect('gestion:validar_pagos_pendientes')
            
            if accion == 'aprobar':
                # Aprobar: Marcar como pagado
                monto_total = Decimal('0')
                almuerzos_ids = []
                
                for venta in ventas:
                    monto_total += venta.saldo_pendiente
                    
                    # Extraer IDs de almuerzos si los hay
                    match_almuerzos = re.search(r'ALMUERZOS:([0-9,]+)', venta.motivo_credito or '')
                    if match_almuerzos:
                        almuerzos_ids = match_almuerzos.group(1).split(',')
                    
                    venta.saldo_pendiente = Decimal('0')
                    venta.estado_pago = 'PAGADA'
                    venta.estado = 'PROCESADO'
                    venta.motivo_credito = f'PAGO_APROBADO:{codigo_confirmacion}:{timezone.now().strftime("%Y%m%d%H%M")}'
                    venta.save()
                
                # Marcar almuerzos como pagados
                if almuerzos_ids:
                    RegistroConsumoAlmuerzo.objects.filter(
                        id_registro_consumo__in=almuerzos_ids
                    ).update(marcado_en_cuenta=False)
                
                mensaje_almuerzos = f" + {len(almuerzos_ids)} almuerzo(s)" if almuerzos_ids else ""
                messages.success(request, f'✅ Pago APROBADO exitosamente. Código: {codigo_confirmacion}. Monto: Gs. {monto_total:,.0f}. {ventas.count()} venta(s){mensaje_almuerzos} actualizadas.')
                
                # Auditoría
                registrar_auditoria(
                    request=request,
                    operacion='APROBAR_PAGO_TRANSFERENCIA',
                    tipo_usuario='ADMIN',
                    descripcion=f'Aprobó pago con código {codigo_confirmacion} por Gs. {monto_total}'
                )
                
            elif accion == 'rechazar':
                # Rechazar: Eliminar ventas ficticias, restaurar almuerzos a pendientes
                ventas_eliminadas = 0
                ventas_actualizadas = 0
                almuerzos_restaurados = 0
                
                for venta in ventas:
                    # Extraer IDs de almuerzos si los hay
                    match_almuerzos = re.search(r'ALMUERZOS:([0-9,]+)', venta.motivo_credito or '')
                    
                    if match_almuerzos:
                        almuerzos_ids = match_almuerzos.group(1).split(',')
                        # Restaurar almuerzos a pendientes
                        RegistroConsumoAlmuerzo.objects.filter(
                            id_registro_consumo__in=almuerzos_ids
                        ).update(marcado_en_cuenta=True)
                        almuerzos_restaurados += len(almuerzos_ids)
                        
                        # Si es venta ficticia (solo almuerzos), eliminarla
                        if venta.tipo_venta == 'CREDITO' and venta.saldo_pendiente == venta.monto_total:
                            venta.delete()
                            ventas_eliminadas += 1
                            continue
                    
                    # Venta real - marcar como rechazada
                    venta.motivo_credito = f'PAGO_RECHAZADO:{codigo_confirmacion}:{timezone.now().strftime("%Y%m%d%H%M")}'
                    venta.estado = 'PROCESADO'
                    venta.save()
                    ventas_actualizadas += 1
                
                mensaje_almuerzos = f" {almuerzos_restaurados} almuerzo(s) restaurados" if almuerzos_restaurados > 0 else ""
                mensaje_detalle = f"({ventas_eliminadas} registro(s) ficticios eliminados, {ventas_actualizadas} actualizados)"
                messages.warning(request, f'⚠️ Pago RECHAZADO. Código: {codigo_confirmacion}.{mensaje_almuerzos}. {mensaje_detalle}')
                
                # Auditoría
                registrar_auditoria(
                    request=request,
                    operacion='RECHAZAR_PAGO_TRANSFERENCIA',
                    tipo_usuario='ADMIN',
                    descripcion=f'Rechazó pago con código {codigo_confirmacion}'
                )
            
    except Exception as e:
        messages.error(request, f'Error al procesar la validación: {str(e)}')
    
    return redirect('gestion:validar_pagos_pendientes')
