"""
API de Sugerencias Inteligentes para POS
=========================================

Proporciona recomendaciones de productos seguros basadas en:
- Restricciones alimentarias del estudiante
- Historial de compras
- Stock disponible
- Preferencias de precio
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json

from .models import Producto, Hijo, RestriccionesHijos
from .restricciones_matcher import ProductoRestriccionMatcher
from .pos_utils import VerificadorRestricciones


@require_http_methods(["POST"])
def sugerir_productos_seguros(request):
    """
    API: Obtener productos recomendados seguros para un estudiante
    
    POST /pos/general/api/sugerir-productos-seguros/
    Body: {
        "id_hijo": 1,
        "limite": 10,
        "solo_stock": true
    }
    
    Response: {
        "success": true,
        "productos": [
            {
                "id": 1,
                "descripcion": "Coca Cola 500ml",
                "precio_venta": 8000,
                "stock_actual": 45,
                "razon_recomendacion": "Sin restricciones detectadas"
            }
        ]
    }
    """
    try:
        data = json.loads(request.body)
        id_hijo = data.get('id_hijo')
        limite = int(data.get('limite', 10))
        solo_stock = data.get('solo_stock', True)
        
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
        
        # Obtener restricciones
        restricciones = RestriccionesHijos.objects.filter(
            id_hijo=hijo,
            activo=True
        )
        
        productos_recomendados = []
        
        # Base de productos a considerar
        query = Producto.objects.filter(activo=True)
        
        if solo_stock:
            query = query.select_related('stock').filter(stock__stock_actual__gt=0)
        
        for producto in query[:100]:
            es_seguro = True
            razon = "Sin restricciones detectadas"
            
            # Verificar cada restricción
            for restriccion in restricciones:
                tiene_conflicto, razon_conflicto, confianza = \
                    ProductoRestriccionMatcher.analizar_producto(
                        producto, restriccion
                    )
                
                if tiene_conflicto:
                    es_seguro = False
                    razon = f"⚠️ {restriccion.tipo_restriccion}: {razon_conflicto}"
                    break
            
            if es_seguro:
                stock_actual = producto.stock.stock_actual if hasattr(producto, 'stock') else 0
                
                # Obtener precio de venta
                precio_producto = producto.precios.filter(
                    id_lista_precio__activo=True
                ).order_by('-id_lista_precio__fecha_vigencia').first()
                
                precio_venta = precio_producto.precio_venta if precio_producto else 0
                
                productos_recomendados.append({
                    'id': producto.id_producto,
                    'descripcion': producto.descripcion,
                    'precio_venta': int(precio_venta),
                    'stock_actual': float(stock_actual),
                    'razon_recomendacion': razon
                })
                
                if len(productos_recomendados) >= limite:
                    break
        
        return JsonResponse({
            'success': True,
            'productos': productos_recomendados,
            'total': len(productos_recomendados),
            'tiene_restricciones': restricciones.exists()
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON inválido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al obtener sugerencias: {str(e)}'
        }, status=500)


@require_http_methods(["POST"])
def obtener_detalles_restriccion(request):
    """
    API: Obtener detalles de una restricción específica
    
    POST /pos/general/api/detalles-restriccion/
    Body: {
        "id_hijo": 1,
        "tipo_restriccion": "Alergia al maní"
    }
    
    Response: {
        "success": true,
        "restriccion": {
            "tipo": "Alergia al maní",
            "descripcion": "Evitar productos con maní y trazas",
            "palabras_clave": ["mani", "peanut", "groundnut"],
            "productos_con_alerta": 5
        }
    }
    """
    try:
        data = json.loads(request.body)
        id_hijo = data.get('id_hijo')
        tipo_restriccion = data.get('tipo_restriccion')
        
        if not id_hijo or not tipo_restriccion:
            return JsonResponse({
                'success': False,
                'error': 'Datos incompletos'
            }, status=400)
        
        # Obtener restricción
        restriccion = RestriccionesHijos.objects.filter(
            id_hijo=id_hijo,
            tipo_restriccion=tipo_restriccion,
            activo=True
        ).first()
        
        if not restriccion:
            return JsonResponse({
                'success': False,
                'error': 'Restricción no encontrada'
            }, status=404)
        
        # Contar productos con alerta
        hijo = Hijo.objects.get(id_hijo=id_hijo)
        productos_alerta = 0
        
        for producto in Producto.objects.filter(activo=True)[:50]:
            tiene_conflicto, _, _ = ProductoRestriccionMatcher.analizar_producto(
                producto, restriccion
            )
            if tiene_conflicto:
                productos_alerta += 1
        
        return JsonResponse({
            'success': True,
            'restriccion': {
                'tipo': restriccion.tipo_restriccion,
                'descripcion': restriccion.descripcion,
                'palabras_clave': getattr(restriccion, 'palabras_clave', []),
                'severidad': restriccion.severidad,
                'productos_con_alerta': productos_alerta
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
            'error': f'Error: {str(e)}'
        }, status=500)
