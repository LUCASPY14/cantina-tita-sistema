#!/usr/bin/env python
"""
Script para verificar y poblar roles y datos base del sistema
"""
import os
import sys
import django
from dotenv import load_dotenv
from datetime import datetime

# Cargar variables de entorno
load_dotenv()

# Configurar Django
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.contrib.auth.models import User, Group, Permission
from gestion.models import (TipoRolGeneral, Empleado, DatosEmpresa, Categoria, 
                           TipoCliente, UnidadMedida, Impuesto, MediosPago, 
                           TiposPago, TipoAlmuerzo)

def verificar_roles():
    """Verificar y mostrar roles existentes"""
    print("=" * 70)
    print("🔐 ROLES Y EMPLEADOS DEL SISTEMA")
    print("=" * 70)
    
    # Roles existentes
    roles = TipoRolGeneral.objects.all()
    print(f"\n📊 ROLES DISPONIBLES ({roles.count()}):")
    print("-" * 50)
    
    if not roles.exists():
        print("❌ No hay roles configurados")
        return False
    
    for rol in roles:
        empleados_count = Empleado.objects.filter(id_rol=rol, activo=True).count()
        print(f"   {rol.id_rol:2d}. {rol.nombre_rol:15} | {empleados_count:2d} empleados | {rol.descripcion or 'Sin descripción'}")
    
    # Empleados por rol
    print(f"\n👥 EMPLEADOS ACTIVOS ({Empleado.objects.filter(activo=True).count()}):")
    print("-" * 50)
    
    empleados = Empleado.objects.filter(activo=True).select_related('id_rol')
    if not empleados.exists():
        print("❌ No hay empleados configurados")
        return False
    
    for emp in empleados:
        rol_nombre = emp.id_rol.nombre_rol if emp.id_rol else "SIN ROL"
        print(f"   👤 {emp.usuario:15} | {emp.nombre:25} | 🎭 {rol_nombre}")
        if hasattr(emp, 'email') and emp.email:
            print(f"      📧 {emp.email}")
        print()
    
    return True

def crear_roles_base():
    """Crear roles base si no existen"""
    print("\n🔧 CREANDO ROLES BASE...")
    
    roles_base = [
        (1, 'CAJERO', 'Acceso básico - Punto de venta y recargas'),
        (2, 'GERENTE', 'Acceso medio - Reportes e inventario'),
        (3, 'ADMINISTRADOR', 'Acceso total - Configuración y gestión'),
        (4, 'SISTEMA', 'Usuario interno - Procesos automatizados'),
    ]
    
    creados = 0
    for id_rol, nombre, descripcion in roles_base:
        rol, created = TipoRolGeneral.objects.get_or_create(
            id_rol=id_rol,
            defaults={
                'nombre_rol': nombre,
                'descripcion': descripcion
            }
        )
        if created:
            print(f"   ✅ Creado: {nombre}")
            creados += 1
        else:
            print(f"   ⚪ Existe: {nombre}")
    
    print(f"\n📊 Roles creados: {creados}")
    return creados > 0

def crear_datos_empresa():
    """Crear datos base de la empresa"""
    print("\n🏢 CONFIGURANDO DATOS EMPRESA...")
    
    empresa, created = DatosEmpresa.objects.get_or_create(
        id_empresa=1,
        defaults={
            'ruc': '80012345-6',
            'razon_social': 'Cantina TITA',
            'direccion': 'Av. Principal 123',
            'ciudad': 'Asunción',
            'pais': 'Paraguay',
            'telefono': '021-123456',
            'email': 'info@cantinatita.com',
            'activo': 1
        }
    )
    
    if created:
        print("   ✅ Empresa configurada")
        return True
    else:
        print("   ⚪ Empresa ya existe")
        return False

def crear_catalogos_base():
    """Crear catálogos base del sistema"""
    print("\n📚 CONFIGURANDO CATÁLOGOS BASE...")
    
    cambios = 0
    
    # Categorías de productos
    categorias = [
        'Alimentos',
        'Bebidas', 
        'Snacks',
        'Almuerzos',
        'Dulces',
        'Útiles Escolares'
    ]
    
    for nombre in categorias:
        cat, created = Categoria.objects.get_or_create(
            nombre=nombre,
            defaults={'activo': True}
        )
        if created:
            print(f"   ✅ Categoría: {nombre}")
            cambios += 1
    
    # Tipos de cliente
    tipos_cliente = [
        'ESTUDIANTE',
        'EMPLEADO',
        'COMERCIAL', 
        'VISITANTE'
    ]
    
    for nombre in tipos_cliente:
        tipo, created = TipoCliente.objects.get_or_create(
            nombre_tipo=nombre,
            defaults={'activo': True}
        )
        if created:
            print(f"   ✅ Tipo Cliente: {nombre}")
            cambios += 1
    
    # Unidades de medida
    unidades = [
        ('UNI', 'Unidad'),
        ('KG', 'Kilogramo'),
        ('LT', 'Litro'),
        ('GR', 'Gramo'),
        ('ML', 'Mililitro'),
        ('DOC', 'Docena')
    ]
    
    for abrev, nombre in unidades:
        uni, created = UnidadMedida.objects.get_or_create(
            abreviatura=abrev,
            defaults={'nombre': nombre, 'activo': True}
        )
        if created:
            print(f"   ✅ Unidad: {abrev} - {nombre}")
            cambios += 1
    
    # Impuestos
    imp, created = Impuesto.objects.get_or_create(
        nombre_impuesto='IVA',
        defaults={
            'porcentaje': 10.0, 
            'vigente_desde': datetime.now().date(),
            'activo': True
        }
    )
    if created:
        print("   ✅ Impuesto: IVA 10%")
        cambios += 1
    
    # Medios de pago
    medios = [
        'Efectivo',
        'Tarjeta de estudiante', 
        'Transferencia bancaria',
        'Código QR'
    ]
    
    for descripcion in medios:
        medio, created = MediosPago.objects.get_or_create(
            descripcion=descripcion,
            defaults={'activo': True}
        )
        if created:
            print(f"   ✅ Medio Pago: {descripcion}")
            cambios += 1
    
    # Tipos de almuerzo
    tipos_almuerzo = [
        ('Almuerzo completo', 15000),
        ('Almuerzo vegetariano', 12000), 
        ('Almuerzo dietético', 13000),
        ('Almuerzo especial', 18000)
    ]
    
    for nombre, precio in tipos_almuerzo:
        tipo, created = TipoAlmuerzo.objects.get_or_create(
            nombre=nombre,
            defaults={
                'descripcion': f'{nombre} - Incluye plato principal',
                'precio_unitario': precio,
                'activo': True
            }
        )
        if created:
            print(f"   ✅ Tipo Almuerzo: {nombre} - Gs. {precio:,}")
            cambios += 1
    
    print(f"\n📊 Catálogos creados/actualizados: {cambios}")
    return cambios > 0

