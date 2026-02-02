import re
from pathlib import Path

def corregir_referencias_foreignkey():
    """Corrige automáticamente las referencias de ForeignKey"""
    
    directorio = Path("gestion/models")
    
    # Mapeo de referencias de string a importaciones directas
    patrones_correccion = [
        (r"'clientes\.(\w+)'", r'\1'),
        (r"'productos\.(\w+)'", r'\1'),
        (r"'ventas\.(\w+)'", r'\1'),
        (r"'compras\.(\w+)'", r'\1'),
        (r"'empleados\.(\w+)'", r'\1'),
        (r"'tarjetas\.(\w+)'", r'\1'),
        (r"'fiscal\.(\w+)'", r'\1'),
        (r"'almuerzos\.(\w+)'", r'\1'),
        (r"'seguridad\.(\w+)'", r'\1'),
        (r"'portal\.(\w+)'", r'\1'),
        (r"'promociones\.(\w+)'", r'\1'),
        (r"'alergenos\.(\w+)'", r'\1'),
        (r"'catalogos\.(\w+)'", r'\1'),
    ]
    
    for archivo in directorio.glob("*.py"):
        if archivo.name in ["__init__.py", "base.py"]:
            continue
            
        print(f"\n🔧 Procesando: {archivo.name}")
        
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        contenido_original = contenido
        
        # Aplicar correcciones
        for patron, reemplazo in patrones_correccion:
            contenido = re.sub(patron, reemplazo, contenido)
        
        # Agregar imports necesarios basados en las referencias usadas
        lineas = contenido.split('\n')
        imports_necesarios = set()
        
        for linea in lineas:
            if 'models.ForeignKey(' in linea or 'models.OneToOneField(' in linea:
                # Buscar referencias que necesiten import
                for clase in ['Cliente', 'Hijo', 'Producto', 'Empleado', 'Tarjeta', 
                            'Ventas', 'Compras', 'CargasSaldo', 'NotasCreditoCliente',
                            'PagosVenta', 'ListaPrecios', 'MovimientosStock']:
                    if clase in linea and f'from .' not in contenido:
                        imports_necesarios.add(clase)
        
        # Reconstruir archivo con imports
        if imports_necesarios:
            nuevas_lineas = []
            import_agregado = False
            
            for linea in lineas:
                nuevas_lineas.append(linea)
                if 'from django.db import models' in linea and not import_agregado:
                    # Agregar imports necesarios
                    for clase in sorted(imports_necesarios):
                        # Determinar de qué módulo importar
                        modulo_origen = determinar_modulo_origen(clase, directorio)
                        if modulo_origen and modulo_origen != archivo.stem:
                            nuevas_lineas.append(f'from .{modulo_origen} import {clase}')
                    import_agregado = True
            
            contenido = '\n'.join(nuevas_lineas)
        
        if contenido != contenido_original:
            with open(archivo, 'w', encoding='utf-8') as f:
                f.write(contenido)
            print(f"   ✅ Corregidas referencias en {archivo.name}")

def determinar_modulo_origen(clase, directorio):
    """Determina de qué módulo importar una clase"""
    # Mapeo conocido
    mapeo = {
        'Cliente': 'clientes',
        'Hijo': 'clientes',
        'RestriccionesHijos': 'clientes',
        'Producto': 'productos',
        'StockUnico': 'productos',
        'MovimientosStock': 'productos',
        'PreciosPorLista': 'productos',
        'CostosHistoricos': 'productos',
        'HistoricoPrecios': 'productos',
        'Empleado': 'empleados',
        'Tarjeta': 'tarjetas',
        'CargasSaldo': 'tarjetas',
        'ConsumoTarjeta': 'tarjetas',
        'Ventas': 'ventas',
        'DetalleVenta': 'ventas',
        'PagosVenta': 'ventas',
        'NotasCreditoCliente': 'ventas',
        'AutorizacionSaldoNegativo': 'ventas',
        'Proveedor': 'compras',
        'Compras': 'compras',
        'ConciliacionPagos': 'compras',
        'ListaPrecios': 'catalogos',
        'TiposPago': 'catalogos',
        'MediosPago': 'catalogos',
        'TarifasComision': 'catalogos',
        'CierresCaja': 'fiscal',
        'TipoAlmuerzo': 'almuerzos',
    }
    
    return mapeo.get(clase)

if __name__ == "__main__":
    print("="*60)
    print("CORRECCIÓN DE REFERENCIAS FOREIGNKEY")
    print("="*60)
    corregir_referencias_foreignkey()
    print("\n" + "="*60)
    print("✅ CORRECCIONES APLICADAS")
    print("="*60)
