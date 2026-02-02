"""
Configuración de Celery para Cantina Tita

Este módulo configura Celery para tareas asíncronas y programadas.

Instalación:
    pip install celery redis

Ejecutar worker:
    celery -A cantina_project worker -l info

Ejecutar beat (scheduler):
    celery -A cantina_project beat -l info

En producción (Linux):
    celery -A cantina_project worker -l info --detach
    celery -A cantina_project beat -l info --detach

Autor: CantiTita
Fecha: 2026-01-12
"""

import os
from celery import Celery
from celery.schedules import crontab

# Configurar Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')

# Crear instancia de Celery
app = Celery('cantina_project')

# Configuración desde settings.py con namespace CELERY
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-descubrir tareas en todas las apps
app.autodiscover_tasks()

# Configuración de tareas programadas (Celery Beat)
app.conf.beat_schedule = {
    # Recordatorios de deuda - Diario a las 08:00
    'recordatorios-deuda-diario': {
        'task': 'recordatorios_deuda_saldo_negativo',
        'schedule': crontab(hour=8, minute=0),
        'options': {'expires': 3600}  # Expira en 1 hora
    },
    
    # Verificar saldos bajos - Diario a las 20:00
    'verificar-saldos-bajos-diario': {
        'task': 'verificar_saldos_bajos_diario',
        'schedule': crontab(hour=20, minute=0),
        'options': {'expires': 3600}
    },
    
    # Reporte diario a gerencia - Diario a las 21:00
    'reporte-diario-gerencia': {
        'task': 'generar_reporte_diario_gerencia',
        'schedule': crontab(hour=21, minute=0),
        'options': {'expires': 3600}
    },
    
    # Limpieza de notificaciones antiguas - Semanal (Domingos 02:00)
    'limpieza-notificaciones-semanal': {
        'task': 'limpieza_notificaciones_antiguas',
        'schedule': crontab(day_of_week=0, hour=2, minute=0),
        'options': {'expires': 7200}
    },
}

# Configuración adicional
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='America/Asuncion',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutos
    task_soft_time_limit=25 * 60,  # 25 minutos
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)


@app.task(bind=True)
def debug_task(self):
    """Tarea de debug para probar Celery"""
    print(f'Request: {self.request!r}')
