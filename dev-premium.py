#!/usr/bin/env python3
"""
🚀 Script de Desarrollo Premium - Cantina TITA
==============================================
Este script inicia ambos servidores (Django + Vite) y proporciona
información útil para el desarrollo.
"""

import subprocess
import sys
import os
import time
import threading
from pathlib import Path

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_banner():
    """Muestra el banner de inicio"""
    banner = f"""
{Colors.HEADER}╔══════════════════════════════════════════╗
║  🍽️  CANTINA TITA - DESARROLLO PREMIUM  ║
║                                          ║
║  Sistema de Gestión Completo             ║
║  Django 5.2.8 + Vite Frontend          ║
╚══════════════════════════════════════════╝{Colors.ENDC}
"""
    print(banner)

def check_requirements():
    """Verifica los requisitos del sistema"""
    print(f"{Colors.OKBLUE}🔍 Verificando requisitos...{Colors.ENDC}")
    
    # Verificar Python
    if sys.version_info < (3, 8):
        print(f"{Colors.FAIL}❌ Se requiere Python 3.8 o superior{Colors.ENDC}")
        sys.exit(1)
    
    # Verificar estructura del proyecto
    backend_path = Path("backend")
    frontend_path = Path("frontend")
    
    if not backend_path.exists():
        print(f"{Colors.FAIL}❌ No se encontró el directorio backend{Colors.ENDC}")
        sys.exit(1)
        
    if not frontend_path.exists():
        print(f"{Colors.FAIL}❌ No se encontró el directorio frontend{Colors.ENDC}")
        sys.exit(1)
    
    print(f"{Colors.OKGREEN}✅ Requisitos verificados correctamente{Colors.ENDC}")

def start_django_server():
    """Inicia el servidor Django"""
    print(f"{Colors.OKCYAN}🐍 Iniciando servidor Django...{Colors.ENDC}")
    
    try:
        # Cambiar al directorio backend
        os.chdir("backend")
        
        # Ejecutar migraciones
        print(f"{Colors.OKBLUE}📦 Aplicando migraciones...{Colors.ENDC}")
        subprocess.run([sys.executable, "manage.py", "migrate"], check=True)
        
        # Iniciar servidor
        print(f"{Colors.OKGREEN}🚀 Django corriendo en http://localhost:8000/{Colors.ENDC}")
        subprocess.run([sys.executable, "manage.py", "runserver", "8000"])
        
    except subprocess.CalledProcessError as e:
        print(f"{Colors.FAIL}❌ Error al iniciar Django: {e}{Colors.ENDC}")
    except KeyboardInterrupt:
        print(f"{Colors.WARNING}⚠️  Cerrando servidor Django...{Colors.ENDC}")
    finally:
        os.chdir("..")

def start_vite_server():
    """Inicia el servidor Vite"""
    print(f"{Colors.OKCYAN}⚡ Iniciando servidor Vite...{Colors.ENDC}")
    
    try:
        # Cambiar al directorio frontend
        os.chdir("frontend")
        
        # Verificar si existe node_modules
        if not Path("node_modules").exists():
            print(f"{Colors.OKBLUE}📦 Instalando dependencias de NPM...{Colors.ENDC}")
            subprocess.run(["npm", "install"], check=True)
        
        # Iniciar servidor de desarrollo
        print(f"{Colors.OKGREEN}⚡ Vite corriendo en http://localhost:5173/{Colors.ENDC}")
        subprocess.run(["npm", "run", "dev"], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"{Colors.FAIL}❌ Error al iniciar Vite: {e}{Colors.ENDC}")
    except KeyboardInterrupt:
        print(f"{Colors.WARNING}⚠️  Cerrando servidor Vite...{Colors.ENDC}")
    finally:
        os.chdir("..")

def show_development_info():
    """Muestra información útil para el desarrollo"""
    info = f"""
{Colors.HEADER}📋 INFORMACIÓN DE DESARROLLO{Colors.ENDC}
{Colors.OKBLUE}═══════════════════════════════════════════{Colors.ENDC}

{Colors.OKGREEN}🌐 URLs Principales:{Colors.ENDC}
  • Backend Django:  http://localhost:8000/
  • Admin Django:    http://localhost:8000/admin/
  • Frontend Vite:   http://localhost:5173/
  • Demo Premium:    http://localhost:5173/demo-premium.html
  • Demo Mobile:     http://localhost:5173/demo-mobile.html

{Colors.OKCYAN}📱 Funcionalidades Implementadas:{Colors.ENDC}
  ✅ Sistema POS completo
  ✅ Gestión de inventario
  ✅ Sistema de tarjetas recargables
  ✅ Portal web responsive
  ✅ Dashboard analytics
  ✅ Admin interface con 40+ modelos
  ✅ UI/UX premium con Glassmorphism
  ✅ Animaciones y efectos avanzados
  ✅ PWA capabilities
  ✅ Mobile-first design

{Colors.WARNING}🔧 Comandos Útiles:{Colors.ENDC}
  • Django Shell:    python backend/manage.py shell
  • Crear Usuario:   python backend/manage.py createsuperuser
  • Migraciones:     python backend/manage.py makemigrations
  • Aplicar Migr:    python backend/manage.py migrate
  • Collectstatic:   python backend/manage.py collectstatic

{Colors.HEADER}🎨 Arquitectura Frontend:{Colors.ENDC}
  • Vite 5.4.21 (Build tool ultra-rápido)
  • TypeScript (Tipado estático)
  • Tailwind CSS + DaisyUI (Utility-first CSS)
  • Alpine.js (Reactividad ligera)
  • HTMX (Interacciones HTTP)
  • Glassmorphism Design System

{Colors.OKGREEN}💡 Tips de Desarrollo:{Colors.ENDC}
  • Hot Reload activado en ambos servidores
  • CSS automáticamente recompilado
  • TypeScript con validación en tiempo real
  • Componentes premium listos para usar
    """
    print(info)

def main():
    """Función principal"""
    print_banner()
    check_requirements()
    show_development_info()
    
    print(f"{Colors.OKBLUE}⚙️  Iniciando servidores de desarrollo...{Colors.ENDC}")
    
    try:
        # Iniciar ambos servidores en threads separados
        django_thread = threading.Thread(target=start_django_server, daemon=True)
        vite_thread = threading.Thread(target=start_vite_server, daemon=True)
        
        django_thread.start()
        time.sleep(3)  # Dar tiempo a Django para iniciar
        vite_thread.start()
        
        # Esperar a que ambos threads terminen
        django_thread.join()
        vite_thread.join()
        
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}🛑 Cerrando servidores...{Colors.ENDC}")
        print(f"{Colors.OKGREEN}✨ ¡Desarrollo completado! ¡Hasta la próxima!{Colors.ENDC}")

if __name__ == "__main__":
    main()