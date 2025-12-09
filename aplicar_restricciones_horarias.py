import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection

def crear_tabla_restricciones():
    """Crear tabla de restricciones horarias"""
    print("⏰ Creando tabla de restricciones horarias...")
    
    sql_create = """
    CREATE TABLE IF NOT EXISTS restricciones_horarias (
        id_restriccion INT AUTO_INCREMENT PRIMARY KEY,
        usuario VARCHAR(100) DEFAULT NULL COMMENT 'Usuario específico (NULL = aplica a tipo_usuario)',
        tipo_usuario ENUM('ADMIN', 'CAJERO', 'CLIENTE_WEB') NOT NULL,
        dia_semana ENUM('LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO', 'DOMINGO') NOT NULL,
        hora_inicio TIME NOT NULL COMMENT 'Hora de inicio permitida',
        hora_fin TIME NOT NULL COMMENT 'Hora de fin permitida',
        activo BOOLEAN DEFAULT TRUE COMMENT 'Si la restricción está activa',
        fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
        
        INDEX idx_usuario (usuario),
        INDEX idx_tipo_usuario (tipo_usuario),
        INDEX idx_activo (activo)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
    COMMENT='Define horarios permitidos para acceso al sistema'
    """
    
    with connection.cursor() as cursor:
        cursor.execute(sql_create)
        print("✅ Tabla restricciones_horarias creada")
        
        # Verificar
        cursor.execute("SELECT COUNT(*) FROM restricciones_horarias")
        count = cursor.fetchone()[0]
        print(f"📊 Tabla restricciones_horarias: {count} registros")
    
    print("✅ Proceso completado!")

if __name__ == '__main__':
    crear_tabla_restricciones()
