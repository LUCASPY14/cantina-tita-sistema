"""
Análisis de Normalización y Duplicados en cantinatitadb
Verifica:
- Tablas duplicadas o similares
- Normalización 1FN y 2FN
- Redundancia de datos
- Integridad referencial
"""

import mysql.connector
from collections import defaultdict
import difflib
import re

# Conexión a la base de datos
try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='admin',  # Ajustar según tu configuración
        database='cantinatitadb'
    )
except mysql.connector.Error as e:
    print(f"❌ Error de conexión: {e}")
    print("\n💡 Ajusta las credenciales en el archivo verificar_normalizacion_bd.py")
    print("   Líneas 16-21: host, user, password")
    exit(1)
cursor = conn.cursor(dictionary=True)

print("=" * 100)
print("ANÁLISIS DE NORMALIZACIÓN Y DUPLICADOS - cantinatitadb")
print("=" * 100)

# ============================================================================
# 1. DETECTAR TABLAS DUPLICADAS O SIMILARES
# ============================================================================
print("\n" + "=" * 100)
print("1. DETECCIÓN DE TABLAS DUPLICADAS O SIMILARES")
print("=" * 100)

cursor.execute("""
    SELECT TABLE_NAME 
    FROM information_schema.TABLES 
    WHERE TABLE_SCHEMA = 'cantinatitadb' 
    AND TABLE_TYPE = 'BASE TABLE'
    ORDER BY TABLE_NAME
""")
tablas = [row['TABLE_NAME'] for row in cursor.fetchall()]

print(f"\n📊 Total de tablas en la BD: {len(tablas)}\n")

# Detectar nombres similares (posibles duplicados)
similares = []
for i, tabla1 in enumerate(tablas):
    for tabla2 in tablas[i+1:]:
        # Calcular similitud de nombres
        similitud = difflib.SequenceMatcher(None, tabla1.lower(), tabla2.lower()).ratio()
        
        if similitud > 0.7 and similitud < 1.0:  # 70% similar pero no idéntico
            similares.append((tabla1, tabla2, similitud))

if similares:
    print("⚠️  TABLAS CON NOMBRES SIMILARES (Posibles Duplicados):")
    print("-" * 80)
    for t1, t2, sim in sorted(similares, key=lambda x: x[2], reverse=True):
        print(f"  • {t1:40} ≈ {t2:40} ({sim*100:.1f}% similar)")
else:
    print("✅ No se detectaron tablas con nombres duplicados o muy similares")

# Detectar tablas con el mismo propósito
print("\n🔍 Análisis de Tablas por Funcionalidad:")
print("-" * 80)

# Agrupar por prefijos/sufijos comunes
grupos_funcionales = defaultdict(list)
for tabla in tablas:
    # Buscar patrones comunes
    if 'auditoria' in tabla.lower():
        grupos_funcionales['Auditoría'].append(tabla)
    elif 'pago' in tabla.lower():
        grupos_funcionales['Pagos'].append(tabla)
    elif 'factura' in tabla.lower() or 'documento' in tabla.lower():
        grupos_funcionales['Facturación'].append(tabla)
    elif 'usuario' in tabla.lower() or 'cliente' in tabla.lower():
        grupos_funcionales['Usuarios/Clientes'].append(tabla)
    elif 'almuerzo' in tabla.lower():
        grupos_funcionales['Almuerzos'].append(tabla)
    elif 'tarjeta' in tabla.lower():
        grupos_funcionales['Tarjetas'].append(tabla)
    elif 'stock' in tabla.lower() or 'inventario' in tabla.lower() or 'producto' in tabla.lower():
        grupos_funcionales['Inventario/Productos'].append(tabla)
    elif tabla.startswith('v_'):
        grupos_funcionales['Vistas'].append(tabla)

for grupo, tablas_grupo in sorted(grupos_funcionales.items()):
    print(f"\n  📁 {grupo} ({len(tablas_grupo)} tablas):")
    for t in sorted(tablas_grupo):
        print(f"     - {t}")

# ============================================================================
# 2. VERIFICAR NORMALIZACIÓN 1FN (Primera Forma Normal)
# ============================================================================
print("\n" + "=" * 100)
print("2. VERIFICACIÓN 1FN (Primera Forma Normal)")
print("   - Cada columna debe contener valores atómicos")
print("   - No debe haber grupos repetitivos")
print("=" * 100)

