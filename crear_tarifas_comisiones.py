"""
Script para crear tarifas de comisiones bancarias iniciales
Sistema Cantina Tita - Fase 1

Configura las tarifas para los medios de pago que generan comisión.
Las tarifas son representativas del mercado paraguayo 2025.
"""

import os
import django
from datetime import datetime
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from gestion.models import MediosPago, TarifasComision

def print_separator(title=""):
    """Imprime un separador visual"""
    print("\n" + "="*70)
    if title:
        print(f"  {title}")
        print("="*70)

def print_result(message, success=True, detail=""):
    """Imprime resultado de una operación"""
    icon = "✅" if success else "❌"
    print(f"{icon} {message}")
    if detail:
        print(f"   {detail}")

def limpiar_tarifas_anteriores():
    """Elimina tarifas de prueba anteriores"""
    print_separator("LIMPIEZA DE TARIFAS ANTERIORES")
    
    try:
        deleted = TarifasComision.objects.all().delete()
        print_result("Tarifas eliminadas", True, f"{deleted[0]} registros")
        return True
    except Exception as e:
        print_result("Error en limpieza", False, str(e))
        return False

def crear_tarifas_comisiones():
    """Crea las tarifas de comisión para cada medio de pago"""
    print_separator("CREAR TARIFAS DE COMISIONES")
    
    # Configuración de tarifas (mercado paraguayo 2025)
    tarifas_config = [
        {
            'medio': 'TARJETA DEBITO /QR',
            'porcentaje': Decimal('0.0180'),  # 1.8%
            'monto_fijo': None,
            'descripcion': 'Tarjeta de débito o QR débito'
        },
        {
            'medio': 'TARJETA CREDITO / QR',
            'porcentaje': Decimal('0.0350'),  # 3.5%
            'monto_fijo': None,
            'descripcion': 'Tarjeta de crédito o QR crédito'
        },
        {
            'medio': 'GIROS TIGO',
            'porcentaje': Decimal('0.0200'),  # 2.0%
            'monto_fijo': Decimal('1500.00'),  # Gs 1,500 fijo + 2%
            'descripcion': 'Giros Tigo Money'
        },
        {
            'medio': 'Tarjeta de Crédito',
            'porcentaje': Decimal('0.0350'),  # 3.5%
            'monto_fijo': None,
            'descripcion': 'Tarjeta de crédito física'
        },
        {
            'medio': 'Tarjeta de Débito',
            'porcentaje': Decimal('0.0180'),  # 1.8%
            'monto_fijo': None,
            'descripcion': 'Tarjeta de débito física'
        },
    ]
    
    tarifas_creadas = []
    fecha_inicio = datetime.now()
    
    for config in tarifas_config:
        try:
            # Buscar el medio de pago
            medio = MediosPago.objects.get(descripcion=config['medio'])
            
            # Verificar que el medio genere comisión
            if not medio.genera_comision:
                print_result(
                    f"Medio: {config['medio']}", 
                    False, 
                    "Este medio no genera comisión"
                )
                continue
            
            # Crear la tarifa
            tarifa = TarifasComision.objects.create(
                id_medio_pago=medio,
                fecha_inicio_vigencia=fecha_inicio,
                fecha_fin_vigencia=None,  # Vigencia indefinida
                porcentaje_comision=config['porcentaje'],
                monto_fijo_comision=config['monto_fijo'],
                activo=True
            )
            
            tarifas_creadas.append(tarifa)
            
            # Calcular ejemplo de comisión
            monto_ejemplo = Decimal('100000.00')  # Gs 100,000
            comision_porcentaje = monto_ejemplo * config['porcentaje']
            comision_fija = config['monto_fijo'] or Decimal('0')
            comision_total = comision_porcentaje + comision_fija
            
            print_result(
                f"Tarifa: {config['medio']}", 
                True, 
                f"ID: {tarifa.id_tarifa} | {config['porcentaje']*100:.2f}% " +
                f"{f'+ Gs {config['monto_fijo']:,.0f}' if config['monto_fijo'] else ''}"
            )
            print(f"      Ejemplo: Gs 100,000 → Comisión: Gs {comision_total:,.0f}")
            
        except MediosPago.DoesNotExist:
            print_result(
                f"Medio: {config['medio']}", 
                False, 
                "No existe en la base de datos"
            )
        except Exception as e:
            print_result(
                f"Error: {config['medio']}", 
                False, 
                str(e)
            )
    
    return tarifas_creadas

