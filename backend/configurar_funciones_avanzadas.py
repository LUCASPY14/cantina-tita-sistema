#!/usr/bin/env python
"""
Script para cargar configuraciones avanzadas y datos iniciales para los nuevos modelos
"""
import os
import sys
import django
from dotenv import load_dotenv
from datetime import datetime, date

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
    KpiMetrica, ReporteTemplate,
    
    # Comunicaciones
    EmailTemplate, SmsTemplate,
    
    # Integraciones
    ProveedorApi, EndpointApi,
    
    # Empleados
    Empleado, TipoRolGeneral
)

def crear_configuraciones_sistema():
    """Crear configuraciones base del sistema"""
    print("\n⚙️  CONFIGURACIONES DEL SISTEMA")
    print("-" * 50)
    
    configuraciones = [
        # General
        {
            'clave': 'NOMBRE_SISTEMA',
            'valor': 'Cantina TITA - Sistema de Gestión',
            'tipo_dato': 'STRING',
            'categoria': 'GENERAL',
            'descripcion': 'Nombre del sistema mostrado en la interfaz',
            'valor_por_defecto': 'Cantina TITA',
            'es_requerido': True
        },
        {
            'clave': 'VERSION_SISTEMA',
            'valor': '1.0.0', 
            'tipo_dato': 'STRING',
            'categoria': 'GENERAL',
            'descripcion': 'Versión actual del sistema',
            'valor_por_defecto': '1.0.0',
            'es_requerido': True
        },
        {
            'clave': 'MONEDA_BASE',
            'valor': 'PYG',
            'tipo_dato': 'STRING',
            'categoria': 'GENERAL',
            'descripcion': 'Moneda base del sistema',
            'valor_por_defecto': 'PYG',
            'valores_permitidos': ['PYG', 'USD', 'EUR'],
            'es_requerido': True
        },
        
        # Notificaciones
        {
            'clave': 'EMAIL_SMTP_HOST',
            'valor': 'smtp.gmail.com',
            'tipo_dato': 'STRING',
            'categoria': 'NOTIFICACIONES',
            'descripcion': 'Servidor SMTP para envío de emails',
            'valor_por_defecto': 'smtp.gmail.com',
            'es_requerido': True
        },
        {
            'clave': 'EMAIL_SMTP_PORT',
            'valor': '587',
            'tipo_dato': 'INTEGER',
            'categoria': 'NOTIFICACIONES',
            'descripcion': 'Puerto SMTP',
            'valor_por_defecto': '587',
            'es_requerido': True
        },
        {
            'clave': 'NOTIFICACIONES_HABILITADAS',
            'valor': 'true',
            'tipo_dato': 'BOOLEAN',
            'categoria': 'NOTIFICACIONES',
            'descripcion': 'Activar/desactivar sistema de notificaciones',
            'valor_por_defecto': 'true',
            'es_requerido': True
        },
        
        # Seguridad
        {
            'clave': 'INTENTOS_LOGIN_MAX',
            'valor': '5',
            'tipo_dato': 'INTEGER',
            'categoria': 'SEGURIDAD',
            'descripcion': 'Máximo intentos de login antes de bloquear',
            'valor_por_defecto': '5',
            'valor_minimo': '3',
            'valor_maximo': '10',
            'es_requerido': True
        },
        {
            'clave': 'SESION_TIMEOUT_MINUTOS',
            'valor': '60',
            'tipo_dato': 'INTEGER',
            'categoria': 'SEGURIDAD',
            'descripcion': 'Tiempo de sesión en minutos',
            'valor_por_defecto': '60',
            'valor_minimo': '15',
            'valor_maximo': '480',
            'es_requerido': True
        },
        
        # Facturación
        {
            'clave': 'IVA_PORCENTAJE_DEFECTO',
            'valor': '10.0',
            'tipo_dato': 'DECIMAL',
            'categoria': 'FACTURACION',
            'descripcion': 'Porcentaje de IVA por defecto',
            'valor_por_defecto': '10.0',
            'es_requerido': True
        },
        
        # Reportes
        {
            'clave': 'REPORTES_AUTO_DIARIOS',
            'valor': 'true',
            'tipo_dato': 'BOOLEAN',
            'categoria': 'REPORTES',
            'descripcion': 'Generar reportes automáticos diarios',
            'valor_por_defecto': 'false',
            'es_requerido': False
        }
    ]
    
    creados = 0
    for config in configuraciones:
        obj, created = ConfiguracionSistema.objects.get_or_create(
            clave=config['clave'],
            defaults=config
        )
        if created:
            print(f"   ✅ {config['clave']}: {config['valor']}")
            creados += 1
        else:
            print(f"   ⚪ {config['clave']}: Ya existe")
    
    print(f"\n📊 Configuraciones creadas: {creados}")
    return creados > 0

