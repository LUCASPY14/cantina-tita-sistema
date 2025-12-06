-- Agregar campo de foto a la tabla hijos para identificación visual en POS
-- Fecha: 06/12/2025

USE cantinatitadb;

-- Agregar columna para almacenar la ruta de la foto
ALTER TABLE hijos 
ADD COLUMN Foto_Perfil VARCHAR(255) NULL COMMENT 'Ruta de la foto del hijo para identificación en POS',
ADD COLUMN Fecha_Foto DATETIME NULL COMMENT 'Fecha y hora de la última actualización de foto';

-- Verificar que se agregó correctamente
DESCRIBE hijos;

SELECT 'Campo Foto_Perfil agregado exitosamente a la tabla hijos' AS Resultado;
