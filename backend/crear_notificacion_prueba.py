"""
Crear notificación de prueba
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from gestion.models_notificaciones import NotificacionSistema

User = get_user_model()

print("=" * 80)
print("🔔 CREANDO NOTIFICACIÓN DE PRUEBA")
print("=" * 80)

# Obtener usuario admin
admin_user = User.objects.get(username='admin')
print(f"\n✅ Usuario: {admin_user.username}")

# Crear notificación de prueba
notif = NotificacionSistema.crear_notificacion(
    usuario=admin_user,
    titulo="¡Sistema de Notificaciones Activo! 🎉",
    mensaje="El sistema de notificaciones en tiempo real está funcionando correctamente. Recibirás alertas automáticas sobre ventas, recargas y stock bajo.",
    tipo='success',
    prioridad='alta',
    icono='fa-check-circle',
    url='/admin/gestion/notificacionsistema/'
)

print(f"\n✅ Notificación creada:")
print(f"   ID: {notif.id}")
print(f"   Título: {notif.titulo}")
print(f"   Tipo: {notif.tipo}")
print(f"   Prioridad: {notif.prioridad}")
print(f"   Leída: {notif.leida}")

# Contar notificaciones no leídas
count = NotificacionSistema.count_no_leidas(admin_user)
print(f"\n📊 Notificaciones no leídas: {count}")

print("\n" + "=" * 80)
print("✅ COMPLETADO")
print("=" * 80)
print("\n💡 Ahora puedes:")
print("   1. Ir a http://localhost:8000/admin/gestion/notificacionsistema/")
print("   2. Ver la notificación de prueba")
print("   3. Verificar que aparece en el panel principal del sistema")
print("   4. Hacer clic en 'Notificaciones' en el admin para administrarlas")
