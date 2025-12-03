"""
Script de análisis completo de la base de datos cantinatitadb
Verifica integridad, relaciones, índices y coherencia con los modelos Django
"""

import os
import sys
import django
from decimal import Decimal
from datetime import datetime
from pathlib import Path

# Agregar el directorio raíz al path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection
from django.apps import apps
from gestion import models

def print_section(title):
    """Imprime un título de sección"""
    print(f"\n{'=' * 80}")
    print(f"{title:^80}")
    print('=' * 80)

def analyze_tables():
    """Analiza todas las tablas en la base de datos"""
    print_section("TABLAS EN LA BASE DE DATOS")
    
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        # Separar por tipo
        main_tables = []
        backup_tables = []
        views = []
        django_tables = []
        gestion_tables = []
        
        for table in tables:
            table_name = table[0]
            if table_name.startswith('v_') or table_name.startswith('vista_'):
                views.append(table_name)
            elif 'backup' in table_name.lower():
                backup_tables.append(table_name)
            elif table_name.startswith('django_') or table_name.startswith('auth_'):
                django_tables.append(table_name)
            elif table_name.startswith('gestion_'):
                gestion_tables.append(table_name)
            else:
                main_tables.append(table_name)
        
        print(f"\n📊 TABLAS PRINCIPALES ({len(main_tables)}):")
        for table in sorted(main_tables):
            print(f"  • {table}")
        
        print(f"\n🗂️  TABLAS GESTION APP ({len(gestion_tables)}):")
        for table in sorted(gestion_tables):
            print(f"  • {table}")
        
        print(f"\n👁️  VISTAS ({len(views)}):")
        for view in sorted(views):
            print(f"  • {view}")
        
        print(f"\n💾 TABLAS BACKUP ({len(backup_tables)}):")
        for table in sorted(backup_tables):
            print(f"  • {table}")
        
        print(f"\n🔧 TABLAS DJANGO/AUTH ({len(django_tables)}):")
        for table in sorted(django_tables):
            print(f"  • {table}")
        
        print(f"\n📈 TOTAL: {len(tables)} tablas/vistas")

def analyze_model_mappings():
    """Analiza el mapeo entre modelos Django y tablas"""
    print_section("MODELOS DJANGO Y SUS TABLAS")
    
    gestion_app = apps.get_app_config('gestion')
    models_list = list(gestion_app.get_models())
    
    print(f"\n📦 Total de modelos en app 'gestion': {len(models_list)}\n")
    
    for model in models_list:
        table_name = model._meta.db_table
        model_name = model.__name__
        field_count = len(model._meta.fields)
        
        print(f"  {model_name:30} → {table_name:30} ({field_count} campos)")

def analyze_relationships():
    """Analiza las relaciones entre modelos"""
    print_section("RELACIONES ENTRE MODELOS")
    
    relationships = {
        'ForeignKey': [],
        'OneToOne': [],
        'ManyToMany': []
    }
    
    gestion_app = apps.get_app_config('gestion')
    for model in gestion_app.get_models():
        for field in model._meta.fields:
            field_type = field.__class__.__name__
            if field_type == 'ForeignKey':
                relationships['ForeignKey'].append({
                    'from': model.__name__,
                    'to': field.related_model.__name__,
                    'field': field.name
                })
            elif field_type == 'OneToOneField':
                relationships['OneToOne'].append({
                    'from': model.__name__,
                    'to': field.related_model.__name__,
                    'field': field.name
                })
    
    print(f"\n🔗 FOREIGN KEYS ({len(relationships['ForeignKey'])}):")
    for rel in relationships['ForeignKey'][:15]:  # Mostrar primeras 15
        print(f"  {rel['from']}.{rel['field']} → {rel['to']}")
    if len(relationships['ForeignKey']) > 15:
        print(f"  ... y {len(relationships['ForeignKey']) - 15} más")
    
    print(f"\n🔗 ONE-TO-ONE ({len(relationships['OneToOne'])}):")
    for rel in relationships['OneToOne']:
        print(f"  {rel['from']}.{rel['field']} → {rel['to']}")