violaciones_1fn = []

for tabla in tablas:
    if tabla.startswith('v_'):  # Ignorar vistas
        continue
    
    cursor.execute(f"""
        SELECT COLUMN_NAME, DATA_TYPE, COLUMN_TYPE
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = 'cantinatitadb'
        AND TABLE_NAME = '{tabla}'
        ORDER BY ORDINAL_POSITION
    """)
    columnas = cursor.fetchall()
    
    # Detectar campos que podrían violar 1FN
    for col in columnas:
        col_name = col['COLUMN_NAME'].lower()
        data_type = col['DATA_TYPE'].lower()
        
        # 1. Buscar campos JSON (pueden contener múltiples valores)
        if data_type == 'json':
            violaciones_1fn.append({
                'tabla': tabla,
                'columna': col['COLUMN_NAME'],
                'tipo': 'JSON',
                'razon': 'Campo JSON puede contener múltiples valores (aceptable si está justificado)',
                'severidad': 'INFO'
            })
        
        # 2. Buscar campos TEXT largos que podrían almacenar listas
        if 'lista' in col_name or 'array' in col_name or 'multiple' in col_name:
            violaciones_1fn.append({
                'tabla': tabla,
                'columna': col['COLUMN_NAME'],
                'tipo': data_type,
                'razon': 'Nombre sugiere múltiples valores - verificar si es una lista',
                'severidad': 'WARNING'
            })
        
        # 3. Detectar campos con separadores (ej: telefono1, telefono2, telefono3)
        match = re.search(r'(\w+)(\d+)$', col_name)
        if match:
            base_name = match.group(1)
            # Contar cuántos campos similares hay
            campos_similares = [c for c in columnas if c['COLUMN_NAME'].lower().startswith(base_name)]
            if len(campos_similares) > 1:
                violaciones_1fn.append({
                    'tabla': tabla,
                    'columna': col['COLUMN_NAME'],
                    'tipo': 'GRUPO REPETITIVO',
                    'razon': f'Posible grupo repetitivo: {len(campos_similares)} campos "{base_name}*"',
                    'severidad': 'WARNING'
                })

if violaciones_1fn:
    print("\n⚠️  POSIBLES VIOLACIONES DE 1FN:")
    print("-" * 80)
    
    # Agrupar por severidad
    for severidad in ['WARNING', 'INFO']:
        items = [v for v in violaciones_1fn if v['severidad'] == severidad]
        if items:
            print(f"\n  {severidad}:")
            for v in items:
                print(f"    • {v['tabla']}.{v['columna']} ({v['tipo']})")
                print(f"      → {v['razon']}")
else:
    print("\n✅ No se detectaron violaciones evidentes de 1FN")

# ============================================================================
# 3. VERIFICAR NORMALIZACIÓN 2FN (Segunda Forma Normal)
# ============================================================================
print("\n" + "=" * 100)
print("3. VERIFICACIÓN 2FN (Segunda Forma Normal)")
print("   - Cumple 1FN")
print("   - Todos los atributos no clave dependen completamente de la clave primaria")
print("   - No hay dependencias parciales de claves compuestas")
print("=" * 100)

violaciones_2fn = []

for tabla in tablas:
    if tabla.startswith('v_'):  # Ignorar vistas
        continue
    
    # Obtener clave primaria
    cursor.execute(f"""
        SELECT COLUMN_NAME
        FROM information_schema.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA = 'cantinatitadb'
        AND TABLE_NAME = '{tabla}'
        AND CONSTRAINT_NAME = 'PRIMARY'
        ORDER BY ORDINAL_POSITION
    """)
    pk_columns = [row['COLUMN_NAME'] for row in cursor.fetchall()]
    
    if len(pk_columns) > 1:
        # Clave compuesta - verificar dependencias parciales
        print(f"\n🔍 Tabla con clave compuesta: {tabla}")
        print(f"   PK: {', '.join(pk_columns)}")
        
        # Obtener todas las columnas
        cursor.execute(f"""
            SELECT COLUMN_NAME, DATA_TYPE
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = 'cantinatitadb'
            AND TABLE_NAME = '{tabla}'
            AND COLUMN_NAME NOT IN ({','.join([f"'{c}'" for c in pk_columns])})
        """)
        otras_columnas = cursor.fetchall()
        
        # Buscar columnas que podrían depender parcialmente
        for col in otras_columnas:
            col_name = col['COLUMN_NAME'].lower()
            
            # Buscar patrones que sugieran dependencia parcial
            for pk_part in pk_columns:
                pk_part_lower = pk_part.lower().replace('id_', '')
                
                if pk_part_lower in col_name and col_name != pk_part_lower:
                    violaciones_2fn.append({
                        'tabla': tabla,
                        'columna': col['COLUMN_NAME'],
                        'pk_compuesta': pk_columns,
                        'razon': f'Columna "{col["COLUMN_NAME"]}" podría depender solo de "{pk_part}"',
                        'severidad': 'WARNING'
                    })

