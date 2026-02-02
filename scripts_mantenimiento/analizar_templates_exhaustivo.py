#!/usr/bin/env python3
"""
Análisis exhaustivo de templates del sistema
Identifica uso real, duplicados y templates faltantes
"""

import os
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).parent

# ============================================================================
# MAPEO DE VISTAS A TEMPLATES (Análisis manual previo)
# ============================================================================

# Template → Vista que lo usa
TEMPLATE_USAGE_MAP = {
    # ===== POS PRINCIPAL =====
    'pos/pos_bootstrap.html': 'pos_general_views.py - venta_view()',
    'pos/dashboard_ventas.html': 'pos_general_views.py - dashboard_ventas_dia()',
    'pos/gestionar_clientes.html': 'cliente_views.py - gestionar_clientes_view()',
    'pos/almuerzo.html': 'almuerzo_views.py - almuerzo_dashboard()',
    'pos/recargas.html': 'pos_general_views.py - recargas_view()',
    'pos/historial.html': 'pos_general_views.py - historial_view()',
    'pos/gestionar_fotos.html': 'pos_general_views.py - gestionar_fotos_hijos()',
    'pos/gestionar_grados.html': 'pos_general_views.py - gestionar_grados()',
   
    # ===== DUPLICADOS =====
    'pos/pos_general.html': '⚠️ DUPLICADO - NO USADO (ver pos_bootstrap.html)',
    'pos/venta.html': '✅ USADO - pos_views.py - venta() [LEGACY]',
    
    # ===== CUENTA CORRIENTE =====
    'pos/cuenta_corriente.html': '✅ USADO - pos_views.py línea 1953',
    'pos/cuenta_corriente_v2.html': '⚠️ VERIFICAR USO',
    'pos/cuenta_corriente_unificada.html': '✅ USADO - pos_views.py línea 2159',
    
    # ===== BASE =====
    'base.html': '✅ Base principal del sistema',
    'registration/login.html': '✅ Login empleados',
    
    # ===== PORTAL =====
    'portal/base_portal.html': '✅ Base portal clientes',
    'portal/login.html': '✅ Login portal clientes',
    'portal/dashboard.html': '✅ Dashboard portal',
    'portal/pagos.html': '✅ Sistema de pagos portal',
    'portal/mis_hijos.html': '✅ Gestión hijos portal',
    'portal/consumos_hijo.html': '✅ Consumos portal',
    'portal/cargar_saldo.html': '✅ Recarga portal',
    'portal/recargar_tarjeta.html': '✅ Recarga alternativa',
    'portal/restricciones_hijo.html': '✅ Restricciones portal',
    'portal/configurar_2fa.html': '✅ 2FA setup',
    'portal/verificar_2fa.html': '✅ 2FA verify',
    
    # ===== REPORTES =====
    'reportes/almuerzo_reportes.html': '✅ Reportes almuerzos',
    'reportes/almuerzo_reporte_diario.html': '✅ Reporte diario',
    'reportes/almuerzo_reporte_mensual.html': '✅ Reporte mensual',
    'reportes/almuerzo_reporte_estudiante.html': '✅ Reporte estudiante',
    'reportes/reporte_comisiones.html': '✅ Comisiones',
    
    # ===== INVENTARIO =====
    'inventario/inventario_dashboard.html': '✅ Dashboard inventario',
    'inventario/inventario_productos.html': '✅ Lista productos',
    'inventario/kardex_producto.html': '✅ Kardex',
    'inventario/ajuste_inventario.html': '✅ Ajustes',
    'inventario/alertas_inventario.html': '✅ Alertas stock',
    
    # ===== FACTURACIÓN =====
    'facturacion/facturacion_dashboard.html': '✅ Dashboard facturación',
    'facturacion/facturacion_listado.html': '✅ Lista facturas',
    'facturacion/facturacion_reporte_cumplimiento.html': '✅ Cumplimiento SET',
    
    # ===== TICKETS =====
    'tickets/ticket.html': '✅ Ticket venta',
    'tickets/ticket_almuerzo.html': '✅ Ticket almuerzo',
    'tickets/comprobante_recarga.html': '✅ Comprobante recarga',
    
    # ===== SEGURIDAD =====
    'seguridad/dashboard.html': '✅ Dashboard seguridad',
    'seguridad/logs_auditoria.html': '✅ Logs auditoría',
    'seguridad/intentos_login.html': '✅ Intentos login',
    
    # ===== EMAILS =====
    'emails/saldo_bajo.html': '✅ Email saldo bajo',
    'emails/recarga_exitosa.html': '✅ Email recarga',
    'emails/cuenta_pendiente.html': '✅ Email cuenta pendiente',
    
    # ===== EMPLEADOS =====
    'gestion/cambiar_contrasena_empleado.html': '✅ Cambio contraseña empleado',
}

