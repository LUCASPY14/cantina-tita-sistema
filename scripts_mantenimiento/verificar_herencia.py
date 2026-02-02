import os
import ast
from pathlib import Path

def verificar_herencia_modelos():
    """Verifica que todos los modelos hereden de ManagedModel"""
    
    directorio = Path("gestion/models")
    problemas = []
    
    for archivo in directorio.glob("*.py"):
        if archivo.name == "__init__.py" or archivo.name == "base.py":
            continue
            
        print(f"\n🔍 Verificando: {archivo.name}")
        
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        try:
            tree = ast.parse(contenido)
            
            for nodo in ast.walk(tree):
                if isinstance(nodo, ast.ClassDef):
                    # Verificar herencia
                    for base in nodo.bases:
                        if isinstance(base, ast.Name):
                            if base.id == 'models.Model':
                                problemas.append(f"❌ {archivo.name}: Clase '{nodo.name}' hereda de models.Model (debe heredar de ManagedModel)")
                                print(f"   ⚠️  {nodo.name}: hereda de models.Model")
                            elif base.id == 'ManagedModel':
                                print(f"   ✅ {nodo.name}: hereda de ManagedModel")
                        elif isinstance(base, ast.Attribute):
                            if base.attr == 'Model':
                                problemas.append(f"❌ {archivo.name}: Clase '{nodo.name}' hereda de models.Model (debe heredar de ManagedModel)")
                                print(f"   ⚠️  {nodo.name}: hereda de models.Model")
        
        except SyntaxError as e:
            problemas.append(f"❌ {archivo.name}: Error de sintaxis: {e}")
    
    if problemas:
        print("\n" + "="*60)
        print("PROBLEMAS DETECTADOS:")
        print("="*60)
        for problema in problemas:
            print(problema)
        return False
    else:
        print("\n" + "="*60)
        print("✅ TODOS LOS MODELOS HEREDAN CORRECTAMENTE DE ManagedModel")
        print("="*60)
        return True

if __name__ == "__main__":
    verificar_herencia_modelos()
