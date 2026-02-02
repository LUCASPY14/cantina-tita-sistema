from django.core.cache import cache
from django.shortcuts import redirect
from django.urls import reverse
from .models import Empleado  # Aquí puedes relacionar con Caja

class CajaSeguraMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Solo verificamos en rutas del POS y si el usuario está logueado
        if request.user.is_authenticated and request.path.startswith('/api/pos/'):
            cache_key = f"caja_abierta_{request.user.username}"
            esta_abierta = cache.get(cache_key)

            if esta_abierta is None:
                # Aquí debes poner tu lógica real de consulta a la DB
                # Ejemplo: esta_abierta = Caja.objects.filter(vendedor__usuario=request.user.username, estado='ABIERTA').exists()
                # Por ahora simulamos True para no bloquearte:
                esta_abierta = True
                cache.set(cache_key, esta_abierta, 3600)  # Guardamos 1 hora en Redis

            if not esta_abierta:
                # Si es API, devolvemos error 403. Si es Web, redireccionamos.
                if request.path.startswith('/api/'):
                    from django.http import JsonResponse
                    return JsonResponse({'error': 'Debe abrir caja para operar'}, status=403)
                return redirect('apertura-caja')

        return self.get_response(request)
