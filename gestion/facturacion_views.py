"""
Vistas de Facturación Electrónica Paraguay
===========================================

Gestión completa de:
- Emisión de facturas electrónicas
- Anulación de facturas
- Reimpresión de KUDE
- Consulta de estado
- Reportes de cumplimiento
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse, FileResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone
from django.db.models import Q, Count, Sum
from decimal import Decimal
import json
from datetime import datetime, timedelta

from .models import (
    Ventas, DatosFacturacionElect, Timbrados, DatosEmpresa,
    DocumentosTributarios
)
from .facturacion_electronica import GeneradorXMLFactura, ClienteEkuatia


@login_required
@require_http_methods(["GET"])
def dashboard_facturacion(request):
    """
    Dashboard de facturación electrónica con estadísticas
    
    GET /gestion/facturacion/dashboard/
    """
    # Estadísticas del mes actual
    hoy = timezone.now()
    inicio_mes = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Facturas emitidas este mes
    facturas_mes = DatosFacturacionElect.objects.filter(
        fecha_envio__gte=inicio_mes
    )
    
    # Estadísticas
    stats = {
        'facturas_emitidas': facturas_mes.count(),
        'facturas_aceptadas': facturas_mes.filter(estado_sifen='ACEPTADA').count(),
        'facturas_rechazadas': facturas_mes.filter(estado_sifen='RECHAZADA').count(),
        'facturas_pendientes': facturas_mes.filter(estado_sifen__isnull=True).count(),
        'monto_total_emitido': Ventas.objects.filter(
            id_venta__in=facturas_mes.values_list('id_documento_id', flat=True)
        ).aggregate(total=Sum('monto_total'))['total'] or 0,
    }
    
    # Timbrados disponibles
    timbrados = Timbrados.objects.filter(
        activo=True,
        es_electronico=True
    ).values('nro_timbrado', 'fecha_inicio', 'fecha_fin').annotate(
        cantidad_emitidas=Count('documentostributarios'),
        estado='VIGENTE'  # Campo calculado para la plantilla
    )
    
    context = {
        'stats': stats,
        'timbrados': timbrados,
        'titulo': 'Dashboard - Facturación Electrónica'
    }
    
    return render(request, 'gestion/facturacion_dashboard.html', context)


@login_required
@require_http_methods(["POST"])
def emitir_factura_api(request):
    """
    API para emitir factura electrónica desde una venta
    
    POST /gestion/facturacion/api/emitir/
    Body: {
        "id_venta": 1,
        "tipo_factura": "electronica"  // electronica o fisica
    }
    
    Response:
    {
        "success": bool,
        "cdc": "...",
        "kude": "...",
        "estado": "ACEPTADA",
        "mensaje": "Factura emitida exitosamente"
    }
    """
    try:
        data = json.loads(request.body)
        id_venta = data.get('id_venta')
        tipo_factura = data.get('tipo_factura', 'electronica')
        
        if not id_venta:
            return JsonResponse({
                'success': False,
                'error': 'ID de venta requerido'
            }, status=400)
        
        # Obtener venta
        venta = get_object_or_404(Ventas, id_venta=id_venta)
        
        # Verificar que tiene timbrado
        if not venta.id_timbrado:
            return JsonResponse({
                'success': False,
                'error': 'Venta sin timbrado asignado'
            }, status=400)
        
        # Verificar que no está facturada
        if hasattr(venta, 'datosfacturacionelect'):
            return JsonResponse({
                'success': False,
                'error': 'Venta ya fue facturada'
            }, status=400)
        
        if tipo_factura == 'electronica':
            # Generar XML
            generador = GeneradorXMLFactura(venta)
            xml_factura = generador.generar_xml()
            
            # Calcular CDC
            cdc = generador.generar_cdc(xml_factura)
            
            # Enviar a Ekuatia
            cliente_ekuatia = ClienteEkuatia()
            respuesta = cliente_ekuatia.enviar_factura(xml_factura, id_venta)
            
            if respuesta['success']:
                # Guardar datos de facturación electrónica
                doc_tributario = DocumentosTributarios.objects.get_or_create(
                    id_venta=venta,
                    defaults={
                        'nro_timbrado': venta.id_timbrado,
                        'tipo_documento': 'Factura',
                        'monto_total': venta.monto_total,
                        'fecha_emision': venta.fecha
                    }
                )[0]
                
                factura_elect = DatosFacturacionElect.objects.create(
                    id_documento=doc_tributario,
                    cdc=respuesta.get('cdc', cdc),
                    url_kude=respuesta.get('kude', ''),
                    xml_transmitido=xml_factura,
                    estado_sifen=respuesta.get('estado'),
                    fecha_envio=timezone.now(),
                    fecha_respuesta=timezone.now() if respuesta['success'] else None
                )
                
                return JsonResponse({
                    'success': True,
                    'cdc': factura_elect.cdc,
                    'kude': factura_elect.url_kude,
                    'estado': factura_elect.estado_sifen,
                    'mensaje': 'Factura electrónica emitida exitosamente',
                    'id_factura': factura_elect.id_documento_id
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': respuesta.get('mensaje', 'Error desconocido')
                }, status=500)
        
        else:
            # Factura física (solo registrar)
            return JsonResponse({
                'success': False,
                'error': 'Facturación física no implementada aún'
            }, status=400)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON inválido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def anular_factura_api(request):
    """
    API para anular una factura electrónica
    
    POST /gestion/facturacion/api/anular/
    Body: {
        "id_factura": 1,
        "motivo": "Error en datos"
    }
    """
    try:
        data = json.loads(request.body)
        id_factura = data.get('id_factura')
        motivo = data.get('motivo')
        
        if not id_factura:
            return JsonResponse({
                'success': False,
                'error': 'ID de factura requerido'
            }, status=400)
        
        factura = get_object_or_404(DatosFacturacionElect, id_documento=id_factura)
        
        # Solo se pueden anular facturas aceptadas
        if factura.estado_sifen != 'ACEPTADA':
            return JsonResponse({
                'success': False,
                'error': f'No se puede anular factura con estado {factura.estado_sifen}'
            }, status=400)
        
        # En Ekuatia se anula con una nota de crédito
        # Por ahora solo marcamos como anulada
        doc_tributario = factura.id_documento
        doc_tributario.estado = 'ANULADO'
        doc_tributario.observaciones = f"Anulado: {motivo}"
        doc_tributario.save()
        
        return JsonResponse({
            'success': True,
            'mensaje': 'Factura anulada exitosamente',
            'cdc': factura.cdc
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON inválido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def descargar_kude(request, cdc):
    """
    Descarga el KUDE (QR autenticado) de una factura
    
    GET /gestion/facturacion/kude/<cdc>/
    """
    try:
        factura = get_object_or_404(DatosFacturacionElect, cdc=cdc)
        
        if not factura.url_kude:
            return HttpResponse('KUDE no disponible', status=404)
        
        cliente_ekuatia = ClienteEkuatia()
        kude_content = cliente_ekuatia.descargar_kude(cdc)
        
        if kude_content:
            return FileResponse(
                kude_content,
                content_type='image/png',
                as_attachment=True,
                filename=f'KUDE_{cdc}.png'
            )
        else:
            return HttpResponse('Error descargando KUDE', status=500)
            
    except Exception as e:
        return HttpResponse(f'Error: {str(e)}', status=500)


@login_required
@require_http_methods(["GET"])
def listar_facturas(request):
    """
    Lista todas las facturas electrónicas emitidas con opciones de filtrado
    
    GET /gestion/facturacion/listado/
    """
    # Filtros
    estado = request.GET.get('estado', '')
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    
    # Base query
    facturas = DatosFacturacionElect.objects.select_related(
        'id_documento__id_venta',
        'id_documento__id_venta__id_cliente'
    ).all()
    
    # Aplicar filtros
    if estado:
        facturas = facturas.filter(estado_sifen=estado)
    
    if fecha_inicio:
        try:
            fecha_ini = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            facturas = facturas.filter(fecha_envio__gte=fecha_ini)
        except ValueError:
            pass
    
    if fecha_fin:
        try:
            fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')
            facturas = facturas.filter(fecha_envio__lte=fecha_fin_dt)
        except ValueError:
            pass
    
    # Paginación
    page = int(request.GET.get('page', 1))
    per_page = 20
    total = facturas.count()
    start = (page - 1) * per_page
    end = start + per_page
    
    facturas_pagina = facturas[start:end]
    
    context = {
        'facturas': facturas_pagina,
        'total': total,
        'pagina_actual': page,
        'total_paginas': (total + per_page - 1) // per_page,
        'titulo': 'Listado de Facturas Electrónicas'
    }
    
    return render(request, 'gestion/facturacion_listado.html', context)


@login_required
@require_http_methods(["GET"])
def reporte_cumplimiento(request):
    """
    Reporte de cumplimiento legal de facturación electrónica
    
    GET /gestion/facturacion/reporte-cumplimiento/
    """
    hoy = timezone.now()
    
    # Últimos 30 días
    hace_30_dias = hoy - timedelta(days=30)
    
    # Estadísticas de cumplimiento
    facturas_30d = DatosFacturacionElect.objects.filter(
        fecha_envio__gte=hace_30_dias
    )
    
    stats = {
        'total_facturadas': facturas_30d.count(),
        'aceptadas': facturas_30d.filter(estado_sifen='ACEPTADA').count(),
        'rechazadas': facturas_30d.filter(estado_sifen='RECHAZADA').count(),
        'pendientes': facturas_30d.filter(estado_sifen__isnull=True).count(),
        'porcentaje_aceptacion': (
            (facturas_30d.filter(estado_sifen='ACEPTADA').count() / facturas_30d.count() * 100)
            if facturas_30d.count() > 0 else 0
        ),
        'monto_total_sin_iva': Ventas.objects.filter(
            id_venta__in=facturas_30d.values_list('id_documento__id_venta_id', flat=True)
        ).aggregate(
            total=Sum(
                'monto_total' / Decimal('1.1')
            )
        )['total'] or 0,
    }
    
    context = {
        'stats': stats,
        'periodo': f"{hace_30_dias.strftime('%d/%m/%Y')} - {hoy.strftime('%d/%m/%Y')}",
        'titulo': 'Reporte de Cumplimiento - Facturación Electrónica'
    }
    
    return render(request, 'gestion/facturacion_reporte_cumplimiento.html', context)
