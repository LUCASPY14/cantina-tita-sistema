#!/usr/bin/env python
"""
Script para corregir automáticamente db_column de uppercase a lowercase
en todos los modelos de Django que tienen problemas de case sensitivity.
"""
import os
import re
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

# Modelos que necesitan corrección según el reporte
MODELOS_CORREGIR = {
    'gestion': [
        'ListaPrecios', 'TipoCliente', 'Categoria', 'UnidadMedida', 'Impuesto',
        'TipoRolGeneral', 'MediosPago', 'TiposPago', 'Cliente', 'Empleado',
        'Producto', 'PreciosPorLista', 'HistoricoPrecios', 'Tarjeta',
        'AplicacionPagosVentas', 'Proveedor', 'Compras', 'DetalleCompra',
        'PagosProveedores', 'AplicacionPagosCompras', 'PuntosExpedicion',
        'Timbrados', 'DocumentosTributarios', 'TarjetaAutorizacion',
        'LogAutorizacion', 'HistorialGradoHijo', 'AjustesInventario',
        'Promocion', 'ProductoPromocion', 'CategoriaPromocion', 'Alergeno'
    ]
}

# Archivos de modelos en gestion
ARCHIVOS_MODELOS = {
    'gestion': [
        'backend/gestion/models.py',  # Archivo principal con la mayoría de modelos
    ]
}

def convertir_a_lowercase(db_column_value):
    """
    Convierte un valor de db_column de uppercase a lowercase.
    Ejemplos:
        'ID_Cliente' -> 'id_cliente'
        'Nombre_Lista' -> 'nombre_lista'
        'Activo' -> 'activo'
    """
    # Si está entre comillas, extraer el valor
    if db_column_value.startswith("'") or db_column_value.startswith('"'):
        match = re.match(r"['\"](.+)['\"]", db_column_value)
        if match:
            original = match.group(1)
            lowercase = original.lower()
            # Mantener el tipo de comillas original
            quote = db_column_value[0]
            return f"{quote}{lowercase}{quote}"
    
    return db_column_value.lower()

def procesar_archivo(archivo_path):
    """
    Procesa un archivo de modelos y corrige todos los db_column.
    """
    if not os.path.exists(archivo_path):
        print(f"  ⏭️  Archivo no existe: {archivo_path}")
        return False
    
    with open(archivo_path, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    contenido_original = contenido
    
    # Patrón para encontrar db_column='...' o db_column="..."
    patron = r"(db_column\s*=\s*)(['\"][^'\"]+['\"])"
    
    def reemplazar(match):
        prefijo = match.group(1)  # "db_column="
        valor_original = match.group(2)  # "'ID_Cliente'" 
        valor_lowercase = convertir_a_lowercase(valor_original)
        
        # Solo cambiar si realmente hay uppercase
        if valor_original != valor_lowercase:
            print(f"    🔄 {valor_original} → {valor_lowercase}")
            return prefijo + valor_lowercase
        return match.group(0)
    
    contenido_nuevo = re.sub(patron, reemplazar, contenido)
    
    if contenido_nuevo != contenido_original:
        # Hacer backup
        backup_path = archivo_path + '.backup'
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(contenido_original)
        
        # Guardar archivo corregido
        with open(archivo_path, 'w', encoding='utf-8') as f:
            f.write(contenido_nuevo)
        
        print(f"  ✅ Archivo corregido: {archivo_path}")
        print(f"  💾 Backup guardado: {backup_path}")
        return True
    else:
        print(f"  ✓  Sin cambios necesarios: {archivo_path}")
        return False

def main():
    print("="*80)
    print("🔧 CORRECCIÓN AUTOMÁTICA DE db_column")
    print("="*80)
    print()
    
    archivos_modificados = 0
    
    for app, archivos in ARCHIVOS_MODELOS.items():
        print(f"\n📦 Procesando app: {app}")
        print("-" * 80)
        
        for archivo in archivos:
            archivo_completo = os.path.join('D:\\anteproyecto20112025', archivo)
            print(f"\n📄 {archivo}")
            
            if procesar_archivo(archivo_completo):
                archivos_modificados += 1
    
    print("\n" + "="*80)
    print("📊 RESUMEN")
    print("="*80)
    print(f"Archivos modificados: {archivos_modificados}")
    print()
    print("🎯 PRÓXIMOS PASOS:")
    print("1. Revisar los cambios realizados")
    print("2. Reiniciar el servidor Django")
    print("3. Probar el acceso al admin")
    print()

if __name__ == '__main__':
    main()
