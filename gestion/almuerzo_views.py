# =============================================================================
# MÓDULO DE ALMUERZOS - VISTAS POS Y GESTIÓN
# =============================================================================
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.db import transaction
from datetime import date, datetime
from decimal import Decimal

from gestion.permisos import acceso_cajero, solo_administrador, solo_gerente_o_superior

from .models import (
    TipoAlmuerzo, 
    RegistroConsumoAlmuerzo, 
    CuentaAlmuerzoMensual,
    PagoCuentaAlmuerzo,
    Tarjeta,
    Hijo,
    TarjetaAutorizacion,
    LogAutorizacion,
    Cliente
)
from .cache_reportes import get_reporte_cacheado, get_datos_dashboard_cacheados


# =============================================================================
# PÁGINA PRINCIPAL DE REPORTES
# =============================================================================

@acceso_cajero
def almuerzo_reportes(request):
    """
    Página principal de reportes de almuerzos con estadísticas rápidas (CACHEADO)
    """
    hoy = date.today()
    
    # Intentar obtener datos cacheados
    from django.core.cache import cache
    cache_key = f'almuerzo_stats:{hoy}'
    stats = cache.get(cache_key)
    
    if stats is None:
        # Estadísticas del día
        almuerzos_hoy = RegistroConsumoAlmuerzo.objects.filter(fecha_consumo=hoy).count()
        total_hoy = RegistroConsumoAlmuerzo.objects.filter(
            fecha_consumo=hoy
        ).aggregate(total=Sum('costo_almuerzo'))['total'] or Decimal('0.00')
        
        # Estadísticas del mes
        almuerzos_mes = RegistroConsumoAlmuerzo.objects.filter(
            fecha_consumo__month=hoy.month,
            fecha_consumo__year=hoy.year
        ).count()
        total_mes = RegistroConsumoAlmuerzo.objects.filter(
            fecha_consumo__month=hoy.month,
            fecha_consumo__year=hoy.year
        ).aggregate(total=Sum('costo_almuerzo'))['total'] or Decimal('0.00')
        
        stats = {
            'fecha_hoy': hoy,
            'almuerzos_hoy': almuerzos_hoy,
            'total_hoy': total_hoy,
            'almuerzos_mes': almuerzos_mes,
            'total_mes': total_mes,
            'mes_actual': hoy.strftime('%B %Y')
        }
        
        # Cache por 2 minutos (almuerzos cambian frecuentemente)
        cache.set(cache_key, stats, 120)
    
    context = {
        'stats': {
            'fecha_hoy': hoy,
            'almuerzos_hoy': almuerzos_hoy,
            'total_hoy': total_hoy,
            'almuerzos_mes': almuerzos_mes,
            'total_mes': total_mes,
            'mes_actual': hoy.strftime('%B %Y')
        }
    }
    
    return render(request, 'pos/almuerzo_reportes.html', context)


# =============================================================================
# POS DE ALMUERZO - Registro rápido con código de barras
# =============================================================================