def crear_kpis_base():
    """Crear KPIs básicos del negocio"""
    print("\n📈 KPIs Y MÉTRICAS")
    print("-" * 50)
    
    kpis = [
        {
            'nombre': 'Ventas Diarias',
            'descripcion': 'Total de ventas por día en guaraníes',
            'formula': 'SELECT SUM(total) FROM pos_venta WHERE DATE(fecha) = CURDATE()',
            'unidad_medida': 'Gs.',
            'categoria': 'VENTAS',
            'frecuencia_calculo': 'DIARIO',
            'valor_objetivo': 500000  # 500k Gs. diarios
        },
        {
            'nombre': 'Número de Transacciones',
            'descripcion': 'Cantidad de ventas realizadas por día',
            'formula': 'SELECT COUNT(*) FROM pos_venta WHERE DATE(fecha) = CURDATE()',
            'unidad_medida': 'unidades',
            'categoria': 'VENTAS', 
            'frecuencia_calculo': 'DIARIO',
            'valor_objetivo': 50  # 50 transacciones diarias
        },
        {
            'nombre': 'Ticket Promedio',
            'descripcion': 'Valor promedio por transacción',
            'formula': 'SELECT AVG(total) FROM pos_venta WHERE DATE(fecha) = CURDATE()',
            'unidad_medida': 'Gs.',
            'categoria': 'VENTAS',
            'frecuencia_calculo': 'DIARIO',
            'valor_objetivo': 10000  # 10k Gs. promedio
        },
        {
            'nombre': 'Productos con Stock Bajo',
            'descripcion': 'Cantidad de productos con stock crítico',
            'formula': 'SELECT COUNT(*) FROM productos p JOIN stock_unico s ON p.id_producto = s.id_producto WHERE s.cantidad_actual <= s.stock_minimo',
            'unidad_medida': 'productos',
            'categoria': 'OPERACIONES',
            'frecuencia_calculo': 'TIEMPO_REAL',
            'valor_objetivo': 0  # Idealmente 0 productos sin stock
        },
        {
            'nombre': 'Clientes Activos',
            'descripcion': 'Cantidad de clientes que compraron en los últimos 30 días',
            'formula': 'SELECT COUNT(DISTINCT id_cliente) FROM pos_venta WHERE fecha >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)',
            'unidad_medida': 'clientes',
            'categoria': 'CLIENTES',
            'frecuencia_calculo': 'SEMANAL',
            'valor_objetivo': 100  # 100 clientes activos
        },
        {
            'nombre': 'Margen de Rentabilidad',
            'descripcion': 'Porcentaje de ganancia sobre las ventas',
            'formula': 'SELECT (SUM(v.total) - SUM(p.costo_promedio * dv.cantidad)) / SUM(v.total) * 100 FROM pos_venta v JOIN pos_detalleventa dv ON v.id_venta = dv.id_venta JOIN productos p ON dv.id_producto = p.id_producto WHERE DATE(v.fecha) = CURDATE()',
            'unidad_medida': '%',
            'categoria': 'RENTABILIDAD',
            'frecuencia_calculo': 'DIARIO',
            'valor_objetivo': 30  # 30% de margen
        }
    ]
    
    creados = 0
    for kpi_data in kpis:
        kpi, created = KpiMetrica.objects.get_or_create(
            nombre=kpi_data['nombre'],
            defaults=kpi_data
        )
        if created:
            print(f"   ✅ KPI: {kpi_data['nombre']}")
            creados += 1
        else:
            print(f"   ⚪ KPI: {kpi_data['nombre']} - Ya existe")
    
    print(f"\n📊 KPIs creados: {creados}")
    return creados > 0

