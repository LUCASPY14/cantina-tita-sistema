import ast
from pathlib import Path

def validar_estructura():
    """Validación completa de la estructura de modelos"""
    
    directorio = Path("gestion/models")
    errores = []
    advertencias = []
    exitos = []
    
    print("="*60)
    print("VALIDACIÓN FINAL DE ESTRUCTURA DE MODELOS")
    print("="*60)
    
    # Lista de archivos esperados
    archivos_esperados = [
        'base.py', 'catalogos.py', 'clientes.py', 'productos.py',
        'empleados.py', 'tarjetas.py', 'ventas.py', 'compras.py',
        'fiscal.py', 'almuerzos.py', 'seguridad.py', 'portal.py',
        'promociones.py', 'alergenos.py', 'vistas.py', '__init__.py'
    ]
    
    # Verificar archivos
    print("\n📁 VERIFICANDO ARCHIVOS:")
    for archivo in archivos_esperados:
        ruta = directorio / archivo
        if ruta.exists():
            exitos.append(f"✅ {archivo}")
        else:
            errores.append(f"❌ FALTA: {archivo}")
    
    # Verificar cada archivo
    for archivo in directorio.glob("*.py"):
        if archivo.name == "__init__.py":
            continue
            
        print(f"\n🔍 ANALIZANDO: {archivo.name}")
        
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Verificar import de ManagedModel
        if archivo.name != "base.py":
            if 'from .base import ManagedModel' not in contenido:
                errores.append(f"❌ {archivo.name}: No importa ManagedModel")
            else:
                exitos.append(f"✅ {archivo.name}: Importa ManagedModel")
        
        # Contar clases
        try:
            tree = ast.parse(contenido)
            clases = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
            
            # Verificar herencia de cada clase
            for clase in clases:
                for base in clase.bases:
                    if isinstance(base, ast.Name):
                        if base.id == 'ManagedModel':
                            exitos.append(f"✅ {archivo.name}.{clase.name}: Hereda de ManagedModel")
                        elif base.id == 'models.Model':
                            errores.append(f"❌ {archivo.name}.{clase.name}: Hereda de models.Model")
        
        except SyntaxError as e:
            errores.append(f"❌ {archivo.name}: Error de sintaxis - {e}")
    
    # Mostrar resultados
    print("\n" + "="*60)
    print("RESULTADOS:")
    print("="*60)
    
    if exitos:
        print("\n✅ ÉXITOS:")
        for exito in exitos[:10]:  # Mostrar primeros 10
            print(f"  {exito}")
        if len(exitos) > 10:
            print(f"  ... y {len(exitos)-10} más")
    
    if advertencias:
        print("\n⚠️  ADVERTENCIAS:")
        for adv in advertencias:
            print(f"  {adv}")
    
    if errores:
        print("\n❌ ERRORES CRÍTICOS:")
        for error in errores:
            print(f"  {error}")
        print("\n" + "="*60)
        print("❌ VALIDACIÓN FALLIDA")
        return False
    else:
        print("\n" + "="*60)
        print("✅ VALIDACIÓN EXITOSA")
        return True

if __name__ == "__main__":
    if validar_estructura():
        print("\n🎉 ¡Estructura de modelos validada correctamente!")
        print("📋 Pasos siguientes:")
        print("   1. Ejecutar: python manage.py makemigrations gestion")
        print("   2. Ejecutar: python manage.py migrate")
        print("   3. Verificar: python manage.py check gestion")
    else:
        print("\n🔧 Se requieren correcciones antes de continuar.")