@acceso_cajero
@require_http_methods(["GET", "POST"])
def pos_almuerzo(request):
    """
    POS de almuerzo - Registro automático al pasar tarjeta
    - Input autofocus para lector de código de barras
    - Registro automático sin confirmación manual
    - Validación de duplicados (1 almuerzo por día)
    - NO descuenta saldo de tarjeta
    """
    context = {
        'ultimos_registros': RegistroConsumoAlmuerzo.objects.select_related(
            'id_hijo', 'id_tipo_almuerzo'
        ).order_by('-fecha_consumo', '-hora_registro')[:10]
    }
    
    if request.method == "POST":
        codigo_barra = request.POST.get('codigo_barra', '').strip()
        hoy = timezone.localdate()
        ahora = timezone.localtime().time()
        
        if not codigo_barra:
            context['error'] = "❌ Código de barras vacío"
            return render(request, 'pos/almuerzo.html', context)
        
        try:
            # 1. Buscar tarjeta activa
            tarjeta = Tarjeta.objects.select_related('id_hijo').get(
                nro_tarjeta=codigo_barra,
                estado='Activa'
            )
        except Tarjeta.DoesNotExist:
            context['error'] = f"❌ Tarjeta {codigo_barra} no encontrada o inactiva"
            context['codigo'] = codigo_barra
            return render(request, 'pos/almuerzo.html', context)
        
        hijo = tarjeta.id_hijo
        
        # 2. Verificar si ya tiene almuerzo hoy
        ya_tiene = RegistroConsumoAlmuerzo.objects.filter(
            id_hijo=hijo,
            fecha_consumo=hoy
        ).exists()
        
        if ya_tiene:
            context['warning'] = f"⚠️ {hijo.nombre_completo} ya tiene almuerzo registrado hoy"
            context['hijo'] = hijo
            context['tarjeta'] = tarjeta
            return render(request, 'pos/almuerzo.html', context)
        
        # 3. Buscar tipo de almuerzo predeterminado (primer activo ordenado por ID)
        tipo_almuerzo = TipoAlmuerzo.objects.filter(activo=True).order_by('id_tipo_almuerzo').first()
        if not tipo_almuerzo:
            context['error'] = "❌ No hay tipo de almuerzo configurado"
            return render(request, 'pos/almuerzo.html', context)
        
        # 4. Verificar si tiene pago mensual activo, sino crear cuenta a crédito
        mes_actual = hoy.month
        anio_actual = hoy.year
        
        cuenta_mensual, created = CuentaAlmuerzoMensual.objects.get_or_create(
            id_hijo=hijo,
            mes=mes_actual,
            anio=anio_actual,
            defaults={
                'forma_cobro': 'CREDITO_MENSUAL',
                'estado': 'PENDIENTE',
                'cantidad_almuerzos': 0,
                'monto_total': Decimal('0.00'),
                'monto_pagado': Decimal('0.00'),
                'fecha_generacion': hoy
            }
        )
        
        if created:
            context['info'] = f"✓ Cuenta mensual creada en modo CRÉDITO para {hijo.nombre_completo}"
        
        # 5. Registrar almuerzo (NO descuenta saldo de tarjeta)
        try:
            with transaction.atomic():
                registro = RegistroConsumoAlmuerzo.objects.create(
                    id_hijo=hijo,
                    nro_tarjeta=tarjeta,
                    id_tipo_almuerzo=tipo_almuerzo,
                    fecha_consumo=hoy,
                    costo_almuerzo=tipo_almuerzo.precio_unitario,
                    marcado_en_cuenta=True,  # Se marca en cuenta mensual
                    id_suscripcion=None,  # Esporádico
                    hora_registro=ahora
                )
                
                # Actualizar totales de la cuenta mensual
                cuenta_mensual.cantidad_almuerzos = RegistroConsumoAlmuerzo.objects.filter(
                    id_hijo=hijo,
                    fecha_consumo__month=mes_actual,
                    fecha_consumo__year=anio_actual,
                    marcado_en_cuenta=True
                ).count()
                
                cuenta_mensual.monto_total = RegistroConsumoAlmuerzo.objects.filter(
                    id_hijo=hijo,
                    fecha_consumo__month=mes_actual,
                    fecha_consumo__year=anio_actual,
                    marcado_en_cuenta=True
                ).aggregate(total=Sum('costo_almuerzo'))['total'] or Decimal('0.00')
                
                cuenta_mensual.save()
                
                context['ok'] = True
                context['hijo'] = hijo
                context['tarjeta'] = tarjeta
                context['registro'] = registro
                context['tipo_almuerzo'] = tipo_almuerzo
                context['cuenta_mensual'] = cuenta_mensual
                context['registro_id'] = registro.id_registro_consumo  # Para abrir el ticket
                
                # Actualizar lista de últimos registros
                context['ultimos_registros'] = RegistroConsumoAlmuerzo.objects.select_related(
                    'id_hijo', 'id_tipo_almuerzo'
                ).order_by('-fecha_consumo', '-hora_registro')[:10]
                
        except Exception as e:
            context['error'] = f"❌ Error al registrar: {str(e)}"
    
    return render(request, 'pos/almuerzo.html', context)


