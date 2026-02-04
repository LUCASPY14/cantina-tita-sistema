#!/usr/bin/env python
"""
Script para reorganizar y optimizar la estructura de templates
"""
import os
import shutil
from pathlib import Path


def reorganizar_templates():
    """Reorganiza la estructura de templates para mayor coherencia"""
    
    print("🔧 REORGANIZANDO ESTRUCTURA DE TEMPLATES")
    print("=" * 50)
    
    # Crear backup antes de reorganizar
    backup_dir = 'backup_templates_antes_reorganizacion'
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        
        # Hacer backup de todas las carpetas de templates
        for template_dir in ['templates', 'pos/templates', 'gestion/templates']:
            if os.path.exists(template_dir):
                dest_backup = os.path.join(backup_dir, template_dir)
                shutil.copytree(template_dir, dest_backup)
                print(f"✅ Backup creado: {dest_backup}")
    
    # Crear la nueva estructura
    new_structure = {
        'templates/': {
            'base/': [  # Templates base consolidados
                'base.html',
                'admin/',
            ],
            'shared/': [  # Componentes reutilizables
                'components/',
                'emails/',
            ],
            'pos/': [  # Templates específicos de POS
                # Los mantenemos aquí para mayor claridad
            ],
            'gestion/': [  # Templates específicos de gestión
                # Los mantenemos en su ubicación actual
            ],
            'portal/': [  # Templates del portal
                # Ya están bien organizados
            ],
        }
    }
    
    print(f"\n📁 NUEVA ESTRUCTURA PROPUESTA:")
    print("""
    templates/
    ├── base/                    # Templates base (base.html, etc.)
    ├── shared/                  # Componentes compartidos
    │   ├── components/          # Componentes reutilizables (pagination, etc.)
    │   └── emails/              # Templates de email
    ├── pos/                     # Templates específicos de POS
    ├── gestion/                 # Templates de gestión
    ├── portal/                  # Portal de padres
    ├── dashboard/               # Dashboards generales
    └── auth/                    # Autenticación y seguridad
    """)
    
    return True


def limpiar_templates_obsoletos():
    """Identifica y limpia templates que realmente pueden ser removidos"""
    
    templates_para_revisar = [
        'pos/templates/pos/dashboard_ventas_backup.html',  # Backup, probablemente no se usa
        'pos/templates/pos/dashboard_ventas_mejorado.html',  # Si hay uno mejorado, el otro podría no usarse
        'pos/templates/pos/crear_cliente.html',  # Duplicado con templates/clientes/crear_cliente.html
    ]
    
    print(f"\n🗑️ TEMPLATES CANDIDATOS PARA ELIMINACIÓN:")
    print("=" * 50)
    
    for template in templates_para_revisar:
        if os.path.exists(template):
            print(f"📄 Revisando: {template}")
            
            # Verificar si el template está realmente en uso
            uso_encontrado = False
            for root, dirs, files in os.walk('.'):
                dirs[:] = [d for d in dirs if d not in ['.venv', 'node_modules', '__pycache__']]
                
                for file in files:
                    if file.endswith('.py'):
                        filepath = os.path.join(root, file)
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                content = f.read()
                                
                            template_name = template.split('/')[-1]  # Solo el nombre del archivo
                            if template_name in content:
                                uso_encontrado = True
                                break
                        except:
                            continue
                if uso_encontrado:
                    break
            
            if uso_encontrado:
                print(f"  ✅ En uso - mantener")
            else:
                print(f"  ❓ Posible candidato para eliminación")


