"""
URLs para el Portal de Padres (Web)
"""
from django.urls import path
from . import portal_views, portal_api

urlpatterns = [
    # Autenticación
    path('', portal_views.login_view, name='portal_login'),
    path('registro/', portal_views.registro_view, name='portal_registro'),
    path('logout/', portal_views.logout_view, name='portal_logout'),
    path('verificar-email/<str:token>/', portal_views.verificar_email_view, name='portal_verificar_email'),
    path('recuperar-password/', portal_views.recuperar_password_view, name='portal_recuperar_password'),
    path('restablecer-password/<str:token>/', portal_views.restablecer_password_view, name='portal_restablecer_password'),
    
    # Vistas principales
    path('dashboard/', portal_views.dashboard_view, name='portal_dashboard'),
    path('mis-hijos/', portal_views.mis_hijos_view, name='portal_mis_hijos'),
    path('perfil/', portal_views.perfil_view, name='portal_perfil'),
    
    # Recargas
    path('recargar/<str:nro_tarjeta>/', portal_views.recargar_tarjeta_view, name='portal_recargar_tarjeta'),
    path('estado-recarga/<str:referencia>/', portal_views.estado_recarga_view, name='portal_estado_recarga'),
    path('pago-exitoso/', portal_views.pago_exitoso_view, name='portal_pago_exitoso'),
    path('pago-cancelado/', portal_views.pago_cancelado_view, name='portal_pago_cancelado'),
    
    # API REST del Portal (Consultas Móviles)
    path('api/tarjeta/<str:nro_tarjeta>/saldo/', portal_api.api_saldo_tarjeta, name='api_portal_saldo'),
    path('api/tarjeta/<str:nro_tarjeta>/movimientos/', portal_api.api_movimientos_tarjeta, name='api_portal_movimientos'),
]
