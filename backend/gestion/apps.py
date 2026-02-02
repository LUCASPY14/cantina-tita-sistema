from django.apps import AppConfig


class GestionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gestion'

    def ready(self):
        """
        Importa signals cuando la app está lista
        Esto conecta automáticamente todos los signals de cache
        """
        import gestion.signals  # noqa
