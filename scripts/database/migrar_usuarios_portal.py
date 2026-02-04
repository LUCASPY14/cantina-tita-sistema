"""
Script de Migración: usuarios_web_clientes → usuario_portal

PROPÓSITO:
Consolidar el sistema de usuarios del portal eliminando duplicación funcional.

PROBLEMA DETECTADO:
- usuarios_web_clientes (tabla legacy): 1 registro
- usuario_portal (tabla nueva): 0 registros
- Ambas tablas tienen el mismo propósito pero diferentes estructuras

SOLUCIÓN:
Migrar todos los usuarios de la tabla legacy a la nueva tabla.
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from gestion.models import UsuariosWebClientes, Cliente
from django.utils import timezone
from django.db import connection

print("=" * 80)
print("MIGRACIÓN: usuarios_web_clientes → usuario_portal")
print("=" * 80)

# Crear tabla usuario_portal si no existe
print("\n0️⃣  CREANDO TABLA usuario_portal SI NO EXISTE...")
print("-" * 80)

with connection.cursor() as cursor:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios_portal (
            ID_Usuario_Portal INT AUTO_INCREMENT PRIMARY KEY,
            ID_Cliente INT NOT NULL,
            Email VARCHAR(255) NOT NULL UNIQUE,
            Password_Hash VARCHAR(255) NOT NULL,
            Email_Verificado BOOLEAN NOT NULL DEFAULT 0,
            Fecha_Registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            Ultimo_Acceso DATETIME NULL,
            Activo BOOLEAN NOT NULL DEFAULT 1,
            Creado_En DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            Actualizado_En DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            
            CONSTRAINT fk_usuarios_portal_cliente 
                FOREIGN KEY (ID_Cliente) 
                REFERENCES clientes(ID_Cliente)
                ON DELETE CASCADE,
            
            INDEX idx_usuarios_portal_cliente (ID_Cliente),
            INDEX idx_usuarios_portal_email (Email),
            INDEX idx_usuarios_portal_activo (Activo)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """)
    print("✓ Tabla usuarios_portal creada/verificada")

# Ahora importar el modelo
from gestion.models import UsuarioPortal

# Verificar estado actual
print("\n1️⃣  VERIFICANDO ESTADO ACTUAL...")
print("-" * 80)

try:
    count_web = UsuariosWebClientes.objects.count()
    print(f"✓ usuarios_web_clientes: {count_web} registros")
except Exception as e:
    print(f"✗ Error al leer usuarios_web_clientes: {e}")
    count_web = 0

try:
    count_portal = UsuarioPortal.objects.count()
    print(f"✓ usuario_portal: {count_portal} registros")
except Exception as e:
    print(f"✗ Error al leer usuario_portal: {e}")
    count_portal = 0

if count_web == 0:
    print("\n⚠️  No hay usuarios en usuarios_web_clientes para migrar")
    print("   Nada que hacer.")
    exit(0)

# Procesar migración
print(f"\n2️⃣  MIGRANDO {count_web} USUARIO(S)...")
print("-" * 80)

migrados = 0
errores = 0
ya_existian = 0

for usuario_web in UsuariosWebClientes.objects.all():
    try:
        # Obtener el cliente
        cliente = usuario_web.id_cliente
        
        # Verificar si ya existe en usuario_portal
        if UsuarioPortal.objects.filter(cliente=cliente).exists():
            print(f"⚠️  Usuario para cliente {cliente.id_cliente} ya existe en portal")
            ya_existian += 1
            continue
        
        # Crear email (si no tiene uno)
        email = f'{usuario_web.usuario}@cantinatita.local'
        
        # Crear usuario en portal
        usuario_portal = UsuarioPortal.objects.create(
            cliente=cliente,
            email=email,
            password_hash=usuario_web.contrasena_hash,
            email_verificado=True,  # Asumir verificado si viene de sistema legacy
            fecha_registro=timezone.now(),
            ultimo_acceso=usuario_web.ultimo_acceso or timezone.now(),
            activo=usuario_web.activo if usuario_web.activo is not None else True
        )
        
        print(f"✓ Migrado: {usuario_web.usuario} → {email}")
        print(f"  Cliente ID: {cliente.id_cliente}")
        print(f"  Portal ID: {usuario_portal.id_usuario_portal}")
        migrados += 1
        
    except Exception as e:
        print(f"✗ Error migrando usuario {usuario_web.usuario}: {e}")
        errores += 1

# Resumen
print("\n3️⃣  RESUMEN DE MIGRACIÓN")
print("-" * 80)
print(f"✓ Usuarios migrados exitosamente:  {migrados}")
print(f"⚠️  Usuarios que ya existían:        {ya_existian}")
print(f"✗ Errores durante migración:       {errores}")
print(f"📊 Total procesados:                {count_web}")

# Verificar resultado final
count_portal_final = UsuarioPortal.objects.count()
print(f"\n✓ Total en usuario_portal ahora:    {count_portal_final}")

if migrados > 0:
    print("\n4️⃣  SIGUIENTE PASO")
    print("-" * 80)
    print("⚠️  IMPORTANTE: Verificar que todo el código use el modelo UsuarioPortal")
    print("")
    print("Comandos para verificar:")
    print("  grep -r 'UsuariosWebClientes' gestion/")
    print("  grep -r 'usuarios_web_clientes' gestion/")
    print("")
    print("Cuando estés seguro que ya no se usa usuarios_web_clientes:")
    print("  1. Comentar el modelo en gestion/models.py")
    print("  2. Crear migración: python manage.py makemigrations")
    print("  3. Aplicar: python manage.py migrate")
    print("  4. O directamente: DROP TABLE usuarios_web_clientes;")

print("\n" + "=" * 80)
print("MIGRACIÓN COMPLETADA")
print("=" * 80)