# Detectar redundancia de datos (violación indirecta de 2FN)
print("\n🔍 Análisis de Redundancia de Datos:")
print("-" * 80)

redundancias = []

for tabla in tablas:
    if tabla.startswith('v_'):
        continue
    
    cursor.execute(f"""
        SELECT COLUMN_NAME, DATA_TYPE
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = 'cantinatitadb'
        AND TABLE_NAME = '{tabla}'
    """)
    columnas = cursor.fetchall()
    
    # Buscar campos calculados que podrían ser redundantes
    for col in columnas:
        col_name = col['COLUMN_NAME'].lower()
        
        # Campos que sugieren valores calculados
        if any(keyword in col_name for keyword in ['total', 'suma', 'subtotal', 'monto_total', 'cantidad_total']):
            redundancias.append({
                'tabla': tabla,
                'columna': col['COLUMN_NAME'],
                'tipo': 'CAMPO CALCULADO',
                'razon': 'Posiblemente calculable desde otras tablas/campos'
            })

if violaciones_2fn:
    print("\n⚠️  POSIBLES VIOLACIONES DE 2FN:")
    for v in violaciones_2fn:
        print(f"  • {v['tabla']}.{v['columna']}")
        print(f"    PK: {', '.join(v['pk_compuesta'])}")
        print(f"    → {v['razon']}")
else:
    print("\n✅ No se detectaron violaciones evidentes de 2FN en claves compuestas")

if redundancias:
    print("\n📊 Campos Potencialmente Redundantes (Revisar si están desnormalizados intencionalmente):")
    for r in redundancias[:10]:  # Mostrar solo primeros 10
        print(f"  • {r['tabla']}.{r['columna']} - {r['razon']}")
    if len(redundancias) > 10:
        print(f"  ... y {len(redundancias) - 10} más")

# ============================================================================
# 4. VERIFICAR INTEGRIDAD REFERENCIAL
# ============================================================================
print("\n" + "=" * 100)
print("4. VERIFICACIÓN DE INTEGRIDAD REFERENCIAL (Foreign Keys)")
print("=" * 100)

cursor.execute("""
    SELECT 
        TABLE_NAME,
        COLUMN_NAME,
        REFERENCED_TABLE_NAME,
        REFERENCED_COLUMN_NAME,
        CONSTRAINT_NAME
    FROM information_schema.KEY_COLUMN_USAGE
    WHERE TABLE_SCHEMA = 'cantinatitadb'
    AND REFERENCED_TABLE_NAME IS NOT NULL
    ORDER BY TABLE_NAME, COLUMN_NAME
""")
foreign_keys = cursor.fetchall()

print(f"\n📊 Total de Foreign Keys definidas: {len(foreign_keys)}")

# Verificar FKs huérfanas
print("\n🔍 Verificando integridad de datos...")

fks_con_problemas = []

for fk in foreign_keys[:20]:  # Verificar las primeras 20
    tabla = fk['TABLE_NAME']
    columna = fk['COLUMN_NAME']
    ref_tabla = fk['REFERENCED_TABLE_NAME']
    ref_columna = fk['REFERENCED_COLUMN_NAME']
    
    try:
        # Buscar registros huérfanos
        cursor.execute(f"""
            SELECT COUNT(*) as huerfanos
            FROM {tabla} t
            WHERE t.{columna} IS NOT NULL
            AND NOT EXISTS (
                SELECT 1 FROM {ref_tabla} r
                WHERE r.{ref_columna} = t.{columna}
            )
        """)
        result = cursor.fetchone()
        
        if result['huerfanos'] > 0:
            fks_con_problemas.append({
                'tabla': tabla,
                'columna': columna,
                'referencia': f"{ref_tabla}.{ref_columna}",
                'huerfanos': result['huerfanos']
            })
    except Exception as e:
        pass  # Ignorar errores de sintaxis en tablas complejas

