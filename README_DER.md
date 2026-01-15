# Generador de Diagramas Entidad-Relación (DER) - CantinatitaDB

Este paquete contiene scripts para generar diagramas ER completos de la base de datos **cantinatitadb** usando Python, SQLAlchemy y Graphviz.

## 📋 Requisitos Previos

### 1. Graphviz (Sistema)
Debe instalar Graphviz en su sistema operativo:

**Windows:**
- Descargar desde: https://graphviz.org/download/
- Instalar y agregar al PATH del sistema
- Verificar: `dot -V`

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install graphviz
```

**macOS:**
```bash
brew install graphviz
```

### 2. Python 3.8+
Verificar versión:
```bash
python --version
```

## 🚀 Instalación

### 1. Instalar dependencias de Python

```bash
pip install sqlalchemy pymysql graphviz python-decouple
```

O usar el archivo de requisitos:

```bash
pip install -r requirements_der.txt
```

### 2. Configurar variables de entorno

Asegúrese de tener un archivo `.env` en la raíz del proyecto con:

```env
DB_NAME=cantinatitadb
DB_USER=root
DB_PASSWORD=su_contraseña
DB_HOST=localhost
DB_PORT=3306
```

## 📊 Scripts Disponibles

### 1. `generar_der_completo.py`
Genera dos diagramas principales:
- **DER Lógico**: Muestra entidades y relaciones conceptuales
- **DER Físico**: Muestra todas las tablas con columnas, tipos de datos y constraints

**Uso:**
```bash
python generar_der_completo.py
```

**Salidas:**
- `diagramas_der/DER_Logico_Cantinatitadb.png`
- `diagramas_der/DER_Fisico_Cantinatitadb.png`
- `diagramas_der/estadisticas_bd.txt`

### 2. `generar_der_modular.py`
Genera diagramas agrupados por módulos funcionales:
- Clientes y Padres
- Hijos/Estudiantes
- Productos e Inventario
- Ventas y Transacciones
- Empleados y Seguridad
- Reportes y Comisiones
- Configuración

**Uso:**
```bash
python generar_der_modular.py
```

**Salidas:**
- `diagramas_der/DER_Modular_Cantinatitadb.png` (Completo con módulos)
- `diagramas_der/DER_Modulo_*.png` (Un diagrama por módulo)

## 📁 Estructura de Salida

```
diagramas_der/
├── DER_Logico_Cantinatitadb.png           # DER Lógico completo
├── DER_Fisico_Cantinatitadb.png           # DER Físico completo
├── DER_Modular_Cantinatitadb.png          # DER por módulos
├── DER_Modulo_Clientes_y_Padres.png       # Módulo individual
├── DER_Modulo_Hijos_Estudiantes.png       # Módulo individual
├── DER_Modulo_Productos_e_Inventario.png  # Módulo individual
├── DER_Modulo_Ventas_y_Transacciones.png  # Módulo individual
├── DER_Modulo_Empleados_y_Seguridad.png   # Módulo individual
├── DER_Modulo_Reportes_y_Comisiones.png   # Módulo individual
├── DER_Modulo_Configuracion.png           # Módulo individual
└── estadisticas_bd.txt                    # Estadísticas de la BD
```

## 🎨 Características de los Diagramas

### DER Lógico
- Vista de alto nivel de entidades y relaciones
- Muestra solo atributos clave
- Ideal para documentación general
- Relaciones con cardinalidad (crow's foot notation)

### DER Físico
- Vista detallada de todas las tablas
- Todas las columnas con tipos de datos
- Indicadores de NULL/NOT NULL
- Primary Keys (PK) y Foreign Keys (FK)
- Ideal para desarrollo y mantenimiento

### DER Modular
- Agrupa tablas por módulos funcionales
- Codificación por colores según módulo
- Vista organizada del sistema
- Facilita comprensión de subsistemas

## 🔍 Información Técnica

### Convenciones de Color

**DER Físico:**
- 🟨 Amarillo (#FFE5B4): Primary Keys
- 🟩 Verde (#C8E6C9): Foreign Keys
- ⬜ Blanco (#FFFFFF): Atributos normales
- 🔵 Azul (#1F4788): Encabezados de tabla

**DER Modular:**
- 🔵 Azul: Clientes y Padres
- 🟣 Morado: Hijos/Estudiantes
- 🟠 Naranja: Productos e Inventario
- 🟢 Verde: Ventas y Transacciones
- 🔴 Rojo: Empleados y Seguridad
- 🟣 Rosa: Reportes y Comisiones
- 🟢 Verde claro: Configuración

### Tipos de Relaciones

- **Crow's foot**: Relación uno a muchos (1:N)
- **Normal arrow**: Relación en DER físico
- Etiquetas muestran nombre de la columna FK

## 📈 Estadísticas Generadas

El archivo `estadisticas_bd.txt` incluye:
- Total de tablas en la base de datos
- Total de columnas
- Total de Primary Keys
- Total de Foreign Keys
- Total de índices
- Detalle por tabla

## 🛠️ Personalización

### Modificar colores
Edite el diccionario `COLORS` en los scripts:

```python
COLORS = {
    'entity_bg': '#E8F4F8',      # Fondo de entidades
    'entity_border': '#2E86AB',   # Borde de entidades
    'pk_bg': '#FFE5B4',          # Fondo de PKs
    'fk_bg': '#C8E6C9',          # Fondo de FKs
    # ...
}
```

### Modificar módulos
Edite el diccionario `MODULES` en `generar_der_modular.py`:

```python
MODULES = {
    'Nombre del Módulo': {
        'tables': ['tabla1', 'tabla2'],
        'color': '#HEXCOLOR',
        'border': '#HEXCOLOR'
    },
    # ...
}
```

### Cambiar formato de salida
Modifique el parámetro `format` en la creación del grafo:

```python
dot = graphviz.Digraph(
    format='png'  # Puede ser: png, svg, pdf, jpg
)
```

## 🐛 Solución de Problemas

### Error: "Graphviz not found"
- Verificar que Graphviz esté instalado: `dot -V`
- Verificar que esté en el PATH del sistema
- Reiniciar la terminal/IDE después de instalar

### Error: "Access denied for user"
- Verificar credenciales en el archivo `.env`
- Verificar que el usuario tenga permisos en la BD
- Verificar que el servicio MySQL esté corriendo

### Error: "Module not found: pymysql"
- Instalar dependencias: `pip install pymysql`
- Verificar el entorno virtual si está usando uno

### Diagramas muy grandes
- Usar los diagramas modulares en lugar del completo
- Generar diagramas individuales por módulo
- Ajustar parámetros de spacing en el código

## 📝 Ejemplo de Uso Completo

```bash
# 1. Instalar dependencias
pip install -r requirements_der.txt

# 2. Verificar Graphviz
dot -V

# 3. Configurar .env
echo "DB_PASSWORD=mi_password" >> .env

# 4. Generar todos los diagramas
python generar_der_completo.py
python generar_der_modular.py

# 5. Ver resultados
cd diagramas_der
dir  # Windows
ls   # Linux/Mac
```

## 📚 Referencias

- **SQLAlchemy**: https://www.sqlalchemy.org/
- **Graphviz**: https://graphviz.org/
- **PyMySQL**: https://pymysql.readthedocs.io/
- **Python Decouple**: https://pypi.org/project/python-decouple/

## 📄 Licencia

Este código es parte del proyecto Cantina Tita y está destinado para uso interno.

## 👥 Autor

Generado para el proyecto de gestión de cantina escolar - Cantina Tita
Fecha: Enero 2026
