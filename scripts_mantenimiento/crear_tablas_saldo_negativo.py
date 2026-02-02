"""
Script para crear las tablas de autorización de saldo negativo
directamente en MySQL sin usar migraciones
"""

import mysql.connector
from mysql.connector import Error

def ejecutar_sql():
    try:
        # Conectar a la base de datos
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,  # Puerto de MySQL
            database='cantinatitadb',
            user='root',
            password='L01G05S33Vice.42'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            print("✅ Conectado a MySQL")
            
            # 1. Verificar si los campos ya existen en tarjetas
            cursor.execute("SHOW COLUMNS FROM tarjetas LIKE 'permite_saldo_negativo'")
            existe_campo = cursor.fetchone()
            
            if not existe_campo:
                print("\n📝 Agregando campos a tabla tarjetas...")
                
                sql_alter_tarjeta = """
                ALTER TABLE tarjetas 
                ADD COLUMN permite_saldo_negativo TINYINT(1) DEFAULT 0 COMMENT 'Indica si la tarjeta puede tener saldo negativo',
                ADD COLUMN limite_credito BIGINT DEFAULT 0 COMMENT 'Monto máximo de crédito (saldo negativo) permitido en guaraníes',
                ADD COLUMN notificar_saldo_bajo TINYINT(1) DEFAULT 1 COMMENT 'Enviar notificaciones cuando el saldo está bajo',
                ADD COLUMN ultima_notificacion_saldo DATETIME NULL COMMENT 'Fecha de la última notificación de saldo enviada'
                """
                
                cursor.execute(sql_alter_tarjeta)
                connection.commit()
                print("✅ Campos agregados a tabla tarjetas")
            else:
                print("ℹ️ Los campos ya existen en tabla tarjetas")
            
            # 2. Crear tabla autorizacion_saldo_negativo
            cursor.execute("SHOW TABLES LIKE 'autorizacion_saldo_negativo'")
            existe_tabla_autorizacion = cursor.fetchone()
            
            if not existe_tabla_autorizacion:
                print("\n📝 Creando tabla autorizacion_saldo_negativo...")
                
                sql_create_autorizacion = """
                CREATE TABLE autorizacion_saldo_negativo (
                    id_autorizacion BIGINT AUTO_INCREMENT PRIMARY KEY,
                    id_venta BIGINT NOT NULL COMMENT 'ID de la venta autorizada',
                    nro_tarjeta VARCHAR(255) NOT NULL COMMENT 'Número de tarjeta',
                    id_empleado_autoriza INT NOT NULL COMMENT 'ID del empleado que autoriza',
                    saldo_anterior BIGINT NOT NULL COMMENT 'Saldo antes de la venta',
                    monto_venta BIGINT NOT NULL COMMENT 'Monto de la venta',
                    saldo_resultante BIGINT NOT NULL COMMENT 'Saldo después de la venta (negativo)',
                    motivo VARCHAR(255) NOT NULL COMMENT 'Justificación de la autorización',
                    fecha_autorizacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Cuándo se autorizó',
                    fecha_regularizacion DATETIME NULL COMMENT 'Cuándo se regularizó el saldo negativo',
                    id_carga_regularizacion BIGINT NULL COMMENT 'ID de la recarga que regularizó',
                    regularizado TINYINT(1) DEFAULT 0 COMMENT 'Si el saldo negativo ya fue regularizado',
                    
                    CONSTRAINT fk_autorizacion_venta FOREIGN KEY (id_venta) 
                        REFERENCES ventas(ID_Venta) ON DELETE RESTRICT,
                    CONSTRAINT fk_autorizacion_tarjeta FOREIGN KEY (nro_tarjeta) 
                        REFERENCES tarjetas(Nro_Tarjeta) ON DELETE CASCADE,
                    CONSTRAINT fk_autorizacion_empleado FOREIGN KEY (id_empleado_autoriza) 
                        REFERENCES empleados(ID_Empleado) ON DELETE RESTRICT,
                    CONSTRAINT fk_autorizacion_carga FOREIGN KEY (id_carga_regularizacion) 
                        REFERENCES cargas_saldo(ID_Carga) ON DELETE SET NULL,
                        
                    INDEX idx_tarjeta_fecha (nro_tarjeta, fecha_autorizacion),
                    INDEX idx_regularizado (regularizado),
                    INDEX idx_empleado (id_empleado_autoriza)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                COMMENT='Registro de autorizaciones de ventas con saldo negativo'
                """
                
                cursor.execute(sql_create_autorizacion)
                connection.commit()
                print("✅ Tabla autorizacion_saldo_negativo creada")
            else:
                print("ℹ️ La tabla autorizacion_saldo_negativo ya existe")
            
            # 3. Crear tabla notificacion_saldo
            cursor.execute("SHOW TABLES LIKE 'notificacion_saldo'")
            existe_tabla_notificacion = cursor.fetchone()
            
            if not existe_tabla_notificacion:
                print("\n📝 Creando tabla notificacion_saldo...")
                
                sql_create_notificacion = """
                CREATE TABLE notificacion_saldo (
                    id_notificacion BIGINT AUTO_INCREMENT PRIMARY KEY,
                    nro_tarjeta VARCHAR(255) NOT NULL COMMENT 'Tarjeta a la que corresponde',
                    tipo_notificacion VARCHAR(50) NOT NULL COMMENT 'SALDO_BAJO, SALDO_NEGATIVO, SALDO_CRITICO, REGULARIZADO',
                    saldo_actual BIGINT NOT NULL COMMENT 'Saldo al momento de la notificación',
                    mensaje TEXT NOT NULL COMMENT 'Mensaje de la notificación',
                    enviada_email TINYINT(1) DEFAULT 0 COMMENT 'Si se envió por email',
                    enviada_sms TINYINT(1) DEFAULT 0 COMMENT 'Si se envió por SMS',
                    leida TINYINT(1) DEFAULT 0 COMMENT 'Si el usuario leyó la notificación',
                    email_destinatario VARCHAR(255) NULL COMMENT 'Email al que se envió',
                    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    fecha_envio DATETIME NULL COMMENT 'Cuándo se envió la notificación',
                    
                    CONSTRAINT fk_notificacion_tarjeta FOREIGN KEY (nro_tarjeta) 
                        REFERENCES tarjetas(Nro_Tarjeta) ON DELETE CASCADE,
                        
                    INDEX idx_tarjeta_tipo (nro_tarjeta, tipo_notificacion),
                    INDEX idx_leida (leida),
                    INDEX idx_fecha_creacion (fecha_creacion)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                COMMENT='Registro de notificaciones de saldo enviadas a padres'
                """
                
                cursor.execute(sql_create_notificacion)
                connection.commit()
                print("✅ Tabla notificacion_saldo creada")
            else:
                print("ℹ️ La tabla notificacion_saldo ya existe")
            
            # Verificar que todo se creó correctamente
            print("\n📊 Verificando estructura:")
            
            cursor.execute("SHOW COLUMNS FROM tarjetas LIKE '%permite_saldo_negativo%'")
            print(f"Campo permite_saldo_negativo: {'✅' if cursor.fetchone() else '❌'}")
            
            cursor.execute("SHOW TABLES LIKE 'autorizacion_saldo_negativo'")
            print(f"Tabla autorizacion_saldo_negativo: {'✅' if cursor.fetchone() else '❌'}")
            
            cursor.execute("SHOW TABLES LIKE 'notificacion_saldo'")
            print(f"Tabla notificacion_saldo: {'✅' if cursor.fetchone() else '❌'}")
            
            print("\n🎉 COMPLETADO: Tablas de saldo negativo creadas exitosamente")
            
    except Error as e:
        print(f"❌ Error al conectar a MySQL: {e}")
        return False
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("\n🔌 Conexión cerrada")
    
    return True

if __name__ == "__main__":
    ejecutar_sql()
