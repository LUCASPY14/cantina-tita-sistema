# 🧪 Testing y Calidad de Código - Sistema Cuenta Corriente

## 📋 Resumen

Este documento describe la infraestructura completa de testing y calidad de código implementada para el sistema de cuenta corriente.

---

## 🎯 Tests Implementados

### 1. Tests Unitarios (`gestion/tests.py`)

**14 tests** que verifican la lógica de negocio:

```bash
python manage.py test gestion
```

**Clases:**
- `VentasModelTest` (4 tests) - Modelo de ventas
- `ComprasModelTest` (2 tests) - Modelo de compras  
- `CuentaCorrienteViewsTest` (2 tests) - Vistas principales
- `EstadoPagoStandardTest` (2 tests) - Estándar MAYÚSCULAS
- `IntegridadDatosTest` (3 tests) - Integridad de datos
- `ReportesIntegrationTest` (1 test) - Integración reportes

### 2. Tests de Autenticación (`gestion/tests_auth.py`)

**12 tests** para autenticación y permisos:

```bash
python manage.py test gestion.tests_auth
```

**Clases:**
- `AuthenticationTestCase` (4 tests) - Login/permisos
- `ComprasDashboardViewTest` (2 tests) - Vista dashboard
- `DeudaProveedoresViewTest` (2 tests) - Vista deudas
- `PermissionsTestCase` (2 tests) - Permisos específicos
- `SessionDataTestCase` (2 tests) - Datos de sesión

### 3. Tests de Performance (`gestion/tests_performance.py`)

**7 tests** de optimización:

```bash
python manage.py test gestion.tests_performance --verbosity=2
```

**Pruebas:**
- Query N+1 vs `select_related()`
- Agregaciones (`Sum`, `Count`)
- `exists()` vs `count()`
- Operaciones bulk

---

## 🎨 Formularios con Validaciones

### Archivo: `gestion/forms.py`

**6 formularios** con validaciones integradas:

#### 1. VentasForm
```python
from gestion.forms import VentasForm

form = VentasForm(request.POST)
if form.is_valid():  # Validaciones automáticas
    venta = form.save()
```

**Validaciones:**
- ✅ Saldo ≤ Total
- ✅ Estado consistente con saldo
- ✅ Monto > 0

#### 2. ComprasForm
- ✅ Saldo ≤ Total
- ✅ PAGADA con saldo = 0

#### 3. PagosVentaForm
- ✅ Monto > 0

#### 4. AplicacionPagosVentasForm
- ✅ Monto no excede saldo
- ✅ Monto disponible del pago

#### 5. PagosProveedorForm
- ✅ Monto no excede saldo de compra

#### 6. Formularios de Filtros
- FiltroCuentaCorrienteClienteForm
- FiltroCuentaCorrienteProveedorForm

---

## 🔄 CI/CD con GitHub Actions

### Archivo: `.github/workflows/tests.yml`

**Pipeline automático** con 3 jobs:

### Job 1: Test
```yaml
- Python 3.10, 3.11, 3.12
- MySQL 8.0 para tests
- Django check
- Ejecución de tests
- Cobertura de código
- Upload a Codecov
```

### Job 2: Lint
```yaml
- flake8 (sintaxis)
- black (formato)
- isort (imports)
```

### Job 3: Security
```yaml
- bandit (análisis de seguridad)
- safety (vulnerabilidades)
```

**Activación:**
- Push a `main` o `develop`
- Pull requests

**Ver resultados:**
```
GitHub → Actions → Tests y CI/CD
```

---

## 📊 Cobertura de Código

### Script Automatizado

```bash
python run_coverage.py
```

**Genera:**
- `htmlcov/index.html` - Reporte interactivo
- `coverage.xml` - Para CI/CD
- Reporte en consola

### Comandos Manuales

```bash
# Ejecutar con cobertura
coverage run --source='gestion' manage.py test gestion

# Ver reporte
coverage report -m

# Generar HTML
coverage html

# Verificar mínimo (70%)
coverage report --fail-under=70
```

### Configuración: `.coveragerc`

```ini
[run]
source = gestion
omit = */migrations/*, */tests*.py

[report]
fail_under = 70
```

---

## 🚀 Comandos Rápidos

### Tests

```bash
# Todos los tests
python manage.py test gestion

# Tests específicos
python manage.py test gestion.tests.VentasModelTest
python manage.py test gestion.tests_auth
python manage.py test gestion.tests_performance

# Con verbosidad
python manage.py test gestion --verbosity=2

# Test específico
python manage.py test gestion.tests.VentasModelTest.test_venta_pendiente_inicial
```

### Cobertura