@acceso_cajero
@require_http_methods(["POST"])
def pos_almuerzo_api(request):
    """
    API para registro de almuerzo (formato JSON)
    Útil para integraciones con lectores de código de barras externos
    """
    codigo_barra = request.POST.get('codigo_barra', '').strip()
    hoy = timezone.localdate()
    ahora = timezone.localtime().time()
    
    if not codigo_barra:
        return JsonResponse({
            'success': False,
            'error': 'Código de barras vacío'
        }, status=400)
    
    try:
        tarjeta = Tarjeta.objects.select_related('id_hijo').get(
            nro_tarjeta=codigo_barra,
            estado='Activa'
        )
    except Tarjeta.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': f'Tarjeta {codigo_barra} no encontrada o inactiva'
        }, status=404)
    
    hijo = tarjeta.id_hijo
    
    # Verificar duplicado
    ya_tiene = RegistroConsumoAlmuerzo.objects.filter(
        id_hijo=hijo,
        fecha_consumo=hoy
    ).exists()
    
    if ya_tiene:
        return JsonResponse({
            'success': False,
            'warning': f'{hijo.nombre_completo} ya tiene almuerzo registrado hoy'
        }, status=409)
    
    try:
        tipo_almuerzo = TipoAlmuerzo.objects.filter(activo=True).first()
        if not tipo_almuerzo:
            return JsonResponse({
                'success': False,
                'error': 'No hay tipo de almuerzo configurado'
            }, status=500)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
    
    try:
        with transaction.atomic():
            registro = RegistroConsumoAlmuerzo.objects.create(
                id_hijo=hijo,
                nro_tarjeta=tarjeta,
                id_tipo_almuerzo=tipo_almuerzo,
                fecha_consumo=hoy,
                costo_almuerzo=tipo_almuerzo.precio_unitario,
                marcado_en_cuenta=False,
                id_suscripcion=None,
                hora_registro=ahora
            )
            
            return JsonResponse({
                'success': True,
                'registro': {
                    'id': registro.id_registro_consumo,
                    'estudiante': hijo.nombre_completo,
                    'tarjeta': tarjeta.nro_tarjeta,
                    'tipo_almuerzo': tipo_almuerzo.nombre,
                    'costo': float(tipo_almuerzo.precio_unitario),
                    'fecha': hoy.isoformat(),
                    'hora': ahora.strftime('%H:%M:%S')
                }
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al registrar: {str(e)}'
        }, status=500)


@acceso_cajero
@require_http_methods(["POST"])
def anular_ultimo_almuerzo(request):
    """
    Anular el último registro de almuerzo del día (emergencias)
    Solo disponible para administradores
    """
    registro_id = request.POST.get('registro_id')
    
    if not registro_id:
        return JsonResponse({
            'success': False,
            'error': 'ID de registro no proporcionado'
        }, status=400)
    
    try:
        registro = RegistroConsumoAlmuerzo.objects.get(
            id_registro_consumo=registro_id,
            fecha_consumo=timezone.localdate()
        )
        
        hijo_nombre = registro.id_hijo.nombre_completo
        registro.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Registro de {hijo_nombre} anulado correctamente'
        })
    except RegistroConsumoAlmuerzo.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Registro no encontrado'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# GESTIÓN DE CUENTAS MENSUALES
# =============================================================================

@acceso_cajero
@require_http_methods(["GET"])
def lista_cuentas_mensuales(request):
    """
    Lista de cuentas mensuales de almuerzo
    Filtros: año, mes, estado, hijo
    """
    anio = request.GET.get('anio', timezone.now().year)
    mes = request.GET.get('mes', timezone.now().month)
    estado = request.GET.get('estado', '')
    
    cuentas = CuentaAlmuerzoMensual.objects.select_related('id_hijo')
    
    if anio:
        cuentas = cuentas.filter(anio=anio)
    if mes:
        cuentas = cuentas.filter(mes=mes)
    if estado:
        cuentas = cuentas.filter(estado=estado)
    
    cuentas = cuentas.order_by('-anio', '-mes', 'id_hijo__apellido')
    
    context = {
        'cuentas': cuentas,
        'anio_actual': anio,
        'mes_actual': mes,
        'estado_filter': estado
    }
    
    return render(request, 'pos/almuerzo_cuentas_mensuales.html', context)


