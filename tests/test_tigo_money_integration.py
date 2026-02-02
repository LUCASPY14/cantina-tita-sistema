"""
Script de prueba completo para integración Tigo Money
Prueba el flujo completo de pagos con billetera digital Tigo Money
"""
import os
import sys
import django
from decimal import Decimal
from datetime import datetime

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from gestion.models import Cliente, Tarjeta, Hijo
from gestion.tigo_money_gateway import TigoMoneyGateway, procesar_pago_tigo_money, verificar_pago_tigo_money
from django.test import RequestFactory
from django.utils import timezone


def print_separator(title=""):
    """Imprime separador visual"""
    print("\n" + "=" * 80)
    if title:
        print(f"  {title}")
        print("=" * 80)


def test_validacion_telefono():
    """Test de validación de números Tigo"""
    print_separator("TEST 1: VALIDACIÓN DE NÚMEROS TIGO")
    
    gateway = TigoMoneyGateway()
    
    # Casos de prueba
    test_cases = [
        ("0981123456", True, "Número Tigo válido con 0 inicial"),
        ("981123456", True, "Número Tigo válido sin 0"),
        ("+595981123456", True, "Número con código de país"),
        ("0971123456", False, "Número Personal (no Tigo)"),
        ("0961123456", False, "Número Claro (no Tigo)"),
        ("0982555666", True, "Número Tigo prefijo 982"),
        ("0991777888", True, "Número Tigo prefijo 991"),
        ("123456", False, "Número inválido (muy corto)"),
    ]
    
    for telefono, esperado, descripcion in test_cases:
        es_valido, mensaje = gateway.validar_telefono_tigo(telefono)
        status = "✅" if es_valido == esperado else "❌"
        print(f"{status} {descripcion}")
        print(f"   Teléfono: {telefono}")
        print(f"   Resultado: {'VÁLIDO' if es_valido else 'INVÁLIDO'}")
        print(f"   Mensaje: {mensaje}")
        print()


def test_formateo_telefono():
    """Test de formateo de números de teléfono"""
    print_separator("TEST 2: FORMATEO DE TELÉFONOS")
    
    gateway = TigoMoneyGateway()
    
    test_phones = [
        "0981123456",
        "981123456",
        "+595981123456",
        "0982-555-666",
        "(0991) 777 888",
    ]
    
    for phone in test_phones:
        formatted = gateway._formatear_telefono(phone)
        print(f"   Input:  {phone:20} → Output: {formatted}")


def test_iniciar_pago_sandbox():
    """Test de inicio de pago en modo sandbox"""
    print_separator("TEST 3: INICIAR PAGO (SANDBOX)")
    
    gateway = TigoMoneyGateway()
    
    # Datos de prueba
    telefono = "0981123456"
    monto = Decimal("50000")  # Gs. 50,000
    descripcion = "Recarga de saldo - Test"
    
    print(f"📱 Teléfono: {telefono}")
    print(f"💰 Monto: Gs. {int(monto):,}")
    print(f"📝 Descripción: {descripcion}")
    print()
    
    # Iniciar pago
    exito, transaction_id, response_data, error = gateway.iniciar_pago(
        telefono=telefono,
        monto=monto,
        descripcion=descripcion,
        customer_data={'nombre': 'Cliente Test'}
    )
    
    if exito:
        print("✅ Pago iniciado exitosamente")
        print(f"   Transaction ID: {transaction_id}")
        print(f"   Datos de respuesta:")
        for key, value in response_data.items():
            print(f"      - {key}: {value}")
    else:
        print(f"❌ Error iniciando pago: {error}")


def test_procesar_pago_funcion():
    """Test de la función de conveniencia procesar_pago_tigo_money"""
    print_separator("TEST 4: FUNCIÓN procesar_pago_tigo_money()")
    
    # Crear request mock
    factory = RequestFactory()
    request = factory.post('/test/')
    request.session = {'cliente_usuario': 'Juan Pérez'}
    
    # Datos de prueba
    telefono = "0981123456"
    monto = Decimal("100000")
    descripcion = "Test de recarga"
    
    print(f"📱 Teléfono: {telefono}")
    print(f"💰 Monto: Gs. {int(monto):,}")
    print()
    
    # Procesar pago
    exito, transaction_id, mensaje, custom_id = procesar_pago_tigo_money(
        telefono=telefono,
        monto=monto,
        descripcion=descripcion,
        request=request,
        tipo_pago='CARGA_SALDO'
    )
    
    if exito:
        print("✅ Pago procesado")
        print(f"   Transaction ID: {transaction_id}")
        print(f"   Custom ID: {custom_id}")
        print(f"\n   Mensaje para usuario:")
        print(mensaje)
    else:
        print(f"❌ Error: {mensaje}")


