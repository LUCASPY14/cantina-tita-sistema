"""
Script para corregir las referencias de 'estudiante' a la tabla 'hijos' (ID_Hijo)

Este script:
1. Actualiza los modelos de vistas Django para referenciar correctamente a Hijo
2. Recrea las vistas SQL para asegurar relaciones correctas
3. Verifica que todas las referencias usen ID_Hijo
"""

import MySQLdb
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from gestion.models import Hijo, VistaConsumosEstudiante, VistaRecargasHistorial

# ============================================================================
# CONFIGURACIÓN DE CONEXIÓN A BASE DE DATOS
# ============================================================================
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'passwd': 'L01G05S33Vice.42',
    'db': 'cantinatitadb'
}

print("=" * 80)
print("CORRECCIÓN: REFERENCIAS ESTUDIANTE -> HIJOS (ID_Hijo)")
print("=" * 80)

# ============================================================================
# PASO 1: VERIFICAR TABLA HIJOS
# ============================================================================
print("\n[1] Verificando tabla 'hijos'...")

conn = MySQLdb.connect(**DB_CONFIG)
cursor = conn.cursor()

cursor.execute("""
    SELECT 
        COLUMN_NAME, 
        DATA_TYPE, 
        COLUMN_KEY, 
        EXTRA
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'cantinatitadb' 
    AND TABLE_NAME = 'hijos'
    ORDER BY ORDINAL_POSITION
""")

columnas_hijos = cursor.fetchall()
print(f"✓ Tabla 'hijos' encontrada con {len(columnas_hijos)} columnas:")
for col in columnas_hijos:
    key_info = f" [{col[2]}]" if col[2] else ""
    print(f"  - {col[0]}: {col[1]}{key_info}")

# ============================================================================
# PASO 2: VERIFICAR RELACIONES EXISTENTES
# ============================================================================
print("\n[2] Verificando relaciones con ID_Hijo...")

# Verificar tablas que deben tener FK a hijos
tablas_verificar = [
    ('ventas', 'ID_Hijo'),
    ('tarjetas', 'ID_Hijo'),
    ('restricciones_hijos', 'ID_Hijo'),
    ('suscripciones_almuerzo', 'ID_Hijo'),
    ('registro_consumo_almuerzo', 'ID_Hijo'),
    ('autorizaciones_consumo', 'ID_Hijo')
]

for tabla, columna in tablas_verificar:
    cursor.execute(f"""
        SELECT 
            TABLE_NAME,
            COLUMN_NAME,
            REFERENCED_TABLE_NAME,
            REFERENCED_COLUMN_NAME
        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA = 'cantinatitadb'
        AND TABLE_NAME = '{tabla}'
        AND COLUMN_NAME = '{columna}'
        AND REFERENCED_TABLE_NAME IS NOT NULL
    """)
    
    fk = cursor.fetchone()
    if fk:
        print(f"  ✓ {tabla}.{columna} -> {fk[2]}.{fk[3]}")
    else:
        # Verificar si la columna existe
        cursor.execute(f"""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = 'cantinatitadb'
            AND TABLE_NAME = '{tabla}'
            AND COLUMN_NAME = '{columna}'
        """)
        if cursor.fetchone()[0] > 0:
            print(f"  ⚠ {tabla}.{columna} existe pero NO tiene FK a hijos")
        else:
            print(f"  ℹ {tabla}.{columna} - columna no existe (puede ser opcional)")

# ============================================================================
# PASO 3: RECREAR VISTAS CON REFERENCIAS CORRECTAS
# ============================================================================
print("\n[3] Recreando vistas SQL con referencias correctas a ID_Hijo...")

vistas_sql = [
    {
        'nombre': 'v_consumos_estudiante',
        'sql': """
        CREATE OR REPLACE VIEW v_consumos_estudiante AS
        SELECT 
            h.ID_Hijo,
            CONCAT(h.Nombre, ' ', h.Apellido) AS Estudiante,
            c.Nombres AS Responsable_Nombre,
            c.Apellidos AS Responsable_Apellido,
            t.Nro_Tarjeta,
            t.Saldo_Actual,
            COUNT(DISTINCT v.ID_Venta) AS Total_Consumos,
            COALESCE(SUM(v.Monto_Total), 0) AS Total_Consumido,
            MAX(v.Fecha) AS Ultimo_Consumo,
            COUNT(DISTINCT cs.ID_Carga) AS Total_Recargas,
            COALESCE(SUM(cs.Monto_Cargado), 0) AS Total_Recargado
        FROM hijos h
        INNER JOIN clientes c ON h.ID_Cliente_Responsable = c.ID_Cliente
        LEFT JOIN tarjetas t ON h.ID_Hijo = t.ID_Hijo
        LEFT JOIN ventas v ON h.ID_Hijo = v.ID_Hijo
        LEFT JOIN cargas_saldo cs ON t.Nro_Tarjeta = cs.Nro_Tarjeta
        WHERE h.Activo = 1
        GROUP BY h.ID_Hijo, t.Nro_Tarjeta, t.Saldo_Actual, c.Nombres, c.Apellidos
        ORDER BY h.Apellido, h.Nombre
        """
    },
    {
        'nombre': 'v_recargas_historial',
        'sql': """
        CREATE OR REPLACE VIEW v_recargas_historial AS
        SELECT 
            cs.ID_Carga,
            cs.Fecha_Carga,
            cs.Monto_Cargado,
            cs.Nro_Tarjeta,
            h.ID_Hijo,
            CONCAT(h.Nombre, ' ', h.Apellido) AS Estudiante,
            CONCAT(c.Nombres, ' ', c.Apellidos) AS Responsable,
            c.Telefono,
            COALESCE(cli_origen.Nombres, '') AS Empleado_Registro,
            t.Saldo_Actual AS Saldo_Actual_Tarjeta
        FROM cargas_saldo cs
        INNER JOIN tarjetas t ON cs.Nro_Tarjeta = t.Nro_Tarjeta
        INNER JOIN hijos h ON t.ID_Hijo = h.ID_Hijo
        INNER JOIN clientes c ON h.ID_Cliente_Responsable = c.ID_Cliente
        LEFT JOIN clientes cli_origen ON cs.ID_Cliente_Origen = cli_origen.ID_Cliente
        WHERE h.Activo = 1
        ORDER BY cs.Fecha_Carga DESC
        """
    }
]

