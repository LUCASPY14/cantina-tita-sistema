"""
Script para ejecutar optimización de BD desde Python
Utiliza las credenciales de Django settings
"""
import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection

print("=" * 80)
print("🚀 EJECUTANDO OPTIMIZACIÓN DE BASE DE DATOS")
print("=" * 80)
print()

# Leer el script SQL
with open('optimizar_performance_bd.sql', 'r', encoding='utf-8') as f:
    sql_script = f.read()

# Dividir en comandos individuales
comandos = []
comando_actual = []

for linea in sql_script.split('\n'):
    linea_limpia = linea.strip()
    
    # Saltar comentarios y líneas vacías
    if not linea_limpia or linea_limpia.startswith('--') or linea_limpia.startswith('/*'):
        continue
    
    comando_actual.append(linea)
    
    # Si termina con ;, es el final del comando
    if linea_limpia.endswith(';'):
        comandos.append('\n'.join(comando_actual))
        comando_actual = []

print(f"📋 Total de comandos SQL a ejecutar: {len(comandos)}")
print()

# Ejecutar cada comando
exitosos = 0
errores = 0
warnings = 0

with connection.cursor() as cursor:
    for i, comando in enumerate(comandos, 1):
        comando_limpio = comando.strip()
        if not comando_limpio:
            continue
        
        # Mostrar primeras palabras del comando
        primeras_palabras = ' '.join(comando_limpio.split()[:5])
        
        try:
            cursor.execute(comando)
            resultado = cursor.fetchall() if cursor.description else None
            
            # Identificar tipo de comando
            if comando_limpio.upper().startswith('CREATE INDEX'):
                print(f"✅ [{i}] Índice creado: {primeras_palabras}...")
            elif comando_limpio.upper().startswith('DROP INDEX'):
                print(f"⚠️  [{i}] Índice eliminado: {primeras_palabras}...")
                warnings += 1
            elif comando_limpio.upper().startswith('OPTIMIZE TABLE'):
                tabla = comando_limpio.split()[2].rstrip(';')
                print(f"🔧 [{i}] Tabla optimizada: {tabla}")
            elif comando_limpio.upper().startswith('ANALYZE TABLE'):
                tabla = comando_limpio.split()[2].rstrip(';')
                print(f"📊 [{i}] Estadísticas actualizadas: {tabla}")
            elif comando_limpio.upper().startswith('SELECT'):
                if resultado:
                    print(f"📋 [{i}] Consulta ejecutada: {len(resultado)} filas")
                    # Mostrar primeras 3 filas de resultados importantes
                    if 'TABLE_NAME' in str(cursor.description):
                        print("     Primeros resultados:")
                        for row in resultado[:3]:
                            print(f"       {row}")
                else:
                    print(f"📋 [{i}] Consulta ejecutada: sin resultados")
            else:
                print(f"✅ [{i}] Comando ejecutado: {primeras_palabras}...")
            
            exitosos += 1
            
        except Exception as e:
            error_msg = str(e)
            
            # Algunos errores son esperados (DROP INDEX si no existe)
            if "Can't DROP" in error_msg or "check that it exists" in error_msg:
                print(f"⚠️  [{i}] Warning: {primeras_palabras}... (índice no existía)")
                warnings += 1
            elif "Duplicate key name" in error_msg:
                print(f"ℹ️  [{i}] Info: Índice ya existe - {primeras_palabras}...")
                exitosos += 1  # No es un error real
            else:
                print(f"❌ [{i}] ERROR: {primeras_palabras}...")
                print(f"     Detalle: {error_msg}")
                errores += 1

print()
print("=" * 80)
print("📊 RESUMEN DE OPTIMIZACIÓN")
print("=" * 80)
print(f"✅ Exitosos: {exitosos}")
print(f"⚠️  Warnings: {warnings}")
print(f"❌ Errores: {errores}")
print()

if errores == 0:
    print("🎉 OPTIMIZACIÓN COMPLETADA EXITOSAMENTE")
    print()
    print("📋 PRÓXIMOS PASOS:")
    print("   1. Ejecutar verificar_indices_explain.py para verificar mejoras")
    print("   2. Comparar performance de queries antes/después")
    print("   3. Monitorear rendimiento en próximos días")
else:
    print("⚠️  OPTIMIZACIÓN COMPLETADA CON ERRORES")
    print("   Revisar los errores arriba y corregir si es necesario")

print()
print("=" * 80)
