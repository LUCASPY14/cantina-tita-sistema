"""
Configuración de formatos locales para Paraguay
"""

# Formatos de fecha
DATE_FORMAT = 'd/m/Y'
TIME_FORMAT = 'H:i'
DATETIME_FORMAT = 'd/m/Y H:i:s'
YEAR_MONTH_FORMAT = 'F Y'
MONTH_DAY_FORMAT = 'j \\d\\e F'
SHORT_DATE_FORMAT = 'd/m/Y'
SHORT_DATETIME_FORMAT = 'd/m/Y H:i'

# Formatos de entrada de fecha
DATE_INPUT_FORMATS = [
    '%d/%m/%Y',  # 25/10/2025
    '%d/%m/%y',  # 25/10/25
    '%d-%m-%Y',  # 25-10-2025
    '%d-%m-%y',  # 25-10-25
    '%Y-%m-%d',  # 2025-10-25 (formato ISO)
]

DATETIME_INPUT_FORMATS = [
    '%d/%m/%Y %H:%M:%S',
    '%d/%m/%Y %H:%M',
    '%d/%m/%y %H:%M:%S',
    '%d/%m/%y %H:%M',
    '%Y-%m-%d %H:%M:%S',
    '%Y-%m-%d %H:%M',
]

TIME_INPUT_FORMATS = [
    '%H:%M:%S',
    '%H:%M',
]

# Formatos de números
DECIMAL_SEPARATOR = ','
THOUSAND_SEPARATOR = '.'
NUMBER_GROUPING = 3

# Primera día de la semana (0=Domingo, 1=Lunes)
FIRST_DAY_OF_WEEK = 1  # Lunes

# Nombres de meses en español
MONTHS = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
}

# Nombres cortos de meses
MONTHS_SHORT = {
    1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr',
    5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Ago',
    9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
}

# Días de la semana
WEEKDAYS = {
    0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves',
    4: 'Viernes', 5: 'Sábado', 6: 'Domingo'
}

# Días de la semana (corto)
WEEKDAYS_SHORT = {
    0: 'Lun', 1: 'Mar', 2: 'Mié', 3: 'Jue',
    4: 'Vie', 5: 'Sáb', 6: 'Dom'
}