@acceso_cajero
@require_http_methods(["GET", "POST"])
def generar_cuentas_mes(request):
    """
    Generar cuentas mensuales para todos los hijos que consumieron almuerzo
    GET: Muestra formulario de confirmación
    POST: Procesa la generación de cuentas
    """
    if request.method == "GET":
        # Mostrar formulario de confirmación
        anio = int(request.GET.get('anio', timezone.now().year))
        mes = int(request.GET.get('mes', timezone.now().month))
        
        # Obtener consumos pendientes de facturar
        consumos_pendientes = RegistroConsumoAlmuerzo.objects.filter(
            fecha_consumo__year=anio,
            fecha_consumo__month=mes,
            marcado_en_cuenta=False
        ).values('id_hijo').annotate(
            cantidad=Count('id_registro_consumo'),
            total=Sum('costo_almuerzo')
        ).count()
        
        context = {
            'anio': anio,
            'mes': mes,
            'consumos_pendientes': consumos_pendientes
        }
        return render(request, 'pos/almuerzo_generar_cuentas.html', context)
    
    # POST: Procesar generación
    # Limpiar espacios no separables y otros caracteres extraños
    anio_str = request.POST.get('anio', str(timezone.now().year)).replace('\xa0', '').replace(' ', '').strip()
    mes_str = request.POST.get('mes', str(timezone.now().month)).replace('\xa0', '').replace(' ', '').strip()
    
    anio = int(anio_str)
    mes = int(mes_str)
    forma_cobro = request.POST.get('forma_cobro', 'CREDITO_MENSUAL')
    
    if forma_cobro not in ['CONTADO_ANTICIPADO', 'CREDITO_MENSUAL']:
        messages.error(request, 'Forma de cobro inválida')
        return redirect('pos:cuentas_mensuales')
    
    try:
        with transaction.atomic():
            # Agrupar consumos del mes por hijo
            consumos_mes = RegistroConsumoAlmuerzo.objects.filter(
                fecha_consumo__year=anio,
                fecha_consumo__month=mes,
                marcado_en_cuenta=False,
                costo_almuerzo__isnull=False
            ).values('id_hijo').annotate(
                cantidad=Count('id_registro_consumo'),
                total=Sum('costo_almuerzo')
            )
            
            cuentas_creadas = 0
            cuentas_actualizadas = 0
            
            for consumo in consumos_mes:
                hijo = Hijo.objects.get(id_hijo=consumo['id_hijo'])
                
                # Crear o actualizar cuenta
                cuenta, created = CuentaAlmuerzoMensual.objects.update_or_create(
                    id_hijo=hijo,
                    anio=anio,
                    mes=mes,
                    defaults={
                        'cantidad_almuerzos': consumo['cantidad'],
                        'monto_total': consumo['total'],
                        'forma_cobro': forma_cobro,
                        'fecha_generacion': timezone.now().date()
                    }
                )
                
                if created:
                    cuentas_creadas += 1
                else:
                    cuentas_actualizadas += 1
            
            # Marcar consumos como facturados
            RegistroConsumoAlmuerzo.objects.filter(
                fecha_consumo__year=anio,
                fecha_consumo__month=mes,
                marcado_en_cuenta=False
            ).update(marcado_en_cuenta=True)
            
            messages.success(request, f'✅ Se generaron {cuentas_creadas} cuentas nuevas y se actualizaron {cuentas_actualizadas} para {mes}/{anio}')
            return redirect('pos:cuentas_mensuales')
            
    except Exception as e:
        messages.error(request, f'Error al generar cuentas: {str(e)}')
        return redirect('pos:cuentas_mensuales')


