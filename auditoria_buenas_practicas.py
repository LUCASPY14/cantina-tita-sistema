#!/usr/bin/env python
"""
🔍 AUDITORÍA Y BUENAS PRÁCTICAS - Sistema Cantina Tita
═══════════════════════════════════════════════════════

Este script analiza todo el proyecto y sugiere mejoras basadas en:
- PEP 8 (estilo de código Python)
- Django Best Practices
- Seguridad
- Performance
- Mantenibilidad
- Organización de código

Fecha: 2 Febrero 2026
"""
import os
import sys
import re
import ast
from pathlib import Path
from collections import defaultdict, Counter
import django

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

class CodigoAnalyzer:
    """Analizador de código y buenas prácticas"""
    
    def __init__(self):
        self.issues = defaultdict(list)
        self.stats = defaultdict(int)
        self.recommendations = []
    
    def analyze_project(self):
        """Análisis completo del proyecto"""
        print("🔍 INICIANDO AUDITORÍA DE BUENAS PRÁCTICAS")
        print("═" * 60)
        
        # 1. Estructura general
        self.analyze_project_structure()
        
        # 2. Archivos Python
        self.analyze_python_files()
        
        # 3. Configuración Django
        self.analyze_django_settings()
        
        # 4. Modelos Django
        self.analyze_models()
        
        # 5. Vistas Django  
        self.analyze_views()
        
        # 6. Templates
        self.analyze_templates()
        
        # 7. Seguridad
        self.analyze_security()
        
        # 8. Performance
        self.analyze_performance()
        
        # 9. Generar reporte
        self.generate_report()
    
    def analyze_project_structure(self):
        """Analiza la estructura general del proyecto"""
        print("\n📁 1. ESTRUCTURA DEL PROYECTO")
        print("-" * 40)
        
        required_files = {
            'manage.py': 'Script principal Django',
            'requirements.txt': 'Dependencias del proyecto',
            '.env': 'Variables de entorno',
            '.gitignore': 'Archivos ignorados por Git',
            'README.md': 'Documentación principal'
        }
        
        missing_files = []
        for file, desc in required_files.items():
            if (BASE_DIR / file).exists():
                print(f"  ✅ {file}: {desc}")
            else:
                print(f"  ❌ {file}: FALTANTE - {desc}")
                missing_files.append(file)
        
        # Verificar estructura de apps
        apps_found = []
        for item in BASE_DIR.iterdir():
            if item.is_dir() and (item / 'apps.py').exists():
                apps_found.append(item.name)
                print(f"  ✅ App Django: {item.name}")
        
        self.stats['apps_count'] = len(apps_found)
        self.stats['missing_files'] = len(missing_files)
        
        if missing_files:
            self.issues['estructura'].extend(missing_files)
    
    def analyze_python_files(self):
        """Analiza archivos Python para estilo PEP 8 y buenas prácticas"""
        print("\n🐍 2. ANÁLISIS DE CÓDIGO PYTHON")
        print("-" * 40)
        
        python_files = list(BASE_DIR.rglob('*.py'))
        self.stats['python_files'] = len(python_files)
        
        issues_count = 0
        for py_file in python_files:
            if self._should_skip_file(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                file_issues = self._analyze_python_content(py_file, content)
                if file_issues:
                    issues_count += len(file_issues)
                    
            except Exception as e:
                print(f"  ⚠️  Error analizando {py_file}: {e}")
        
        print(f"  📊 Archivos Python: {len(python_files)}")
        print(f"  📊 Issues encontrados: {issues_count}")
    
    def _analyze_python_content(self, filepath, content):
        """Analiza contenido de un archivo Python"""
        issues = []
        lines = content.split('\n')
        
        # 1. Imports organizados
        import_issues = self._check_imports_organization(lines)
        if import_issues:
            issues.extend(import_issues)
            
        # 2. Líneas muy largas (PEP 8: max 79 chars)
        for i, line in enumerate(lines, 1):
            if len(line) > 120:  # Más flexible que PEP 8 estricto
                issues.append(f"Línea {i}: Demasiado larga ({len(line)} chars)")
        
        # 3. Funciones sin docstring
        if 'def ' in content:
            function_issues = self._check_docstrings(content)
            issues.extend(function_issues)
        
        # 4. TODO y FIXME pendientes
        todo_count = content.count('TODO') + content.count('FIXME')
        if todo_count > 0:
            issues.append(f"TODOs/FIXMEs pendientes: {todo_count}")
        
        if issues:
            self.issues['python_style'][str(filepath)] = issues
        
        return issues
    
    def _check_imports_organization(self, lines):
        """Verifica organización de imports según PEP 8"""
        issues = []
        import_sections = {'stdlib': [], 'third_party': [], 'local': []}
        current_section = None
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if not (line.startswith('import ') or line.startswith('from ')):
                break
                
            # Clasificar import
            if line.startswith('from django') or line.startswith('import django'):
                section = 'third_party'
            elif '.' in line and ('from .' in line or 'from gestion' in line):
                section = 'local'
            else:
                section = 'stdlib'
            
            import_sections[section].append((i+1, line))
        
        # Verificar orden: stdlib -> third_party -> local
        expected_order = ['stdlib', 'third_party', 'local']
        last_seen = -1
        
        for section in expected_order:
            if import_sections[section]:
                first_line_num = import_sections[section][0][0]
                if first_line_num < last_seen:
                    issues.append(f"Imports desordenados: {section} debería ir después")
                last_seen = max(line_num for line_num, _ in import_sections[section])
        
        return issues
    
    def _check_docstrings(self, content):
        """Verifica presencia de docstrings en funciones"""
        issues = []
        
        # Buscar funciones sin docstring
        function_pattern = r'def\s+(\w+)\s*\([^)]*\):'
        functions = re.findall(function_pattern, content)
        
        for func_name in functions:
            # Buscar si tiene docstring inmediatamente después
            func_start = content.find(f'def {func_name}(')
            if func_start != -1:
                # Buscar docstring en las siguientes líneas
                after_def = content[func_start:func_start+500]  # Primeros 500 chars
                if '"""' not in after_def and "'''" not in after_def:
                    if not func_name.startswith('_'):  # Skip private methods
                        issues.append(f"Función '{func_name}' sin docstring")
        
        return issues
    
    def analyze_django_settings(self):
        """Analiza configuración de Django"""
        print("\n⚙️  3. CONFIGURACIÓN DJANGO")
        print("-" * 40)
        
        settings_file = BASE_DIR / 'cantina_project' / 'settings.py'
        if not settings_file.exists():
            print("  ❌ settings.py no encontrado")
            return
            
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar configuraciones críticas
            checks = {
                'DEBUG': 'DEBUG = ' in content,
                'SECRET_KEY': 'SECRET_KEY' in content,
                'ALLOWED_HOSTS': 'ALLOWED_HOSTS' in content,
                'DATABASES': 'DATABASES' in content,
                'MIDDLEWARE': 'MIDDLEWARE' in content,
                'INSTALLED_APPS': 'INSTALLED_APPS' in content,
            }
            
            for setting, exists in checks.items():
                status = "✅" if exists else "❌"
                print(f"  {status} {setting}: {'Configurado' if exists else 'FALTANTE'}")
            
            # Verificar seguridad
            security_issues = []
            if 'DEBUG = True' in content:
                security_issues.append("DEBUG=True en settings.py (riesgo en producción)")
            
            if 'django.middleware.security.SecurityMiddleware' not in content:
                security_issues.append("SecurityMiddleware no configurado")
            
            if security_issues:
                self.issues['security'].extend(security_issues)
                
        except Exception as e:
            print(f"  ⚠️  Error analizando settings.py: {e}")
    
    def analyze_models(self):
        """Analiza modelos Django"""
        print("\n📊 4. MODELOS DJANGO")
        print("-" * 40)
        
        models_file = BASE_DIR / 'gestion' / 'models.py'
        if not models_file.exists():
            print("  ❌ models.py no encontrado")
            return
            
        try:
            with open(models_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Contar modelos
            model_count = content.count('class ') - content.count('class Meta:')
            print(f"  📊 Modelos definidos: {model_count}")
            
            # Verificar mejores prácticas en modelos
            model_issues = []
            
            # 1. __str__ methods
            str_methods = content.count('def __str__(')
            if str_methods < model_count * 0.8:  # Al menos 80% deberían tener __str__
                model_issues.append(f"Algunos modelos sin método __str__ ({str_methods}/{model_count})")
            
            # 2. Meta classes
            meta_classes = content.count('class Meta:')
            if meta_classes < model_count * 0.9:  # Al menos 90% deberían tener Meta
                model_issues.append(f"Algunos modelos sin clase Meta ({meta_classes}/{model_count})")
            
            # 3. Verbose names
            verbose_count = content.count('verbose_name')
            if verbose_count < model_count:
                model_issues.append("Algunos modelos sin verbose_name")
            
            if model_issues:
                self.issues['models'].extend(model_issues)
                
            self.stats['models_count'] = model_count
            
        except Exception as e:
            print(f"  ⚠️  Error analizando models.py: {e}")
    
    def analyze_views(self):
        """Analiza vistas Django"""
        print("\n👀 5. VISTAS DJANGO")
        print("-" * 40)
        
        view_files = list((BASE_DIR / 'gestion').glob('*views.py'))
        total_views = 0
        
        for view_file in view_files:
            try:
                with open(view_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                view_count = content.count('def ') - content.count('def __')
                total_views += view_count
                
                print(f"  📄 {view_file.name}: {view_count} vistas")
                
                # Verificar decoradores de seguridad
                security_decorators = [
                    '@login_required',
                    '@permission_required',
                    '@user_passes_test'
                ]
                
                has_security = any(dec in content for dec in security_decorators)
                if not has_security and view_count > 0:
                    self.issues['views'].append(f"{view_file.name}: Sin decoradores de seguridad")
                
            except Exception as e:
                print(f"  ⚠️  Error analizando {view_file}: {e}")
        
        print(f"  📊 Total de vistas: {total_views}")
        self.stats['views_count'] = total_views
    
    def analyze_templates(self):
        """Analiza templates HTML"""
        print("\n🎨 6. TEMPLATES HTML")
        print("-" * 40)
        
        template_dirs = [
            BASE_DIR / 'templates',
            BASE_DIR / 'gestion' / 'templates'
        ]
        
        total_templates = 0
        for template_dir in template_dirs:
            if template_dir.exists():
                templates = list(template_dir.rglob('*.html'))
                total_templates += len(templates)
                print(f"  📁 {template_dir.name}: {len(templates)} templates")
        
        print(f"  📊 Total templates: {total_templates}")
        self.stats['templates_count'] = total_templates
    
    def analyze_security(self):
        """Analiza aspectos de seguridad"""
        print("\n🔐 7. SEGURIDAD")
        print("-" * 40)
        
        # Verificar archivo .env
        env_file = BASE_DIR / '.env'
        if env_file.exists():
            print("  ✅ Archivo .env: Configurado")
            
            # Verificar si tiene contraseñas vacías
            with open(env_file, 'r') as f:
                env_content = f.read()
            
            if 'PASSWORD=' in env_content and 'PASSWORD=\\n' in env_content:
                self.issues['security'].append("Contraseñas vacías en .env")
        else:
            print("  ❌ Archivo .env: FALTANTE")
            self.issues['security'].append("Archivo .env no configurado")
        
        # Verificar .gitignore
        gitignore_file = BASE_DIR / '.gitignore'
        if gitignore_file.exists():
            with open(gitignore_file, 'r') as f:
                gitignore_content = f.read()
            
            critical_ignores = ['.env', '*.pyc', '__pycache__', 'db.sqlite3']
            missing_ignores = [item for item in critical_ignores if item not in gitignore_content]
            
            if missing_ignores:
                self.issues['security'].append(f"Archivos críticos no en .gitignore: {missing_ignores}")
        
        print(f"  📊 Issues de seguridad: {len(self.issues['security'])}")
    
    def analyze_performance(self):
        """Analiza aspectos de performance"""
        print("\n⚡ 8. PERFORMANCE")
        print("-" * 40)
        
        # Buscar queries N+1 potenciales
        view_files = list((BASE_DIR / 'gestion').glob('*views.py'))
        n_plus_one_issues = []
        
        for view_file in view_files:
            try:
                with open(view_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Patrones problemáticos
                patterns = {
                    'filter_sin_select': r'\\.filter\\([^)]+\\)(?!\\.select_related|\\.prefetch_related)',
                    'all_sin_select': r'\\.all\\(\\)(?!\\.select_related|\\.prefetch_related)',
                }
                
                for pattern_name, pattern in patterns.items():
                    matches = re.findall(pattern, content)
                    if matches:
                        n_plus_one_issues.append(f"{view_file.name}: {len(matches)} posibles N+1 queries")
                        
            except Exception as e:
                continue
        
        if n_plus_one_issues:
            self.issues['performance'].extend(n_plus_one_issues)
        
        print(f"  📊 Posibles issues N+1: {len(n_plus_one_issues)}")
    
    def generate_report(self):
        """Genera reporte final"""
        print("\n" + "═" * 60)
        print("📋 REPORTE FINAL - BUENAS PRÁCTICAS")
        print("═" * 60)
        
        # Resumen estadísticas
        print("\\n📊 ESTADÍSTICAS:")
        for key, value in self.stats.items():
            print(f"  • {key.replace('_', ' ').title()}: {value}")
        
        # Issues por categoría
        total_issues = sum(len(issues) for issues in self.issues.values())
        print(f"\\n⚠️  TOTAL DE ISSUES: {total_issues}")
        
        if total_issues == 0:
            print("\\n🎉 ¡EXCELENTE! No se encontraron issues importantes.")
            return
        
        for category, issues in self.issues.items():
            if issues:
                print(f"\\n📂 {category.upper()}:")
                for issue in issues[:5]:  # Mostrar primeros 5
                    print(f"  • {issue}")
                if len(issues) > 5:
                    print(f"  ... y {len(issues) - 5} más")
        
        # Recomendaciones
        self._generate_recommendations()
        
        # Guardar reporte
        self._save_report()
    
    def _generate_recommendations(self):
        """Genera recomendaciones específicas"""
        print("\\n💡 RECOMENDACIONES PRINCIPALES:")
        
        recommendations = []
        
        # Basadas en issues encontrados
        if 'python_style' in self.issues:
            recommendations.append("1. Reorganizar imports según PEP 8 (stdlib, third-party, local)")
            recommendations.append("2. Agregar docstrings a funciones públicas")
            recommendations.append("3. Limitar líneas a 120 caracteres máximo")
        
        if 'security' in self.issues:
            recommendations.append("4. Configurar todas las variables en .env")
            recommendations.append("5. Asegurar que .env esté en .gitignore")
            recommendations.append("6. Usar DEBUG=False en producción")
        
        if 'performance' in self.issues:
            recommendations.append("7. Optimizar queries con select_related() y prefetch_related()")
            recommendations.append("8. Implementar cache en vistas pesadas")
        
        if 'models' in self.issues:
            recommendations.append("9. Agregar __str__() y Meta class a todos los modelos")
            recommendations.append("10. Usar verbose_name para mejor admin interface")
        
        # Recomendaciones generales
        recommendations.extend([
            "11. Implementar tests unitarios para funciones críticas",
            "12. Documentar APIs con Swagger/OpenAPI",
            "13. Usar logging para errores y eventos importantes",
            "14. Configurar monitoreo de performance en producción",
            "15. Implementar backup automático de base de datos"
        ])
        
        for rec in recommendations[:10]:  # Mostrar top 10
            print(f"  {rec}")
    
    def _save_report(self):
        """Guarda reporte en archivo"""
        report_file = BASE_DIR / 'AUDITORIA_BUENAS_PRACTICAS.md'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# 🔍 AUDITORÍA DE BUENAS PRÁCTICAS - Sistema Cantina Tita\\n\\n")
            f.write(f"**Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\\n\\n")
            
            f.write("## 📊 ESTADÍSTICAS\\n\\n")
            for key, value in self.stats.items():
                f.write(f"- **{key.replace('_', ' ').title()}:** {value}\\n")
            
            f.write(f"\\n## ⚠️ ISSUES ENCONTRADOS: {sum(len(issues) for issues in self.issues.values())}\\n\\n")
            
            for category, issues in self.issues.items():
                if issues:
                    f.write(f"### {category.replace('_', ' ').title()}\\n\\n")
                    for issue in issues:
                        f.write(f"- {issue}\\n")
                    f.write("\\n")
            
            f.write("## 💡 RECOMENDACIONES\\n\\n")
            f.write("Ver sección de recomendaciones en la salida del script.\\n")
        
        print(f"\\n💾 Reporte guardado en: {report_file}")
    
    def _should_skip_file(self, filepath):
        """Determina si un archivo debe saltarse en el análisis"""
        skip_patterns = [
            '__pycache__',
            '.venv',
            'migrations',
            'node_modules',
            'backup'
        ]
        
        return any(pattern in str(filepath) for pattern in skip_patterns)

def main():
    """Función principal"""
    from datetime import datetime
    
    analyzer = CodigoAnalyzer()
    analyzer.analyze_project()

if __name__ == '__main__':
    main()