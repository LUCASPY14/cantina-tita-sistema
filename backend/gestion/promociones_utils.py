"""
Utilidades para el sistema de promociones y descuentos
"""
from django.db import connection
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, date, time
from typing import Dict, List, Any, Optional
import json


def calcular_promociones_disponibles(items_carrito: List[Dict], 
                                     estudiante_grado: str = None,
                                     codigo_promocion: str = None) -> Dict[str, Any]:
    """
    Calcula las promociones disponibles para un carrito de compras.
    
    Args:
        items_carrito: Lista de dicts con {producto_id, cantidad, precio_unitario, categoria_id}
        estudiante_grado: Grado del estudiante (opcional)
        codigo_promocion: Código de promoción ingresado (opcional)
        
    Returns:
        Dict con promociones aplicables y la mejor opción
    """
    if not items_carrito:
        return {
            'promociones_aplicables': [],
            'mejor_promocion': None,
            'descuento_maximo': 0,
            'subtotal_original': 0,
            'total_con_descuento': 0
        }
    
    # Calcular subtotal
    subtotal = sum(Decimal(str(item['precio_unitario'])) * item['cantidad'] for item in items_carrito)
    
    # Obtener fecha/hora actual
    ahora = timezone.now()
    fecha_hoy = ahora.date()
    hora_ahora = ahora.time()
    dia_semana = ahora.isoweekday()  # 1=Lunes, 7=Domingo
    
    # Buscar promociones activas
    with connection.cursor() as cursor:
        # Query base
        query = """
            SELECT 
                p.ID_Promocion,
                p.Nombre,
                p.Descripcion,
                p.Tipo_Promocion,
                p.Valor_Descuento,
                p.Aplica_A,
                p.Min_Cantidad,
                p.Monto_Minimo,
                p.Dias_Semana,
                p.Max_Usos_Cliente,
                p.Max_Usos_Total,
                p.Usos_Actuales,
                p.Prioridad
            FROM promociones p
            WHERE p.Activo = TRUE
                AND p.Fecha_Inicio <= %s
                AND (p.Fecha_Fin IS NULL OR p.Fecha_Fin >= %s)
                AND (p.Hora_Inicio IS NULL OR p.Hora_Inicio <= %s)
                AND (p.Hora_Fin IS NULL OR p.Hora_Fin >= %s)
                AND (p.Max_Usos_Total IS NULL OR p.Usos_Actuales < p.Max_Usos_Total)
        """
        
        params = [fecha_hoy, fecha_hoy, hora_ahora, hora_ahora]
        
        if codigo_promocion:
            query += " AND p.Codigo_Promocion = %s"
            params.append(codigo_promocion)
        
        query += " ORDER BY p.Prioridad, p.Valor_Descuento DESC"
        
        cursor.execute(query, params)
        promociones = cursor.fetchall()
    
    promociones_aplicables = []
    
    for promo in promociones:
        (id_promo, nombre, descripcion, tipo_promo, valor_desc, aplica_a,
         min_cant, monto_min, dias_json, max_usos_cli, max_usos_tot,
         usos_act, prioridad) = promo
        
        # Verificar día de la semana
        if dias_json:
            try:
                dias_validos = json.loads(dias_json) if isinstance(dias_json, str) else dias_json
                if dia_semana not in dias_validos:
                    continue  # No aplica hoy
            except:
                pass  # Si hay error, asumir que aplica todos los días
        
        # Verificar monto mínimo
        if monto_min and subtotal < Decimal(str(monto_min)):
            continue
        
        # Verificar según tipo de aplicación
        aplica = False
        descuento = Decimal('0')
        
        if aplica_a == 'TOTAL_VENTA':
            aplica = True
            descuento = _calcular_descuento_total(
                tipo_promo, valor_desc, subtotal, min_cant, sum(item['cantidad'] for item in items_carrito)
            )
        
        elif aplica_a == 'PRODUCTO':
            # Obtener productos de la promoción
            with connection.cursor() as cursor2:
                cursor2.execute("""
                    SELECT ID_Producto
                    FROM productos_promocion
                    WHERE ID_Promocion = %s
                """, [id_promo])
                productos_promo = [row[0] for row in cursor2.fetchall()]
            
            if productos_promo:
                items_promocion = [item for item in items_carrito if item['producto_id'] in productos_promo]
                if items_promocion:
                    aplica = True
                    descuento = _calcular_descuento_productos(
                        tipo_promo, valor_desc, items_promocion, min_cant
                    )
        
        elif aplica_a == 'CATEGORIA':
            # Obtener categorías de la promoción
            with connection.cursor() as cursor2:
                cursor2.execute("""
                    SELECT ID_Categoria
                    FROM categorias_promocion
                    WHERE ID_Promocion = %s
                """, [id_promo])
                categorias_promo = [row[0] for row in cursor2.fetchall()]
            
            if categorias_promo:
                items_promocion = [item for item in items_carrito if item.get('categoria_id') in categorias_promo]
                if items_promocion:
                    aplica = True
                    descuento = _calcular_descuento_productos(
                        tipo_promo, valor_desc, items_promocion, min_cant
                    )
        
        elif aplica_a == 'ESTUDIANTE_GRADO':
            if estudiante_grado:
                # TODO: Implementar lógica de grados permitidos
                # Por ahora, asumir que aplica
                aplica = True
                descuento = _calcular_descuento_total(
                    tipo_promo, valor_desc, subtotal, min_cant, sum(item['cantidad'] for item in items_carrito)
                )
        
        if aplica and descuento > 0:
            promociones_aplicables.append({
                'id': id_promo,
                'nombre': nombre,
                'descripcion': descripcion,
                'tipo': tipo_promo,
                'descuento': float(descuento),
                'prioridad': prioridad
            })
    
    # Determinar mejor promoción (mayor descuento)
    mejor_promocion = None
    descuento_maximo = Decimal('0')
    
    if promociones_aplicables:
        mejor = max(promociones_aplicables, key=lambda x: x['descuento'])
        mejor_promocion = mejor
        descuento_maximo = Decimal(str(mejor['descuento']))
    
    total_con_descuento = subtotal - descuento_maximo
    
    return {
        'promociones_aplicables': promociones_aplicables,
        'mejor_promocion': mejor_promocion,
        'descuento_maximo': float(descuento_maximo),
        'subtotal_original': float(subtotal),
        'total_con_descuento': float(total_con_descuento)
    }


