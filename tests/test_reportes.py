"""
✅ TEST DE REPORTES - VERIFICACIÓN
===================================

Verifica que las funciones de reportes existen y están accesibles.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

print("=" * 80)
print("📊 VERIFICACIÓN DE REPORTES")
print("=" * 80)

# ============================================================================
# TEST 1: Verificar clases de reportes
# ============================================================================
print("\n📋 TEST 1: Clases de Reportes")
print("-" * 80)

try:
    from gestion import reportes
    
    # Verificar clases
    if hasattr(reportes, 'ReportesPDF'):
        print("✅ Clase ReportesPDF existe")
        
        # Listar métodos de ReportesPDF
        metodos_pdf = [m for m in dir(reportes.ReportesPDF) 
                       if not m.startswith('_') and callable(getattr(reportes.ReportesPDF, m))]
        print(f"   Métodos disponibles: {len(metodos_pdf)}")
        
        # Buscar métodos de cuenta corriente
        metodos_cc = [m for m in metodos_pdf if 'cta_corriente' in m.lower()]
        if metodos_cc:
            print(f"\n   ✅ Métodos de cuenta corriente:")
            for metodo in metodos_cc:
                print(f"      • {metodo}")
        else:
            print("   ⚠️  No se encontraron métodos de cuenta corriente")
    
    if hasattr(reportes, 'ReportesExcel'):
        print("\n✅ Clase ReportesExcel existe")
        
        # Listar métodos de ReportesExcel
        metodos_excel = [m for m in dir(reportes.ReportesExcel) 
                         if not m.startswith('_') and callable(getattr(reportes.ReportesExcel, m))]
        print(f"   Métodos disponibles: {len(metodos_excel)}")
        
        # Buscar métodos de cuenta corriente
        metodos_cc = [m for m in metodos_excel if 'cta_corriente' in m.lower()]
        if metodos_cc:
            print(f"\n   ✅ Métodos de cuenta corriente:")
            for metodo in metodos_cc:
                print(f"      • {metodo}")
        else:
            print("   ⚠️  No se encontraron métodos de cuenta corriente")
            
except Exception as e:
    print(f"❌ Error: {e}")

# ============================================================================
# TEST 2: Verificar acceso a métodos específicos
# ============================================================================
print("\n📋 TEST 2: Acceso a Métodos Específicos")
print("-" * 80)

try:
    from gestion.reportes import ReportesPDF, ReportesExcel
    
    # Verificar ReportesPDF
    metodos_verificar_pdf = [
        'reporte_cta_corriente_cliente',
        'reporte_cta_corriente_proveedor',
    ]
    
    print("ReportesPDF:")
    for metodo in metodos_verificar_pdf:
        if hasattr(ReportesPDF, metodo):
            print(f"   ✅ {metodo}")
        else:
            print(f"   ❌ {metodo} - No encontrado")
    
    # Verificar ReportesExcel
    metodos_verificar_excel = [
        'reporte_cta_corriente_cliente',
        'reporte_cta_corriente_proveedor',
    ]
    
    print("\nReportesExcel:")
    for metodo in metodos_verificar_excel:
        if hasattr(ReportesExcel, metodo):
            print(f"   ✅ {metodo}")
        else:
            print(f"   ❌ {metodo} - No encontrado")
            
except Exception as e:
    print(f"❌ Error: {e}")

# ============================================================================
# TEST 3: Verificar que los métodos son llamables
# ============================================================================
print("\n📋 TEST 3: Métodos Callable")
print("-" * 80)

try:
    from gestion.reportes import ReportesPDF, ReportesExcel
    
    # ReportesPDF
    if hasattr(ReportesPDF, 'reporte_cta_corriente_cliente'):
        metodo = getattr(ReportesPDF, 'reporte_cta_corriente_cliente')
        if callable(metodo):
            print("✅ ReportesPDF.reporte_cta_corriente_cliente es callable")
        else:
            print("❌ ReportesPDF.reporte_cta_corriente_cliente NO es callable")
    
    if hasattr(ReportesPDF, 'reporte_cta_corriente_proveedor'):
        metodo = getattr(ReportesPDF, 'reporte_cta_corriente_proveedor')
        if callable(metodo):
            print("✅ ReportesPDF.reporte_cta_corriente_proveedor es callable")
        else:
            print("❌ ReportesPDF.reporte_cta_corriente_proveedor NO es callable")
    
    # ReportesExcel
    if hasattr(ReportesExcel, 'reporte_cta_corriente_cliente'):
        metodo = getattr(ReportesExcel, 'reporte_cta_corriente_cliente')
        if callable(metodo):
            print("✅ ReportesExcel.reporte_cta_corriente_cliente es callable")
        else:
            print("❌ ReportesExcel.reporte_cta_corriente_cliente NO es callable")
    
    if hasattr(ReportesExcel, 'reporte_cta_corriente_proveedor'):
        metodo = getattr(ReportesExcel, 'reporte_cta_corriente_proveedor')
        if callable(metodo):
            print("✅ ReportesExcel.reporte_cta_corriente_proveedor es callable")
        else:
            print("❌ ReportesExcel.reporte_cta_corriente_proveedor NO es callable")
            
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 80)
print("✅ VERIFICACIÓN COMPLETADA")
print("=" * 80)
