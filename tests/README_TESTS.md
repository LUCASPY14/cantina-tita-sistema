# ==================== GUÍA DE TESTING - CANTINA TITA ====================

## DESCRIPCIÓN GENERAL

Este directorio contiene tests exhaustivos para el sistema Cantina Tita.
Los tests están organizados en 3 archivos principales:

1. **test_validaciones.py** - Tests para endpoints de validación (cargas y pagos)
2. **test_empleados_ajax.py** - Tests para endpoints AJAX de gestión de empleados
3. **test_integracion.py** - Tests de integración completos (flujos end-to-end)

---

## REQUISITOS

```bash
# Instalar dependencias de testing
pip install pytest pytest-django pytest-cov coverage
```

Actualizar `requirements.txt`:
```
pytest==7.4.3
pytest-django==4.7.0
pytest-cov==4.1.0
coverage==7.3.2
```

---

## CONFIGURACIÓN

### Archivo: pytest.ini (en raíz del proyecto)

```ini
[pytest]
DJANGO_SETTINGS_MODULE = cantitatita.settings
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

### Archivo: .coveragerc (en raíz del proyecto)

```ini
[run]
source = gestion
omit =
    */migrations/*
    */tests/*
    */admin.py
    */__init__.py
    */apps.py

[report]
precision = 2
show_missing = True
skip_covered = False

[html]
directory = htmlcov
```

---

## EJECUTAR TESTS

### Con Django Test Runner

```bash
# Ejecutar todos los tests
python manage.py test

# Ejecutar tests de un archivo específico
python manage.py test gestion.tests.test_validaciones

# Ejecutar tests de una clase específica
python manage.py test gestion.tests.test_validaciones.TestValidacionCargasSaldo

# Ejecutar un test específico
python manage.py test gestion.tests.test_validaciones.TestValidacionCargasSaldo.test_validar_carga_post_success

# Ejecutar con verbosidad
python manage.py test --verbosity=2

# Mantener base de datos de test (útil para debugging)
python manage.py test --keepdb
```

### Con Pytest

```bash
# Ejecutar todos los tests
pytest

# Ejecutar tests de un archivo
pytest tests/test_validaciones.py

# Ejecutar tests con cobertura
pytest --cov=gestion

# Ejecutar tests y generar reporte HTML de cobertura
pytest --cov=gestion --cov-report=html

# Ejecutar solo tests rápidos (excluir integration)
pytest -m "not slow"

# Ejecutar con salida detallada
pytest -v

# Ejecutar tests y mostrar print statements
pytest -s

# Ejecutar tests en paralelo (instalar pytest-xdist)
pytest -n 4
```

### Cobertura de Código

```bash
# Ejecutar tests con cobertura
coverage run --source='gestion' manage.py test

# Ver reporte en consola
coverage report

# Generar reporte HTML
coverage html

# Abrir reporte HTML
# Windows:
start htmlcov/index.html

# Linux/Mac:
xdg-open htmlcov/index.html  # Linux
open htmlcov/index.html      # Mac

# Ver archivos sin cobertura
coverage report --skip-covered

