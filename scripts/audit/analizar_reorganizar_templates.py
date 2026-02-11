"""
Script para analizar y reorganizar templates por acciones/categorías
Sistema usa HTML + Tailwind CSS
"""
import os
from pathlib import Path
from collections import defaultdict
import json

# Directorio base de templates
TEMPLATES_DIR = Path("frontend/templates")

# Definir estructura de categorías por acción
ESTRUCTURA_ORGANIZACION = {
    # AUTH - Autenticación y Seguridad
    "auth": {
        "descripcion": "Autenticación, seguridad y control de acceso",
        "subcategorias": {
            "login": ["login", "iniciar_sesion"],
            "password": ["password", "contrasena", "recuperar", "restablecer", "cambiar_password"],
            "2fa": ["2fa", "verificar", "activar", "deshabilitar"],
            "security": ["auditoria", "logs", "intentos"],
        }
    },
    
    # DASHBOARD - Tableros y vistas principales
    "dashboard": {
        "descripcion": "Paneles de control y dashboards",
        "subcategorias": {
            "main": ["dashboard_principal", "main"],
            "pos": ["dashboard.*pos", "pos_dashboard"],
            "sales": ["ventas", "dashboard_ventas"],
            "purchases": ["compras", "dashboard_compras"],
            "inventory": ["inventario_dashboard"],
            "lunch": ["almuerzos_dashboard"],
            "commissions": ["comisiones_dashboard"],
            "cash": ["cajas_dashboard"],
            "security": ["dashboard_seguridad"],
            "saldos": ["dashboard_saldos"],
        }
    },
    
    # SALES - Ventas y POS
    "sales": {
        "descripcion": "Ventas, POS y tickets",
        "subcategorias": {
            "new": ["nueva_venta", "new_sale", "venta_modern"],
            "list": ["lista_ventas", "venta_lista"],
            "ticket": ["ticket"],
            "history": ["historial"],
        }
    },
    
    # PURCHASES - Compras y proveedores
    "purchases": {
        "descripcion": "Compras, proveedores y recepción",
        "subcategorias": {
            "new": ["nueva_compra", "nueva"],
            "suppliers": ["proveedores", "proveedor_detalle"],
            "reception": ["recepcion_mercaderia"],
            "debts": ["deuda_proveedores"],
        }
    },
    
    # INVENTORY - Inventario y productos
    "inventory": {
        "descripcion": "Gestión de inventario y productos",
        "subcategorias": {
            "products": ["productos", "product", "crear_productos", "editar_productos"],
            "list": ["productos_lista", "products_list", "lista_productos"],
            "import": ["productos_importar", "importar_preview"],
            "adjust": ["ajuste_inventario", "adjust_inventory"],
            "alerts": ["alertas_inventario", "alerts"],
            "kardex": ["kardex"],
            "categories": ["categoria"],
            "search": ["buscar_productos"],
        }
    },
    
    # CLIENTS - Clientes y tarjetas
    "clients": {
        "descripcion": "Gestión de clientes y tarjetas",
        "subcategorias": {
            "list": ["clientes_lista", "clientes_list", "lista_clientes"],
            "create": ["crear_cliente"],
            "manage": ["gestionar_clientes"],
            "cards": ["tarjeta", "alertas_tarjetas"],
            "grades": ["grados", "gestionar_grados", "historial_grados"],
            "photos": ["fotos", "gestionar_fotos"],
        }
    },
    
    # PAYMENTS - Pagos y recargas
    "payments": {
        "descripcion": "Pagos, recargas y saldo",
        "subcategorias": {
            "recharge": ["recargar", "recargas", "cargar_saldo"],
            "process": ["procesar_recargas"],
            "validate": ["validar_pago", "validar_carga", "validar_pagos"],
            "pending": ["pendientes", "lista_cargas_pendientes", "lista_pagos_pendientes"],
            "status": ["pago_exitoso", "pago_cancelado", "estado_recarga"],
            "voucher": ["comprobante"],
            "history": ["historial_recargas"],
            "notifications": ["notificaciones_saldo"],
            "terms": ["terminos_saldo_negativo"],
            "authorization": ["autorizar_saldo_negativo", "autorizaciones_saldo_negativo"],
        }
    },
    
    # ACCOUNTS - Cuenta corriente
    "accounts": {
        "descripcion": "Cuenta corriente y estados",
        "subcategorias": {
            "current": ["cuenta_corriente"],
            "unified": ["unificada"],
            "statement": ["estado_cuenta"],
            "detail": ["cc_detalle"],
            "reconciliation": ["conciliacion_pagos"],
        }
    },
    
    # CASH_REGISTER - Caja
    "cash_register": {
        "descripcion": "Gestión de caja",
        "subcategorias": {
            "opening": ["apertura_caja"],
            "closing": ["cierre_caja"],
            "count": ["arqueo_caja"],
            "dashboard": ["cajas_dashboard"],
        }
    },
    
    # LUNCH - Servicio de almuerzo
    "lunch": {
        "descripcion": "Gestión de almuerzos",
        "subcategorias": {
            "main": ["almuerzo.html$"],  # Solo almuerzo.html exacto
            "menu": ["menu_diario"],
            "plans": ["planes_almuerzo"],
            "subscriptions": ["suscripciones_almuerzo"],
            "registration": ["registro_consumo"],
            "reports": ["almuerzo_reporte", "almuerzo_reportes"],
            "billing": ["almuerzo_generar_cuentas", "almuerzo_cuentas_mensuales", "almuerzo_pagar"],
            "ticket": ["ticket_almuerzo"],
            "pricing": ["configurar_precio"],
        }
    },
    
    # REPORTS - Reportes
    "reports": {
        "descripcion": "Reportes y estadísticas",
        "subcategorias": {
            "general": ["reportes.html$", "index.html"],  # reportes generales
            "sales": ["reportes_pos"],
            "lunch": ["reportes_almuerzos"],
            "commissions": ["reporte_comisiones"],
            "billing": ["facturacion"],
            "authorizations": ["logs_autorizaciones"],
        }
    },
    
    # EMPLOYEES - Empleados
    "employees": {
        "descripcion": "Gestión de empleados",
        "subcategorias": {
            "list": ["gestionar_empleados"],
            "create": ["crear_empleado", "crear.html"],
            "profile": ["perfil_empleado"],
            "password": ["cambiar_contrasena_empleado"],
        }
    },
    
    # PORTAL - Portal padres
    "portal": {
        "descripcion": "Portal de padres",
        "subcategorias": {
            "children": ["mis_hijos", "mis-hijos", "consumos_hijo", "consumos-hijo", "restricciones_hijo"],
            "profile": ["perfil"],
            "registration": ["registro"],
            "limits": ["configurar_limites"],
        }
    },
    
    # ADMIN - Administración
    "admin": {
        "descripcion": "Administración del sistema",
        "subcategorias": {
            "authorizations": ["admin_autorizaciones"],
            "alerts": ["alertas_sistema"],
            "config": ["configurar_tarifas"],
        }
    },
    
    # BASE - Templates base
    "base": {
        "descripcion": "Templates base y layouts",
        "subcategorias": {
            "main": ["^base", "gestion_base", "pos_base"],
        }
    },
    
    # COMPONENTS - Componentes reutilizables
    "components": {
        "descripcion": "Componentes compartidos",
        "subcategorias": {
            "navigation": ["navigation", "footer"],
            "messages": ["messages"],
            "pagination": ["pagination"],
            "grids": ["grid"],
            "modals": ["modal"],
            "widgets": ["widget"],
        }
    },
    
    # EMAILS - Templates de email
    "emails": {
        "descripcion": "Templates de correos electrónicos",
        "subcategorias": {
            "notifications": ["notificacion", "recarga_exitosa", "saldo_bajo", "cuenta_pendiente"],
            "reminders": ["recordatorio", "tarjeta_bloqueada"],
        }
    },
}

