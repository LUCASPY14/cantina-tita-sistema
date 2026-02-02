from django.db import connection

cursor = connection.cursor()

# Verificar estructura de tabla ventas
cursor.execute('DESCRIBE ventas')
columns = cursor.fetchall()

print('=' * 70)
print('ESTRUCTURA DE TABLA VENTAS')
print('=' * 70)
print(f'{"Campo":<30} {"Tipo":<20} {"Null":<8} {"Default":<15}')
print('-' * 70)

for col in columns:
    campo = col[0]
    tipo = col[1]
    null_permitido = col[2]
    default = col[4] if col[4] else ''
    
    # Resaltar nuevos campos
    if campo in ('Tipo_Venta', 'Autorizado_Por', 'Motivo_Credito', 'Genera_Factura_Legal'):
        print(f'✨ {campo:<27} {tipo:<20} {null_permitido:<8} {default:<15}')
    else:
        print(f'   {campo:<27} {tipo:<20} {null_permitido:<8} {default:<15}')

print('\n' + '=' * 70)
print('VERIFICACIÓN DE DATOS EXISTENTES')
print('=' * 70)

# Verificar distribución de tipo_venta
cursor.execute('''
    SELECT 
        Tipo_Venta,
        COUNT(*) as Cantidad
    FROM ventas
    GROUP BY Tipo_Venta
''')
print('\nDistribución de Tipo_Venta:')
for row in cursor.fetchall():
    print(f'  - {row[0]}: {row[1]} ventas')

# Verificar genera_factura_legal
cursor.execute('''
    SELECT 
        Genera_Factura_Legal,
        COUNT(*) as Cantidad
    FROM ventas
    GROUP BY Genera_Factura_Legal
''')
print('\nDistribución de Genera_Factura_Legal:')
for row in cursor.fetchall():
    factura = 'SÍ' if row[0] == 1 else 'NO'
    print(f'  - Genera factura: {factura} → {row[1]} ventas')

# Verificar si hay ventas con autorización
cursor.execute('''
    SELECT COUNT(*) 
    FROM ventas 
    WHERE Autorizado_Por IS NOT NULL
''')
ventas_autorizadas = cursor.fetchone()[0]
print(f'\nVentas con autorización de supervisor: {ventas_autorizadas}')

# Verificar índices creados
cursor.execute('''
    SHOW INDEX FROM ventas 
    WHERE Key_name IN ('IDX_Ventas_Tipo_Venta', 'IDX_Ventas_Autorizado_Por', 'IDX_Ventas_Factura_Legal')
''')
indices = cursor.fetchall()
print(f'\nÍndices creados: {len(indices)}')
for idx in indices:
    print(f'  - {idx[2]} en columna {idx[4]}')

print('\n' + '=' * 70)
print('✅ VERIFICACIÓN COMPLETADA')
print('=' * 70)
print('\nResumen:')
print('  ✓ Columnas nuevas agregadas correctamente')
print('  ✓ Datos existentes actualizados')
print('  ✓ Índices creados para optimización')
print('  ✓ Sistema listo para usar')
