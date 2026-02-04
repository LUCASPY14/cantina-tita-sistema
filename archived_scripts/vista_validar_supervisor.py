# Esta vista se debe agregar al final de pos_views.py

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def validar_supervisor(request):
    """
    Validar que una tarjeta corresponde a un supervisor para autorizar ventas a crédito.
    
    POST params:
        - nro_tarjeta: Número de tarjeta del supervisor
    
    Returns:
        - success: bool
        - nombre: Nombre completo del supervisor
        - id_empleado: ID del empleado supervisor
        - error: Mensaje de error si falla
    """
    try:
        data = json.loads(request.body)
        nro_tarjeta = data.get('nro_tarjeta', '').strip()
        
        if not nro_tarjeta:
            return JsonResponse({
                'success': False,
                'error': 'Debe escanear una tarjeta'
            })
        
        # Buscar tarjeta de supervisor
        try:
            tarjeta = Tarjeta.objects.select_related(
                'id_hijo',
                'id_hijo__id_cliente_responsable'
            ).get(
                nro_tarjeta=nro_tarjeta,
                tipo_autorizacion='SUPERVISOR',
                estado='ACTIVA'
            )
            
            # Obtener el empleado asociado a esta tarjeta de supervisor
            # La tarjeta de supervisor puede estar asociada a un hijo cuyo responsable es el empleado
            # O podemos buscar al empleado por otro criterio
            
            # Buscar empleado por el cliente responsable de la tarjeta
            if tarjeta.id_hijo and tarjeta.id_hijo.id_cliente_responsable:
                cliente = tarjeta.id_hijo.id_cliente_responsable
                
                # Buscar empleado que coincida con el RUC/CI del cliente
                try:
                    empleado = Empleado.objects.get(
                        ci=cliente.ruc_ci,
                        activo=True
                    )
                    
                    # Verificar que el empleado tenga rol de supervisor
                    if empleado.id_rol.nombre_rol not in ['SUPERVISOR', 'ADMINISTRADOR', 'GERENTE']:
                        return JsonResponse({
                            'success': False,
                            'error': 'Esta tarjeta no pertenece a un supervisor autorizado'
                        })
                    
                    return JsonResponse({
                        'success': True,
                        'nombre': f'{empleado.nombre} {empleado.apellido}',
                        'id_empleado': empleado.id_empleado,
                        'rol': empleado.id_rol.nombre_rol
                    })
                    
                except Empleado.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'error': 'No se encontró empleado asociado a esta tarjeta de supervisor'
                    })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Tarjeta de supervisor no tiene datos asociados'
                })
                
        except Tarjeta.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Tarjeta no encontrada o no es una tarjeta de supervisor activa'
            })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Datos inválidos'
        }, status=400)
    except Exception as e:
        print(f"❌ ERROR al validar supervisor: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': f'Error al validar supervisor: {str(e)}'
        }, status=500)
