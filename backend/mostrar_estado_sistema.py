#!/usr/bin/env python
"""
Script para crear dashboards y mostrar el estado completo del sistema
"""
import os
import sys
import django
from dotenv import load_dotenv
from datetime import datetime, date, timedelta

# Cargar variables de entorno
load_dotenv()

# Configurar Django
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from gestion.models import (
    # Configuraciones
    ConfiguracionSistema, 
    
    # Analytics
    KpiMetrica, ReporteTemplate, Dashboard,
    
    # Comunicaciones
    EmailTemplate, SmsTemplate,
    
    # Integraciones
    ProveedorApi, EndpointApi,
    
    # Core models
    Empleado, TipoRolGeneral, Cliente
)

def crear_dashboards():
    """Crear dashboards por roles"""
    print("\n📊 CREANDO DASHBOARDS POR ROL")
    print("-" * 50)
    
    # Crear un empleado admin si no existe para los dashboards
    admin_empleado, created = Empleado.objects.get_or_create(
        nombre='Admin',
        apellido='Sistema',
        defaults={
            'email': 'admin@cantinatita.com',
            'telefono': '0000000000',
            'direccion': 'Sistema',
            'activo': True
        }
    )
    
    if created:
        print(f"   ✅ Empleado admin creado para dashboards")
    
    dashboards = [
        {
            'nombre': 'Dashboard Cajero',
            'descripcion': 'Vista principal para cajeros',
            'empleado': admin_empleado,
            'configuracion_json': {
                'tipo_usuario': 'CAJERO',
                    'widgets': [
                        {
                            'id': 'ventas_hoy',
                            'titulo': 'Ventas de Hoy',
                            'tipo': 'NUMERO',
                            'posicion': {'x': 0, 'y': 0, 'w': 3, 'h': 2},
                            'kpi': 'Ventas Diarias'
                        },
                        {
                            'id': 'transacciones_hoy',
                            'titulo': 'Transacciones',
                            'tipo': 'NUMERO',
                            'posicion': {'x': 3, 'y': 0, 'w': 3, 'h': 2},
                            'kpi': 'Número de Transacciones'  
                        },
                        {
                            'id': 'ticket_promedio',
                            'titulo': 'Ticket Promedio',
                            'tipo': 'NUMERO',
                            'posicion': {'x': 6, 'y': 0, 'w': 3, 'h': 2},
                            'kpi': 'Ticket Promedio'
                        },
                        {
                            'id': 'stock_bajo',
                            'titulo': 'Productos Stock Bajo',
                            'tipo': 'ALERTA',
                            'posicion': {'x': 9, 'y': 0, 'w': 3, 'h': 2},
                            'kpi': 'Productos con Stock Bajo'
                        }
                    ]
                },
                'tema': {
                    'color_primario': '#06a775',
                    'color_secundario': '#e7f5f0',
                    'fuente': 'Inter'
                }
            },
            'es_publico': True,
            'predeterminado': True
        },
        {
            'nombre': 'Dashboard Gerente',
            'descripcion': 'Vista ejecutiva para gerentes',
            'empleado': admin_empleado,
            'configuracion_json': {
                'tipo_usuario': 'GERENTE',
                'widgets': [
                    {
                        'id': 'ventas_hoy',
                        'titulo': 'Ventas de Hoy',
                        'tipo': 'NUMERO',
                        'posicion': {'x': 0, 'y': 0, 'w': 2, 'h': 2}
                    },
                    {
                        'id': 'clientes_activos',
                        'titulo': 'Clientes Activos',
                        'tipo': 'NUMERO',
                        'posicion': {'x': 2, 'y': 0, 'w': 2, 'h': 2}
                    },
                    {
                        'id': 'margen_rentabilidad',
                        'titulo': 'Margen (%)',
                        'tipo': 'PORCENTAJE',
                        'posicion': {'x': 4, 'y': 0, 'w': 2, 'h': 2}
                    },
                    {
                        'id': 'grafico_ventas_semana',
                        'titulo': 'Ventas Últimos 7 Días',
                        'tipo': 'GRAFICO_LINEA',
                        'posicion': {'x': 0, 'y': 2, 'w': 6, 'h': 4}
                    },
                    {
                        'id': 'top_productos',
                        'titulo': 'Top 5 Productos',
                        'tipo': 'TABLA',
                        'posicion': {'x': 6, 'y': 2, 'w': 6, 'h': 4}
                    }
                ],
                'tema': {
                    'color_primario': '#1e40af',
                    'color_secundario': '#eff6ff',
                    'fuente': 'Inter'
                }
            },
            'es_publico': True,
            'predeterminado': False
        },
        {
            'nombre': 'Dashboard Administrador',
            'descripcion': 'Vista completa del sistema',
            'empleado': admin_empleado,
            'configuracion_json': {
                'tipo_usuario': 'ADMINISTRADOR',
                'widgets': [
                    {
                        'id': 'kpis_principales',
                        'titulo': 'KPIs Principales',
                        'tipo': 'RESUMEN',
                        'posicion': {'x': 0, 'y': 0, 'w': 12, 'h': 2}
                    },
                    {
                        'id': 'alertas_sistema',
                        'titulo': 'Alertas del Sistema',
                        'tipo': 'ALERTAS',
                        'posicion': {'x': 0, 'y': 2, 'w': 4, 'h': 3}
                    },
                    {
                        'id': 'integraciones_estado',
                        'titulo': 'Estado APIs',
                        'tipo': 'ESTADO',
                        'posicion': {'x': 4, 'y': 2, 'w': 4, 'h': 3}
                    },
                    {
                        'id': 'actividad_usuarios',
                        'titulo': 'Actividad de Usuarios',
                        'tipo': 'TABLA',
                        'posicion': {'x': 8, 'y': 2, 'w': 4, 'h': 3}
                    },
                    {
                        'id': 'reportes_programados',
                        'titulo': 'Reportes Programados',
                        'tipo': 'TABLA',
                        'posicion': {'x': 0, 'y': 5, 'w': 6, 'h': 3}
                    },
                    {
                        'id': 'configuraciones_sistema',
                        'titulo': 'Configuraciones',
                        'tipo': 'CONFIGURACION',
                        'posicion': {'x': 6, 'y': 5, 'w': 6, 'h': 3}
                    }
                ],
                'tema': {
                    'color_primario': '#7c2d12',
                    'color_secundario': '#fef7f0',
                    'fuente': 'Inter'
                }
            },
            'es_publico': True,
            'predeterminado': False
        }
    ]
    
    creados = 0
    for dashboard_data in dashboards:
        dashboard, created = Dashboard.objects.get_or_create(
            nombre=dashboard_data['nombre'],
            defaults=dashboard_data
        )
        if created:
            print(f"   ✅ Dashboard: {dashboard_data['nombre']}")
            creados += 1
        else:
            print(f"   ⚪ Dashboard: {dashboard_data['nombre']} - Ya existe")
    
    print(f"\n📊 Dashboards creados: {creados}")
    return creados > 0

