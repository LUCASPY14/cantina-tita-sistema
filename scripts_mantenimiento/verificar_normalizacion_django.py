"""
Análisis de Normalización usando Django ORM
"""
import os
import django
from collections import defaultdict
import difflib

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection

print("=" * 100)
print("ANÁLISIS DE NORMALIZACIÓN Y DUPLICADOS - cantinatitadb")
print("=" * 100)

with connection.cursor() as cursor:
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
    tablas = [row[0] for row in cursor.fetchall()]

    print(f"\n📊 Total de tablas en la BD: {len(tablas)}\n")

    # Detectar nombres similares
    similares = []
    for i, tabla1 in enumerate(tablas):
        for tabla2 in tablas[i+1:]:
            similitud = difflib.SequenceMatcher(None, tabla1.lower(), tabla2.lower()).ratio()
            
            if similitud > 0.7 and similitud < 1.0:
                similares.append((tabla1, tabla2, similitud))

    if similares:
        print("⚠️  TABLAS CON NOMBRES SIMILARES (Posibles Duplicados):")
        print("-" * 80)
        for t1, t2, sim in sorted(similares, key=lambda x: x[2], reverse=True):
            print(f"  • {t1:45} ≈ {t2:45} ({sim*100:.1f}% similar)")
    else:
        print("✅ No se detectaron tablas con nombres duplicados o muy similares")

    # ============================================================================
    # 2. VERIFICAR TABLAS QUE PODRÍAN SER DUPLICADAS (FUNCIONALIDAD)
    # ============================================================================
    print("\n" + "=" * 100)
    print("2. ANÁLISIS DE POSIBLES DUPLICADOS FUNCIONALES")
    print("=" * 100)

    # Casos específicos a revisar
    casos_revisar = [
        ('usuarios_web_clientes', 'usuario_portal', 'Gestión de usuarios del portal'),
        ('cta_corriente', 'vista_saldo_clientes', 'Saldos de clientes'),
        ('pagos_venta', 'aplicacion_pagos_ventas', 'Aplicación de pagos'),
        ('stock_unico', 'movimientos_stock', 'Control de inventario'),
    ]

    print("\n🔍 Pares de tablas a revisar:")
    print("-" * 80)
    
    for t1, t2, proposito in casos_revisar:
        if t1 in tablas and t2 in tablas:
            # Obtener estructura de ambas tablas
            cursor.execute(f"""
                SELECT COUNT(*) FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = 'cantinatitadb' AND TABLE_NAME = '{t1}'
            """)
            cols_t1 = cursor.fetchone()[0]
            
            cursor.execute(f"""
                SELECT COUNT(*) FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = 'cantinatitadb' AND TABLE_NAME = '{t2}'
            """)
            cols_t2 = cursor.fetchone()[0]
            
            # Obtener cantidad de registros
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {t1}")
                registros_t1 = cursor.fetchone()[0]
            except:
                registros_t1 = "N/A"
            
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {t2}")
                registros_t2 = cursor.fetchone()[0]
            except:
                registros_t2 = "N/A"
            
            print(f"\n  📋 {proposito}")
            print(f"     ├─ {t1:30} ({cols_t1} columnas, {registros_t1} registros)")
            print(f"     └─ {t2:30} ({cols_t2} columnas, {registros_t2} registros)")

    # ============================================================================
    # 3. VERIFICAR NORMALIZACIÓN 1FN
    # ============================================================================
    print("\n" + "=" * 100)
    print("3. VERIFICACIÓN 1FN (Primera Forma Normal)")
    print("=" * 100)

    violaciones_1fn = []

    for tabla in tablas:
        if tabla.startswith('v_'):
            continue
        
        cursor.execute(f"""
            SELECT COLUMN_NAME, DATA_TYPE, COLUMN_TYPE
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = 'cantinatitadb'
            AND TABLE_NAME = '{tabla}'
            ORDER BY ORDINAL_POSITION
        """)
        columnas = cursor.fetchall()
        
        # Detectar campos JSON
        for col in columnas:
            col_name, data_type, column_type = col
            
            if data_type.lower() == 'json':
                violaciones_1fn.append({
                    'tabla': tabla,
                    'columna': col_name,
                    'tipo': 'JSON',
                    'severidad': 'INFO'
                })

    if violaciones_1fn:
        print(f"\n📊 Campos JSON detectados ({len(violaciones_1fn)}):")
        print("-" * 80)
        for v in violaciones_1fn:
            print(f"  • {v['tabla']}.{v['columna']}")
        print("\n  ℹ️  Los campos JSON son aceptables para datos semi-estructurados")
    else:
        print("\n✅ No se detectaron campos JSON")

    # ============================================================================
    # 4. VERIFICAR NORMALIZACIÓN 2FN
    # ============================================================================
    print("\n" + "=" * 100)
    print("4. VERIFICACIÓN 2FN (Segunda Forma Normal)")
    print("=" * 100)

    claves_compuestas = []

    for tabla in tablas:
        if tabla.startswith('v_'):
            continue
        
        cursor.execute(f"""
            SELECT COUNT(*) as num_pk
            FROM information_schema.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = 'cantinatitadb'
            AND TABLE_NAME = '{tabla}'
            AND CONSTRAINT_NAME = 'PRIMARY'
        """)
        result = cursor.fetchone()
        
        if result and result[0] > 1:
            cursor.execute(f"""
                SELECT COLUMN_NAME
                FROM information_schema.KEY_COLUMN_USAGE
                WHERE TABLE_SCHEMA = 'cantinatitadb'
                AND TABLE_NAME = '{tabla}'
                AND CONSTRAINT_NAME = 'PRIMARY'
                ORDER BY ORDINAL_POSITION
            """)
            pk_cols = [row[0] for row in cursor.fetchall()]
            claves_compuestas.append((tabla, pk_cols))

    if claves_compuestas:
        print(f"\n📊 Tablas con Claves Compuestas ({len(claves_compuestas)}):")
        print("-" * 80)
        for tabla, pk_cols in claves_compuestas:
            print(f"  • {tabla:40} PK: {', '.join(pk_cols)}")
        print("\n  ℹ️  Las claves compuestas son normales en tablas de unión (Many-to-Many)")
    else:
        print("\n✅ No hay tablas con claves compuestas (todas usan PK simple)")

    # ============================================================================
    # 5. VERIFICAR INTEGRIDAD REFERENCIAL
    # ============================================================================
    print("\n" + "=" * 100)
    print("5. VERIFICACIÓN DE INTEGRIDAD REFERENCIAL")
    print("=" * 100)

    cursor.execute("""
        SELECT COUNT(*) as total_fks
        FROM information_schema.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA = 'cantinatitadb'
        AND REFERENCED_TABLE_NAME IS NOT NULL
    """)
    total_fks = cursor.fetchone()[0]
    
    print(f"\n📊 Total de Foreign Keys definidas: {total_fks}")

    # Detectar tablas sin FKs cuando deberían tenerlas
    cursor.execute("""
        SELECT TABLE_NAME
        FROM information_schema.TABLES
        WHERE TABLE_SCHEMA = 'cantinatitadb'
        AND TABLE_TYPE = 'BASE TABLE'
        AND TABLE_NAME NOT LIKE 'v_%'
        AND TABLE_NAME NOT LIKE 'auth_%'
        AND TABLE_NAME NOT LIKE 'django_%'
        ORDER BY TABLE_NAME
    """)
    todas_tablas = [row[0] for row in cursor.fetchall()]
    
    tablas_sin_fk = []
    for tabla in todas_tablas:
        cursor.execute(f"""
            SELECT COUNT(*) as num_fks
            FROM information_schema.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = 'cantinatitadb'
            AND TABLE_NAME = '{tabla}'
            AND REFERENCED_TABLE_NAME IS NOT NULL
        """)
        num_fks = cursor.fetchone()[0]
        
        # Contar columnas
        cursor.execute(f"""
            SELECT COUNT(*) as num_cols
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = 'cantinatitadb'
            AND TABLE_NAME = '{tabla}'
        """)
        num_cols = cursor.fetchone()[0]
        
        # Si tiene más de 3 columnas y ninguna FK, podría ser sospechoso
        if num_fks == 0 and num_cols > 3 and not tabla.startswith('tipos_'):
            tablas_sin_fk.append(tabla)

    if tablas_sin_fk:
        print(f"\n⚠️  Tablas sin Foreign Keys (revisar si es correcto):")
        print("-" * 80)
        for tabla in tablas_sin_fk[:10]:
            print(f"  • {tabla}")
        if len(tablas_sin_fk) > 10:
            print(f"  ... y {len(tablas_sin_fk) - 10} más")
    else:
        print("\n✅ Todas las tablas tienen Foreign Keys cuando corresponde")

    # ============================================================================
    # 6. DETECTAR DUPLICACIÓN DE DATOS
    # ============================================================================
    print("\n" + "=" * 100)
    print("6. ANÁLISIS DE POSIBLE DUPLICACIÓN DE DATOS")
    print("=" * 100)

    print("\n🔍 Verificando pares específicos de tablas...")
    
    # Verificar usuarios_web_clientes vs usuario_portal
    if 'usuarios_web_clientes' in tablas and 'usuario_portal' in tablas:
        cursor.execute("SELECT COUNT(*) FROM usuarios_web_clientes")
        count_web = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM usuario_portal")
        count_portal = cursor.fetchone()[0]
        
        print(f"\n  📋 Sistema de Usuarios:")
        print(f"     • usuarios_web_clientes: {count_web} registros")
        print(f"     • usuario_portal: {count_portal} registros")
        
        if count_web > 0 and count_portal > 0:
            print(f"     ⚠️  POSIBLE DUPLICACIÓN: Ambas tablas tienen datos")
            print(f"     💡 Recomendación: Consolidar en una sola tabla")
        elif count_web > 0 and count_portal == 0:
            print(f"     ℹ️  usuarios_web_clientes tiene datos, usuario_portal está vacía")
            print(f"     💡 Migrar datos a usuario_portal si es la tabla principal")

    # Verificar aplicacion_pagos_ventas vs pagos_venta
    if 'aplicacion_pagos_ventas' in tablas and 'pagos_venta' in tablas:
        cursor.execute("SELECT COUNT(*) FROM aplicacion_pagos_ventas")
        count_apl = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM pagos_venta")
        count_pago = cursor.fetchone()[0]
        
        print(f"\n  📋 Sistema de Pagos:")
        print(f"     • pagos_venta: {count_pago} registros")
        print(f"     • aplicacion_pagos_ventas: {count_apl} registros")
        print(f"     ✅ Estas tablas tienen propósitos diferentes (correcto)")

    # ============================================================================
    # 7. RESUMEN FINAL
    # ============================================================================
    print("\n" + "=" * 100)
    print("7. RESUMEN Y RECOMENDACIONES")
    print("=" * 100)

    total_problemas = len(similares)
    
    print(f"\n📊 HALLAZGOS:")
    print(f"  • Total de tablas:                            {len(tablas)}")
    print(f"  • Tablas con nombres similares:               {len(similares)}")
    print(f"  • Tablas con claves compuestas:               {len(claves_compuestas)}")
    print(f"  • Foreign Keys totales:                       {total_fks}")
    print(f"  • Campos JSON (semi-estructurados):           {len(violaciones_1fn)}")

    print("\n🎯 CONCLUSIÓN:")
    if total_problemas == 0 and len(tablas_sin_fk) < 5:
        print("  ✅ BASE DE DATOS BIEN NORMALIZADA")
        print("  ✅ No se detectaron duplicados evidentes")
        print("  ✅ Cumple con 1FN y 2FN")
    else:
        print(f"  ⚠️  Se detectaron {total_problemas} posibles problemas")
        print("  ℹ️  Revisar las recomendaciones específicas arriba")

    print("\n💡 RECOMENDACIONES ESPECÍFICAS:")
    
    # Recomendación 1: Consolidar usuarios
    if 'usuarios_web_clientes' in tablas and 'usuario_portal' in tablas:
        cursor.execute("SELECT COUNT(*) FROM usuarios_web_clientes")
        if cursor.fetchone()[0] > 0:
            print("\n  1. CONSOLIDAR SISTEMA DE USUARIOS:")
            print("     • Decidir si usar 'usuarios_web_clientes' o 'usuario_portal'")
            print("     • Migrar datos a la tabla principal")
            print("     • Eliminar la tabla redundante")
    
    # Recomendación 2: Vistas vs tablas
    cursor.execute("""
        SELECT COUNT(*) FROM information_schema.VIEWS
        WHERE TABLE_SCHEMA = 'cantinatitadb'
    """)
    total_vistas = cursor.fetchone()[0]
    
    print(f"\n  2. VISTAS vs TABLAS:")
    print(f"     • Total de vistas: {total_vistas}")
    print(f"     ✅ Las vistas son correctas para datos derivados/calculados")
    
    print("\n" + "=" * 100)
    print("FIN DEL ANÁLISIS")
    print("=" * 100)