def crear_plantillas_email():
    """Crear plantillas de email base"""
    print("\n📧 PLANTILLAS DE EMAIL")
    print("-" * 50)
    
    plantillas = [
        {
            'codigo': 'BIENVENIDA_CLIENTE',
            'nombre': 'Bienvenida a nuevo cliente',
            'categoria': 'BIENVENIDA',
            'asunto': 'Bienvenido a Cantina TITA - {{cliente.nombre}}',
            'cuerpo_html': '''
<html>
<body>
    <h2>¡Bienvenido a Cantina TITA!</h2>
    <p>Estimado/a {{cliente.nombre}},</p>
    <p>Nos complace darte la bienvenida a nuestro sistema de cantina.</p>
    <p><strong>Datos de tu cuenta:</strong></p>
    <ul>
        <li>Número de cliente: {{cliente.id}}</li>
        <li>Email: {{cliente.email}}</li>
        <li>Fecha de registro: {{fecha_registro}}</li>
    </ul>
    <p>Ya puedes comenzar a usar nuestros servicios.</p>
    <p>Saludos cordiales,<br>Equipo Cantina TITA</p>
</body>
</html>
            ''',
            'cuerpo_texto': '''
¡Bienvenido a Cantina TITA!

Estimado/a {{cliente.nombre}},

Nos complace darte la bienvenida a nuestro sistema de cantina.

Datos de tu cuenta:
- Número de cliente: {{cliente.id}}
- Email: {{cliente.email}}
- Fecha de registro: {{fecha_registro}}

Ya puedes comenzar a usar nuestros servicios.

Saludos cordiales,
Equipo Cantina TITA
            ''',
            'variables_disponibles': ['cliente.nombre', 'cliente.id', 'cliente.email', 'fecha_registro']
        },
        {
            'codigo': 'NOTIF_SALDO_BAJO',
            'nombre': 'Notificación de saldo bajo',
            'categoria': 'NOTIFICACION',
            'asunto': 'Saldo bajo en tu cuenta - Cantina TITA',
            'cuerpo_html': '''
<html>
<body>
    <h2>Saldo Bajo en tu Cuenta</h2>
    <p>Estimado/a {{cliente.nombre}},</p>
    <p>Te informamos que el saldo en tu cuenta está bajo:</p>
    <p><strong>Saldo actual: {{saldo_actual}} Gs.</strong></p>
    <p>Te recomendamos realizar una recarga para continuar usando nuestros servicios.</p>
    <p>Puedes recargar tu saldo:</p>
    <ul>
        <li>En la cantina</li>
        <li>A través del portal web</li>
        <li>Con transferencia bancaria</li>
    </ul>
    <p>Saludos cordiales,<br>Equipo Cantina TITA</p>
</body>
</html>
            ''',
            'variables_disponibles': ['cliente.nombre', 'saldo_actual']
        },
        {
            'codigo': 'REPORTE_DIARIO',
            'nombre': 'Reporte diario de ventas',
            'categoria': 'SISTEMA',
            'asunto': 'Reporte Diario - {{fecha}}',
            'cuerpo_html': '''
<html>
<body>
    <h2>Reporte Diario de Ventas</h2>
    <p>Fecha: {{fecha}}</p>
    <h3>Resumen</h3>
    <ul>
        <li>Total ventas: {{total_ventas}} Gs.</li>
        <li>Número de transacciones: {{num_transacciones}}</li>
        <li>Ticket promedio: {{ticket_promedio}} Gs.</li>
        <li>Producto más vendido: {{producto_top}}</li>
    </ul>
    <p>Generado automáticamente por el sistema.</p>
</body>
</html>
            ''',
            'variables_disponibles': ['fecha', 'total_ventas', 'num_transacciones', 'ticket_promedio', 'producto_top']
        }
    ]
    
    creados = 0
    for template_data in plantillas:
        template, created = EmailTemplate.objects.get_or_create(
            codigo=template_data['codigo'],
            defaults=template_data
        )
        if created:
            print(f"   ✅ Template: {template_data['nombre']}")
            creados += 1
        else:
            print(f"   ⚪ Template: {template_data['nombre']} - Ya existe")
    
    print(f"\n📊 Plantillas creadas: {creados}")
    return creados > 0

