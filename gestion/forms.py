"""
Formularios con Validaciones - Sistema de Cuenta Corriente
===========================================================

Formularios Django que integran las validaciones del modelo.
"""

from django import forms
from django.core.exceptions import ValidationError
from decimal import Decimal

from .models import Ventas, Compras, PagosVenta, AplicacionPagosVentas, PagosProveedor


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
            'total',
            'saldo_pendiente',
            'estado_pago'
        ]
        widgets = {
            'fecha': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def clean(self):
        """Validaciones a nivel de formulario"""
        cleaned_data = super().clean()
        
        total = cleaned_data.get('total')
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