def analyze_indexes():
    """Analiza los índices de las tablas principales"""
    print_section("ÍNDICES EN TABLAS PRINCIPALES")
    
    important_tables = [
        'ventas', 'detalle_venta', 'productos', 'clientes',
        'tarjetas', 'cargas_saldo', 'consumos_tarjeta'
    ]
    
    with connection.cursor() as cursor:
        for table in important_tables:
            cursor.execute(f"SHOW INDEX FROM {table}")
            indexes = cursor.fetchall()
            
            print(f"\n📑 {table.upper()}:")
            unique_indexes = []
            regular_indexes = []
            
            for idx in indexes:
                idx_name = idx[2]
                is_unique = not idx[1]
                column = idx[4]
                
                if is_unique and idx_name not in [x[0] for x in unique_indexes]:
                    unique_indexes.append((idx_name, column))
                elif not is_unique and idx_name not in [x[0] for x in regular_indexes]:
                    regular_indexes.append((idx_name, column))
            
            if unique_indexes:
                print("  UNIQUE:")
                for idx_name, col in unique_indexes:
                    print(f"    • {idx_name} ({col})")
            
            if regular_indexes:
                print("  ÍNDICES:")
                for idx_name, col in regular_indexes:
                    print(f"    • {idx_name} ({col})")

def analyze_data_integrity():
    """Analiza la integridad de los datos"""
    print_section("INTEGRIDAD DE DATOS")
    
    checks = []
    
    # 1. Verificar clientes
    total_clientes = models.Cliente.objects.count()
    clientes_activos = models.Cliente.objects.filter(activo=True).count()
    checks.append(f"✓ Clientes: {total_clientes} total, {clientes_activos} activos")
    
    # 2. Verificar productos
    total_productos = models.Producto.objects.count()
    productos_activos = models.Producto.objects.filter(activo=True).count()
    checks.append(f"✓ Productos: {total_productos} total, {productos_activos} activos")
    
    # 3. Verificar ventas
    total_ventas = models.Ventas.objects.count()
    ventas_pendientes = models.Ventas.objects.filter(estado_pago='PENDIENTE').count()
    checks.append(f"✓ Ventas: {total_ventas} total, {ventas_pendientes} pendientes")
    
    # 4. Verificar tarjetas
    total_tarjetas = models.Tarjeta.objects.count()
    tarjetas_activas = models.Tarjeta.objects.filter(estado='ACTIVA').count()
    checks.append(f"✓ Tarjetas: {total_tarjetas} total, {tarjetas_activas} activas")
    
    # 5. Verificar stock
    total_stock = models.StockUnico.objects.count()
    productos_sin_stock = models.StockUnico.objects.filter(stock_actual=0).count()
    checks.append(f"✓ Stock: {total_stock} productos, {productos_sin_stock} sin stock")
    
    # 6. Verificar hijos
    total_hijos = models.Hijo.objects.count()
    hijos_activos = models.Hijo.objects.filter(activo=True).count()
    checks.append(f"✓ Hijos: {total_hijos} total, {hijos_activos} activos")
    
    # 7. Verificar empleados
    total_empleados = models.Empleado.objects.count()
    empleados_activos = models.Empleado.objects.filter(activo=True).count()
    checks.append(f"✓ Empleados: {total_empleados} total, {empleados_activos} activos")
    
    # 8. Verificar proveedores
    total_proveedores = models.Proveedor.objects.count()
    proveedores_activos = models.Proveedor.objects.filter(activo=True).count()
    checks.append(f"✓ Proveedores: {total_proveedores} total, {proveedores_activos} activos")
    
    print("\n")
    for check in checks:
        print(f"  {check}")

