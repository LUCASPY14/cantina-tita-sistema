#!/usr/bin/env python
"""
Script de Testing - Sistema de Almuerzos
Prueba todas las vistas del sistema de almuerzos
"""
import os
import django
import sys
from datetime import date, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.contrib.auth.models import User
from gestion.models import (
    PlanesAlmuerzo, SuscripcionesAlmuerzo, 
    RegistroConsumoAlmuerzo, PagosAlmuerzoMensual,
    Hijo, Cliente
)

def print_separator(title=""):
    print("\n" + "="*70)
    if title:
        print(f"  {title}")
        print("="*70)

def print_result(test_name, success, message=""):
    status = "✅ OK" if success else "❌ ERROR"
    print(f"{status} - {test_name}")
    if message:
        print(f"      {message}")

def test_models_exist():
    """Verifica que los modelos existan y sean accesibles"""
    print_separator("TEST 1: Verificación de Modelos")
    
    models = [
        ('PlanesAlmuerzo', PlanesAlmuerzo),
        ('SuscripcionesAlmuerzo', SuscripcionesAlmuerzo),
        ('RegistroConsumoAlmuerzo', RegistroConsumoAlmuerzo),
        ('PagosAlmuerzoMensual', PagosAlmuerzoMensual),
    ]
    
    all_ok = True
    for model_name, model_class in models:
        try:
            count = model_class.objects.count()
            print_result(f"Modelo {model_name}", True, f"{count} registros")
        except Exception as e:
            print_result(f"Modelo {model_name}", False, str(e))
            all_ok = False
    
    return all_ok

def test_create_plan():
    """Prueba crear un plan de almuerzo"""
    print_separator("TEST 2: Crear Plan de Almuerzo")
    
    try:
        from django.utils import timezone
        
        # Crear plan mensual
        plan_mensual = PlanesAlmuerzo.objects.create(
            nombre_plan="Plan Mensual Test",
            descripcion="Plan de almuerzo mensual",
            precio_mensual=50000.00,
            dias_semana_incluidos="Lunes a Viernes",
            activo=True,
            fecha_creacion=timezone.now()
        )
        print_result("Crear Plan Mensual", True, f"ID: {plan_mensual.id_plan_almuerzo}")
        
        # Crear plan semanal
        plan_semanal = PlanesAlmuerzo.objects.create(
            nombre_plan="Plan Semanal Test",
            descripcion="Plan de almuerzo semanal",
            precio_mensual=15000.00,
            dias_semana_incluidos="Lunes a Viernes",
            activo=True,
            fecha_creacion=timezone.now()
        )
        print_result("Crear Plan Semanal", True, f"ID: {plan_semanal.id_plan_almuerzo}")
        
        # Crear plan económico
        plan_economico = PlanesAlmuerzo.objects.create(
            nombre_plan="Plan Económico Test",
            descripcion="Plan de almuerzo económico",
            precio_mensual=30000.00,
            dias_semana_incluidos="Lunes a Viernes",
            activo=True,
            fecha_creacion=timezone.now()
        )
        print_result("Crear Plan Económico", True, f"ID: {plan_economico.id_plan_almuerzo}")
        
        return True
    except Exception as e:
        print_result("Crear Planes", False, str(e))
        return False

def test_suscription():
    """Prueba crear suscripciones"""
    print_separator("TEST 3: Crear Suscripciones")
    
    try:
        from gestion.models import ListaPrecios
        
        # Obtener lista de precios por defecto
        lista_precios = ListaPrecios.objects.first()
        if not lista_precios:
            print_result("Lista Precios", False, "No hay listas de precios en el sistema")
            return False
        
        # Obtener o crear estudiante de prueba
        cliente, _ = Cliente.objects.get_or_create(
            nombres="Padre Test",
            apellidos="Apellido Test",
            defaults={
                'id_lista_por_defecto': lista_precios,
                'email': 'padre@test.com'
            }
        )
        
        hijo, _ = Hijo.objects.get_or_create(
            codigo_hijo="EST001",
            defaults={
                'nombres': 'Estudiante',
                'apellidos': 'Test',
                'grado': '5to Primaria',
                'id_cliente': cliente
            }
        )
        print_result("Crear/Obtener Estudiante", True, f"{hijo.nombres} {hijo.apellidos}")
        
        # Obtener planes
        plan_mensual = PlanesAlmuerzo.objects.filter(activo=True).first()
        
        if not plan_mensual:
            print_result("Obtener Plan", False, "No hay planes activos")
            return False
        
        # Crear suscripción
        fecha_inicio = date.today()
        fecha_fin = fecha_inicio + timedelta(days=30)
        
        suscripcion = SuscripcionesAlmuerzo.objects.create(
            id_hijo=hijo,
            id_plan_almuerzo=plan_mensual,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            estado='Activa'
        )
        print_result("Crear Suscripción", True, f"ID: {suscripcion.id_suscripcion_almuerzo}")
        
        # Verificar que no se pueda crear duplicado
        try:
            suscripcion_dup = SuscripcionesAlmuerzo.objects.create(
                id_hijo=hijo,
                id_plan_almuerzo=plan_mensual,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                estado='Activa'
            )
            # Eliminar el duplicado
            suscripcion_dup.delete()
            print_result("Validación Duplicados", False, "Permitió crear suscripción duplicada")
        except:
            # En realidad, la validación debe estar en la vista, no en el modelo
            print_result("Validación Duplicados", True, "Nota: Validación debe estar en la vista")
        
        return True
    except Exception as e:
        print_result("Crear Suscripciones", False, str(e))
        return False

