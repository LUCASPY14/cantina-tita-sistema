"""
Vista POS General - Punto de venta multi-producto
Gestiona ventas de productos generales con:
- Búsqueda por código de barras / texto
- Carrito de compras
- Pagos mixtos (efectivo, tarjeta débito/crédito, tarjeta estudiante)
- Validación de stock en tiempo real
- Cálculo automático de comisiones
- Integración con restricciones alimentarias
"""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction, models
from django.utils import timezone
from django.db.models import Q, F, Sum
from decimal import Decimal
from datetime import datetime
import json
import io

# ReportLab para PDF
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode import code128
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF

from .models import (
    Producto, StockUnico, Cliente, Hijo, Tarjeta, MediosPago,
    Ventas, DetalleVenta, PagosVenta, Empleado, TiposPago, TipoCliente, ListaPrecios,
    TarifasComision, DetalleComisionVenta, CierresCaja,
    RestriccionesHijos, ProductoAlergeno
)
from .restricciones_matcher import verificar_restricciones_venta


@require_http_methods(["GET"])
def pos_general(request):
    """
    Vista principal del POS General
    Renderiza la interfaz del punto de venta con Bootstrap 5
    """
    context = {
        'titulo': 'POS General - Cantina Tita',
        'fecha_actual': timezone.now().strftime('%Y-%m-%d'),
        'hora_actual': timezone.now().strftime('%H:%M:%S'),
    }
    return render(request, 'pos/pos_bootstrap.html', context)


@require_http_methods(["POST"])
def buscar_producto_api(request):
    """
    API: Buscar productos por código de barras o texto
    
    POST /pos/general/api/buscar-producto/
    Body: {
        "query": "código_barras o texto de búsqueda",
        "limite": 10  (opcional)
    }
    
    Response: {
        "success": true,
        "productos": [
            {
                "id": 1,
                "codigo_barra": "7891234567890",
                "descripcion": "Coca Cola 500ml",
                "precio_venta": 8000,
                "stock_actual": 45.0,
                "permite_stock_negativo": false,
                "categoria": "Bebidas",
                "unidad_medida": "Unidad",
                "impuesto": "IVA 10%",
                "alergenos": ["Cafeína"]
            }
        ]
    }
    """
    try:
        data = json.loads(request.body)
        query = data.get('query', '').strip()
        limite = int(data.get('limite', 10))
        
        if not query:
            return JsonResponse({
                'success': False,
                'error': 'Debe ingresar un criterio de búsqueda'
            }, status=400)
        
        # Búsqueda: primero por código exacto, luego por texto
        productos = Producto.objects.filter(activo=True)
        
        # Intenta buscar por código de barras exacto primero
        producto_exacto = productos.filter(codigo_barra__iexact=query).select_related(
            'id_categoria', 'id_unidad_de_medida', 'id_impuesto'
        ).prefetch_related(
            'precios__id_lista',
            'productoalergeno_set__id_alergeno'
        ).first()
        
        if producto_exacto:
            # Si encuentra código exacto, devuelve solo ese producto
            productos_encontrados = [producto_exacto]
        else:
            # Búsqueda por texto en descripción o código parcial (OPTIMIZADO)
            productos_encontrados = productos.filter(
                Q(descripcion__icontains=query) |
                Q(codigo_barra__icontains=query)
            ).select_related(
                'id_categoria', 'id_unidad_de_medida', 'id_impuesto', 'stock'
            ).prefetch_related(
                'precios__id_lista',
                'productoalergeno_set__id_alergeno'
            )[:limite]
        
        # Serializar productos (sin queries adicionales)
        resultado = []
        for p in productos_encontrados:
            # Obtener precio de venta actual (ya prefetched)
            precio_producto = None
            for precio in p.precios.all():
                if precio.id_lista and precio.id_lista.activo:
                    if not precio_producto or precio.id_lista.fecha_vigencia > precio_producto.id_lista.fecha_vigencia:
                        precio_producto = precio
            
            precio_venta = precio_producto.precio_unitario_neto if precio_producto else 5000
            
            # Stock actual (ya en select_related)
            stock_actual = p.stock.stock_actual if hasattr(p, 'stock') and p.stock else 0
            
            # Alérgenos asociados (ya prefetched)
            alergenos = [pa.id_alergeno.nombre for pa in p.productoalergeno_set.all() if pa.id_alergeno]
            
            resultado.append({
                'id': p.id_producto,
                'codigo_barra': p.codigo_barra or '',
                'descripcion': p.descripcion,
                'precio': int(precio_venta),
                'stock': float(stock_actual),
                'activo': p.activo,
                'alergenos': alergenos
            })
        
        return JsonResponse({
            'success': True,
            'productos': resultado,
            'total': len(resultado)
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON inválido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al buscar productos: {str(e)}'
        }, status=500)