def mostrar_estado_sistema():
    """Mostrar estado completo del sistema"""
    print("\n" + "=" * 80)
    print("🎯 ESTADO COMPLETO DEL SISTEMA CANTINA TITA")
    print("=" * 80)
    
    # Obtener configuración del sistema
    sistema_config = ConfiguracionSistema.objects.filter(categoria='GENERAL')
    
    print("\n📋 INFORMACIÓN DEL SISTEMA:")
    for config in sistema_config[:3]:  # Solo mostrar las primeras 3
        print(f"   • {config.descripcion}: {config.valor}")
    
    print("\n👥 ROLES Y USUARIOS:")
    roles = TipoRolGeneral.objects.all()
    for rol in roles:
        empleados_count = Empleado.objects.filter(rol=rol).count()
        print(f"   • {rol.nombre}: {empleados_count} usuarios")
    
    print("\n📊 MÉTRICAS Y ANALYTICS:")
    kpis = KpiMetrica.objects.all()
    print(f"   • KPIs configurados: {kpis.count()}")
    for kpi in list(kpis)[:3]:
        print(f"     - {kpi.nombre} ({kpi.categoria})")
    
    dashboards = Dashboard.objects.all()
    print(f"   • Dashboards por rol: {dashboards.count()}")
    
    print("\n📧 COMUNICACIONES:")
    email_templates = EmailTemplate.objects.all()
    sms_templates = SmsTemplate.objects.all()
    print(f"   • Plantillas de email: {email_templates.count()}")
    print(f"   • Plantillas de SMS: {sms_templates.count()}")
    
    print("\n🔌 INTEGRACIONES:")
    proveedores = ProveedorApi.objects.all()
    endpoints = EndpointApi.objects.all()
    print(f"   • Proveedores de API: {proveedores.count()}")
    print(f"   • Endpoints configurados: {endpoints.count()}")
    
    for proveedor in proveedores:
        estado = "🟢 Activa" if proveedor.esta_activo else "🔴 Inactiva"
        print(f"     - {proveedor.nombre} ({proveedor.tipo_servicio}): {estado}")
    
    print("\n📊 REPORTES:")
    reportes = ReporteTemplate.objects.all()
    print(f"   • Plantillas de reportes: {reportes.count()}")
    for reporte in reportes:
        print(f"     - {reporte.nombre} (Frecuencia: {reporte.frecuencia_auto})")
    
    print("\n⚙️ CONFIGURACIONES:")
    all_configs = ConfiguracionSistema.objects.all()
    categorias = all_configs.values_list('categoria', flat=True).distinct()
    for categoria in categorias:
        count = all_configs.filter(categoria=categoria).count()
        print(f"   • {categoria}: {count} configuraciones")

