-- Sistema de Tarjetas de Autorización para Administradores
-- USE cantina_tita;  -- Comentado, se usa la DB conectada

-- Crear tabla de tarjetas de autorización
CREATE TABLE IF NOT EXISTS tarjetas_autorizacion (
    ID_Tarjeta_Autorizacion INT AUTO_INCREMENT PRIMARY KEY,
    Codigo_Barra VARCHAR(50) NOT NULL UNIQUE,
    ID_Empleado INT NULL,
    Tipo_Autorizacion ENUM('ADMIN', 'SUPERVISOR', 'CAJERO') DEFAULT 'ADMIN',
    Puede_Anular_Almuerzos BOOLEAN DEFAULT TRUE,
    Puede_Anular_Ventas BOOLEAN DEFAULT TRUE,
    Puede_Anular_Recargas BOOLEAN DEFAULT TRUE,
    Puede_Modificar_Precios BOOLEAN DEFAULT FALSE,
    Activo BOOLEAN DEFAULT TRUE,
    Fecha_Creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    Fecha_Vencimiento DATE NULL,
    Observaciones TEXT NULL,
    FOREIGN KEY (ID_Empleado) REFERENCES empleados(ID_Empleado) ON DELETE SET NULL,
    INDEX idx_codigo_barra (Codigo_Barra),
    INDEX idx_activo (Activo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insertar tarjeta de administrador por defecto
INSERT INTO tarjetas_autorizacion 
(Codigo_Barra, Tipo_Autorizacion, Puede_Anular_Almuerzos, Puede_Anular_Ventas, Puede_Anular_Recargas, Puede_Modificar_Precios, Observaciones)
VALUES 
('ADMIN001', 'ADMIN', TRUE, TRUE, TRUE, TRUE, 'Tarjeta de autorización principal del administrador'),
('SUPER001', 'SUPERVISOR', TRUE, TRUE, TRUE, FALSE, 'Tarjeta de supervisores'),
('CAJERO001', 'CAJERO', FALSE, FALSE, FALSE, FALSE, 'Tarjeta de cajeros (sin permisos de anulación)');

-- Crear tabla de log de autorizaciones
CREATE TABLE IF NOT EXISTS log_autorizaciones (
    ID_Log BIGINT AUTO_INCREMENT PRIMARY KEY,
    ID_Tarjeta_Autorizacion INT NOT NULL,
    Codigo_Barra VARCHAR(50) NOT NULL,
    Tipo_Operacion ENUM('ANULAR_ALMUERZO', 'ANULAR_VENTA', 'ANULAR_RECARGA', 'MODIFICAR_PRECIO', 'OTRO') NOT NULL,
    ID_Registro_Afectado BIGINT NULL,
    Descripcion TEXT NULL,
    ID_Usuario INT NULL,
    Fecha_Hora DATETIME DEFAULT CURRENT_TIMESTAMP,
    IP_Origen VARCHAR(45) NULL,
    Resultado ENUM('EXITOSO', 'RECHAZADO', 'ERROR') DEFAULT 'EXITOSO',
    FOREIGN KEY (ID_Tarjeta_Autorizacion) REFERENCES tarjetas_autorizacion(ID_Tarjeta_Autorizacion) ON DELETE CASCADE,
    INDEX idx_fecha (Fecha_Hora),
    INDEX idx_tipo_operacion (Tipo_Operacion)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Verificar creación
SELECT 'Tabla tarjetas_autorizacion creada' AS status;
SELECT * FROM tarjetas_autorizacion;

SELECT 'Tabla log_autorizaciones creada' AS status;