@require_http_methods(["POST"])
def verificar_tarjeta_api(request):
    """
    API: Verificar si una tarjeta existe y obtener datos del estudiante
    
    POST /pos/buscar-tarjeta/
    Body: {
        "nro_tarjeta": "12345678"  O "codigo_tarjeta": "12345678"
    }
    
    Response: {
        "success": true,
        "estudiante": {
            "id_hijo": 1,
            "nombre": "Juan Pérez",
            "saldo": 50000,
            "cliente": "María Pérez",
            "grado": "5to Grado",
            "restricciones": [...]
        }
    }
    """
    try:
        # Leer el cuerpo de la solicitud
        body = request.body.decode('utf-8') if isinstance(request.body, bytes) else request.body
        data = json.loads(body) if body else {}
        
        # Aceptar tanto 'nro_tarjeta' como 'codigo_tarjeta'
        nro_tarjeta = (data.get('nro_tarjeta') or data.get('codigo_tarjeta') or '').strip()
        
        if not nro_tarjeta:
            return JsonResponse({
                'success': False,
                'error': 'Debe ingresar un número de tarjeta'
            }, status=400)
        
        # Buscar tarjeta activa - usar relación correcta: id_hijo__id_cliente_responsable
        tarjeta = Tarjeta.objects.select_related(
            'id_hijo',
            'id_hijo__id_cliente_responsable'
        ).filter(
            nro_tarjeta=nro_tarjeta,
            estado='Activa'
        ).first()
        
        if not tarjeta:
            return JsonResponse({
                'success': False,
                'error': 'Tarjeta no encontrada o inactiva'
            }, status=404)
        
        # Obtener restricciones del hijo
        restricciones = list(RestriccionesHijos.objects.filter(
            id_hijo=tarjeta.id_hijo,
            activo=True
        ).values('tipo_restriccion', 'descripcion', 'severidad'))
        
        # Construir respuesta con toda la información necesaria
        return JsonResponse({
            'success': True,
            'estudiante': {
                'id_hijo': tarjeta.id_hijo.id_hijo,
                'nombre': f"{tarjeta.id_hijo.nombre} {tarjeta.id_hijo.apellido}",
                'saldo': int(tarjeta.saldo_actual),
                'grado': tarjeta.id_hijo.grado or 'N/A',
                'cliente': tarjeta.id_hijo.id_cliente_responsable.nombre_completo if tarjeta.id_hijo.id_cliente_responsable else 'N/A',
                'nro_tarjeta': tarjeta.nro_tarjeta,
                'foto_perfil': tarjeta.id_hijo.foto_perfil or None,
                'restricciones': restricciones
            }
        })
        

        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON inválido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al verificar tarjeta: {str(e)}'
        }, status=500)