def mostrar_resumen():
    """Muestra resumen de las tarifas configuradas"""
    print_separator("RESUMEN DE TARIFAS CONFIGURADAS")
    
    # Medios de pago activos
    medios_activos = MediosPago.objects.filter(activo=True)
    print(f"\n📊 Medios de pago activos: {medios_activos.count()}")
    
    for medio in medios_activos:
        tiene_tarifa = TarifasComision.objects.filter(
            id_medio_pago=medio,
            activo=True
        ).exists()
        
        icon = "💳" if medio.genera_comision else "✓"
        tarifa_icon = "✅" if tiene_tarifa else "⚠️"
        
        print(f"  {tarifa_icon} {icon} {medio.descripcion}")
        
        if medio.genera_comision and tiene_tarifa:
            tarifa = TarifasComision.objects.filter(
                id_medio_pago=medio,
                activo=True
            ).first()
            
            if tarifa:
                monto_fijo_str = f" + Gs {tarifa.monto_fijo_comision:,.0f}" if tarifa.monto_fijo_comision else ""
                print(f"      → {tarifa.porcentaje_comision*100:.2f}%{monto_fijo_str}")
    
    # Tarifas activas
    tarifas_activas = TarifasComision.objects.filter(activo=True)
    print(f"\n✅ Total tarifas activas: {tarifas_activas.count()}")
    
    # Medios sin configurar
    medios_sin_tarifa = MediosPago.objects.filter(
        genera_comision=True,
        activo=True
    ).exclude(
        id_medio_pago__in=tarifas_activas.values_list('id_medio_pago', flat=True)
    )
    
    if medios_sin_tarifa.exists():
        print(f"\n⚠️  Medios sin tarifa configurada: {medios_sin_tarifa.count()}")
        for medio in medios_sin_tarifa:
            print(f"    - {medio.descripcion}")
    else:
        print("\n✅ Todos los medios que generan comisión tienen tarifa configurada")

def verificar_trigger():
    """Verifica que el trigger de cálculo de comisiones esté activo"""
    print_separator("VERIFICACIÓN DE TRIGGER")
    
    from django.db import connection
    cursor = connection.cursor()
    
    try:
        cursor.execute("""
            SHOW TRIGGERS 
            WHERE `Table` = 'pagos_venta' 
            AND `Trigger` = 'trg_pago_comision_ai'
        """)
        
        trigger = cursor.fetchone()
        
        if trigger:
            print_result(
                "Trigger activo: trg_pago_comision_ai", 
                True, 
                "Calculará comisiones automáticamente en cada pago"
            )
            return True
        else:
            print_result(
                "Trigger NO encontrado", 
                False, 
                "Las comisiones no se calcularán automáticamente"
            )
            return False
    except Exception as e:
        print_result("Error al verificar trigger", False, str(e))
        return False

def probar_calculo_ejemplo():
    """Muestra ejemplos de cálculo de comisiones"""
    print_separator("EJEMPLOS DE CÁLCULO DE COMISIONES")
    
    tarifas = TarifasComision.objects.filter(activo=True).select_related('id_medio_pago')
    
    montos_ejemplo = [Decimal('50000'), Decimal('100000'), Decimal('500000')]
    
    for tarifa in tarifas:
        print(f"\n💳 {tarifa.id_medio_pago.descripcion}")
        print(f"   Tarifa: {tarifa.porcentaje_comision*100:.2f}%" + 
              (f" + Gs {tarifa.monto_fijo_comision:,.0f}" if tarifa.monto_fijo_comision else ""))
        
        print("   Ejemplos:")
        for monto in montos_ejemplo:
            comision_porcentaje = monto * tarifa.porcentaje_comision
            comision_fija = tarifa.monto_fijo_comision or Decimal('0')
            comision_total = comision_porcentaje + comision_fija
            porcentaje_efectivo = (comision_total / monto) * 100
            
            print(f"     Gs {monto:>8,} → Comisión: Gs {comision_total:>6,.0f} ({porcentaje_efectivo:.2f}%)")

def main():
    """Función principal"""
    print("\n" + "="*70)
    print("  CONFIGURACIÓN DE TARIFAS DE COMISIONES BANCARIAS")
    print("  Sistema Cantina Tita - Fase 1")
    print("="*70)
    
    try:
        # 1. Limpiar tarifas anteriores
        limpiar_tarifas_anteriores()
        
        # 2. Crear tarifas
        tarifas = crear_tarifas_comisiones()
        if not tarifas:
            print("\n⚠️  No se pudieron crear tarifas.")
            return
        
        # 3. Verificar trigger
        verificar_trigger()
        
        # 4. Mostrar resumen
        mostrar_resumen()
        
        # 5. Ejemplos de cálculo
        probar_calculo_ejemplo()
        
        print("\n" + "="*70)
        print("  ✅ CONFIGURACIÓN COMPLETADA EXITOSAMENTE")
        print("="*70)
        print("\n📋 Próximos pasos:")
        print("  1. Realizar una venta de prueba con tarjeta")
        print("  2. Verificar que la comisión se calcule automáticamente")
        print("  3. Revisar tabla: detalle_comision_venta")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ ERROR GENERAL: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
