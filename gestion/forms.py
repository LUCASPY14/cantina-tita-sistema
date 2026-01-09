"""
Formularios con Validaciones - Sistema de Cuenta Corriente
===========================================================

Formularios Django que integran las validaciones del modelo.
"""

from django import forms
from django.core.exceptions import ValidationError
from decimal import Decimal

from .models import (
    Ventas, Compras, PagosVenta, AplicacionPagosVentas, PagosProveedores,
    Producto, Categoria, UnidadMedida, Impuesto, Alergeno, ProductoAlergeno
)


class VentasForm(forms.ModelForm):
    """
    Formulario para crear/editar Ventas
    Integra las validaciones del modelo
    """
    
    class Meta:
        model = Ventas
        fields = [
            'nro_factura_venta',
            'id_cliente',
            'id_tipo_pago',
            'id_empleado_cajero',
            'fecha',
            'monto_total',
            'saldo_pendiente',
            'estado_pago',
            'estado',
            'tipo_venta'
        ]
        widgets = {
            'fecha': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'observaciones': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean(self):
        """
        Validaciones a nivel de formulario
        Llama a las validaciones del modelo
        """
        cleaned_data = super().clean()
        
        # Crear instancia temporal para validar
        instance = Ventas(**cleaned_data)
        
        try:
            # Ejecutar validaciones del modelo
            instance.clean()
        except ValidationError as e:
            # Re-lanzar errores para mostrarlos en el formulario
            for field, errors in e.message_dict.items():
                for error in errors:
                    self.add_error(field, error)
        
        return cleaned_data
    
    def clean_saldo_pendiente(self):
        """Validación adicional: saldo no puede ser negativo"""
        saldo = self.cleaned_data.get('saldo_pendiente')
        
        if saldo and saldo < 0:
            raise ValidationError("El saldo pendiente no puede ser negativo")
        
        return saldo
    
    def clean_monto_total(self):
        """Validación adicional: monto total debe ser mayor a 0"""
        monto = self.cleaned_data.get('monto_total')
        
        if monto and monto <= 0:
            raise ValidationError("El monto total debe ser mayor a 0")
        
        return monto


class ComprasForm(forms.ModelForm):
    """
    Formulario para crear/editar Compras
    """
    
    class Meta:
        model = Compras
        fields = [
            'nro_factura',
            'id_proveedor',
            'fecha',
            'monto_total',
            'saldo_pendiente',
            'estado_pago'
        ]
        widgets = {
            'fecha': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def clean(self):
        """Validaciones a nivel de formulario"""
        cleaned_data = super().clean()
        
        total = cleaned_data.get('monto_total')
        saldo = cleaned_data.get('saldo_pendiente')
        estado_pago = cleaned_data.get('estado_pago')
        
        # Validar saldo <= total
        if total and saldo and saldo > total:
            self.add_error('saldo_pendiente', 'El saldo no puede ser mayor al total')
        
        # Validar consistencia estado con saldo
        if estado_pago == 'PAGADA' and saldo and saldo > 0:
            self.add_error('estado_pago', 'Una compra PAGADA debe tener saldo 0')
        
        if estado_pago == 'PENDIENTE' and total and saldo != total:
            self.add_error('estado_pago', 'Una compra PENDIENTE debe tener saldo igual al total')
        
        return cleaned_data


class PagosVentaForm(forms.ModelForm):
    """
    Formulario para registrar pagos de ventas
    """
    
    class Meta:
        model = PagosVenta
        fields = [
            'id_cliente',
            'monto_pago',
            'fecha_pago',
            'id_medio_pago',
            'observaciones'
        ]
        widgets = {
            'fecha_pago': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'observaciones': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean_monto_pago(self):
        """Validar que el monto del pago sea mayor a 0"""
        monto = self.cleaned_data.get('monto_pago')
        
        if monto and monto <= 0:
            raise ValidationError("El monto del pago debe ser mayor a 0")
        
        return monto


class AplicacionPagosVentasForm(forms.ModelForm):
    """
    Formulario para aplicar pagos a ventas específicas
    """
    
    class Meta:
        model = AplicacionPagosVentas
        fields = [
            'id_pago_venta',
            'id_venta',
            'monto_aplicado'
        ]
    
    def clean(self):
        """Validaciones a nivel de formulario"""
        cleaned_data = super().clean()
        
        pago = cleaned_data.get('id_pago_venta')
        venta = cleaned_data.get('id_venta')
        monto_aplicado = cleaned_data.get('monto_aplicado')
        
        if not all([pago, venta, monto_aplicado]):
            return cleaned_data
        
        # Validar que el monto aplicado sea mayor a 0
        if monto_aplicado <= 0:
            self.add_error('monto_aplicado', 'El monto aplicado debe ser mayor a 0')
        
        # Validar que no exceda el saldo pendiente de la venta
        if monto_aplicado > venta.saldo_pendiente:
            self.add_error(
                'monto_aplicado',
                f'El monto aplicado ({monto_aplicado}) no puede ser mayor '
                f'al saldo pendiente de la venta ({venta.saldo_pendiente})'
            )
        
        # Validar que no exceda el monto del pago
        total_aplicado = AplicacionPagosVentas.objects.filter(
            id_pago_venta=pago
        ).exclude(
            id_aplicacion=self.instance.id_aplicacion if self.instance.pk else None
        ).aggregate(
            total=models.Sum('monto_aplicado')
        )['total'] or 0
        
        if total_aplicado + monto_aplicado > pago.monto_pago:
            disponible = pago.monto_pago - total_aplicado
            self.add_error(
                'monto_aplicado',
                f'El monto disponible del pago es {disponible}. '
                f'Ya se aplicaron {total_aplicado} del total {pago.monto_pago}'
            )
        
        return cleaned_data


class PagosProveedorForm(forms.ModelForm):
    """
    Formulario para registrar pagos a proveedores
    """
    
    class Meta:
        model = PagosProveedor
        fields = [
            'id_proveedor',
            'id_compra',
            'monto_pago',
            'fecha_pago',
            'id_medio_pago',
            'observaciones'
        ]
        widgets = {
            'fecha_pago': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'observaciones': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean(self):
        """Validaciones a nivel de formulario"""
        cleaned_data = super().clean()
        
        compra = cleaned_data.get('id_compra')
        monto_pago = cleaned_data.get('monto_pago')
        
        if not all([compra, monto_pago]):
            return cleaned_data
        
        # Validar que el monto sea mayor a 0
        if monto_pago <= 0:
            self.add_error('monto_pago', 'El monto del pago debe ser mayor a 0')
        
        # Validar que no exceda el saldo pendiente
        if monto_pago > compra.saldo_pendiente:
            self.add_error(
                'monto_pago',
                f'El monto del pago ({monto_pago}) no puede ser mayor '
                f'al saldo pendiente de la compra ({compra.saldo_pendiente})'
            )
        
        return cleaned_data


# =============================================================================
# Formularios de Filtros para Reportes
# =============================================================================

class FiltroReporteForm(forms.Form):
    """
    Formulario base para filtros de reportes
    """
    fecha_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Fecha Inicio'
    )
    fecha_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Fecha Fin'
    )
    
    def clean(self):
        """Validar que fecha_inicio <= fecha_fin"""
        cleaned_data = super().clean()
        
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        
        if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
            raise ValidationError(
                'La fecha de inicio no puede ser mayor a la fecha de fin'
            )
        
        return cleaned_data


class FiltroCuentaCorrienteClienteForm(FiltroReporteForm):
    """
    Formulario para filtrar reporte de cuenta corriente de clientes
    """
    from .models import Cliente
    
    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.filter(activo=True).order_by('nombres'),
        required=False,
        label='Cliente',
        empty_label='-- Todos los clientes --'
    )
    
    estado_pago = forms.ChoiceField(
        choices=[
            ('', '-- Todos los estados --'),
            ('PENDIENTE', 'PENDIENTE'),
            ('PARCIAL', 'PARCIAL'),
            ('PAGADA', 'PAGADA'),
        ],
        required=False,
        label='Estado de Pago'
    )


class FiltroCuentaCorrienteProveedorForm(FiltroReporteForm):
    """
    Formulario para filtrar reporte de cuenta corriente de proveedores
    """
    from .models import Proveedor
    
    proveedor = forms.ModelChoiceField(
        queryset=Proveedor.objects.filter(activo=True).order_by('razon_social'),
        required=False,
        label='Proveedor',
        empty_label='-- Todos los proveedores --'
    )
    
    estado_pago = forms.ChoiceField(
        choices=[
            ('', '-- Todos los estados --'),
            ('PENDIENTE', 'PENDIENTE'),
            ('PARCIAL', 'PARCIAL'),
            ('PAGADA', 'PAGADA'),
        ],
        required=False,
        label='Estado de Pago'
    )


# =============================================================================
# Ejemplo de uso en vistas
# =============================================================================

"""
# En views.py:

from django.shortcuts import render, redirect
from .forms import VentasForm, PagosVentaForm

def crear_venta(request):
    if request.method == 'POST':
        form = VentasForm(request.POST)
        if form.is_valid():
            venta = form.save()
            messages.success(request, f'Venta {venta.nro_factura_venta} creada exitosamente')
            return redirect('detalle_venta', pk=venta.pk)
    else:
        form = VentasForm()
    
    return render(request, 'ventas/crear.html', {'form': form})


def aplicar_pago_venta(request, venta_id):
    venta = get_object_or_404(Ventas, pk=venta_id)
    
    if request.method == 'POST':
        pago_form = PagosVentaForm(request.POST)
        aplicacion_form = AplicacionPagosVentasForm(request.POST)
        
        if pago_form.is_valid() and aplicacion_form.is_valid():
            # Guardar pago
            pago = pago_form.save()
            
            # Aplicar a la venta
            aplicacion = aplicacion_form.save(commit=False)
            aplicacion.id_pago_venta = pago
            aplicacion.id_venta = venta
            aplicacion.save()
            
            messages.success(request, 'Pago aplicado exitosamente')
            return redirect('detalle_venta', pk=venta_id)
    else:
        pago_form = PagosVentaForm(initial={'id_cliente': venta.id_cliente})
        aplicacion_form = AplicacionPagosVentasForm()
    
    context = {
        'venta': venta,
        'pago_form': pago_form,
        'aplicacion_form': aplicacion_form
    }
    
    return render(request, 'ventas/aplicar_pago.html', context)
"""


# ==================== PRODUCTOS ====================

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