def analizar_estructura_actual():
    """Analiza la estructura actual de templates"""
    print("=" * 80)
    print("ANÁLISIS DE ESTRUCTURA ACTUAL DE TEMPLATES")
    print("=" * 80)
    
    templates_encontrados = defaultdict(list)
    total = 0
    
    # Recorrer todos los templates
    for root, dirs, files in os.walk(TEMPLATES_DIR):
        for file in files:
            if file.endswith('.html'):
                ruta_relativa = os.path.relpath(os.path.join(root, file), TEMPLATES_DIR)
                carpeta = os.path.dirname(ruta_relativa)
                templates_encontrados[carpeta].append(file)
                total += 1
    
    print(f"\n📊 Total de templates encontrados: {total}")
    print(f"📁 Total de carpetas: {len(templates_encontrados)}")
    print("\n" + "=" * 80)
    print("DISTRIBUCIÓN POR CARPETA:")
    print("=" * 80)
    
    for carpeta in sorted(templates_encontrados.keys()):
        archivos = templates_encontrados[carpeta]
        print(f"\n📂 {carpeta or '(raíz)'} ({len(archivos)} archivos)")
        for archivo in sorted(archivos):
            print(f"   • {archivo}")
    
    return templates_encontrados, total

def clasificar_templates():
    """Clasifica templates según la nueva estructura"""
    print("\n" + "=" * 80)
    print("CLASIFICACIÓN POR ACCIÓN/CATEGORÍA")
    print("=" * 80)
    
    import re
    
    clasificacion = defaultdict(lambda: defaultdict(list))
    sin_clasificar = []
    
    # Recorrer todos los templates
    for root, dirs, files in os.walk(TEMPLATES_DIR):
        for file in files:
            if not file.endswith('.html'):
                continue
                
            ruta_completa = os.path.join(root, file)
            ruta_relativa = os.path.relpath(ruta_completa, TEMPLATES_DIR)
            clasificado = False
            
            # Intentar clasificar
            for categoria, info in ESTRUCTURA_ORGANIZACION.items():
                if clasificado:
                    break
                    
                for subcategoria, patrones in info.get('subcategorias', {}).items():
                    for patron in patrones:
                        # Usar regex para match más flexible
                        if re.search(patron, file, re.IGNORECASE):
                            clasificacion[categoria][subcategoria].append({
                                'archivo': file,
                                'ruta_actual': ruta_relativa,
                                'patron_match': patron
                            })
                            clasificado = True
                            break
                    if clasificado:
                        break
            
            if not clasificado:
                sin_clasificar.append(ruta_relativa)
    
    # Mostrar clasificación
    for categoria in sorted(clasificacion.keys()):
        desc = ESTRUCTURA_ORGANIZACION[categoria]['descripcion']
        print(f"\n{'=' * 80}")
        print(f"📁 {categoria.upper()} - {desc}")
        print(f"{'=' * 80}")
        
        for subcategoria in sorted(clasificacion[categoria].keys()):
            items = clasificacion[categoria][subcategoria]
            print(f"\n  📂 {subcategoria}/ ({len(items)} archivos)")
            for item in sorted(items, key=lambda x: x['archivo']):
                print(f"     • {item['archivo']:<40} ← {item['ruta_actual']}")
    
    # Mostrar sin clasificar
    if sin_clasificar:
        print(f"\n{'=' * 80}")
        print(f"⚠️  SIN CLASIFICAR ({len(sin_clasificar)} archivos)")
        print(f"{'=' * 80}")
        for item in sorted(sin_clasificar):
            print(f"   • {item}")
    
    return clasificacion, sin_clasificar