@acceso_cajero
@require_http_methods(["GET", "POST"])
def registrar_pago_almuerzo(request):
    """
    Registrar pago de cuenta de almuerzo
    GET: Muestra formulario de pago
    POST: Procesa el pago
    """
    if request.method == "GET":
        # Mostrar formulario de pago
        cuenta_id = request.GET.get('cuenta')
        if not cuenta_id:
            messages.error(request, 'Debe especificar una cuenta')
            return redirect('pos:cuentas_mensuales')
        
        try:
            cuenta = CuentaAlmuerzoMensual.objects.select_related('id_hijo').get(id_cuenta=cuenta_id)
            context = {
                'cuenta': cuenta,
            }
            return render(request, 'pos/almuerzo_pagar.html', context)
        except CuentaAlmuerzoMensual.DoesNotExist:
            messages.error(request, 'Cuenta no encontrada')
            return redirect('pos:cuentas_mensuales')
    
    # POST: Procesar pago
    cuenta_id = request.POST.get('cuenta_id')
    monto = Decimal(request.POST.get('monto', '0'))
    medio_pago = request.POST.get('medio_pago', 'EFECTIVO')
    referencia = request.POST.get('referencia', '')
    
    try:
        cuenta = CuentaAlmuerzoMensual.objects.get(id_cuenta=cuenta_id)
        
        with transaction.atomic():
            pago = PagoCuentaAlmuerzo.objects.create(
                id_cuenta=cuenta,
                monto=monto,
                medio_pago=medio_pago,
                referencia=referencia
            )
            
            # Actualizar cuenta
            total_pagado = PagoCuentaAlmuerzo.objects.filter(
                id_cuenta=cuenta
            ).aggregate(Sum('monto'))['monto__sum'] or Decimal('0')
            
            cuenta.monto_pagado = total_pagado
            
            if total_pagado >= cuenta.monto_total:
                cuenta.estado = 'PAGADO'
            elif total_pagado > 0:
                cuenta.estado = 'PARCIAL'
            else:
                cuenta.estado = 'PENDIENTE'
            
            cuenta.save()
            
            messages.success(request, f'Pago registrado exitosamente. Nuevo saldo: Gs. {cuenta.saldo_pendiente:,.0f}')
            return redirect('pos:cuentas_mensuales')
            
    except CuentaAlmuerzoMensual.DoesNotExist:
        messages.error(request, 'Cuenta no encontrada')
        return redirect('pos:cuentas_mensuales')
    except Exception as e:
        messages.error(request, f'Error al registrar pago: {str(e)}')
        return redirect('pos:cuentas_mensuales')


# =============================================================================
# REPORTES
# =============================================================================

@acceso_cajero
@require_http_methods(["GET"])
def reporte_almuerzos_diarios(request):
    """
    Reporte de almuerzos del día o rango de fechas (CACHEADO)
    """
    fecha_desde = request.GET.get('fecha_desde', timezone.now().date())
    fecha_hasta = request.GET.get('fecha_hasta', timezone.now().date())
    
    # Cache por 5 minutos
    from django.core.cache import cache
    cache_key = f'almuerzo_diario:{fecha_desde}:{fecha_hasta}'
    data = cache.get(cache_key)
    
    if data is None:
        registros = RegistroConsumoAlmuerzo.objects.filter(
            fecha_consumo__range=[fecha_desde, fecha_hasta]
        ).select_related('id_hijo', 'id_tipo_almuerzo', 'nro_tarjeta').order_by('-fecha_consumo', '-hora_registro')
        
        total = registros.aggregate(
            cantidad=Count('id_registro_consumo'),
            monto_total=Sum('costo_almuerzo')
        )
        
        data = {
            'registros': list(registros),
            'total': total
        }
        
        cache.set(cache_key, data, 300)  # 5 minutos
    
    registros = data['registros']
    total = data['total']
    
    context = {
        'registros': registros,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'total': total
    }
    
    return render(request, 'pos/almuerzo_reporte_diario.html', context)