def _calcular_descuento_total(tipo: str, valor: Decimal, subtotal: Decimal, 
                               min_cant: int, cantidad_total: int) -> Decimal:
    """Calcula descuento sobre el total"""
    if min_cant and cantidad_total < min_cant:
        return Decimal('0')
    
    if tipo == 'DESCUENTO_PORCENTAJE':
        return subtotal * (Decimal(str(valor)) / Decimal('100'))
    elif tipo == 'DESCUENTO_MONTO':
        return min(Decimal(str(valor)), subtotal)  # No descontar más del subtotal
    else:
        return Decimal('0')


def _calcular_descuento_productos(tipo: str, valor: Decimal, items: List[Dict], 
                                   min_cant: int) -> Decimal:
    """Calcula descuento sobre productos específicos"""
    cantidad_total = sum(item['cantidad'] for item in items)
    
    if min_cant and cantidad_total < min_cant:
        return Decimal('0')
    
    subtotal_items = sum(Decimal(str(item['precio_unitario'])) * item['cantidad'] for item in items)
    
    if tipo == 'DESCUENTO_PORCENTAJE':
        return subtotal_items * (Decimal(str(valor)) / Decimal('100'))
    
    elif tipo == 'DESCUENTO_MONTO':
        return min(Decimal(str(valor)), subtotal_items)
    
    elif tipo == 'PRECIO_FIJO':
        # Precio fijo para el conjunto
        return max(Decimal('0'), subtotal_items - Decimal(str(valor)))
    
    elif tipo == 'NXM':
        # Ejemplo: 2x1 = valor_descuento = 50%
        # Calcular cuántos productos gratis
        if cantidad_total >= min_cant:
            precio_promedio = subtotal_items / Decimal(str(cantidad_total))
            unidades_gratis = int(cantidad_total * (Decimal(str(valor)) / Decimal('100')))
            return precio_promedio * Decimal(str(unidades_gratis))
    
    return Decimal('0')


