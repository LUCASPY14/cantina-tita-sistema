# Guía para Crear las Vistas MySQL

## 📋 Contenido

Este directorio contiene los scripts SQL para crear las vistas necesarias del sistema.

## 🎯 Vistas Incluidas

### 1. **v_saldo_clientes**
- **Propósito:** Muestra el saldo actual de cuenta corriente de cada cliente
- **Campos:**
  - `ID_Cliente`, `nombre_completo`, `tipo_cliente`
  - `saldo_actual` - Suma de cargos menos abonos
  - `ultima_actualizacion` - Fecha del último movimiento
  - `total_movimientos` - Cantidad de transacciones
- **Filtro:** Solo clientes con saldo pendiente (≠ 0)

### 2. **v_stock_alerta**
- **Propósito:** Productos con stock bajo o agotado
- **Campos:**
  - `ID_Producto`, `producto`, `categoria`
  - `Stock_Actual`, `Stock_Minimo`, `cantidad_faltante`
  - `nivel_alerta` - AGOTADO / CRÍTICO / BAJO
- **Filtro:** Solo productos donde `Stock_Actual <= Stock_Minimo`
- **Orden:** Por nivel de criticidad

## 🚀 Método 1: PowerShell Script (Recomendado)

```powershell
# Ejecutar desde el directorio raíz del proyecto
.\crear_vistas_mysql.ps1
```

Te pedirá la contraseña de MySQL y creará las vistas automáticamente.

## 🔧 Método 2: MySQL Workbench o phpMyAdmin

1. Abre MySQL Workbench o phpMyAdmin
2. Selecciona la base de datos `cantinatitadb`
3. Abre el archivo `sql/crear_vistas.sql`
4. Ejecuta todo el contenido del archivo
5. Verifica que aparezcan las vistas en el explorador de objetos

## 💻 Método 3: Línea de Comandos MySQL

```bash
# Windows PowerShell
Get-Content sql\crear_vistas.sql | mysql -u root -p cantinatitadb

# Linux/Mac
mysql -u root -p cantinatitadb < sql/crear_vistas.sql
```

## ✅ Verificar Creación

Ejecuta en MySQL:

```sql
-- Ver vistas creadas
SHOW FULL TABLES WHERE Table_type = 'VIEW';

-- Probar vista de saldos
SELECT * FROM v_saldo_clientes LIMIT 5;

-- Probar vista de stock
SELECT * FROM v_stock_alerta LIMIT 5;
```

## 🔄 Después de Crear las Vistas

1. **Descomentar modelos Django:**
   - Abrir `gestion/models.py`
   - Buscar las secciones comentadas:
     - `# class VistaStockAlerta`
     - `# class VistaSaldoClientes`
   - Descomentar ambas clases completas

2. **Descomentar admin Django:**
   - Abrir `gestion/admin.py`
   - Descomentar imports y registros de admin

3. **Reiniciar servidor:**
   ```powershell
   python manage.py check
   python manage.py runserver
   ```

## 🔍 Uso en el Sistema

### Consultar Saldos Pendientes
```python
from gestion.models import VistaSaldoClientes

# Clientes con deuda
deudores = VistaSaldoClientes.objects.filter(saldo_actual__gt=0)

# Cliente con mayor deuda
mayor_deuda = VistaSaldoClientes.objects.order_by('-saldo_actual').first()
```

### Consultar Stock Bajo
```python
from gestion.models import VistaStockAlerta

# Todos los productos con stock bajo
alertas = VistaStockAlerta.objects.all()

# Solo productos agotados
agotados = VistaStockAlerta.objects.filter(nivel_alerta='AGOTADO')

# Productos críticos
criticos = VistaStockAlerta.objects.filter(nivel_alerta='CRÍTICO')
```

## 🛠️ Troubleshooting

### Error: "Access denied"
- Verifica usuario y contraseña MySQL
- Asegúrate de tener permisos para crear vistas

### Error: "Table doesn't exist"
- Verifica que todas las tablas existan en la BD
- Revisa nombres de tablas (case-sensitive en Linux)

### Error: "Unknown database"
- Verifica que la base de datos `cantinatitadb` exista
- Ajusta el nombre en los scripts si es diferente

## 📝 Notas Importantes

- Las vistas son **solo lectura** (no se pueden modificar desde Django)
- Se actualizan automáticamente cuando cambian los datos base
- Usar `managed = False` en los modelos Django
- No requieren migraciones

## 🆘 Soporte

Si encuentras problemas:
1. Verifica que MySQL esté corriendo
2. Revisa los logs de MySQL
3. Confirma permisos del usuario
4. Verifica nombres de tablas y columnas

---

**Fecha de creación:** 20/11/2025  
**Sistema:** Cantina Tita  
**Base de datos:** MySQL 8.0.44
