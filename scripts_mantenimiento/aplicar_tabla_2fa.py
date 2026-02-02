import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection

def crear_tabla_2fa():
    """Crea la tabla de autenticación 2FA"""
    print("🔐 Creando tabla de autenticación 2FA...")
    
    sql_create = """
    CREATE TABLE IF NOT EXISTS autenticacion_2fa (
        id_2fa INT AUTO_INCREMENT PRIMARY KEY,
        usuario VARCHAR(100) NOT NULL,
        tipo_usuario ENUM('ADMIN', 'CAJERO', 'CLIENTE_WEB') NOT NULL,
        secret_key VARCHAR(32) NOT NULL COMMENT 'Clave secreta TOTP codificada en Base32',
        backup_codes TEXT COMMENT 'Códigos de respaldo JSON (array de strings hasheados)',
        habilitado BOOLEAN DEFAULT FALSE COMMENT 'Si el usuario tiene 2FA activo',
        fecha_activacion DATETIME DEFAULT NULL COMMENT 'Cuando se activó por primera vez',
        ultima_verificacion DATETIME DEFAULT NULL COMMENT 'Último uso exitoso del código',
        fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
        
        UNIQUE KEY idx_usuario_tipo (usuario, tipo_usuario),
        INDEX idx_habilitado (habilitado)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
    COMMENT='Almacena configuración de 2FA para usuarios'
    """
    
    with connection.cursor() as cursor:
        cursor.execute(sql_create)
        print("✅ Tabla autenticacion_2fa creada")
        
        # Verificar
        cursor.execute("SELECT COUNT(*) FROM autenticacion_2fa")
        count = cursor.fetchone()[0]
        print(f"📊 Tabla autenticacion_2fa: {count} registros")
    
    print("✅ Proceso completado!")

if __name__ == '__main__':
    crear_tabla_2fa()
