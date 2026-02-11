"""
Utilidades y funciones auxiliares para el POS General
======================================================

Este módulo contiene funciones y clases auxiliares para:
- Validación de operaciones de venta
- Cálculo de comisiones
- Generación de alertas
- Manejo de restricciones alimentarias en tiempo real
"""

from decimal import Decimal
from typing import List, Dict, Tuple, Optional
from django.db.models import QuerySet

from .models import (
    Producto, Tarjeta, RestriccionesHijos, Hijo, 
    MediosPago, TarifasComision
)
from .restricciones_matcher import ProductoRestriccionMatcher
from django.utils import timezone


class ValidadorVenta:
    """Validador de operaciones de venta"""
    
    @staticmethod
    def validar_productos(productos: List[Dict]) -> Tuple[bool, str]:
        """
        Valida que los productos existan y tengan stock suficiente
        
        Args:
            productos: Lista de dicts con id_producto, cantidad, precio_unitario
            
        Returns:
            (valido, mensaje_error)
        """
        for item in productos:
            try:
                producto = Producto.objects.get(
                    id_producto=item['id_producto'],
                    activo=True
                )
                
                # Validar cantidad
                if item['cantidad'] <= 0:
                    return False, f"Cantidad inválida para {producto.descripcion}"
                
                # Validar stock
                stock_actual = producto.stock.stock_actual if hasattr(producto, 'stock') else 0
                if not producto.permite_stock_negativo and stock_actual < item['cantidad']:
                    return False, f"Stock insuficiente para {producto.descripcion}. Disponible: {int(stock_actual)}"
                    
            except Producto.DoesNotExist:
                return False, f"Producto {item['id_producto']} no encontrado"
                
        return True, ""
    
    @staticmethod
    def validar_pagos(pagos: List[Dict], monto_total: int) -> Tuple[bool, str]:
        """
        Valida que los pagos sean válidos y sumen el total correcto
        
        Args:
            pagos: Lista de dicts con id_medio_pago, monto, nro_tarjeta
            monto_total: Monto total de la venta
            
        Returns:
            (valido, mensaje_error)
        """
        total_pagos = 0
        
        for pago in pagos:
            if not pago.get('id_medio_pago'):
                return False, "Medio de pago no especificado"
                
            if pago.get('monto', 0) <= 0:
                return False, "El monto del pago debe ser mayor a 0"
            
            total_pagos += pago.get('monto', 0)
            
            # Validar medio de pago
            try:
                MediosPago.objects.get(id_medio_pago=pago['id_medio_pago'])
            except MediosPago.DoesNotExist:
                return False, f"Medio de pago {pago['id_medio_pago']} no válido"
        
        if total_pagos != monto_total:
            return False, f"Total de pagos ({total_pagos}) ≠ Total de venta ({monto_total})"
            
        return True, ""


class CalculadorComisiones:
    """Calcula comisiones basadas en medios de pago"""
    
    @staticmethod
    def calcular(
        id_medio_pago: int, 
        monto_pago: int,
        fecha: Optional[timezone.datetime] = None
    ) -> int:
        """
        Calcula la comisión para un medio de pago específico
        
        Args:
            id_medio_pago: ID del medio de pago
            monto_pago: Monto del pago en Guaraníes
            fecha: Fecha de la transacción (por defecto: hoy)
            
        Returns:
            Monto de comisión en Guaraníes
        """
        if fecha is None:
            fecha = timezone.now()
        
        try:
            tarifa = TarifasComision.objects.filter(
                id_medio_pago=id_medio_pago,
                activo=True,
                fecha_inicio_vigencia__lte=fecha
            ).filter(
                models.Q(fecha_fin_vigencia__isnull=True) | 
                models.Q(fecha_fin_vigencia__gte=fecha)
            ).order_by('-fecha_inicio_vigencia').first()
            
            if not tarifa:
                return 0
            
            comision = Decimal(monto_pago) * tarifa.porcentaje_comision
            
            if tarifa.monto_fijo_comision:
                comision += tarifa.monto_fijo_comision
            
            return int(comision)
            
        except Exception:
            return 0


