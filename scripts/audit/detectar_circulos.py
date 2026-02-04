import ast
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt

def analizar_dependencias():
    """Analiza las dependencias entre módulos para detectar ciclos"""
    
    directorio = Path("gestion/models")
    grafo = nx.DiGraph()
    dependencias = {}
    
    # Analizar cada archivo
    for archivo in directorio.glob("*.py"):
        if archivo.name in ["__init__.py", "base.py"]:
            continue
            
        modulo = archivo.stem
        grafo.add_node(modulo)
        
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        imports_directos = set()
        
        # Buscar importaciones directas
        lineas = contenido.split('\n')
        for linea in lineas:
            if linea.strip().startswith('from .'):
                partes = linea.split('import')
                if len(partes) > 1:
                    modulo_importado = partes[0].replace('from .', '').strip()
                    imports_directos.add(modulo_importado)
        
        dependencias[modulo] = imports_directos
        
        for importado in imports_directos:
            grafo.add_edge(modulo, importado)
    
    # Detectar ciclos
    try:
        ciclos = list(nx.find_cycle(grafo))
        print("\n❌ CICLOS DETECTADOS:")
        for ciclo in ciclos:
            print(f"  {ciclo[0]} -> {ciclo[1]}")
        
        # Mostrar gráfico
        plt.figure(figsize=(10, 8))
        pos = nx.spring_layout(grafo)
        nx.draw(grafo, pos, with_labels=True, node_color='lightblue', 
                node_size=2000, font_size=10, font_weight='bold')
        plt.title("Grafo de Dependencias entre Módulos")
        plt.savefig('dependencias_modelos.png')
        print("\n📊 Gráfico guardado como 'dependencias_modelos.png'")
        
        return True, ciclos
    except nx.NetworkXNoCycle:
        print("\n✅ NO HAY CICLOS DE IMPORTACIÓN")
        return False, None

def recomendar_correcciones(ciclos):
    """Recomienda correcciones para los ciclos detectados"""
    
    print("\n🔧 RECOMENDACIONES DE CORRECCIÓN:")
    
    correcciones = {
        ('productos', 'compras'): "En productos.py, cambiar 'Compras' por 'compras.Compras' (string)",
        ('compras', 'productos'): "En compras.py, cambiar 'Producto' por 'productos.Producto' (string)",
        ('productos', 'ventas'): "En productos.py, cambiar 'Ventas' por 'ventas.Ventas' (string)",
        ('ventas', 'productos'): "En ventas.py, cambiar 'Producto' por 'productos.Producto' (string)",
    }
    
    for origen, destino in ciclos:
        clave = (origen, destino)
        if clave in correcciones:
            print(f"  • {correcciones[clave]}")
        else:
            print(f"  • En {origen}.py, cambiar importación directa de '{destino}' a referencia de string")

if __name__ == "__main__":
    print("="*60)
    print("ANÁLISIS DE DEPENDENCIAS ENTRE MÓDULOS")
    print("="*60)
    
    hay_ciclos, ciclos = analizar_dependencias()
    
    if hay_ciclos:
        recomendar_correcciones(ciclos)
        print("\n📝 Resumen de correcciones necesarias:")
        print("  1. En relaciones ForeignKey/OneToOneField que causan ciclos,")
        print("     usar referencias de string en lugar de importaciones directas.")
        print("  2. Formato: models.ForeignKey('app.Model', ...)")
        print("  3. Para modelos en la misma app: models.ForeignKey('gestion.Model', ...)")
