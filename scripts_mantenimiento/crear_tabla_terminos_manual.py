"""
Script para crear tabla aceptacion_terminos_saldo_negativo
directamente en MySQL, evitando conflictos con migraciones de Django
"""

import mysql.connector
from decouple import config
import sys

def crear_tabla_terminos():
    """Crea la tabla en MySQL directamente"""
    
    # Configuración de conexión
    db_config = {
        'host': config('DB_HOST', default='localhost'),
        'user': config('DB_USER', default='root'),
        'password': config('DB_PASSWORD'),
        'database': config('DB_NAME', default='cantitatitadb'),
        'port': config('DB_PORT', default=3306, cast=int)
    }
    
    print(f"Conectando a MySQL: {db_config['user']}@{db_config['host']}/{db_config['database']}...")
    
    try:
        # Conectar a MySQL
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # SQL para crear tabla
        sql_create = """
        CREATE TABLE IF NOT EXISTS `aceptacion_terminos_saldo_negativo` (
            `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
            `nro_tarjeta` VARCHAR(20) NOT NULL,
            `id_cliente` INT NOT NULL,
            `id_usuario_portal` INT NULL,
            `fecha_aceptacion` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            `ip_address` VARCHAR(45) NULL COMMENT 'IPv4 o IPv6',
            `user_agent` VARCHAR(500) NULL,
            `version_terminos` VARCHAR(20) NOT NULL DEFAULT '1.0',
            `contenido_aceptado` TEXT NOT NULL,
            `firma_digital` VARCHAR(500) NULL,
            `activo` TINYINT(1) NOT NULL DEFAULT 1,
            `revocado` TINYINT(1) NOT NULL DEFAULT 0,
            `fecha_revocacion` DATETIME NULL,
            
            -- Foreign Keys
            CONSTRAINT `fk_aceptacion_tarjeta` 
                FOREIGN KEY (`nro_tarjeta`) 
                REFERENCES `tarjetas` (`Nro_Tarjeta`) 
                ON DELETE CASCADE,
            
            CONSTRAINT `fk_aceptacion_cliente` 
                FOREIGN KEY (`id_cliente`) 
                REFERENCES `clientes` (`ID_Cliente`) 
                ON DELETE CASCADE,
            
            CONSTRAINT `fk_aceptacion_usuario` 
                FOREIGN KEY (`id_usuario_portal`) 
                REFERENCES `auth_user` (`id`) 
                ON DELETE SET NULL,
            
            -- Índices
            INDEX `idx_tarjeta_activo` (`nro_tarjeta`, `activo`),
            INDEX `idx_cliente` (`id_cliente`),
            INDEX `idx_fecha_aceptacion` (`fecha_aceptacion`),
            INDEX `idx_revocado` (`revocado`)
            
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        COMMENT='Registro de aceptación de términos legales para saldo negativo'
        """
        
        print("Ejecutando CREATE TABLE...")
        cursor.execute(sql_create)
        
        # Verificar que se creó
        cursor.execute("SHOW TABLES LIKE 'aceptacion_terminos_saldo_negativo'")
        result = cursor.fetchone()
        
        if result:
            print("✅ Tabla 'aceptacion_terminos_saldo_negativo' creada exitosamente")
            
            # Mostrar estructura
            cursor.execute("DESCRIBE aceptacion_terminos_saldo_negativo")
            print("\n📋 Estructura de la tabla:")
            for row in cursor.fetchall():
                print(f"  - {row[0]}: {row[1]}")
            
            conn.commit()
            return True
        else:
            print("❌ Error: la tabla no se creó")
            return False
            
    except mysql.connector.Error as e:
        print(f"❌ Error de MySQL: {e}")
        return False
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
            print("Conexión cerrada")


if __name__ == '__main__':
    print("=" * 70)
    print("CREAR TABLA: aceptacion_terminos_saldo_negativo")
    print("=" * 70)
    
    success = crear_tabla_terminos()
    
    if success:
        print("\n✅ ÉXITO: Tabla creada correctamente")
        print("\nPróximos pasos:")
        print("1. Ejecutar: python manage.py migrate gestion --fake 0008")
        print("2. Verificar: python manage.py showmigrations gestion")
        sys.exit(0)
    else:
        print("\n❌ FALLO: No se pudo crear la tabla")
        sys.exit(1)
