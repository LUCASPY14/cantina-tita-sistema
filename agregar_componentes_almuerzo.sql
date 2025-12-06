-- Simplificar tipos_almuerzo: Solo "Almuerzo Completo"
USE cantina_tita;

-- Agregar campos de componentes (son fijos para el único tipo)
ALTER TABLE tipos_almuerzo
ADD COLUMN Incluye_Plato_Principal BOOLEAN DEFAULT TRUE AFTER Precio_Unitario,
ADD COLUMN Incluye_Postre BOOLEAN DEFAULT TRUE AFTER Incluye_Plato_Principal,
ADD COLUMN Incluye_Bebida BOOLEAN DEFAULT TRUE AFTER Incluye_Postre;

-- Desactivar todos los tipos excepto "Almuerzo Completo"
UPDATE tipos_almuerzo 
SET Activo = FALSE
WHERE Nombre != 'Almuerzo Completo';

-- Configurar el único tipo activo con todos los componentes
UPDATE tipos_almuerzo 
SET 
    Incluye_Plato_Principal = TRUE,
    Incluye_Postre = TRUE,
    Incluye_Bebida = TRUE,
    Descripcion = 'Plato principal + Postre + Jugo'
WHERE Nombre = 'Almuerzo Completo';

-- Verificar configuración
SELECT 
    ID_Tipo_Almuerzo,
    Nombre,
    Descripcion,
    Precio_Unitario,
    Incluye_Plato_Principal,
    Incluye_Postre,
    Incluye_Bebida,
    Activo
FROM tipos_almuerzo
ORDER BY Activo DESC, ID_Tipo_Almuerzo;

-- Nota: El precio se puede modificar directamente en la tabla o desde el admin de Django
-- El nuevo precio se aplica automáticamente a nuevos registros
-- Los registros históricos mantienen el precio con el que fueron registrados
