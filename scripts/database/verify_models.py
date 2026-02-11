"""
Script para verificar la integridad y accesibilidad de todas las tablas
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from gestion.models_existentes import (
    ClienteExistente, ProductoExistente, StockUnico,
    CategoriaDB, ProveedorDB, Empleado, TipoCliente,
    Hijo, Tarjeta, VistaStockAlerta, VistaSaldoClientes
)

def verificar_modelos():
    """Verifica que todos los modelos puedan acceder a sus tablas"""
    
    print("=" * 80)
    print("🔍 VERIFICACIÓN DE INTEGRIDAD DE MODELOS DJANGO")
    print("=" * 80)
    
    modelos = [
        ('ClienteExistente', ClienteExistente),
        ('ProductoExistente', ProductoExistente),
        ('StockUnico', StockUnico),
        ('CategoríaDB', CategoriaDB),
        ('ProveedorDB', ProveedorDB),
        ('Empleado', Empleado),
        ('TipoCliente', TipoCliente),
        ('Hijo', Hijo),
        ('Tarjeta', Tarjeta),
        ('VistaStockAlerta', VistaStockAlerta),
        ('VistaSaldoClientes', VistaSaldoClientes),
    ]
    
    resultados = []
    
    for nombre, modelo in modelos:
        try:
            # Intentar contar registros
            count = modelo.objects.count()
            
            # Intentar obtener el primer registro
            primer_registro = modelo.objects.first()
            
            resultado = {
                'nombre': nombre,
                'tabla': modelo._meta.db_table,
                'count': count,
                'accesible': True,
                'primer_registro': str(primer_registro) if primer_registro else 'N/A'
            }
            
            print(f"\n✅ {nombre} ({modelo._meta.db_table})")
            print(f"   📊 Registros: {count}")
            if primer_registro:
                print(f"   📝 Ejemplo: {str(primer_registro)[:80]}")
            
        except Exception as e:
            resultado = {
                'nombre': nombre,
                'tabla': modelo._meta.db_table,
                'count': 0,
                'accesible': False,
                'error': str(e)
            }
            
            print(f"\n❌ {nombre} ({modelo._meta.db_table})")
            print(f"   Error: {str(e)}")
        
        resultados.append(resultado)
    
    # Resumen
    print(f"\n\n{'=' * 80}")
    print("📊 RESUMEN DE VERIFICACIÓN")
    print('=' * 80)
    
    accesibles = sum(1 for r in resultados if r['accesible'])
    total = len(resultados)
    
    print(f"\n✅ Modelos accesibles: {accesibles}/{total}")
    print(f"❌ Modelos con error: {total - accesibles}/{total}")
    
    total_registros = sum(r['count'] for r in resultados if r['accesible'])
    print(f"\n📊 Total de registros accesibles: {total_registros:,}")
    
    # Detalle por modelo
    print(f"\n\n{'=' * 80}")
    print("📋 DETALLE POR MODELO")
    print('=' * 80)
    
    for resultado in resultados:
        if resultado['accesible']:
            print(f"\n{resultado['nombre']:25} | {resultado['count']:>8,} registros")
    
    # Verificar relaciones importantes
    print(f"\n\n{'=' * 80}")
    print("🔗 VERIFICACIÓN DE RELACIONES")
    print('=' * 80)
    
    try:
        # Cliente con tarjetas
        clientes_con_hijos = ClienteExistente.objects.filter(hijos__isnull=False).distinct().count()
        print(f"\n✅ Clientes con hijos: {clientes_con_hijos}")
        
        # Productos con stock
        productos_con_stock = ProductoExistente.objects.filter(stock__isnull=False).count()
        print(f"✅ Productos con stock: {productos_con_stock}")
        
        # Productos bajo stock mínimo
        productos_bajo_stock = VistaStockAlerta.objects.count()
        print(f"⚠️  Productos con stock bajo: {productos_bajo_stock}")
        
        # Tarjetas activas
        tarjetas_activas = Tarjeta.objects.filter(estado='Activa').count()
        print(f"✅ Tarjetas activas: {tarjetas_activas}")
        
        # Empleados activos
        empleados_activos = Empleado.objects.filter(activo=True).count()
        print(f"✅ Empleados activos: {empleados_activos}")
        
    except Exception as e:
        print(f"\n❌ Error al verificar relaciones: {e}")
    
    print(f"\n{'=' * 80}")
    print("✅ Verificación completa")
    print('=' * 80)
    
    return resultados


if __name__ == '__main__':
    verificar_modelos()
