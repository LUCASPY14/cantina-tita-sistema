"""
Utilidades para formateo de moneda paraguaya (Guaraníes)
"""
from decimal import Decimal


def formatear_guaranies(monto):
    """
    Formatea un monto en Guaraníes con el símbolo Gs.
    
    Args:
        monto: Monto a formatear (puede ser int, float o Decimal)
    
    Returns:
        str: Monto formateado como "Gs. 1.000.000"
    
    Ejemplos:
        >>> formatear_guaranies(1000000)
        'Gs. 1.000.000'
        >>> formatear_guaranies(50000)
        'Gs. 50.000'
    """
    if monto is None:
        return 'Gs. 0'
    
    # Convertir a int (los guaraníes no tienen decimales)
    monto = int(monto)
    
    # Formatear con separador de miles
    monto_str = f"{monto:,}".replace(',', '.')
    
    return f"Gs. {monto_str}"


def formatear_guaranies_largo(monto):
    """
    Formatea un monto en Guaraníes con el nombre completo
    
    Args:
        monto: Monto a formatear
    
    Returns:
        str: Monto formateado como "1.000.000 Guaraníes"
    """
    if monto is None:
        return '0 Guaraníes'
    
    monto = int(monto)
    monto_str = f"{monto:,}".replace(',', '.')
    
    if monto == 1:
        return f"{monto_str} Guaraní"
    else:
        return f"{monto_str} Guaraníes"


def parsear_guaranies(texto):
    """
    Convierte un texto con formato de guaraníes a número
    
    Args:
        texto: Texto con formato "Gs. 1.000.000" o "1.000.000"
    
    Returns:
        int: Monto como número entero
    
    Ejemplos:
        >>> parsear_guaranies("Gs. 1.000.000")
        1000000
        >>> parsear_guaranies("50.000")
        50000
    """
    if not texto:
        return 0
    
    # Eliminar símbolo de moneda y espacios
    texto = texto.replace('Gs.', '').replace('Gs', '').strip()
    
    # Eliminar separadores de miles
    texto = texto.replace('.', '')
    
    # Convertir a entero
    try:
        return int(texto)
    except ValueError:
        return 0


def formatear_precio_lista(precio_unitario, cantidad=1, impuesto_incluido=True):
    """
    Formatea un precio para mostrar en lista de productos
    
    Args:
        precio_unitario: Precio unitario en guaraníes
        cantidad: Cantidad (default 1)
        impuesto_incluido: Si el precio incluye IVA
    
    Returns:
        dict: Información formateada del precio
    """
    precio_unit = int(precio_unitario)
    subtotal = precio_unit * cantidad
    
    resultado = {
        'precio_unitario': formatear_guaranies(precio_unit),
        'cantidad': cantidad,
        'subtotal': formatear_guaranies(subtotal),
        'precio_unitario_num': precio_unit,
        'subtotal_num': subtotal
    }
    
    if impuesto_incluido:
        resultado['nota'] = '(IVA incluido)'
    
    return resultado


# Constantes comunes en Paraguay
SALARIO_MINIMO_2025 = 2680373  # Gs. 2.680.373 (ejemplo, verificar valor actual)
IVA_10 = Decimal('0.10')  # 10%
IVA_5 = Decimal('0.05')   # 5%

def calcular_iva(monto, tasa='10'):
    """
    Calcula el IVA de un monto
    
    Args:
        monto: Monto base
        tasa: '10' para IVA 10%, '5' para IVA 5%
    
    Returns:
        tuple: (monto_con_iva, iva_calculado)
    """
    monto = Decimal(str(monto))
    
    if tasa == '10':
        iva = monto * IVA_10
    elif tasa == '5':
        iva = monto * IVA_5
    else:
        iva = Decimal('0')
    
    monto_con_iva = monto + iva
    
    return (int(monto_con_iva), int(iva))


def extraer_iva(monto_total, tasa='10'):
    """
    Extrae el IVA de un monto que ya lo incluye
    
    Args:
        monto_total: Monto total con IVA incluido
        tasa: '10' para IVA 10%, '5' para IVA 5%
    
    Returns:
        tuple: (monto_sin_iva, iva_extraido)
    """
    monto_total = Decimal(str(monto_total))
    
    if tasa == '10':
        divisor = Decimal('1.10')
    elif tasa == '5':
        divisor = Decimal('1.05')
    else:
        return (int(monto_total), 0)
    
    monto_sin_iva = monto_total / divisor
    iva_extraido = monto_total - monto_sin_iva
    
    return (int(monto_sin_iva), int(iva_extraido))
