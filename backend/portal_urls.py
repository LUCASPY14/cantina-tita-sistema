"""
URLs para el portal de clientes/padres de familia
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from gestion import views_basicas as views

app_name = 'portal'

urlpatterns = [
    # Ruta raíz del portal - redirige al dashboard
    path('', views.portal_dashboard, name='portal_home'),
    
    # Autenticación
    path('login/', views.portal_login, name='portal_login'),
    path('logout/', views.portal_logout, name='portal_logout'),
    path('registro/', views.portal_registro, name='registro'),
    path('dashboard/', views.portal_dashboard, name='portal_dashboard'),
    
    # Password Reset para portal
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='portal/auth/password_reset.html',
             email_template_name='portal/auth/password_reset_email.html',
             subject_template_name='portal/auth/password_reset_subject.txt',
         ), 
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='portal/auth/password_reset_done.html'
         ), 
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='portal/auth/password_reset_confirm.html'
         ), 
         name='password_reset_confirm'),
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='portal/auth/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
    
    # 2FA
    path('verificar-2fa/', views.portal_verificar_2fa, name='portal_verificar_2fa'),
    path('activar-2fa/', views.portal_activar_2fa, name='portal_activar_2fa'),
    path('deshabilitar-2fa/', views.portal_deshabilitar_2fa, name='portal_deshabilitar_2fa'),
    
    # Recuperación de password
    path('restablecer-password/', views.portal_restablecer_password, name='portal_restablecer_password'),
    path('revocar-terminos/', views.portal_revocar_terminos, name='portal_revocar_terminos'),
    
    # Hijos
    path('mis-hijos/', views.portal_mis_hijos, name='portal_mis_hijos'),
    path('consumos-hijo/<int:hijo_id>/', views.portal_consumos_hijo, name='portal_consumos_hijo'),
    path('restricciones-hijo/<int:hijo_id>/', views.portal_restricciones_hijo, name='portal_restricciones_hijo'),
    
    # Pagos y recargas
    path('cargar-saldo/', views.portal_cargar_saldo, name='portal_cargar_saldo'),
    path('pagos/', views.portal_pagos, name='portal_pagos'),
    path('recargas/', views.portal_recargas, name='portal_recargas'),
    path('recargar-tarjeta/', views.portal_recargar_tarjeta, name='portal_recargar_tarjeta'),
    
    # Notificaciones
    path('notificaciones-saldo/', views.portal_notificaciones_saldo, name='portal_notificaciones_saldo'),
    
    # APIs
    path('api/movimientos/<int:tarjeta_id>/', views.api_portal_movimientos, name='api_portal_movimientos'),
    path('api/saldo/<int:tarjeta_id>/', views.api_portal_saldo, name='api_portal_saldo'),
]