@require_http_methods(["POST"])
def verificar_restricciones_carrito_api(request):
    """
    API: Verificar restricciones alimentarias del carrito completo
    
    POST /pos/general/api/verificar-restricciones-carrito/
    Body: {
        "id_hijo": 1,
        "productos": [
            {"id_producto": 5, "cantidad": 2},
            {"id_producto": 12, "cantidad": 1}
        ]
    }
    
    Response: {
        "success": true,
        "tiene_alertas": true,
        "alertas": [
            {
                "id_producto": 5,
                "nombre_producto": "Brownie de Chocolate",
                "restriccion": "Alergia al maní",
                "severidad": "ALTA",
                "razon": "Producto contiene trazas de frutos secos"
            }
        ]
    }
    """
    try:
        data = json.loads(request.body)
        id_hijo = data.get('id_hijo')
        productos = data.get('productos', [])
        
        if not id_hijo:
            return JsonResponse({
                'success': False,
                'error': 'Debe especificar el hijo'
            }, status=400)
        
        # Obtener hijo
        hijo = Hijo.objects.filter(id_hijo=id_hijo).first()
        if not hijo:
            return JsonResponse({
                'success': False,
                'error': 'Hijo no encontrado'
            }, status=404)
        
        # Verificar restricciones para cada producto
        alertas = []
        
        for item in productos:
            id_producto = item.get('id_producto')
            producto = Producto.objects.filter(id_producto=id_producto).first()
            
            if not producto:
                continue
            
            # Usar función de matching automático para verificar restricciones
            restricciones_hijo = RestriccionesHijos.objects.filter(
                id_hijo=hijo,
                activo=True
            )
            
            for restriccion in restricciones_hijo:
                tiene_conflicto, razon, confianza = ProductoRestriccionMatcher.analizar_producto(
                    producto, restriccion
                )
                
                if tiene_conflicto:
                    # Determinar severidad (de baja a alta según confianza)
                    if confianza >= 90:
                        severidad = 'ALTA'
                    elif confianza >= 70:
                        severidad = 'MEDIA'
                    else:
                        severidad = 'BAJA'
                    
                    alertas.append({
                        'id_producto': producto.id_producto,
                        'nombre_producto': producto.descripcion,
                        'restriccion': restriccion.tipo_restriccion,
                        'severidad': severidad,
                        'razon': razon,
                        'confianza': confianza
                    })
        
        return JsonResponse({
            'success': True,
            'tiene_alertas': len(alertas) > 0,
            'alertas': alertas
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON inválido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al verificar restricciones: {str(e)}'
        }, status=500)


