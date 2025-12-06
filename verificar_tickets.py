"""
Script de verificación rápida del sistema de tickets de almuerzo
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from gestion.models import RegistroConsumoAlmuerzo
from django.utils import timezone

print("="*80)
print("VERIFICACIÓN: Sistema de Tickets de Almuerzo")
print("="*80)

# Verificar último registro
ultimo_registro = RegistroConsumoAlmuerzo.objects.order_by('-id_registro_consumo').first()

if ultimo_registro:
    print(f"\n✅ Último registro encontrado:")
    print(f"   ID: {ultimo_registro.id_registro_consumo}")
    print(f"   Estudiante: {ultimo_registro.id_hijo.nombre_completo}")
    print(f"   Tarjeta: {ultimo_registro.nro_tarjeta.nro_tarjeta}")
    print(f"   Fecha: {ultimo_registro.fecha_consumo}")
    print(f"   Hora: {ultimo_registro.hora_registro}")
    print(f"   Tipo: {ultimo_registro.id_tipo_almuerzo.nombre}")
    print(f"   Costo: Gs. {ultimo_registro.costo_almuerzo:,.0f}")
    
    print(f"\n🎫 URL del Ticket:")
    print(f"   http://localhost:8000/pos/almuerzo/ticket/{ultimo_registro.id_registro_consumo}/")
    
    print(f"\n📋 Para probar:")
    print(f"   1. Abre el navegador en: http://localhost:8000/pos/almuerzo/")
    print(f"   2. Pasa una tarjeta (ej: 01024)")
    print(f"   3. El ticket se abrirá automáticamente")
    print(f"   4. Se imprimirá automáticamente")
else:
    print("\n⚠️  No hay registros aún")
    print("   Registra un almuerzo primero en: http://localhost:8000/pos/almuerzo/")

print("\n" + "="*80)
print("✅ SISTEMA LISTO")
print("="*80)