def mostrar_guia_uso():
    """Mostrar guía de uso del sistema"""
    print("\n" + "=" * 80)
    print("📚 GUÍA DE USO DEL SISTEMA")
    print("=" * 80)
    
    print("\n🔐 ACCESO AL SISTEMA:")
    print("   • URL Admin: http://localhost:8000/admin/")
    print("   • Usuario: admin")
    print("   • Contraseña: admin123")
    
    print("\n🎯 FUNCIONALIDADES PRINCIPALES:")
    print("   1. 📊 ANALYTICS Y REPORTES:")
    print("      - Dashboards personalizados por rol")
    print("      - KPIs en tiempo real")
    print("      - Reportes automáticos programados")
    print("      - Alertas automáticas configurables")
    
    print("\n   2. 📧 COMUNICACIONES:")
    print("      - Plantillas de email personalizables")
    print("      - Envío masivo de emails")
    print("      - SMS automáticos (saldo bajo, confirmaciones)")
    print("      - Campañas de marketing")
    
    print("\n   3. 🔌 INTEGRACIONES:")
    print("      - API de facturación electrónica (SET)")
    print("      - Procesamiento de pagos (Tigo Money)")
    print("      - Envío de SMS (Personal)")
    print("      - Email SMTP (Gmail)")
    print("      - Webhooks para eventos en tiempo real")
    
    print("\n   4. ⚙️ CONFIGURACIONES:")
    print("      - Configuraciones del sistema centralizadas")
    print("      - Perfiles de usuario personalizables")
    print("      - Tareas automatizadas programables")
    print("      - Cache inteligente para optimización")
    
    print("\n🚀 PRÓXIMOS PASOS:")
    print("   1. Personalizar dashboards según necesidades")
    print("   2. Configurar credenciales de APIs reales")
    print("   3. Programar reportes automáticos")
    print("   4. Configurar alertas para eventos críticos")
    print("   5. Personalizar plantillas de comunicación")

def main():
    """Función principal"""
    crear_dashboards()
    mostrar_estado_sistema()
    mostrar_guia_uso()
    
    print("\n" + "=" * 80)
    print("✅ SISTEMA COMPLETAMENTE CONFIGURADO Y LISTO PARA USAR")
    print("=" * 80)

if __name__ == "__main__":
    main()