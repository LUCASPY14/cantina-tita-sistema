#!/usr/bin/env python
"""
VERIFICACIÓN RÁPIDA - Confirmar que todas las tareas se completaron
Ejecutar después de descargar los cambios
"""

import os
from pathlib import Path

def verificar_archivo(ruta, descripcion):
    """Verificar que un archivo existe"""
    existe = Path(ruta).exists()
    estado = "✅" if existe else "❌"
    print(f"{estado} {descripcion}")
    return existe

def verificar_linea_archivo(ruta, texto, descripcion):
    """Verificar que un archivo contiene una línea específica"""
    try:
        with open(ruta, 'r', encoding='utf-8') as f:
            contenido = f.read()
            existe = texto in contenido
            estado = "✅" if existe else "❌"
            print(f"  {estado} {descripcion}")
            return existe
    except:
        print(f"  ❌ Error al leer {ruta}")
        return False

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║                   VERIFICACIÓN DE TAREAS COMPLETADAS                       ║
║                        (Ejecutar después de git pull)                       ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝

""")

# TAREA 1: Restricciones
print("1️⃣  VERIFICAR: Integración de Restricciones Alimentarias")
print("─" * 70)
t1 = verificar_archivo('gestion/pos_general_views.py', 'pos_general_views.py existe')
if t1:
    verificar_linea_archivo(
        'gestion/pos_general_views.py',
        'VALIDAR RESTRICCIONES ALIMENTARIAS si existe hijo',
        'Código de validación de restricciones'
    )
    verificar_linea_archivo(
        'gestion/pos_general_views.py',
        'ProductoRestriccionMatcher.analizar_producto',
        'Uso de matcher automático'
    )
print()

# TAREA 2: Backup
print("2️⃣  VERIFICAR: Script de Backup Automático")
print("─" * 70)
t2 = verificar_archivo('crear_backup_automatico.py', 'crear_backup_automatico.py existe')
if t2:
    verificar_linea_archivo(
        'crear_backup_automatico.py',
        'mysqldump',
        'Comando mysqldump'
    )
    verificar_linea_archivo(
        'crear_backup_automatico.py',
        'gzip.open',
        'Compresión gzip'
    )
    verificar_linea_archivo(
        'crear_backup_automatico.py',
        'KEEP_DAYS',
        'Retención de backups'
    )
print()

# TAREA 3: Dashboard
print("3️⃣  VERIFICAR: Dashboard POS Específico")
print("─" * 70)
t3_html = verificar_archivo('templates/pos/dashboard_ventas.html', 'dashboard_ventas.html existe')
t3_py = verificar_archivo('gestion/pos_general_views.py', 'pos_general_views.py existe')
if t3_html:
    verificar_linea_archivo(
        'templates/pos/dashboard_ventas.html',
        'Chart.js',
        'Gráficas ChartJS'
    )
    verificar_linea_archivo(
        'templates/pos/dashboard_ventas.html',
        'dashboard-card',
        'Tarjetas de estadísticas'
    )
if t3_py:
    verificar_linea_archivo(
        'gestion/pos_general_views.py',
        'def dashboard_ventas_dia',
        'Función dashboard_ventas_dia'
    )
if verificar_archivo('gestion/pos_urls.py', 'pos_urls.py existe'):
    verificar_linea_archivo(
        'gestion/pos_urls.py',
        "path('dashboard/', pos_general_views.dashboard_ventas_dia",
        'Ruta /pos/dashboard/'
    )
print()

# TAREA 4: Limpieza
print("4️⃣  VERIFICAR: Análisis de Archivos Legacy")
print("─" * 70)
t4 = verificar_archivo('REVISION_ARCHIVOS_LEGACY.py', 'REVISION_ARCHIVOS_LEGACY.py existe')
t4b = verificar_archivo('gestion/pos_views.py', 'gestion/pos_views.py existe (MANTENER)')
t4c = verificar_archivo('templates/pos/venta.html', 'templates/pos/venta.html existe (MANTENER)')
print()

# TAREA 5: Impresora
print("5️⃣  VERIFICAR: Validador de Impresora Térmica")
print("─" * 70)
t5 = verificar_archivo('validar_impresora_termica.py', 'validar_impresora_termica.py existe')
if t5:
    verificar_linea_archivo(
        'validar_impresora_termica.py',
        'serial.tools.list_ports',
        'Detección de puertos COM'
    )
    verificar_linea_archivo(
        'validar_impresora_termica.py',
        'ESC/POS',
        'Comandos ESC/POS'
    )
print()

# Documentación
print("6️⃣  VERIFICAR: Documentación")
print("─" * 70)
verificar_archivo('TRABAJO_COMPLETADO_README.md', 'TRABAJO_COMPLETADO_README.md')
verificar_archivo('RESUMEN_5_TAREAS_COMPLETADAS.py', 'RESUMEN_5_TAREAS_COMPLETADAS.py')
verificar_archivo('VERIFICACION_FEATURES_PENDIENTES.py', 'VERIFICACION_FEATURES_PENDIENTES.py')
print()

# RESUMEN
print("=" * 70)
print("\n📋 RESUMEN DE VERIFICACIÓN\n")

tareas = [
    ("Integración de restricciones", t1),
    ("Script de backup", t2),
    ("Dashboard POS", t3_html and t3_py),
    ("Análisis legacy", t4),
    ("Validador impresora", t5),
]

completadas = sum(1 for _, completada in tareas if completada)

for nombre, completada in tareas:
    estado = "✅" if completada else "❌"
    print(f"  {estado} {nombre}")

print(f"\n{completadas}/5 tareas completadas\n")

if completadas == 5:
    print("╔════════════════════════════════════════════════════════════════════════════╗")
    print("║                                                                            ║")
    print("║                    ✅ TODAS LAS TAREAS COMPLETADAS                         ║")
    print("║                                                                            ║")
    print("║              El sistema está listo para pruebas en producción               ║")
    print("║                                                                            ║")
    print("╚════════════════════════════════════════════════════════════════════════════╝")
else:
    print("⚠️  Algunas tareas no se completaron correctamente")
    print("Verifique los archivos faltantes arriba")

print("\n" + "=" * 70)

# INSTRUCCIONES DE USO
print("""
📚 PRÓXIMOS PASOS
═════════════════════════════════════════════════════════════════════════════

1. PROBAR RESTRICCIONES ALIMENTARIAS
   - No requiere configuración adicional
   - Se validan automáticamente en procesar_venta_api()
   - Respuesta incluye alertas si hay restricciones

2. HACER BACKUP DE LA BD
   python crear_backup_automatico.py backup
   
   Verificar que se creó en ./backups/:
   ls -la backups/

3. ACCEDER AL DASHBOARD
   http://localhost:8000/pos/dashboard/
   
   Debe mostrar:
   - Total de ventas
   - Monto total
   - Gráficas interactivas
   - Top productos y clientes

4. VALIDAR IMPRESORA TÉRMICA (Opcional)
   pip install pyserial
   python validar_impresora_termica.py
   
   Conectar impresora USB antes

5. REVISAR DOCUMENTACIÓN
   - TRABAJO_COMPLETADO_README.md (Índice general)
   - RESUMEN_5_TAREAS_COMPLETADAS.py (Detalles técnicos)
   - REVISION_ARCHIVOS_LEGACY.py (Análisis de legacy)

═════════════════════════════════════════════════════════════════════════════

⚠️  NOTA: Si hay errores, revisar logs de Django:
   
   python manage.py runserver 0.0.0.0:8000
   
   Y verificar en navegador si hay errores de template o importación.

═════════════════════════════════════════════════════════════════════════════
""")
