"""
URLs para el portal de clientes
"""
from django.urls import path
from gestion import cliente_views

app_name = 'clientes'

urlpatterns = [
    # Autenticación del portal
    path('login/', cliente_views.portal_login_view, name='portal_login'),
    path('logout/', cliente_views.portal_logout_view, name='portal_logout'),

    # Dashboard del portal
    path('', cliente_views.portal_dashboard_view, name='portal_dashboard'),

    # Gestión de hijos
    path('hijo/<int:hijo_id>/consumos/', cliente_views.portal_consumos_hijo_view, name='portal_consumos_hijo'),
    path('hijo/<int:hijo_id>/restricciones/', cliente_views.portal_restricciones_hijo_view, name='portal_restricciones_hijo'),

    # Recargas y pagos
    path('recargas/', cliente_views.portal_recargas_view, name='portal_recargas'),
    path('cargar-saldo/', cliente_views.portal_cargar_saldo_view, name='portal_cargar_saldo'),
    path('pagos/', cliente_views.portal_pagos_view, name='portal_pagos'),

    # Resultados de pagos
    path('pago-exitoso/', cliente_views.portal_pago_exitoso_view, name='portal_pago_exitoso'),
    path('pago-cancelado/', cliente_views.portal_pago_cancelado_view, name='portal_pago_cancelado'),

    # Seguridad
    path('cambiar-password/', cliente_views.portal_cambiar_password_view, name='portal_cambiar_password'),
    path('recuperar-password/', cliente_views.portal_recuperar_password_view, name='portal_recuperar_password'),
    path('reset-password/<str:token>/', cliente_views.portal_reset_password_view, name='portal_reset_password'),
    path('configurar-2fa/', cliente_views.configurar_2fa_view, name='configurar_2fa'),

    # Webhooks
    path('webhook/', cliente_views.metrepay_webhook_view, name='metrepay_webhook'),
]