@require_http_methods(["POST"])
@transaction.atomic
@require_http_methods(["POST"])
@transaction.atomic
def procesar_venta_api(request):
    """
    API: Procesar venta completa con validaciones
    
    POST /pos/procesar-venta/
    Body: {
        "id_hijo": 10,
        "productos": [
            {"id_producto": 1, "cantidad": 2, "precio_unitario": 5000}
        ],
        "pagos": [
            {"id_medio_pago": 1, "monto": 10000, "nro_tarjeta": "00203"}
        ],
        "tipo_venta": "CONTADO",
        "emitir_factura": true,
        "medio_pago_id": 1
    }
    """
    try:
        data = json.loads(request.body)
        
        # Extrar datos
        id_hijo = data.get('id_hijo')
        productos_data = data.get('productos', [])
        pagos_data = data.get('pagos', [])
        tipo_venta = data.get('tipo_venta', 'CONTADO')
        emitir_factura = data.get('emitir_factura', False)
        medio_pago_id = data.get('medio_pago_id', 1)
        
        # Validaciones básicas
        if not productos_data:
            return JsonResponse({
                'success': False,
                'error': 'No hay productos en el carrito'
            }, status=400)
        
        if not pagos_data:
            return JsonResponse({
                'success': False,
                'error': 'Debe especificar al menos un medio de pago'
            }, status=400)
        
        # Obtener hijo y cliente
        hijo = None
        cliente = None
        tarjeta = None
        
        if id_hijo:
            hijo = Hijo.objects.select_related('id_cliente_responsable').filter(
                id_hijo=id_hijo,
                activo=True
            ).first()
            
            if hijo:
                cliente = hijo.id_cliente_responsable
                
                # Obtener tarjeta si existe
                tarjeta = Tarjeta.objects.filter(
                    id_hijo=hijo,
                    estado='Activa'
                ).first()
        
        # Si no hay cliente, usar cliente público
        if not cliente:
            cliente = Cliente.objects.filter(
                Q(nombres__icontains='público') | Q(apellidos__icontains='público')
            ).first()
            
            if not cliente:
                return JsonResponse({
                    'success': False,
                    'error': 'Cliente público no configurado'
                }, status=500)
        
        # Validar medio de pago
        medio_pago = MediosPago.objects.filter(id_medio_pago=medio_pago_id).first()
        if not medio_pago:
            return JsonResponse({
                'success': False,
                'error': f'Medio de pago {medio_pago_id} no válido'
            }, status=400)
        
        # Validar factura electrónica
        if emitir_factura:
            # Verificar si el medio de pago permite factura
            medios_permitidos = [1, 2, 3, 4, 5]  # No es tarjeta estudiantil
            if medio_pago_id == 6:
                return JsonResponse({
                    'success': False,
                    'error': 'Tarjeta Estudiantil no genera factura electrónica'
                }, status=400)
            
            if not hijo:
                return JsonResponse({
                    'success': False,
                    'error': 'Para emitir factura debe verificar tarjeta de estudiante'
                }, status=400)
        
        # Procesar productos y calcular total
        monto_total = 0
        detalles_venta = []
        
        for item in productos_data:
            id_producto = item.get('id_producto')
            cantidad = Decimal(str(item.get('cantidad', 0)))
            precio_unitario = int(item.get('precio_unitario', 0))
            
            # Validar producto
            producto = Producto.objects.filter(
                id_producto=id_producto,
                activo=True
            ).select_related('stock').first()
            
            if not producto:
                return JsonResponse({
                    'success': False,
                    'error': f'Producto {id_producto} no encontrado'
                }, status=404)
            
            # Validar stock
            stock_actual = producto.stock.stock_actual if hasattr(producto, 'stock') else 0
            
            if not producto.permite_stock_negativo and stock_actual < cantidad:
                return JsonResponse({
                    'success': False,
                    'error': f'Stock insuficiente: {producto.descripcion}'
                }, status=400)
            
            subtotal = precio_unitario * int(cantidad)
            monto_total += subtotal
            
            detalles_venta.append({
                'producto': producto,
                'cantidad': cantidad,
                'precio_unitario': precio_unitario,
                'subtotal': subtotal
            })
        
        # VALIDAR RESTRICCIONES ALIMENTARIAS si existe hijo
        if hijo:
            from gestion.restricciones_matcher import ProductoRestriccionMatcher
            from gestion.models import RestriccionesHijos
            
            # Obtener restricciones del hijo
            restricciones_hijo = RestriccionesHijos.objects.filter(
                id_hijo=hijo,
                activo=True
            )
            
            # Si tiene restricciones, validar todos los productos
            if restricciones_hijo.exists():
                alertas_restricciones = []
                
                for detalle in detalles_venta:
                    producto = detalle['producto']
                    
                    for restriccion in restricciones_hijo:
                        tiene_conflicto, razon, confianza = ProductoRestriccionMatcher.analizar_producto(
                            producto, restriccion
                        )
                        
                        if tiene_conflicto:
                            # Determinar severidad según confianza
                            if confianza >= 90:
                                severidad = 'ALTA'
                            elif confianza >= 70:
                                severidad = 'MEDIA'
                            else:
                                severidad = 'BAJA'
                            
                            # Si es severidad ALTA, bloquear la venta
                            if severidad == 'ALTA':
                                return JsonResponse({
                                    'success': False,
                                    'error': f'ALERTA DE RESTRICCIÓN ALTA: {producto.descripcion} contiene {restriccion.tipo_restriccion}. Razón: {razon}. Requiere autorización.',
                                    'tipo': 'restriccion_bloqueada',
                                    'restriccion': {
                                        'producto': producto.descripcion,
                                        'tipo': restriccion.tipo_restriccion,
                                        'severidad': severidad,
                                        'razon': razon,
                                        'confianza': confianza
                                    }
                                }, status=403)
                            
                            # Alertas de severidad MEDIA/BAJA
                            alertas_restricciones.append({
                                'id_producto': producto.id_producto,
                                'nombre_producto': producto.descripcion,
                                'restriccion': restriccion.tipo_restriccion,
                                'severidad': severidad,
                                'razon': razon,
                                'confianza': confianza
                            })
                
                # Si hay alertas, devolver para confirmación
                if alertas_restricciones:
                    # Guardar alertas en sesión para confirmar después
                    request.session['alertas_restricciones_pendientes'] = alertas_restricciones
        
        # Validar que los pagos sumen correctamente
        total_pagos = sum(p.get('monto', 0) for p in pagos_data)
        
        if total_pagos != monto_total:
            return JsonResponse({
                'success': False,
                'error': f'Total de pagos ({total_pagos}) no coincide con total de venta ({monto_total})'
            }, status=400)
        
        # Obtener o crear tipo de pago
        tipo_pago = TiposPago.objects.filter(descripcion='CONTADO').first()
        if not tipo_pago:
            tipo_pago = TiposPago.objects.create(descripcion='CONTADO')
        
        # Obtener empleado cajero (usar usuario del request)
        empleado = None
        if request.user.is_authenticated:
            try:
                empleado = Empleado.objects.filter(usuario=request.user.username).first()
            except:
                pass
        
        # Usar empleado genérico si no hay usuario
        if not empleado:
            empleado = Empleado.objects.filter(nombre__icontains='sistema').first()
            if not empleado:
                # Crear empleado genérico
                empleado = Empleado.objects.create(
                    usuario='sistema',
                    nombre='Sistema',
                    apellido='Automático',
                    activo=True
                )
        
        # Crear venta
        nro_factura = None
        if emitir_factura and tarjeta:
            # Generar número de factura (incrementar desde el último)
            ultima_venta = Ventas.objects.filter(
                nro_factura_venta__isnull=False
            ).order_by('-nro_factura_venta').first()
            
            nro_factura = (ultima_venta.nro_factura_venta + 1) if ultima_venta else 1
        
        venta = Ventas.objects.create(
            id_cliente=cliente,
            id_hijo=hijo,
            id_tipo_pago=tipo_pago,
            id_empleado_cajero=empleado,
            fecha=timezone.now(),
            monto_total=monto_total,
            saldo_pendiente=0,
            estado_pago='PAGADA',
            estado='PROCESADO',
            tipo_venta=tipo_venta,
            nro_factura_venta=nro_factura,
            genera_factura_legal=emitir_factura
        )
        
        # Crear detalles de venta y actualizar stock
        for detalle in detalles_venta:
            DetalleVenta.objects.create(
                id_venta=venta,
                id_producto=detalle['producto'],
                cantidad=detalle['cantidad'],
                precio_unitario=detalle['precio_unitario'],
                subtotal_total=detalle['subtotal']
            )
            
            # Actualizar stock
            stock = detalle['producto'].stock
            stock.stock_actual -= detalle['cantidad']
            stock.save()
        
        # Procesar pagos
        for pago_data in pagos_data:
            id_medio = pago_data.get('id_medio_pago')
            monto = pago_data.get('monto')
            nro_tarjeta = pago_data.get('nro_tarjeta')
            
            medio = MediosPago.objects.filter(id_medio_pago=id_medio).first()
            if not medio:
                continue
            
            tarjeta_pago = None
            
            # Procesar descuento de saldo si es tarjeta
            if nro_tarjeta and id_medio == 6:  # Tarjeta Estudiantil
                tarjeta_pago = Tarjeta.objects.filter(nro_tarjeta=nro_tarjeta).first()
                if tarjeta_pago:
                    tarjeta_pago.saldo_actual -= monto
                    if tarjeta_pago.saldo_actual < 0:
                        tarjeta_pago.saldo_actual = 0
                    tarjeta_pago.save()
            
            # Registrar pago
            PagosVenta.objects.create(
                id_venta=venta,
                id_medio_pago=medio,
                nro_tarjeta_usada=tarjeta_pago,
                monto_aplicado=monto,
                fecha_pago=timezone.now(),
                estado='PROCESADO'
            )
        
        # Retornar éxito
        respuesta = {
            'success': True,
            'id_venta': venta.id_venta,
            'nro_factura': venta.nro_factura_venta,
            'monto_total': monto_total,
            'mensaje': '✅ Venta procesada exitosamente'
        }
        
        # Incluir alertas si las hay
        if 'alertas_restricciones_pendientes' in request.session:
            respuesta['alertas_restricciones'] = request.session.pop('alertas_restricciones_pendientes')
            respuesta['advertencia'] = 'Venta procesada con alertas de restricciones alimentarias'
        
        return JsonResponse(respuesta)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON inválido'
        }, status=400)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': f'Error al procesar venta: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def imprimir_ticket_venta(request, id_venta):
    """
    Generar e imprimir ticket de venta en formato PDF (80mm ancho)
    Optimizado para impresoras térmicas
    
    GET /pos/general/ticket/<id_venta>/
    """
    try:
        # Obtener venta con detalles
        venta = get_object_or_404(
            Ventas.objects.select_related(
                'id_cliente', 'id_hijo', 'id_empleado_cajero'
            ).prefetch_related(
                'detalles__id_producto',
                'pagos__id_medio_pago'
            ),
            id_venta=id_venta
        )
        
        # Crear buffer para PDF
        buffer = io.BytesIO()
        
        # Tamaño de ticket térmico: 80mm ancho
        ancho_ticket = 80 * mm
        alto_estimado = 250 * mm  # Se ajusta dinámicamente
        
        # Crear PDF
        p = canvas.Canvas(buffer, pagesize=(ancho_ticket, alto_estimado))
        
        # Configuración
        y = alto_estimado - 10 * mm
        margen_izq = 5 * mm
        ancho_util = ancho_ticket - (2 * margen_izq)
        
        # Encabezado
        p.setFont("Helvetica-Bold", 14)
        p.drawCentredString(ancho_ticket / 2, y, "CANTINA TITA")
        y -= 5 * mm
        
        p.setFont("Helvetica", 8)
        p.drawCentredString(ancho_ticket / 2, y, "Colegio XYZ")
        y -= 3 * mm
        p.drawCentredString(ancho_ticket / 2, y, "RUC: 12345678-9")
        y -= 3 * mm
        p.drawCentredString(ancho_ticket / 2, y, "Tel: (021) 123-456")
        y -= 6 * mm
        
        # Línea separadora
        p.line(margen_izq, y, ancho_ticket - margen_izq, y)
        y -= 5 * mm
        
        # Información de venta
        p.setFont("Helvetica-Bold", 10)
        p.drawCentredString(ancho_ticket / 2, y, "TICKET DE VENTA")
        y -= 5 * mm
        
        p.setFont("Helvetica", 8)
        p.drawString(margen_izq, y, f"Nro: {venta.id_venta}")
        y -= 3.5 * mm
        
        fecha_str = venta.fecha.strftime('%d/%m/%Y %H:%M')
        p.drawString(margen_izq, y, f"Fecha: {fecha_str}")
        y -= 3.5 * mm
        
        p.drawString(margen_izq, y, f"Cajero: {venta.id_empleado_cajero.nombre} {venta.id_empleado_cajero.apellido}")
        y -= 3.5 * mm
        
        if venta.id_hijo:
            p.drawString(margen_izq, y, f"Cliente: {venta.id_hijo.nombre} {venta.id_hijo.apellido}")
            y -= 3.5 * mm
        elif venta.id_cliente:
            p.drawString(margen_izq, y, f"Cliente: {venta.id_cliente.nombre_completo}")
            y -= 3.5 * mm
        
        y -= 3 * mm
        p.line(margen_izq, y, ancho_ticket - margen_izq, y)
        y -= 5 * mm
        
        # Encabezado de productos
        p.setFont("Helvetica-Bold", 8)
        p.drawString(margen_izq, y, "CANT")
        p.drawString(margen_izq + 12 * mm, y, "DESCRIPCIÓN")
        p.drawRightString(ancho_ticket - margen_izq, y, "IMPORTE")
        y -= 4 * mm
        
        p.line(margen_izq, y, ancho_ticket - margen_izq, y)
        y -= 4 * mm
        
        # Productos
        p.setFont("Helvetica", 7)
        for detalle in venta.detalles.all():
            # Cantidad
            p.drawString(margen_izq, y, str(int(detalle.cantidad)))
            
            # Descripción (puede ser larga, truncar si es necesario)
            descripcion = detalle.id_producto.descripcion
            if len(descripcion) > 25:
                descripcion = descripcion[:22] + "..."
            p.drawString(margen_izq + 12 * mm, y, descripcion)
            
            # Subtotal
            subtotal_str = f"Gs. {detalle.subtotal_total:,.0f}"
            p.drawRightString(ancho_ticket - margen_izq, y, subtotal_str)
            y -= 3.5 * mm
            
            # Precio unitario (línea adicional)
            precio_unit_str = f"@Gs. {detalle.precio_unitario:,.0f}"
            p.setFont("Helvetica", 6)
            p.drawString(margen_izq + 12 * mm, y, precio_unit_str)
            p.setFont("Helvetica", 7)
            y -= 4 * mm
        
        y -= 2 * mm
        p.line(margen_izq, y, ancho_ticket - margen_izq, y)
        y -= 5 * mm
        
        # Total
        p.setFont("Helvetica-Bold", 12)
        p.drawString(margen_izq, y, "TOTAL:")
        total_str = f"Gs. {venta.monto_total:,.0f}"
        p.drawRightString(ancho_ticket - margen_izq, y, total_str)
        y -= 6 * mm
        
        p.line(margen_izq, y, ancho_ticket - margen_izq, y)
        y -= 5 * mm
        
        # Medios de pago
        p.setFont("Helvetica-Bold", 8)
        p.drawString(margen_izq, y, "MEDIOS DE PAGO:")
        y -= 4 * mm
        
        p.setFont("Helvetica", 7)
        for pago in venta.pagos.all():
            medio = pago.id_medio_pago.descripcion
            monto_str = f"Gs. {pago.monto_aplicado:,.0f}"
            p.drawString(margen_izq + 3 * mm, y, medio)
            p.drawRightString(ancho_ticket - margen_izq, y, monto_str)
            y -= 3.5 * mm
        
        y -= 3 * mm
        p.line(margen_izq, y, ancho_ticket - margen_izq, y)
        y -= 5 * mm
        
        # Mensaje final
        p.setFont("Helvetica", 7)
        p.drawCentredString(ancho_ticket / 2, y, "¡Gracias por su compra!")
        y -= 4 * mm
        p.drawCentredString(ancho_ticket / 2, y, "Vuelva pronto")
        y -= 6 * mm
        
        # Código de barras (opcional)
        try:
            barcode = code128.Code128(str(venta.id_venta), barHeight=10*mm, barWidth=0.5*mm)
            barcode.drawOn(p, margen_izq + 10*mm, y - 12*mm)
            y -= 15 * mm
        except:
            pass
        
        # Finalizar PDF
        p.showPage()
        p.save()
        
        # Preparar respuesta
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="ticket_venta_{venta.id_venta}.pdf"'
        
        return response
        
    except Ventas.DoesNotExist:
        return HttpResponse('Venta no encontrada', status=404)
    except Exception as e:
        return HttpResponse(f'Error al generar ticket: {str(e)}', status=500)