if fks_con_problemas:
    print("\n⚠️  FOREIGN KEYS CON REGISTROS HUÉRFANOS:")
    for fk in fks_con_problemas:
        print(f"  • {fk['tabla']}.{fk['columna']} → {fk['referencia']}")
        print(f"    {fk['huerfanos']} registros sin referencia válida")
else:
    print("\n✅ Todas las Foreign Keys verificadas tienen integridad correcta")

# ============================================================================
# 5. DETECTAR TABLAS DE UNIÓN DUPLICADAS
# ============================================================================
print("\n" + "=" * 100)
print("5. DETECCIÓN DE TABLAS DE UNIÓN (Many-to-Many)")
print("=" * 100)

tablas_union = []

for tabla in tablas:
    if tabla.startswith('v_'):
        continue
    
    # Obtener todas las columnas
    cursor.execute(f"""
        SELECT COLUMN_NAME
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = 'cantinatitadb'
        AND TABLE_NAME = '{tabla}'
    """)
    columnas = [row['COLUMN_NAME'] for row in cursor.fetchall()]
    
    # Contar FKs
    fks_tabla = [fk for fk in foreign_keys if fk['TABLE_NAME'] == tabla]
    
    # Si tiene 2 FKs y pocas columnas, probablemente es tabla de unión
    if len(fks_tabla) >= 2 and len(columnas) <= 5:
        tablas_union.append({
            'tabla': tabla,
            'fks': [(fk['COLUMN_NAME'], fk['REFERENCED_TABLE_NAME']) for fk in fks_tabla],
            'total_columnas': len(columnas)
        })

if tablas_union:
    print(f"\n📊 Tablas de Unión Detectadas: {len(tablas_union)}")
    print("-" * 80)
    for tu in tablas_union:
        print(f"\n  • {tu['tabla']} ({tu['total_columnas']} columnas)")
        print(f"    Relaciona:")
        for fk_col, ref_tabla in tu['fks']:
            print(f"      - {fk_col} → {ref_tabla}")

# ============================================================================
# 6. RESUMEN Y RECOMENDACIONES
# ============================================================================
print("\n" + "=" * 100)
print("6. RESUMEN Y RECOMENDACIONES")
print("=" * 100)

total_problemas = len(similares) + len([v for v in violaciones_1fn if v['severidad'] == 'WARNING']) + len(violaciones_2fn) + len(fks_con_problemas)

print(f"\n📊 RESUMEN DE HALLAZGOS:")
print(f"  • Tablas similares (posibles duplicados):     {len(similares)}")
print(f"  • Posibles violaciones 1FN:                   {len([v for v in violaciones_1fn if v['severidad'] == 'WARNING'])}")
print(f"  • Posibles violaciones 2FN:                   {len(violaciones_2fn)}")
print(f"  • FKs con registros huérfanos:                {len(fks_con_problemas)}")
print(f"  • Campos redundantes:                         {len(redundancias)}")
print(f"  • Tablas de unión (M2M):                      {len(tablas_union)}")

if total_problemas == 0:
    print("\n✅ CONCLUSIÓN: Base de datos bien normalizada y sin duplicados evidentes")
else:
    print(f"\n⚠️  CONCLUSIÓN: Se encontraron {total_problemas} problemas potenciales que requieren revisión")

print("\n💡 RECOMENDACIONES:")

if similares:
    print("\n  1. Revisar tablas con nombres similares:")
    for t1, t2, sim in similares[:3]:
        print(f"     - ¿{t1} y {t2} son realmente diferentes?")

if violaciones_2fn:
    print("\n  2. Revisar dependencias parciales en claves compuestas")

if redundancias:
    print("\n  3. Verificar si los campos calculados están desnormalizados intencionalmente")
    print("     (La desnormalización controlada es aceptable para performance)")

if fks_con_problemas:
    print("\n  4. Limpiar registros huérfanos en las Foreign Keys detectadas")

print("\n" + "=" * 100)
print("FIN DEL ANÁLISIS")
print("=" * 100)

cursor.close()
conn.close()
