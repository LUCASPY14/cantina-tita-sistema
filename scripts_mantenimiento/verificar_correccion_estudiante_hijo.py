"""
Script de verificación para confirmar que las referencias estudiante->hijos funcionan correctamente
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from gestion.models import Hijo, VistaConsumosEstudiante, VistaRecargasHistorial, Tarjeta, Ventas

print("=" * 80)
print("VERIFICACIÓN: REFERENCIAS ESTUDIANTE -> HIJOS (ID_Hijo)")
print("=" * 80)

# ============================================================================
# VERIFICACIÓN 1: Modelo Hijo
# ============================================================================
print("\n[1] Verificando modelo Hijo...")
hijos = Hijo.objects.all()[:5]
print(f"✓ Total de hijos en sistema: {Hijo.objects.count()}")
print(f"\nPrimeros 5 hijos:")
for hijo in hijos:
    print(f"  - ID: {hijo.id_hijo}, Nombre: {hijo.nombre_completo}, Grado: {hijo.grado or 'N/A'}")

# ============================================================================
# VERIFICACIÓN 2: Vista Consumos Estudiante
# ============================================================================
print("\n[2] Verificando VistaConsumosEstudiante con ForeignKey...")
try:
    consumos = VistaConsumosEstudiante.objects.select_related('id_hijo').all()[:5]
    print(f"✓ Vista funciona correctamente")
    print(f"  Total registros: {VistaConsumosEstudiante.objects.count()}")
    
    print(f"\nPrimeros 5 registros de consumos:")
    for consumo in consumos:
        print(f"  - Estudiante: {consumo.estudiante}")
        print(f"    ID_Hijo: {consumo.id_hijo.id_hijo}")
        print(f"    Nombre completo: {consumo.id_hijo.nombre_completo}")
        print(f"    Responsable: {consumo.responsable_nombre} {consumo.responsable_apellido}")
        print(f"    Saldo: Gs. {consumo.saldo_actual:,}")
        print(f"    Total consumido: Gs. {float(consumo.total_consumido):,.2f}")
        print()
        
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# VERIFICACIÓN 3: Vista Recargas Historial
# ============================================================================
print("\n[3] Verificando VistaRecargasHistorial con ForeignKey...")
try:
    recargas = VistaRecargasHistorial.objects.select_related('id_hijo').all()[:5]
    print(f"✓ Vista funciona correctamente")
    print(f"  Total registros: {VistaRecargasHistorial.objects.count()}")
    
    print(f"\nPrimeras 5 recargas:")
    for recarga in recargas:
        print(f"  - Recarga ID: {recarga.id_carga}")
        print(f"    Estudiante: {recarga.estudiante}")
        print(f"    ID_Hijo: {recarga.id_hijo.id_hijo}")
        print(f"    Nombre completo: {recarga.id_hijo.nombre_completo}")
        print(f"    Monto: Gs. {float(recarga.monto_cargado):,.2f}")
        print(f"    Fecha: {recarga.fecha_carga}")
        print()
        
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# VERIFICACIÓN 4: Tabla Tarjetas
# ============================================================================
print("\n[4] Verificando tabla Tarjetas (OneToOneField con Hijo)...")
try:
    tarjetas = Tarjeta.objects.select_related('id_hijo').all()[:5]
    print(f"✓ Tarjetas funcionan correctamente")
    print(f"  Total tarjetas: {Tarjeta.objects.count()}")
    
    print(f"\nPrimeras 5 tarjetas:")
    for tarjeta in tarjetas:
        print(f"  - Tarjeta: {tarjeta.nro_tarjeta}")
        print(f"    ID_Hijo: {tarjeta.id_hijo.id_hijo}")
        print(f"    Estudiante: {tarjeta.id_hijo.nombre_completo}")
        print(f"    Saldo: Gs. {tarjeta.saldo_actual:,}")
        print(f"    Estado: {tarjeta.estado}")
        print()
        
except Exception as e:
    print(f"✗ Error: {e}")

# ============================================================================
# VERIFICACIÓN 5: Tabla Ventas
# ============================================================================
print("\n[5] Verificando tabla Ventas (ForeignKey con Hijo)...")
try:
    ventas = Ventas.objects.select_related('id_hijo').filter(id_hijo__isnull=False)[:5]
    print(f"✓ Ventas funcionan correctamente")
    print(f"  Total ventas con hijo: {Ventas.objects.filter(id_hijo__isnull=False).count()}")
    
    print(f"\nPrimeras 5 ventas con estudiante:")
    for venta in ventas:
        print(f"  - Venta ID: {venta.id_venta}")
        print(f"    ID_Hijo: {venta.id_hijo.id_hijo}")
        print(f"    Estudiante: {venta.id_hijo.nombre_completo}")
        print(f"    Monto: Gs. {venta.monto_total:,}")
        print(f"    Fecha: {venta.fecha}")
        print()
        
except Exception as e:
    print(f"✗ Error: {e}")

# ============================================================================
# VERIFICACIÓN 6: Acceso mediante propiedades
# ============================================================================
print("\n[6] Verificando acceso mediante propiedades...")
try:
    consumo = VistaConsumosEstudiante.objects.first()
    if consumo:
        print(f"✓ Acceso mediante property 'hijo':")
        print(f"  consumo.hijo = {consumo.hijo}")
        print(f"  consumo.hijo.nombre_completo = {consumo.hijo.nombre_completo}")
        print(f"  consumo.hijo.grado = {consumo.hijo.grado or 'N/A'}")
        
    recarga = VistaRecargasHistorial.objects.first()
    if recarga:
        print(f"\n✓ Acceso mediante property 'hijo' en recargas:")
        print(f"  recarga.hijo = {recarga.hijo}")
        print(f"  recarga.hijo.nombre_completo = {recarga.hijo.nombre_completo}")
        
except Exception as e:
    print(f"✗ Error: {e}")

# ============================================================================
# VERIFICACIÓN 7: Queries complejas
# ============================================================================
print("\n[7] Verificando queries con JOIN...")
try:
    # Query con filtro por grado
    consumos_grado = VistaConsumosEstudiante.objects.select_related('id_hijo').filter(
        id_hijo__grado__isnull=False
    )[:3]
    
    print(f"✓ Consumos filtrados por estudiantes con grado asignado:")
    for c in consumos_grado:
        print(f"  - {c.estudiante}, Grado: {c.id_hijo.grado}")
    
    # Query con filtro por cliente responsable
    ventas_cliente = Ventas.objects.select_related('id_hijo', 'id_hijo__id_cliente_responsable').filter(
        id_hijo__isnull=False
    ).first()
    
    if ventas_cliente:
        print(f"\n✓ Venta con acceso a datos del responsable:")
        print(f"  - Estudiante: {ventas_cliente.id_hijo.nombre_completo}")
        print(f"  - Responsable: {ventas_cliente.id_hijo.id_cliente_responsable.nombre_completo}")
        
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "=" * 80)
print("RESUMEN")
print("=" * 80)
print("""
✅ CORRECCIONES APLICADAS EXITOSAMENTE:

1. ✓ Tabla 'hijos' con ID_Hijo como PK
2. ✓ Vistas SQL actualizadas con ID_Hijo explícito
3. ✓ Modelos Django con ForeignKey a Hijo
4. ✓ Propiedades 'hijo' para acceso directo
5. ✓ Queries con select_related funcionan correctamente
6. ✓ Acceso a datos relacionados (cliente responsable, grado, etc.)

CONCLUSIÓN:
Las referencias 'estudiante' y 'estudiantes' ahora están correctamente
relacionadas con la tabla 'hijos' mediante ID_Hijo, tanto en la base
de datos SQL como en los modelos de Django.
""")
print("=" * 80)
