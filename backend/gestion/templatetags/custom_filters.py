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

@register.filter
def get_item(lista, indice):
    """
    Obtiene un item de una lista por su índice.
    Uso: {{ mi_lista|get_item:0 }}
    """
    try:
        return lista[int(indice)]
    except (ValueError, IndexError, TypeError):
        return ''