@require_http_methods(["GET"])
def dashboard_ventas_dia(request):
    """
    Dashboard de ventas del día
    Resumen de ventas, productos vendidos, ingresos y métodos de pago
    
    GET /pos/dashboard/
    """
    from datetime import datetime
    from django.db.models import Sum, Count, F
    from decimal import Decimal
    
    try:
        hoy = datetime.now().date()
        hoy_dt = datetime.now()  # Para el template con formato de fecha completo
        
        # Ventas del día
        ventas_hoy = Ventas.objects.filter(
            fecha__date=hoy
        ).select_related('id_cliente', 'id_hijo')
        
        # Estadísticas generales
        total_ventas = ventas_hoy.count()
        monto_total = ventas_hoy.aggregate(total=Sum('monto_total'))['total'] or Decimal('0')
        
        # Productos más vendidos
        productos_vendidos = DetalleVenta.objects.filter(
            id_venta__fecha__date=hoy
        ).values('id_producto__descripcion').annotate(
            cantidad_total=Sum('cantidad'),
            ingresos=Sum(F('cantidad') * F('precio_unitario'), output_field=models.DecimalField())
        ).order_by('-cantidad_total')[:10]
        
        # Ingresos por método de pago
        ingresos_pago = PagosVenta.objects.filter(
            id_venta__fecha__date=hoy
        ).values('id_medio_pago__descripcion').annotate(
            total=Sum('monto_aplicado'),
            cantidad=Count('id_pago_venta')
        ).order_by('-total')
        
        # Evolución por hora
        from django.db.models.functions import ExtractHour
        evoluccion_hora = Ventas.objects.filter(
            fecha__date=hoy
        ).annotate(
            hora=ExtractHour('fecha')
        ).values('hora').annotate(
            ventas=Count('id_venta'),
            monto=Sum('monto_total')
        ).order_by('hora')
        
        # Estadísticas de ventas por tarjeta de estudiante vs efectivo
        ventas_tarjeta_est = DetalleVenta.objects.filter(
            id_venta__fecha__date=hoy
        ).filter(
            id_venta__id_hijo__isnull=False
        ).aggregate(
            cantidad=Count('id_detalle'),
            monto=Sum('precio_unitario')
        )
        
        # Top clientes
        top_clientes = Ventas.objects.filter(
            fecha__date=hoy
        ).values('id_cliente__nombres', 'id_cliente__apellidos').annotate(
            cantidad_compras=Count('id_venta'),
            monto_total_calc=Sum('monto_total')
        ).order_by('-monto_total_calc')[:5]
        
        # Preparar datos para gráficas
        horas_data = [item['hora'] or 0 for item in evoluccion_hora]
        ventas_x_hora = [item['ventas'] or 0 for item in evoluccion_hora]
        montos_x_hora = [float(item['monto'] or 0) for item in evoluccion_hora]
        
        # Datos de métodos de pago para gráfica pie
        metodos_labels = [item['id_medio_pago__descripcion'] for item in ingresos_pago]
        metodos_montos = [float(item['total']) for item in ingresos_pago]
        
        # Productos vendidos para gráfica
        productos_labels = [item['id_producto__descripcion'][:20] for item in productos_vendidos]
        productos_cantidades = [int(item['cantidad_total']) for item in productos_vendidos]
        
        context = {
            'hoy': hoy_dt,
            'total_ventas': total_ventas,
            'monto_total': float(monto_total),
            'productos_vendidos': list(productos_vendidos),
            'ingresos_pago': list(ingresos_pago),
            'top_clientes': list(top_clientes),
            'ventas_tarjeta_est': ventas_tarjeta_est,
            
            # Para gráficas
            'horas_data': horas_data,
            'ventas_x_hora': ventas_x_hora,
            'montos_x_hora': montos_x_hora,
            'metodos_labels': metodos_labels,
            'metodos_montos': metodos_montos,
            'productos_labels': productos_labels,
            'productos_cantidades': productos_cantidades,
        }
        
        # Si es AJAX, devolver JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(context)
        
        # Si no, renderizar template
        return render(request, 'pos/dashboard_ventas.html', context)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        error_msg = f'Error al generar dashboard: {str(e)}'
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': error_msg}, status=500)
        
        return render(request, 'pos/dashboard_ventas.html', {
            'error': error_msg
        })
