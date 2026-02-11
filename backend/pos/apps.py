from django.apps import AppConfig


class PosConfig(AppConfig):
    """Configuración de la app POS"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pos'
    verbose_name = 'Punto de Venta (POS)'
    
    def ready(self):
        """Importar signals cuando la app esté lista"""
        try:
            import pos.signals  # noqa
        except ImportError:
            pass
