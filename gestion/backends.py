"""
Backend de autenticación personalizado para Empleados
"""
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from gestion.models import Empleado
import bcrypt


class EmpleadoBackend(BaseBackend):
    """
    Backend de autenticación que valida contra la tabla empleados
    usando bcrypt para verificar contraseñas.
    
    Crea automáticamente un User de Django la primera vez que un empleado
    inicia sesión exitosamente.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Autentica un empleado verificando usuario y contraseña contra la tabla empleados.
        
        Args:
            request: HttpRequest object
            username: Usuario del empleado
            password: Contraseña en texto plano
            
        Returns:
            User object si la autenticación es exitosa, None en caso contrario
        """
        if not username or not password:
            return None
        
        try:
            # Buscar empleado activo por usuario
            empleado = Empleado.objects.get(usuario=username, activo=True)
            
            # Verificar contraseña con bcrypt
            if not empleado.contrasena_hash:
                return None
                
            password_bytes = password.encode('utf-8')
            hash_bytes = empleado.contrasena_hash.encode('utf-8')
            
            if bcrypt.checkpw(password_bytes, hash_bytes):
                # Contraseña correcta - obtener o crear User de Django
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'first_name': empleado.nombre,
                        'last_name': empleado.apellido,
                        'email': empleado.email or '',
                        'is_active': True,
                        'is_staff': empleado.id_rol_id >= 2,  # Gerente o superior
                        'is_superuser': empleado.id_rol_id == 3,  # Solo administrador
                    }
                )
                
                # Si el usuario ya existía, actualizar sus datos
                if not created:
                    user.first_name = empleado.nombre
                    user.last_name = empleado.apellido
                    user.email = empleado.email or ''
                    user.is_active = True
                    user.is_staff = empleado.id_rol_id >= 2
                    user.is_superuser = empleado.id_rol_id == 3
                    user.save()
                
                # Guardar el ID del empleado en el usuario para acceso rápido
                if not hasattr(user, '_empleado_id'):
                    user._empleado_id = empleado.id_empleado
                
                return user
            
        except Empleado.DoesNotExist:
            # Usuario no existe o no está activo
            return None
        except Exception as e:
            # Log error pero no revelar detalles
            print(f"Error en autenticación de empleado: {str(e)}")
            return None
        
        return None
    
    def get_user(self, user_id):
        """
        Obtiene un usuario por su ID.
        
        Args:
            user_id: ID del usuario Django
            
        Returns:
            User object o None
        """
        try:
            user = User.objects.get(pk=user_id)
            # Verificar que el empleado sigue activo
            try:
                empleado = Empleado.objects.get(usuario=user.username, activo=True)
                user._empleado_id = empleado.id_empleado
                return user
            except Empleado.DoesNotExist:
                # Si el empleado fue desactivado, no permitir acceso
                return None
        except User.DoesNotExist:
            return None