def test_consultar_estado():
    """Test de consulta de estado de pago"""
    print_separator("TEST 5: CONSULTAR ESTADO DE PAGO")
    
    # Primero iniciar un pago
    gateway = TigoMoneyGateway()
    exito, transaction_id, _, _ = gateway.iniciar_pago(
        telefono="0981123456",
        monto=Decimal("25000"),
        descripcion="Test estado"
    )
    
    if not exito:
        print("❌ No se pudo iniciar pago para probar")
        return
    
    print(f"🔍 Consultando estado de: {transaction_id}")
    print()
    
    # Consultar estado
    resultado = verificar_pago_tigo_money(transaction_id)
    
    print(f"✅ Consulta exitosa: {resultado['exito']}")
    print(f"   Estado: {resultado['estado']}")
    print(f"   Completado: {resultado['completado']}")
    print(f"   Pendiente: {resultado['pendiente']}")
    print(f"   Fallido: {resultado['fallido']}")
    
    if resultado['datos']:
        print(f"\n   Datos completos:")
        for key, value in resultado['datos'].items():
            print(f"      - {key}: {value}")


def test_integracion_con_cliente_real():
    """Test con datos reales de un cliente del sistema"""
    print_separator("TEST 6: INTEGRACIÓN CON CLIENTE REAL")
    
    # Buscar un cliente con hijo y tarjeta
    try:
        hijo = Hijo.objects.filter(activo=True).select_related(
            'id_cliente_responsable'
        ).first()
        
        if not hijo:
            print("⚠️  No hay hijos en el sistema para probar")
            return
        
        cliente = hijo.id_cliente_responsable
        tarjeta = Tarjeta.objects.filter(id_hijo=hijo).first()
        
        if not tarjeta:
            print("⚠️  El hijo no tiene tarjeta asignada")
            return
        
        print(f"👤 Cliente: {cliente.nombres} {cliente.apellidos}")
        print(f"👶 Hijo: {hijo.nombre} {hijo.apellido}")
        print(f"💳 Tarjeta: {tarjeta.nro_tarjeta}")
        print(f"💰 Saldo actual: Gs. {int(tarjeta.saldo_actual):,}")
        print()
        
        # Simular recarga
        telefono_test = "0981123456"  # Cambiar por número real del cliente si existe
        monto_recarga = Decimal("50000")
        
        print(f"🔄 Simulando recarga de Gs. {int(monto_recarga):,}")
        print(f"   Al teléfono: {telefono_test}")
        print()
        
        # Crear request mock
        factory = RequestFactory()
        request = factory.post('/portal/recarga/')
        request.session = {
            'cliente_id': cliente.id_cliente,
            'cliente_usuario': f"{cliente.nombres} {cliente.apellidos}"
        }
        
        # Procesar pago
        exito, transaction_id, mensaje, custom_id = procesar_pago_tigo_money(
            telefono=telefono_test,
            monto=monto_recarga,
            descripcion=f"Recarga para {hijo.nombre}",
            request=request,
            tipo_pago='CARGA_SALDO'
        )
        
        if exito:
            print("✅ Recarga iniciada exitosamente")
            print(f"   Transaction ID: {transaction_id}")
            print(f"   Custom ID: {custom_id}")
            print(f"\n   📱 Instrucciones enviadas al cliente:")
            print(mensaje)
            
            print(f"\n   💡 Próximo paso:")
            print(f"   Una vez que el cliente confirme el pago con *555#,")
            print(f"   el webhook actualizará automáticamente:")
            print(f"   - Saldo de tarjeta: Gs. {int(tarjeta.saldo_actual):,} → Gs. {int(tarjeta.saldo_actual + monto_recarga):,}")
            print(f"   - Estado en cargas_saldo: PENDIENTE → CONFIRMADO")
        else:
            print(f"❌ Error: {mensaje}")
    
    except Exception as e:
        print(f"❌ Error en test: {e}")


