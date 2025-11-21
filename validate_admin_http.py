#!/usr/bin/env python
"""
Script para validar todas las URLs del admin haciendo peticiones HTTP reales
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

print("\n" + "="*80)
print("VALIDACIÓN DE URLs DEL ADMIN - TEST HTTP".center(80))
print("="*80 + "\n")

# Crear cliente de prueba
client = Client()

# Obtener o crear superusuario para las pruebas
try:
    user = User.objects.filter(is_superuser=True).first()
    if not user:
        print("⚠️  No hay superusuario. Creando usuario de prueba temporal...")
        user = User.objects.create_superuser('test_admin', 'test@test.com', 'test123')
        print("✅ Usuario temporal creado\n")
    
    # Login
    client.force_login(user)
    print(f"✅ Login exitoso como: {user.username}\n")
    print("-"*80 + "\n")
    
except Exception as e:
    print(f"❌ Error en login: {e}")
    exit(1)

# Lista de URLs del admin a probar
URLS_ADMIN = [
    ('Inicio Admin', '/admin/'),
    ('Tipos Cliente', '/admin/gestion/tipocliente/'),
    ('Listas Precios', '/admin/gestion/listaprecios/'),
    ('Categorías', '/admin/gestion/categoria/'),
    ('Unidades Medida', '/admin/gestion/unidadmedida/'),
    ('Impuestos', '/admin/gestion/impuesto/'),
    ('Tipos Rol', '/admin/gestion/tiporolgeneral/'),
    ('Clientes', '/admin/gestion/cliente/'),
    ('Hijos', '/admin/gestion/hijo/'),
    ('Tarjetas', '/admin/gestion/tarjeta/'),
    ('Productos', '/admin/gestion/producto/'),
    ('Stock Único', '/admin/gestion/stockunico/'),
    ('Proveedores', '/admin/gestion/proveedor/'),
    ('Empleados', '/admin/gestion/empleado/'),
    ('Datos Empresa', '/admin/gestion/datosempresa/'),
    ('Precios por Lista', '/admin/gestion/preciosporlista/'),
    ('Costos Históricos', '/admin/gestion/costoshistoricos/'),
    ('Histórico Precios', '/admin/gestion/historicoprecios/'),
    ('Compras', '/admin/gestion/compras/'),
    ('Detalle Compra', '/admin/gestion/detallecompra/'),
    ('Cta Corriente Prov', '/admin/gestion/ctacorrienteprov/'),
    ('Cargas Saldo', '/admin/gestion/cargassaldo/'),
    ('Usuarios Web', '/admin/gestion/usuarioswebclientes/'),
    ('Puntos Expedición', '/admin/gestion/puntosexpedicion/'),
    ('Timbrados', '/admin/gestion/timbrados/'),
    ('Documentos Tributarios', '/admin/gestion/documentostributarios/'),
    ('Facturación Electrónica', '/admin/gestion/datosfacturacionelect/'),
    ('Facturación Física', '/admin/gestion/datosfacturacionfisica/'),
    ('Movimientos Stock', '/admin/gestion/movimientosstock/'),
    ('Ajustes Inventario', '/admin/gestion/ajustesinventario/'),
    ('Detalle Ajuste', '/admin/gestion/detalleajuste/'),
    ('Cajas', '/admin/gestion/cajas/'),
    ('Cierres Caja', '/admin/gestion/cierrescaja/'),
    ('Medios Pago', '/admin/gestion/mediospago/'),
    ('Tipos Pago', '/admin/gestion/tipospago/'),
    ('Ventas', '/admin/gestion/ventas/'),
    ('Detalle Venta', '/admin/gestion/detalleventa/'),
    ('Pagos Venta', '/admin/gestion/pagosventa/'),
    ('Cuenta Corriente', '/admin/gestion/ctacorriente/'),
    ('Notas Crédito', '/admin/gestion/notascredito/'),
    ('Detalle Nota', '/admin/gestion/detallenota/'),
    ('Conciliación Pagos', '/admin/gestion/conciliacionpagos/'),
    ('Planes Almuerzo', '/admin/gestion/planesalmuerzo/'),
    ('Suscripciones', '/admin/gestion/suscripcionesalmuerzo/'),
    ('Pagos Almuerzo', '/admin/gestion/pagosalmuerzomensual/'),
    ('Registro Consumo', '/admin/gestion/registroconsumoalmuerzo/'),
    ('Tarifas Comisión', '/admin/gestion/tarifascomision/'),
    ('Detalle Comisión', '/admin/gestion/detallecomisionventa/'),
    ('Alertas Sistema', '/admin/gestion/alertassistema/'),
    ('Solicitudes Notif', '/admin/gestion/solicitudesnotificacion/'),
    ('Auditoría Empleados', '/admin/gestion/auditoriaempleados/'),
    ('Auditoría Usuarios', '/admin/gestion/auditoriausuariosweb/'),
    ('Auditoría Comisiones', '/admin/gestion/auditoriacomisiones/'),
    ('Vista Stock Alerta', '/admin/gestion/vistastockalerta/'),
    ('Vista Saldo Clientes', '/admin/gestion/vistasaldoclientes/'),
]

exitosas = []
fallidas = []

for nombre, url in URLS_ADMIN:
    try:
        response = client.get(url)
        
        if response.status_code == 200:
            print(f"✅ {nombre:<30} {url:<50} [200 OK]")
            exitosas.append((nombre, url))
        elif response.status_code == 302:
            print(f"⚠️  {nombre:<30} {url:<50} [302 Redirect]")
            exitosas.append((nombre, url))
        else:
            print(f"❌ {nombre:<30} {url:<50} [{response.status_code}]")
            fallidas.append((nombre, url, response.status_code))
            
    except Exception as e:
        error_msg = str(e)[:60]
        print(f"❌ {nombre:<30} {url:<50} ERROR: {error_msg}")
        fallidas.append((nombre, url, error_msg))

print("\n" + "="*80)
print(f"RESUMEN: {len(exitosas)} Exitosas | {len(fallidas)} Fallidas")
print("="*80 + "\n")

if fallidas:
    print("URLs CON PROBLEMAS:\n")
    for nombre, url, error in fallidas:
        print(f"  • {nombre}: {url}")
        print(f"    Error: {error}\n")
else:
    print("🎉 ¡TODAS LAS URLs DEL ADMIN FUNCIONAN CORRECTAMENTE!")

print("="*80 + "\n")

# Limpiar usuario de prueba si fue creado
if user.username == 'test_admin':
    user.delete()
    print("🧹 Usuario temporal eliminado\n")
