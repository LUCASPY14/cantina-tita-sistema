"""
Script para inicializar datos del sistema de Cajas, Compras y Comisiones
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from gestion.models import Cajas, MediosPago, TiposPago
from decimal import Decimal

def crear_medios_pago():
    """Crear medios de pago necesarios"""
    print("\n=== Creando Medios de Pago ===")
    
    medios = [
        {'descripcion': 'Efectivo', 'genera_comision': False, 'requiere_validacion': False, 'activo': True},
        {'descripcion': 'Tarjeta de Crédito', 'genera_comision': True, 'requiere_validacion': True, 'activo': True},
        {'descripcion': 'Tarjeta de Débito', 'genera_comision': True, 'requiere_validacion': True, 'activo': True},
        {'descripcion': 'Giros Tigo', 'genera_comision': True, 'requiere_validacion': True, 'activo': True},
        {'descripcion': 'Transferencia Bancaria', 'genera_comision': False, 'requiere_validacion': False, 'activo': True},
    ]
    
    for medio_data in medios:
        medio, created = MediosPago.objects.get_or_create(
            descripcion=medio_data['descripcion'],
            defaults=medio_data
        )
        if created:
            print(f"✓ Creado: {medio.descripcion}")
        else:
            print(f"○ Ya existe: {medio.descripcion}")

def crear_tipos_pago():
    """Crear tipos de pago"""
    print("\n=== Creando Tipos de Pago ===")
    
    tipos = [
        {'descripcion': 'Contado', 'activo': True},
        {'descripcion': 'Crédito', 'activo': True},
        {'descripcion': 'Tarjeta', 'activo': True},
    ]
    
    for tipo_data in tipos:
        tipo, created = TiposPago.objects.get_or_create(
            descripcion=tipo_data['descripcion'],
            defaults=tipo_data
        )
        if created:
            print(f"✓ Creado: {tipo.descripcion}")
        else:
            print(f"○ Ya existe: {tipo.descripcion}")

def crear_caja_inicial():
    """Crear caja inicial"""
    print("\n=== Creando Caja Inicial ===")
    
    caja, created = Cajas.objects.get_or_create(
        nombre_caja='Caja Principal',
        defaults={
            'ubicacion': 'Cantina',
            'activo': True
        }
    )
    
    if created:
        print(f"✓ Creada: {caja.nombre_caja}")
    else:
        print(f"○ Ya existe: {caja.nombre_caja}")

def main():
    print("\n" + "="*60)
    print("INICIALIZACIÓN DE DATOS - SISTEMA CANTINA TITA")
    print("="*60)
    
    try:
        crear_medios_pago()
        crear_tipos_pago()
        crear_caja_inicial()
        
        print("\n" + "="*60)
        print("✓ INICIALIZACIÓN COMPLETADA EXITOSAMENTE")
        print("="*60)
        
        print("\n📋 Resumen:")
        print(f"   - Medios de Pago: {MediosPago.objects.count()}")
        print(f"   - Tipos de Pago: {TiposPago.objects.count()}")
        print(f"   - Cajas: {Cajas.objects.count()}")
        
        print("\n🎯 Próximos pasos:")
        print("   1. Configurar tarifas de comisión en: /pos/comisiones/configurar/")
        print("   2. Abrir caja para empezar a operar: /pos/cajas/apertura/")
        print("   3. Registrar primera compra: /pos/compras/nueva/")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
