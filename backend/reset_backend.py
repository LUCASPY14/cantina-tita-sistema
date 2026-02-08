# reset_backend.py - Guardar en D:\anteproyecto20112025\backend\
import os
import sys
import subprocess
import mysql.connector
import getpass
from pathlib import Path

def print_step(step, title):
    print(f"\n{'='*60}")
    print(f"🔧 PASO {step}: {title}")
    print(f"{'='*60}")

def get_db_config():
    """Obtener configuración de BD desde settings.py"""
    try:
        # Importar settings del proyecto
        project_root = Path.cwd()
        
        # Buscar settings.py
        settings_file = project_root / "cantina_project" / "settings.py"
        if not settings_file.exists():
            # Buscar en otras ubicaciones
            settings_files = list(project_root.rglob("settings.py"))
            for sf in settings_files:
                if 'venv' not in str(sf) and '.venv' not in str(sf):
                    settings_file = sf
                    break
        
        if settings_file.exists():
            # Cargar módulo dinámicamente
            import importlib.util
            spec = importlib.util.spec_from_file_location("django_settings", settings_file)
            settings = importlib.util.module_from_spec(spec)
            sys.modules["django_settings"] = settings
            spec.loader.exec_module(settings)
            
            db_config = settings.DATABASES['default']
            print(f"✅ Configuración BD cargada de: {settings_file.name}")
            return db_config
        else:
            raise FileNotFoundError("settings.py no encontrado")
            
    except Exception as e:
        print(f"⚠️  Error cargando settings: {e}")
        print("Usando configuración por defecto...")
        return {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'cantinatitadb',
            'USER': 'root',
            'PASSWORD': '',
            'HOST': 'localhost',
            'PORT': '3306'
        }

