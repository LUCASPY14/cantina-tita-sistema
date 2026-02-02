"""
Crear tablas de análisis de patrones directamente
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection

print("🔍 Creando tablas de análisis de patrones...\n")

sqls = [
    # Patrones de acceso
    """
    CREATE TABLE IF NOT EXISTS patrones_acceso (
        ID_Patron INT AUTO_INCREMENT PRIMARY KEY,
        Usuario VARCHAR(100) NOT NULL,
        Tipo_Usuario ENUM('EMPLEADO', 'CLIENTE_WEB', 'ADMIN') NOT NULL,
        IP_Address VARCHAR(45) NOT NULL,
        Horario_Inicio TIME,
        Horario_Fin TIME,
        Dias_Semana VARCHAR(50),
        Primera_Deteccion DATETIME NOT NULL,
        Ultima_Deteccion DATETIME NOT NULL,
        Frecuencia_Accesos INT DEFAULT 1,
        Es_Habitual BOOLEAN DEFAULT FALSE,
        INDEX idx_usuario (Usuario),
        INDEX idx_ip (IP_Address),
        INDEX idx_es_habitual (Es_Habitual)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    
    # Anomalías detectadas
    """
    CREATE TABLE IF NOT EXISTS anomalias_detectadas (
        ID_Anomalia INT AUTO_INCREMENT PRIMARY KEY,
        Usuario VARCHAR(100) NOT NULL,
        Tipo_Anomalia ENUM('IP_NUEVA', 'HORARIO_INUSUAL', 'MULTIPLES_SESIONES', 'UBICACION_SOSPECHOSA') NOT NULL,
        IP_Address VARCHAR(45),
        Fecha_Deteccion DATETIME NOT NULL,
        Descripcion TEXT,
        Nivel_Riesgo ENUM('BAJO', 'MEDIO', 'ALTO') DEFAULT 'MEDIO',
        Notificado BOOLEAN DEFAULT FALSE,
        INDEX idx_usuario (Usuario),
        INDEX idx_tipo (Tipo_Anomalia),
        INDEX idx_fecha (Fecha_Deteccion),
        INDEX idx_notificado (Notificado)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    
    # Sesiones activas
    """
    CREATE TABLE IF NOT EXISTS sesiones_activas (
        ID_Sesion INT AUTO_INCREMENT PRIMARY KEY,
        Usuario VARCHAR(100) NOT NULL,
        Tipo_Usuario ENUM('EMPLEADO', 'CLIENTE_WEB', 'ADMIN') NOT NULL,
        Session_Key VARCHAR(255) UNIQUE NOT NULL,
        IP_Address VARCHAR(45),
        User_Agent TEXT,
        Fecha_Inicio DATETIME NOT NULL,
        Ultima_Actividad DATETIME NOT NULL,
        Activa BOOLEAN DEFAULT TRUE,
        INDEX idx_usuario (Usuario),
        INDEX idx_activa (Activa),
        INDEX idx_session_key (Session_Key)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
]

nombres = ['patrones_acceso', 'anomalias_detectadas', 'sesiones_activas']

with connection.cursor() as cursor:
    for i, sql in enumerate(sqls):
        nombre = nombres[i]
        try:
            print(f"Creando {nombre}...", end=" ")
            cursor.execute(sql)
            print("✅")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    connection.commit()
    
    print("\n📊 Verificando creación:")
    for nombre in nombres:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {nombre}")
            count = cursor.fetchone()[0]
            print(f"   ✅ {nombre} - {count} registros")
        except Exception as e:
            print(f"   ❌ {nombre} - Error: {e}")

print("\n✅ Proceso completado!")
