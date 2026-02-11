"""
Clases de Paginación Personalizadas para la API
===============================================
Proporciona paginación flexible y optimizada para diferentes endpoints
"""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardPagination(PageNumberPagination):
    """
    Paginación estándar para listados generales
    - 25 items por página (configurable)
    - Máximo 100 items por página
    - Parámetros: ?page=1&page_size=50
    """
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        """Respuesta personalizada con metadatos de paginación"""
        return Response({
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'page_size': self.page.paginator.per_page,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })


class LargePagination(PageNumberPagination):
    """
    Paginación para listados grandes (productos, inventario)
    - 50 items por página
    - Máximo 200 items por página
    """
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200
    
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'page_size': self.page.paginator.per_page,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })


class SmallPagination(PageNumberPagination):
    """
    Paginación para listados pequeños o detallados
    - 10 items por página
    - Máximo 50 items por página
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50
    
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'page_size': self.page.paginator.per_page,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })


class ReportPagination(PageNumberPagination):
    """
    Paginación para reportes
    - 100 items por página
    - Máximo 500 items por página
    - Permite exportar grandes cantidades de datos
    """
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 500
    
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'page_size': self.page.paginator.per_page,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
            'export': {
                'total_records': self.page.paginator.count,
                'available': True
            }
        })
