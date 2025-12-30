from django.db import transaction
from django.utils import timezone
from gestion.models import Tarjeta, CargasSaldo, Hijo

nro_tarjeta = '01024'
monto = 50000
forma_pago = 'efectivo'
observaciones = 'Prueba backend'

print("="*70)
print(f"Simulando recarga de {monto} Gs. a tarjeta {nro_tarjeta}")
print("="*70)

try:
    tarjeta = Tarjeta.objects.get(nro_tarjeta=nro_tarjeta)
    saldo_anterior = tarjeta.saldo_actual
    hijo = tarjeta.id_hijo
    with transaction.atomic():
        recarga = CargasSaldo.objects.create(
            nro_tarjeta=tarjeta,
            fecha_carga=timezone.now(),
            monto_cargado=monto,
            referencia='Prueba backend'
        )
        tarjeta.saldo_actual += monto
        tarjeta.save()
    print(f"✅ Recarga registrada. Nuevo saldo: {tarjeta.saldo_actual}")
    print(f"ID recarga: {recarga.id_carga_saldo}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\nVerificando registro en BD...")
recargas = CargasSaldo.objects.filter(nro_tarjeta=tarjeta).order_by('-fecha_carga')[:3]
for r in recargas:
    print(f"  - {r.fecha_carga} | Monto: {r.monto_cargado} | Forma: {r.forma_pago} | Saldo: {r.saldo_posterior}")
print("="*70)