# ============================================================================
# TEMPLATES FALTANTES (Necesarios pero no existen)
# ============================================================================

TEMPLATES_FALTANTES = [
    {
        'nombre': 'gestion/perfil_empleado.html',
        'razon': 'Vista perfil_empleado() existe pero no tiene template',
        'prioridad': 'MEDIA',
        'vista': 'empleado_views.py - perfil_empleado()'
    },
    {
        'nombre': 'gestion/gestionar_empleados.html',
        'razon': 'Necesario para administración de empleados',
        'prioridad': 'MEDIA',
        'vista': 'Pendiente - crear vista lista empleados'
    },
    {
        'nombre': 'reportes/dashboard_unificado_mejorado.html',
        'razon': 'Existe dashboard_unificado.html pero necesita mejoras',
        'prioridad': 'BAJA',
        'vista': 'Optimización de reportes_views.py'
    }
]

# ============================================================================
# ANÁLISIS
# ============================================================================

def encontrar_todos_templates():
    """Encuentra todos los archivos .html en templates/"""
    templates = []
    
    # Buscar en templates/
    templates_dir = BASE_DIR / 'templates'
    if templates_dir.exists():
        for html_file in templates_dir.rglob('*.html'):
            rel_path = html_file.relative_to(templates_dir)
            templates.append(str(rel_path))
    
    # Buscar en gestion/templates/
    gestion_templates_dir = BASE_DIR / 'gestion' / 'templates'
    if gestion_templates_dir.exists():
        for html_file in gestion_templates_dir.rglob('*.html'):
            rel_path = html_file.relative_to(gestion_templates_dir)
            templates.append(f"gestion/{rel_path}")
    
    return sorted(templates)

def buscar_en_codigo(template_name):
    """Busca si un template se usa en archivos Python"""
    referencias = []
    nombre_base = os.path.basename(template_name)
    
    for py_file in BASE_DIR.rglob('*.py'):
        if 'venv' in str(py_file) or 'env' in str(py_file):
            continue
        
        # Ignorar archivos de análisis/documentación
        if py_file.name in ['limpiar_templates.py', 'analizar_templates_exhaustivo.py']:
            continue
        
        if py_file.name.startswith('RESUMEN_') or py_file.name.startswith('REVISION_'):
            continue
        
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                contenido = f.read()
                
                # Buscar por nombre completo o solo nombre de archivo
                if template_name in contenido or nombre_base in contenido:
                    # Verificar que sea en render() o template_name
                    if 'render(' in contenido or 'template_name' in contenido:
                        referencias.append(str(py_file.relative_to(BASE_DIR)))
        except:
            pass
    
    return referencias

