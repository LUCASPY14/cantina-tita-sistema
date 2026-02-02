import re
from pathlib import Path

def verificar_posicion_clases():
    """Verifica que las clases estén definidas después de los imports"""
    
    directorio = Path("gestion/models")
    problemas = []
    
    for archivo in directorio.glob("*.py"):
        if archivo.name in ["__init__.py", "base.py"]:
            continue
            
        print(f"\n🔍 Analizando: {archivo.name}")
        
        with open(archivo, 'r', encoding='utf-8') as f:
            lineas = f.readlines()
        
        # Encontrar posición del último import
        ultimo_import = -1
        for i, linea in enumerate(lineas):
            if linea.strip().startswith(('import ', 'from ')):
                ultimo_import = i
        
        # Verificar posición de cada clase
        for i, linea in enumerate(lineas):
            if linea.strip().startswith('class '):
                nombre_clase = linea.split('class ')[1].split('(')[0].strip()
                
                if i <= ultimo_import:
                    problemas.append(f"❌ {archivo.name}: Clase '{nombre_clase}' definida antes de imports (línea {i+1})")
                    print(f"   ⚠️  {nombre_clase} en línea {i+1} (imports hasta línea {ultimo_import+1})")
                else:
                    print(f"   ✅ {nombre_clase} en línea {i+1} (después de imports)")
        
        # Verificar si hay código antes de imports
        for i, linea in enumerate(lineas):
            if i > ultimo_import:
                break
            if (linea.strip() and 
                not linea.strip().startswith(('#', 'from ', 'import ')) and
                not linea.strip().startswith('"""') and
                not linea.strip().startswith("'''") ):
                problemas.append(f"❌ {archivo.name}: Código no-comentario antes de imports (línea {i+1}): {linea.strip()[:50]}...")
    
    if problemas:
        print("\n" + "="*60)
        print("PROBLEMAS DE POSICIÓN DETECTADOS:")
        print("="*60)
        for problema in problemas:
            print(problema)
        return False
    else:
        print("\n" + "="*60)
        print("✅ TODAS LAS CLASES EN POSICIÓN CORRECTA")
        print("="*60)
        return True

def corregir_posiciones():
    """Corrige automáticamente las posiciones de las clases"""
    
    directorio = Path("gestion/models")
    
    for archivo in directorio.glob("*.py"):
        if archivo.name in ["__init__.py", "base.py"]:
            continue
            
        print(f"\n🔧 Procesando: {archivo.name}")
        
        with open(archivo, 'r', encoding='utf-8') as f:
            lineas = f.readlines()
        
        # Separar imports, clases y otras líneas
        imports = []
        clases = []
        otras_lineas = []
        en_docstring = False
        
        for linea in lineas:
            # Manejar docstrings multilínea
            if '"""' in linea or "'''" in linea:
                if not en_docstring:
                    en_docstring = True
                else:
                    en_docstring = False
            
            # Si estamos en docstring o es un comentario/import
            if en_docstring or linea.strip().startswith('#') or linea.strip().startswith('from ') or linea.strip().startswith('import '):
                imports.append(linea)
            elif linea.strip().startswith('class '):
                clases.append(linea)
            else:
                otras_lineas.append(linea)
        
        # Reconstruir archivo en orden correcto
        lineas_corregidas = []
        
        # 1. Agregar imports y comentarios iniciales
        lineas_corregidas.extend(imports)
        
        # 2. Agregar una línea en blanco después de imports
        if imports and imports[-1].strip():
            lineas_corregidas.append('\n')
        
        # 3. Agregar clases
        lineas_corregidas.extend(clases)
        
        # 4. Agregar otras líneas (métodos, funciones, etc.)
        if otras_lineas:
            lineas_corregidas.append('\n')
            lineas_corregidas.extend(otras_lineas)
        
        # Guardar cambios
        with open(archivo, 'w', encoding='utf-8') as f:
            f.writelines(lineas_corregidas)
        
        print(f"   ✅ Reordenado: {len(imports)} líneas de import, {len(clases)} clases")

def buscar_clases_duplicadas():
    """Busca clases duplicadas en los archivos"""
    
    directorio = Path("gestion/models")
    clases_encontradas = {}
    duplicados = []
    
    for archivo in directorio.glob("*.py"):
        if archivo.name in ["__init__.py", "base.py"]:
            continue
        
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Buscar definiciones de clase
        patron = r'class (\w+)\(.*?\):'
        matches = re.findall(patron, contenido)
        
        for clase in matches:
            if clase in clases_encontradas:
                duplicados.append(f"❌ Clase '{clase}' definida en {clases_encontradas[clase]} y {archivo.name}")
            else:
                clases_encontradas[clase] = archivo.name
    
    if duplicados:
        print("\n" + "="*60)
        print("CLASES DUPLICADAS DETECTADAS:")
        print("="*60)
        for duplicado in duplicados:
            print(duplicado)
        return False
    else:
        print("\n✅ NO HAY CLASES DUPLICADAS")
        return True

if __name__ == "__main__":
    print("="*60)
    print("VERIFICACIÓN Y CORRECCIÓN DE POSICIONES")
    print("="*60)
    
    # 1. Buscar clases duplicadas
    print("\n1. Buscando clases duplicadas...")
    buscar_clases_duplicadas()
    
    # 2. Verificar posiciones actuales
    print("\n2. Verificando posiciones de clases...")
    if not verificar_posicion_clases():
        respuesta = input("\n¿Deseas corregir automáticamente las posiciones? (s/n): ")
        if respuesta.lower() == 's':
            print("\n3. Aplicando correcciones...")
            corregir_posiciones()
            print("\n✅ Correcciones aplicadas. Verificando nuevamente...")
            verificar_posicion_clases()
    
    print("\n" + "="*60)
    print("PROCESO COMPLETADO")
    print("="*60)
    print("\n🎯 Siguiente paso: python manage.py makemigrations gestion")
