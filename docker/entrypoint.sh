#!/bin/bash
# Entrypoint script para Django container
# Espera a que MySQL esté listo antes de iniciar Django

set -e

echo "🔍 Esperando a que MySQL esté disponible..."

# Esperar a que MySQL esté listo
while ! nc -z db 3306; do
  echo "⏳ MySQL no está listo - esperando..."
  sleep 2
done

echo "✅ MySQL está listo!"

# Ejecutar migraciones (opcional, comentar si usas managed=False)
# echo "🔄 Ejecutando migraciones..."
# python manage.py migrate --noinput

# Recolectar archivos estáticos
echo "📦 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput --clear

# Crear superusuario si no existe (opcional)
# python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@cantina.com', 'admin')"

echo "🚀 Iniciando Django..."

# Ejecutar el comando pasado como argumentos
exec "$@"
