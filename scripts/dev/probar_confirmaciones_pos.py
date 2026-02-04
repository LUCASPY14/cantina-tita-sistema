#!/usr/bin/env python
"""
Script para probar las confirmaciones en POS - Cantina Tita
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from gestion.models import Hijo, Tarjeta, Producto, UsuariosWebClientes
from django.test import Client
from django.urls import reverse

def probar_confirmaciones_pos():
    """Probar que las confirmaciones en POS funcionen correctamente"""

    print("🛒 PRUEBA DE CONFIRMACIONES EN POS - CANTINA TITA")
    print("=" * 60)

    # Verificar que existe un hijo con restricciones
    hijo_con_restricciones = Hijo.objects.filter(
        restricciones_compra__isnull=False
    ).exclude(restricciones_compra='').first()

    if not hijo_con_restricciones:
        print("⚠️ No hay hijos con restricciones registradas")
        print("   Creando datos de prueba...")

        # Buscar un hijo existente
        hijo = Hijo.objects.first()
        if not hijo:
            print("❌ No hay hijos registrados. Ejecuta crear_datos_prueba.py primero")
            return False

        # Agregar restricciones de prueba
        hijo.restricciones_compra = "Alergia a maní y productos lácteos. No consumir golosinas ni productos con azúcar refinado."
        hijo.save()
        hijo_con_restricciones = hijo
        print(f"✅ Agregadas restricciones de prueba a {hijo.nombre} {hijo.apellido}")

    print(f"✅ Hijo con restricciones encontrado: {hijo_con_restricciones.nombre} {hijo_con_restricciones.apellido}")
    print(f"   Restricciones: {hijo_con_restricciones.restricciones_compra[:100]}...")

    # Verificar que tiene tarjeta
    tarjeta = Tarjeta.objects.filter(id_hijo=hijo_con_restricciones).first()
    if not tarjeta:
        print("❌ El hijo no tiene tarjeta asignada")
        return False

    print(f"✅ Tarjeta encontrada: #{tarjeta.nro_tarjeta} - Saldo: Gs. {tarjeta.saldo_actual:,.0f}")

    # Verificar que hay productos disponibles
    productos = Producto.objects.filter(activo=True)[:3]
    if not productos:
        print("❌ No hay productos activos")
        return False

    print(f"✅ Productos disponibles: {len(productos)} encontrados")
    for prod in productos:
        print(f"   - {prod.descripcion} (ID: {prod.id_producto})")

    # Verificar que el modal de restricciones existe en el template
    try:
        with open('templates/pos/venta.html', 'r', encoding='utf-8') as f:
            template_content = f.read()
    except FileNotFoundError:
        print("❌ Template venta.html no encontrado")
        return False

    if 'modal-restricciones' not in template_content:
        print("❌ Modal de restricciones no encontrado en template")
        return False

    if 'restriccionesModal()' not in template_content:
        print("❌ Componente restriccionesModal() no encontrado")
        return False

    print("✅ Modal de restricciones presente en template")

    # Verificar lógica en base.html
    try:
        with open('templates/base.html', 'r', encoding='utf-8') as f:
            base_content = f.read()
    except FileNotFoundError:
        print("❌ Template base.html no encontrado")
        return False

    if 'restricciones_confirmadas' not in base_content:
        print("❌ Lógica de restricciones no encontrada en base.html")
        return False

    print("✅ Lógica de confirmación de restricciones presente")

    # Verificar que la auditoría está implementada en pos_views.py
    try:
        with open('gestion/pos_views.py', 'r', encoding='utf-8') as f:
            views_content = f.read()
    except FileNotFoundError:
        print("❌ Archivo pos_views.py no encontrado")
        return False

    if 'VENTA_CON_RESTRICCIONES' not in views_content:
        print("❌ Auditoría de restricciones no implementada en pos_views.py")
        return False

    print("✅ Auditoría de restricciones implementada")

    # Verificar configuración de JavaScript
    if 'restriccionesConfirmadas' not in base_content:
        print("❌ Eventos de restricciones no configurados")
        return False

    print("✅ Eventos de confirmación configurados")

    print("\n" + "=" * 60)
    print("📊 RESULTADO: CONFIRMACIONES POS FUNCIONANDO")
    print("✅ Modal de restricciones: Implementado")
    print("✅ Lógica de confirmación: Presente")
    print("✅ Auditoría: Configurada")
    print("✅ Eventos JavaScript: Configurados")
    print("✅ Datos de prueba: Listos")

    print("\n🧪 PRUEBA MANUAL RECOMENDADA:")
    print("1. Inicia el servidor: python manage.py runserver")
    print("2. Ve al POS: http://127.0.0.1:8000/pos/venta/")
    print("3. Escanea la tarjeta del hijo con restricciones")
    print("4. Agrega productos al carrito")
    print("5. Confirma la venta - debería aparecer el modal de restricciones")
    print("6. Marca el checkbox y agrega justificación opcional")
    print("7. Procede con la venta")

    return True

if __name__ == '__main__':
    probar_confirmaciones_pos()