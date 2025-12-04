import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    # Crear la tabla Cta_Corriente
    print("Creando tabla Cta_Corriente...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Cta_Corriente (
            ID_Movimiento BIGINT AUTO_INCREMENT PRIMARY KEY,
            ID_Cliente INT NOT NULL,
            Fecha DATETIME NOT NULL,
            Tipo_Movimiento VARCHAR(50) NOT NULL,
            ID_Venta BIGINT NULL,
            ID_Pago BIGINT NULL,
            Monto_Cargo DECIMAL(12,2) DEFAULT 0,
            Monto_Abono DECIMAL(12,2) DEFAULT 0,
            Saldo_Acumulado DECIMAL(12,2) NOT NULL,
            Observaciones VARCHAR(255),
            INDEX idx_cliente (ID_Cliente),
            INDEX idx_fecha (Fecha),
            FOREIGN KEY (ID_Cliente) REFERENCES Clientes(ID_Cliente)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    print("✅ Tabla Cta_Corriente creada exitosamente")
