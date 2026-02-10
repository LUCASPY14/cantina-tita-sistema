"""
URLs para el sistema de notificaciones
"""
from django.urls import path
from . import views_notificaciones

app_name = 'notificaciones'

urlpatterns = [
    # API endpoints
    path('api/', views_notificaciones.notificaciones_api, name='api'),
    path('marcar-leida/<int:notificacion_id>/', views_notificaciones.marcar_como_leida, name='marcar_leida'),
    path('marcar-todas-leidas/', views_notificaciones.marcar_todas_leidas, name='marcar_todas_leidas'),
    path('eliminar/<int:notificacion_id>/', views_notificaciones.eliminar_notificacion, name='eliminar'),
    
    # HTMX endpoints
    path('badge/', views_notificaciones.notificaciones_badge, name='badge'),
    path('dropdown/', views_notificaciones.notificaciones_dropdown, name='dropdown'),
    
    # Views
    path('panel/', views_notificaciones.panel_notificaciones, name='panel'),
    path('configuracion/', views_notificaciones.configuracion_notificaciones, name='configuracion'),
]
