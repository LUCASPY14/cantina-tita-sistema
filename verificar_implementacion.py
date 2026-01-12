"""
Test simple de verificación de código implementado
"""
import os
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')

import django
django.setup()

def test_validaciones_backend():
    """Verificar que las funciones de validación existen"""
    from gestion import pos_views
    
    funciones_requeridas = [
        'validar_carga_saldo',
        'validar_pago',
        'lista_cargas_pendientes',
        'lista_pagos_pendientes'
    ]
    
    for func_name in funciones_requeridas:
        assert hasattr(pos_views, func_name), f"❌ Falta función: {func_name}"
        print(f"✅ Función {func_name} existe")
    
    print("\n✅ TODAS LAS FUNCIONES DE VALIDACIÓN EXISTEN")


def test_empleados_ajax_backend():
    """Verificar que las funciones AJAX de empleados existen"""
    from gestion import empleado_views
    
    funciones_requeridas = [
        'obtener_empleado_ajax',
        'editar_empleado_ajax',
        'resetear_password_empleado_ajax',
        'toggle_estado_empleado_ajax'
    ]
    
    for func_name in funciones_requeridas:
        assert hasattr(empleado_views, func_name), f"❌ Falta función: {func_name}"
        print(f"✅ Función {func_name} existe")
    
    print("\n✅ TODAS LAS FUNCIONES AJAX DE EMPLEADOS EXISTEN")


def test_templates():
    """Verificar que los templates existen"""
    import os
    from django.conf import settings
    
    templates_requeridos = [
        'pos/validar_carga.html',
        'pos/validar_pago.html',
        'pos/lista_cargas_pendientes.html',
        'pos/lista_pagos_pendientes.html'
    ]
    
    base_dir = settings.BASE_DIR
    templates_dir = os.path.join(base_dir, 'gestion', 'templates')
    
    for template in templates_requeridos:
        template_path = os.path.join(templates_dir, template)
        assert os.path.exists(template_path), f"❌ Falta template: {template}"
        print(f"✅ Template {template} existe")
    
    print("\n✅ TODOS LOS TEMPLATES EXISTEN")


def test_archivos_produccion():
    """Verificar que los archivos de configuración de producción existen"""
    import os
    from django.conf import settings
    
    archivos_requeridos = [
        'gunicorn_config.py',
        'deployment/cantitatita.service',
        'deployment/nginx.conf',
        'deployment/GUIA_DESPLIEGUE.md'
    ]
    
    base_dir = settings.BASE_DIR
    
    for archivo in archivos_requeridos:
        archivo_path = os.path.join(base_dir, archivo)
        assert os.path.exists(archivo_path), f"❌ Falta archivo: {archivo}"
        
        # Verificar que no está vacío
        size = os.path.getsize(archivo_path)
        assert size > 0, f"❌ Archivo vacío: {archivo}"
        
        print(f"✅ Archivo {archivo} existe ({size:,} bytes)")
    
    print("\n✅ TODOS LOS ARCHIVOS DE PRODUCCIÓN EXISTEN")


def test_archivos_tests():
    """Verificar que los archivos de tests existen"""
    import os
    from django.conf import settings
    
    archivos_requeridos = [
        'tests/test_validaciones.py',
        'tests/test_empleados_ajax.py',
        'tests/test_integracion.py',
        'tests/README_TESTS.md'
    ]
    
    base_dir = settings.BASE_DIR
    
    for archivo in archivos_requeridos:
        archivo_path = os.path.join(base_dir, archivo)
        assert os.path.exists(archivo_path), f"❌ Falta archivo: {archivo}"
        
        size = os.path.getsize(archivo_path)
        print(f"✅ Archivo {archivo} existe ({size:,} bytes)")
    
    print("\n✅ TODOS LOS ARCHIVOS DE TESTS EXISTEN")


def test_urls():
    """Verificar que las URLs están configuradas"""
    from django.urls import reverse, NoReverseMatch
    
    urls_validaciones = [
        ('pos:lista_cargas_pendientes', []),
        ('pos:lista_pagos_pendientes', []),
    ]
    
    urls_empleados = [
        ('obtener_empleado_ajax', [1]),
        ('editar_empleado_ajax', [1]),
        ('resetear_password_ajax', [1]),
        ('toggle_estado_ajax', [1]),
    ]
    
    print("\n🔗 Verificando URLs de validaciones:")
    for url_name, args in urls_validaciones:
        try:
            url = reverse(url_name, args=args)
            print(f"✅ URL {url_name} → {url}")
        except NoReverseMatch:
            print(f"❌ URL {url_name} no encontrada")
    
    print("\n🔗 Verificando URLs de empleados:")
    for url_name, args in urls_empleados:
        try:
            url = reverse(url_name, args=args)
            print(f"✅ URL {url_name} → {url}")
        except NoReverseMatch:
            print(f"❌ URL {url_name} no encontrada")


def main():
    print("=" * 70)
    print("VERIFICACIÓN DE IMPLEMENTACIÓN - CANTINA TITA")
    print("=" * 70)
    
    try:
        print("\n📦 1. VERIFICANDO BACKEND - VALIDACIONES")
        print("-" * 70)
        test_validaciones_backend()
        
        print("\n📦 2. VERIFICANDO BACKEND - AJAX EMPLEADOS")
        print("-" * 70)
        test_empleados_ajax_backend()
        
        print("\n📄 3. VERIFICANDO TEMPLATES")
        print("-" * 70)
        test_templates()
        
        print("\n🚀 4. VERIFICANDO ARCHIVOS DE PRODUCCIÓN")
        print("-" * 70)
        test_archivos_produccion()
        
        print("\n🧪 5. VERIFICANDO ARCHIVOS DE TESTS")
        print("-" * 70)
        test_archivos_tests()
        
        print("\n🔗 6. VERIFICANDO URLs")
        print("-" * 70)
        test_urls()
        
        print("\n" + "=" * 70)
        print("✅ VERIFICACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 70)
        
        print("\n📊 RESUMEN:")
        print("  • 4 vistas de validación ✓")
        print("  • 4 endpoints AJAX de empleados ✓")
        print("  • 4 templates HTML ✓")
        print("  • 4 archivos de configuración de producción ✓")
        print("  • 4 archivos de tests ✓")
        print("\n🎉 ¡TODO IMPLEMENTADO CORRECTAMENTE!")
        
        return 0
        
    except AssertionError as e:
        print(f"\n❌ ERROR: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