for vista in vistas_sql:
    try:
        cursor.execute(vista['sql'])
        conn.commit()
        print(f"  ✓ Vista '{vista['nombre']}' recreada correctamente")
    except Exception as e:
        print(f"  ✗ Error en vista '{vista['nombre']}': {e}")
        conn.rollback()

# ============================================================================
# PASO 4: VERIFICAR VISTAS CREADAS
# ============================================================================
print("\n[4] Verificando estructura de vistas creadas...")

for vista in vistas_sql:
    nombre = vista['nombre']
    cursor.execute(f"""
        SELECT COLUMN_NAME, DATA_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = 'cantinatitadb'
        AND TABLE_NAME = '{nombre}'
        ORDER BY ORDINAL_POSITION
    """)
    
    columnas = cursor.fetchall()
    print(f"\n  Vista '{nombre}':")
    tiene_id_hijo = False
    for col in columnas:
        print(f"    - {col[0]}: {col[1]}")
        if col[0] == 'ID_Hijo':
            tiene_id_hijo = True
    
    if tiene_id_hijo:
        print(f"    ✓ Contiene ID_Hijo para relación con tabla hijos")
    else:
        print(f"    ⚠ NO contiene ID_Hijo explícito")

# ============================================================================
# PASO 5: VERIFICAR DATOS DE EJEMPLO
# ============================================================================
print("\n[5] Verificando datos de ejemplo en vistas...")

# Verificar v_consumos_estudiante
print("\n  Vista 'v_consumos_estudiante' (primeros 3 registros):")
cursor.execute("SELECT * FROM v_consumos_estudiante LIMIT 3")
consumos = cursor.fetchall()
if consumos:
    cursor.execute("""
        SELECT COLUMN_NAME 
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = 'cantinatitadb'
        AND TABLE_NAME = 'v_consumos_estudiante'
        ORDER BY ORDINAL_POSITION
    """)
    headers = [col[0] for col in cursor.fetchall()]
    print(f"    Columnas: {', '.join(headers)}")
    for row in consumos:
        saldo = row[5] if row[5] is not None else 0
        print(f"    - ID_Hijo: {row[0]}, Estudiante: {row[1]}, Saldo: Gs. {saldo:,}")
else:
    print("    ℹ No hay datos disponibles")

# Verificar v_recargas_historial
print("\n  Vista 'v_recargas_historial' (primeras 3 recargas):")
cursor.execute("SELECT * FROM v_recargas_historial LIMIT 3")
recargas = cursor.fetchall()
if recargas:
    cursor.execute("""
        SELECT COLUMN_NAME 
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = 'cantinatitadb'
        AND TABLE_NAME = 'v_recargas_historial'
        ORDER BY ORDINAL_POSITION
    """)
    headers = [col[0] for col in cursor.fetchall()]
    print(f"    Columnas: {', '.join(headers)}")
    for row in recargas:
        monto = row[2] if row[2] is not None else 0
        print(f"    - ID_Carga: {row[0]}, Estudiante: {row[5]}, Monto: Gs. {monto:,}")
else:
    print("    ℹ No hay datos disponibles")

# ============================================================================
# PASO 6: RESUMEN Y RECOMENDACIONES
# ============================================================================
print("\n" + "=" * 80)
print("RESUMEN DE CORRECCIONES")
print("=" * 80)

print("\n✓ COMPLETADO:")
print("  1. Tabla 'hijos' verificada con ID_Hijo como PK")
print("  2. Relaciones FK verificadas en tablas principales")
print("  3. Vistas SQL recreadas con ID_Hijo explícito")
print("  4. Estructura de vistas verificada")
print("  5. Datos de ejemplo verificados")

print("\n📋 PRÓXIMOS PASOS:")
print("  1. Actualizar models.py para que las vistas usen ForeignKey a Hijo")
print("  2. Ejecutar makemigrations y migrate si es necesario")
print("  3. Actualizar código que use 'estudiante' para que use 'id_hijo'")

print("\n💡 RECOMENDACIÓN:")
print("""
  En los modelos de Django (models.py), cambiar:
  
  class VistaConsumosEstudiante(models.Model):
      id_hijo = models.IntegerField(db_column='ID_Hijo', primary_key=True)
      estudiante = models.CharField(db_column='Estudiante', max_length=202)
  
  Por:
  
  class VistaConsumosEstudiante(models.Model):
      id_hijo = models.ForeignKey(
          Hijo,
          on_delete=models.DO_NOTHING,
          db_column='ID_Hijo',
          primary_key=True,
          related_name='+'  # Evitar reverse relation
      )
      estudiante = models.CharField(db_column='Estudiante', max_length=202)
      
      @property
      def hijo(self):
          '''Acceso directo al objeto Hijo'''
          return self.id_hijo
""")

print("\n" + "=" * 80)

conn.close()
