# Migración de Notificaciones
# Generated manually for notifications system

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('gestion', '0001_initial'),  # Ajustar según última migración
    ]

    operations = [
        migrations.CreateModel(
            name='Notificacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(help_text='Título corto de la notificación', max_length=200)),
                ('mensaje', models.TextField(help_text='Mensaje completo de la notificación')),
                ('tipo', models.CharField(
                    choices=[
                        ('info', 'Información'),
                        ('success', 'Éxito'),
                        ('warning', 'Advertencia'),
                        ('error', 'Error'),
                        ('venta', 'Venta'),
                        ('recarga', 'Recarga'),
                        ('stock', 'Stock Bajo'),
                        ('sistema', 'Sistema'),
                    ],
                    default='info',
                    help_text='Tipo de notificación',
                    max_length=20
                )),
                ('prioridad', models.CharField(
                    choices=[
                        ('baja', 'Baja'),
                        ('media', 'Media'),
                        ('alta', 'Alta'),
                        ('critica', 'Crítica'),
                    ],
                    default='media',
                    help_text='Prioridad de la notificación',
                    max_length=20
                )),
                ('icono', models.CharField(blank=True, help_text='Clase de ícono FontAwesome (ej: fa-bell)', max_length=50, null=True)),
                ('url', models.CharField(blank=True, help_text='URL de acción al hacer clic', max_length=500, null=True)),
                ('leida', models.BooleanField(default=False, help_text='¿La notificación ha sido leída?')),
                ('fecha_leida', models.DateTimeField(blank=True, help_text='Fecha y hora en que se leyó', null=True)),
                ('creada_en', models.DateTimeField(auto_now_add=True, help_text='Fecha de creación')),
                ('expira_en', models.DateTimeField(blank=True, help_text='Fecha de expiración (opcional)', null=True)),
                ('usuario', models.ForeignKey(
                    help_text='Usuario que recibe la notificación',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='notificaciones',
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'verbose_name': 'Notificación',
                'verbose_name_plural': 'Notificaciones',
                'ordering': ['-creada_en'],
            },
        ),
        migrations.CreateModel(
            name='ConfiguracionNotificaciones',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notif_ventas', models.BooleanField(default=True, verbose_name='Notificaciones de Ventas')),
                ('notif_recargas', models.BooleanField(default=True, verbose_name='Notificaciones de Recargas')),
                ('notif_stock', models.BooleanField(default=True, verbose_name='Notificaciones de Stock Bajo')),
                ('notif_sistema', models.BooleanField(default=True, verbose_name='Notificaciones del Sistema')),
                ('push_habilitado', models.BooleanField(default=False, verbose_name='Push Notifications Habilitadas')),
                ('push_subscription', models.JSONField(
                    blank=True,
                    help_text='Datos de suscripción del navegador',
                    null=True,
                    verbose_name='Subscription de Push'
                )),
                ('solo_criticas', models.BooleanField(
                    default=False,
                    help_text='Recibir solo notificaciones de prioridad alta/crítica',
                    verbose_name='Solo Notificaciones Críticas'
                )),
                ('sonido_habilitado', models.BooleanField(default=True, verbose_name='Sonido de Notificaciones')),
                ('usuario', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='config_notificaciones',
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'verbose_name': 'Configuración de Notificaciones',
                'verbose_name_plural': 'Configuraciones de Notificaciones',
            },
        ),
        migrations.AddIndex(
            model_name='notificacion',
            index=models.Index(fields=['usuario', '-creada_en'], name='gestion_not_usuario_idx'),
        ),
        migrations.AddIndex(
            model_name='notificacion',
            index=models.Index(fields=['usuario', 'leida'], name='gestion_not_leida_idx'),
        ),
        migrations.AddIndex(
            model_name='notificacion',
            index=models.Index(fields=['tipo', '-creada_en'], name='gestion_not_tipo_idx'),
        ),
    ]
