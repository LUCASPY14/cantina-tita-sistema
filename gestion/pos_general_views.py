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
from django.db import transaction
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
    Renderiza la interfaz del punto de venta
    """
    context = {
        'titulo': 'POS General',
        'fecha_actual': timezone.now().strftime('%Y-%m-%d'),
        'hora_actual': timezone.now().strftime('%H:%M:%S'),
    }
    return render(request, 'gestion/pos_general.html', context)


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
        producto_exacto = productos.filter(codigo_barra__iexact=query).first()
        
        if producto_exacto:
            # Si encuentra código exacto, devuelve solo ese producto
            productos_encontrados = [producto_exacto]
        else:
            # Búsqueda por texto en descripción o código parcial
            productos_encontrados = productos.filter(
                Q(descripcion__icontains=query) |
                Q(codigo_barra__icontains=query)
            ).select_related(
                'id_categoria', 'id_unidad_de_medida', 'id_impuesto', 'stock'
            )[:limite]
        
        # Serializar productos
        resultado = []
        for p in productos_encontrados:
            # Obtener precio de venta actual (última lista de precios)
            precio_producto = p.precios.filter(
                id_lista_precio__activo=True
            ).order_by('-id_lista_precio__fecha_vigencia').first()
            
            precio_venta = precio_producto.precio_venta if precio_producto else 0
            
            # Stock actual
            stock_actual = p.stock.stock_actual if hasattr(p, 'stock') else 0
            
            # Alérgenos asociados
            alergenos = list(
                p.productoalergeno_set.values_list('id_alergeno__nombre', flat=True)
            )
            
            resultado.append({
                'id': p.id_producto,
                'codigo_barra': p.codigo_barra or '',
                'descripcion': p.descripcion,
                'precio_venta': int(precio_venta),
                'stock_actual': float(stock_actual),
                'permite_stock_negativo': p.permite_stock_negativo,
                'categoria': p.id_categoria.descripcion if p.id_categoria else '',
                'unidad_medida': p.id_unidad_de_medida.descripcion if p.id_unidad_de_medida else '',
                'impuesto': p.id_impuesto.descripcion if p.id_impuesto else '',
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
    
    POST /pos/general/api/verificar-tarjeta/
    Body: {
        "codigo_tarjeta": "12345678"
    }
    
    Response: {
        "success": true,
        "tarjeta_valida": true,
        "estudiante": {
            "id_hijo": 1,
            "nombre_completo": "Juan Pérez",
            "saldo_actual": 50000,
            "cliente": "María Pérez",
            "restricciones": [
                {"tipo": "Alergia", "detalle": "Maní"}
            ]
        }
    }
    """
    try:
        data = json.loads(request.body)
        codigo_tarjeta = data.get('codigo_tarjeta', '').strip()
        
        if not codigo_tarjeta:
            return JsonResponse({
                'success': False,
                'error': 'Debe ingresar un código de tarjeta'
            }, status=400)
        
        # Buscar tarjeta activa
        tarjeta = Tarjeta.objects.filter(
            nro_tarjeta=codigo_tarjeta,
            estado='Activa'
        ).select_related('id_hijo', 'id_hijo__id_cliente').first()
        
        if not tarjeta:
            return JsonResponse({
                'success': True,
                'tarjeta_valida': False,
                'mensaje': 'Tarjeta no encontrada o inactiva'
            })
        
        # Obtener restricciones del hijo
        restricciones = RestriccionesHijos.objects.filter(
            id_hijo=tarjeta.id_hijo,
            activo=True
        ).values('tipo_restriccion', 'descripcion', 'severidad')
        
        return JsonResponse({
            'success': True,
            'tarjeta_valida': True,
            'estudiante': {
                'id_hijo': tarjeta.id_hijo.id_hijo,
                'nombre_completo': f"{tarjeta.id_hijo.nombre} {tarjeta.id_hijo.apellido}",
                'saldo_actual': int(tarjeta.saldo_actual),
                'cliente': tarjeta.id_hijo.id_cliente.nombre_completo,
                'restricciones': list(restricciones)
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
            
            # Usar función de matching automático
            conflictos = verificar_restricciones_producto(hijo, producto)
            
            for conflicto in conflictos:
                alertas.append({
                    'id_producto': producto.id_producto,
                    'nombre_producto': producto.descripcion,
                    'restriccion': conflicto['restriccion'],
                    'severidad': conflicto['severidad'],
                    'razon': conflicto['razon']
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
def procesar_venta_api(request):
    """
    API: Procesar venta completa con pagos mixtos
    
    POST /pos/general/api/procesar-venta/
    Body: {
        "id_empleado_cajero": 1,
        "id_hijo": 1 (opcional, si es venta con tarjeta estudiante),
        "productos": [
            {"id_producto": 5, "cantidad": 2, "precio_unitario": 8000},
            {"id_producto": 12, "cantidad": 1, "precio_unitario": 15000}
        ],
        "pagos": [
            {"id_medio_pago": 1, "monto": 20000},  // Efectivo
            {"id_medio_pago": 3, "monto": 11000, "nro_tarjeta": "12345678"}  // Tarjeta estudiante
        ],
        "tipo_venta": "CONTADO"
    }
    
    Response: {
        "success": true,
        "id_venta": 1234,
        "nro_factura": 56789,
        "monto_total": 31000,
        "pagos_aplicados": 31000,
        "comisiones_calculadas": 620,
        "mensaje": "Venta procesada exitosamente"
    }
    """
    try:
        data = json.loads(request.body)
        
        # Validaciones básicas
        id_empleado = data.get('id_empleado_cajero')
        productos = data.get('productos', [])
        pagos = data.get('pagos', [])
        tipo_venta = data.get('tipo_venta', 'CONTADO')
        id_hijo = data.get('id_hijo')
        
        if not id_empleado or not productos or not pagos:
            return JsonResponse({
                'success': False,
                'error': 'Datos incompletos: empleado, productos y pagos son requeridos'
            }, status=400)
        
        # Obtener empleado cajero
        empleado = Empleado.objects.filter(id_empleado=id_empleado).first()
        if not empleado:
            return JsonResponse({
                'success': False,
                'error': 'Empleado no encontrado'
            }, status=404)
        
        # Obtener tipo de pago (usar primer medio de pago como referencia)
        tipo_pago = TiposPago.objects.filter(nombre_tipo='CONTADO').first()
        if not tipo_pago:
            return JsonResponse({
                'success': False,
                'error': 'Tipo de pago CONTADO no configurado'
            }, status=500)
        
        # Calcular monto total
        monto_total = 0
        detalles_venta = []
        
        for item in productos:
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
                    'error': f'Producto {id_producto} no encontrado o inactivo'
                }, status=404)
            
            # Validar stock
            stock_actual = producto.stock.stock_actual if hasattr(producto, 'stock') else 0
            
            if not producto.permite_stock_negativo and stock_actual < cantidad:
                return JsonResponse({
                    'success': False,
                    'error': f'Stock insuficiente para {producto.descripcion}. Disponible: {stock_actual}'
                }, status=400)
            
            subtotal = precio_unitario * int(cantidad)
            monto_total += subtotal
            
            detalles_venta.append({
                'producto': producto,
                'cantidad': cantidad,
                'precio_unitario': precio_unitario,
                'subtotal': subtotal
            })
        
        # Validar que el total de pagos coincida con monto total
        total_pagos = sum(p.get('monto', 0) for p in pagos)
        
        if total_pagos != monto_total:
            return JsonResponse({
                'success': False,
                'error': f'Total de pagos ({total_pagos}) no coincide con total de venta ({monto_total})'
            }, status=400)
        
        # Obtener hijo/cliente si aplica
        hijo = None
        cliente = None
        
        if id_hijo:
            hijo = Hijo.objects.select_related('id_cliente').filter(id_hijo=id_hijo).first()
            if hijo:
                cliente = hijo.id_cliente
        
        # Si no hay hijo, buscar cliente genérico "Público"
        if not cliente:
            cliente = Cliente.objects.filter(
                nombre_completo__icontains='público'
            ).first()
            
            if not cliente:
                # Crear cliente genérico si no existe
                tipo_cliente = TipoCliente.objects.first()
                lista_precio = ListaPrecio.objects.filter(activo=True).first()
                
                cliente = Cliente.objects.create(
                    id_tipo_cliente=tipo_cliente,
                    id_lista_precio=lista_precio,
                    nombre_completo='CLIENTE PÚBLICO',
                    ci_ruc='00000000',
                    activo=True
                )
        
        # Crear venta
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
            genera_factura_legal=False
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
        
        # Procesar pagos y calcular comisiones
        total_comisiones = 0
        
        for pago_data in pagos:
            id_medio_pago = pago_data.get('id_medio_pago')
            monto_pago = pago_data.get('monto')
            nro_tarjeta = pago_data.get('nro_tarjeta')
            
            medio_pago = MediosPago.objects.filter(id_medio_pago=id_medio_pago).first()
            
            if not medio_pago:
                raise Exception(f'Medio de pago {id_medio_pago} no encontrado')
            
            # Obtener tarjeta si aplica
            tarjeta = None
            if nro_tarjeta:
                tarjeta = Tarjeta.objects.filter(nro_tarjeta=nro_tarjeta).first()
                
                if tarjeta:
                    # Descontar saldo de tarjeta
                    tarjeta.saldo_actual -= monto_pago
                    tarjeta.save()
            
            # Crear pago
            pago_venta = PagosVenta.objects.create(
                id_venta=venta,
                id_medio_pago=medio_pago,
                nro_tarjeta_usada=tarjeta,
                monto_aplicado=monto_pago,
                fecha_pago=timezone.now(),
                estado='CONFIRMADO'
            )
            
            # Calcular comisión si aplica
            if medio_pago.genera_comision:
                tarifa_vigente = TarifasComision.objects.filter(
                    id_medio_pago=medio_pago,
                    activo=True,
                    fecha_inicio_vigencia__lte=timezone.now()
                ).filter(
                    Q(fecha_fin_vigencia__isnull=True) | Q(fecha_fin_vigencia__gte=timezone.now())
                ).order_by('-fecha_inicio_vigencia').first()
                
                if tarifa_vigente:
                    comision = (Decimal(monto_pago) * tarifa_vigente.porcentaje_comision)
                    
                    if tarifa_vigente.monto_fijo_comision:
                        comision += tarifa_vigente.monto_fijo_comision
                    
                    total_comisiones += int(comision)
                    
                    # Registrar comisión
                    DetalleComisionVenta.objects.create(
                        id_pago_venta=pago_venta,
                        id_tarifa=tarifa_vigente,
                        monto_comision=int(comision),
                        fecha_calculo=timezone.now()
                    )
        
        return JsonResponse({
            'success': True,
            'id_venta': venta.id_venta,
            'nro_factura': venta.nro_factura_venta,
            'monto_total': monto_total,
            'pagos_aplicados': total_pagos,
            'comisiones_calculadas': total_comisiones,
            'mensaje': 'Venta procesada exitosamente'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON inválido'
        }, status=400)
    except Exception as e:
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

