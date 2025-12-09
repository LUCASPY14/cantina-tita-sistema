import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection

def crear_tablas_seguridad_avanzada():
    """Crear tablas adicionales para seguridad avanzada"""
    print("🔐 Creando tablas de seguridad avanzada...")
    
    with connection.cursor() as cursor:
        # Tabla intentos_2fa
        print("Creando intentos_2fa...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS intentos_2fa (
                id_intento INT AUTO_INCREMENT PRIMARY KEY,
                usuario VARCHAR(100) NOT NULL,
                tipo_usuario ENUM('ADMIN', 'CAJERO', 'CLIENTE_WEB') NOT NULL,
                ip_address VARCHAR(45),
                ciudad VARCHAR(100),
                pais VARCHAR(100),
                codigo_ingresado VARCHAR(10) COMMENT 'Código que intentó usar (hasheado)',
                exitoso BOOLEAN DEFAULT FALSE,
                tipo_codigo ENUM('TOTP', 'BACKUP') COMMENT 'Tipo de código usado',
                fecha_intento DATETIME DEFAULT CURRENT_TIMESTAMP,
                
                INDEX idx_usuario (usuario),
                INDEX idx_fecha (fecha_intento),
                INDEX idx_exitoso (exitoso)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
            COMMENT='Registro de intentos de verificación 2FA'
        """)
        print("✅ Tabla intentos_2fa creada")
        
        # Tabla renovaciones_sesion
        print("Creando renovaciones_sesion...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS renovaciones_sesion (
                id_renovacion INT AUTO_INCREMENT PRIMARY KEY,
                usuario VARCHAR(100) NOT NULL,
                session_key_anterior VARCHAR(255),
                session_key_nuevo VARCHAR(255),
                ip_address VARCHAR(45),
                user_agent TEXT,
                fecha_renovacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                
                INDEX idx_usuario (usuario),
                INDEX idx_fecha (fecha_renovacion)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
            COMMENT='Auditoría de renovaciones de tokens de sesión'
        """)
        print("✅ Tabla renovaciones_sesion creada")
        
        # Verificar conteos
        cursor.execute("SELECT COUNT(*) FROM intentos_2fa")
        count_2fa = cursor.fetchone()[0]
        print(f"📊 intentos_2fa: {count_2fa} registros")
        
        cursor.execute("SELECT COUNT(*) FROM renovaciones_sesion")
        count_renov = cursor.fetchone()[0]
        print(f"📊 renovaciones_sesion: {count_renov} registros")
    
    print("✅ Proceso completado!")

if __name__ == '__main__':
    crear_tablas_seguridad_avanzada()
