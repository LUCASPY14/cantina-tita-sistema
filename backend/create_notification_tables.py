import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection

# SQL para crear las tablas de notificaciones
sql_commands = [
    # Crear tabla ConfiguracionNotificacionesSistema
    """
    CREATE TABLE `gestion_configuracionnotificacionessistema` (
        `id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `notif_ventas` bool NOT NULL,
        `notif_recargas` bool NOT NULL,
        `notif_stock` bool NOT NULL,
        `notif_sistema` bool NOT NULL,
        `push_habilitado` bool NOT NULL,
        `push_subscription` json NULL,
        `solo_criticas` bool NOT NULL,
        `sonido_habilitado` bool NOT NULL
    )
    """,
    
    # Crear tabla NotificacionSistema
    """
    CREATE TABLE `gestion_notificacionsistema` (
        `id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `titulo` varchar(200) NOT NULL,
        `mensaje` longtext NOT NULL,
        `tipo` varchar(20) NOT NULL,
        `prioridad` varchar(20) NOT NULL,
        `icono` varchar(50) NULL,
        `url` varchar(500) NULL,
        `leida` bool NOT NULL,
        `fecha_leida` datetime(6) NULL,
        `creada_en` datetime(6) NOT NULL,
        `expira_en` datetime(6) NULL
    )
    """,
    
    # Agregar foreign key usuario a ConfiguracionNotificacionesSistema
    """
    ALTER TABLE `gestion_configuracionnotificacionessistema` 
    ADD COLUMN `usuario_id` integer NOT NULL UNIQUE,
    ADD CONSTRAINT `gestion_configuracio_usuario_id_6d1d7edd_fk_auth_user` 
    FOREIGN KEY (`usuario_id`) REFERENCES `auth_user`(`id`)
    """,
    
    # Agregar foreign key usuario a NotificacionSistema
    """
    ALTER TABLE `gestion_notificacionsistema` 
    ADD COLUMN `usuario_id` integer NOT NULL,
    ADD CONSTRAINT `gestion_notificacionsistema_usuario_id_1c275da7_fk_auth_user_id` 
    FOREIGN KEY (`usuario_id`) REFERENCES `auth_user`(`id`)
    """,
    
    # Crear índices para NotificacionSistema
    """
    CREATE INDEX `gestion_not_usuario_992fdb_idx` 
    ON `gestion_notificacionsistema` (`usuario_id`, `creada_en` DESC)
    """,
    
    """
    CREATE INDEX `gestion_not_usuario_537bae_idx` 
    ON `gestion_notificacionsistema` (`usuario_id`, `leida`)
    """,
    
    """
    CREATE INDEX `gestion_not_tipo_425520_idx` 
    ON `gestion_notificacionsistema` (`tipo`, `creada_en` DESC)
    """
]

print("🔧 Creando tablas de notificaciones del sistema...")
print("=" * 60)

cursor = connection.cursor()

for i, sql in enumerate(sql_commands, 1):
    try:
        print(f"\n[{i}/{len(sql_commands)}] Ejecutando comando...")
        cursor.execute(sql)
        print(f"✅ Éxito")
    except Exception as e:
        print(f"❌ Error: {e}")
        if "already exists" in str(e).lower():
            print("   (La tabla/columna/índice ya existe, continuando...)")
        else:
            print("   ⚠️  Error crítico, abortando...")
            raise

print("\n" + "=" * 60)
print("✅ ¡Tablas de notificaciones creadas exitosamente!")
print("\n🔍 Verificando...")

# Verificar que las tablas existan
cursor.execute("SHOW TABLES LIKE 'gestion_notificacionsistema'")
if cursor.fetchone():
    print("✅ Tabla gestion_notificacionsistema creada")
    
    # Mostrar estructura
    cursor.execute("DESCRIBE gestion_notificacionsistema")
    print("\n   Columnas:")
    for row in cursor.fetchall():
        print(f"     - {row[0]} ({row[1]})")
else:
    print("❌ Tabla gestion_notificacionsistema NO encontrada")

cursor.execute("SHOW TABLES LIKE 'gestion_configuracionnotificacionessistema'")
if cursor.fetchone():
    print("\n✅ Tabla gestion_configuracionnotificacionessistema creada")
    
    # Mostrar estructura
    cursor.execute("DESCRIBE gestion_configuracionnotificacionessistema")
    print("\n   Columnas:")
    for row in cursor.fetchall():
        print(f"     - {row[0]} ({row[1]})")
else:
    print("❌ Tabla gestion_configuracionnotificacionessistema NO encontrada")

print("\n" + "=" * 60)
print("🎉 ¡Sistema de notificaciones listo para usar!")