```bash
# Automatizado
python run_coverage.py

# Manual
coverage run --source='gestion' manage.py test gestion
coverage report
coverage html

# Abrir reporte HTML
# Windows: start htmlcov/index.html
# Linux/Mac: open htmlcov/index.html
```

### Linting

```bash
# Sintaxis
flake8 gestion

# Formato
black gestion --line-length=127

# Imports
isort gestion
```

### Seguridad

```bash
# Análisis
bandit -r gestion

# Vulnerabilidades
safety check
```

---

## 📈 Métricas de Calidad

| Métrica | Objetivo | Actual |
|---------|----------|--------|
| Tests Unitarios | ≥20 | ✅ 29 |
| Cobertura | >80% | 🎯 Por medir |
| Formularios | ≥5 | ✅ 6 |
| CI/CD Jobs | 3 | ✅ 3 |
| Django Check | 0 errores | ✅ 0 |

---

## 🎓 Mejores Prácticas

### Tests

✅ **Organización:**
```
gestion/
├── tests.py              # Tests unitarios
├── tests_auth.py         # Tests autenticación
└── tests_performance.py  # Tests performance
```

✅ **Estructura de Test:**
```python
class MiTestCase(TestCase):
    def setUp(self):
        """Configuración inicial"""
        pass
    
    def test_descripcion_clara(self):
        """Docstring explicando el test"""
        # Arrange
        # Act
        # Assert
        pass
```

### Formularios

✅ **Validaciones:**
```python
class MiForm(forms.ModelForm):
    def clean(self):
        """Validaciones a nivel de formulario"""
        cleaned_data = super().clean()
        
        # Validaciones personalizadas
        
        return cleaned_data
    
    def clean_campo(self):
        """Validación de campo específico"""
        valor = self.cleaned_data.get('campo')
        
        # Validar
        
        return valor
```

### CI/CD

✅ **Workflow:**
1. Commit → Push
2. GitHub Actions ejecuta
3. Tests automáticos
4. Linting y seguridad
5. Reporte de cobertura
6. ✅ o ❌ en PR

---

## 📚 Documentación

- [`docs/PROXIMOS_PASOS_IMPLEMENTADOS.md`](docs/PROXIMOS_PASOS_IMPLEMENTADOS.md) - Implementación completa
- [`docs/CUENTA_CORRIENTE.md`](docs/CUENTA_CORRIENTE.md) - Sistema cuenta corriente
- [`docs/MEJORAS_IMPLEMENTADAS.md`](docs/MEJORAS_IMPLEMENTADAS.md) - Mejoras prioridad media
- [`docs/ESTANDARES_CODIGO.md`](docs/ESTANDARES_CODIGO.md) - Estándares de código

---

## 🆘 Troubleshooting

### Tests fallan en CI/CD

**Problema:** Tests pasan local pero fallan en CI/CD

**Solución:**
```bash
# Verificar configuración de base de datos
# En .github/workflows/tests.yml
env:
  DB_NAME: test_cantina_titadb
  DB_USER: test_user
  DB_PASSWORD: test_password
```

### Cobertura baja

**Problema:** Cobertura < 70%

**Solución:**
```bash
# Ver líneas no cubiertas
coverage report -m

# Ver reporte HTML detallado
coverage html
# Abrir htmlcov/index.html
```

### Tests lentos

**Problema:** Tests toman mucho tiempo

**Solución:**
```bash
# Ejecutar tests de performance
python manage.py test gestion.tests_performance

# Optimizar queries (ver resultados)
```

---

## ✅ Checklist de Calidad

Antes de hacer commit:

- [ ] ✅ Tests pasan: `python manage.py test gestion`
- [ ] ✅ Django check: `python manage.py check`
- [ ] ✅ Linting: `flake8 gestion`
- [ ] ✅ Cobertura: `coverage report` (>70%)

Antes de hacer release:

- [ ] ✅ Todos los tests pasan
- [ ] ✅ Cobertura >80%
- [ ] ✅ CI/CD verde
- [ ] ✅ Seguridad OK: `bandit -r gestion`
- [ ] ✅ Dependencias actualizadas: `safety check`

---

## 🎉 Resultado Final

**Sistema de testing profesional implementado:**

- ✅ **29 tests automatizados**
- ✅ **6 formularios con validaciones**
- ✅ **CI/CD con 3 jobs**
- ✅ **Sistema de cobertura configurado**
- ✅ **0 errores en Django check**

**Próximo paso:**
```bash
python run_coverage.py
```

---

**Fecha:** 2 de diciembre de 2025  
**Estado:** ✅ Implementación completa  
**Mantenedor:** Equipo Cantina Tita
