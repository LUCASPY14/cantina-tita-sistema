"""
Vistas de autenticación para el sistema Cantina Tita
"""
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy


class CustomLoginView(auth_views.LoginView):
    """
    Vista personalizada de login con redirección al POS
    """
    template_name = 'registration/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        """
        Redirige al dashboard POS después de login exitoso
        """
        # Si hay un 'next' en la URL, lo respeta
        next_url = self.request.GET.get('next') or self.request.POST.get('next')
        if next_url:
            return next_url
        
        # Redirige al POS por defecto
        return reverse_lazy('pos:venta')
    
    def form_valid(self, form):
        """
        Procesa el formulario válido
        """
        remember_me = self.request.POST.get('remember_me')
        
        if not remember_me:
            # Si no marcó "recordarme", la sesión expira al cerrar el navegador
            self.request.session.set_expiry(0)
        else:
            # Si marcó "recordarme", la sesión dura 2 semanas
            self.request.session.set_expiry(1209600)  # 2 semanas en segundos
        
        return super().form_valid(form)


class CustomLogoutView(auth_views.LogoutView):
    """
    Vista personalizada de logout
    """
    next_page = 'login'
    
    def dispatch(self, request, *args, **kwargs):
        """
        Agrega mensaje de confirmación al logout
        """
        if request.user.is_authenticated:
            # Aquí podrías agregar un mensaje de despedida
            pass
        return super().dispatch(request, *args, **kwargs)


@login_required
def dashboard_redirect(request):
    """
    Redirección desde la raíz al dashboard apropiado
    """
    # Si es superusuario, puede ir al admin
    if request.user.is_superuser:
        return redirect('admin:index')
    
    # Por defecto, todos van al POS
    return redirect('pos:venta')