@acceso_cajero
@require_http_methods(["GET"])
def reporte_mensual_separado(request):
    """
    Reporte mensual SEPARADO: Almuerzos vs Uso de Tarjeta
    Como se especificó en los requerimientos
    """
    anio = request.GET.get('anio', timezone.now().year)
    mes = request.GET.get('mes', timezone.now().month)
    
    # Usar la vista SQL creada
    from .models import VistaReporteMensualSeparado
    
    reporte = VistaReporteMensualSeparado.objects.all()
    
    context = {
        'reporte': reporte,
        'anio': anio,
        'mes': mes
    }
    
    return render(request, 'pos/almuerzo_reporte_mensual.html', context)


@acceso_cajero
@require_http_methods(["GET"])
def reporte_por_estudiante(request):
    """
    Reporte detallado de consumos de almuerzo por estudiante (hijo/tarjeta)
    Muestra historial completo con estadísticas y totales
    """
    from django.db.models import Sum, Count, Avg

    from datetime import datetime, timedelta
    import calendar
    
    # Obtener todos los estudiantes con tarjetas activas
    estudiantes = Hijo.objects.filter(
        tarjeta__estado='Activa'
    ).distinct().order_by('nombre', 'apellido')
    
    # Parámetros de filtro
    id_hijo_seleccionado = request.GET.get('id_hijo')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    
    # Fechas por defecto: mes actual
    if not fecha_desde:
        fecha_desde = date.today().replace(day=1)
    else:
        fecha_desde = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
    
    if not fecha_hasta:
        fecha_hasta = date.today()
    else:
        fecha_hasta = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
    
    context = {
        'estudiantes': estudiantes,
        'id_hijo_seleccionado': id_hijo_seleccionado,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
    }
    
    if id_hijo_seleccionado:
        hijo_seleccionado = get_object_or_404(Hijo, id_hijo=id_hijo_seleccionado)
        
        # Obtener registros del estudiante
        registros = RegistroConsumoAlmuerzo.objects.filter(
            id_hijo=hijo_seleccionado,
            fecha_consumo__range=[fecha_desde, fecha_hasta]
        ).select_related('id_tipo_almuerzo').order_by('-fecha_consumo', '-hora_registro')
        
        # Calcular totales
        totales = registros.aggregate(
            total_registros=Count('id_registro_consumo'),
            total_monto=Sum('costo_almuerzo'),
            costo_promedio=Avg('costo_almuerzo')
        )
        
        # Consumo por mes
        consumo_por_mes = registros.values(
            'fecha_consumo__year', 'fecha_consumo__month'
        ).annotate(
            cantidad=Count('id_registro_consumo'),
            total=Sum('costo_almuerzo')
        ).order_by('fecha_consumo__year', 'fecha_consumo__month')
        
        # Agregar nombres de meses
        meses_espanol = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        
        for item in consumo_por_mes:
            mes_num = item['fecha_consumo__month']
            anio = item['fecha_consumo__year']
            item['mes_nombre'] = f"{meses_espanol[mes_num - 1]} {anio}"
        
        # Calcular promedio diario
        dias_transcurridos = (fecha_hasta - fecha_desde).days + 1
        promedio_diario = totales['total_registros'] / dias_transcurridos if dias_transcurridos > 0 else 0
        
        # Última fecha de consumo
        ultima_fecha = registros.first().fecha_consumo if registros.exists() else None
        
        # Obtener tarjeta principal
        tarjeta = Tarjeta.objects.filter(
            id_hijo=hijo_seleccionado, 
            estado='Activa'
        ).first()
        
        if tarjeta:
            hijo_seleccionado.nro_tarjeta = tarjeta.nro_tarjeta
        
        context.update({
            'hijo_seleccionado': hijo_seleccionado,
            'registros': registros,
            'total_registros': totales['total_registros'] or 0,
            'total_monto': totales['total_monto'] or Decimal('0.00'),
            'costo_promedio': totales['costo_promedio'] or Decimal('0.00'),
            'promedio_diario': promedio_diario,
            'ultima_fecha': ultima_fecha,
            'consumo_por_mes': consumo_por_mes,
        })
    
    return render(request, 'pos/almuerzo_reporte_estudiante.html', context)


# =============================================================================
# TICKET DE CONTROL DE ALMUERZO
# =============================================================================

