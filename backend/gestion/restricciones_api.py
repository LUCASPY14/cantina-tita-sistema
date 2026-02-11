"""
API Views para sistema de matching automático de restricciones alimentarias
"""

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
import json

from gestion.models import Tarjeta, Producto
from gestion.restricciones_matcher import ProductoRestriccionMatcher, verificar_restricciones_venta


@login_required
@require_http_methods(["POST"])
def verificar_restricciones_api(request):
    """
    API para verificar restricciones alimentarias en tiempo real
    
    POST /api/verificar-restricciones/
    Body: {
        "tarjeta_codigo": "123456",
        "items": [
            {"producto_id": 1, "cantidad": 2},
            {"producto_id": 5, "cantidad": 1}
        ]
    }
    
    Response: {
        "success": true,
        "tiene_alertas": false,
        "puede_continuar": true,
        "requiere_autorizacion": false,
        "alertas": [...]
    }
    """
    try:
        data = json.loads(request.body)
        tarjeta_codigo = data.get('tarjeta_codigo')
        items = data.get('items', [])
        
        if not tarjeta_codigo:
            return JsonResponse({
                'success': False,
                'error': 'Código de tarjeta requerido'
            }, status=400)
        
        # Buscar tarjeta
        try:
            tarjeta = Tarjeta.objects.select_related('id_hijo').get(
                nro_tarjeta=tarjeta_codigo,
                estado='Activa'
            )
        except Tarjeta.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Tarjeta no encontrada o inactiva'
            }, status=404)
        
        # Verificar restricciones
        resultado = verificar_restricciones_venta(tarjeta, items)
        
        # Formatear alertas para JSON
        alertas_json = []
        for alerta in resultado.get('alertas', []):
            alertas_json.append({
                'producto_id': alerta['producto'].id_producto,
                'producto_nombre': alerta['producto'].descripcion,
                'restriccion_tipo': alerta['restriccion'].tipo_restriccion,
                'razon': alerta['razon'],
                'nivel_confianza': alerta['nivel_confianza'],
                'severidad': alerta['severidad']
            })
        
        return JsonResponse({
            'success': True,
            'tiene_alertas': resultado['tiene_alertas'],
            'puede_continuar': resultado['puede_continuar'],
            'requiere_autorizacion': resultado['requiere_autorizacion'],
            'alertas': alertas_json,
            'estudiante': {
                'nombre': f"{tarjeta.id_hijo.nombre} {tarjeta.id_hijo.apellido}" if tarjeta.id_hijo else "N/A",
                'grado': tarjeta.id_hijo.grado if tarjeta.id_hijo and hasattr(tarjeta.id_hijo, 'grado') else "N/A"
            }
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def obtener_productos_seguros_api(request, tarjeta_codigo):
    """
    API para obtener productos seguros para un estudiante
    
    GET /api/productos-seguros/{tarjeta_codigo}/
    Query params:
        - categoria_id: Filtrar por categoría (opcional)
    
    Response: {
        "success": true,
        "productos": [...]
    }
    """
    try:
        # Buscar tarjeta
        try:
            tarjeta = Tarjeta.objects.select_related('id_hijo').get(
                nro_tarjeta=tarjeta_codigo,
                estado='Activa'
            )
        except Tarjeta.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Tarjeta no encontrada'
            }, status=404)
        
        if not tarjeta.id_hijo:
            return JsonResponse({
                'success': False,
                'error': 'Tarjeta sin hijo asociado'
            }, status=400)
        
        # Obtener restricciones
        from gestion.models import RestriccionesHijos
        restricciones = RestriccionesHijos.objects.filter(
            id_hijo=tarjeta.id_hijo,
            activo=True
        )
        
        if not restricciones.exists():
            # Sin restricciones, retornar todos los productos
            productos = Producto.objects.filter(activo=True)[:50]
        else:
            # Filtrar productos seguros
            productos_todos = Producto.objects.filter(activo=True)
            productos_seguros = []
            
            for producto in productos_todos:
                es_seguro = True
                for restriccion in restricciones:
                    tiene_conflicto, _, _ = ProductoRestriccionMatcher.analizar_producto(
                        producto, restriccion
                    )
                    if tiene_conflicto:
                        es_seguro = False
                        break
                
                if es_seguro:
                    productos_seguros.append(producto)
            
            productos = productos_seguros[:50]
        
        # Formatear productos
        productos_json = []
        from gestion.models import ListaPrecios, PreciosPorLista
        lista_precios = ListaPrecios.objects.filter(activo=True).first()
        
        for producto in productos:
            precio = 0
            if lista_precios:
                try:
                    precio_obj = PreciosPorLista.objects.get(
                        id_producto=producto,
                        id_lista=lista_precios
                    )
                    precio = float(precio_obj.precio_unitario_neto)
                except PreciosPorLista.DoesNotExist:
                    pass
            
            productos_json.append({
                'id': producto.id_producto,
                'codigo': producto.codigo_barra or '',
                'descripcion': producto.descripcion,
                'categoria': producto.id_categoria.nombre if hasattr(producto, 'id_categoria') and producto.id_categoria else 'Sin categoría',
                'precio': precio
            })
        
        return JsonResponse({
            'success': True,
            'total': len(productos_json),
            'productos': productos_json
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def sugerir_alternativas_api(request):
    """
    API para sugerir productos alternativos seguros
    
    POST /api/sugerir-alternativas/
    Body: {
        "tarjeta_codigo": "123456",
        "producto_id": 5
    }
    
    Response: {
        "success": true,
        "alternativas": [...]
    }
    """
    try:
        data = json.loads(request.body)
        tarjeta_codigo = data.get('tarjeta_codigo')
        producto_id = data.get('producto_id')
        
        # Buscar tarjeta y producto
        tarjeta = Tarjeta.objects.select_related('id_hijo').get(
            nro_tarjeta=tarjeta_codigo,
            estado='Activa'
        )
        producto = Producto.objects.get(id_producto=producto_id)
        
        # Obtener restricciones
        from gestion.models import RestriccionesHijos
        restricciones = RestriccionesHijos.objects.filter(
            id_hijo=tarjeta.id_hijo,
            activo=True
        )
        
        # Sugerir alternativas para cada restricción
        alternativas = []
        for restriccion in restricciones:
            sugerencias = ProductoRestriccionMatcher.sugerir_alternativas(
                producto, restriccion, max_resultados=5
            )
            
            for sugerencia in sugerencias:
                if sugerencia not in alternativas:
                    alternativas.append(sugerencia)
        
        # Formatear alternativas
        from gestion.models import ListaPrecios, PreciosPorLista
        lista_precios = ListaPrecios.objects.filter(activo=True).first()
        
        alternativas_json = []
        for alt in alternativas[:10]:  # Máximo 10 sugerencias
            precio = 0
            if lista_precios:
                try:
                    precio_obj = PreciosPorLista.objects.get(
                        id_producto=alt,
                        id_lista=lista_precios
                    )
                    precio = float(precio_obj.precio_unitario_neto)
                except PreciosPorLista.DoesNotExist:
                    pass
            
            alternativas_json.append({
                'id': alt.id_producto,
                'codigo': alt.codigo_barra or '',
                'descripcion': alt.descripcion,
                'categoria': alt.id_categoria.nombre if hasattr(alt, 'id_categoria') and alt.id_categoria else 'Sin categoría',
                'precio': precio
            })
        
        return JsonResponse({
            'success': True,
            'total': len(alternativas_json),
            'producto_original': producto.descripcion,
            'alternativas': alternativas_json
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
