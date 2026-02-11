#!/usr/bin/env python3
"""
Script de desarrollo integrado para Django + Vite
"""
import os
import sys
import subprocess
import signal
import threading
import time
from pathlib import Path

class DevelopmentServer:
    def __init__(self):
        self.processes = []
        self.project_root = Path(__file__).parent
        self.backend_dir = self.project_root / 'backend'
        self.frontend_dir = self.project_root / 'frontend'
        
    def start_django(self):
        """Iniciar servidor Django"""
        print("🐍 Iniciando servidor Django...")
        
        # Activar entorno virtual si existe
        venv_activate = self.project_root / '.venv' / 'Scripts' / 'activate.ps1'
        if os.name == 'nt' and venv_activate.exists():
            cmd = f'powershell -Command "& {venv_activate}; cd {self.backend_dir}; python manage.py runserver 0.0.0.0:8000"'
        else:
            cmd = f'cd {self.backend_dir} && python manage.py runserver 0.0.0.0:8000'
            
        process = subprocess.Popen(
            cmd, 
            shell=True,
            cwd=self.backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        self.processes.append(('Django', process))
        
        # Thread para mostrar output de Django
        def show_django_output():
            for line in iter(process.stdout.readline, ''):
                if line.strip():
                    print(f"🐍 Django: {line.strip()}")
        
        threading.Thread(target=show_django_output, daemon=True).start()
        
    def start_vite(self):
        """Iniciar servidor Vite"""
        print("⚡ Iniciando servidor Vite...")
        
        # Verificar si node_modules existe
        node_modules = self.frontend_dir / 'node_modules'
        if not node_modules.exists():
            print("📦 Instalando dependencias de npm...")
            npm_install = subprocess.run(['npm', 'install'], cwd=self.frontend_dir)
            if npm_install.returncode != 0:
                print("❌ Error instalando dependencias npm")
                return
        
        process = subprocess.Popen(
            ['npm', 'run', 'dev'],
            cwd=self.frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        self.processes.append(('Vite', process))
        
        # Thread para mostrar output de Vite
        def show_vite_output():
            for line in iter(process.stdout.readline, ''):
                if line.strip():
                    print(f"⚡ Vite: {line.strip()}")
        
        threading.Thread(target=show_vite_output, daemon=True).start()
    
    def check_dependencies(self):
        """Verificar dependencias"""
        print("🔍 Verificando dependencias...")
        
        # Verificar Python
        try:
            result = subprocess.run([sys.executable, '--version'], 
                                  capture_output=True, text=True)
            print(f"✅ Python: {result.stdout.strip()}")
        except:
            print("❌ Python no encontrado")
            return False
            
        # Verificar Node.js
        try:
            result = subprocess.run(['node', '--version'], 
                                  capture_output=True, text=True)
            print(f"✅ Node.js: {result.stdout.strip()}")
        except:
            print("❌ Node.js no encontrado")
            return False
            
        # Verificar npm
        try:
            result = subprocess.run(['npm', '--version'], 
                                  capture_output=True, text=True)
            print(f"✅ npm: {result.stdout.strip()}")
        except:
            print("❌ npm no encontrado")
            return False
            
        return True
    
    def setup_signal_handlers(self):
        """Configurar manejo de señales"""
        def signal_handler(sig, frame):
            print("\\n🛑 Deteniendo servidores...")
            self.stop_all()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def stop_all(self):
        """Detener todos los procesos"""
        for name, process in self.processes:
            if process.poll() is None:  # Si está corriendo
                print(f"🛑 Deteniendo {name}...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
    
    def start(self):
        """Iniciar todos los servidores"""
        print("🚀 Iniciando entorno de desarrollo...")
        print("=" * 50)
        
        if not self.check_dependencies():
            print("❌ Faltan dependencias requeridas")
            return 1
        
        self.setup_signal_handlers()
        
        # Iniciar servidores
        self.start_vite()
        time.sleep(2)  # Esperar que Vite inicie
        self.start_django()
        
        print("=" * 50)
        print("✅ Servidores iniciados:")
        print("  🐍 Django: http://localhost:8000")
        print("  ⚡ Vite: http://localhost:3000")
        print("  📚 Admin: http://localhost:8000/admin/")
        print("  🔗 API: http://localhost:8000/api/")
        print("\\n🔥 Hot reload habilitado para frontend")
        print("\\n⏹️  Presiona Ctrl+C para detener")
        print("=" * 50)
        
        # Mantener el script corriendo
        try:
            while True:
                # Verificar que los procesos estén corriendo
                for name, process in self.processes:
                    if process.poll() is not None:  # Si el proceso terminó
                        print(f"❌ {name} se detuvo inesperadamente")
                        self.stop_all()
                        return 1
                
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        
        return 0

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("""
🚀 Servidor de Desarrollo Integrado - Cantina Tita

Uso: python dev_server.py [opciones]

Opciones:
  --help    Mostrar esta ayuda

Este script inicia automáticamente:
  - Servidor Django (puerto 8000)
  - Servidor Vite (puerto 3000)
  - Hot reload para frontend
  - Proxy de API configurado

Requisitos:
  - Python 3.8+
  - Node.js 18+
  - npm o yarn
        """)
        return 0
    
    server = DevelopmentServer()
    return server.start()

if __name__ == '__main__':
    sys.exit(main())