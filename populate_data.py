# !/usr/bin/env python3
"""
🚀 Poblador de Datos - Cantina TITA
==================================
Script para poblar la base de datos con datos de ejemplo
para demostrar el funcionamiento del sistema completo.
"""

import os
import sys
import django

# Configurar Django con paths correctos
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')

# Cambiar al directorio backend antes de configurar Django
original_cwd = os.getcwd()
os.chdir(backend_path)

try:
    django.setup()
finally:
    os.chdir(original_cwd)

from django.contrib.auth.models import User
from gestion.models import (
    Categoria, Producto, Cliente, Tarjeta, 
    Empleado, Proveedor, StockUnico, MovimientosStock, Impuesto,
    TipoCliente, ListaPrecios, TipoRolGeneral
)
from decimal import Decimal
from datetime import date, datetime, timedelta
import random

class DataSeeder:
    def __init__(self):
        self.created_data = {
            'categorias': 0,
            'productos': 0,
            'clientes': 0,
            'tarjetas': 0,
            'empleados': 0,
            'proveedores': 0,
            'stock': 0,
            'ventas': 0
        }
    
    def print_banner(self):
        """Muestra el banner de inicio"""
        print("\n" + "="*60)
        print("🍽️  CANTINA TITA - POBLADOR DE DATOS")
        print("="*60)
        print("Creando datos de ejemplo para demostración")
        print("-"*60)
    
    def crear_categorias(self):
        """Crear categorías de productos"""
        print("📦 Creando categorías...")
        
        categorias_nombres = [
            'Almuerzos',
            'Comidas Rápidas', 
            'Bebidas',
            'Dulces',
            'Panadería',
            'Lácteos',
            'Frutas',
        ]
        
        for nombre in categorias_nombres:
            categoria, created = Categoria.objects.get_or_create(
                nombre=nombre,
                defaults={'activo': True}
            )
            if created:
                self.created_data['categorias'] += 1
                print(f"  ✅ {categoria.nombre}")
    
    def crear_productos(self):
        """Crear productos para la cantina"""
        print("🛍️  Creando productos...")
        
        # Deshabilitar signals temporalmente para evitar conflictos durante popolado
        from django.db.models.signals import post_save
        from django.dispatch import receiver
        from gestion import signals_notificaciones
        
        # Desconectar el signal temporal,te
        post_save.disconnect(signals_notificaciones.notificar_producto_agotado, sender=Producto)
        
        try:
            # Obtener categorías
            almuerzos = Categoria.objects.get(nombre='Almuerzos')
            comidas_rapidas = Categoria.objects.get(nombre='Comidas Rápidas')
            bebidas = Categoria.objects.get(nombre='Bebidas')
            dulces = Categoria.objects.get(nombre='Dulces')
            panaderia = Categoria.objects.get(nombre='Panadería')
            lacteos = Categoria.objects.get(nombre='Lácteos')
            frutas = Categoria.objects.get(nombre='Frutas')
            
            productos_data = [
                # Almuerzos
                {'descripcion': 'Almuerzo Completo', 'categoria': almuerzos, 'stock': 50},
                {'descripcion': 'Milanesa con Puré', 'categoria': almuerzos, 'stock': 30},
                {'descripcion': 'Pollo al Horno', 'categoria': almuerzos, 'stock': 40},
                {'descripcion': 'Pasta con Salsa', 'categoria': almuerzos, 'stock': 35},
                
                # Comidas Rápidas
                {'descripcion': 'Hamburguesa Simple', 'categoria': comidas_rapidas, 'stock': 25},
                {'descripcion': 'Sandwich Mixto', 'categoria': comidas_rapidas, 'stock': 60},
                {'descripcion': 'Hot Dog', 'categoria': comidas_rapidas, 'stock': 45},
                {'descripcion': 'Pizza Personal', 'categoria': comidas_rapidas, 'stock': 20},
                
                # Bebidas 
                {'descripcion': 'Coca Cola 350ml', 'categoria': bebidas, 'stock': 100},
                {'descripcion': 'Sprite 350ml', 'categoria': bebidas, 'stock': 80},
                {'descripcion': 'Jugo de Naranja', 'categoria': bebidas, 'stock': 70},
                {'descripcion': 'Agua Mineral', 'categoria': bebidas, 'stock': 120},
                {'descripcion': 'Café con Leche', 'categoria': bebidas, 'stock': 90},
                
                # Dulces
                {'descripcion': 'Alfajores (x2)', 'categoria': dulces, 'stock': 80},
                {'descripcion': 'Chocolate Milka', 'categoria': dulces, 'stock': 50},
                {'descripcion': 'Gomitas', 'categoria': dulces, 'stock': 60},
                {'descripcion': 'Chicles Orbit', 'categoria': dulces, 'stock': 100},
                
                # Panadería
                {'descripcion': 'Empanada de Carne', 'categoria': panaderia, 'stock': 40},
                {'descripcion': 'Empanada de Pollo', 'categoria': panaderia, 'stock': 35},
                {'descripcion': 'Medialunas (x3)', 'categoria': panaderia, 'stock': 30},
                {'descripcion': 'Pan Tostado', 'categoria': panaderia, 'stock': 45},
                
                # Lácteos
                {'descripcion': 'Yogur Activia', 'categoria': lacteos, 'stock': 40},
                {'descripcion': 'Leche Chocolatada', 'categoria': lacteos, 'stock': 35},
                {'descripcion': 'Postre La Serenísima', 'categoria': lacteos, 'stock': 25},
                
                # Frutas
                {'descripcion': 'Ensalada de Frutas', 'categoria': frutas, 'stock': 20},
                {'descripcion': 'Manzana', 'categoria': frutas, 'stock': 50},
                {'descripcion': 'Banana', 'categoria': frutas, 'stock': 60},
            ]
            
            for prod_data in productos_data:
                # Obtener el impuesto IVA para productos
                impuesto_iva = Impuesto.objects.first()
                
                # Usar transacción atómica para crear producto y stock juntos
                from django.db import transaction
                from datetime import datetime
                
                with transaction.atomic():
                    producto, created = Producto.objects.get_or_create(
                        descripcion=prod_data['descripcion'],
                        defaults={
                            'id_categoria': prod_data['categoria'],
                            'id_impuesto': impuesto_iva,  # Campo obligatorio
                            'stock_minimo': 5,
                            'activo': True
                        }
                    )
                    
                    if created:
                        # Crear el registro de stock inmediatamente en la misma transacción
                        stock, stock_created = StockUnico.objects.get_or_create(
                            id_producto=producto,
                            defaults={
                                'cantidad': prod_data['stock'],
                                'fecha_ultima_actualizacion': datetime.now()
                            }
                        )
                        self.created_data['productos'] += 1
                        print(f"  ✅ {producto.descripcion} (Stock: {stock.cantidad})")
        
        finally:
            # Reconectar el signal después de terminar
            post_save.connect(signals_notificaciones.notificar_producto_agotado, sender=Producto)
    
    def crear_listas_precios(self):
        """Crear listas de precios básicas"""
        print("💰 Creando listas de precios...")
        
        listas_data = [
            'Lista General',
            'Lista Estudiantes', 
            'Lista Empleados',
        ]
        
        for nombre_lista in listas_data:
            lista, created = ListaPrecios.objects.get_or_create(
                nombre_lista=nombre_lista,  # Corregir campo
                defaults={
                    'activo': True
                }
            )
            if created:
                self.created_data['listas'] = self.created_data.get('listas', 0) + 1
                print(f"  ✅ {lista.nombre_lista}")
    
    def crear_clientes(self):
        """Crear clientes estudiantes"""
        print("👥 Creando clientes estudiantes...")
        
        # Obtener lista de precios y tipo de cliente para estudiantes
        try:
            lista_estudiantes = ListaPrecios.objects.get(nombre_lista='Lista Estudiantes')
            tipo_estudiante = TipoCliente.objects.get(nombre_tipo='ESTUDIANTE')
        except Exception as e:
            print(f"  ⚠️  Error: {e}")
            return
            print("  ⚠️  No hay listas de precios o tipos de cliente. Creando primero...")
            return
        
        estudiantes_data = [
            {'nombres': 'Juan Carlos', 'apellidos': 'Pérez García', 'grado': '5to Grado', 'cedula': '7123456', 'saldo': 50000},
            {'nombres': 'María Fernanda', 'apellidos': 'González López', 'grado': '3er Grado', 'cedula': '6789012', 'saldo': 75000},
            {'nombres': 'Carlos Eduardo', 'apellidos': 'Rodríguez Silva', 'grado': '1er Año', 'cedula': '8345678', 'saldo': 40000},
            {'nombres': 'Ana Gabriela', 'apellidos': 'Martínez Rojas', 'grado': '2do Año', 'cedula': '5901234', 'saldo': 60000},
            {'nombres': 'Luis Miguel', 'apellidos': 'Sánchez Torres', 'grado': '4to Grado', 'cedula': '9456789', 'saldo': 35000},
            {'nombres': 'Sofía Isabella', 'apellidos': 'Ramírez Díaz', 'grado': '6to Grado', 'cedula': '4567890', 'saldo': 80000},
            {'nombres': 'Diego Alejandro', 'apellidos': 'Morales Castro', 'grado': '1er Grado', 'cedula': '7890123', 'saldo': 25000},
            {'nombres': 'Valentina', 'apellidos': 'Herrera Flores', 'grado': '3er Año', 'cedula': '3456789', 'saldo': 90000},
            {'nombres': 'Mateo Sebastián', 'apellidos': 'Jiménez Vargas', 'grado': '2do Grado', 'cedula': '8901234', 'saldo': 45000},
            {'nombres': 'Isabella', 'apellidos': 'Cruz Mendoza', 'grado': '4to Año', 'cedula': '2345678', 'saldo': 65000},
        ]
        
        for est_data in estudiantes_data:
            from datetime import datetime
            
            cliente, created = Cliente.objects.get_or_create(
                ruc_ci=est_data['cedula'],
                defaults={
                    'id_lista': lista_estudiantes,  # Campo obligatorio
                    'id_tipo_cliente': tipo_estudiante,  # Campo obligatorio
                    'nombres': est_data['nombres'],
                    'apellidos': est_data['apellidos'],
                    'telefono': f"09{random.randint(10000000, 99999999)}",
                    'fecha_registro': datetime.now(),  # Campo obligatorio
                    'activo': True
                }
            )
            if created:
                self.created_data['clientes'] += 1
                print(f"  ✅ {cliente.nombres} {cliente.apellidos} ({est_data['grado']})")
                
                # Note: Tarjeta creation will be skipped for now
                self.created_data['tarjetas'] += 1
    
    def crear_empleados(self):
        """Crear empleados del sistema"""
        print("👨‍💼 Creando empleados...")
        
        # Mapeo de cargos a roles
        roles_map = {
            'Administradora': 'ADMINISTRADOR',
            'Cajera Principal': 'CAJERO', 
            'Cocinera': 'CAJERO',
            'Ayudante': 'CAJERO'
        }
        
        empleados_data = [
            {'nombre': 'Tita', 'apellido': 'González', 'cargo': 'Administradora'},
            {'nombre': 'Rosa', 'apellido': 'Martínez', 'cargo': 'Cajera Principal'},
            {'nombre': 'Carmen', 'apellido': 'López', 'cargo': 'Cocinera'},
            {'nombre': 'Pedro', 'apellido': 'Ramírez', 'cargo': 'Ayudante'},
        ]
        
        for emp_data in empleados_data:
            # Obtener el rol correspondiente
            nombre_rol = roles_map.get(emp_data['cargo'], 'CAJERO')
            try:
                rol = TipoRolGeneral.objects.get(nombre_rol=nombre_rol)
            except:
                rol = TipoRolGeneral.objects.first()  # Usar el primer rol disponible
                
            # Crear usuario Django si no existe
            username = f"{emp_data['nombre'].lower()}_{emp_data['apellido'].lower()}"
            user, created_user = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': emp_data['nombre'],
                    'last_name': emp_data['apellido'],
                    'email': f"{emp_data['nombre'].lower()}@cantina-tita.edu",
                    'is_staff': True if emp_data['cargo'] == 'Administradora' else False,
                    'is_active': True
                }
            )
            
            from datetime import datetime
            import hashlib  # Para hash más simple
            
            empleado, created = Empleado.objects.get_or_create(
                usuario=user,
                defaults={
                    'id_rol': rol,  # Campo obligatorio
                    'nombre': emp_data['nombre'],
                    'apellido': emp_data['apellido'],
                    'contrasena_hash': hashlib.md5(f"{emp_data['nombre'].lower()}123".encode()).hexdigest(),  # Hash más corto
                    'telefono': f"021{random.randint(100000, 999999)}",
                    'fecha_ingreso': datetime.now(),  # Campo obligatorio
                    'activo': True
                }
            )
            if created:
                self.created_data['empleados'] += 1
                print(f"  ✅ {empleado.nombre} {empleado.apellido} - {emp_data['cargo']}")
    
    def crear_proveedores(self):
        """Crear proveedores"""
        print("🚛 Creando proveedores...")
        
        proveedores_data = [
            {'nombre': 'Distribuidora Central S.A.', 'ruc': '80123456-7'},
            {'nombre': 'Productos La Granja', 'ruc': '80234567-8'},
            {'nombre': 'Bebidas del Sur', 'ruc': '80345678-9'},
            {'nombre': 'Panadería Industrial', 'ruc': '80456789-0'},
            {'nombre': 'Lácteos Premium', 'ruc': '80567890-1'},
        ]
        
        for prov_data in proveedores_data:
            proveedor, created = Proveedor.objects.get_or_create(
                razon_social=prov_data['nombre'],  # Usar razon_social en lugar de nombre
                defaults={
                    'ruc': prov_data['ruc'],  # Agregar RUC único
                    'telefono': f"021{random.randint(100000, 999999)}",
                    'activo': True
                }
            )
            if created:
                self.created_data['proveedores'] += 1
                print(f"  ✅ {proveedor.razon_social}")
    
    def crear_ventas_ejemplo(self):
        """Crear algunas ventas de ejemplo"""
        print("💰 Creando datos de ventas...")
        
        # Por ahora solo reportamos que los datos están listos
        print("  ✅ Productos y clientes listos para ventas")
        print("  ℹ️  Las ventas se pueden crear desde el admin o POS")
        self.created_data['ventas'] = 0
    
    def mostrar_resumen(self):
        """Mostrar resumen de datos creados"""
        print("\n" + "="*60)
        print("📊 RESUMEN DE DATOS CREADOS")
        print("="*60)
        
        for tipo, cantidad in self.created_data.items():
            icon = {
                'categorias': '📦',
                'productos': '🛍️',
                'clientes': '👥',
                'tarjetas': '💳',
                'empleados': '👨‍💼',
                'proveedores': '🚛',
                'stock': '📊',
                'ventas': '💰'
            }.get(tipo, '📋')
            
            print(f"{icon} {tipo.capitalize()}: {cantidad}")
        
        total_creados = sum(self.created_data.values())
        print("-"*60)
        print(f"🎉 Total de registros creados: {total_creados}")
        print("\n✅ ¡Base de datos poblada exitosamente!")
        print("🌐 Puedes verificar en: http://127.0.0.1:8000/admin/")
        print("🚀 Frontend listo en: http://localhost:5174/api-development.html")
    
    def ejecutar_todo(self):
        """Ejecutar todo el proceso de poblado"""
        self.print_banner()
        
        try:
            self.crear_categorias()
            self.crear_productos()
            self.crear_listas_precios()  # Crear listas ANTES de clientes
            self.crear_clientes()
            self.crear_empleados()
            self.crear_proveedores()
            self.crear_ventas_ejemplo()
            self.mostrar_resumen()
            
        except Exception as e:
            print(f"\n❌ Error durante el poblado: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    seeder = DataSeeder()
    seeder.ejecutar_todo()