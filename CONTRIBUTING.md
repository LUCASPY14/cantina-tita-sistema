# 🤝 Guía de Contribución

Gracias por tu interés en contribuir al **Sistema de Gestión de Cantina**. Este documento te guiará a través del proceso de contribución.

---

## 📋 Tabla de Contenidos

- [Código de Conducta](#código-de-conducta)
- [Cómo Contribuir](#cómo-contribuir)
- [Configuración del Entorno](#configuración-del-entorno)
- [Proceso de Desarrollo](#proceso-de-desarrollo)
- [Estándares de Código](#estándares-de-código)
- [Testing](#testing)
- [Pull Requests](#pull-requests)
- [Reportar Bugs](#reportar-bugs)
- [Solicitar Features](#solicitar-features)

---

## 📜 Código de Conducta

Este proyecto se adhiere a un Código de Conducta. Al participar, se espera que mantengas este código. Por favor reporta comportamientos inaceptables a los maintainers.

Ver [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)

---

## 🚀 Cómo Contribuir

### 1. Fork del Repositorio

```bash
# Hacer fork en GitHub, luego clonar
git clone https://github.com/TU-USUARIO/cantina.git
cd cantina
```

### 2. Crear una Rama

```bash
# Crear rama desde develop
git checkout develop
git pull origin develop
git checkout -b feature/mi-nueva-feature

# O para bugs
git checkout -b fix/corregir-bug-xyz
```

**Convención de Nombres de Ramas:**
- `feature/nombre-descriptivo` - Nuevas características
- `fix/descripcion-bug` - Corrección de bugs
- `docs/tema` - Documentación
- `refactor/componente` - Refactorización
- `test/area` - Mejoras de testing
- `chore/tarea` - Tareas de mantenimiento

---

## ⚙️ Configuración del Entorno

### Opción 1: Docker (Recomendado)

```bash
# Copiar variables de entorno
cp .env.example .env

# Editar .env con tus configuraciones
nano .env

# Levantar servicios
make docker-up

# Ejecutar migraciones
make docker-migrate

# Acceder
# Django: http://localhost:8000
# Nginx: http://localhost
```

### Opción 2: Desarrollo Local

```bash
# 1. Backend
make setup

# O manualmente:
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
pip install -r backend/requirements.txt

# 2. Base de datos
# Asegúrate de tener MySQL 8.0 corriendo
mysql -u root -p
CREATE DATABASE cantina_titadb;

# 3. Migraciones
cd backend
python manage.py migrate
python manage.py createsuperuser

# 4. Frontend
cd frontend
npm install
npm run build

# 5. Ejecutar servidor
python backend/manage.py runserver
```

### Verificar Instalación

```bash
# Tests backend
make test

# Tests frontend
make test-frontend

# Tests E2E
make test-e2e

# Todas las verificaciones
make check
```

---

## 🔄 Proceso de Desarrollo

### 1. Desarrollo

```bash
# Crear/modificar código
# Seguir estándares de código (ver abajo)

# Ejecutar tests frecuentemente
make test

# Verificar linters
make lint

# Formatear código
make format
```

### 2. Commits

**Seguimos [Conventional Commits](https://www.conventionalcommits.org/):**

```bash
# Formato
<tipo>[scope opcional]: <descripción>

[cuerpo opcional]

[footer opcional]
```

**Tipos:**
- `feat`: Nueva característica
- `fix`: Corrección de bug
- `docs`: Documentación
- `style`: Formato (sin cambios de código)
- `refactor`: Refactorización
- `test`: Agregar/modificar tests
- `chore`: Tareas de mantenimiento
- `perf`: Mejora de performance

**Ejemplos:**

```bash
git commit -m "feat(pos): agregar búsqueda de productos por código de barras"
git commit -m "fix(ventas): corregir cálculo de impuestos en facturas"
git commit -m "docs: actualizar README con instrucciones de Docker"
git commit -m "test(api): agregar tests para endpoint de recargas"
git commit -m "refactor(models): simplificar lógica de cuenta corriente"
```

### 3. Push y Pull Request

```bash
# Push a tu fork
git push origin feature/mi-nueva-feature

# Crear Pull Request en GitHub
# Usar la plantilla de PR
```

---

## 📝 Estándares de Código

### Python (Backend)

**Seguimos PEP 8 y Django Best Practices:**

```python
# ✅ BUENO
from decimal import Decimal
from django.db import models


class Producto(models.Model):
    """Modelo de Producto con validaciones."""
    
    nombre = models.CharField(
        max_length=200,
        help_text="Nombre del producto"
    )
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre
    
    def clean(self):
        """Validaciones personalizadas."""
        if self.precio <= 0:
            raise ValidationError("Precio debe ser mayor a 0")


# ❌ MALO
class producto(models.Model):  # Nombre en minúscula
    nombre=models.CharField(max_length=200)  # Sin espacios
    precio=models.DecimalField(max_digits=10,decimal_places=2)  # Sin espacios
    # Sin docstrings
    # Sin validaciones
    # Sin __str__
```

**Herramientas:**

```bash
# Formateo automático
make format  # black + isort

# Linting
make lint  # flake8 + pylint

# Type checking
mypy backend/gestion
```

**Reglas:**
- ✅ Usar type hints en funciones
- ✅ Docstrings en clases y funciones públicas
- ✅ Max 88 caracteres por línea (black)
- ✅ Imports ordenados (isort)
- ✅ Nombres descriptivos (no `x`, `temp`, `data`)
- ❌ No usar `import *`
- ❌ No hardcodear valores (usar settings)

### TypeScript (Frontend)

**Seguimos Airbnb Style Guide:**

```typescript
// ✅ BUENO
interface Product {
  id: number
  name: string
  price: number
  stock: number
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('es-PY', {
    style: 'currency',
    currency: 'PYG',
    minimumFractionDigits: 0
  }).format(value)
}

class ProductService {
  private baseUrl: string
  
  constructor(baseUrl: string) {
    this.baseUrl = baseUrl
  }
  
  async getProducts(): Promise<Product[]> {
    const response = await fetch(`${this.baseUrl}/productos/`)
    return response.json()
  }
}

// ❌ MALO
function format(v) {  // Sin tipos
  return v.toString()  // Sin lógica
}

var x = 5  // Usar const/let
```

**Herramientas:**

```bash
# Type checking
npm run typecheck

# Linting
npm run lint

# Formateo
npm run format  # prettier
```

### CSS/Tailwind

```html
<!-- ✅ BUENO: Clases semánticas, responsive -->
<div class="flex flex-col gap-4 p-6 bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow md:flex-row">
  <h2 class="text-2xl font-bold text-gray-800">Título</h2>
</div>

<!-- ❌ MALO: Inline styles, no responsive -->
<div style="display: flex; padding: 24px;">
  <h2 style="font-size: 24px;">Título</h2>
</div>
```

---

## 🧪 Testing

**Cobertura mínima: 70%**

### Backend (Pytest)

```python
# backend/gestion/tests/test_models.py
import pytest
from decimal import Decimal
from gestion.models import Producto


@pytest.mark.django_db
class TestProductoModel:
    """Tests para modelo Producto."""
    
    def test_crear_producto_valido(self, categoria_producto):
        """Test: Crear producto con datos válidos."""
        producto = Producto.objects.create(
            nombre='Test Producto',
            categoria=categoria_producto,
            precio_venta=Decimal('5000.00'),
            stock_actual=100
        )
        
        assert producto.id is not None
        assert producto.nombre == 'Test Producto'
        assert producto.precio_venta == Decimal('5000.00')
    
    def test_precio_no_negativo(self):
        """Test: Precio no puede ser negativo."""
        with pytest.raises(ValidationError):
            producto = Producto(
                nombre='Test',
                precio_venta=Decimal('-100.00')
            )
            producto.full_clean()
```

**Ejecutar:**

```bash
# Todos los tests
pytest

# Solo unitarios
pytest -m unit

# Con coverage
pytest --cov

# Específico
pytest backend/gestion/tests/test_models.py::TestProductoModel::test_crear_producto_valido
```

### Frontend (Vitest)

```typescript
// frontend/src/tests/utils.test.ts
import { describe, it, expect } from 'vitest'
import { formatCurrency } from '@/utils/formatters'

describe('formatCurrency', () => {
  it('formatea guaraníes correctamente', () => {
    expect(formatCurrency(5000)).toBe('₲ 5.000')
  })
  
  it('maneja cero', () => {
    expect(formatCurrency(0)).toBe('₲ 0')
  })
})
```

**Ejecutar:**

```bash
cd frontend
npm run test
npm run test:coverage
```

### E2E (Playwright)

```typescript
// e2e/venta.spec.ts
import { test, expect } from '@playwright/test'

test('crear venta exitosa', async ({ page }) => {
  await page.goto('/pos/')
  
  // Buscar producto
  await page.fill('input[type="search"]', 'coca cola')
  await page.click('button:has-text("Agregar")')
  
  // Completar venta
  await page.fill('input[name="efectivo"]', '10000')
  await page.click('button:has-text("Cobrar")')
  
  // Verificar
  await expect(page.locator('.alert-success')).toBeVisible()
})
```

**Ejecutar:**

```bash
npx playwright test
npx playwright test --ui
```

---

## 📤 Pull Requests

### Antes de Crear PR

```bash
# 1. Actualizar desde develop
git checkout develop
git pull origin develop
git checkout feature/mi-feature
git rebase develop

# 2. Tests pasan
make test-all

# 3. Linters limpios
make lint

# 4. Commits limpios
git log --oneline
```

### Plantilla de PR

```markdown
## Descripción
Breve descripción de los cambios

## Tipo de Cambio
- [ ] Bug fix
- [ ] Nueva feature
- [ ] Breaking change
- [ ] Documentación

## Testing
- [ ] Tests unitarios agregados/actualizados
- [ ] Tests E2E agregados/actualizados
- [ ] Tests pasan localmente
- [ ] Coverage >70%

## Checklist
- [ ] Código sigue guía de estilo
- [ ] Documentación actualizada
- [ ] No hay warnings de linters
- [ ] Commits siguen Conventional Commits
- [ ] PR contra rama `develop`

## Screenshots (si aplica)
[Agregar screenshots]

## Issues Relacionados
Closes #123
```

### Proceso de Review

1. **Automated Checks:**
   - ✅ Tests CI/CD pasan
   - ✅ Coverage >70%
   - ✅ No linting errors
   - ✅ Build exitoso

2. **Code Review:**
   - Al menos 1 aprobación de maintainer
   - Todos los comentarios resueltos
   - No conflicts con develop

3. **Merge:**
   - Squash and merge (preferido)
   - Merge commit (si es feature grande)
   - Rebase and merge (si commits son limpios)

---

## 🐛 Reportar Bugs

### Antes de Reportar

- ✅ Busca en issues existentes
- ✅ Verifica que sea reproducible
- ✅ Usa la última versión

### Template de Bug Report

```markdown
**Descripción del Bug**
Descripción clara del problema

**Para Reproducir**
1. Ir a '...'
2. Click en '...'
3. Ver error

**Comportamiento Esperado**
Qué debería pasar

**Screenshots**
[Si aplica]

**Entorno:**
- OS: [e.g. Windows 11]
- Browser: [e.g. Chrome 120]
- Python: [e.g. 3.12]
- Django: [e.g. 5.2.8]

**Logs**
```
Paste logs aquí
```

**Información Adicional**
Contexto adicional
```

---

## ✨ Solicitar Features

### Template de Feature Request

```markdown
**¿Está relacionado a un problema?**
Descripción del problema

**Describe la solución que te gustaría**
Solución propuesta

**Alternativas consideradas**
Otras soluciones evaluadas

**Información Adicional**
Contexto, mockups, referencias
```

---

## 📚 Recursos

### Documentación del Proyecto
- [README.md](README.md) - Introducción general
- [QUICKSTART.md](QUICKSTART.md) - Inicio rápido
- [API Documentation](http://localhost:8000/api/docs/) - Swagger UI
- [Sprint Docs](./docs/sprints/) - Documentación de sprints

### Tecnologías
- [Django 5.2](https://docs.djangoproject.com/en/5.2/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Vite 5](https://vitejs.dev/)
- [TypeScript 5](https://www.typescriptlang.org/)
- [Tailwind CSS 3](https://tailwindcss.com/)
- [Alpine.js 3](https://alpinejs.dev/)
- [Pytest](https://docs.pytest.org/)
- [Playwright](https://playwright.dev/)

### Guías de Estilo
- [PEP 8](https://pep8.org/)
- [Django Coding Style](https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/)
- [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

## 💬 Comunidad

### Contacto
- **Issues:** [GitHub Issues](https://github.com/tu-usuario/cantina/issues)
- **Discussions:** [GitHub Discussions](https://github.com/tu-usuario/cantina/discussions)
- **Email:** dev@cantina-sistema.com

### Maintainers
- [@tu-usuario](https://github.com/tu-usuario) - Lead Developer

---

## 🙏 Agradecimientos

Gracias a todos los [contributors](https://github.com/tu-usuario/cantina/graphs/contributors) que han ayudado a mejorar este proyecto.

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

Al contribuir, aceptas que tus contribuciones serán licenciadas bajo la misma licencia MIT.
