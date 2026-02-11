# reset_project.py - VERSIÓN CORREGIDA
import os
import sys
import subprocess
import importlib.util
from pathlib import Path

def setup_django_environment():
    """Configurar el entorno Django correctamente"""
    # Agregar el directorio del proyecto al path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    # Configurar variable de entorno
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'anteproyecto20112025.settings')
    
    try:
        import django
        django.setup()
        print("✅ Entorno Django configurado")
        return True
    except Exception as e:
        print(f"❌ Error configurando Django: {e}")
        return False

def get_db_config():
    """Obtener configuración de BD de settings.py"""
    try:
        # Importar settings usando la ruta completa
        project_path = Path(__file__).parent
        
        # Buscar settings.py
        settings_path = project_path / 'anteproyecto20112025' / 'settings.py'
        if not settings_path.exists():
            # Buscar en raíz
            settings_path = project_path / 'settings.py'
        
        if settings_path.exists():
            # Cargar módulo dinámicamente
            spec = importlib.util.spec_from_file_location("project_settings", settings_path)
            settings_module = importlib.util.module_from_spec(spec)
            
            # Ejecutar el módulo
            sys.modules["project_settings"] = settings_module
            spec.loader.exec_module(settings_module)
            
            db_config = settings_module.DATABASES['default']
            print("✅ Configuración de BD cargada desde settings.py")
            return db_config
        else:
            print("⚠️  settings.py no encontrado, usando configuración por defecto")
    
    except Exception as e:
        print(f"⚠️  Error cargando settings: {e}")
    
    # Configuración por defecto (preguntar al usuario)
    print("\n📝 Usando configuración manual...")
    import getpass
    
    db_config = {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'cantinatitadb',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '3306',
    }
    
    # Preguntar contraseña si no está en settings
    if not db_config.get('PASSWORD'):
        db_config['PASSWORD'] = getpass.getpass("🔐 Ingresa la contraseña de MySQL root: ")
    
    return db_config

