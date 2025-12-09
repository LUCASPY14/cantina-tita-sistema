"""
Utilidades para el sistema de matching de productos con restricciones alimentarias
"""
from django.db import connection
import re
import json
from typing import Dict, List, Any


def analizar_restricciones_producto(producto_id: int, restricciones_texto: str) -> Dict[str, Any]:
    """
    Analiza si un producto tiene conflictos con las restricciones alimentarias de un estudiante.
    
    Args:
        producto_id: ID del producto a analizar
        restricciones_texto: Texto completo de las restricciones del estudiante
        
    Returns:
        Dict con:
        - tiene_conflicto: bool
        - nivel_riesgo: str (CRITICO, ALTO, MEDIO, BAJO)
        - coincidencias: list de alérgenos que coinciden
        - mensaje: str con mensaje descriptivo
        - puede_vender: bool
    """
    if not restricciones_texto or restricciones_texto.strip() == '':
        return {
            'tiene_conflicto': False,
            'nivel_riesgo': None,
            'coincidencias': [],
            'mensaje': 'Sin restricciones',
            'puede_vender': True
        }
    
    # 1. Obtener información del producto
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                p.ID_Producto,
                p.Descripcion,
                p.Codigo_Barra
            FROM productos p
            WHERE p.ID_Producto = %s
        """, [producto_id])
        
        producto = cursor.fetchone()
        
        if not producto:
            return {
                'tiene_conflicto': False,
                'nivel_riesgo': None,
                'coincidencias': [],
                'mensaje': 'Producto no encontrado',
                'puede_vender': False
            }
        
        prod_id, descripcion, codigo = producto
        descripcion_lower = descripcion.lower()
    
    # 2. Obtener alérgenos asociados directamente al producto
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                a.ID_Alergeno,
                a.Nombre,
                a.Icono,
                a.Nivel_Severidad,
                pa.Contiene
            FROM producto_alergenos pa
            INNER JOIN alergenos a ON pa.ID_Alergeno = a.ID_Alergeno
            WHERE pa.ID_Producto = %s
                AND a.Activo = TRUE
            ORDER BY 
                FIELD(a.Nivel_Severidad, 'CRITICO', 'ALTO', 'MEDIO', 'BAJO')
        """, [producto_id])
        
        alergenos_producto = cursor.fetchall()
    
    # 3. Obtener todos los alérgenos activos con palabras clave
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                ID_Alergeno,
                Nombre,
                Palabras_Clave,
                Nivel_Severidad,
                Icono
            FROM alergenos
            WHERE Activo = TRUE
            ORDER BY FIELD(Nivel_Severidad, 'CRITICO', 'ALTO', 'MEDIO', 'BAJO')
        """)
        
        todos_alergenos = cursor.fetchall()
    
    # 4. Analizar coincidencias
    coincidencias = []
    nivel_riesgo_maximo = None
    restricciones_lower = restricciones_texto.lower()
    
    # 4.1. Verificar alérgenos asociados directamente
    for alergeno in alergenos_producto:
        alergeno_id, nombre, icono, severidad, contiene = alergeno
        
        # Buscar si el nombre del alérgeno está en las restricciones
        if nombre.lower() in restricciones_lower:
            tipo_presencia = 'Contiene' if contiene else 'Puede contener trazas de'
            coincidencias.append({
                'alergeno': nombre,
                'icono': icono,
                'severidad': severidad,
                'tipo': tipo_presencia,
                'score': 100 if contiene else 50
            })
            
            if not nivel_riesgo_maximo or _comparar_severidad(severidad, nivel_riesgo_maximo) > 0:
                nivel_riesgo_maximo = severidad
    
    # 4.2. Buscar palabras clave en descripción del producto vs. restricciones
    for alergeno in todos_alergenos:
        alergeno_id, nombre, palabras_clave_json, severidad, icono = alergeno
        
        try:
            palabras_clave = json.loads(palabras_clave_json) if isinstance(palabras_clave_json, str) else palabras_clave_json
        except:
            palabras_clave = []
        
        # Verificar si alguna palabra clave está en las restricciones
        for palabra in palabras_clave:
            palabra_lower = palabra.lower()
            
            # Coincidencia en restricciones del estudiante
            if palabra_lower in restricciones_lower:
                # Verificar también en descripción del producto
                if palabra_lower in descripcion_lower:
                    # Ya no agregar si ya está por relación directa
                    if not any(c['alergeno'] == nombre for c in coincidencias):
                        coincidencias.append({
                            'alergeno': nombre,
                            'icono': icono,
                            'severidad': severidad,
                            'tipo': f'Producto contiene "{palabra}"',
                            'score': 70
                        })
                        
                        if not nivel_riesgo_maximo or _comparar_severidad(severidad, nivel_riesgo_maximo) > 0:
                            nivel_riesgo_maximo = severidad
                    break
    
    # 5. Generar resultado
    tiene_conflicto = len(coincidencias) > 0
    
    if not tiene_conflicto:
        return {
            'tiene_conflicto': False,
            'nivel_riesgo': None,
            'coincidencias': [],
            'mensaje': 'No se detectaron conflictos',
            'puede_vender': True,
            'producto': descripcion
        }
    
    # Ordenar coincidencias por score
    coincidencias.sort(key=lambda x: x['score'], reverse=True)
    
    # Generar mensaje
    primera_coincidencia = coincidencias[0]
    if len(coincidencias) == 1:
        mensaje = f"⚠️ {primera_coincidencia['icono']} {primera_coincidencia['alergeno']}: {primera_coincidencia['tipo']}"
    else:
        mensaje = f"⚠️ {len(coincidencias)} restricciones detectadas: " + \
                  ", ".join([f"{c['icono']} {c['alergeno']}" for c in coincidencias[:3]])
    
    # Determinar si se puede vender (crítico no se puede)
    puede_vender = nivel_riesgo_maximo != 'CRITICO'
    
    return {
        'tiene_conflicto': True,
        'nivel_riesgo': nivel_riesgo_maximo,
        'coincidencias': coincidencias,
        'mensaje': mensaje,
        'puede_vender': puede_vender,
        'producto': descripcion,
        'total_coincidencias': len(coincidencias)
    }


def _comparar_severidad(sev1: str, sev2: str) -> int:
    """
    Compara dos niveles de severidad.
    Retorna: 1 si sev1 > sev2, -1 si sev1 < sev2, 0 si son iguales
    """
    orden = {'CRITICO': 4, 'ALTO': 3, 'MEDIO': 2, 'BAJO': 1}
    val1 = orden.get(sev1, 0)
    val2 = orden.get(sev2, 0)
    
    if val1 > val2:
        return 1
    elif val1 < val2:
        return -1
    else:
        return 0


def obtener_alergenos_activos() -> List[Dict[str, Any]]:
    """Obtiene la lista de alérgenos activos en el sistema"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                ID_Alergeno,
                CONCAT(IFNULL(Icono, ''), ' ', Nombre) AS Nombre_Completo,
                Nivel_Severidad,
                Palabras_Clave
            FROM alergenos
            WHERE Activo = TRUE
            ORDER BY FIELD(Nivel_Severidad, 'CRITICO', 'ALTO', 'MEDIO', 'BAJO'), Nombre
        """)
        
        alergenos = []
        for row in cursor.fetchall():
            alergenos.append({
                'id': row[0],
                'nombre': row[1],
                'severidad': row[2],
                'palabras_clave': json.loads(row[3]) if isinstance(row[3], str) else row[3]
            })
        
        return alergenos


def asociar_alergeno_a_producto(producto_id: int, alergeno_id: int, 
                                 contiene: bool = True, 
                                 observaciones: str = None,
                                 usuario: str = None) -> bool:
    """
    Asocia un alérgeno a un producto.
    
    Args:
        producto_id: ID del producto
        alergeno_id: ID del alérgeno
        contiene: True si contiene, False si solo trazas
        observaciones: Texto opcional de observaciones
        usuario: Usuario que registra
        
    Returns:
        True si se asoció exitosamente
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO producto_alergenos 
                (ID_Producto, ID_Alergeno, Contiene, Observaciones, Usuario_Registro)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    Contiene = VALUES(Contiene),
                    Observaciones = VALUES(Observaciones),
                    Usuario_Registro = VALUES(Usuario_Registro)
            """, [producto_id, alergeno_id, contiene, observaciones, usuario])
            
            return True
    except Exception as e:
        print(f"Error asociando alérgeno: {e}")
        return False


def analizar_carrito_completo(items_carrito: List[Dict], restricciones_texto: str) -> Dict[str, Any]:
    """
    Analiza todo el carrito de compras contra las restricciones del estudiante.
    
    Args:
        items_carrito: Lista de dicts con {producto_id, cantidad, descripcion}
        restricciones_texto: Texto de restricciones del estudiante
        
    Returns:
        Dict con análisis completo del carrito
    """
    if not restricciones_texto or not items_carrito:
        return {
            'tiene_conflictos': False,
            'productos_con_conflicto': [],
            'productos_seguros': len(items_carrito),
            'nivel_riesgo_maximo': None
        }
    
    productos_con_conflicto = []
    nivel_riesgo_maximo = None
    
    for item in items_carrito:
        analisis = analizar_restricciones_producto(
            item['producto_id'],
            restricciones_texto
        )
        
        if analisis['tiene_conflicto']:
            productos_con_conflicto.append({
                **item,
                **analisis
            })
            
            if not nivel_riesgo_maximo or \
               _comparar_severidad(analisis['nivel_riesgo'], nivel_riesgo_maximo) > 0:
                nivel_riesgo_maximo = analisis['nivel_riesgo']
    
    return {
        'tiene_conflictos': len(productos_con_conflicto) > 0,
        'productos_con_conflicto': productos_con_conflicto,
        'productos_seguros': len(items_carrito) - len(productos_con_conflicto),
        'total_productos': len(items_carrito),
        'nivel_riesgo_maximo': nivel_riesgo_maximo
    }
