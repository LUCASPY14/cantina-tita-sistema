"""
Script de Verificación - Modelos Django vs Base de Datos MySQL
================================================================

Este script verifica que los modelos Django estén correctamente sincronizados
con la estructura de las tablas MySQL después de la actualización.

Uso:
    python verificar_modelos.py

Fecha: 2025-12-02
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection
from gestion.models import (
    Ventas, DetalleVenta, NotasCreditoCliente, PagosVenta,
    UnidadMedida, Producto, Cliente, CargasSaldo, Compras,
    PagosProveedores, AplicacionPagosVentas, AplicacionPagosCompras,
    NotasCreditoProveedor, DetalleNotaCreditoProveedor
)

def obtener_columnas_db(tabla):
    """Obtiene las columnas de una tabla MySQL."""
    with connection.cursor() as cursor:
        cursor.execute(f"SHOW COLUMNS FROM {tabla}")
        return {row[0]: row[1] for row in cursor.fetchall()}

def obtener_campos_modelo(modelo):
    """Obtiene los campos de un modelo Django."""
    campos = {}
    for field in modelo._meta.get_fields():
        if hasattr(field, 'db_column') and field.db_column:
            campos[field.db_column] = field.__class__.__name__
        elif hasattr(field, 'name'):
            campos[field.name] = field.__class__.__name__
    return campos

def verificar_modelo(modelo, tabla):
    """Verifica que un modelo esté sincronizado con su tabla."""
    print(f"\n{'='*70}")
    print(f"Verificando: {modelo.__name__} → {tabla}")
    print('='*70)
    
    try:
        columnas_db = obtener_columnas_db(tabla)
        campos_modelo = obtener_campos_modelo(modelo)
        
        # Campos en DB pero no en modelo
        faltantes_en_modelo = set(columnas_db.keys()) - set(campos_modelo.keys())
        
        # Campos en modelo pero no en DB
        faltantes_en_db = set(campos_modelo.keys()) - set(columnas_db.keys())
        
        # Campos presentes en ambos
        campos_comunes = set(columnas_db.keys()) & set(campos_modelo.keys())
        
        print(f"✓ Columnas en DB: {len(columnas_db)}")
        print(f"✓ Campos en Modelo: {len(campos_modelo)}")
        print(f"✓ Campos comunes: {len(campos_comunes)}")
        
        if faltantes_en_modelo:
            print(f"\n⚠ Columnas en DB que faltan en modelo ({len(faltantes_en_modelo)}):")
            for col in sorted(faltantes_en_modelo):
                print(f"  - {col}: {columnas_db[col]}")
        
        if faltantes_en_db:
            print(f"\n⚠ Campos en modelo que no existen en DB ({len(faltantes_en_db)}):")
            for campo in sorted(faltantes_en_db):
                print(f"  - {campo}: {campos_modelo[campo]}")
        
        if not faltantes_en_modelo and not faltantes_en_db:
            print("\n✅ SINCRONIZADO PERFECTAMENTE")
            return True
        else:
            print("\n❌ HAY DIFERENCIAS")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False

def verificar_cambios_especificos():
    """Verifica cambios específicos de la actualización."""
    print("\n" + "="*70)
    print("VERIFICACIÓN DE CAMBIOS ESPECÍFICOS")
    print("="*70)
    
    cambios = []
    
    # 1. Ventas - nro_factura_venta
    try:
        from gestion.models import Ventas
        if hasattr(Ventas, 'nro_factura_venta'):
            cambios.append(("✅", "Ventas.nro_factura_venta existe"))
        else:
            cambios.append(("❌", "Ventas.nro_factura_venta NO existe"))
    except:
        cambios.append(("❌", "Error verificando Ventas.nro_factura_venta"))
    
    # 2. Ventas - saldo_pendiente
    try:
        if hasattr(Ventas, 'saldo_pendiente'):
            cambios.append(("✅", "Ventas.saldo_pendiente existe"))
        else:
            cambios.append(("❌", "Ventas.saldo_pendiente NO existe"))
    except:
        cambios.append(("❌", "Error verificando Ventas.saldo_pendiente"))
    
    # 3. Ventas - estado_pago
    try:
        if hasattr(Ventas, 'estado_pago'):
            cambios.append(("✅", "Ventas.estado_pago existe"))
        else:
            cambios.append(("❌", "Ventas.estado_pago NO existe"))
    except:
        cambios.append(("❌", "Error verificando Ventas.estado_pago"))
    
    # 4. DetalleVenta - precio_unitario (renombrado)
    try:
        if hasattr(DetalleVenta, 'precio_unitario'):
            cambios.append(("✅", "DetalleVenta.precio_unitario existe (renombrado)"))
        else:
            cambios.append(("❌", "DetalleVenta.precio_unitario NO existe"))
        
        if hasattr(DetalleVenta, 'precio_unitario_total'):
            cambios.append(("❌", "DetalleVenta.precio_unitario_total aún existe (debería eliminarse)"))
    except:
        cambios.append(("❌", "Error verificando DetalleVenta.precio_unitario"))
    
    # 5. NotasCreditoCliente - clase renombrada
    try:
        from gestion.models import NotasCreditoCliente
        cambios.append(("✅", "NotasCreditoCliente existe (renombrado de NotasCredito)"))
    except ImportError:
        cambios.append(("❌", "NotasCreditoCliente NO existe"))
    
    # 6. NotasCreditoCliente - observacion
    try:
        if hasattr(NotasCreditoCliente, 'observacion'):
            cambios.append(("✅", "NotasCreditoCliente.observacion existe"))
        else:
            cambios.append(("❌", "NotasCreditoCliente.observacion NO existe"))
    except:
        cambios.append(("❌", "Error verificando NotasCreditoCliente.observacion"))
    
    # 7. PagosVenta - estado
    try:
        if hasattr(PagosVenta, 'estado'):
            cambios.append(("✅", "PagosVenta.estado existe"))
        else:
            cambios.append(("❌", "PagosVenta.estado NO existe"))
    except:
        cambios.append(("❌", "Error verificando PagosVenta.estado"))
    
    # 8. UnidadMedida - id_unidad_de_medida
    try:
        if hasattr(UnidadMedida, 'id_unidad_de_medida'):
            cambios.append(("✅", "UnidadMedida.id_unidad_de_medida existe"))
        else:
            cambios.append(("❌", "UnidadMedida.id_unidad_de_medida NO existe"))
    except:
        cambios.append(("❌", "Error verificando UnidadMedida.id_unidad_de_medida"))
    
    # 9. Producto - codigo_barra
    try:
        if hasattr(Producto, 'codigo_barra'):
            cambios.append(("✅", "Producto.codigo_barra existe"))
        else:
            cambios.append(("❌", "Producto.codigo_barra NO existe"))
    except:
        cambios.append(("❌", "Error verificando Producto.codigo_barra"))
    
    # 10. Cliente - id_lista
    try:
        if hasattr(Cliente, 'id_lista'):
            cambios.append(("✅", "Cliente.id_lista existe"))
        else:
            cambios.append(("❌", "Cliente.id_lista NO existe"))
    except:
        cambios.append(("❌", "Error verificando Cliente.id_lista"))
    
    # 11. CargasSaldo - id_nota
    try:
        if hasattr(CargasSaldo, 'id_nota'):
            cambios.append(("✅", "CargasSaldo.id_nota existe"))
        else:
            cambios.append(("❌", "CargasSaldo.id_nota NO existe"))
    except:
        cambios.append(("❌", "Error verificando CargasSaldo.id_nota"))
    
    # 12. PagosProveedores - modelo nuevo
    try:
        from gestion.models import PagosProveedores
        cambios.append(("✅", "PagosProveedores existe (modelo nuevo)"))
    except ImportError:
        cambios.append(("❌", "PagosProveedores NO existe"))
    
    # 13. AplicacionPagosVentas - modelo nuevo
    try:
        from gestion.models import AplicacionPagosVentas
        cambios.append(("✅", "AplicacionPagosVentas existe (modelo nuevo)"))
    except ImportError:
        cambios.append(("❌", "AplicacionPagosVentas NO existe"))
    
    # 14. AplicacionPagosCompras - modelo nuevo
    try:
        from gestion.models import AplicacionPagosCompras
        cambios.append(("✅", "AplicacionPagosCompras existe (modelo nuevo)"))
    except ImportError:
        cambios.append(("❌", "AplicacionPagosCompras NO existe"))
    
    # 15. NotasCreditoProveedor - modelo nuevo
    try:
        from gestion.models import NotasCreditoProveedor
        cambios.append(("✅", "NotasCreditoProveedor existe (modelo nuevo)"))
    except ImportError:
        cambios.append(("❌", "NotasCreditoProveedor NO existe"))
    
    # 16. DetalleNotaCreditoProveedor - modelo nuevo
    try:
        from gestion.models import DetalleNotaCreditoProveedor
        cambios.append(("✅", "DetalleNotaCreditoProveedor existe (modelo nuevo)"))
    except ImportError:
        cambios.append(("❌", "DetalleNotaCreditoProveedor NO existe"))
    
    # Mostrar resultados
    exitosos = 0
    fallidos = 0
    
    for estado, mensaje in cambios:
        print(f"{estado} {mensaje}")
        if estado == "✅":
            exitosos += 1
        else:
            fallidos += 1
    
    print(f"\n{'='*70}")
    print(f"RESUMEN: {exitosos} exitosos, {fallidos} fallidos de {len(cambios)} verificaciones")
    print('='*70)
    
    return fallidos == 0

def main():
    """Función principal."""
    print("\n" + "="*70)
    print("VERIFICACIÓN DE MODELOS DJANGO - SINCRONIZACIÓN CON BASE DE DATOS")
    print("="*70)
    
    modelos_a_verificar = [
        (Ventas, 'ventas'),
        (DetalleVenta, 'detalle_venta'),
        (NotasCreditoCliente, 'notas_credito_cliente'),
        (PagosVenta, 'pagos_venta'),
        (UnidadMedida, 'unidades_medida'),
        (Producto, 'productos'),
        (Cliente, 'clientes'),
        (CargasSaldo, 'cargas_saldo'),
        (Compras, 'compras'),
        (PagosProveedores, 'pagos_proveedores'),
        (AplicacionPagosVentas, 'aplicacion_pagos_ventas'),
        (AplicacionPagosCompras, 'aplicacion_pagos_compras'),
        (NotasCreditoProveedor, 'notas_credito_proveedor'),
        (DetalleNotaCreditoProveedor, 'detalle_nota_credito_proveedor'),
    ]
    
    resultados = []
    
    for modelo, tabla in modelos_a_verificar:
        resultado = verificar_modelo(modelo, tabla)
        resultados.append((modelo.__name__, resultado))
    
    # Verificar cambios específicos
    cambios_ok = verificar_cambios_especificos()
    
    # Resumen final
    print("\n" + "="*70)
    print("RESUMEN FINAL")
    print("="*70)
    
    exitosos = sum(1 for _, ok in resultados if ok)
    total = len(resultados)
    
    print(f"\nModelos verificados: {total}")
    print(f"✅ Sincronizados: {exitosos}")
    print(f"❌ Con diferencias: {total - exitosos}")
    
    if exitosos == total and cambios_ok:
        print("\n🎉 TODOS LOS MODELOS ESTÁN PERFECTAMENTE SINCRONIZADOS 🎉")
        return 0
    else:
        print("\n⚠ HAY MODELOS CON DIFERENCIAS - REVISAR ARRIBA")
        return 1

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n❌ Verificación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ ERROR FATAL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