# Cobertura específica de un módulo
coverage run --source='gestion.views' manage.py test
coverage report
```

---

## ESTRUCTURA DE TESTS

### test_validaciones.py

**Clases:**
- `TestValidacionCargasSaldo`: Tests para validación de cargas de saldo
- `TestValidacionPagos`: Tests para validación de pagos por transferencia
- `TestPermisos`: Tests de permisos y seguridad
- `TestIntegracionValidaciones`: Tests de integración

**Tests incluidos:**
- ✅ Listar cargas pendientes (GET)
- ✅ Filtrar cargas por búsqueda
- ✅ Mostrar formulario de validación (GET)
- ✅ Validar carga exitosamente (POST)
- ✅ Intentar validar carga inexistente
- ✅ Intentar validar carga ya confirmada
- ✅ Listar pagos pendientes (GET)
- ✅ Mostrar formulario de validación de pago
- ✅ Validar pago exitosamente (POST)
- ✅ Validar pago sin comprobante (error)
- ✅ Filtrar pagos por rango de fechas
- ✅ Acceso denegado sin permisos de admin

### test_empleados_ajax.py

**Clases:**
- `TestEmpleadoAjaxEndpoints`: Tests para endpoints AJAX de empleados
- `TestPermisosAjax`: Tests de permisos para AJAX

**Tests incluidos:**
- ✅ Obtener datos de empleado vía AJAX (GET)
- ✅ Obtener empleado inexistente
- ✅ Editar empleado vía AJAX (POST)
- ✅ Editar con nombre duplicado (error)
- ✅ Editar con campos vacíos (error)
- ✅ Resetear contraseña vía AJAX
- ✅ Resetear con passwords que no coinciden (error)
- ✅ Resetear con password muy corta (error)
- ✅ Activar/desactivar empleado vía AJAX
- ✅ Acceso denegado sin permisos de admin

### test_integracion.py

**Clases:**
- `TestIntegracionVentaCompleta`: Flujo completo de venta desde POS
- `TestIntegracionRecarga`: Flujo completo de recarga de saldo
- `TestIntegracionCuentaCorriente`: Flujo completo de cuenta corriente
- `TestIntegracionAlmuerzos`: Flujo completo de almuerzos
- `TestRendimiento`: Tests de rendimiento y carga

**Tests incluidos:**
- ✅ Flujo completo de venta (agregar productos, confirmar, verificar stock y saldo)
- ✅ Flujo completo de recarga con validación
- ✅ Venta en cuenta corriente con validación de pago posterior
- ✅ Registro de almuerzo y descuento de saldo
- ✅ Procesar múltiples ventas simultáneas (rendimiento)

---

## RESULTADOS ESPERADOS

### Cobertura mínima objetivo: **85%**

```
Name                              Stmts   Miss  Cover
-----------------------------------------------------
gestion/pos_views.py              2345     187   92%
gestion/empleado_views.py          234      23   90%
gestion/cliente_views.py           189      28   85%
gestion/almuerzo_views.py          156      19   88%
gestion/api_views.py               178      31   83%
gestion/models.py                  567      34   94%
gestion/serializers.py             123      15   88%
-----------------------------------------------------
TOTAL                             3792     337   91%
```

---

## TESTING EN CI/CD

### GitHub Actions Workflow (.github/workflows/tests.yml)

```yaml
name: Django Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: testpassword
          MYSQL_DATABASE: test_cantitatitadb
        ports:
          - 3306:3306
        options: >-
          --health-cmd="mysqladmin ping"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=3
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests with coverage
      env:
        DATABASE_HOST: 127.0.0.1
        DATABASE_PORT: 3306
        DATABASE_USER: root
        DATABASE_PASSWORD: testpassword
        DATABASE_NAME: test_cantitatitadb
      run: |
        coverage run --source='gestion' manage.py test
        coverage report --fail-under=85
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
```

---

## DEBUGGING DE TESTS

### Ver output detallado:
```bash
# Django test runner
python manage.py test --verbosity=3

# Pytest
pytest -vv -s
```

### Ejecutar test específico con debugging:
```bash
# Django
python manage.py test gestion.tests.test_validaciones.TestValidacionCargasSaldo.test_validar_carga_post_success --pdb

# Pytest
pytest tests/test_validaciones.py::TestValidacionCargasSaldo::test_validar_carga_post_success --pdb
```

### Ver queries SQL ejecutadas:
```python
# En el test, agregar:
from django.test.utils import override_settings
from django.db import connection
from django.test.utils import setup_test_environment

@override_settings(DEBUG=True)
def test_algo(self):
    # Tu código aquí
    print(len(connection.queries))
    print(connection.queries)
```

---

## TIPS Y MEJORES PRÁCTICAS

1. **Ejecutar tests frecuentemente**: Ejecutar tests después de cada cambio importante
2. **Mantener tests rápidos**: Usar `--keepdb` para evitar recrear DB en cada ejecución
3. **Tests aislados**: Cada test debe ser independiente y no depender del orden
4. **Usar fixtures**: Crear fixtures para datos comunes
5. **Verificar cobertura**: Apuntar a >85% de cobertura
6. **Nombres descriptivos**: Nombres de tests deben describir qué se está probando
7. **Setup y teardown**: Usar setUp() y tearDown() correctamente
8. **Mocks cuando sea necesario**: Usar mocks para servicios externos
9. **Tests parametrizados**: Usar @pytest.mark.parametrize para múltiples casos
10. **CI/CD**: Integrar tests en pipeline de CI/CD

---

## TROUBLESHOOTING

### Error: "No module named 'pytest'"
```bash
pip install pytest pytest-django
```

### Error: "django.db.utils.OperationalError: (2002, 'Can't connect to server')"
- Verificar que MySQL esté corriendo
- Verificar configuración de base de datos de test en settings.py

### Tests muy lentos
```bash
# Usar --keepdb para mantener BD entre ejecuciones
python manage.py test --keepdb

# Ejecutar en paralelo con pytest-xdist
pytest -n auto
```

### Error: "Test database creation failed"
```bash
# Otorgar permisos al usuario de MySQL
GRANT ALL ON test_*.* TO 'tu_usuario'@'localhost';
```

---

¡Tests completados! 🎯