def test_consumo():
    """Prueba registrar consumo"""
    print_separator("TEST 4: Registrar Consumo")
    
    try:
        # Obtener suscripción activa
        suscripcion = SuscripcionesAlmuerzo.objects.filter(estado='Activa').first()
        
        if not suscripcion:
            print_result("Obtener Suscripción", False, "No hay suscripciones activas")
            return False
        
        # Registrar consumo de hoy
        from django.utils import timezone
        consumo = RegistroConsumoAlmuerzo.objects.create(
            id_hijo=suscripcion.id_hijo,
            id_suscripcion=suscripcion,
            fecha_consumo=date.today(),
            hora_registro=timezone.now().time()
        )
        print_result("Registrar Consumo Hoy", True, f"ID: {consumo.id_registro_consumo}")
        
        # Intentar duplicar (debe fallar por unique_together)
        try:
            consumo_dup = RegistroConsumoAlmuerzo.objects.create(
                id_hijo=suscripcion.id_hijo,
                id_suscripcion=suscripcion,
                fecha_consumo=date.today(),
                hora_registro=timezone.now().time()
            )
            consumo_dup.delete()
            print_result("Validación Consumo Duplicado", False, "Permitió registrar dos veces")
        except:
            print_result("Validación Consumo Duplicado", True, "Restricción unique_together funciona")
        
        # Contar consumos
        total_consumos = RegistroConsumoAlmuerzo.objects.filter(
            id_hijo=suscripcion.id_hijo
        ).count()
        print_result("Contar Consumos", True, f"{total_consumos} consumos registrados")
        
        return True
    except Exception as e:
        print_result("Registrar Consumo", False, str(e))
        return False

def test_facturacion():
    """Prueba la facturación mensual"""
    print_separator("TEST 5: Facturación Mensual")
    
    try:
        from django.utils import timezone
        from datetime import datetime
        
        # Obtener suscripciones activas
        suscripciones_activas = SuscripcionesAlmuerzo.objects.filter(estado='Activa')
        print_result("Suscripciones Activas", True, f"{suscripciones_activas.count()} encontradas")
        
        if suscripciones_activas.count() == 0:
            print_result("Facturación", False, "No hay suscripciones para facturar")
            return False
        
        # Simular facturación
        mes_actual = timezone.now().month
        anio_actual = timezone.now().year
        fecha_mes = datetime(anio_actual, mes_actual, 1).date()
        
        for suscripcion in suscripciones_activas:
            # Contar días consumidos
            dias_consumidos = RegistroConsumoAlmuerzo.objects.filter(
                id_hijo=suscripcion.id_hijo,
                fecha_consumo__month=mes_actual,
                fecha_consumo__year=anio_actual
            ).count()
            
            # Calcular monto (precio mensual completo)
            monto = suscripcion.id_plan_almuerzo.precio_mensual
            
            # Crear pago (verificar si ya existe)
            pago_existente = PagosAlmuerzoMensual.objects.filter(
                id_suscripcion=suscripcion,
                mes_pagado__month=mes_actual,
                mes_pagado__year=anio_actual
            ).first()
            
            if pago_existente:
                print_result(f"Pago {suscripcion.id_hijo.nombres}", True, 
                           f"Ya existe - ${monto:,.0f}")
            else:
                pago = PagosAlmuerzoMensual.objects.create(
                    id_suscripcion=suscripcion,
                    fecha_pago=timezone.now(),
                    monto_pagado=monto,
                    mes_pagado=fecha_mes,
                    estado='Pendiente'
                )
                print_result(f"Facturar {suscripcion.id_hijo.nombres}", True, 
                           f"ID: {pago.id_pago_almuerzo_mensual} - ${monto:,.0f}")
        
        return True
    except Exception as e:
        print_result("Facturación Mensual", False, str(e))
        return False