def generar_propuesta_estructura():
    """Genera propuesta de nueva estructura"""
    print("\n" + "=" * 80)
    print("PROPUESTA DE NUEVA ESTRUCTURA")
    print("=" * 80)
    
    print("""
frontend/templates/
├── base/                          # Templates base
│   ├── base.html                  # Base general
│   ├── base_modern.html           # Base moderna
│   ├── pos_base.html              # Base POS
│   └── portal_base.html           # Base portal padres
│
├── components/                    # Componentes reutilizables
│   ├── navigation/
│   │   ├── navbar.html
│   │   └── footer.html
│   ├── forms/
│   │   ├── pagination.html
│   │   └── messages.html
│   ├── grids/
│   │   └── productos_grid.html
│   └── modals/
│       └── autorizar_saldo.html
│
├── auth/                          # Autenticación
│   ├── login.html
│   ├── password/
│   │   ├── cambiar.html
│   │   ├── recuperar.html
│   │   └── restablecer.html
│   ├── 2fa/
│   │   ├── activar.html
│   │   ├── verificar.html
│   │   └── deshabilitar.html
│   └── security/
│       ├── logs_auditoria.html
│       └── intentos_login.html
│
├── dashboard/                     # Dashboards
│   ├── main.html                  # Dashboard principal
│   ├── pos.html
│   ├── sales.html
│   ├── purchases.html
│   ├── inventory.html
│   ├── lunch.html
│   ├── commissions.html
│   └── security.html
│
├── sales/                         # Ventas
│   ├── new.html
│   ├── list.html
│   ├── ticket.html
│   └── history.html
│
├── purchases/                     # Compras
│   ├── new.html
│   ├── dashboard.html
│   ├── suppliers/
│   │   ├── list.html
│   │   └── detail.html
│   ├── reception/
│   │   └── mercaderia.html
│   └── debts/
│       └── proveedores.html
│
├── inventory/                     # Inventario
│   ├── dashboard.html
│   ├── products/
│   │   ├── list.html
│   │   ├── create.html
│   │   ├── edit.html
│   │   └── import.html
│   ├── categories/
│   │   ├── list.html
│   │   └── form.html
│   ├── adjustments/
│   │   └── adjust.html
│   ├── alerts/
│   │   └── inventory.html
│   └── kardex/
│       └── producto.html
│
├── clients/                       # Clientes
│   ├── list.html
│   ├── create.html
│   ├── manage.html
│   ├── cards/
│   │   └── alerts.html
│   ├── grades/
│   │   ├── manage.html
│   │   └── history.html
│   └── photos/
│       └── manage.html
│
├── payments/                      # Pagos y recargas
│   ├── recharge/
│   │   ├── new.html
│   │   ├── list.html
│   │   └── process.html
│   ├── validate/
│   │   ├── pago.html
│   │   └── carga.html
│   ├── pending/
│   │   ├── cargas.html
│   │   └── pagos.html
│   ├── status/
│   │   ├── exitoso.html
│   │   ├── cancelado.html
│   │   └── estado.html
│   ├── voucher/
│   │   └── comprobante.html
│   ├── history/
│   │   └── recargas.html
│   ├── notifications/
│   │   ├── saldo.html
│   │   └── widget.html
│   └── authorization/
│       ├── authorize.html
│       └── list.html
│
├── accounts/                      # Cuenta corriente
│   ├── current.html
│   ├── unified.html
│   ├── statement.html
│   ├── detail.html
│   └── reconciliation.html
│
├── cash_register/                 # Caja
│   ├── dashboard.html
│   ├── opening.html
│   ├── closing.html
│   └── count.html
│
├── lunch/                         # Almuerzos
│   ├── dashboard.html
│   ├── main.html
│   ├── menu/
│   │   └── daily.html
│   ├── plans/
│   │   ├── list.html
│   │   └── subscriptions.html
│   ├── registration/
│   │   └── consume.html
│   ├── reports/
│   │   ├── daily.html
│   │   ├── monthly.html
│   │   ├── student.html
│   │   └── list.html
│   ├── billing/
│   │   ├── generate.html
│   │   ├── monthly.html
│   │   └── pay.html
│   ├── ticket/
│   │   └── ticket.html
│   └── pricing/
│       └── config.html
│
├── reports/                       # Reportes
│   ├── index.html
│   ├── sales/
│   │   └── pos.html
│   ├── lunch/
│   │   └── almuerzos.html
│   ├── commissions/
│   │   └── reporte.html
│   ├── billing/
│   │   ├── dashboard.html
│   │   ├── listado.html
│   │   └── mensual.html
│   └── authorizations/
│       └── logs.html
│
├── employees/                     # Empleados
│   ├── list.html
│   ├── create.html
│   ├── profile.html
│   └── password/
│       └── change.html
│
├── portal/                        # Portal padres
│   ├── base.html
│   ├── dashboard.html
│   ├── children/
│   │   ├── list.html
│   │   ├── consumos.html
│   │   └── restrictions.html
│   ├── profile/
│   │   └── perfil.html
│   ├── registration/
│   │   └── registro.html
│   └── config/
│       └── limits.html
│
├── admin/                         # Administración
│   ├── dashboard.html
│   ├── authorizations.html
│   ├── alerts.html
│   └── config/
│       └── tarifas.html
│
└── emails/                        # Emails
    ├── notifications/
    │   ├── recarga_exitosa.html
    │   ├── saldo_bajo.html
    │   └── cuenta_pendiente.html
    └── reminders/
        ├── deuda_amable.html
        ├── deuda_urgente.html
        ├── deuda_critico.html
        └── tarjeta_bloqueada.html
""")