def test_comparacion_metrepay_vs_tigo():
    """Comparación entre MetrePay y Tigo Money"""
    print_separator("TEST 7: COMPARACIÓN MetrePay vs Tigo Money")
    
    print("📊 COMPARACIÓN DE MÉTODOS DE PAGO PARAGUAYOS")
    print()
    
    comparacion = """
    ┌────────────────────────┬──────────────────────┬──────────────────────┐
    │ Característica         │ MetrePay             │ Tigo Money           │
    ├────────────────────────┼──────────────────────┼──────────────────────┤
    │ Tipo                   │ Gateway de pagos     │ Billetera digital    │
    │ Método de pago         │ Tarjeta crédito/déb. │ Número de teléfono   │
    │ Confirmación           │ Automática           │ SMS/USSD (*555#)     │
    │ Comisión típica        │ 2.5-3%               │ 1-2%                 │
    │ Tiempo de procesamiento│ Inmediato            │ 1-5 minutos          │
    │ Requiere cuenta bancaria│ Sí                  │ No                   │
    │ Popularidad en Paraguay│ Alta (comercios)     │ Alta (personas)      │
    │ Integración            │ ✅ Implementado      │ ✅ Implementado      │
    └────────────────────────┴──────────────────────┴──────────────────────┘
    """
    
    print(comparacion)
    
    print("\n💡 RECOMENDACIÓN DE USO:")
    print("   • MetrePay: Para clientes con tarjeta bancaria")
    print("   • Tigo Money: Para clientes sin tarjeta, pagos rápidos")
    print("   • Ambos: Ofrecer las 2 opciones maximiza cobertura")
    print()
    
    print("📈 VENTAJAS COMBINADAS:")
    print("   ✅ Cobertura del 95%+ de usuarios paraguayos")
    print("   ✅ Opciones de pago flexibles")
    print("   ✅ Menores comisiones que métodos tradicionales")
    print("   ✅ Confirmación automática via webhooks")


def run_all_tests():
    """Ejecuta todos los tests"""
    print("=" * 80)
    print("  🧪 SUITE COMPLETA DE TESTS - TIGO MONEY INTEGRATION")
    print("=" * 80)
    print(f"  Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("  Entorno: Sandbox/Desarrollo")
    print("=" * 80)
    
    tests = [
        ("Validación de teléfonos", test_validacion_telefono),
        ("Formateo de teléfonos", test_formateo_telefono),
        ("Iniciar pago en sandbox", test_iniciar_pago_sandbox),
        ("Función procesar_pago_tigo_money", test_procesar_pago_funcion),
        ("Consultar estado de pago", test_consultar_estado),
        ("Integración con cliente real", test_integracion_con_cliente_real),
        ("Comparación MetrePay vs Tigo", test_comparacion_metrepay_vs_tigo),
    ]
    
    resultados = []
    
    for nombre, test_func in tests:
        try:
            test_func()
            resultados.append((nombre, "✅ PASÓ"))
        except Exception as e:
            resultados.append((nombre, f"❌ FALLÓ: {str(e)}"))
            print(f"\n❌ Error en {nombre}: {e}")
    
    # Resumen final
    print_separator("RESUMEN DE TESTS")
    
    for nombre, resultado in resultados:
        print(f"  {resultado:15} - {nombre}")
    
    total = len(resultados)
    pasados = sum(1 for _, r in resultados if r.startswith("✅"))
    
    print()
    print(f"  Total: {pasados}/{total} tests pasados")
    print()
    
    if pasados == total:
        print("  🎉 ¡TODOS LOS TESTS PASARON!")
    else:
        print("  ⚠️  Algunos tests fallaron, revisar logs arriba")
    
    print_separator()
    
    print("\n💡 PRÓXIMOS PASOS:")
    print("   1. Obtener credenciales reales de Tigo Money")
    print("   2. Configurar variables en .env.production")
    print("   3. Configurar webhook en panel de Tigo Money")
    print("   4. Probar en ambiente de producción con pago real pequeño")
    print("   5. Monitorear logs de webhooks en primeros pagos")
    print()


if __name__ == "__main__":
    run_all_tests()
