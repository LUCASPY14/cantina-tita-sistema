"""
Formularios para Gestión de Productos y Categorías
===================================================
"""

from django import forms
from django.core.exceptions import ValidationError

from .models import Producto, Categoria, UnidadMedida, Impuesto, Alergeno, ProductoAlergeno


class ProductoForm(forms.ModelForm):
    """
    Formulario para crear/editar Productos
    Incluye validaciones completas y soporte para alérgenos
    """
    
    # Campo multi-select para alérgenos (ManyToMany)
    alergenos = forms.ModelMultipleChoiceField(
        queryset=Alergeno.objects.filter(activo=True),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Alérgenos presentes en el producto',
        help_text='Selecciona todos los alérgenos que contiene este producto'
    )
    
    class Meta:
        model = Producto
        fields = [
            'codigo_barra',
            'descripcion',
            'id_categoria',
            'id_unidad_de_medida',
            'id_impuesto',
            'stock_minimo',
            'permite_stock_negativo',
            'activo'
        ]
        labels = {
            'codigo_barra': 'Código de Barras',
            'descripcion': 'Descripción del Producto',
            'id_categoria': 'Categoría',
            'id_unidad_de_medida': 'Unidad de Medida',
            'id_impuesto': 'Impuesto',
            'stock_minimo': 'Stock Mínimo',
            'permite_stock_negativo': 'Permite Stock Negativo',
            'activo': 'Producto Activo'
        }
        widgets = {
            'codigo_barra': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Ej: 7891234567890',
                'maxlength': 50
            }),
            'descripcion': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Ej: Coca Cola 500ml',
                'maxlength': 255
            }),
            'id_categoria': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
            'id_unidad_de_medida': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
            'id_impuesto': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
            'stock_minimo': forms.NumberInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': '0.000',
                'step': '0.001',
                'min': '0'
            }),
            'permite_stock_negativo': forms.CheckboxInput(attrs={
                'class': 'checkbox checkbox-primary'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'checkbox checkbox-primary'
            })
        }
        help_texts = {
            'codigo_barra': 'Debe ser único en el sistema',
            'stock_minimo': 'Nivel de stock que genera alertas',
            'permite_stock_negativo': 'Marcar para productos bajo pedido (ej: almuerzos preparados)'
        }
    
    def __init__(self, *args, **kwargs):
        """Inicializar formulario con alérgenos del producto si existe"""
        super().__init__(*args, **kwargs)
        
        # Si estamos editando, cargar alérgenos existentes
        if self.instance and self.instance.pk:
            self.fields['alergenos'].initial = self.instance.alergenos_producto.values_list('id_alergeno', flat=True)
        
        # Filtrar solo categorías activas y ordenar
        self.fields['id_categoria'].queryset = Categoria.objects.filter(activo=True).order_by('nombre')
        self.fields['id_unidad_de_medida'].queryset = UnidadMedida.objects.filter(activo=True).order_by('nombre')
        self.fields['id_impuesto'].queryset = Impuesto.objects.filter(activo=True).order_by('descripcion')
    
    def clean_codigo_barra(self):
        """Validar que el código de barras sea único (excepto para el mismo producto al editar)"""
        codigo = self.cleaned_data.get('codigo_barra')
        
        if not codigo:
            return codigo
        
        # Verificar duplicados
        qs = Producto.objects.filter(codigo_barra=codigo)
        
        # Si estamos editando, excluir el producto actual
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        
        if qs.exists():
            raise ValidationError(
                f'Ya existe un producto con el código de barras "{codigo}"'
            )
        
        return codigo
    
    def clean_stock_minimo(self):
        """Validar que el stock mínimo sea >= 0"""
        stock_minimo = self.cleaned_data.get('stock_minimo')
        
        if stock_minimo is not None and stock_minimo < 0:
            raise ValidationError('El stock mínimo no puede ser negativo')
        
        return stock_minimo
    
    def clean_descripcion(self):
        """Validar que la descripción no esté vacía"""
        descripcion = self.cleaned_data.get('descripcion', '').strip()
        
        if not descripcion:
            raise ValidationError('La descripción del producto es obligatoria')
        
        return descripcion
    
    def save(self, commit=True):
        """Guardar producto y relaciones con alérgenos"""
        producto = super().save(commit=commit)
        
        if commit:
            # Limpiar alérgenos existentes
            ProductoAlergeno.objects.filter(id_producto=producto).delete()
            
            # Crear nuevas relaciones con alérgenos
            alergenos = self.cleaned_data.get('alergenos', [])
            for alergeno in alergenos:
                ProductoAlergeno.objects.create(
                    id_producto=producto,
                    id_alergeno=alergeno,
                    contiene=True
                )
        
        return producto


class CategoriaForm(forms.ModelForm):
    """
    Formulario para crear/editar Categorías
    Soporte para categorías jerárquicas (padre-hijo)
    """
    
    class Meta:
        model = Categoria
        fields = ['nombre', 'id_categoria_padre', 'activo']
        labels = {
            'nombre': 'Nombre de la Categoría',
            'id_categoria_padre': 'Categoría Padre (opcional)',
            'activo': 'Categoría Activa'
        }
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Ej: Bebidas',
                'maxlength': 100
            }),
            'id_categoria_padre': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'checkbox checkbox-primary'
            })
        }
        help_texts = {
            'id_categoria_padre': 'Deja vacío para categorías principales',
            'activo': 'Desactivar oculta la categoría sin eliminarla'
        }
    
    def __init__(self, *args, **kwargs):
        """Filtrar categorías padre disponibles"""
        super().__init__(*args, **kwargs)
        
        # Excluir la categoría actual de la lista de padres (evitar ciclos)
        if self.instance and self.instance.pk:
            self.fields['id_categoria_padre'].queryset = Categoria.objects.filter(
                activo=True
            ).exclude(pk=self.instance.pk).order_by('nombre')
        else:
            self.fields['id_categoria_padre'].queryset = Categoria.objects.filter(
                activo=True
            ).order_by('nombre')
        
        # Hacer el campo opcional visualmente
        self.fields['id_categoria_padre'].required = False
        self.fields['id_categoria_padre'].empty_label = '--- Sin categoría padre ---'
    
    def clean_nombre(self):
        """Validar que el nombre no esté vacío"""
        nombre = self.cleaned_data.get('nombre', '').strip()
        
        if not nombre:
            raise ValidationError('El nombre de la categoría es obligatorio')
        
        # Verificar duplicados
        qs = Categoria.objects.filter(nombre__iexact=nombre)
        
        # Si estamos editando, excluir la categoría actual
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        
        if qs.exists():
            raise ValidationError(f'Ya existe una categoría con el nombre "{nombre}"')
        
        return nombre
    
    def clean(self):
        """Validar que no se cree un ciclo en la jerarquía"""
        cleaned_data = super().clean()
        categoria_padre = cleaned_data.get('id_categoria_padre')
        
        # Solo validar si estamos editando y hay categoría padre
        if self.instance and self.instance.pk and categoria_padre:
            # Verificar que la categoría padre no sea descendiente de la actual
            actual = categoria_padre
            while actual:
                if actual.pk == self.instance.pk:
                    raise ValidationError(
                        'No se puede seleccionar una subcategoría como categoría padre (ciclo detectado)'
                    )
                actual = actual.id_categoria_padre
        
        return cleaned_data