def generar_reporte_json():
    """Genera reporte en JSON"""
    clasificacion, sin_clasificar = clasificar_templates()
    
    reporte = {
        "fecha_analisis": "2026-02-03",
        "total_templates": sum(len(items) for cat in clasificacion.values() for items in cat.values()) + len(sin_clasificar),
        "clasificados": {
            cat: {
                subcat: [item['ruta_actual'] for item in items]
                for subcat, items in subcats.items()
            }
            for cat, subcats in clasificacion.items()
        },
        "sin_clasificar": sin_clasificar,
        "estructura_propuesta": ESTRUCTURA_ORGANIZACION
    }
    
    with open('reporte_templates_organizacion.json', 'w', encoding='utf-8') as f:
        json.dump(reporte, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Reporte JSON generado: reporte_templates_organizacion.json")

def main():
    """Función principal"""
    print("\n🔍 ANÁLISIS EXHAUSTIVO DE TEMPLATES")
    print("Sistema: HTML + Tailwind CSS")
    print("=" * 80)
    
    # 1. Analizar estructura actual
    templates_actuales, total = analizar_estructura_actual()
    
    # 2. Clasificar templates
    clasificacion, sin_clasificar = clasificar_templates()
    
    # 3. Generar propuesta
    generar_propuesta_estructura()
    
    # 4. Estadísticas finales
    print("\n" + "=" * 80)
    print("ESTADÍSTICAS FINALES")
    print("=" * 80)
    
    total_clasificados = sum(len(items) for cat in clasificacion.values() for items in cat.values())
    porcentaje = (total_clasificados / total * 100) if total > 0 else 0
    
    print(f"\n✅ Templates clasificados: {total_clasificados}/{total} ({porcentaje:.1f}%)")
    print(f"⚠️  Templates sin clasificar: {len(sin_clasificar)}")
    print(f"📁 Categorías: {len(clasificacion)}")
    
    # 5. Generar JSON
    generar_reporte_json()
    
    print("\n" + "=" * 80)
    print("✅ ANÁLISIS COMPLETADO")
    print("=" * 80)

if __name__ == "__main__":
    main()