def install_dependencies():
    """Instalar dependencias necesarias"""
    print("📦 Verificando dependencias...")
    
    # mysql-connector-python
    try:
        import mysql.connector
        print("✅ mysql-connector-python ya instalado")
    except ImportError:
        print("Instalando mysql-connector-python...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "mysql-connector-python"])
        import mysql.connector
        print("✅ mysql-connector-python instalado")

def reset_database(db_config, password):
    """Reiniciar base de datos"""
    try:
        # Conectar a MySQL server
        connection = mysql.connector.connect(
            host=db_config.get('HOST', 'localhost'),
            user=db_config['USER'],
            password=password,
            auth_plugin='mysql_native_password'
        )
        
        cursor = connection.cursor()
        
        db_name = db_config['NAME']
        print(f"🗑️  Eliminando base de datos: {db_name}")
        cursor.execute(f"DROP DATABASE IF EXISTS `{db_name}`")
        
        print(f"🔧 Creando base de datos: {db_name}")
        cursor.execute(f"""
            CREATE DATABASE `{db_name}` 
            CHARACTER SET utf8mb4 
            COLLATE utf8mb4_unicode_ci
        """)
        
        cursor.close()
        connection.close()
        
        print("✅ Base de datos reiniciada")
        return True
        
    except Exception as e:
        print(f"❌ Error reiniciando BD: {e}")
        return False

def restore_structure(db_config, password):
    """Restaurar estructura desde SQL"""
    # Buscar estructura.sql
    estructura_path = Path("estructura.sql")
    if not estructura_path.exists():
        # Buscar en directorio padre
        parent_path = Path("..") / "estructura.sql"
        if parent_path.exists():
            print(f"📄 Copiando estructura.sql desde directorio padre...")
            import shutil
            shutil.copy2(parent_path, "estructura.sql")
            estructura_path = Path("estructura.sql")
        else:
            print("❌ estructura.sql no encontrado")
            return False
    
    print(f"📖 Leyendo {estructura_path} ({estructura_path.stat().st_size / 1024:.1f} KB)")
    
    try:
        connection = mysql.connector.connect(
            host=db_config.get('HOST', 'localhost'),
            user=db_config['USER'],
            password=password,
            database=db_config['NAME'],
            auth_plugin='mysql_native_password'
        )
        
        cursor = connection.cursor()
        
        with open(estructura_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Dividir y ejecutar comandos
        commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip()]
        
        print(f"⚡ Ejecutando {len(commands)} comandos...")
        
        success = 0
        for i, cmd in enumerate(commands):
            if cmd and not cmd.startswith('--'):
                try:
                    cursor.execute(cmd)
                    success += 1
                    if (i + 1) % 100 == 0:
                        print(f"  📊 Progreso: {i+1}/{len(commands)}")
                except Exception as e:
                    if success == 0:  # Solo mostrar primeros errores
                        print(f"  ⚠️  Error comando {i+1}: {str(e)[:80]}")
        
        connection.commit()
        
        # Verificar tablas
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        print(f"✅ {success}/{len(commands)} comandos exitosos")
        print(f"📋 {len(tables)} tablas creadas")
        
        if tables:
            print("📋 Primeras 5 tablas:")
            for table in tables[:5]:
                print(f"  - {table[0]}")
        
        cursor.close()
        connection.close()
        
        return success > 0
        
    except Exception as e:
        print(f"❌ Error restaurando estructura: {e}")
        return False

def clean_django():
    """Limpiar migraciones Django"""
    deleted = 0
    
    # Eliminar .pyc y __pycache__
    for pyc in Path('.').rglob('*.pyc'):
        pyc.unlink()
        deleted += 1
    
    for cache_dir in Path('.').rglob('__pycache__'):
        import shutil
        shutil.rmtree(cache_dir, ignore_errors=True)
    
    # Eliminar migraciones (excepto __init__.py)
    for mig_file in Path('.').rglob('migrations/*.py'):
        if mig_file.name != '__init__.py':
            mig_file.unlink()
            deleted += 1
    
    print(f"✅ {deleted} archivos limpiados")
    return True

def generate_models():
    """Generar modelos con inspectdb"""
    print("🤖 Generando modelos Django...")
    
    result = subprocess.run(
        ['python', 'manage.py', 'inspectdb'],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        models_content = result.stdout
        
        # Buscar apps Django
        apps = []
        for item in Path('.').iterdir():
            if item.is_dir() and (item / 'apps.py').exists():
                apps.append(item)
        
        if apps:
            # Usar la primera app (probablemente la principal)
            app = apps[0]
            models_file = app / 'models.py'
            
            # Hacer backup si existe
            if models_file.exists():
                backup = models_file.with_suffix('.backup.py')
                import shutil
                shutil.copy2(models_file, backup)
                print(f"✅ Backup creado: {backup}")
            
            # Guardar nuevos modelos
            models_file.write_text(models_content, encoding='utf-8')
            
            # Contar modelos
            model_count = models_content.count('class ')
            print(f"✅ {model_count} modelos generados en: {models_file}")
            
            return True
        else:
            print("⚠️  No se encontraron apps Django")
            return False
    else:
        print(f"❌ Error inspectdb: {result.stderr}")
        return False

def run_django_command(cmd, description):
    """Ejecutar comando de Django"""
    print(f"  {description}...")
    
    result = subprocess.run(
        ['python', 'manage.py'] + cmd.split(),
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(f"    ✅ Completado")
        return True
    else:
        print(f"    ⚠️  Error: {result.stderr[:200]}")
        return False

def create_superuser():
    """Crear superuser"""
    try:
        # Configurar Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
        
        import django
        django.setup()
        
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        username = 'admin'
        password = 'admin123'
        
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username, 'admin@example.com', password)
            print(f"✅ Superuser creado: {username}/{password}")
        else:
            # Actualizar password
            user = User.objects.get(username=username)
            user.set_password(password)
            user.save()
            print(f"✅ Superuser actualizado: {username}/{password}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creando superuser: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("🚀 REINICIO COMPLETO - BACKEND DJANGO")
    print("="*60)
    
    # Verificar que estamos en backend
    current_dir = Path.cwd()
    if not (current_dir / "manage.py").exists():
        print("❌ ERROR: No se encontró manage.py")
        print("💡 Ejecuta desde: D:\\anteproyecto20112025\\backend")
        return
    
    print(f"📁 Directorio actual: {current_dir}")
    print(f"✅ manage.py encontrado")
    
    # Instalar dependencias
    install_dependencies()
    
    # Obtener configuración
    db_config = get_db_config()
    
    # Solicitar contraseña si no está en settings
    password = db_config.get('PASSWORD', '')
    if not password:
        password = getpass.getpass("🔐 Contraseña MySQL root: ")
    
    # Ejecutar pasos
    steps = [
        (1, "Reiniciar base de datos", lambda: reset_database(db_config, password)),
        (2, "Restaurar estructura SQL", lambda: restore_structure(db_config, password)),
        (3, "Limpiar migraciones Django", clean_django),
        (4, "Generar modelos Django", generate_models),
        (5, "Crear migraciones", lambda: run_django_command("makemigrations", "Creando migraciones")),
        (6, "Aplicar migraciones", lambda: run_django_command("migrate", "Aplicando migraciones")),
        (7, "Crear superuser", create_superuser),
    ]
    
    successful = 0
    total = len(steps)
    
    for step_num, title, func in steps:
        print_step(step_num, title)
        try:
            if func():
                successful += 1
            else:
                print(f"⚠️  Paso {step_num} falló parcialmente")
        except Exception as e:
            print(f"❌ Error en paso {step_num}: {e}")
    
    # Resumen
    print("\n" + "="*60)
    print("📊 RESUMEN FINAL")
    print("="*60)
    print(f"✅ Pasos completados: {successful}/{total}")
    
    if successful >= total - 1:  # Permitir 1 error
        print("\n🎉 ¡REINICIO EXITOSO!")
        print("\n🌐 PARA INICIAR EL SERVIDOR:")
        print("   python manage.py runserver")
        print("\n🔗 ADMINISTRADOR:")
        print("   http://127.0.0.1:8000/admin")
        print("   Usuario: admin")
        print("   Contraseña: admin123")
    else:
        print("\n⚠️  Hubo errores. Revisa los mensajes.")

if __name__ == '__main__':
    main()