class VerificadorRestricciones:
    """Verifica restricciones alimentarias en tiempo real"""
    
    @staticmethod
    def verificar_carrito(
        hijo: Hijo,
        productos: List[Dict]
    ) -> Dict:
        """
        Verifica restricciones para todos los productos del carrito
        
        Args:
            hijo: Instancia de Hijo
            productos: Lista de dicts con id_producto, cantidad
            
        Returns:
            {
                'tiene_alertas': bool,
                'alertas': [
                    {
                        'id_producto': int,
                        'nombre_producto': str,
                        'restriccion': str,
                        'severidad': 'ALTA|MEDIA|BAJA',
                        'razon': str,
                        'confianza': int (0-100)
                    }
                ],
                'confianza_promedio': float
            }
        """
        alertas = []
        confianzas = []
        
        # Obtener restricciones del hijo
        restricciones = RestriccionesHijos.objects.filter(
            id_hijo=hijo,
            activo=True
        )
        
        if not restricciones.exists():
            return {
                'tiene_alertas': False,
                'alertas': [],
                'confianza_promedio': 100
            }
        
        for item in productos:
            try:
                producto = Producto.objects.get(id_producto=item['id_producto'])
                
                for restriccion in restricciones:
                    tiene_conflicto, razon, confianza = \
                        ProductoRestriccionMatcher.analizar_producto(
                            producto, restriccion
                        )
                    
                    if tiene_conflicto:
                        confianzas.append(confianza)
                        
                        # Determinar severidad
                        if confianza >= 90:
                            severidad = 'ALTA'
                        elif confianza >= 70:
                            severidad = 'MEDIA'
                        else:
                            severidad = 'BAJA'
                        
                        alertas.append({
                            'id_producto': producto.id_producto,
                            'nombre_producto': producto.descripcion,
                            'restriccion': restriccion.tipo_restriccion,
                            'severidad': severidad,
                            'razon': razon,
                            'confianza': confianza
                        })
                        
            except Producto.DoesNotExist:
                continue
        
        confianza_promedio = (sum(confianzas) / len(confianzas)) if confianzas else 100
        
        return {
            'tiene_alertas': len(alertas) > 0,
            'alertas': alertas,
            'confianza_promedio': confianza_promedio
        }
    
    @staticmethod
    def obtener_productos_seguros(
        hijo: Hijo,
        limite: int = 10
    ) -> QuerySet:
        """
        Obtiene productos recomendados para el hijo (sin restricciones)
        
        Args:
            hijo: Instancia de Hijo
            limite: Número máximo de productos a retornar
            
        Returns:
            QuerySet de Productos
        """
        restricciones = RestriccionesHijos.objects.filter(
            id_hijo=hijo,
            activo=True
        )
        
        if not restricciones.exists():
            # Sin restricciones, retornar productos en stock
            return Producto.objects.filter(
                activo=True
            ).select_related('stock').filter(
                stock__stock_actual__gt=0
            )[:limite]
        
        # Productos que no generan alertas
        productos_seguros = []
        
        for producto in Producto.objects.filter(activo=True)[:100]:
            es_seguro = True
            
            for restriccion in restricciones:
                tiene_conflicto, _, _ = \
                    ProductoRestriccionMatcher.analizar_producto(
                        producto, restriccion
                    )
                
                if tiene_conflicto:
                    es_seguro = False
                    break
            
            if es_seguro:
                productos_seguros.append(producto.id_producto)
                
                if len(productos_seguros) >= limite:
                    break
        
        return Producto.objects.filter(id_producto__in=productos_seguros)


class GeneradorAlertas:
    """Genera alertas del sistema para el POS"""
    
    TIPOS_ALERTA = {
        'STOCK_BAJO': {
            'color': 'warning',
            'icon': '⚠️',
            'nivel': 'INFO'
        },
        'STOCK_CRITICO': {
            'color': 'error',
            'icon': '🔴',
            'nivel': 'ALTA'
        },
        'RESTRICCION_MEDIA': {
            'color': 'warning',
            'icon': '⚠️',
            'nivel': 'MEDIA'
        },
        'RESTRICCION_ALTA': {
            'color': 'error',
            'icon': '🚫',
            'nivel': 'ALTA'
        },
        'SALDO_BAJO': {
            'color': 'warning',
            'icon': '💰',
            'nivel': 'INFO'
        }
    }
    
    @staticmethod
    def alerta_stock_bajo(producto: Producto) -> Optional[Dict]:
        """Genera alerta si el stock está bajo"""
        stock = producto.stock.stock_actual if hasattr(producto, 'stock') else 0
        stock_minimo = producto.stock_minimo or Decimal('0')
        
        if stock > 0 and stock <= stock_minimo:
            return {
                'tipo': 'STOCK_BAJO',
                'titulo': f'Stock bajo: {producto.descripcion}',
                'descripcion': f'Stock actual: {int(stock)}, Mínimo: {int(stock_minimo)}',
                'producto_id': producto.id_producto
            }
        
        return None
    
    @staticmethod
    def alerta_restriccion(alerta_restriccion: Dict) -> Dict:
        """Formatea una alerta de restricción"""
        if alerta_restriccion['severidad'] == 'ALTA':
            tipo = 'RESTRICCION_ALTA'
        else:
            tipo = 'RESTRICCION_MEDIA'
        
        config = GeneradorAlertas.TIPOS_ALERTA[tipo]
        
        return {
            'tipo': tipo,
            'titulo': f"{config['icon']} {alerta_restriccion['nombre_producto']}",
            'descripcion': f"{alerta_restriccion['restriccion']}: {alerta_restriccion['razon']}",
            'nivel': config['nivel'],
            'confianza': alerta_restriccion['confianza']
        }
    
    @staticmethod
    def alerta_saldo_bajo(tarjeta: Tarjeta, porcentaje: int = 20) -> Optional[Dict]:
        """Genera alerta si el saldo está bajo"""
        # Comparar contra un saldo mínimo típico (ej. 50,000 Gs)
        saldo_minimo = 50000
        
        if 0 < tarjeta.saldo_actual <= saldo_minimo:
            return {
                'tipo': 'SALDO_BAJO',
                'titulo': f'Saldo bajo: {tarjeta.id_hijo.nombre}',
                'descripcion': f'Saldo actual: Gs. {tarjeta.saldo_actual:,.0f}',
                'estudiante_id': tarjeta.id_hijo.id_hijo
            }
        
        return None
