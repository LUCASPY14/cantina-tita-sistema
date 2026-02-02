"""
Sistema de Matching Automático: Producto vs Restricción Alimentaria

Este módulo implementa el análisis automático de productos contra restricciones
alimentarias de los estudiantes, utilizando palabras clave y categorías.
"""

from django.db import models
from decimal import Decimal
from typing import List, Dict, Tuple
import re


class ProductoRestriccionMatcher:
    """
    Clase para hacer matching entre productos y restricciones alimentarias
    """
    
    # Diccionario de palabras clave por tipo de restricción
    KEYWORDS_RESTRICCIONES = {
        'Celíaco': [
            'harina', 'trigo', 'pan', 'galleta', 'pasta', 'fideos',
            'empanada', 'pizza', 'torta', 'bizcocho', 'pastel',
            'cerveza', 'malta', 'avena', 'cebada', 'centeno'
        ],
        'Intolerancia a la lactosa': [
            'leche', 'yogur', 'queso', 'crema', 'manteca', 'manteiga',
            'dulce de leche', 'nata', 'lacteo', 'lácteo', 'helado',
            'flan', 'natilla', 'ricota', 'mozarella', 'parmesano'
        ],
        'Alergia al maní': [
            'mani', 'maní', 'cacahuate', 'cacahuete', 'peanut',
            'mantequilla de mani', 'mantequilla de maní'
        ],
        'Alergia a frutos secos': [
            'nuez', 'almendra', 'avellana', 'pistacho', 'castaña',
            'anacardo', 'macadamia', 'pecana', 'nueces', 'almendras'
        ],
        'Alergia al huevo': [
            'huevo', 'clara', 'yema', 'merengue', 'mayonesa',
            'tortilla', 'omelette', 'omelet'
        ],
        'Alergia a mariscos': [
            'camaron', 'camarón', 'langosta', 'cangrejo', 'surubí',
            'pescado', 'atún', 'salmon', 'salmón', 'merluza',
            'corvina', 'dorado', 'mejillón', 'almeja', 'calamar'
        ],
        'Vegetariano': [
            'carne', 'pollo', 'cerdo', 'res', 'vacuno', 'pavo',
            'jamón', 'chorizo', 'salchicha', 'mortadela', 'milanesa',
            'hamburguesa', 'asado', 'costilla', 'lomo'
        ],
        'Vegano': [
            'carne', 'pollo', 'cerdo', 'res', 'vacuno', 'pavo',
            'jamón', 'chorizo', 'salchicha', 'mortadela', 'milanesa',
            'hamburguesa', 'asado', 'costilla', 'lomo',
            'leche', 'yogur', 'queso', 'crema', 'manteca',
            'huevo', 'clara', 'yema', 'miel'
        ],
        'Diabetes': [
            'azucar', 'azúcar', 'dulce', 'caramelo', 'chocolate',
            'gaseosa', 'coca', 'sprite', 'fanta', 'refresco',
            'jugo', 'néctar', 'helado', 'golosina', 'galleta dulce'
        ],
        'Hipertensión': [
            'sal', 'salado', 'embutido', 'fiambre', 'jamón',
            'mortadela', 'chorizo', 'salchicha', 'snack',
            'chipa', 'chipá', 'papas fritas', 'papa frita'
        ]
    }
    
    # Categorías de productos que típicamente contienen alérgenos
    CATEGORIAS_RIESGO = {
        'Celíaco': ['Panadería', 'Pastelería', 'Snacks'],
        'Intolerancia a la lactosa': ['Lácteos', 'Postres', 'Helados'],
        'Alergia al maní': ['Snacks', 'Dulces', 'Confitería'],
        'Alergia a frutos secos': ['Snacks', 'Dulces', 'Confitería'],
        'Alergia al huevo': ['Panadería', 'Pastelería', 'Postres'],
        'Alergia a mariscos': ['Almuerzos', 'Platos preparados'],
        'Vegetariano': ['Almuerzos', 'Snacks', 'Platos preparados'],
        'Vegano': ['Almuerzos', 'Lácteos', 'Postres', 'Platos preparados'],
        'Diabetes': ['Dulces', 'Bebidas', 'Snacks', 'Postres'],
        'Hipertensión': ['Snacks', 'Almuerzos', 'Embutidos']
    }
    
    @classmethod
    def analizar_producto(cls, producto, restriccion) -> Tuple[bool, str, int]:
        """
        Analiza si un producto puede contener ingredientes restringidos
        
        Args:
            producto: Objeto Producto de Django
            restriccion: Objeto RestriccionesHijos con tipo_restriccion y observaciones
            
        Returns:
            Tuple (tiene_conflicto: bool, razon: str, nivel_confianza: int)
            nivel_confianza: 0-100 (0=sin match, 100=match seguro)
        """
        tipo_restriccion = restriccion.tipo_restriccion
        keywords = cls.KEYWORDS_RESTRICCIONES.get(tipo_restriccion, [])
        categorias_riesgo = cls.CATEGORIAS_RIESGO.get(tipo_restriccion, [])
        
        nivel_confianza = 0
        razones = []
        
        # 1. Buscar palabras clave en descripción del producto
        descripcion_lower = producto.descripcion.lower()
        
        for keyword in keywords:
            if keyword in descripcion_lower:
                nivel_confianza += 30
                razones.append(f"Contiene '{keyword}' en descripción")
        
        # 2. Verificar categoría del producto
        if hasattr(producto, 'id_categoria') and producto.id_categoria:
            categoria_nombre = producto.id_categoria.nombre
            if categoria_nombre in categorias_riesgo:
                nivel_confianza += 20
                razones.append(f"Pertenece a categoría de riesgo: {categoria_nombre}")
        
        # 3. Revisar componentes si es un almuerzo
        if hasattr(producto, 'componentesalmuerzo_set'):
            componentes = producto.componentesalmuerzo_set.all()
            for componente in componentes:
                comp_desc = componente.nombre_componente.lower()
                for keyword in keywords:
                    if keyword in comp_desc:
                        nivel_confianza += 25
                        razones.append(f"Componente '{componente.nombre_componente}' puede contener {keyword}")
        
        # 4. Verificar observaciones específicas de la restricción
        if restriccion.observaciones:
            obs_lower = restriccion.observaciones.lower()
            for keyword in keywords:
                if keyword in obs_lower:
                    nivel_confianza += 15
                    razones.append(f"Observaciones mencionan '{keyword}'")
        
        # Limitar confianza a 100
        nivel_confianza = min(nivel_confianza, 100)
        
        tiene_conflicto = nivel_confianza >= 50  # Umbral: 50% de confianza
        razon = "; ".join(razones) if razones else "Sin coincidencias detectadas"
        
        return tiene_conflicto, razon, nivel_confianza
    
    @classmethod
    def analizar_carrito(cls, items_carrito: List[Dict], tarjeta) -> Dict:
        """
        Analiza todo el carrito contra las restricciones del estudiante
        
        Args:
            items_carrito: Lista de diccionarios con {producto, cantidad}
            tarjeta: Objeto Tarjeta con id_hijo asociado
            
        Returns:
            Dict con análisis completo:
            {
                'tiene_alertas': bool,
                'alertas': [
                    {
                        'producto': Producto,
                        'restriccion': RestriccionesHijos,
                        'razon': str,
                        'nivel_confianza': int,
                        'severidad': 'alta|media|baja'
                    }
                ],
                'puede_continuar': bool,
                'requiere_autorizacion': bool
            }
        """
        from gestion.models import RestriccionesHijos, Producto
        
        resultado = {
            'tiene_alertas': False,
            'alertas': [],
            'puede_continuar': True,
            'requiere_autorizacion': False
        }
        
        # Si no hay tarjeta o no tiene hijo asociado, no hay restricciones que verificar
        if not tarjeta or not hasattr(tarjeta, 'id_hijo') or not tarjeta.id_hijo:
            return resultado
        
        # Obtener restricciones del hijo
        restricciones = RestriccionesHijos.objects.filter(
            id_hijo=tarjeta.id_hijo,
            activo=True
        )
        
        if not restricciones.exists():
            return resultado
        
        # Analizar cada producto contra cada restricción
        for item in items_carrito:
            producto = item.get('producto')
            if not producto:
                continue
            
            for restriccion in restricciones:
                tiene_conflicto, razon, nivel_confianza = cls.analizar_producto(
                    producto, restriccion
                )
                
                if tiene_conflicto:
                    # Determinar severidad según nivel de confianza
                    if nivel_confianza >= 80:
                        severidad = 'alta'
                        resultado['requiere_autorizacion'] = True
                    elif nivel_confianza >= 60:
                        severidad = 'media'
                        resultado['requiere_autorizacion'] = True
                    else:
                        severidad = 'baja'
                    
                    resultado['alertas'].append({
                        'producto': producto,
                        'restriccion': restriccion,
                        'razon': razon,
                        'nivel_confianza': nivel_confianza,
                        'severidad': severidad
                    })
                    resultado['tiene_alertas'] = True
        
        return resultado
    
    @classmethod
    def obtener_productos_seguros(cls, restriccion, categoria=None) -> List:
        """
        Obtiene lista de productos seguros para una restricción específica
        
        Args:
            restriccion: Objeto RestriccionesHijos
            categoria: Filtrar por categoría (opcional)
            
        Returns:
            QuerySet de productos seguros
        """
        from gestion.models import Producto
        
        productos = Producto.objects.filter(activo=True)
        
        if categoria:
            productos = productos.filter(id_categoria=categoria)
        
        # Filtrar productos que NO contengan palabras clave de la restricción
        tipo_restriccion = restriccion.tipo_restriccion
        keywords = cls.KEYWORDS_RESTRICCIONES.get(tipo_restriccion, [])
        
        productos_seguros = []
        for producto in productos:
            tiene_conflicto, _, _ = cls.analizar_producto(producto, restriccion)
            if not tiene_conflicto:
                productos_seguros.append(producto)
        
        return productos_seguros
    
    @classmethod
    def sugerir_alternativas(cls, producto, restriccion, max_resultados=5) -> List:
        """
        Sugiere productos alternativos seguros de la misma categoría
        
        Args:
            producto: Producto conflictivo
            restriccion: Restricción alimentaria
            max_resultados: Máximo de sugerencias
            
        Returns:
            Lista de productos alternativos seguros
        """
        categoria = producto.id_categoria if hasattr(producto, 'id_categoria') else None
        productos_seguros = cls.obtener_productos_seguros(restriccion, categoria)
        
        return productos_seguros[:max_resultados]


# Función de utilidad para usar en views
def verificar_restricciones_venta(tarjeta, items_carrito):
    """
    Función helper para verificar restricciones en una venta
    
    Args:
        tarjeta: Objeto Tarjeta
        items_carrito: Lista de items [{producto_id, cantidad}]
        
    Returns:
        Dict con resultado del análisis
    """
    from gestion.models import Producto
    
    # Convertir items a formato esperado
    items = []
    for item in items_carrito:
        try:
            producto = Producto.objects.get(id_producto=item['producto_id'])
            items.append({'producto': producto, 'cantidad': item.get('cantidad', 1)})
        except Producto.DoesNotExist:
            continue
    
    return ProductoRestriccionMatcher.analizar_carrito(items, tarjeta)
