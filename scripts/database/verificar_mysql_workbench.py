#!/usr/bin/env python
"""
VERIFICACION MYSQL WORKBENCH - CANTINA TITA
Verifica conexión a MySQL y estado de la base de datos cantinatitadb
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection
from django.conf import settings

def verificar_mysql():
    print("🔍 VERIFICACIÓN MYSQL WORKBENCH - CANTINA TITA")
    print("=" * 60)
    
    # 1. Verificar configuración
    print("\n1️⃣ CONFIGURACIÓN ACTUAL:")
    db_config = settings.DATABASES['default']
    print(f"   Motor: {db_config['ENGINE']}")
    print(f"   Base de datos: {db_config['NAME']}")
    print(f"   Usuario: {db_config['USER']}")
    print(f"   Host: {db_config['HOST']}")
    print(f"   Puerto: {db_config['PORT']}")
    print(f"   Contraseña: {'✅ Configurada' if db_config['PASSWORD'] else '❌ Vacía'}")
    
    # 2. Probar conexión
    print("\n2️⃣ ESTADO DE CONEXIÓN:")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
            print(f"   ✅ MySQL conectado: {version}")
            
            # Verificar base de datos actual
            cursor.execute("SELECT DATABASE()")
            current_db = cursor.fetchone()[0]
            print(f"   ✅ Base de datos activa: {current_db}")
            
            # Contar tablas
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"   ✅ Tablas encontradas: {len(tables)}")
            
            return True
            
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
        print("\n💡 SOLUCIÓN:")
        print("   1. Abrir MySQL Workbench")
        print("   2. Verificar que la base de datos 'cantinatitadb' existe")
        print("   3. Configurar DB_PASSWORD en archivo .env")
        print("   4. Asegurar que MySQL Server está ejecutándose")
        return False

def verificar_workbench():
    print("\n3️⃣ MYSQL WORKBENCH:")
    
    # Verificar instalación
    workbench_path = Path("C:/Program Files/MySQL/MySQL Workbench 8.0")
    if workbench_path.exists():
        print("   ✅ MySQL Workbench 8.0 instalado")
        print(f"   📍 Ubicación: {workbench_path}")
    else:
        print("   ❌ MySQL Workbench no encontrado")
    
    # Verificar procesos MySQL
    import subprocess
    try:
        result = subprocess.run(['tasklist', '/fi', 'imagename eq mysqld.exe'], 
                              capture_output=True, text=True)
        if 'mysqld.exe' in result.stdout:
            print("   ✅ MySQL Server ejecutándose")
        else:
            print("   ❌ MySQL Server no encontrado")
    except:
        print("   ⚠️ No se pudo verificar MySQL Server")

def main():
    verificar_workbench()
    conexion_ok = verificar_mysql()
    
    print("\n" + "=" * 60)
    if conexion_ok:
        print("🎉 ESTADO: TODO FUNCIONANDO CORRECTAMENTE")
        print("✅ MySQL Workbench + Servidor + Base de datos OK")
    else:
        print("⚠️ ESTADO: REQUIERE CONFIGURACIÓN")
        print("🔧 Completar configuración de credenciales MySQL")
    print("=" * 60)

if __name__ == '__main__':
    main()