def crear_plantillas_sms():
    """Crear plantillas de SMS"""
    print("\n📱 PLANTILLAS DE SMS")
    print("-" * 50)
    
    plantillas = [
        {
            'codigo': 'SALDO_BAJO_SMS',
            'nombre': 'SMS Saldo Bajo',
            'categoria': 'ALERTA',
            'mensaje': 'Cantina TITA: Tu saldo es {{saldo}} Gs. Recarga pronto. Info: cantinatita.com',
            'variables_disponibles': ['saldo']
        },
        {
            'codigo': 'CONFIRMACION_RECARGA',
            'nombre': 'Confirmación de recarga',
            'categoria': 'CONFIRMACION',
            'mensaje': 'Cantina TITA: Recarga exitosa! Gs. {{monto}}. Saldo: {{saldo_nuevo}} Gs.',
            'variables_disponibles': ['monto', 'saldo_nuevo']
        },
        {
            'codigo': 'PROMOCION_ESPECIAL',
            'nombre': 'Promoción especial',
            'categoria': 'PROMOCION',
            'mensaje': 'Cantina TITA: {{descripcion_promocion}} ¡Válido hasta {{fecha_limite}}!',
            'variables_disponibles': ['descripcion_promocion', 'fecha_limite']
        }
    ]
    
    creados = 0
    for template_data in plantillas:
        template, created = SmsTemplate.objects.get_or_create(
            codigo=template_data['codigo'],
            defaults=template_data
        )
        if created:
            print(f"   ✅ SMS: {template_data['nombre']}")
            creados += 1
        else:
            print(f"   ⚪ SMS: {template_data['nombre']} - Ya existe")
    
    print(f"\n📊 SMS Templates creados: {creados}")
    return creados > 0

def crear_integraciones_base():
    """Crear integraciones base con proveedores"""
    print("\n🔌 INTEGRACIONES CON APIs")
    print("-" * 50)
    
    proveedores = [
        {
            'nombre': 'SET - Facturación Electrónica',
            'descripcion': 'Sistema de facturación electrónica de Paraguay',
            'tipo_servicio': 'FACTURACION',
            'url_base': 'https://sifen.set.gov.py/de/ws/sync/',
            'version_api': 'v1',
            'documentacion_url': 'https://www.set.gov.py/factura-electronica',
            'tipo_autenticacion': 'CUSTOM',
            'config_autenticacion': {
                'method': 'digital_signature',
                'certificate_required': True
            }
        },
        {
            'nombre': 'Tigo Money',
            'descripcion': 'Procesador de pagos móviles',
            'tipo_servicio': 'PAGOS',
            'url_base': 'https://test.tigomoney.com.py/v2/',
            'version_api': 'v2',
            'tipo_autenticacion': 'API_KEY',
            'config_autenticacion': {
                'header_name': 'Authorization',
                'prefix': 'Bearer'
            }
        },
        {
            'nombre': 'Personal SMS',
            'descripcion': 'Servicio de envío de SMS',
            'tipo_servicio': 'SMS',
            'url_base': 'https://api.personal.com.py/sms/',
            'version_api': 'v1',
            'tipo_autenticacion': 'BASIC',
            'config_autenticacion': {
                'requires_username': True,
                'requires_password': True
            }
        },
        {
            'nombre': 'Gmail SMTP',
            'descripcion': 'Servicio de email de Google',
            'tipo_servicio': 'EMAIL',
            'url_base': 'https://gmail.googleapis.com/',
            'version_api': 'v1',
            'tipo_autenticacion': 'OAUTH',
            'config_autenticacion': {
                'scope': 'https://www.googleapis.com/auth/gmail.send',
                'client_id_required': True
            }
        }
    ]
    
    creados = 0
    for proveedor_data in proveedores:
        proveedor, created = ProveedorApi.objects.get_or_create(
            nombre=proveedor_data['nombre'],
            defaults=proveedor_data
        )
        if created:
            print(f"   ✅ API: {proveedor_data['nombre']}")
            creados += 1
            
            # Crear endpoints básicos para cada proveedor
            if proveedor.tipo_servicio == 'PAGOS':
                EndpointApi.objects.create(
                    proveedor=proveedor,
                    nombre='Procesar Pago',
                    descripcion='Procesar pago con tarjeta/billetera',
                    path='/payment/process',
                    metodo_http='POST'
                )
                EndpointApi.objects.create(
                    proveedor=proveedor,
                    nombre='Consultar Estado',
                    descripcion='Consultar estado de pago',
                    path='/payment/status/{id}',
                    metodo_http='GET'
                )
        else:
            print(f"   ⚪ API: {proveedor_data['nombre']} - Ya existe")
    
    print(f"\n📊 Integraciones creadas: {creados}")
    return creados > 0

