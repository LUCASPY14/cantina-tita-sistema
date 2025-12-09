"""
Crear tablas de seguridad usando Django directamente
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection

print("🔒 Creando tablas de seguridad...\n")

# SQL para cada tabla
sqls = [
    # Tabla intentos_login
    """
    CREATE TABLE IF NOT EXISTS intentos_login (
        ID_Intento INT AUTO_INCREMENT PRIMARY KEY,
        Usuario VARCHAR(100) NOT NULL,
        IP_Address VARCHAR(45) NOT NULL,
        Fecha_Intento DATETIME NOT NULL,
        Exitoso BOOLEAN NOT NULL DEFAULT FALSE,
        Motivo_Fallo VARCHAR(100),
        INDEX idx_usuario_fecha (Usuario, Fecha_Intento),
        INDEX idx_ip_fecha (IP_Address, Fecha_Intento)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    
    # Tabla auditoria_operaciones
    """
    CREATE TABLE IF NOT EXISTS auditoria_operaciones (
        ID_Auditoria INT AUTO_INCREMENT PRIMARY KEY,
        Usuario VARCHAR(100) NOT NULL,
        Tipo_Usuario ENUM('EMPLEADO', 'CLIENTE_WEB', 'ADMIN') NOT NULL,
        ID_Usuario INT,
        Operacion VARCHAR(100) NOT NULL,
        Tabla_Afectada VARCHAR(100),
        ID_Registro INT,
        Descripcion TEXT,
        Datos_Anteriores JSON,
        Datos_Nuevos JSON,
        IP_Address VARCHAR(45),
        User_Agent TEXT,
        Fecha_Operacion DATETIME NOT NULL,
        Resultado ENUM('EXITOSO', 'FALLIDO') NOT NULL,
        Mensaje_Error TEXT,
        INDEX idx_usuario (Usuario),
        INDEX idx_fecha (Fecha_Operacion),
        INDEX idx_operacion (Operacion),
        INDEX idx_tabla (Tabla_Afectada, ID_Registro)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    
    # Tabla tokens_recuperacion
    """
    CREATE TABLE IF NOT EXISTS tokens_recuperacion (
        ID_Token INT AUTO_INCREMENT PRIMARY KEY,
        ID_Cliente INT NOT NULL,
        Token VARCHAR(64) NOT NULL UNIQUE,
        Fecha_Creacion DATETIME NOT NULL,
        Fecha_Expiracion DATETIME NOT NULL,
        Usado BOOLEAN NOT NULL DEFAULT FALSE,
        Fecha_Uso DATETIME NULL,
        IP_Solicitud VARCHAR(45),
        INDEX idx_token (Token),
        INDEX idx_cliente (ID_Cliente),
        INDEX idx_expiracion (Fecha_Expiracion),
        FOREIGN KEY (ID_Cliente) REFERENCES clientes(ID_Cliente)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    
    # Tabla bloqueos_cuenta
    """
    CREATE TABLE IF NOT EXISTS bloqueos_cuenta (
        ID_Bloqueo INT AUTO_INCREMENT PRIMARY KEY,
        Usuario VARCHAR(100) NOT NULL,
        Tipo_Usuario ENUM('EMPLEADO', 'CLIENTE_WEB', 'ADMIN') NOT NULL,
        Motivo VARCHAR(200),
        Fecha_Bloqueo DATETIME NOT NULL,
        Fecha_Desbloqueo DATETIME NULL,
        Activo BOOLEAN NOT NULL DEFAULT TRUE,
        Bloqueado_Por VARCHAR(100),
        INDEX idx_usuario_activo (Usuario, Activo),
        INDEX idx_fecha_desbloqueo (Fecha_Desbloqueo)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
]

nombres = ['intentos_login', 'auditoria_operaciones', 'tokens_recuperacion', 'bloqueos_cuenta']

with connection.cursor() as cursor:
    for i, sql in enumerate(sqls):
        nombre = nombres[i]
        try:
            print(f"Creando {nombre}...", end=" ")
            cursor.execute(sql)
            print("✅")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Commit
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
