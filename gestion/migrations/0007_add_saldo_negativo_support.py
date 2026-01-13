# Migration: Agregar soporte para saldo negativo y notificaciones
# gestion/migrations/0004_add_saldo_negativo_support.py

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0005_restriccioneshijos_usuarioportal_transacciononline_and_more'),
    ]

    operations = [
        # Agregar campo permite_saldo_negativo a Tarjeta
        migrations.AddField(
            model_name='tarjeta',
            name='permite_saldo_negativo',
            field=models.BooleanField(
                db_column='Permite_Saldo_Negativo',
                default=False,
                help_text='Permite que la tarjeta tenga saldo negativo temporal con autorización'
            ),
        ),
        
        # Agregar campo limite_credito (saldo negativo máximo permitido)
        migrations.AddField(
            model_name='tarjeta',
            name='limite_credito',
            field=models.BigIntegerField(
                db_column='Limite_Credito',
                default=0,
                help_text='Límite de saldo negativo permitido (ej: 50000 = puede deber hasta ₲50,000)'
            ),
        ),
        
        # Agregar campo notificar_saldo_bajo
        migrations.AddField(
            model_name='tarjeta',
            name='notificar_saldo_bajo',
            field=models.BooleanField(
                db_column='Notificar_Saldo_Bajo',
                default=True,
                help_text='Enviar notificación cuando saldo < saldo_alerta'
            ),
        ),
        
        # Agregar campo ultima_notificacion_saldo
        migrations.AddField(
            model_name='tarjeta',
            name='ultima_notificacion_saldo',
            field=models.DateTimeField(
                db_column='Ultima_Notificacion_Saldo',
                blank=True,
                null=True,
                help_text='Fecha de la última notificación de saldo bajo'
            ),
        ),
        
        # Crear tabla de autorizaciones de saldo negativo
        migrations.CreateModel(
            name='AutorizacionSaldoNegativo',
            fields=[
                ('id_autorizacion', models.AutoField(db_column='ID_Autorizacion', primary_key=True)),
                ('id_venta', models.ForeignKey(
                    on_delete=models.CASCADE,
                    db_column='ID_Venta',
                    to='gestion.ventas',
                    related_name='autorizaciones_saldo_negativo'
                )),
                ('nro_tarjeta', models.ForeignKey(
                    on_delete=models.CASCADE,
                    db_column='Nro_Tarjeta',
                    to='gestion.tarjeta',
                    related_name='autorizaciones_negativas'
                )),
                ('id_empleado_autoriza', models.ForeignKey(
                    on_delete=models.PROTECT,
                    db_column='ID_Empleado_Autoriza',
                    to='gestion.empleado',
                    related_name='autorizaciones_saldo_negativo'
                )),
                ('saldo_anterior', models.BigIntegerField(db_column='Saldo_Anterior')),
                ('monto_venta', models.BigIntegerField(db_column='Monto_Venta')),
                ('saldo_resultante', models.BigIntegerField(
                    db_column='Saldo_Resultante',
                    help_text='Saldo después de la venta (negativo)'
                )),
                ('motivo', models.CharField(
                    db_column='Motivo',
                    max_length=255,
                    help_text='Razón por la cual se autoriza el saldo negativo'
                )),
                ('fecha_autorizacion', models.DateTimeField(
                    db_column='Fecha_Autorizacion',
                    auto_now_add=True
                )),
                ('fecha_regularizacion', models.DateTimeField(
                    db_column='Fecha_Regularizacion',
                    blank=True,
                    null=True,
                    help_text='Fecha cuando se regularizó el saldo (recarga)'
                )),
                ('id_carga_regularizacion', models.ForeignKey(
                    on_delete=models.SET_NULL,
                    db_column='ID_Carga_Regularizacion',
                    to='gestion.cargassaldo',
                    blank=True,
                    null=True,
                    related_name='regularizaciones_saldo'
                )),
                ('regularizado', models.BooleanField(
                    db_column='Regularizado',
                    default=False
                )),
            ],
            options={
                'db_table': 'autorizaciones_saldo_negativo',
                'verbose_name': 'Autorización Saldo Negativo',
                'verbose_name_plural': 'Autorizaciones Saldo Negativo',
                'managed': True,
            },
        ),
        
        # Crear tabla de notificaciones de saldo
        migrations.CreateModel(
            name='NotificacionSaldo',
            fields=[
                ('id_notificacion', models.AutoField(db_column='ID_Notificacion', primary_key=True)),
                ('nro_tarjeta', models.ForeignKey(
                    on_delete=models.CASCADE,
                    db_column='Nro_Tarjeta',
                    to='gestion.tarjeta',
                    related_name='notificaciones_saldo'
                )),
                ('tipo_notificacion', models.CharField(
                    db_column='Tipo_Notificacion',
                    max_length=30,
                    choices=[
                        ('SALDO_BAJO', 'Saldo Bajo'),
                        ('SALDO_NEGATIVO', 'Saldo Negativo'),
                        ('SALDO_CRITICO', 'Saldo Crítico'),
                        ('REGULARIZADO', 'Saldo Regularizado'),
                    ]
                )),
                ('saldo_actual', models.BigIntegerField(db_column='Saldo_Actual')),
                ('mensaje', models.TextField(db_column='Mensaje')),
                ('enviada_email', models.BooleanField(
                    db_column='Enviada_Email',
                    default=False
                )),
                ('enviada_sms', models.BooleanField(
                    db_column='Enviada_SMS',
                    default=False
                )),
                ('email_destinatario', models.EmailField(
                    db_column='Email_Destinatario',
                    blank=True,
                    null=True
                )),
                ('fecha_creacion', models.DateTimeField(
                    db_column='Fecha_Creacion',
                    auto_now_add=True
                )),
                ('fecha_envio', models.DateTimeField(
                    db_column='Fecha_Envio',
                    blank=True,
                    null=True
                )),
                ('leida', models.BooleanField(
                    db_column='Leida',
                    default=False
                )),
            ],
            options={
                'db_table': 'notificaciones_saldo',
                'verbose_name': 'Notificación de Saldo',
                'verbose_name_plural': 'Notificaciones de Saldo',
                'managed': True,
                'ordering': ['-fecha_creacion'],
            },
        ),
    ]