def generar_reporte():
    """Genera reporte completo de templates"""
    import sys
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    
    todos_templates = encontrar_todos_templates()
    
    print("=" * 80)
    print("REPORTE EXHAUSTIVO DE TEMPLATES - Sistema Cantina Tita")
    print("=" * 80)
    print(f"\nTotal de templates encontrados: {len(todos_templates)}")
    print()
    
    # ========================================================================
    # SECCIÓN 1: Templates en uso activo
    # ========================================================================
    print("\n" + "=" * 80)
    print("✅ TEMPLATES EN USO ACTIVO")
    print("=" * 80)
    
    en_uso = 0
    for template in todos_templates:
        # Normalizar el path
        template_norm = template.replace('\\', '/')
        
        if template_norm in TEMPLATE_USAGE_MAP:
            uso = TEMPLATE_USAGE_MAP[template_norm]
            
            if not uso.startswith('⚠️'):
                print(f"\n📝 {template_norm}")
                print(f"   └─ {uso}")
                en_uso += 1
    
    print(f"\n📊 Total en uso activo: {en_uso}/{len(todos_templates)}")
    
    # ========================================================================
    # SECCIÓN 2: Templates duplicados o legacy
    # ========================================================================
    print("\n" + "=" * 80)
    print("⚠️ TEMPLATES DUPLICADOS O LEGACY")
    print("=" * 80)
    
    duplicados = []
    for template in todos_templates:
        template_norm = template.replace('\\', '/')
        
        if template_norm in TEMPLATE_USAGE_MAP:
            uso = TEMPLATE_USAGE_MAP[template_norm]
            
            if '⚠️' in uso:
                print(f"\n⚠️ {template_norm}")
                print(f"   └─ {uso}")
                duplicados.append(template_norm)
    
    print(f"\n📊 Total duplicados/legacy: {len(duplicados)}")
    
    # ========================================================================
    # SECCIÓN 3: Templates sin mapeo conocido
    # ========================================================================
    print("\n" + "=" * 80)
    print("❓ TEMPLATES SIN MAPEO CONOCIDO (Requieren verificación)")
    print("=" * 80)
    
    sin_mapeo = []
    for template in todos_templates:
        template_norm = template.replace('\\', '/')
        
        if template_norm not in TEMPLATE_USAGE_MAP:
            # Buscar en código
            refs = buscar_en_codigo(template_norm)
            
            print(f"\n❓ {template_norm}")
            if refs:
                print(f"   └─ Encontrado en: {', '.join(refs[:3])}")
                if len(refs) > 3:
                    print(f"      ... y {len(refs) - 3} más")
            else:
                print(f"   └─ ⚠️ NO encontrado en código Python")
                sin_mapeo.append(template_norm)
    
    print(f"\n📊 Total sin mapeo: {len(sin_mapeo)}")
    
    # ========================================================================
    # SECCIÓN 4: Templates faltantes
    # ========================================================================
    print("\n" + "=" * 80)
    print("❌ TEMPLATES FALTANTES (Necesarios pero no existen)")
    print("=" * 80)
    
    for faltante in TEMPLATES_FALTANTES:
        print(f"\n❌ {faltante['nombre']}")
        print(f"   ├─ Prioridad: {faltante['prioridad']}")
        print(f"   ├─ Razón: {faltante['razon']}")
        print(f"   └─ Vista: {faltante['vista']}")
    
    print(f"\n📊 Total faltantes: {len(TEMPLATES_FALTANTES)}")
    
    # ========================================================================
    # RESUMEN FINAL
    # ========================================================================
    print("\n" + "=" * 80)
    print("📊 RESUMEN EJECUTIVO")
    print("=" * 80)
    
    print(f"\n✅ Templates en uso activo: {en_uso}")
    print(f"⚠️ Templates duplicados/legacy: {len(duplicados)}")
    print(f"❓ Templates sin mapeo conocido: {len(sin_mapeo)}")
    print(f"❌ Templates faltantes (necesarios): {len(TEMPLATES_FALTANTES)}")
    print(f"━━━━━━━━━━━━━━━━━━━━━━")
    print(f"📁 TOTAL: {len(todos_templates)} templates")
    
    # ========================================================================
    # ACCIONES RECOMENDADAS
    # ========================================================================
    print("\n" + "=" * 80)
    print("🔧 ACCIONES RECOMENDADAS")
    print("=" * 80)
    
    print("\n1. ELIMINAR (Duplicados confirmados)")
    print("   ─────────────────────────────────")
    if duplicados:
        for dup in duplicados:
            if 'NO USADO' in TEMPLATE_USAGE_MAP.get(dup, ''):
                print(f"   ❌ {dup}")
    
    print("\n2. VERIFICAR MANUALMENTE")
    print("   ──────────────────────")
    if sin_mapeo:
        for sm in sin_mapeo[:10]:  # Máximo 10
            print(f"   ❓ {sm}")
        if len(sin_mapeo) > 10:
            print(f"   ... y {len(sin_mapeo) - 10} más")
    
    print("\n3. CREAR TEMPLATES FALTANTES")
    print("   ──────────────────────────────")
    for faltante in TEMPLATES_FALTANTES:
        if faltante['prioridad'] in ['ALTA', 'MEDIA']:
            print(f"   ❌ {faltante['nombre']} (Prioridad: {faltante['prioridad']})")
    
    print("\n" + "=" * 80)
    print("✅ Análisis completado")
    print("=" * 80)

if __name__ == '__main__':
    generar_reporte()
