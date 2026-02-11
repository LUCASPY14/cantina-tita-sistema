#!/usr/bin/env python
"""
Script para validar todas las URLs del admin y detectar modelos con errores
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.apps import apps
from gestion import models as gestion_models

# Lista de todos los modelos de gestion
MODELOS = [
    'TipoCliente', 'ListaPrecios', 'Categoria', 'UnidadMedida', 'Impuesto',
    'TipoRolGeneral', 'Cliente', 'Hijo', 'Tarjeta', 'Producto', 'StockUnico',
    'Proveedor', 'Empleado', 'DatosEmpresa', 'PreciosPorLista', 'CostosHistoricos',
    'HistoricoPrecios', 'Compras', 'DetalleCompra', 'CtaCorrienteProv', 'CargasSaldo',
    'UsuariosWebClientes', 'PuntosExpedicion', 'Timbrados', 'DocumentosTributarios',
    'DatosFacturacionElect', 'DatosFacturacionFisica', 'MovimientosStock', 'StockUnico',
    'AjustesInventario', 'DetalleAjuste', 'Cajas', 'CierresCaja', 'MediosPago',
    'TiposPago', 'Ventas', 'DetalleVenta', 'PagosVenta', 'CtaCorriente',
    'NotasCredito', 'DetalleNota', 'ConciliacionPagos', 'PlanesAlmuerzo',
    'SuscripcionesAlmuerzo', 'PagosAlmuerzoMensual', 'RegistroConsumoAlmuerzo',
    'TarifasComision', 'DetalleComisionVenta', 'AlertasSistema', 'SolicitudesNotificacion',
    'AuditoriaEmpleados', 'AuditoriaUsuariosWeb', 'AuditoriaComisiones',
    'VistaStockAlerta', 'VistaSaldoClientes'
]

print("\n" + "="*80)
print("VALIDACIÓN DE MODELOS Y URLS DEL ADMIN".center(80))
print("="*80 + "\n")

exitosos = []
fallidos = []

for nombre_modelo in MODELOS:
    try:
        # Obtener el modelo
        modelo = getattr(gestion_models, nombre_modelo)
        
        # Intentar hacer una consulta simple
        modelo.objects.first()
        
        exitosos.append(nombre_modelo)
        print(f"✅ {nombre_modelo:<35} OK")
        
    except AttributeError:
        print(f"⚠️  {nombre_modelo:<35} MODELO NO EXISTE")
        fallidos.append((nombre_modelo, "Modelo no encontrado"))
        
    except Exception as e:
        error_msg = str(e)
        if "Unknown column" in error_msg or "Columna desconocida" in error_msg:
            # Extraer el nombre del campo problemático
            if "'" in error_msg:
                campo = error_msg.split("'")[1]
            else:
                campo = "desconocido"
            print(f"❌ {nombre_modelo:<35} ERROR: Campo '{campo}' no existe")
            fallidos.append((nombre_modelo, f"Campo inexistente: {campo}"))
        else:
            print(f"❌ {nombre_modelo:<35} ERROR: {error_msg[:50]}")
            fallidos.append((nombre_modelo, error_msg[:100]))

print("\n" + "="*80)
print(f"RESUMEN: {len(exitosos)} OK | {len(fallidos)} CON ERRORES")
print("="*80 + "\n")

if fallidos:
    print("MODELOS QUE REQUIEREN CORRECCIÓN:\n")
    for modelo, error in fallidos:
        print(f"  • {modelo}: {error}")
    print(f"\nTotal a corregir: {len(fallidos)} modelos")
else:
    print("🎉 ¡TODOS LOS MODELOS ESTÁN CORRECTOS!")

print("\n" + "="*80 + "\n")
