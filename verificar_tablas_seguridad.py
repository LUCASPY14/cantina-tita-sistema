"""
Verificar y crear tablas de seguridad directamente con Python
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection

print("🔍 Verificando tablas de seguridad...\n")

# Verificar cada tabla
tablas = ['intentos_login', 'auditoria_operaciones', 'tokens_recuperacion', 'bloqueos_cuenta']

with connection.cursor() as cursor:
    cursor.execute("SHOW TABLES")
    tablas_existentes = [table[0] for table in cursor.fetchall()]
    
    print("📋 Tablas existentes en cantinatitadb:")
    for tabla in tablas_existentes:
        marca = "✅" if tabla in tablas else "  "
        print(f"   {marca} {tabla}")
    
    print("\n🔐 Tablas de seguridad requeridas:")
    for tabla in tablas:
        if tabla in tablas_existentes:
            print(f"   ✅ {tabla} - EXISTS")
        else:
            print(f"   ❌ {tabla} - MISSING")
    
    # Si faltan tablas, crearlas
    tablas_faltantes = [t for t in tablas if t not in tablas_existentes]
    
    if tablas_faltantes:
        print(f"\n⚠️ Faltan {len(tablas_faltantes)} tablas, creándolas...")
        
        # Leer y ejecutar SQL
        with open('crear_sistema_seguridad.sql', 'r', encoding='utf-8') as f:
            sql = f.read()
        
        # Ejecutar cada sentencia
        for statement in sql.split(';'):
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                try:
                    cursor.execute(statement)
                    print(".", end="", flush=True)
                except Exception as e:
                    if "already exists" not in str(e).lower():
                        print(f"\n⚠️ Warning: {e}")
        
        connection.commit()
        print("\n✅ Tablas creadas!")
        
        # Verificar nuevamente
        cursor.execute("SHOW TABLES")
        tablas_existentes = [table[0] for table in cursor.fetchall()]
        
        print("\n📊 Estado final:")
        for tabla in tablas:
            if tabla in tablas_existentes:
                cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                count = cursor.fetchone()[0]
                print(f"   ✅ {tabla} - {count} registros")
            else:
                print(f"   ❌ {tabla} - NO CREADA")
    else:
        print("\n✅ Todas las tablas de seguridad existen!")
        print("\n📊 Registros por tabla:")
        for tabla in tablas:
            cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
            count = cursor.fetchone()[0]
            print(f"   {tabla}: {count} registros")