def crear_reportes_base():
    """Crear plantillas de reportes base"""
    print("\n📊 PLANTILLAS DE REPORTES")
    print("-" * 50)
    
    reportes = [
        {
            'nombre': 'Ventas del Día',
            'descripcion': 'Reporte detallado de ventas diarias',
            'tipo_reporte': 'VENTAS',
            'frecuencia_auto': 'DIARIO',
            'query_sql': '''
                SELECT 
                    v.fecha,
                    COUNT(*) as total_transacciones,
                    SUM(v.total) as total_ventas,
                    AVG(v.total) as ticket_promedio
                FROM pos_venta v
                WHERE DATE(v.fecha) = %s
                GROUP BY DATE(v.fecha)
            ''',
            'parametros_json': ['fecha']
        },
        {
            'nombre': 'Top 10 Productos',
            'descripcion': 'Los 10 productos más vendidos',
            'tipo_reporte': 'PRODUCTOS',
            'frecuencia_auto': 'SEMANAL',
            'query_sql': '''
                SELECT 
                    p.nombre,
                    SUM(dv.cantidad) as cantidad_vendida,
                    SUM(dv.precio * dv.cantidad) as total_ventas
                FROM productos p
                JOIN pos_detalleventa dv ON p.id_producto = dv.id_producto
                JOIN pos_venta v ON dv.id_venta = v.id_venta
                WHERE v.fecha >= %s AND v.fecha <= %s
                GROUP BY p.id_producto, p.nombre
                ORDER BY cantidad_vendida DESC
                LIMIT 10
            ''',
            'parametros_json': ['fecha_desde', 'fecha_hasta']
        },
        {
            'nombre': 'Clientes más Activos',
            'descripcion': 'Clientes con más transacciones en el período',
            'tipo_reporte': 'CLIENTES',
            'frecuencia_auto': 'MENSUAL',
            'query_sql': '''
                SELECT 
                    c.nombre,
                    c.apellido,
                    COUNT(v.id_venta) as total_compras,
                    SUM(v.total) as total_gastado
                FROM clientes c
                JOIN pos_venta v ON c.id_cliente = v.id_cliente
                WHERE v.fecha >= %s AND v.fecha <= %s
                GROUP BY c.id_cliente
                ORDER BY total_compras DESC
                LIMIT 20
            ''',
            'parametros_json': ['fecha_desde', 'fecha_hasta']
        }
    ]
    
    creados = 0
    for reporte_data in reportes:
        reporte, created = ReporteTemplate.objects.get_or_create(
            nombre=reporte_data['nombre'],
            defaults=reporte_data
        )
        if created:
            print(f"   ✅ Reporte: {reporte_data['nombre']}")
            creados += 1
        else:
            print(f"   ⚪ Reporte: {reporte_data['nombre']} - Ya existe")
    
    print(f"\n📊 Reportes creados: {creados}")
    return creados > 0

def mostrar_resumen():
    """Mostrar resumen de todo lo configurado"""
    print("\n" + "=" * 70)
    print("📊 RESUMEN DE CONFIGURACIONES AVANZADAS")
    print("=" * 70)
    
    from gestion.models import (
        ConfiguracionSistema, KpiMetrica, EmailTemplate, 
        SmsTemplate, ProveedorApi, ReporteTemplate
    )
    
    print(f"⚙️  Configuraciones del sistema: {ConfiguracionSistema.objects.count()}")
    print(f"📈 KPIs configurados: {KpiMetrica.objects.count()}")
    print(f"📧 Plantillas de email: {EmailTemplate.objects.count()}")
    print(f"📱 Plantillas de SMS: {SmsTemplate.objects.count()}")
    print(f"🔌 Integraciones API: {ProveedorApi.objects.count()}")
    print(f"📊 Plantillas de reportes: {ReporteTemplate.objects.count()}")
    
    print(f"\n🎯 PRÓXIMOS PASOS:")
    print("   1. Configurar credenciales de APIs en ambiente de producción")
    print("   2. Configurar servidor SMTP para emails")
    print("   3. Personalizar dashboards por rol de usuario")
    print("   4. Configurar alertas automáticas")
    print("   5. Programar tareas de generación de reportes")

def main():
    """Función principal"""
    print("🚀 CONFIGURACIÓN DE FUNCIONALIDADES AVANZADAS")
    print("=" * 70)
    
    # Cargar configuraciones base
    crear_configuraciones_sistema()
    crear_kpis_base()
    crear_plantillas_email()
    crear_plantillas_sms()
    crear_integraciones_base()
    crear_reportes_base()
    
    # Mostrar resumen
    mostrar_resumen()
    
    print("\n✅ CONFIGURACIONES AVANZADAS COMPLETADAS")
    print("=" * 70)

if __name__ == "__main__":
    main()