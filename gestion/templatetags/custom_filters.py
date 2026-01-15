"""
Filtros personalizados para templates
"""
from django import template

register = template.Library()

@register.filter
def abs(value):
    """Retorna el valor absoluto de un número"""
    try:
        return abs(float(value))
    except (ValueError, TypeError):
        return value
