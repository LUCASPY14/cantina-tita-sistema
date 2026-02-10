"""
Señales para generar notificaciones automáticas
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()


@receiver(post_save, sender='pos.Venta')
def notificar_nueva_venta(sender, instance, created, **kwargs):
    """
    Genera notificación cuando se registra una nueva venta
    """
    if created:
        from .models_notificaciones import NotificacionSistema, ConfiguracionNotificacionesSistema
        
        # Notificar a cajeros y administradores
        usuarios = User.objects.filter(
            is_staff=True,
            is_active=True
        )
        
        for usuario in usuarios:
            config = ConfiguracionNotificacionesSistema.get_or_create_for_user(usuario)
            
            # Verificar si tiene habilitadas las notificaciones de ventas
            if not config.notif_ventas:
                continue
            
            # Determinar prioridad según el monto
            if instance.total >= Decimal('500000'):
                prioridad = 'alta'
            elif instance.total >= Decimal('100000'):
                prioridad = 'media'
            else:
                prioridad = 'baja'
            
            # Verificar si solo quiere críticas
            if config.solo_criticas and prioridad not in ['alta', 'critica']:
                continue
            
            NotificacionSistema.crear_notificacion(
                usuario=usuario,
                titulo='Nueva Venta Registrada',
                mensaje=f'Se realizó una venta por ₲ {instance.total:,.0f}',
                tipo='venta',
                prioridad=prioridad,
                icono='fa-cash-register',
                url=f'/pos/ventas/{instance.id}/'
            )


@receiver(post_save, sender='gestion.CargasSaldo')
def notificar_nueva_recarga(sender, instance, created, **kwargs):
    """
    Genera notificación cuando se realiza una recarga
    """
    if created:
        from .models_notificaciones import NotificacionSistema, ConfiguracionNotificacionesSistema
        
        # Notificar al cliente (padre) de la recarga
        if hasattr(instance, 'cliente') and instance.cliente:
            cliente_user = instance.cliente.usuario if hasattr(instance.cliente, 'usuario') else None
            
            if cliente_user:
                config = ConfiguracionNotificacionesSistema.get_or_create_for_user(cliente_user)
                
                if config.notif_recargas:
                    NotificacionSistema.crear_notificacion(
                        usuario=cliente_user,
                        titulo='Recarga Exitosa',
                        mensaje=f'Se acreditaron ₲ {instance.monto:,.0f} a tu cuenta',
                        tipo='recarga',
                        prioridad='media',
                        icono='fa-credit-card',
                        url='/clientes/historial/'
                    )
        
        # Notificar a staff
        usuarios_staff = User.objects.filter(is_staff=True, is_active=True)
        for usuario in usuarios_staff:
            config = ConfiguracionNotificacionesSistema.get_or_create_for_user(usuario)
            
            if config.notif_recargas:
                NotificacionSistema.crear_notificacion(
                    usuario=usuario,
                    titulo='Nueva Recarga',
                    mensaje=f'Recarga de ₲ {instance.monto:,.0f} procesada',
                    tipo='recarga',
                    prioridad='baja',
                    icono='fa-credit-card'
                )


@receiver(pre_save, sender='gestion.Producto')
def notificar_stock_bajo(sender, instance, **kwargs):
    """
    Genera notificación cuando un producto tiene stock bajo
    """
    if instance.pk:  # Solo para productos existentes
        from .models_notificaciones import NotificacionSistema, ConfiguracionNotificacionesSistema
        
        try:
            producto_anterior = sender.objects.get(pk=instance.pk)
            
            # Solo notificar si el stock cambió y está por debajo del mínimo
            if (producto_anterior.stock != instance.stock and 
                instance.stock <= instance.stock_minimo and 
                instance.stock > 0):
                
                # Notificar a administradores
                usuarios = User.objects.filter(
                    is_staff=True,
                    is_active=True
                )
                
                for usuario in usuarios:
                    config = ConfiguracionNotificacionesSistema.get_or_create_for_user(usuario)
                    
                    if not config.notif_stock:
                        continue
                    
                    # Verificar si ya existe una notificación reciente sobre este producto
                    from django.utils import timezone
                    from datetime import timedelta
                    
                    hace_1_hora = timezone.now() - timedelta(hours=1)
                    
                    notif_existente = NotificacionSistema.objects.filter(
                        usuario=usuario,
                        tipo='stock',
                        mensaje__icontains=instance.nombre,
                        creada_en__gte=hace_1_hora
                    ).exists()
                    
                    if not notif_existente:
                        NotificacionSistema.crear_notificacion(
                            usuario=usuario,
                            titulo='⚠️ Stock Bajo',
                            mensaje=f'El producto "{instance.nombre}" tiene solo {instance.stock} unidades disponibles',
                            tipo='stock',
                            prioridad='alta' if instance.stock <= 5 else 'media',
                            icono='fa-exclamation-triangle',
                            url='/gestion/productos/'
                        )
        
        except sender.DoesNotExist:
            pass


@receiver(post_save, sender='gestion.Producto')
def notificar_producto_agotado(sender, instance, **kwargs):
    """
    Genera notificación crítica cuando un producto se agota
    """
    if instance.stock == 0:
        from .models_notificaciones import NotificacionSistema, ConfiguracionNotificacionesSistema
        
        # Notificar a administradores
        usuarios = User.objects.filter(
            is_staff=True,
            is_active=True
        )
        
        for usuario in usuarios:
            config = ConfiguracionNotificacionesSistema.get_or_create_for_user(usuario)
            
            if config.notif_stock:
                # Verificar si no se notificó recientemente
                from django.utils import timezone
                from datetime import timedelta
                
                hace_30_min = timezone.now() - timedelta(minutes=30)
                
                notif_existente = NotificacionSistema.objects.filter(
                    usuario=usuario,
                    tipo='stock',
                    mensaje__icontains=instance.nombre,
                    prioridad='critica',
                    creada_en__gte=hace_30_min
                ).exists()
                
                if not notif_existente:
                    NotificacionSistema.crear_notificacion(
                        usuario=usuario,
                        titulo='🚨 Producto Agotado',
                        mensaje=f'El producto "{instance.nombre}" se ha AGOTADO',
                        tipo='stock',
                        prioridad='critica',
                        icono='fa-times-circle',
                        url='/gestion/productos/'
                    )


def notificar_sistema(titulo, mensaje, usuarios=None, prioridad='media'):
    """
    Función helper para crear notificaciones del sistema
    
    Uso:
        from .signals_notificaciones import notificar_sistema
        notificar_sistema(
            titulo="Backup Completado",
            mensaje="El backup del sistema se completó exitosamente",
            prioridad='baja'
        )
    """
    from .models_notificaciones import NotificacionSistema, ConfiguracionNotificacionesSistema
    
    if usuarios is None:
        # Por defecto, notificar a superusuarios
        usuarios = User.objects.filter(
            is_superuser=True,
            is_active=True
        )
    
    for usuario in usuarios:
        config = ConfiguracionNotificacionesSistema.get_or_create_for_user(usuario)
        
        if config.notif_sistema:
            if config.solo_criticas and prioridad not in ['alta', 'critica']:
                continue
            
            NotificacionSistema.crear_notificacion(
                usuario=usuario,
                titulo=titulo,
                mensaje=mensaje,
                tipo='sistema',
                prioridad=prioridad,
                icono='fa-server'
            )


def notificar_usuarios(usuarios, titulo, mensaje, tipo='info', prioridad='media', **kwargs):
    """
    Función helper para notificar a múltiples usuarios
    
    Uso:
        from .signals_notificaciones import notificar_usuarios
        usuarios = User.objects.filter(is_staff=True)
        notificar_usuarios(
            usuarios=usuarios,
            titulo="Mantenimiento Programado",
            mensaje="El sistema estará en mantenimiento mañana a las 2 AM",
            tipo='warning',
            prioridad='alta'
        )
    """
    from .models_notificaciones import NotificacionSistema
    
    for usuario in usuarios:
        NotificacionSistema.crear_notificacion(
            usuario=usuario,
            titulo=titulo,
            mensaje=mensaje,
            tipo=tipo,
            prioridad=prioridad,
            **kwargs
        )
