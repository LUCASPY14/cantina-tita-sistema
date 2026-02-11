"""
Template tags para paginación en HTML
Facilita la creación de controles de paginación con Bootstrap 5
"""
from django import template
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

register = template.Library()


@register.simple_tag(takes_context=True)
def paginate(context, queryset, per_page=25):
    """
    Pagina un queryset y agrega page_obj al contexto
    
    Uso en template:
        {% paginate object_list 25 %}
        {% for item in page_obj %}
            ...
        {% endfor %}
    """
    request = context['request']
    page = request.GET.get('page', 1)
    
    paginator = Paginator(queryset, per_page)
    
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    context['page_obj'] = page_obj
    context['paginator'] = paginator
    context['is_paginated'] = paginator.num_pages > 1
    
    return ''


@register.inclusion_tag('gestion/components/pagination.html', takes_context=True)
def render_pagination(context, page_obj=None, anchor=''):
    """
    Renderiza controles de paginación con Bootstrap 5
    
    Uso en template:
        {% render_pagination page_obj %}
        {% render_pagination page_obj anchor="#resultados" %}
    """
    if page_obj is None:
        page_obj = context.get('page_obj')
    
    if not page_obj:
        return {}
    
    # Calcular rango de páginas a mostrar (máximo 7 números)
    current_page = page_obj.number
    num_pages = page_obj.paginator.num_pages
    
    page_range = []
    
    if num_pages <= 7:
        # Mostrar todas las páginas
        page_range = range(1, num_pages + 1)
    else:
        # Mostrar ventana deslizante
        if current_page <= 4:
            # Cerca del inicio
            page_range = list(range(1, 6)) + ['...', num_pages]
        elif current_page >= num_pages - 3:
            # Cerca del final
            page_range = [1, '...'] + list(range(num_pages - 4, num_pages + 1))
        else:
            # En el medio
            page_range = [1, '...'] + list(range(current_page - 1, current_page + 2)) + ['...', num_pages]
    
    return {
        'page_obj': page_obj,
        'page_range': page_range,
        'anchor': anchor,
        'query_params': context.get('request').GET.copy() if context.get('request') else {}
    }


@register.simple_tag
def query_transform(request, **kwargs):
    """
    Transforma query params preservando los existentes
    
    Uso en template:
        <a href="?{% query_transform request page=2 %}">Página 2</a>
    """
    updated = request.GET.copy()
    for key, value in kwargs.items():
        if value is not None:
            updated[key] = value
        elif key in updated:
            del updated[key]
    
    return updated.urlencode()


@register.filter
def get_item(dictionary, key):
    """
    Obtiene un item de un diccionario por clave
    
    Uso en template:
        {{ my_dict|get_item:"key_name" }}
    """
    return dictionary.get(key)


@register.filter
def multiply(value, arg):
    """
    Multiplica dos valores
    
    Uso en template:
        {{ page_obj.number|multiply:per_page }}
    """
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return 0
