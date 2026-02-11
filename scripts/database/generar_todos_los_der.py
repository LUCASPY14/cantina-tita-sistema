"""
Script master para ejecutar todos los generadores de DER
Ejecuta en secuencia:
1. Verificación de dependencias
2. Generación de DER Completo (Lógico y Físico)
3. Generación de DER Modular
4. Generación de reporte consolidado
"""

import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime


def check_dependencies():
    """Verifica que todas las dependencias estén instaladas"""
    print("="*70)
    print("VERIFICANDO DEPENDENCIAS")
    print("="*70)
    
    dependencies = {
        'sqlalchemy': 'SQLAlchemy',
        'pymysql': 'PyMySQL',
        'graphviz': 'Graphviz (Python)',
        'decouple': 'Python Decouple'
    }
    
    missing = []
    
    for module, name in dependencies.items():
        try:
            __import__(module)
            print(f"✓ {name} instalado")
        except ImportError:
            print(f"✗ {name} NO instalado")
            missing.append(module)
    
    # Verificar Graphviz del sistema
    try:
        result = subprocess.run(['dot', '-V'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Graphviz (sistema) instalado: {result.stderr.strip()}")
        else:
            print("✗ Graphviz (sistema) NO instalado o no está en PATH")
            missing.append('graphviz-system')
    except FileNotFoundError:
        print("✗ Graphviz (sistema) NO instalado o no está en PATH")
        missing.append('graphviz-system')
    
    if missing:
        print("\n" + "="*70)
        print("DEPENDENCIAS FALTANTES")
        print("="*70)
        
        if 'graphviz-system' in missing:
            print("\n⚠ Graphviz (sistema) no está instalado o no está en PATH")
            print("Descargue e instale desde: https://graphviz.org/download/")
            print("Luego reinicie su terminal/IDE")
        
        python_missing = [m for m in missing if m != 'graphviz-system']
        if python_missing:
            print(f"\n⚠ Instale las dependencias de Python:")
            print(f"pip install {' '.join(python_missing)}")
            print("\nO use el archivo de requisitos:")
            print("pip install -r requirements_der.txt")
        
        return False
    
    print("\n✓ Todas las dependencias están instaladas correctamente")
    return True


def run_script(script_name, description):
    """Ejecuta un script de Python"""
    print("\n" + "="*70)
    print(f"EJECUTANDO: {description}")
    print("="*70)
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        print(result.stdout)
        
        if result.returncode != 0:
            print(f"✗ Error al ejecutar {script_name}")
            print(result.stderr)
            return False
        
        print(f"✓ {description} completado exitosamente")
        return True
        
    except Exception as e:
        print(f"✗ Error ejecutando {script_name}: {e}")
        return False


def generate_consolidated_report():
    """Genera un reporte consolidado en HTML"""
    print("\n" + "="*70)
    print("GENERANDO REPORTE CONSOLIDADO")
    print("="*70)
    
    output_dir = Path('diagramas_der')
    
    # Buscar todos los archivos PNG generados
    png_files = sorted(output_dir.glob('*.png'))
    
    if not png_files:
        print("✗ No se encontraron diagramas generados")
        return False
    
    # Generar HTML
    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DER - Base de Datos CantinatitaDB</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .section {{
            margin-bottom: 50px;
        }}
        
        .section h2 {{
            color: #1e3c72;
            font-size: 2em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }}
        
        .diagram-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 30px;
            margin-top: 20px;
        }}
        
        .diagram-card {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }}
        
        .diagram-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0,0,0,0.2);
        }}
        
        .diagram-card h3 {{
            color: #2a5298;
            margin-bottom: 15px;
            font-size: 1.3em;
        }}
        
        .diagram-card img {{
            width: 100%;
            height: auto;
            border-radius: 8px;
            border: 2px solid #ddd;
            cursor: pointer;
            transition: border-color 0.3s;
        }}
        
        .diagram-card img:hover {{
            border-color: #667eea;
        }}
        
        .stats {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        
        .stats h3 {{
            font-size: 1.8em;
            margin-bottom: 15px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        
        .stat-item {{
            background: rgba(255,255,255,0.2);
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        
        .stat-item .number {{
            font-size: 3em;
            font-weight: bold;
            display: block;
            margin-bottom: 5px;
        }}
        
        .stat-item .label {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 30px;
            text-align: center;
            color: #666;
            border-top: 1px solid #ddd;
        }}
        
        .modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.9);
            padding: 20px;
        }}
        
        .modal-content {{
            position: relative;
            margin: auto;
            max-width: 95%;
            max-height: 95%;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .modal-content img {{
            max-width: 100%;
            max-height: 90vh;
            border-radius: 8px;
        }}
        
        .close {{
            position: absolute;
            top: 20px;
            right: 40px;
            color: white;
            font-size: 40px;
            font-weight: bold;
            cursor: pointer;
            z-index: 1001;
        }}
        
        .close:hover {{
            color: #667eea;
        }}
        
        @media (max-width: 768px) {{
            .diagram-grid {{
                grid-template-columns: 1fr;
            }}
            
            .header h1 {{
                font-size: 1.8em;
            }}
            
            .section h2 {{
                font-size: 1.5em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Diagramas Entidad-Relación</h1>
            <h2>Base de Datos: CantinatitaDB</h2>
            <p>Generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M:%S')}</p>
        </div>
        
        <div class="content">
"""
    
    # Leer estadísticas si existen
    stats_file = output_dir / 'estadisticas_bd.txt'
    if stats_file.exists():
        with open(stats_file, 'r', encoding='utf-8') as f:
            stats_content = f.read()
            
            # Extraer números de las estadísticas
            import re
            total_tablas = re.search(r'Total de tablas: (\d+)', stats_content)
            total_columnas = re.search(r'Total de columnas: (\d+)', stats_content)
            total_pks = re.search(r'Total de Primary Keys: (\d+)', stats_content)
            total_fks = re.search(r'Total de Foreign Keys: (\d+)', stats_content)
            
            if total_tablas:
                html_content += f"""
            <div class="stats">
                <h3>📈 Estadísticas de la Base de Datos</h3>
                <div class="stats-grid">
                    <div class="stat-item">
                        <span class="number">{total_tablas.group(1)}</span>
                        <span class="label">Tablas</span>
                    </div>
                    <div class="stat-item">
                        <span class="number">{total_columnas.group(1) if total_columnas else 'N/A'}</span>
                        <span class="label">Columnas</span>
                    </div>
                    <div class="stat-item">
                        <span class="number">{total_pks.group(1) if total_pks else 'N/A'}</span>
                        <span class="label">Primary Keys</span>
                    </div>
                    <div class="stat-item">
                        <span class="number">{total_fks.group(1) if total_fks else 'N/A'}</span>
                        <span class="label">Foreign Keys</span>
                    </div>
                </div>
            </div>
"""
    
    # Categorizar diagramas
    diagrams = {
        'Diagramas Principales': [],
        'Diagramas por Módulo': []
    }
    
    for png in png_files:
        if 'Modulo' in png.name:
            diagrams['Diagramas por Módulo'].append(png)
        else:
            diagrams['Diagramas Principales'].append(png)
    
    # Agregar secciones
    for section_name, files in diagrams.items():
        if not files:
            continue
            
        html_content += f"""
            <div class="section">
                <h2>{section_name}</h2>
                <div class="diagram-grid">
"""
        
        for png in sorted(files):
            # Formatear nombre para mostrar
            display_name = png.stem.replace('_', ' ').replace('DER', 'DER:')
            
            html_content += f"""
                    <div class="diagram-card">
                        <h3>{display_name}</h3>
                        <img src="{png.name}" alt="{display_name}" onclick="openModal(this.src)">
                    </div>
"""
        
        html_content += """
                </div>
            </div>
"""
    
    # Cerrar HTML
    html_content += f"""
        </div>
        
        <div class="footer">
            <p><strong>Sistema de Gestión de Cantina Escolar - Cantina Tita</strong></p>
            <p>Diagramas generados automáticamente con Python, SQLAlchemy y Graphviz</p>
            <p>© {datetime.now().year} - Todos los derechos reservados</p>
        </div>
    </div>
    
    <!-- Modal para ver imágenes ampliadas -->
    <div id="imageModal" class="modal" onclick="closeModal()">
        <span class="close">&times;</span>
        <div class="modal-content">
            <img id="modalImage" src="" alt="">
        </div>
    </div>
    
    <script>
        function openModal(src) {{
            document.getElementById('imageModal').style.display = 'block';
            document.getElementById('modalImage').src = src;
        }}
        
        function closeModal() {{
            document.getElementById('imageModal').style.display = 'none';
        }}
        
        // Cerrar modal con ESC
        document.addEventListener('keydown', function(event) {{
            if (event.key === 'Escape') {{
                closeModal();
            }}
        }});
    </script>
</body>
</html>
"""
    
    # Guardar HTML
    html_file = output_dir / 'index_diagramas.html'
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✓ Reporte HTML generado: {html_file}")
    print(f"  Total de diagramas: {len(png_files)}")
    return str(html_file)


def main():
    """Función principal"""
    print("\n")
    print("="*70)
    print("GENERADOR MASTER DE DER - CANTINATITADB")
    print("="*70)
    print("Este script ejecutará todos los generadores de DER en secuencia")
    print("="*70)
    
    start_time = datetime.now()
    
    # 1. Verificar dependencias
    if not check_dependencies():
        print("\n✗ Proceso abortado: Faltan dependencias")
        return False
    
    # 2. Generar DER Completo
    if not run_script('generar_der_completo.py', 'Generador DER Completo'):
        print("\n⚠ Advertencia: Error en DER Completo")
    
    # 3. Generar DER Modular
    if not run_script('generar_der_modular.py', 'Generador DER Modular'):
        print("\n⚠ Advertencia: Error en DER Modular")
    
    # 4. Generar reporte consolidado
    html_file = generate_consolidated_report()
    
    # Resumen final
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("\n" + "="*70)
    print("PROCESO COMPLETADO")
    print("="*70)
    print(f"Tiempo total: {duration:.2f} segundos")
    
    output_dir = Path('diagramas_der')
    if output_dir.exists():
        png_count = len(list(output_dir.glob('*.png')))
        print(f"\nArchivos generados: {png_count} diagramas PNG")
        print(f"Directorio de salida: {output_dir.absolute()}")
        
        if html_file:
            print(f"\n📄 Reporte HTML: {html_file}")
            print(f"   Abrir en navegador para ver todos los diagramas")
    
    print("\n✓ Todos los diagramas han sido generados exitosamente")
    print("="*70 + "\n")
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
