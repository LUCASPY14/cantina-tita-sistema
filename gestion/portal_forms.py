# Portal de Padres - Formularios
# Formularios para registro, login y recuperación de contraseña

from django import forms
from django.contrib.auth.hashers import make_password, check_password
from django.core.validators import EmailValidator
from .models import UsuarioPortal, Hijo
import re


class RegistroForm(forms.Form):
    """Formulario de registro para nuevos usuarios del portal"""
    
    email = forms.EmailField(
        label='Correo Electrónico',
        max_length=255,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com',
            'required': True
        }),
        validators=[EmailValidator(message='Ingrese un correo electrónico válido')]
    )
    
    password = forms.CharField(
        label='Contraseña',
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mínimo 8 caracteres',
            'required': True
        }),
        help_text='La contraseña debe tener al menos 8 caracteres, incluir mayúsculas, minúsculas y números'
    )
    
    password_confirm = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Repita la contraseña',
            'required': True
        })
    )
    
    ruc_ci = forms.CharField(
        label='RUC/CI del Titular',
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '12345678-9',
            'required': True
        }),
        help_text='Ingrese el RUC o CI del titular registrado en el sistema'
    )
    
    acepto_terminos = forms.BooleanField(
        label='Acepto los términos y condiciones',
        required=True,
        error_messages={'required': 'Debe aceptar los términos y condiciones'}
    )
    
    def clean_email(self):
        """Valida que el email no esté ya registrado"""
        email = self.cleaned_data.get('email')
        if UsuarioPortal.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo electrónico ya está registrado')
        return email.lower()
    
    def clean_password(self):
        """Valida complejidad de la contraseña"""
        password = self.cleaned_data.get('password')
        
        if len(password) < 8:
            raise forms.ValidationError('La contraseña debe tener al menos 8 caracteres')
        
        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError('La contraseña debe incluir al menos una letra mayúscula')
        
        if not re.search(r'[a-z]', password):
            raise forms.ValidationError('La contraseña debe incluir al menos una letra minúscula')
        
        if not re.search(r'\d', password):
            raise forms.ValidationError('La contraseña debe incluir al menos un número')
        
        return password
    
    def clean(self):
        """Valida que las contraseñas coincidan"""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm:
            if password != password_confirm:
                raise forms.ValidationError('Las contraseñas no coinciden')
        
        return cleaned_data


class LoginForm(forms.Form):
    """Formulario de inicio de sesión"""
    
    email = forms.EmailField(
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com',
            'autofocus': True,
            'required': True
        })
    )
    
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su contraseña',
            'required': True
        })
    )
    
    recordarme = forms.BooleanField(
        label='Recordarme',
        required=False,
        initial=False
    )
    
    def clean(self):
        """Valida credenciales del usuario"""
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        
        if email and password:
            try:
                usuario = UsuarioPortal.objects.get(email=email.lower())
                
                if not usuario.activo:
                    raise forms.ValidationError('Su cuenta está desactivada. Contacte al administrador.')
                
                if not check_password(password, usuario.password_hash):
                    raise forms.ValidationError('Credenciales incorrectas')
                
                # Guardar usuario para uso posterior
                cleaned_data['usuario'] = usuario
                
            except UsuarioPortal.DoesNotExist:
                raise forms.ValidationError('Credenciales incorrectas')
        
        return cleaned_data


class RecuperarPasswordForm(forms.Form):
    """Formulario para solicitar recuperación de contraseña"""
    
    email = forms.EmailField(
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com',
            'autofocus': True,
            'required': True
        }),
        help_text='Ingrese el correo electrónico con el que se registró'
    )
    
    def clean_email(self):
        """Valida que el email exista en el sistema"""
        email = self.cleaned_data.get('email')
        
        if not UsuarioPortal.objects.filter(email=email.lower()).exists():
            raise forms.ValidationError('No encontramos una cuenta con este correo electrónico')
        
        return email.lower()


class CambiarPasswordForm(forms.Form):
    """Formulario para cambiar la contraseña con token"""
    
    password = forms.CharField(
        label='Nueva Contraseña',
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mínimo 8 caracteres',
            'required': True
        }),
        help_text='La contraseña debe tener al menos 8 caracteres, incluir mayúsculas, minúsculas y números'
    )
    
    password_confirm = forms.CharField(
        label='Confirmar Nueva Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Repita la contraseña',
            'required': True
        })
    )
    
    def clean_password(self):
        """Valida complejidad de la contraseña"""
        password = self.cleaned_data.get('password')
        
        if len(password) < 8:
            raise forms.ValidationError('La contraseña debe tener al menos 8 caracteres')
        
        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError('La contraseña debe incluir al menos una letra mayúscula')
        
        if not re.search(r'[a-z]', password):
            raise forms.ValidationError('La contraseña debe incluir al menos una letra minúscula')
        
        if not re.search(r'\d', password):
            raise forms.ValidationError('La contraseña debe incluir al menos un número')
        
        return password
    
    def clean(self):
        """Valida que las contraseñas coincidan"""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm:
            if password != password_confirm:
                raise forms.ValidationError('Las contraseñas no coinciden')
        
        return cleaned_data


class ActualizarPerfilForm(forms.Form):
    """Formulario para actualizar información del perfil"""
    
    email = forms.EmailField(
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'readonly': True
        }),
        disabled=True
    )
    
    telefono_contacto = forms.CharField(
        label='Teléfono de Contacto',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+595981123456'
        })
    )
    
    notificaciones_email = forms.BooleanField(
        label='Recibir notificaciones por correo',
        required=False,
        initial=True
    )
    
    notificaciones_saldo_bajo = forms.BooleanField(
        label='Alertas de saldo bajo',
        required=False,
        initial=True
    )
    
    umbral_saldo_bajo = forms.IntegerField(
        label='Umbral de saldo bajo (Guaraníes)',
        min_value=0,
        initial=5000,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '5000'
        }),
        help_text='Recibirá una alerta cuando el saldo sea menor a este monto'
    )