@acceso_cajero
@require_http_methods(["GET"])
def ticket_almuerzo(request, registro_id):
    """
    Genera ticket de control de almuerzo para el estudiante
    Se imprime automáticamente al registrar
    """
    from .models import Cliente
    
    try:
        registro = RegistroConsumoAlmuerzo.objects.select_related(
            'id_hijo',
            'nro_tarjeta',
            'id_tipo_almuerzo'
        ).get(id_registro_consumo=registro_id)
        
        hijo = registro.id_hijo
        
        # Obtener responsable
        responsable = Cliente.objects.filter(
            id_cliente=hijo.id_cliente_responsable_id
        ).first()
        
        # Obtener cuenta mensual
        cuenta_mensual = CuentaAlmuerzoMensual.objects.filter(
            id_hijo=hijo,
            mes=registro.fecha_consumo.month,
            anio=registro.fecha_consumo.year
        ).first()
        
        context = {
            'registro': registro,
            'hijo': hijo,
            'responsable': responsable,
            'cuenta_mensual': cuenta_mensual,
        }
        
        return render(request, 'pos/ticket_almuerzo.html', context)
        
    except RegistroConsumoAlmuerzo.DoesNotExist:
        return JsonResponse({
            'error': 'Registro no encontrado'
        }, status=404)


# =============================================================================
# CONFIGURACIÓN DE PRECIO DE ALMUERZO
# =============================================================================

@acceso_cajero
@require_http_methods(["GET", "POST"])
def configurar_precio_almuerzo(request):
    """
    Vista para que el administrador configure el precio del almuerzo
    El cambio de precio se aplica inmediatamente a todos los nuevos registros
    """
    from .models import Cliente
    
    tipo_almuerzo = TipoAlmuerzo.objects.filter(activo=True).first()
    
    if request.method == "POST":
        nuevo_precio = request.POST.get('precio_unitario')
        
        try:
            nuevo_precio = Decimal(nuevo_precio)
            
            if nuevo_precio <= 0:
                messages.error(request, '❌ El precio debe ser mayor a 0')
            else:
                precio_anterior = tipo_almuerzo.precio_unitario
                tipo_almuerzo.precio_unitario = nuevo_precio
                tipo_almuerzo.save()
                
                messages.success(
                    request,
                    f'✅ Precio actualizado: Gs. {precio_anterior:,.0f} → Gs. {nuevo_precio:,.0f}'
                )
                
                return redirect('pos:configurar_precio_almuerzo')
                
        except (ValueError, TypeError):
            messages.error(request, '❌ Precio inválido')
    
    # Obtener estadísticas para mostrar impacto
    hoy = date.today()
    registros_hoy = RegistroConsumoAlmuerzo.objects.filter(fecha_consumo=hoy).count()
    cuentas_pendientes = CuentaAlmuerzoMensual.objects.filter(
        estado__in=['PENDIENTE', 'PARCIAL']
    ).count()
    
    context = {
        'tipo_almuerzo': tipo_almuerzo,
        'registros_hoy': registros_hoy,
        'cuentas_pendientes': cuentas_pendientes,
    }
    
    return render(request, 'almuerzo/configurar_precio.html', context)


# =============================================================================
# SISTEMA DE AUTORIZACIONES PARA ANULACIONES
# =============================================================================

