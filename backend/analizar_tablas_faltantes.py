#!/usr/bin/env python
"""
Script para identificar tablas extra en MySQL que no tienen modelos Django
"""
import os
import sys
import django
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar Django
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

import mysql.connector
from django.apps import apps

def obtener_tablas_mysql():
    """Obtener todas las tablas de MySQL"""
    try:
        db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'database': os.getenv('DB_NAME', 'cantinatitadb'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', 'L01G05S33Vice.42')
        }
        
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute('SHOW TABLES')
        tablas = [tabla[0] for tabla in cursor.fetchall()]
        conn.close()
        return sorted(tablas)
    except Exception as e:
        print(f"Error conectando a MySQL: {e}")
        return []

def obtener_tablas_django():
    """Obtener todas las tablas de modelos Django"""
    tablas_django = set()
    
    # Obtener apps específicas
    apps_objetivo = ['gestion', 'pos']
    
    for app_name in apps_objetivo:
        try:
            app_config = apps.get_app_config(app_name)
            for model in app_config.get_models():
                tabla_name = model._meta.db_table
                tablas_django.add(tabla_name)
        except Exception as e:
            print(f"Error obteniendo modelos de {app_name}: {e}")
    
    return sorted(list(tablas_django))

def analizar_diferencias():
    """Analizar diferencias entre tablas MySQL y Django"""
    
    print("=" * 80)
    print("🔍 ANÁLISIS DE TABLAS FALTANTES EN MODELOS DJANGO")
    print("=" * 80)
    
    # Obtener tablas
    tablas_mysql = obtener_tablas_mysql()
    tablas_django = obtener_tablas_django()
    
    print(f"\n📊 ESTADÍSTICAS:")
    print(f"   🗄️  Tablas en MySQL: {len(tablas_mysql)}")
    print(f"   📦 Tablas con modelo Django: {len(tablas_django)}")
    
    # Tablas que están en MySQL pero NO tienen modelo Django
    tablas_sin_modelo = set(tablas_mysql) - set(tablas_django)
    
    print(f"\n🚨 TABLAS SIN MODELO DJANGO: {len(tablas_sin_modelo)}")
    print("-" * 50)
    
    if tablas_sin_modelo:
        # Categorizar las tablas
        tablas_django_sistema = []
        tablas_auth = []
        tablas_contenttypes = []
        tablas_sessions = []
        tablas_admin = []
        tablas_migrations = []
        tablas_custom = []
        
        for tabla in sorted(tablas_sin_modelo):
            if tabla.startswith('django_'):
                tablas_django_sistema.append(tabla)
            elif tabla.startswith('auth_'):
                tablas_auth.append(tabla)
            elif tabla.startswith('django_content_type'):
                tablas_contenttypes.append(tabla)
            elif tabla.startswith('django_session'):
                tablas_sessions.append(tabla)
            elif tabla.startswith('django_admin_log'):
                tablas_admin.append(tabla)
            elif tabla.startswith('django_migrations'):
                tablas_migrations.append(tabla)
            else:
                tablas_custom.append(tabla)
        
        # Mostrar categorías
        if tablas_django_sistema:
            print(f"\n🔧 TABLAS DEL SISTEMA DJANGO ({len(tablas_django_sistema)}):")
            for tabla in tablas_django_sistema:
                print(f"   • {tabla}")
                
        if tablas_auth:
            print(f"\n🔐 TABLAS DE AUTENTICACIÓN ({len(tablas_auth)}):")
            for tabla in tablas_auth:
                print(f"   • {tabla}")
                
        if tablas_contenttypes:
            print(f"\n📝 TABLAS DE CONTENT TYPES ({len(tablas_contenttypes)}):")
            for tabla in tablas_contenttypes:
                print(f"   • {tabla}")
                
        if tablas_sessions:
            print(f"\n🔑 TABLAS DE SESIONES ({len(tablas_sessions)}):")
            for tabla in tablas_sessions:
                print(f"   • {tabla}")
                
        if tablas_admin:
            print(f"\n👨‍💼 TABLAS DE ADMIN ({len(tablas_admin)}):")
            for tabla in tablas_admin:
                print(f"   • {tabla}")
                
        if tablas_migrations:
            print(f"\n🔄 TABLAS DE MIGRACIONES ({len(tablas_migrations)}):")
            for tabla in tablas_migrations:
                print(f"   • {tabla}")
                
        if tablas_custom:
            print(f"\n❗ TABLAS PERSONALIZADAS SIN MODELO ({len(tablas_custom)}):")
            for tabla in tablas_custom:
                print(f"   • {tabla} ⬅️ ¡ESTAS NECESITAN MODELOS!")
    else:
        print("   ✅ No hay tablas sin modelo")
    
    # Tablas que tienen modelo pero NO están en MySQL (esto no debería pasar)
    modelos_sin_tabla = set(tablas_django) - set(tablas_mysql)
    
    if modelos_sin_tabla:
        print(f"\n⚠️ MODELOS SIN TABLA EN MYSQL: {len(modelos_sin_tabla)}")
        print("-" * 50)
        for tabla in sorted(modelos_sin_tabla):
            print(f"   • {tabla}")
    
    print("\n" + "=" * 80)
    
    return tablas_custom if tablas_sin_modelo else []

if __name__ == "__main__":
    tablas_faltantes = analizar_diferencias()
    
    if tablas_faltantes:
        print(f"\n🎯 ACCIÓN REQUERIDA:")
        print(f"Hay {len(tablas_faltantes)} tablas personalizadas que necesitan modelos Django")
        print("Revise estas tablas y cree los modelos correspondientes.")
    else:
        print("\n🎉 ¡PERFECTO!")
        print("Todas las tablas personalizadas tienen sus modelos Django correspondientes.")