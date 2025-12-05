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

from .models import (
    TipoAlmuerzo, 
    RegistroConsumoAlmuerzo, 
    CuentaAlmuerzoMensual,
    PagoCuentaAlmuerzo,
    Tarjeta,
    Hijo
)


# =============================================================================
# PÁGINA PRINCIPAL DE REPORTES
# =============================================================================

def almuerzo_reportes(request):
    """
    Página principal de reportes de almuerzos con estadísticas rápidas
    """
    hoy = date.today()
    
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
                
                # Actualizar lista de últimos registros
                context['ultimos_registros'] = RegistroConsumoAlmuerzo.objects.select_related(
                    'id_hijo', 'id_tipo_almuerzo'
                ).order_by('-fecha_consumo', '-hora_registro')[:10]
                
        except Exception as e:
            context['error'] = f"❌ Error al registrar: {str(e)}"
    
    return render(request, 'pos/almuerzo.html', context)


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

@require_http_methods(["GET"])
def reporte_almuerzos_diarios(request):
    """
    Reporte de almuerzos del día o rango de fechas
    """
    fecha_desde = request.GET.get('fecha_desde', timezone.now().date())
    fecha_hasta = request.GET.get('fecha_hasta', timezone.now().date())
    
    registros = RegistroConsumoAlmuerzo.objects.filter(
        fecha_consumo__range=[fecha_desde, fecha_hasta]
    ).select_related('id_hijo', 'id_tipo_almuerzo', 'nro_tarjeta').order_by('-fecha_consumo', '-hora_registro')
    
    total = registros.aggregate(
        cantidad=Count('id_registro_consumo'),
        monto_total=Sum('costo_almuerzo')
    )
    
    context = {
        'registros': registros,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'total': total
    }
    
    return render(request, 'pos/almuerzo_reporte_diario.html', context)


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

