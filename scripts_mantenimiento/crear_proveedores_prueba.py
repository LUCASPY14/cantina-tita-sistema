"""
Script para crear proveedores de prueba
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from gestion.models import Proveedor

def crear_proveedores_prueba():
    print("=" * 60)
    print("CREANDO PROVEEDORES DE PRUEBA")
    print("=" * 60)
    
    proveedores_data = [
        {
            'ruc': '80012345-7',
            'razon_social': 'Distribuidora La Esperanza S.R.L.',
            'telefono': '021-555-1234',
            'email': 'ventas@laesperanza.com.py',
            'direccion': 'Av. Eusebio Ayala Km 4.5',
            'ciudad': 'Asunción'
        },
        {
            'ruc': '80023456-8',
            'razon_social': 'Alimentos del Paraguay S.A.',
            'telefono': '021-555-2345',
            'email': 'contacto@alimentospy.com',
            'direccion': 'Ruta 2 Km 25',
            'ciudad': 'San Lorenzo'
        },
        {
            'ruc': '80034567-9',
            'razon_social': 'Bebidas y Refrescos del Este',
            'telefono': '0983-345678',
            'email': 'ventas@bebidaseste.com',
            'direccion': 'Av. Mariscal López 1234',
            'ciudad': 'Asunción'
        },
        {
            'ruc': '80045678-0',
            'razon_social': 'Panadería y Confitería San José',
            'telefono': '0984-456789',
            'email': 'pedidos@sanjose.com.py',
            'direccion': 'Calle Palma 567',
            'ciudad': 'Asunción'
        },
        {
            'ruc': '80056789-1',
            'razon_social': 'Lácteos del Valle S.A.',
            'telefono': '021-555-5678',
            'email': 'info@lacteosdelvalle.com',
            'direccion': 'Ruta 1 Km 35',
            'ciudad': 'Itá'
        },
        {
            'ruc': '80067890-2',
            'razon_social': 'Carnes y Embutidos Premium',
            'telefono': '0985-678901',
            'email': 'ventas@carnespremium.com',
            'direccion': 'Av. España 890',
            'ciudad': 'Luque'
        },
        {
            'ruc': '80078901-3',
            'razon_social': 'Verduras Frescas del Campo',
            'telefono': '0986-789012',
            'email': 'pedidos@verdurasdelcampo.com',
            'direccion': 'Mercado Central Local 45',
            'ciudad': 'Asunción'
        },
        {
            'ruc': '80089012-4',
            'razon_social': 'Limpieza e Higiene Total S.R.L.',
            'telefono': '021-555-9012',
            'email': 'ventas@limpiezatotal.com',
            'direccion': 'Av. Madame Lynch 1567',
            'ciudad': 'Asunción'
        }
    ]
    
    creados = 0
    existentes = 0
    
    for data in proveedores_data:
        proveedor, created = Proveedor.objects.get_or_create(
            ruc=data['ruc'],
            defaults={
                'razon_social': data['razon_social'],
                'telefono': data['telefono'],
                'email': data['email'],
                'direccion': data['direccion'],
                'ciudad': data['ciudad'],
                'activo': True
            }
        )
        
        if created:
            print(f"✓ Proveedor creado: {proveedor.razon_social}")
            print(f"  RUC: {proveedor.ruc}")
            print(f"  Ciudad: {proveedor.ciudad}")
            print(f"  Teléfono: {proveedor.telefono}")
            print()
            creados += 1
        else:
            print(f"⚠ Proveedor ya existe: {proveedor.razon_social}")
            existentes += 1
    
    print("=" * 60)
    print(f"✅ Proceso completado")
    print(f"   - Proveedores creados: {creados}")
    print(f"   - Proveedores existentes: {existentes}")
    print(f"   - Total en base de datos: {Proveedor.objects.count()}")
    print()
    print("URLs para probar:")
    print("http://127.0.0.1:8000/pos/proveedores/")
    print("=" * 60)

if __name__ == '__main__':
    crear_proveedores_prueba()
