import os
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).parent

def mover_archivos(origen, destino):
    """Mueve archivos manteniendo estructura"""
    if os.path.exists(origen):
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        shutil.move(str(origen), str(destino))
        print(f"✓ Movido: {origen} -> {destino}")
    else:
        print(f"✗ No existe: {origen}")

# 1. Reorganizar app gestion
print("\n=== REORGANIZANDO APP GESTION ===")
mover_archivos(
    BASE_DIR / "gestion" / "templates" / "emails" / "cuenta_pendiente.html",
    BASE_DIR / "gestion" / "templates" / "gestion" / "emails" / "cuenta_pendiente.html"
)
mover_archivos(
    BASE_DIR / "gestion" / "templates" / "emails" / "recarga_exitosa.html",
    BASE_DIR / "gestion" / "templates" / "gestion" / "emails" / "recarga_exitosa.html"
)
mover_archivos(
    BASE_DIR / "gestion" / "templates" / "emails" / "saldo_bajo.html",
    BASE_DIR / "gestion" / "templates" / "gestion" / "emails" / "saldo_bajo.html"
)

# 2. Mover templates de gestion desde templates globales
gestion_files = [
    "cambiar_contrasena_empleado.html",
    "categorias_lista.html",
    "categoria_form.html",
    "facturacion_dashboard.html",
    "facturacion_listado.html",
    "facturacion_reporte_cumplimiento.html",
    "gestionar_empleados.html",
    "perfil_empleado.html",
    "productos_importar.html",
    "productos_importar_preview.html",
    "producto_form.html",
    "validar_pagos.html"
]

print("\n=== MOVIENDO TEMPLATES GESTION ===")
for file in gestion_files:
    mover_archivos(
        BASE_DIR / "templates" / "gestion" / file,
        BASE_DIR / "gestion" / "templates" / "gestion" / file
    )

# 3. Mover templates de pos
print("\n=== REORGANIZANDO APP POS ===")
# Crear directorio pos si no existe
pos_templates_dir = BASE_DIR / "pos" / "templates" / "pos"
pos_templates_dir.mkdir(parents=True, exist_ok=True)

# Mover archivos de pos
pos_source = BASE_DIR / "templates" / "pos"
if pos_source.exists():
    for item in pos_source.iterdir():
        if item.is_file():
            destino = pos_templates_dir / item.name
            shutil.move(str(item), str(destino))
            print(f"✓ Movido: {item.name} -> pos/templates/pos/")
        elif item.is_dir():
            # Mover subdirectorios como almuerzo
            shutil.move(str(item), str(pos_templates_dir / item.name))
            print(f"✓ Movido directorio: {item.name}/ -> pos/templates/pos/")

# 4. Mover almuerzo si está separado
almuerzo_source = BASE_DIR / "templates" / "almuerzo"
if almuerzo_source.exists():
    almuerzo_dest = pos_templates_dir / "almuerzo"
    almuerzo_dest.mkdir(parents=True, exist_ok=True)
    for item in almuerzo_source.iterdir():
        shutil.move(str(item), str(almuerzo_dest / item.name))
    print("✓ Movida carpeta almuerzo a pos/templates/pos/")

print("\n=== REORGANIZACIÓN COMPLETADA ===")
print("\nRecuerda actualizar:")
print("1. settings.py - Configurar TEMPLATES con APP_DIRS=True")
print("2. Todas las views - Usar paths con namespace (app/nombre_template.html)")
print("3. Templates que extienden - Verificar paths de 'extends'")