def registrar_promocion_aplicada(venta_id: int, promocion_id: int, 
                                  monto_descontado: Decimal) -> bool:
    """
    Registra una promoción aplicada a una venta.
    
    Returns:
        True si se registró exitosamente
    """
    try:
        with connection.cursor() as cursor:
            # Insertar aplicación
            cursor.execute("""
                INSERT INTO promociones_aplicadas
                (ID_Venta, ID_Promocion, Monto_Descontado)
                VALUES (%s, %s, %s)
            """, [venta_id, promocion_id, monto_descontado])
            
            # Incrementar contador de usos
            cursor.execute("""
                UPDATE promociones
                SET Usos_Actuales = Usos_Actuales + 1
                WHERE ID_Promocion = %s
            """, [promocion_id])
            
            return True
    except Exception as e:
        print(f"Error registrando promoción aplicada: {e}")
        return False


def obtener_promociones_activas() -> List[Dict[str, Any]]:
    """Obtiene lista de promociones activas para mostrar en admin"""
    ahora = timezone.now()
    fecha_hoy = ahora.date()
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                p.ID_Promocion,
                p.Nombre,
                p.Tipo_Promocion,
                p.Valor_Descuento,
                p.Fecha_Inicio,
                p.Fecha_Fin,
                p.Usos_Actuales,
                p.Max_Usos_Total,
                p.Activo
            FROM promociones p
            WHERE p.Fecha_Inicio <= %s
                AND (p.Fecha_Fin IS NULL OR p.Fecha_Fin >= %s)
            ORDER BY p.Activo DESC, p.Prioridad, p.Nombre
        """, [fecha_hoy, fecha_hoy])
        
        promociones = []
        for row in cursor.fetchall():
            promociones.append({
                'id': row[0],
                'nombre': row[1],
                'tipo': row[2],
                'valor': float(row[3]),
                'fecha_inicio': row[4],
                'fecha_fin': row[5],
                'usos': row[6],
                'max_usos': row[7],
                'activo': row[8]
            })
        
        return promociones


def verificar_validez_promocion(promocion_id: int) -> Dict[str, Any]:
    """
    Verifica si una promoción es válida en este momento.
    
    Returns:
        Dict con {valida: bool, motivo: str}
    """
    ahora = timezone.now()
    fecha_hoy = ahora.date()
    hora_ahora = ahora.time()
    dia_semana = ahora.isoweekday()
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                Activo,
                Fecha_Inicio,
                Fecha_Fin,
                Hora_Inicio,
                Hora_Fin,
                Dias_Semana,
                Max_Usos_Total,
                Usos_Actuales
            FROM promociones
            WHERE ID_Promocion = %s
        """, [promocion_id])
        
        promo = cursor.fetchone()
        
        if not promo:
            return {'valida': False, 'motivo': 'Promoción no encontrada'}
        
        (activo, fecha_ini, fecha_fin, hora_ini, hora_fin, 
         dias_json, max_usos, usos_act) = promo
        
        if not activo:
            return {'valida': False, 'motivo': 'Promoción desactivada'}
        
        if fecha_ini > fecha_hoy:
            return {'valida': False, 'motivo': 'Promoción aún no vigente'}
        
        if fecha_fin and fecha_fin < fecha_hoy:
            return {'valida': False, 'motivo': 'Promoción expirada'}
        
        if hora_ini and hora_ahora < hora_ini:
            return {'valida': False, 'motivo': 'Fuera del horario de promoción'}
        
        if hora_fin and hora_ahora > hora_fin:
            return {'valida': False, 'motivo': 'Fuera del horario de promoción'}
        
        if dias_json:
            try:
                dias_validos = json.loads(dias_json) if isinstance(dias_json, str) else dias_json
                if dia_semana not in dias_validos:
                    dias_nombres = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
                    return {'valida': False, 'motivo': f'No aplica los {dias_nombres[dia_semana-1]}'}
            except:
                pass
        
        if max_usos and usos_act >= max_usos:
            return {'valida': False, 'motivo': 'Promoción agotada (máximo de usos alcanzado)'}
        
        return {'valida': True, 'motivo': 'Promoción válida'}