def install_mysql_connector():
    """Instalar mysql-connector-python si no está instalado"""
    try:
        import mysql.connector
        print("✅ mysql-connector-python ya instalado")
        return True
    except ImportError:
        print("📦 Instalando mysql-connector-python...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "mysql-connector-python"])
            import mysql.connector
            print("✅ mysql-connector-python instalado exitosamente")
            return True
        except Exception as e:
            print(f"❌ Error instalando mysql-connector-python: {e}")
            return False

def reset_database(db_config):
    """Reiniciar base de datos MySQL"""
    print("\n" + "="*60)
    print("🔧 PASO 1: REINICIANDO BASE DE DATOS")
    print("="*60)
    
    if not install_mysql_connector():
        return False
    
    try:
        import mysql.connector
        from mysql.connector import Error
        
        # Conectar a MySQL server
        connection = mysql.connector.connect(
            host=db_config.get('HOST', 'localhost'),
            user=db_config['ROOT'],
            password=db_config['L01G05S33Vice.42'],
            auth_plugin='mysql_native_password'  # Para MySQL 8+
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # 1. Eliminar base de datos si existe
            print("🗑️  Eliminando base de datos existente...")
            cursor.execute(f"DROP DATABASE IF EXISTS `{db_config['NAME']}`")
            print("✅ Base de datos eliminada")
            
            # 2. Crear nueva base de datos
            print("🔧 Creando nueva base de datos...")
            cursor.execute(f"""
                CREATE DATABASE `{db_config['NAME']}` 
                CHARACTER SET utf8mb4 
                COLLATE utf8mb4_unicode_ci
            """)
            print("✅ Base de datos creada con utf8mb4")
            
            cursor.close()
            connection.close()
            
            return True
            
    except Error as e:
        print(f"❌ Error MySQL: {e}")
        print("\n💡 Soluciones posibles:")
        print("1. Verifica que MySQL esté corriendo")
        print("2. Revisa usuario/contraseña")
        print("3. Para MySQL 8+, quizás necesites: pip install mysql-connector-python==8.0.33")
        return False

def restore_structure(db_config):
    """Restaurar estructura desde archivo SQL"""
    print("\n" + "="*60)
    print("💾 PASO 2: RESTAURANDO ESTRUCTURA SQL")
    print("="*60)
    
    sql_file = Path('estructura.sql')
    
    if not sql_file.exists():
        print(f"❌ Archivo '{sql_file}' no encontrado")
        print("💡 Asegúrate de tener estructura.sql en la carpeta del proyecto")
        return False
    
    try:
        import mysql.connector
        from mysql.connector import Error
        
        # Conectar a la base de datos específica
        connection = mysql.connector.connect(
            host=db_config.get('HOST', 'localhost'),
            user=db_config['ROOT'],
            password=db_config['L01G05S33Vice.42'],
            database=db_config['cantinatitadb'],
            auth_plugin='mysql_native_password'
        )
        
        cursor = connection.cursor()
        
        # Leer archivo SQL
        print(f"📖 Leyendo {sql_file}...")
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Dividir en comandos (manejo mejorado)
        print("🔨 Procesando comandos SQL...")
        
        # Método simple: dividir por punto y coma
        commands = []
        current = []
        in_string = False
        string_char = None
        in_comment = False
        
        i = 0
        while i < len(sql_content):
            char = sql_content[i]
            
            # Manejar comentarios
            if not in_string and not in_comment:
                if char == '-' and i + 1 < len(sql_content) and sql_content[i + 1] == '-':
                    in_comment = True
                    i += 2
                    continue
                elif char == '/' and i + 1 < len(sql_content) and sql_content[i + 1] == '*':
                    in_comment = True
                    i += 2
                    continue
            
            if in_comment:
                if char == '\n' and sql_content[i-1:i+1] != '\\n':
                    in_comment = False
                elif char == '*' and i + 1 < len(sql_content) and sql_content[i + 1] == '/':
                    in_comment = False
                    i += 2
                    continue
                i += 1
                continue
            
            # Manejar strings
            if char in ("'", '"', '`') and (i == 0 or sql_content[i-1] != '\\'):
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char:
                    in_string = False
                    string_char = None
            
            current.append(char)
            
            # Fin de comando
            if char == ';' and not in_string:
                command = ''.join(current).strip()
                if command:
                    commands.append(command)
                current = []
            
            i += 1
        
        # Ejecutar comandos
        print(f"⚡ Ejecutando {len(commands)} comandos...")
        
        success_count = 0
        error_count = 0
        
        for i, cmd in enumerate(commands):
            if cmd and not cmd.startswith('--'):
                try:
                    cursor.execute(cmd)
                    success_count += 1
                    
                    # Mostrar progreso
                    if (i + 1) % 50 == 0:
                        print(f"  📊 Progreso: {i+1}/{len(commands)} comandos")
                        
                except Error as e:
                    error_count += 1
                    # Solo mostrar primeros errores
                    if error_count <= 5:
                        print(f"  ⚠️  Error en comando {i+1}: {str(e)[:100]}...")
        
        connection.commit()
        
        # Verificar tablas creadas
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        
        print(f"\n📊 RESULTADO:")
        print(f"  ✅ Comandos exitosos: {success_count}")
        print(f"  ⚠️  Comandos con error: {error_count}")
        print(f"  📋 Tablas creadas: {len(tables)}")
        
        if tables:
            print("\n📋 Primeras 10 tablas:")
            for table in tables[:10]:
                cursor.execute(f"SHOW CREATE TABLE `{table}`")
                create_stmt = cursor.fetchone()[1]
                # Contar columnas aproximado
                col_count = create_stmt.count('`') // 2
                print(f"  - {table} ({col_count} columnas)")
            
            if len(tables) > 10:
                print(f"  ... y {len(tables) - 10} más")
        
        cursor.close()
        connection.close()
        
        return success_count > 0  # Retorna True si al menos un comando fue exitoso
        
    except Error as e:
        print(f"❌ Error restaurando estructura: {e}")
        return False

def clean_django_migrations():
    """Limpiar migraciones de Django"""
    print("\n" + "="*60)
    print("🧹 PASO 3: LIMPIANDO MIGRACIONES DJANGO")
    print("="*60)
    
    try:
        from pathlib import Path
        
        deleted_count = 0
        
        # Buscar y eliminar archivos de migración
        for pyc_file in Path('.').rglob('*.pyc'):
            pyc_file.unlink()
            deleted_count += 1
        
        for pycache in Path('.').rglob('__pycache__'):
            if pycache.is_dir():
                import shutil
                shutil.rmtree(pycache)
        
        # Buscar carpetas migrations
        for mig_dir in Path('.').rglob('migrations'):
            if mig_dir.is_dir():
                for mig_file in mig_dir.glob('*.py'):
                    if mig_file.name != '__init__.py':
                        mig_file.unlink()
                        deleted_count += 1
        
        # Eliminar db.sqlite3 si existe
        sqlite_db = Path('db.sqlite3')
        if sqlite_db.exists():
            sqlite_db.unlink()
            print("✅ db.sqlite3 eliminado")
        
        print(f"✅ {deleted_count} archivos eliminados")
        return True
        
    except Exception as e:
        print(f"❌ Error limpiando migraciones: {e}")
        return False

def generate_django_models(db_config):
    """Generar modelos Django automáticamente"""
    print("\n" + "="*60)
    print("🤖 PASO 4: GENERANDO MODELOS DJANGO")
    print("="*60)
    
    try:
        # Configurar entorno temporal para inspectdb
        temp_env = os.environ.copy()
        temp_env['DJANGO_SETTINGS_MODULE'] = 'anteproyecto20112025.settings'
        
        print("🔍 Ejecutando inspectdb...")
        
        # Ejecutar inspectdb
        result = subprocess.run(
            [sys.executable, 'manage.py', 'inspectdb'],
            capture_output=True,
            text=True,
            env=temp_env
        )
        
        if result.returncode == 0:
            models_content = result.stdout
            
            # Buscar app principal
            app_dirs = []
            for item in Path('.').iterdir():
                if item.is_dir() and (item / 'apps.py').exists():
                    app_dirs.append(item)
            
            if app_dirs:
                # Usar la primera app encontrada
                main_app = app_dirs[0]
                models_file = main_app / 'models.py'
                
                # Hacer backup si existe
                if models_file.exists():
                    backup_file = models_file.with_suffix('.models.backup.py')
                    import shutil
                    shutil.copy2(models_file, backup_file)
                    print(f"✅ Backup creado: {backup_file}")
                
                # Guardar modelos
                models_file.write_text(models_content, encoding='utf-8')
                
                # Contar modelos
                model_count = models_content.count('class ')
                print(f"✅ Modelos generados en: {models_file}")
                print(f"📊 {model_count} clases de modelo generadas")
                
                # Mostrar primeros modelos
                lines = models_content.split('\n')
                model_lines = [l for l in lines if l.strip().startswith('class ')]
                print("\n📋 Primeros 5 modelos:")
                for model_line in model_lines[:5]:
                    model_name = model_line.split(' ')[1].split('(')[0]
                    print(f"  - {model_name}")
                
                if len(model_lines) > 5:
                    print(f"  ... y {len(model_lines) - 5} más")
                
                return True
            else:
                print("⚠️  No se encontró app Django, guardando en models_generated.py")
                Path('models_generated.py').write_text(models_content, encoding='utf-8')
                return True
        else:
            print(f"❌ Error en inspectdb: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error generando modelos: {e}")
        return False

def run_django_command(command, description):
    """Ejecutar un comando de Django"""
    print(f"\n🔧 {description}...")
    
    try:
        result = subprocess.run(
            [sys.executable, 'manage.py'] + command.split(),
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ {description} completado")
            if result.stdout and len(result.stdout.strip()) > 0:
                print(f"📄 Salida: {result.stdout[:200]}...")
            return True
        else:
            print(f"❌ Error en {description}: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando comando: {e}")
        return False

def create_superuser():
    """Crear superuser para Django Admin"""
    print("\n" + "="*60)
    print("👑 PASO 7: CREANDO SUPERUSER")
    print("="*60)
    
    try:
        # Setup Django
        setup_django_environment()
        
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        # Crear o actualizar superuser
        username = 'admin'
        email = 'admin@example.com'
        password = 'admin123'
        
        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': email, 'is_staff': True, 'is_superuser': True}
        )
        
        if created:
            user.set_password(password)
            user.save()
            print(f"✅ Superuser creado: {username} / {password}")
        else:
            # Actualizar password si ya existe
            user.set_password(password)
            user.email = email
            user.is_staff = True
            user.is_superuser = True
            user.save()
            print(f"✅ Superuser actualizado: {username} / {password}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creando superuser: {e}")
        return False

def setup_django_admin_auto():
    """Configurar Django Admin automáticamente"""
    print("\n" + "="*60)
    print("⚙️  PASO 8: CONFIGURANDO DJANGO ADMIN")
    print("="*60)
    
    try:
        # Setup Django
        setup_django_environment()
        
        from django.apps import apps
        
        # Buscar app con modelos
        for app_config in apps.get_app_configs():
            if app_config.models:
                app_name = app_config.name
                app_path = Path(app_config.path)
                admin_file = app_path / 'admin.py'
                
                # Generar admin.py automático
                admin_content = f'''from django.contrib import admin
from django.apps import apps

# Registrar TODOS los modelos de {app_name} automáticamente
app_models = apps.get_app_config('{app_name}').get_models()

for model in app_models:
    try:
        @admin.register(model)
        class AutoAdmin(admin.ModelAdmin):
            list_display = [field.name for field in model._meta.fields[:4]]
            list_filter = [field.name for field in model._meta.fields 
                          if field.get_internal_type() in ['BooleanField', 'ForeignKey']]
            search_fields = [field.name for field in model._meta.fields 
                           if field.get_internal_type() in ['CharField', 'TextField']]
            
            def get_list_display(self, request):
                # Mostrar máximo 5 campos
                return [field.name for field in model._meta.fields[:5]]
    except Exception as e:
        print(f"⚠️ No se pudo registrar {{model.__name__}}: {{e}}")
'''
                
                admin_file.write_text(admin_content, encoding='utf-8')
                print(f"✅ admin.py creado en: {admin_file}")
                
                # Mostrar modelos que se registrarán
                print(f"📋 Modelos en {app_name}:")
                for model in list(app_config.get_models())[:10]:
                    print(f"  - {model.__name__}")
                
                if len(list(app_config.get_models())) > 10:
                    print(f"  ... y {len(list(app_config.get_models())) - 10} más")
                
                return True
        
        print("⚠️  No se encontraron apps con modelos para configurar admin")
        return False
        
    except Exception as e:
        print(f"❌ Error configurando admin: {e}")
        return False

def main():
    """Función principal"""
    print("\n" + "="*60)
    print("🚀 REINICIO COMPLETO DEL PROYECTO DJANGO + MYSQL")
    print("="*60)
    
    # Verificar estructura.sql
    if not Path('estructura.sql').exists():
        print("❌ ERROR: Archivo 'estructura.sql' no encontrado en el directorio actual")
        print("💡 Coloca el archivo en: D:\\anteproyecto20112025\\estructura.sql")
        return
    
    # Obtener configuración de BD
    db_config = get_db_config()
    
    # Ejecutar pasos
    steps = [
        ("Reiniciar base de datos", lambda: reset_database(db_config)),
        ("Restaurar estructura SQL", lambda: restore_structure(db_config)),
        ("Limpiar migraciones Django", clean_django_migrations),
        ("Generar modelos Django", lambda: generate_django_models(db_config)),
        ("Crear migraciones", lambda: run_django_command("makemigrations", "Creando migraciones")),
        ("Aplicar migraciones", lambda: run_django_command("migrate", "Aplicando migraciones")),
        ("Crear superuser", create_superuser),
        ("Configurar Django Admin", setup_django_admin_auto),
    ]
    
    print("\n📋 EJECUTANDO PASOS:")
    print("-"*40)
    
    successful_steps = []
    failed_steps = []
    
    for i, (name, func) in enumerate(steps, 1):
        print(f"\n[{i}/{len(steps)}] {name.upper()}...")
        try:
            if func():
                successful_steps.append(name)
                print(f"   ✅ {name}: COMPLETADO")
            else:
                failed_steps.append(name)
                print(f"   ❌ {name}: FALLÓ")
        except Exception as e:
            failed_steps.append(name)
            print(f"   ❌ {name}: ERROR - {e}")
    
    # Resumen final
    print("\n" + "="*60)
    print("📊 RESUMEN FINAL")
    print("="*60)
    print(f"✅ Pasos exitosos: {len(successful_steps)}/{len(steps)}")
    print(f"❌ Pasos fallidos: {len(failed_steps)}/{len(steps)}")
    
    if failed_steps:
        print("\n⚠️  Pasos con problemas:")
        for step in failed_steps:
            print(f"   • {step}")
    
    if len(successful_steps) >= 6:  # Al menos 6 de 8 pasos exitosos
        print("\n🎉 ¡REINICIO MAYORITARIAMENTE EXITOSO!")
        print("\n🌐 PARA INICIAR:")
        print("   cd D:\\anteproyecto20112025")
        print("   python manage.py runserver")
        print("\n🔗 URLs:")
        print("   • Django Admin: http://127.0.0.1:8000/admin")
        print("   • Usuario: admin / admin123")
    else:
        print("\n⚠️  Reinicio con problemas significativos")
        print("💡 Revisa los errores y ejecuta manualmente los pasos fallidos")

if __name__ == '__main__':
    # Cambiar al directorio del script si es necesario
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    main()