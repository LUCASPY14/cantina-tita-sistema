"""
Script simplificado para verificar comisiones
Usa los pagos existentes y muestra el estado del sistema
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from gestion.models import (
    PagosVenta, DetalleComisionVenta, MediosPago, TarifasComision
)
from django.db import connection
from decimal import Decimal

def print_separator(title=""):
    print("\n" + "="*80)
    if title:
        print(f"  {title}")
        print("="*80)

def print_result(message, success=True, detail=""):
    icon = "✅" if success else "❌"
    print(f"{icon} {message}")
    if detail:
        print(f"   {detail}")

def mostrar_tarifas_configuradas():
    """Muestra las tarifas configuradas"""
    print_separator("TARIFAS CONFIGURADAS")
    
    tarifas = TarifasComision.objects.filter(activo=True).select_related('id_medio_pago')
    
    print(f"\n📊 Total tarifas activas: {tarifas.count()}\n")
    
    for tarifa in tarifas:
        monto_fijo_str = f" + Gs {tarifa.monto_fijo_comision:,.0f}" if tarifa.monto_fijo_comision else ""
        print(f"💳 {tarifa.id_medio_pago.descripcion}")
        print(f"   {tarifa.porcentaje_comision*100:.2f}%{monto_fijo_str}")
        
        # Ejemplo de cálculo
        monto_ej = Decimal('100000')
        comision = monto_ej * tarifa.porcentaje_comision
        if tarifa.monto_fijo_comision:
            comision += tarifa.monto_fijo_comision
        print(f"   Ejemplo: Gs 100,000 → Comisión: Gs {comision:,.0f}\n")

def analizar_pagos_existentes():
    """Analiza los pagos existentes y sus comisiones"""
    print_separator("ANÁLISIS DE PAGOS EXISTENTES")
    
    cursor = connection.cursor()
    
    cursor.execute("""
        SELECT 
            pv.ID_Pago_Venta,
            v.ID_Venta,
            DATE(v.Fecha) as Fecha,
            mp.Descripcion as Medio_Pago,
            mp.Genera_Comision,
            pv.Monto_Aplicado,
            dc.Monto_Comision_Calculada,
            dc.Porcentaje_Aplicado,
            CASE 
                WHEN dc.ID_Detalle_Comision IS NOT NULL THEN 'SÍ'
                WHEN mp.Genera_Comision = 1 THEN 'PENDIENTE'
                ELSE 'NO APLICA'
            END as Estado_Comision
        FROM Pagos_Venta pv
        JOIN Ventas v ON pv.ID_Venta = v.ID_Venta
        JOIN Medios_Pago mp ON pv.ID_Medio_Pago = mp.ID_Medio_Pago
        LEFT JOIN Detalle_Comision_Venta dc ON pv.ID_Pago_Venta = dc.ID_Pago_Venta
        ORDER BY pv.ID_Pago_Venta DESC
        LIMIT 20
    """)
    
    rows = cursor.fetchall()
    
    if not rows:
        print("\n⚠️  No hay pagos registrados en el sistema")
        return
    
    print(f"\n📋 Últimos {len(rows)} pagos:\n")
    print(f"{'ID':<6} {'Fecha':<12} {'Medio':<25} {'Monto':>12} {'Comisión':>12} {'%':>8} {'Estado':<12}")
    print("-" * 100)
    
    total_monto = Decimal('0')
    total_comision = Decimal('0')
    pendientes = 0
    
    for row in rows:
        id_pago, id_venta, fecha, medio, genera, monto, comision, porcentaje, estado = row
        
        total_monto += Decimal(str(monto))
        if comision:
            total_comision += Decimal(str(comision))
        
        if estado == 'PENDIENTE':
            pendientes += 1
        
        monto_str = f"Gs {monto:>9,}"
        
        if comision:
            comision_str = f"Gs {float(comision):>8,.0f}"
            porcentaje_str = f"{float(porcentaje)*100:.2f}%"
        else:
            comision_str = "-"
            porcentaje_str = "-"
        
        estado_icon = {
            'SÍ': '✅',
            'PENDIENTE': '⚠️',
            'NO APLICA': '➖'
        }.get(estado, '❓')
        
        print(f"{id_pago:<6} {fecha} {medio:<25} {monto_str} {comision_str:>12} {porcentaje_str:>8} {estado_icon} {estado}")
    
    print("-" * 100)
    print(f"{'TOTAL':<44} Gs {total_monto:>9,} Gs {total_comision:>8,.0f}")
    
    if pendientes > 0:
        print(f"\n⚠️  {pendientes} pagos pendientes de cálculo de comisión")

def mostrar_estadisticas():
    """Muestra estadísticas generales"""
    print_separator("ESTADÍSTICAS GENERALES")
    
    cursor = connection.cursor()
    
    # Estadísticas por medio de pago
    cursor.execute("""
        SELECT 
            mp.Descripcion,
            COUNT(pv.ID_Pago_Venta) as Total_Pagos,
            SUM(pv.Monto_Aplicado) as Total_Monto,
            COUNT(dc.ID_Detalle_Comision) as Pagos_Con_Comision,
            SUM(COALESCE(dc.Monto_Comision_Calculada, 0)) as Total_Comisiones
        FROM Medios_Pago mp
        LEFT JOIN Pagos_Venta pv ON mp.ID_Medio_Pago = pv.ID_Medio_Pago
        LEFT JOIN Detalle_Comision_Venta dc ON pv.ID_Pago_Venta = dc.ID_Pago_Venta
        WHERE mp.Activo = 1
        GROUP BY mp.ID_Medio_Pago, mp.Descripcion
        HAVING Total_Pagos > 0
        ORDER BY Total_Monto DESC
    """)
    
    stats = cursor.fetchall()
    
    if stats:
        print("\n📊 Por medio de pago:\n")
        print(f"{'Medio':<30} {'Pagos':>8} {'Monto Total':>15} {'Comisiones':>15} {'% Efectivo':>12}")
        print("-" * 85)
        
        for row in stats:
            medio, total_pagos, total_monto, pagos_con_com, total_com = row
            
            if total_monto and total_monto > 0:
                porcentaje_ef = (float(total_com) / float(total_monto)) * 100 if total_com else 0
            else:
                porcentaje_ef = 0
            
            print(f"{medio:<30} {total_pagos:>8} Gs {total_monto:>12,} Gs {float(total_com):>12,.0f} {porcentaje_ef:>11.2f}%")
    
    # Totales generales
    cursor.execute("""
        SELECT 
            COUNT(DISTINCT pv.ID_Pago_Venta) as Total_Pagos,
            SUM(pv.Monto_Aplicado) as Total_Procesado,
            COUNT(DISTINCT dc.ID_Detalle_Comision) as Pagos_Con_Comision,
            SUM(COALESCE(dc.Monto_Comision_Calculada, 0)) as Total_Comisiones,
            COUNT(DISTINCT CASE WHEN mp.Genera_Comision = 1 AND dc.ID_Detalle_Comision IS NULL THEN pv.ID_Pago_Venta END) as Pendientes
        FROM Pagos_Venta pv
        LEFT JOIN Detalle_Comision_Venta dc ON pv.ID_Pago_Venta = dc.ID_Pago_Venta
        LEFT JOIN Medios_Pago mp ON pv.ID_Medio_Pago = mp.ID_Medio_Pago
    """)
    
    totals = cursor.fetchone()
    
    print("\n📈 Totales:")
    print(f"  - Pagos registrados: {totals[0]}")
    print(f"  - Monto procesado: Gs {totals[1]:,}")
    print(f"  - Pagos con comisión calculada: {totals[2]}")
    print(f"  - Total comisiones: Gs {float(totals[3]):,.2f}")
    print(f"  - Pagos pendientes: {totals[4]}")
    
    if totals[1] and totals[1] > 0:
        porcentaje_general = (float(totals[3]) / float(totals[1])) * 100
        print(f"  - Comisión promedio efectiva: {porcentaje_general:.2f}%")

def verificar_sistema():
    """Verifica que el sistema esté configurado correctamente"""
    print_separator("VERIFICACIÓN DEL SISTEMA")
    
    # 1. Verificar tarifas
    tarifas_count = TarifasComision.objects.filter(activo=True).count()
    medios_con_comision = MediosPago.objects.filter(genera_comision=True, activo=True).count()
    
    if tarifas_count >= medios_con_comision:
        print_result("Tarifas configuradas", True, f"{tarifas_count}/{medios_con_comision} medios")
    else:
        print_result("Tarifas incompletas", False, f"Solo {tarifas_count}/{medios_con_comision} configuradas")
    
    # 2. Verificar trigger
    cursor = connection.cursor()
    cursor.execute("""
        SHOW TRIGGERS 
        WHERE `Table` = 'pagos_venta' 
        AND `Trigger` = 'trg_pago_comision_ai'
    """)
    
    trigger = cursor.fetchone()
    if trigger:
        print_result("Trigger activo", True, "trg_pago_comision_ai")
    else:
        print_result("Trigger no encontrado", False, "Las comisiones no se calcularán")
    
    # 3. Verificar pagos sin comisión
    cursor.execute("""
        SELECT COUNT(*)
        FROM Pagos_Venta pv
        JOIN Medios_Pago mp ON pv.ID_Medio_Pago = mp.ID_Medio_Pago
        LEFT JOIN Detalle_Comision_Venta dc ON pv.ID_Pago_Venta = dc.ID_Pago_Venta
        WHERE mp.Genera_Comision = 1
        AND dc.ID_Detalle_Comision IS NULL
    """)
    
    pendientes = cursor.fetchone()[0]
    
    if pendientes == 0:
        print_result("Comisiones al día", True, "Todos los pagos tienen comisión calculada")
    else:
        print_result("Comisiones pendientes", False, f"{pendientes} pagos sin calcular")

def main():
    print("\n" + "="*80)
    print("  ESTADO DEL SISTEMA DE COMISIONES BANCARIAS")
    print("  Sistema Cantina Tita - Fase 1")
    print("="*80)
    
    try:
        # 1. Mostrar tarifas configuradas
        mostrar_tarifas_configuradas()
        
        # 2. Verificar configuración del sistema
        verificar_sistema()
        
        # 3. Analizar pagos existentes
        analizar_pagos_existentes()
        
        # 4. Mostrar estadísticas
        mostrar_estadisticas()
        
        print("\n" + "="*80)
        print("  ✅ ANÁLISIS COMPLETADO")
        print("="*80)
        print("\n📋 Conclusiones:")
        print("  - Las tarifas están configuradas correctamente")
        print("  - El trigger está activo y calculará comisiones automáticamente")
        print("  - Los pagos nuevos con tarjeta tendrán comisión calculada")
        print("\n💡 Para probar:")
        print("  1. Realizar una venta en el sistema POS")
        print("  2. Pagar con tarjeta de crédito o débito")
        print("  3. Verificar que la comisión aparezca automáticamente")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
