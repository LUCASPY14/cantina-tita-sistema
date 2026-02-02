import os
import ast
from pathlib import Path

def corregir_herencias():
    """Corrige automáticamente las herencias de models.Model a ManagedModel"""
    
    directorio = Path("gestion/models")
    
    for archivo in directorio.glob("*.py"):
        if archivo.name == "__init__.py" or archivo.name == "base.py":
            continue
            
        print(f"\n🔧 Procesando: {archivo.name}")
        
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Verificar si importa ManagedModel
        if 'from .base import ManagedModel' not in contenido:
            # Agregar import si falta
            lineas = contenido.split('\n')
            nuevas_lineas = []
            import_agregado = False
            
            for linea in lineas:
                nuevas_lineas.append(linea)
                if 'from django.db import models' in linea and not import_agregado:
                    nuevas_lineas.append('from .base import ManagedModel')
                    import_agregado = True
            
            contenido = '\n'.join(nuevas_lineas)
            print(f"   ✅ Añadido import ManagedModel")
        
        # Corregir herencias
        if 'class ' in contenido and ('models.Model' in contenido or 'models.Model,' in contenido):
            # Reemplazar models.Model por ManagedModel
            contenido_original = contenido
            contenido = contenido.replace('models.Model)', 'ManagedModel)')
            contenido = contenido.replace('models.Model,', 'ManagedModel,')
            
            if contenido != contenido_original:
                print(f"   ✅ Corregidas herencias de models.Model a ManagedModel")
        
        # Guardar cambios
        with open(archivo, 'w', encoding='utf-8') as f:
            f.write(contenido)
    
    print("\n" + "="*60)
    print("✅ CORRECCIONES APLICADAS")
    print("="*60)

def verificar_correcciones():
    """Verifica que las correcciones fueron aplicadas"""
    
    directorio = Path("gestion/models")
    problemas = []
    
    for archivo in directorio.glob("*.py"):
        if archivo.name == "__init__.py" or archivo.name == "base.py":
            continue
            
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Verificar que no haya models.Model en herencias
        if 'class ' in contenido:
            lineas = contenido.split('\n')
            for i, linea in enumerate(lineas):
                if 'class ' in linea and 'models.Model' in linea:
                    problemas.append(f"❌ {archivo.name}: Línea {i+1} - {linea.strip()}")
    
    if problemas:
        print("\n⚠️  PROBLEMAS PERSISTENTES:")
        for problema in problemas:
            print(problema)
        return False
    else:
        print("\n✅ TODAS LAS HERENCIAS CORREGIDAS")
        return True

if __name__ == "__main__":
    print("="*60)
    print("CORRECTOR DE HERENCIAS DE MODELOS")
    print("="*60)
    
    # 1. Eliminar archivo conciliacion.py si existe
    conciliacion_path = Path("gestion/models/conciliacion.py")
    if conciliacion_path.exists():
        conciliacion_path.unlink()
        print("🗑️  Eliminado: gestion/models/conciliacion.py")
    
    # 2. Aplicar correcciones
    corregir_herencias()
    
    # 3. Verificar
    verificar_correcciones()
