from django.db import connection

cursor = connection.cursor()

# Agregar columna Autorizado_Por
try:
    cursor.execute('ALTER TABLE ventas ADD COLUMN Autorizado_Por INT NULL AFTER Tipo_Venta')
    print('✅ Columna Autorizado_Por agregada')
except Exception as e:
    print(f'⚠️ Autorizado_Por: {e}')

# Agregar columna Motivo_Credito
try:
    cursor.execute('ALTER TABLE ventas ADD COLUMN Motivo_Credito TEXT NULL AFTER Autorizado_Por')
    print('✅ Columna Motivo_Credito agregada')
except Exception as e:
    print(f'⚠️ Motivo_Credito: {e}')

# Agregar columna Genera_Factura_Legal
try:
    cursor.execute('ALTER TABLE ventas ADD COLUMN Genera_Factura_Legal TINYINT(1) DEFAULT 0 AFTER Motivo_Credito')
    print('✅ Columna Genera_Factura_Legal agregada')
except Exception as e:
    print(f'⚠️ Genera_Factura_Legal: {e}')

# Agregar FK para Autorizado_Por
try:
    cursor.execute('''
        ALTER TABLE ventas
        ADD CONSTRAINT FK_Ventas_Autorizado_Por
        FOREIGN KEY (Autorizado_Por) REFERENCES empleados(ID_Empleado)
        ON DELETE RESTRICT ON UPDATE CASCADE
    ''')
    print('✅ Foreign Key agregada')
except Exception as e:
    print(f'⚠️ FK: {e}')

# Actualizar valores existentes
try:
    cursor.execute("UPDATE ventas SET Tipo_Venta = 'CONTADO' WHERE Tipo_Venta IN ('Venta Directa', 'Consumo Tarjeta', 'Carga Saldo', 'Pago Almuerzo')")
    print('✅ Valores de Tipo_Venta actualizados')
except Exception as e:
    print(f'⚠️ Update Tipo_Venta: {e}')

# Actualizar Genera_Factura_Legal
try:
    cursor.execute('UPDATE ventas SET Genera_Factura_Legal = 0 WHERE Nro_Factura_Venta IS NULL')
    cursor.execute('UPDATE ventas SET Genera_Factura_Legal = 1 WHERE Nro_Factura_Venta IS NOT NULL')
    print('✅ Genera_Factura_Legal actualizado')
except Exception as e:
    print(f'⚠️ Update Genera_Factura_Legal: {e}')

# Crear índices
try:
    cursor.execute('CREATE INDEX IDX_Ventas_Tipo_Venta ON ventas(Tipo_Venta)')
    print('✅ Índice IDX_Ventas_Tipo_Venta creado')
except Exception as e:
    print(f'⚠️ Índice Tipo_Venta: {e}')

try:
    cursor.execute('CREATE INDEX IDX_Ventas_Autorizado_Por ON ventas(Autorizado_Por)')
    print('✅ Índice IDX_Ventas_Autorizado_Por creado')
except Exception as e:
    print(f'⚠️ Índice Autorizado_Por: {e}')

try:
    cursor.execute('CREATE INDEX IDX_Ventas_Factura_Legal ON ventas(Genera_Factura_Legal, Tipo_Venta)')
    print('✅ Índice IDX_Ventas_Factura_Legal creado')
except Exception as e:
    print(f'⚠️ Índice Factura_Legal: {e}')

# Verificar estructura
cursor.execute('DESCRIBE ventas')
columns = cursor.fetchall()

print('\n=== ESTRUCTURA ACTUALIZADA DE TABLA VENTAS ===')
for col in columns:
    if col[0] in ('Tipo_Venta', 'Autorizado_Por', 'Motivo_Credito', 'Genera_Factura_Legal'):
        print(f'{col[0]}: {col[1]} {"NULL" if col[2] == "YES" else "NOT NULL"} {col[4] if col[4] else ""}')

print('\n✅ Migración completada exitosamente!')
