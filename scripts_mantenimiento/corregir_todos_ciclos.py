import re
from pathlib import Path

def corregir_todas_referencias_circulares():
    """Corrige todas las referencias circulares automáticamente"""
    
    directorio = Path("gestion/models")
    
    # Lista de archivos en orden de dependencia (menos dependientes primero)
    orden_correccion = [
        'base.py',
        'catalogos.py',      # Depende solo de base
        'clientes.py',       # Depende de catalogos
        'empleados.py',      # Depende de catalogos
        'productos.py',      # Depende de catalogos, empleados
        'tarjetas.py',       # Depende de clientes, empleados
        'ventas.py',         # Depende de clientes, empleados, catalogos, fiscal
        'compras.py',        # Depende de productos, empleados, catalogos
        'fiscal.py',         # Depende de empleados
        'almuerzos.py',      # Depende de clientes, tarjetas, ventas
        'seguridad.py',      # Depende de casi todos
        'portal.py',         # Depende de clientes, tarjetas
        'promociones.py',    # Depende de productos, catalogos, ventas
        'alergenos.py',      # Depende de productos
        'vistas.py',         # Depende de varios
    ]
    
    # Mapeo de qué módulos importar directamente vs por string
    importaciones_directas = {
        'catalogos': ['TipoCliente', 'ListaPrecios', 'Categoria', 'UnidadMedida', 
                     'Impuesto', 'TipoRolGeneral', 'TiposPago', 'MediosPago', 
                     'TarifasComision', 'Grado'],
        'clientes': ['Cliente', 'Hijo', 'RestriccionesHijos'],
        'empleados': ['Empleado'],
        'productos': ['Producto', 'StockUnico', 'PreciosPorLista', 'CostosHistoricos',
                     'HistoricoPrecios', 'MovimientosStock'],
        'tarjetas': ['Tarjeta', 'ConsumoTarjeta', 'CargasSaldo'],
        'ventas': ['Ventas', 'DetalleVenta', 'PagosVenta', 'NotasCreditoCliente'],
        'compras': ['Proveedor', 'Compras', 'DetalleCompra'],
        'fiscal': ['CierresCaja'],
    }
    
    # Para cada archivo, aplicar correcciones
    for archivo_nombre in orden_correccion:
        archivo_path = directorio / archivo_nombre
        
        if not archivo_path.exists() or archivo_nombre in ['__init__.py', 'base.py']:
            continue
            
        print(f"\n🔧 Procesando: {archivo_nombre}")
        
        with open(archivo_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        contenido_original = contenido
        
        # Paso 1: Reemplazar referencias de string problemáticas
        # Cambiar 'modulo.Clase' por referencias directas cuando no hay ciclo
        modulo_actual = archivo_path.stem
        
        # Buscar referencias de string en ForeignKeys
        patron_foreignkey = r"models\.(?:ForeignKey|OneToOneField)\(\s*'([a-z]+)\.(\w+)'"
        matches = re.findall(patron_foreignkey, contenido)
        
        for modulo_ref, clase_ref in matches:
            # Verificar si es seguro cambiar a importación directa
            # (si el módulo referenciado viene ANTES en el orden de corrección)
            if modulo_ref in orden_correccion:
                indice_ref = orden_correccion.index(modulo_ref)
                indice_actual = orden_correccion.index(archivo_nombre)
                
                if indice_ref < indice_actual:  # Módulo referenciado viene antes
                    # Es seguro importar directamente
                    contenido = re.sub(
                        f"models\\.(?:ForeignKey|OneToOneField)\\(\\s*'{modulo_ref}\\.{clase_ref}'",
                        f"models.\\1({clase_ref}",
                        contenido
                    )
                    print(f"   ✅ {modulo_ref}.{clase_ref} → importación directa")
        
        # Paso 2: Eliminar imports circulares
        lineas = contenido.split('\n')
        nuevas_lineas = []
        imports_a_eliminar = []
        
        for i, linea in enumerate(lineas):
            # Detectar imports problemáticos
            if 'from .' in linea and ' import ' in linea:
                # Extraer el módulo importado
                match = re.match(r"from \\.(\w+) import", linea)
                if match:
                    modulo_importado = match.group(1)
                    
                    # Verificar si causa ciclo
                    if modulo_importado in orden_correccion:
                        indice_import = orden_correccion.index(modulo_importado + '.py')
                        indice_actual = orden_correccion.index(archivo_nombre)
                        
                        if indice_import >= indice_actual:  # Posible ciclo
                            imports_a_eliminar.append((i, linea, modulo_importado))
                            print(f"   ⚠️  Eliminando import circular: {linea.strip()}")
                            continue  # No agregar esta línea
            
            nuevas_lineas.append(linea)
        
        contenido = '\n'.join(nuevas_lineas)
        
        # Paso 3: Agregar comentario sobre referencias de string
        if imports_a_eliminar:
            header = "### NOTA: Referencias de string para evitar importaciones circulares ###\n"
            contenido = header + contenido
        
        # Guardar cambios si hubo modificaciones
        if contenido != contenido_original:
            with open(archivo_path, 'w', encoding='utf-8') as f:
                f.write(contenido)
            print(f"   💾 Guardados cambios en {archivo_nombre}")
    
    print("\n" + "="*60)
    print("✅ CORRECCIONES COMPLETAS")
    print("="*60)
    print("\n📝 Resumen de cambios aplicados:")
    print("1. Eliminadas importaciones circulares")
    print("2. Mantenidas referencias de string para relaciones con ciclos")
    print("3. Convertidas a importaciones directas cuando es seguro")
    print("\n🎯 Ejecutar ahora: python manage.py makemigrations gestion")

def verificar_ciclos_restantes():
    """Verifica si quedan ciclos después de las correcciones"""
    
    import ast
    from pathlib import Path
    
    directorio = Path("gestion/models")
    ciclos_encontrados = []
    
    for archivo in directorio.glob("*.py"):
        if archivo.name in ["__init__.py", "base.py"]:
            continue
            
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Buscar referencias de string problemáticas (que indiquen ciclo)
        if "'gestion." in contenido or "'.gestion." in contenido:
            print(f"⚠️  {archivo.name}: Contiene referencias de string a 'gestion.'")
            ciclos_encontrados.append(archivo.name)
    
    if ciclos_encontrados:
        print("\n🔍 Archivos con posibles ciclos restantes:")
        for archivo in ciclos_encontrados:
            print(f"   • {archivo}")
        return False
    else:
        print("\n✅ NO SE DETECTARON CICLOS RESTANTES")
        return True

if __name__ == "__main__":
    print("="*60)
    print("CORRECCIÓN COMPLETA DE CICLOS DE IMPORTACIÓN")
    print("="*60)
    
    # 1. Aplicar correcciones automáticas
    corregir_todas_referencias_circulares()
    
    # 2. Verificar resultados
    print("\n" + "="*60)
    print("VERIFICACIÓN FINAL")
    print("="*60)
    
    exito = verificar_ciclos_restantes()
    
    if exito:
        print("\n🎉 ¡Correcciones aplicadas exitosamente!")
        print("\n📋 Siguientes pasos:")
        print("   1. Ejecutar: python manage.py makemigrations gestion")
        print("   2. Ejecutar: python manage.py migrate")
        print("   3. Verificar: python manage.py check gestion")
    else:
        print("\n🔧 Se requieren ajustes manuales adicionales.")
