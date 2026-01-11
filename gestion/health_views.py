"""
API View para Health Checks del Sistema
Endpoint: /api/health/
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from django.core.cache import cache
from django.conf import settings
import psutil
import time
from datetime import datetime


@api_view(['GET'])
@permission_classes([AllowAny])  # Permitir acceso sin autenticación para monitoring externo
def health_check(request):
    """
    Health check endpoint para monitoring externo
    Retorna estado de componentes críticos del sistema
    """
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'checks': {}
    }
    
    all_healthy = True
    
    # 1. Check Database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        health_status['checks']['database'] = {'status': 'ok', 'message': 'Connected'}
    except Exception as e:
        health_status['checks']['database'] = {'status': 'error', 'message': str(e)}
        all_healthy = False
    
    # 2. Check Cache
    try:
        test_key = 'health_check'
        cache.set(test_key, 'ok', 10)
        if cache.get(test_key) == 'ok':
            health_status['checks']['cache'] = {'status': 'ok', 'message': 'Responding'}
            cache.delete(test_key)
        else:
            health_status['checks']['cache'] = {'status': 'warning', 'message': 'Not responding correctly'}
            all_healthy = False
    except Exception as e:
        health_status['checks']['cache'] = {'status': 'error', 'message': str(e)}
        # Cache no es crítico
    
    # 3. Check Disk
    try:
        disk = psutil.disk_usage(str(settings.BASE_DIR))
        disk_percent = disk.percent
        health_status['checks']['disk'] = {
            'status': 'ok' if disk_percent < 90 else 'warning',
            'usage_percent': disk_percent,
            'free_gb': round(disk.free / (1024**3), 2)
        }
        if disk_percent >= 90:
            all_healthy = False
    except Exception as e:
        health_status['checks']['disk'] = {'status': 'error', 'message': str(e)}
    
    # 4. Check Memory
    try:
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        health_status['checks']['memory'] = {
            'status': 'ok' if memory_percent < 90 else 'warning',
            'usage_percent': memory_percent,
            'available_gb': round(memory.available / (1024**3), 2)
        }
        if memory_percent >= 90:
            all_healthy = False
    except Exception as e:
        health_status['checks']['memory'] = {'status': 'error', 'message': str(e)}
    
    # Determinar status global
    health_status['status'] = 'healthy' if all_healthy else 'degraded'
    
    # Retornar código HTTP apropiado
    http_status = status.HTTP_200_OK if all_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return Response(health_status, status=http_status)


@api_view(['GET'])
@permission_classes([AllowAny])
def readiness_check(request):
    """
    Readiness check - verifica si el sistema puede recibir tráfico
    """
    try:
        # Check crítico: Base de datos
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        
        return Response({
            'status': 'ready',
            'timestamp': datetime.now().isoformat()
        }, status=status.HTTP_200_OK)
    except:
        return Response({
            'status': 'not_ready',
            'timestamp': datetime.now().isoformat()
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['GET'])
@permission_classes([AllowAny])
def liveness_check(request):
    """
    Liveness check - verifica que el proceso esté vivo
    """
    return Response({
        'status': 'alive',
        'timestamp': datetime.now().isoformat()
    }, status=status.HTTP_200_OK)