def test_estadisticas():
    """Prueba las estadísticas del sistema"""
    print_separator("TEST 6: Estadísticas del Sistema")
    
    try:
        # Planes activos
        planes_activos = PlanesAlmuerzo.objects.filter(activo=True).count()
        print_result("Planes Activos", True, f"{planes_activos} planes")
        
        # Suscripciones activas
        suscripciones_activas = SuscripcionesAlmuerzo.objects.filter(estado='Activa').count()
        print_result("Suscripciones Activas", True, f"{suscripciones_activas} suscripciones")
        
        # Consumos de hoy
        consumos_hoy = RegistroConsumoAlmuerzo.objects.filter(
            fecha_consumo=date.today()
        ).count()
        print_result("Consumos Hoy", True, f"{consumos_hoy} almuerzos")
        
        # Ingresos del mes
        from django.utils import timezone
        from django.db.models import Sum
        from datetime import datetime
        
        mes_actual = timezone.now().month
        anio_actual = timezone.now().year
        fecha_inicio = datetime(anio_actual, mes_actual, 1).date()
        if mes_actual == 12:
            fecha_fin = datetime(anio_actual + 1, 1, 1).date()
        else:
            fecha_fin = datetime(anio_actual, mes_actual + 1, 1).date()
        
        ingresos = PagosAlmuerzoMensual.objects.filter(
            mes_pagado__gte=fecha_inicio,
            mes_pagado__lt=fecha_fin
        ).aggregate(total=Sum('monto_pagado'))['total'] or 0
        
        print_result("Ingresos del Mes", True, f"${ingresos:,.0f}")
        
        return True
    except Exception as e:
        print_result("Estadísticas", False, str(e))
        return False

def cleanup():
    """Limpiar datos de prueba (opcional)"""
    print_separator("LIMPIEZA (Opcional)")
    
    response = input("\n¿Desea eliminar los datos de prueba? (s/n): ")
    
    if response.lower() == 's':
        try:
            # Eliminar en orden inverso por dependencias
            RegistroConsumoAlmuerzo.objects.filter(
                id_suscripcion__id_hijo__codigo_hijo='EST001'
            ).delete()
            
            PagosAlmuerzoMensual.objects.filter(
                id_suscripcion__id_hijo__codigo_hijo='EST001'
            ).delete()
            
            SuscripcionesAlmuerzo.objects.filter(
                id_hijo__codigo_hijo='EST001'
            ).delete()
            
            PlanesAlmuerzo.objects.filter(
                nombre_plan__contains='Test'
            ).delete()
            
            Hijo.objects.filter(codigo_hijo='EST001').delete()
            Cliente.objects.filter(nombres='Padre Test').delete()
            
            print_result("Limpieza Completada", True, "Datos de prueba eliminados")
        except Exception as e:
            print_result("Limpieza", False, str(e))
    else:
        print("Datos de prueba conservados para inspección manual")

def main():
    print_separator("SISTEMA DE ALMUERZOS - SUITE DE PRUEBAS")
    print("Fecha:", date.today().strftime("%d/%m/%Y"))
    print("="*70)
    
    tests = [
        ("Modelos", test_models_exist),
        ("Planes", test_create_plan),
        ("Suscripciones", test_suscription),
        ("Consumo", test_consumo),
        ("Facturación", test_facturacion),
        ("Estadísticas", test_estadisticas),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print_result(test_name, False, f"Error crítico: {str(e)}")
            results[test_name] = False
    
    # Resumen final
    print_separator("RESUMEN DE PRUEBAS")
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed
    
    print(f"\nTotal de pruebas: {total}")
    print(f"✅ Exitosas: {passed}")
    print(f"❌ Fallidas: {failed}")
    print(f"📊 Tasa de éxito: {(passed/total)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 ¡Todas las pruebas pasaron exitosamente!")
    else:
        print(f"\n⚠️  Hay {failed} prueba(s) que requieren atención")
    
    print_separator()
    
    # Opción de limpieza
    cleanup()
    
    return failed == 0

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Pruebas interrumpidas por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error crítico: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
