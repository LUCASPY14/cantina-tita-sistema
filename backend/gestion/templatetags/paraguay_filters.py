"""
Template tags personalizados para formateo paraguayo
"""
from django import template
from django.utils.formats import number_format
from decimal import Decimal

register = template.Library()


@register.filter(name='guaranies')
def guaranies(value):
    """
    Formatea un número como Guaraníes
    Uso: {{ monto|guaranies }}
    """
    if value is None:
        return 'Gs. 0'
    
    try:
        value = int(value)
        value_str = f"{value:,}".replace(',', '.')
        return f"Gs. {value_str}"
    except (ValueError, TypeError):
        return 'Gs. 0'


@register.filter(name='guaranies_corto')
def guaranies_corto(value):
    """
    Formatea Guaraníes en formato corto (K para miles, M para millones)
    Uso: {{ monto|guaranies_corto }}
    """
    if value is None:
        return 'Gs. 0'
    
    try:
        value = int(value)
        
        if value >= 1000000:
            return f"Gs. {value/1000000:.1f}M".replace('.', ',')
        elif value >= 1000:
            return f"Gs. {value/1000:.0f}K"
        else:
            return f"Gs. {value}"
    except (ValueError, TypeError):
        return 'Gs. 0'


@register.filter(name='ruc_format')
def ruc_format(value):
    """
    Formatea un RUC paraguayo con guiones
    Formato: 12345678-9 o 1234567-8
    Uso: {{ ruc|ruc_format }}
    """
    if not value:
        return ''
    
    value = str(value).replace('-', '').strip()
    
    if len(value) == 9:
        # RUC de 8 dígitos + 1 verificador
        return f"{value[:8]}-{value[8]}"
    elif len(value) == 8:
        # RUC de 7 dígitos + 1 verificador
        return f"{value[:7]}-{value[7]}"
    else:
        return value


@register.filter(name='ci_format')
def ci_format(value):
    """
    Formatea una Cédula de Identidad paraguaya con puntos
    Formato: 1.234.567
    Uso: {{ ci|ci_format }}
    """
    if not value:
        return ''
    
    value = str(value).replace('.', '').replace('-', '').strip()
    
    try:
        # Formatear con separador de miles
        return f"{int(value):,}".replace(',', '.')
    except ValueError:
        return value


@register.filter(name='telefono_py')
def telefono_py(value):
    """
    Formatea un teléfono paraguayo
    Formato: (021) 123-456 o 0981 123 456
    Uso: {{ telefono|telefono_py }}
    """
    if not value:
        return ''
    
    value = str(value).replace('(', '').replace(')', '').replace('-', '').replace(' ', '').strip()
    
    if value.startswith('09') and len(value) == 10:
        # Celular: 0981 123 456
        return f"{value[:4]} {value[4:7]} {value[7:]}"
    elif len(value) >= 7:
        # Fijo: (021) 123-456
        if len(value) > 6:
            codigo = value[:3]
            numero = value[3:]
            return f"({codigo}) {numero[:3]}-{numero[3:]}"
    
    return value


@register.simple_tag
def monto_con_iva(monto, tasa=10):
    """
    Calcula y muestra el monto con IVA
    Uso: {% monto_con_iva 100000 10 %}
    """
    if monto is None:
        return 'Gs. 0'
    
    try:
        monto = Decimal(str(monto))
        tasa_decimal = Decimal(str(tasa)) / 100
        total = monto * (1 + tasa_decimal)
        
        return f"Gs. {int(total):,}".replace(',', '.')
    except (ValueError, TypeError):
        return 'Gs. 0'


@register.simple_tag
def fecha_py(fecha):
    """
    Formatea una fecha en formato paraguayo
    Uso: {% fecha_py fecha %}
    """
    if not fecha:
        return ''
    
    from django.utils import formats
    return formats.date_format(fecha, "d/m/Y")


@register.simple_tag
def fecha_hora_py(fecha):
    """
    Formatea una fecha y hora en formato paraguayo
    Uso: {% fecha_hora_py fecha %}
    """
    if not fecha:
        return ''
    
    from django.utils import formats
    return formats.date_format(fecha, "d/m/Y H:i")
