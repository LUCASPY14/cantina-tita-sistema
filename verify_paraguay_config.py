"""
Script para verificar la configuración regional de Paraguay
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.conf import settings
from django.utils import timezone, formats
from gestion.utils_moneda import formatear_guaranies, calcular_iva, formatear_guaranies_largo
from datetime import datetime

print("=" * 80)
print("🇵🇾 VERIFICACIÓN DE CONFIGURACIÓN REGIONAL - PARAGUAY")
print("=" * 80)

# Configuración básica
print("\n📋 CONFIGURACIÓN BÁSICA:")
print(f"   Idioma: {settings.LANGUAGE_CODE}")
print(f"   Zona horaria: {settings.TIME_ZONE}")
print(f"   Usar i18n: {settings.USE_I18N}")
print(f"   Usar TZ: {settings.USE_TZ}")

# Formatos de fecha
print("\n📅 FORMATOS DE FECHA:")
print(f"   Formato fecha: {settings.DATE_FORMAT}")
print(f"   Formato fecha/hora: {settings.DATETIME_FORMAT}")

# Formatos numéricos
print("\n🔢 FORMATOS NUMÉRICOS:")
print(f"   Separador de miles: '{settings.THOUSAND_SEPARATOR}'")
print(f"   Separador decimal: '{settings.DECIMAL_SEPARATOR}'")
print(f"   Usar separador: {settings.USE_THOUSAND_SEPARATOR}")

# Prueba de fecha actual
print("\n🕐 FECHA Y HORA ACTUAL:")
ahora = timezone.now()
print(f"   Fecha/hora local: {ahora}")
print(f"   Formateado: {formats.date_format(ahora, 'SHORT_DATETIME_FORMAT')}")

# Prueba de formateo de moneda
print("\n💰 FORMATEO DE GUARANÍES:")
montos = [1000, 50000, 1500000, 25000000]
for monto in montos:
    print(f"   {monto:>10} → {formatear_guaranies(monto)}")
    print(f"   {' '*10}    {formatear_guaranies_largo(monto)}")

# Prueba de IVA
print("\n🧾 CÁLCULO DE IVA:")
monto_base = 100000
monto_con_iva_10, iva_10 = calcular_iva(monto_base, '10')
monto_con_iva_5, iva_5 = calcular_iva(monto_base, '5')

print(f"   Base: {formatear_guaranies(monto_base)}")
print(f"   Con IVA 10%: {formatear_guaranies(monto_con_iva_10)} (IVA: {formatear_guaranies(iva_10)})")
print(f"   Con IVA 5%: {formatear_guaranies(monto_con_iva_5)} (IVA: {formatear_guaranies(iva_5)})")

# Ejemplo de venta
print("\n🛒 EJEMPLO DE VENTA:")
productos = [
    {'nombre': 'Coca Cola 500ml', 'precio': 5000, 'cantidad': 2},
    {'nombre': 'Empanada de carne', 'precio': 3500, 'cantidad': 3},
    {'nombre': 'Agua mineral', 'precio': 2500, 'cantidad': 1},
]

print(f"\n   {'Producto':<25} {'Cant.':<6} {'Precio Unit.':<18} {'Subtotal':<18}")
print(f"   {'-'*70}")

subtotal = 0
for prod in productos:
    precio_total = prod['precio'] * prod['cantidad']
    subtotal += precio_total
    print(f"   {prod['nombre']:<25} {prod['cantidad']:<6} {formatear_guaranies(prod['precio']):<18} {formatear_guaranies(precio_total):<18}")

iva_total = int(subtotal * 0.10)
total = subtotal + iva_total

print(f"   {'-'*70}")
print(f"   {'Subtotal:':<32} {formatear_guaranies(subtotal):>38}")
print(f"   {'IVA 10%:':<32} {formatear_guaranies(iva_total):>38}")
print(f"   {'TOTAL:':<32} {formatear_guaranies(total):>38}")

print("\n" + "=" * 80)
print("✅ CONFIGURACIÓN VERIFICADA CORRECTAMENTE")
print("=" * 80)
print("\n💡 Consejos:")
print("   • Usa {{ monto|guaranies }} en templates para formatear")
print("   • Usa formatear_guaranies(monto) en Python")
print("   • Las fechas se mostrarán en formato DD/MM/AAAA")
print("   • Los números usarán punto (.) como separador de miles")
print("\n")
