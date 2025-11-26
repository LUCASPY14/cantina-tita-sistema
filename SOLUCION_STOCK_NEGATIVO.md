# 🔧 Solución: Permitir Stock Negativo en Productos Específicos

## 📋 Problema
Error al crear movimientos de stock: `(1644, 'Stock insuficiente para realizar la salida')`

## 💡 Causa
El sistema tiene un trigger en MySQL que impide ventas cuando no hay stock disponible. Esto es correcto para productos de inventario, pero para productos como **Almuerzo Completo** o **Almuerzo por Kilos** que se preparan bajo demanda, necesitamos permitir stock negativo.

## ✅ Solución

### Opción 1: Script Completo (RECOMENDADO)

Este script crea el campo y modifica el trigger correctamente.

**Archivo:** `sql/permitir_stock_negativo.sql`

**Pasos:**
1. Abrir **MySQL Workbench**
2. Conectar a la base de datos `cantinatitadb`
3. Abrir el archivo `sql/permitir_stock_negativo.sql`
4. Ejecutar todo el script (Ctrl+Shift+Enter)
5. Verificar que se muestren los productos con stock negativo permitido
6. Reiniciar el servidor Django

---

### Opción 2: Comandos Rápidos (Para pruebas inmediatas)

Si necesitas solucionar rápido para continuar trabajando:

```sql
-- 1. Agregar campo a productos
ALTER TABLE productos 
ADD COLUMN Permite_Stock_Negativo BOOLEAN DEFAULT FALSE;

-- 2. Configurar productos específicos
UPDATE productos 
SET Permite_Stock_Negativo = TRUE 
WHERE Descripcion LIKE '%Almuerzo%' OR Codigo LIKE 'ALM%';

-- 3. Eliminar trigger antiguo
DROP TRIGGER IF EXISTS trg_validar_stock_movimiento;

-- 4. Crear trigger nuevo (copiar del archivo permitir_stock_negativo.sql)
-- ⚠️ IMPORTANTE: Copiar el bloque DELIMITER $$ ... DELIMITER ; completo
```

---

## 🎯 Qué hace este cambio

### Antes:
- ❌ Todos los productos requieren stock positivo
- ❌ No se puede vender si no hay stock disponible
- ❌ Imposible registrar ventas de almuerzos preparados bajo demanda

### Después:
- ✅ Productos normales (snacks, bebidas): Requieren stock positivo
- ✅ Productos bajo demanda (almuerzos): Permiten stock negativo
- ✅ Puedes registrar la venta y el stock se actualiza a negativo
- ✅ El sistema indica que debes preparar/reponer ese producto

---

## 🔍 Verificación

### 1. Ver productos configurados:
```sql
SELECT 
    ID_Producto,
    Codigo,
    Descripcion,
    Permite_Stock_Negativo
FROM productos
WHERE Permite_Stock_Negativo = TRUE;
```

### 2. Probar movimiento de stock:
1. Ir a http://127.0.0.1:8000/admin/gestion/movimientosstock/add/
2. Seleccionar producto con stock negativo permitido (ej: Almuerzo Completo)
3. Registrar venta de 5 unidades
4. ✅ Debería guardarse correctamente, incluso si el stock queda negativo

### 3. Ver stock actualizado:
```sql
SELECT 
    p.Codigo,
    p.Descripcion,
    s.Stock_Actual,
    p.Permite_Stock_Negativo
FROM productos p
INNER JOIN stock_unico s ON p.ID_Producto = s.ID_Producto
WHERE p.Permite_Stock_Negativo = TRUE;
```

---

## 🛠️ Configurar más productos

Si necesitas permitir stock negativo en otros productos:

```sql
-- Por código específico
UPDATE productos 
SET Permite_Stock_Negativo = TRUE 
WHERE Codigo = 'TU_CODIGO';

-- Por descripción
UPDATE productos 
SET Permite_Stock_Negativo = TRUE 
WHERE Descripcion LIKE '%tu_palabra%';

-- Por categoría
UPDATE productos 
SET Permite_Stock_Negativo = TRUE 
WHERE ID_Categoria = (SELECT ID_Categoria FROM categorias WHERE Nombre = 'Almuerzos');
```

---

## 📝 Modelo Django Actualizado

El modelo `Producto` ahora incluye el campo:

```python
permite_stock_negativo = models.BooleanField(
    db_column='Permite_Stock_Negativo', 
    default=False, 
    help_text='Permite que el producto tenga stock negativo (ej: almuerzos preparados bajo demanda)'
)
```

Este campo aparecerá en el admin de Django al editar productos.

---

## ⚠️ Notas Importantes

1. **Reiniciar Django:** Después de ejecutar el script SQL, reinicia el servidor Django para que reconozca los cambios
2. **Stock Negativo != Sin Control:** El stock negativo indica que debes preparar/reponer el producto
3. **Reportes:** Monitorea regularmente los productos con stock negativo para planificar producción
4. **Backup:** Este cambio modifica la estructura de la BD, se recomienda hacer backup antes

---

## 🎯 Próximos Pasos

Después de aplicar la solución:

1. ✅ Ejecutar script SQL
2. ✅ Reiniciar servidor Django
3. ✅ Verificar productos configurados
4. ✅ Probar registro de venta con producto de almuerzo
5. ✅ Continuar con FASE 4 de la guía de inicio rápido

---

**Fecha:** 25/11/2025  
**Versión Django:** 5.2.8  
**Base de Datos:** MySQL 8.0.44