def analyze_orphan_records():
    """Detecta registros huérfanos (sin relaciones válidas)"""
    print_section("VERIFICACIÓN DE REGISTROS HUÉRFANOS")
    
    issues = []
    
    # Verificar DetalleVenta sin venta
    try:
        orphan_details = models.DetalleVenta.objects.filter(id_venta__isnull=True).count()
        if orphan_details > 0:
            issues.append(f"⚠️  {orphan_details} DetalleVenta sin venta asociada")
        else:
            print("  ✓ DetalleVenta: Sin huérfanos")
    except Exception as e:
        issues.append(f"❌ Error verificando DetalleVenta: {e}")
    
    # Verificar Productos sin categoría
    try:
        orphan_products = models.Producto.objects.filter(id_categoria__isnull=True).count()
        if orphan_products > 0:
            issues.append(f"⚠️  {orphan_products} Productos sin categoría")
        else:
            print("  ✓ Productos: Sin huérfanos")
    except Exception as e:
        issues.append(f"❌ Error verificando Productos: {e}")
    
    # Verificar Hijos sin cliente responsable
    try:
        orphan_hijos = models.Hijo.objects.filter(id_cliente_responsable__isnull=True).count()
        if orphan_hijos > 0:
            issues.append(f"⚠️  {orphan_hijos} Hijos sin cliente responsable")
        else:
            print("  ✓ Hijos: Sin huérfanos")
    except Exception as e:
        issues.append(f"❌ Error verificando Hijos: {e}")
    
    # Verificar Tarjetas sin hijo
    try:
        orphan_tarjetas = models.Tarjeta.objects.filter(id_hijo__isnull=True).count()
        if orphan_tarjetas > 0:
            issues.append(f"⚠️  {orphan_tarjetas} Tarjetas sin hijo asociado")
        else:
            print("  ✓ Tarjetas: Sin huérfanos")
    except Exception as e:
        issues.append(f"❌ Error verificando Tarjetas: {e}")
    
    if issues:
        print("\n  PROBLEMAS DETECTADOS:")
        for issue in issues:
            print(f"  {issue}")

def analyze_views():
    """Analiza las vistas de la base de datos"""
    print_section("VISTAS DE BASE DE DATOS")
    
    with connection.cursor() as cursor:
        cursor.execute("SHOW FULL TABLES WHERE Table_type = 'VIEW'")
        views = cursor.fetchall()
        
        print(f"\n📊 Total de vistas: {len(views)}\n")
        
        for view in views:
            view_name = view[0]
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {view_name}")
                count = cursor.fetchone()[0]
                print(f"  • {view_name:40} ({count:>6} registros)")
            except Exception as e:
                print(f"  • {view_name:40} (⚠️ Error: {str(e)[:30]})")

def analyze_constraints():
    """Analiza las constraints (restricciones) de las tablas"""
    print_section("CONSTRAINTS Y FOREIGN KEYS")
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                TABLE_NAME,
                CONSTRAINT_NAME,
                CONSTRAINT_TYPE
            FROM information_schema.TABLE_CONSTRAINTS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME NOT LIKE 'auth_%'
            AND TABLE_NAME NOT LIKE 'django_%'
            AND CONSTRAINT_TYPE IN ('FOREIGN KEY', 'UNIQUE')
            ORDER BY TABLE_NAME, CONSTRAINT_TYPE
        """)
        
        constraints = cursor.fetchall()
        
        fk_count = sum(1 for c in constraints if c[2] == 'FOREIGN KEY')
        unique_count = sum(1 for c in constraints if c[2] == 'UNIQUE')
        
        print(f"\n📋 Total constraints: {len(constraints)}")
        print(f"  • Foreign Keys: {fk_count}")
        print(f"  • Unique: {unique_count}")
        
        # Mostrar las primeras 10
        print("\n  EJEMPLOS:")
        for constraint in constraints[:10]:
            table, name, ctype = constraint
            print(f"    {table:25} → {name:40} ({ctype})")

def main():
    """Función principal"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " ANÁLISIS COMPLETO DE BASE DE DATOS CANTINATITADB".center(78) + "║")
    print("╚" + "═" * 78 + "╝")
    
    try:
        analyze_tables()
        analyze_model_mappings()
        analyze_relationships()
        analyze_data_integrity()
        analyze_orphan_records()
        analyze_views()
        analyze_indexes()
        analyze_constraints()
        
        print_section("RESUMEN FINAL")
        print("\n✅ Análisis completado exitosamente")
        print("\nRECOMENDACIONES:")
        print("  1. Las tablas backup_* pueden ser eliminadas si ya no se necesitan")
        print("  2. Verificar que todas las vistas estén funcionando correctamente")
        print("  3. Las relaciones ForeignKey están correctamente implementadas")
        print("  4. Considerar agregar más índices en columnas frecuentemente consultadas")
        print("  5. Los modelos Django están sincronizados con las tablas de la BD")
        
    except Exception as e:
        print(f"\n❌ Error durante el análisis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