def crear_grupos_django():
    """Crear grupos de Django para permisos"""
    print("\n👥 CONFIGURANDO GRUPOS DJANGO...")
    
    grupos_permisos = {
        'Administradores': [
            'add_user', 'change_user', 'delete_user', 'view_user',
            'add_cliente', 'change_cliente', 'delete_cliente', 'view_cliente',
            'add_producto', 'change_producto', 'delete_producto', 'view_producto',
            'add_empleado', 'change_empleado', 'delete_empleado', 'view_empleado'
        ],
        'Gerentes': [
            'view_user', 'view_cliente', 'add_cliente', 'change_cliente',
            'view_producto', 'add_producto', 'change_producto',
            'view_empleado'
        ],
        'Cajeros': [
            'view_cliente', 'view_producto', 'add_venta', 'view_venta'
        ]
    }
    
    creados = 0
    for grupo_nombre, permisos in grupos_permisos.items():
        grupo, created = Group.objects.get_or_create(name=grupo_nombre)
        
        if created:
            print(f"   ✅ Grupo: {grupo_nombre}")
            creados += 1
            
            # Agregar permisos al grupo
            for permiso_codename in permisos:
                try:
                    permiso = Permission.objects.get(codename=permiso_codename)
                    grupo.permissions.add(permiso)
                except Permission.DoesNotExist:
                    continue
        else:
            print(f"   ⚪ Grupo existe: {grupo_nombre}")
    
    print(f"\n📊 Grupos Django creados: {creados}")
    return creados > 0

def verificar_usuario_admin():
    """Verificar usuario administrador"""
    print("\n🔑 VERIFICANDO USUARIO ADMIN...")
    
    try:
        admin_user = User.objects.get(username='admin')
        print(f"   ✅ Admin existe: {admin_user.username}")
        print(f"   📧 Email: {admin_user.email}")
        print(f"   🔑 Superuser: {admin_user.is_superuser}")
        print(f"   👨‍💼 Staff: {admin_user.is_staff}")
        
        # Verificar si tiene empleado asociado
        try:
            empleado = Empleado.objects.get(usuario=admin_user.username)
            print(f"   👤 Empleado: {empleado.nombre}")
            print(f"   🎭 Rol: {empleado.id_rol.nombre_rol if empleado.id_rol else 'SIN ROL'}")
        except Empleado.DoesNotExist:
            print("   ⚠️ No tiene empleado asociado")
            
        return True
        
    except User.DoesNotExist:
        print("   ❌ Usuario admin no existe")
        return False

def main():
    """Función principal"""
    print("🚀 VERIFICACIÓN Y CONFIGURACIÓN DEL SISTEMA")
    print("=" * 70)
    
    # 1. Verificar roles existentes
    roles_ok = verificar_roles()
    
    if not roles_ok:
        # 2. Crear roles si no existen
        crear_roles_base()
    
    # 3. Configurar datos empresa
    crear_datos_empresa()
    
    # 4. Crear catálogos base
    crear_catalogos_base()
    
    # 5. Crear grupos Django
    crear_grupos_django()
    
    # 6. Verificar admin
    verificar_usuario_admin()
    
    print("\n" + "=" * 70)
    print("✅ CONFIGURACIÓN COMPLETADA")
    print("=" * 70)
    
    # Mostrar resumen final
    print(f"\n📊 RESUMEN FINAL:")
    print(f"   👥 Usuarios Django: {User.objects.count()}")
    print(f"   🎭 Roles: {TipoRolGeneral.objects.count()}")
    print(f"   👤 Empleados: {Empleado.objects.filter(activo=True).count()}")
    print(f"   🏢 Empresa: {'✅' if DatosEmpresa.objects.exists() else '❌'}")
    print(f"   📚 Categorías: {Categoria.objects.count()}")
    print(f"   👥 Grupos Django: {Group.objects.count()}")

if __name__ == "__main__":
    main()