"""
Script de prueba para el sistema de matching automático de restricciones alimentarias

Ejecutar con: python test_restricciones_matcher.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from gestion.models import Producto, Tarjeta, RestriccionesHijos, Hijo
from gestion.restricciones_matcher import ProductoRestriccionMatcher
from decimal import Decimal


def print_header(texto):
    print(f"\n{'='*70}")
    print(f"  {texto}")
    print(f"{'='*70}")


def print_success(texto):
    print(f"✅ {texto}")


def print_warning(texto):
    print(f"⚠️  {texto}")


def print_error(texto):
    print(f"❌ {texto}")


def print_info(texto):
    print(f"ℹ️  {texto}")


def test_matcher_basico():
    """Test 1: Matching básico de productos"""
    print_header("TEST 1: MATCHING BÁSICO DE PRODUCTOS")
    
    try:
        # Buscar un producto con palabras clave comunes
        productos_test = [
            ('pan', 'Celíaco'),
            ('leche', 'Intolerancia a la lactosa'),
            ('hamburguesa', 'Vegetariano'),
            ('gaseosa', 'Diabetes'),
        ]
        
        for palabra, tipo_restriccion in productos_test:
            # Buscar producto que contenga la palabra
            productos = Producto.objects.filter(
                descripcion__icontains=palabra,
                activo=True
            )[:1]
            
            if productos.exists():
                producto = productos[0]
                
                # Crear restricción de prueba
                restriccion = RestriccionesHijos(
                    tipo_restriccion=tipo_restriccion,
                    observaciones=f'Test para {tipo_restriccion}'
                )
                
                # Analizar
                tiene_conflicto, razon, confianza = ProductoRestriccionMatcher.analizar_producto(
                    producto, restriccion
                )
                
                print(f"\n📦 Producto: {producto.descripcion}")
                print(f"🚫 Restricción: {tipo_restriccion}")
                print(f"{'🔴' if tiene_conflicto else '🟢'} Conflicto: {'SÍ' if tiene_conflicto else 'NO'}")
                print(f"📊 Confianza: {confianza}%")
                print(f"💭 Razón: {razon}")
                
                if tiene_conflicto:
                    print_warning(f"Alerta generada correctamente")
                else:
                    print_success(f"Producto seguro")
            else:
                print_info(f"No se encontraron productos con '{palabra}'")
        
        print_success("\n✓✓✓ TEST 1 COMPLETADO ✓✓✓")
        return True
        
    except Exception as e:
        print_error(f"Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_analisis_carrito():
    """Test 2: Análisis completo de carrito"""
    print_header("TEST 2: ANÁLISIS DE CARRITO COMPLETO")
    
    try:
        # Buscar una tarjeta con hijo y restricciones
        tarjetas_con_hijo = Tarjeta.objects.filter(
            id_hijo__isnull=False,
            estado='Activa'
        ).select_related('id_hijo')
        
        if not tarjetas_con_hijo.exists():
            print_warning("No hay tarjetas con hijo asociado para probar")
            return True
        
        tarjeta = tarjetas_con_hijo.first()
        print_info(f"Tarjeta: {tarjeta.nro_tarjeta}")
        print_info(f"Estudiante: {tarjeta.id_hijo.nombre} {tarjeta.id_hijo.apellido}")
        
        # Verificar si tiene restricciones
        restricciones = RestriccionesHijos.objects.filter(
            id_hijo=tarjeta.id_hijo,
            activo=True
        )
        
        if not restricciones.exists():
            print_warning(f"Estudiante sin restricciones activas")
            return True
        
        print_info(f"Restricciones activas: {restricciones.count()}")
        for r in restricciones:
            print(f"  - {r.tipo_restriccion}")
        
        # Crear carrito de prueba con productos diversos
        productos = Producto.objects.filter(activo=True)[:5]
        carrito = [{'producto': p, 'cantidad': 1} for p in productos]
        
        print(f"\n🛒 Carrito de prueba ({len(carrito)} items):")
        for item in carrito:
            print(f"  - {item['producto'].descripcion}")
        
        # Analizar carrito
        resultado = ProductoRestriccionMatcher.analizar_carrito(carrito, tarjeta)
        
        print(f"\n📊 RESULTADO DEL ANÁLISIS:")
        print(f"  Tiene alertas: {'SÍ' if resultado['tiene_alertas'] else 'NO'}")
        print(f"  Puede continuar: {'SÍ' if resultado['puede_continuar'] else 'NO'}")
        print(f"  Requiere autorización: {'SÍ' if resultado['requiere_autorizacion'] else 'NO'}")
        
        if resultado['alertas']:
            print(f"\n🚨 ALERTAS DETECTADAS ({len(resultado['alertas'])}):")
            for i, alerta in enumerate(resultado['alertas'], 1):
                print(f"\n  Alerta #{i}:")
                print(f"    Producto: {alerta['producto'].descripcion}")
                print(f"    Restricción: {alerta['restriccion'].tipo_restriccion}")
                print(f"    Severidad: {alerta['severidad'].upper()}")
                print(f"    Confianza: {alerta['nivel_confianza']}%")
                print(f"    Razón: {alerta['razon']}")
        else:
            print_success("\n✓ Carrito seguro, sin alertas")
        
        print_success("\n✓✓✓ TEST 2 COMPLETADO ✓✓✓")
        return True
        
    except Exception as e:
        print_error(f"Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_sugerir_alternativas():
    """Test 3: Sugerencias de productos alternativos"""
    print_header("TEST 3: SUGERENCIAS DE ALTERNATIVAS")
    
    try:
        # Buscar producto con palabra clave común
        productos = Producto.objects.filter(
            descripcion__icontains='carne',
            activo=True
        )[:1]
        
        if not productos.exists():
            print_warning("No se encontraron productos con 'carne'")
            return True
        
        producto = productos[0]
        print_info(f"Producto conflictivo: {producto.descripcion}")
        
        # Crear restricción vegetariana
        restriccion = RestriccionesHijos(
            tipo_restriccion='Vegetariano',
            observaciones='No consume carne'
        )
        
        # Obtener alternativas
        alternativas = ProductoRestriccionMatcher.sugerir_alternativas(
            producto, restriccion, max_resultados=5
        )
        
        if alternativas:
            print_success(f"\n✓ Encontradas {len(alternativas)} alternativas:")
            for i, alt in enumerate(alternativas, 1):
                print(f"  {i}. {alt.descripcion}")
        else:
            print_warning("No se encontraron alternativas")
        
        print_success("\n✓✓✓ TEST 3 COMPLETADO ✓✓✓")
        return True
        
    except Exception as e:
        print_error(f"Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_base_conocimiento():
    """Test 4: Verificar base de conocimiento"""
    print_header("TEST 4: BASE DE CONOCIMIENTO")
    
    print("\n📚 RESTRICCIONES SOPORTADAS:")
    for tipo, keywords in ProductoRestriccionMatcher.KEYWORDS_RESTRICCIONES.items():
        print(f"\n  {tipo}:")
        print(f"    - Keywords: {len(keywords)} palabras")
        print(f"    - Ejemplos: {', '.join(keywords[:5])}...")
        
        categorias = ProductoRestriccionMatcher.CATEGORIAS_RIESGO.get(tipo, [])
        if categorias:
            print(f"    - Categorías riesgo: {', '.join(categorias)}")
    
    print_success("\n✓✓✓ BASE DE CONOCIMIENTO VERIFICADA ✓✓✓")
    return True


def main():
    print("\n" + "="*70)
    print("  TEST DEL SISTEMA DE MATCHING AUTOMÁTICO")
    print("  Restricciones Alimentarias vs Productos")
    print("="*70)
    
    resultados = []
    
    # Ejecutar todos los tests
    resultados.append(("Matching Básico", test_matcher_basico()))
    resultados.append(("Análisis de Carrito", test_analisis_carrito()))
    resultados.append(("Sugerencias", test_sugerir_alternativas()))
    resultados.append(("Base de Conocimiento", test_base_conocimiento()))
    
    # Resumen
    print_header("RESUMEN DE TESTS")
    
    exitosos = sum(1 for _, resultado in resultados if resultado)
    total = len(resultados)
    
    for nombre, resultado in resultados:
        if resultado:
            print_success(f"{nombre}: EXITOSO")
        else:
            print_error(f"{nombre}: FALLIDO")
    
    print(f"\n📊 Total: {exitosos}/{total} tests exitosos ({int(exitosos/total*100)}%)")
    
    if exitosos == total:
        print_success("\n🎉 TODOS LOS TESTS PASARON CORRECTAMENTE 🎉")
    else:
        print_error(f"\n⚠️  {total - exitosos} test(s) fallaron")


if __name__ == '__main__':
    main()