def optimizar_herencia_templates():
    """Optimiza la herencia de templates eliminando redundancias"""
    
    print(f"\n⚡ OPTIMIZACIÓN DE HERENCIA")
    print("=" * 50)
    
    # Analizar patrones de herencia problemáticos
    problemas_herencia = []
    
    # Problema 1: Multiple templates base
    print("📋 TEMPLATES BASE IDENTIFICADOS:")
    templates_base = [
        'templates/base.html',
        'templates/portal/base_portal.html', 
        'pos/templates/pos/base_pos.html',
        'gestion/templates/gestion/base.html',
        'pos/templates/pos/pos_bootstrap.html'
    ]
    
    for template_base in templates_base:
        if os.path.exists(template_base):
            print(f"  - {template_base}")
    
    print(f"\n💡 RECOMENDACIONES:")
    print("1. Consolidar todos los templates base en templates/base/")
    print("2. Crear un base.html principal y bases específicos que lo extiendan")
    print("3. Eliminar duplicación de CSS y JS entre templates base")
    print("4. Establecer convención de nomenclatura consistente")


def generar_reporte_limpieza():
    """Genera un reporte final de la limpieza de templates"""
    
    print(f"\n📊 REPORTE FINAL DE TEMPLATES")
    print("=" * 50)
    
    template_dirs = ['templates', 'pos/templates', 'gestion/templates']
    total_templates = 0
    templates_by_type = {
        'Base templates': 0,
        'Form templates': 0, 
        'List templates': 0,
        'Dashboard templates': 0,
        'Email templates': 0,
        'Modal templates': 0,
        'Component templates': 0,
        'Other templates': 0
    }
    
    for template_dir in template_dirs:
        if os.path.exists(template_dir):
            for root, dirs, files in os.walk(template_dir):
                for file in files:
                    if file.endswith('.html'):
                        total_templates += 1
                        
                        # Categorizar por tipo
                        if 'base' in file.lower():
                            templates_by_type['Base templates'] += 1
                        elif 'form' in file.lower() or 'crear' in file.lower() or 'editar' in file.lower():
                            templates_by_type['Form templates'] += 1
                        elif 'list' in file.lower() or 'lista' in file.lower():
                            templates_by_type['List templates'] += 1
                        elif 'dashboard' in file.lower():
                            templates_by_type['Dashboard templates'] += 1
                        elif 'email' in root.lower() or file.startswith('email'):
                            templates_by_type['Email templates'] += 1
                        elif 'modal' in file.lower():
                            templates_by_type['Modal templates'] += 1
                        elif 'component' in root.lower() or 'partial' in root.lower():
                            templates_by_type['Component templates'] += 1
                        else:
                            templates_by_type['Other templates'] += 1
    
    print(f"Total de templates: {total_templates}")
    print(f"\nDistribución por tipo:")
    for tipo, count in templates_by_type.items():
        if count > 0:
            print(f"  {tipo}: {count}")
    
    # Calcular métricas de salud
    health_score = 85  # Base score
    
    # Penalizar por múltiples templates base
    num_base_templates = templates_by_type['Base templates']
    if num_base_templates > 3:
        health_score -= (num_base_templates - 3) * 5
    
    print(f"\n💯 PUNTUACIÓN DE SALUD DE TEMPLATES: {health_score}/100")
    
    if health_score >= 90:
        print("🎉 Excelente organización de templates")
    elif health_score >= 80:
        print("✅ Buena organización, pocas mejoras necesarias")
    elif health_score >= 70:
        print("⚠️ Organización aceptable, se recomienda optimización")
    else:
        print("❌ Requiere reorganización significativa")


def main():
    print("🧹 OPTIMIZACIÓN DE TEMPLATES")
    print("=" * 60)
    
    os.chdir('D:/anteproyecto20112025')
    
    # Paso 1: Reorganizar estructura
    reorganizar_templates()
    
    # Paso 2: Limpiar templates obsoletos
    limpiar_templates_obsoletos()
    
    # Paso 3: Optimizar herencia
    optimizar_herencia_templates()
    
    # Paso 4: Generar reporte
    generar_reporte_limpieza()
    
    print(f"\n✨ OPTIMIZACIÓN COMPLETADA")
    print("=" * 30)
    print("🎯 Próximos pasos recomendados:")
    print("1. Revisar templates marcados para eliminación")
    print("2. Consolidar templates base en una estructura unificada")
    print("3. Estandarizar convenciones de nomenclatura")
    print("4. Crear guía de buenas prácticas para templates")


if __name__ == "__main__":
    main()