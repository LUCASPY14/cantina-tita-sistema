# Migración manual para registrar tabla creada directamente en MySQL
# Evita conflictos con modelos legacy

from django.db import migrations


class Migration(migrations.Migration):
    """
    Esta migración NO crea la tabla, solo la registra en el historial.
    La tabla debe crearse manualmente ejecutando: crear_tabla_aceptacion_terminos.sql
    """

    dependencies = [
        ('gestion', '0007_add_saldo_negativo_support'),
    ]

    operations = [
        # RunSQL con noop (no operation) para registrar sin ejecutar nada
        migrations.RunSQL(
            sql=migrations.RunSQL.noop,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
