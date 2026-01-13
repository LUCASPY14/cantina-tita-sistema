"""
Utilidades para Autorización de Saldo Negativo
Cantina Tita - 2026
"""

from django.db import transaction
from django.utils import timezone
from decimal import Decimal


def puede_autorizar_saldo_negativo(empleado):
    """
    Verifica si un empleado puede autorizar ventas con saldo negativo
    
    Requisitos:
    - Debe ser ADMINISTRADOR o GERENTE
    - Debe estar activo
    """
    from gestion.models import TipoRolGeneral
    
    if not empleado or not empleado.activo:
        return False
    
    # Solo ADMINISTRADOR (3) o GERENTE (2) pueden autorizar
    roles_autorizados = ['ADMINISTRADOR', 'GERENTE']
    
    if empleado.id_rol and empleado.id_rol.nombre_rol in roles_autorizados:
        return True
    
    return False


def validar_limite_credito(tarjeta, monto_venta):
    """
    Valida si la venta puede realizarse considerando el límite de crédito
    
    Returns:
        (bool, str): (puede_vender, mensaje_error)
    """
    saldo_actual = tarjeta.saldo_actual
    limite_credito = tarjeta.limite_credito or 0
    
    # Calcular saldo después de la venta
    saldo_resultante = saldo_actual - monto_venta
    
    # Si el saldo resultante es positivo, ok
    if saldo_resultante >= 0:
        return True, "Saldo suficiente"
    
    # Si el saldo resultante es negativo
    if not tarjeta.permite_saldo_negativo:
        return False, "Esta tarjeta no permite saldo negativo"
    
    # Verificar límite de crédito
    deuda_resultante = abs(saldo_resultante)
    if deuda_resultante > limite_credito:
        return False, f"Excede el límite de crédito (₲{limite_credito:,})"
    
    # Puede vender con autorización
    return True, "Requiere autorización de supervisor"


@transaction.atomic
def autorizar_venta_saldo_negativo(venta, tarjeta, empleado_autoriza, motivo):
    """
    Autoriza una venta que deja el saldo en negativo
    
    Args:
        venta: Objeto Ventas
        tarjeta: Objeto Tarjeta
        empleado_autoriza: Empleado que autoriza
        motivo: Razón de la autorización
    
    Returns:
        AutorizacionSaldoNegativo creada
    """
    from gestion.models import AutorizacionSaldoNegativo
    from gestion.seguridad_utils import registrar_auditoria
    
    # Validar que el empleado puede autorizar
    if not puede_autorizar_saldo_negativo(empleado_autoriza):
        raise ValueError("No tiene permisos para autorizar saldo negativo")
    
    # Calcular saldos
    saldo_anterior = tarjeta.saldo_actual
    monto_venta = venta.total
    saldo_resultante = saldo_anterior - monto_venta
    
    # Crear autorización
    autorizacion = AutorizacionSaldoNegativo.objects.create(
        id_venta=venta,
        nro_tarjeta=tarjeta,
        id_empleado_autoriza=empleado_autoriza,
        saldo_anterior=saldo_anterior,
        monto_venta=monto_venta,
        saldo_resultante=saldo_resultante,
        motivo=motivo,
        regularizado=False
    )
    
    # Registrar auditoría
    registrar_auditoria(
        tabla='autorizaciones_saldo_negativo',
        accion='CREAR',
        registro_id=autorizacion.id_autorizacion,
        usuario=empleado_autoriza.nombre_usuario,
        detalles=f'Autorización saldo negativo - Venta #{venta.id_venta} - Tarjeta {tarjeta.nro_tarjeta} - Saldo: ₲{saldo_resultante:,}'
    )
    
    return autorizacion


@transaction.atomic
def regularizar_saldo_negativo(tarjeta, carga_saldo):
    """
    Regulariza el saldo negativo cuando se hace una recarga
    
    Process:
    1. Detectar si hay saldo negativo
    2. Descontar primero del saldo negativo
    3. El resto se acredita a la tarjeta
    4. Marcar autorizaciones como regularizadas
    5. Enviar notificación de regularización
    
    Args:
        tarjeta: Objeto Tarjeta
        carga_saldo: Objeto CargasSaldo
    
    Returns:
        dict con detalles de la regularización
    """
    from gestion.models import AutorizacionSaldoNegativo
    from gestion.notificaciones_saldo import notificar_regularizacion_saldo
    from gestion.seguridad_utils import registrar_auditoria
    
    saldo_anterior = tarjeta.saldo_actual
    monto_recarga = carga_saldo.monto
    
    # Si el saldo es positivo o cero, no hay nada que regularizar
    if saldo_anterior >= 0:
        return {
            'habia_deuda': False,
            'deuda_anterior': 0,
            'monto_recarga': monto_recarga,
            'monto_aplicado_deuda': 0,
            'saldo_final': saldo_anterior + monto_recarga
        }
    
    # Hay saldo negativo (deuda)
    deuda_anterior = abs(saldo_anterior)
    
    # Calcular cuánto se aplica a la deuda y cuánto queda de saldo
    if monto_recarga >= deuda_anterior:
        # La recarga cubre toda la deuda y queda saldo
        monto_aplicado_deuda = deuda_anterior
        saldo_final = monto_recarga - deuda_anterior
    else:
        # La recarga no cubre toda la deuda
        monto_aplicado_deuda = monto_recarga
        saldo_final = saldo_anterior + monto_recarga  # Sigue negativo
    
    # Marcar autorizaciones como regularizadas
    autorizaciones_pendientes = AutorizacionSaldoNegativo.objects.filter(
        nro_tarjeta=tarjeta,
        regularizado=False
    )
    
    for autorizacion in autorizaciones_pendientes:
        if saldo_final >= 0:  # Si ya se regularizó completamente
            autorizacion.regularizado = True
            autorizacion.fecha_regularizacion = timezone.now()
            autorizacion.id_carga_regularizacion = carga_saldo
            autorizacion.save()
    
    # Registrar auditoría
    registrar_auditoria(
        tabla='tarjetas',
        accion='REGULARIZAR_SALDO',
        registro_id=tarjeta.nro_tarjeta,
        usuario='SISTEMA',
        detalles=f'Regularización saldo - Deuda: ₲{deuda_anterior:,} - Recarga: ₲{monto_recarga:,} - Aplicado a deuda: ₲{monto_aplicado_deuda:,} - Saldo final: ₲{saldo_final:,}'
    )
    
    # Enviar notificación si se regularizó completamente
    if saldo_final >= 0 and deuda_anterior > 0:
        notificar_regularizacion_saldo(tarjeta, carga_saldo)
    
    return {
        'habia_deuda': True,
        'deuda_anterior': deuda_anterior,
        'monto_recarga': monto_recarga,
        'monto_aplicado_deuda': monto_aplicado_deuda,
        'saldo_final': saldo_final,
        'regularizado_completamente': saldo_final >= 0
    }