@acceso_cajero
@require_http_methods(["POST"])
def validar_autorizacion(request):
    """
    Valida si una tarjeta de autorización tiene permisos para una operación
    """
    try:
        codigo_barra = request.POST.get('codigo_barra', '').strip()
        tipo_operacion = request.POST.get('tipo_operacion', '')
        id_registro = request.POST.get('id_registro', None)
        
        if not codigo_barra:
            return JsonResponse({
                'success': False,
                'message': 'Debe escanear una tarjeta de autorización'
            })
        
        # Buscar la tarjeta
        try:
            tarjeta = TarjetaAutorizacion.objects.get(codigo_barra=codigo_barra)
        except TarjetaAutorizacion.DoesNotExist:
            # Registrar intento fallido
            LogAutorizacion.objects.create(
                id_tarjeta_autorizacion=None,
                codigo_barra=codigo_barra,
                tipo_operacion=tipo_operacion,
                id_registro_afectado=id_registro,
                descripcion=f'Tarjeta no encontrada: {codigo_barra}',
                resultado='RECHAZADO'
            )
            return JsonResponse({
                'success': False,
                'message': 'Tarjeta de autorización no válida'
            })
        
        # Verificar si tiene permiso
        if not tarjeta.tiene_permiso(tipo_operacion):
            # Registrar intento rechazado
            LogAutorizacion.objects.create(
                id_tarjeta_autorizacion=tarjeta,
                codigo_barra=codigo_barra,
                tipo_operacion=tipo_operacion,
                id_registro_afectado=id_registro,
                descripcion=f'Sin permisos para {tipo_operacion}',
                resultado='RECHAZADO'
            )
            return JsonResponse({
                'success': False,
                'message': f'Esta tarjeta no tiene permisos para {tipo_operacion.replace("_", " ").lower()}'
            })
        
        # Autorización exitosa
        log = LogAutorizacion.objects.create(
            id_tarjeta_autorizacion=tarjeta,
            codigo_barra=codigo_barra,
            tipo_operacion=tipo_operacion,
            id_registro_afectado=id_registro,
            descripcion=f'Autorización concedida por {tarjeta.get_tipo_autorizacion_display()}',
            resultado='EXITOSO'
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Autorización concedida',
            'tarjeta_tipo': tarjeta.get_tipo_autorizacion_display(),
            'log_id': log.id_log
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al validar autorización: {str(e)}'
        })


@acceso_cajero
@require_http_methods(["POST"])
def anular_almuerzo(request, registro_id):
    """
    Anula un registro de almuerzo después de validar autorización
    """
    try:
        # Obtener el log de autorización
        log_id = request.POST.get('log_id')
        motivo = request.POST.get('motivo', 'Sin motivo especificado')
        
        if not log_id:
            return JsonResponse({
                'success': False,
                'message': 'Se requiere autorización para anular'
            })
        
        # Verificar que el log sea reciente (últimos 30 segundos)
        try:
            log = LogAutorizacion.objects.get(
                id_log=log_id,
                resultado='EXITOSO',
                fecha_hora__gte=timezone.now() - timezone.timedelta(seconds=30)
            )
        except LogAutorizacion.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Autorización expirada. Escanee nuevamente la tarjeta.'
            })
        
        # Obtener el registro de almuerzo
        registro = get_object_or_404(RegistroConsumoAlmuerzo, id_registro_consumo=registro_id)
        
        # Verificar que no esté ya anulado
        if hasattr(registro, 'anulado') and registro.anulado:
            return JsonResponse({
                'success': False,
                'message': 'Este registro ya está anulado'
            })
        
        with transaction.atomic():
            # Guardar información para el log
            hijo_nombre = registro.id_hijo.nombre_completo
            costo = registro.costo_almuerzo
            fecha = registro.fecha_consumo
            
            # Marcar como anulado (si existe el campo)
            # Si no existe, eliminar el registro
            try:
                registro.anulado = True
                registro.fecha_anulacion = timezone.now()
                registro.motivo_anulacion = motivo
                registro.save()
            except AttributeError:
                # Si no existe el campo anulado, eliminar el registro
                registro.delete()
            
            # Actualizar el log de autorización
            log.descripcion += f' | Anulado: {hijo_nombre} - Gs. {costo:,.0f} ({fecha}). Motivo: {motivo}'
            log.id_registro_afectado = registro_id
            log.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Almuerzo anulado correctamente. {hijo_nombre} - Gs. {costo:,.0f}'
            })
        
    except Exception as e:
        # Registrar error en el log si existe
        if log_id:
            try:
                log = LogAutorizacion.objects.get(id_log=log_id)
                log.resultado = 'ERROR'
                log.descripcion += f' | Error: {str(e)}'
                log.save()
            except:
                pass
        
        return JsonResponse({
            'success': False,
            'message': f'Error al anular almuerzo: {str(e)}'
        })
