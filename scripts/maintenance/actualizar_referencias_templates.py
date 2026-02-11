# SCRIPT PARA ACTUALIZAR REFERENCIAS EN VIEWS.PY

import os
import re

# Mapeo de templates reorganizados
TEMPLATE_MAPPING = {
    # Portal
    'apps/portal/dashboard/dashboard.html': 'portal/dashboard/main.html',
    'portal/dashboard/dashboard.html': 'portal/dashboard/main.html',
    
    # POS  
    'apps/pos/dashboard/dashboard.html': 'pos/dashboard/main.html',
    'pos/dashboard/dashboard.html': 'pos/dashboard/main.html',
    'apps/pos/ventas/dashboard.html': 'pos/sales/dashboard.html',
    'apps/pos/ventas/nueva_venta.html': 'pos/sales/new_sale.html',
    'apps/pos/inventario/dashboard.html': 'pos/inventory/dashboard.html',
    'apps/pos/inventario/productos.html': 'pos/inventory/products_list.html',
    'apps/pos/inventario/ajuste_inventario.html': 'pos/inventory/adjust_inventory.html',
    'apps/pos/inventario/alertas_inventario.html': 'pos/inventory/alerts.html',
    
    # Gestión
    'apps/gestion/dashboard/dashboard.html': 'gestion/dashboard/main.html',
    'gestion/dashboard/dashboard.html': 'gestion/dashboard/main.html', 
    'apps/gestion/productos/crear.html': 'gestion/products/create.html',
    'apps/gestion/productos/editar.html': 'gestion/products/edit.html',
    'apps/gestion/productos/lista.html': 'gestion/products/list.html',
    'apps/gestion/categorias/crear.html': 'gestion/categories/create.html',
    'apps/gestion/categorias/editar.html': 'gestion/categories/edit.html',
    'apps/gestion/categorias/lista.html': 'gestion/categories/list.html',
    
    # Auth
    'registration/login.html': 'auth/login.html',
    
    # Base
    'base/pos_base.html': 'base/base_pos.html',
    'base/gestion_base.html': 'base/base_admin.html',
}

def update_template_references():
    """Actualizar referencias de templates en archivos views.py"""
    
    views_files = [
        'D:/anteproyecto20112025/backend/views_basicas.py',
        'D:/anteproyecto20112025/backend/pos_views_basicas.py',
    ]
    
    for views_file in views_files:
        if os.path.exists(views_file):
            print(f"Actualizando: {views_file}")
            
            with open(views_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Contador de cambios
            changes = 0
            
            # Buscar y reemplazar referencias
            for old_path, new_path in TEMPLATE_MAPPING.items():
                if old_path in content:
                    content = content.replace(f"'{old_path}'", f"'{new_path}'")
                    content = content.replace(f'"{old_path}"', f'"{new_path}"')
                    changes += 1
                    print(f"  ✓ {old_path} → {new_path}")
            
            if changes > 0:
                # Backup original
                backup_file = f"{views_file}.backup"
                with open(backup_file, 'w', encoding='utf-8') as f:
                    f.write(open(views_file, 'r', encoding='utf-8').read())
                
                # Escribir archivo actualizado
                with open(views_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"  → {changes} referencias actualizadas en {views_file}")
            else:
                print(f"  → No se encontraron referencias para actualizar")

if __name__ == "__main__":
    update_template_references()
    print("\n✅ Actualización de referencias completada")