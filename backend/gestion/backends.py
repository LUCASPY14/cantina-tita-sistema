"""
Backend de autenticación personalizado para Empleados
"""
from django.contrib.auth.backends import ModelBackend  # <--- Cambiado
from django.contrib.auth.models import User
from gestion.models import Empleado
import bcrypt


class EmpleadoBackend(ModelBackend):  # <--- Cambiado
    """
    Backend de autenticación que valida contra la tabla empleados
    usando bcrypt para verificar contraseñas.
    
    Crea automáticamente un User de Django la primera vez que un empleado
    inicia sesión exitosamente.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None
        try:
            # 1. Buscar empleado activo. Usamos select_related si id_rol se usa mucho
            empleado = Empleado.objects.get(usuario=username, activo=True)
            if not empleado.contrasena_hash:
                return None
            # 2. Verificación de bcrypt
            password_bytes = password.encode('utf-8')
            hash_bytes = empleado.contrasena_hash.encode('utf-8')
            if bcrypt.checkpw(password_bytes, hash_bytes):
                # 3. Mapeo de permisos basado en tu lógica de ID de Rol
                is_staff = empleado.id_rol_id >= 2
                is_superuser = empleado.id_rol_id == 3
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'first_name': empleado.nombre,
                        'last_name': empleado.apellido,
                        'email': empleado.email or '',
                        'is_active': True,
                        'is_staff': is_staff,
                        'is_superuser': is_superuser,
                    }
                )
                if not created:
                    # Sincronización de datos si el empleado cambió de rol o nombre
                    user.first_name = empleado.nombre
                    user.last_name = empleado.apellido
                    user.email = empleado.email or ''
                    user.is_staff = is_staff
                    user.is_superuser = is_superuser
                    user.save(update_fields=['first_name', 'last_name', 'email', 'is_staff', 'is_superuser'])
                # Adjuntar el ID para uso en la sesión actual
                user._empleado_id = empleado.id_empleado
                return user
        except Empleado.DoesNotExist:
            return None
        except Exception as e:
            # Usando tu logger o print para debug
            print(f"Error en autenticación de empleado: {str(e)}")
            return None
    
    def get_user(self, user_id):
        try:
            user = User.objects.get(pk=user_id)
            # Verificamos que el empleado siga activo en cada request (importante por seguridad)
            # Aquí podrías usar cache (Redis) más adelante si la DB sufre mucho
            if Empleado.objects.filter(usuario=user.username, activo=True).exists():
                # Re-adjuntamos el ID del empleado al objeto user en la request
                empleado = Empleado.objects.only('id_empleado').get(usuario=user.username)
                user._empleado_id = empleado.id_empleado
                return user
            return None # Si ya no está activo, invalidamos la sesión
        except (User.DoesNotExist, Empleado.DoesNotExist):
            return None
