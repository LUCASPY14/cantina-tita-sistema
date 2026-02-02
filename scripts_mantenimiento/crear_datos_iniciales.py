#!/usr/bin/env python
"""
Script para crear datos iniciales faltantes
"""
import os
import django
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from gestion.models import Cliente, ListaPrecios, TipoCliente

# Obtener o crear lista de precios y tipo de cliente
lista_precios = ListaPrecios.objects.filter(activo=True).first()
if not lista_precios:
    print("[ERROR] No hay lista de precios configurada")
    sys.exit(1)

tipo_cliente = TipoCliente.objects.first()
if not tipo_cliente:
    tipo_cliente = TipoCliente.objects.create(descripcion='Público')

# Crear Cliente público si no existe
cliente_publico = Cliente.objects.filter(nombres__icontains='público').first()

if not cliente_publico:
    cliente_publico = Cliente.objects.create(
        id_lista=lista_precios,
        id_tipo_cliente=tipo_cliente,
        nombres='Cliente',
        apellidos='Público',
        ruc_ci='0000000-0',
        email='publico@sistema.local',
        telefono='0000',
        activo=True
    )
    print(f"[OK] Cliente Público creado: {cliente_publico.nombre_completo}")
else:
    print(f"[OK] Cliente Público ya existe: {cliente_publico.nombre_completo}")
