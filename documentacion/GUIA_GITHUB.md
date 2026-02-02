# 🚀 Guía para Subir el Proyecto a GitHub

## ✅ Estado Actual

- ✅ Git inicializado
- ✅ Primer commit creado con 37 archivos
- ✅ Configuración local completa

---

## 📋 Pasos para Crear y Conectar Repositorio en GitHub

### 1️⃣ Crear Repositorio en GitHub

1. Ve a [GitHub](https://github.com) e inicia sesión
2. Haz clic en el botón **"+"** (esquina superior derecha) → **"New repository"**
3. Configura el repositorio:
   - **Repository name**: `cantina-tita-sistema` (o el nombre que prefieras)
   - **Description**: "Sistema completo de gestión para cantina escolar - Django + MySQL"
   - **Visibility**: 
     - ✅ **Private** (recomendado para proyecto comercial)
     - ⚠️ **Public** (si quieres que sea código abierto)
   - ⚠️ **NO marques**: "Initialize this repository with a README" (ya tenemos uno)
4. Haz clic en **"Create repository"**

---

### 2️⃣ Conectar Repositorio Local con GitHub

Una vez creado el repositorio en GitHub, ejecuta estos comandos en tu terminal:

#### Opción A: Si tu repositorio es HTTPS

```bash
git remote add origin https://github.com/TU_USUARIO/cantina-tita-sistema.git
git branch -M main
git push -u origin main
```

#### Opción B: Si tu repositorio es SSH (recomendado)

```bash
git remote add origin git@github.com:TU_USUARIO/cantina-tita-sistema.git
git branch -M main
git push -u origin main
```

**Nota**: Reemplaza `TU_USUARIO` con tu nombre de usuario de GitHub.

---

### 3️⃣ Verificar Conexión

```bash
# Ver el remoto configurado
git remote -v

# Debería mostrar:
# origin  https://github.com/TU_USUARIO/cantina-tita-sistema.git (fetch)
# origin  https://github.com/TU_USUARIO/cantina-tita-sistema.git (push)
```

---

## 🔐 Configurar SSH (Opcional pero Recomendado)

Si quieres usar SSH en lugar de HTTPS (más seguro y no pide contraseña cada vez):

### 1. Generar clave SSH (si no tienes una)

```bash
ssh-keygen -t ed25519 -C "tu_email@ejemplo.com"
```

Presiona Enter 3 veces (acepta ubicación por defecto y sin passphrase)

### 2. Copiar clave pública

```bash
# Windows PowerShell
Get-Content ~/.ssh/id_ed25519.pub | Set-Clipboard

# Windows Git Bash
cat ~/.ssh/id_ed25519.pub | clip
```

### 3. Agregar clave a GitHub

1. Ve a GitHub → Settings → SSH and GPG keys
2. Haz clic en **"New SSH key"**
3. Pega la clave copiada
4. Haz clic en **"Add SSH key"**

### 4. Probar conexión

```bash
ssh -T git@github.com

# Debería responder:
# Hi TU_USUARIO! You've successfully authenticated...
```

---

## 📝 Comandos Git Útiles para el Día a Día

### Ver estado del repositorio
```bash
git status
```

### Agregar archivos modificados
```bash
git add .                    # Agregar todos los archivos
git add archivo.py           # Agregar archivo específico
```

### Hacer commit
```bash
git commit -m "Descripción del cambio"
```

### Subir cambios a GitHub
```bash
git push
```

### Bajar cambios de GitHub
```bash
git pull
```

### Ver historial de commits
```bash
git log --oneline
```

### Crear una nueva rama
```bash
git checkout -b nombre-rama
```

### Cambiar de rama
```bash
git checkout main
```

### Ver ramas
```bash
git branch
```

---

## 🔄 Flujo de Trabajo Recomendado

### Desarrollo de Nueva Funcionalidad

```bash
# 1. Crear rama para la funcionalidad
git checkout -b feature/nueva-funcionalidad

# 2. Hacer cambios en el código
# ... editar archivos ...

# 3. Agregar y commitear cambios
git add .
git commit -m "Agregar nueva funcionalidad X"

# 4. Subir rama a GitHub
git push -u origin feature/nueva-funcionalidad

# 5. Crear Pull Request en GitHub
# (desde la interfaz web)

# 6. Una vez aprobado, fusionar a main
git checkout main
git merge feature/nueva-funcionalidad
git push
```

---

## 📦 Archivos Importantes No Versionados

Estos archivos están en `.gitignore` y NO se suben a GitHub:

- ✅ `.venv/` - Entorno virtual (se instala localmente)
- ✅ `.env` - Variables de entorno con contraseñas
- ✅ `*.pyc` - Archivos compilados de Python
- ✅ `__pycache__/` - Cache de Python
- ✅ `*.log` - Archivos de log
- ✅ Configuración MySQL - Base de datos de producción
- ✅ `.vscode/` - Configuración del editor

---

## ⚠️ IMPORTANTE: Archivos Sensibles

**NUNCA subas a GitHub:**
- ❌ Contraseñas de base de datos
- ❌ Claves secretas (SECRET_KEY)
- ❌ Archivos `.env` con credenciales
- ❌ Tokens de API
- ❌ Dumps de base de datos con datos reales

**Usa** `.env.example` como plantilla (sin valores reales):

```env
# .env.example (SÍ se versiona)
DEBUG=True
SECRET_KEY=coloca_aqui_tu_clave_secreta
DB_NAME=cantinaTitadb
DB_USER=tu_usuario
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=3306
```

---

## 🎯 Configuración del Repositorio en GitHub

### Proteger rama principal

1. Ve a tu repositorio en GitHub
2. Settings → Branches
3. Add branch protection rule
4. Branch name pattern: `main`
5. Marca:
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass
   - ✅ Require conversation resolution before merging

### Agregar colaboradores

1. Settings → Collaborators
2. Add people
3. Ingresa usuario de GitHub del colaborador

### Agregar descripción y tags

1. Edita el repositorio (arriba)
2. About → Settings
3. Agrega:
   - **Description**: Sistema de gestión para cantina escolar
   - **Topics**: `django`, `python`, `mysql`, `pos`, `paraguay`, `school-management`

---

## 📊 Tu Proyecto en GitHub

Una vez subido, tu repositorio mostrará:

```
📁 cantina-tita-sistema
├── 📄 README.md                    → Documentación principal
├── 📄 IMPLEMENTACION_COMPLETA.md   → Detalle de implementación
├── 📄 CONFIGURACION_PARAGUAY.md    → Config regional Paraguay
├── 📁 cantina_project/             → Configuración Django
├── 📁 gestion/                     → App principal (55 modelos)
├── 📄 requirements.txt             → Dependencias Python
├── 📄 manage.py                    → Script Django
└── 📄 .gitignore                   → Archivos excluidos

37 files | 6,419 lines | Python, Django
```

---

## 🚀 Siguientes Pasos

1. ✅ Crear repositorio en GitHub
2. ✅ Conectar repositorio local
3. ✅ Hacer primer push
4. ⏭️ Configurar protección de rama
5. ⏭️ Agregar colaboradores (si aplica)
6. ⏭️ Configurar GitHub Actions (CI/CD)
7. ⏭️ Crear issues para nuevas funcionalidades

---

## 💡 Tips

### Commits descriptivos
```bash
# ❌ Mal
git commit -m "cambios"

# ✅ Bien
git commit -m "Agregar modelo de NotasCredito con validaciones"
git commit -m "Fix: Corregir cálculo de IVA en ventas"
git commit -m "Docs: Actualizar README con instrucciones de instalación"
```

### Prefijos recomendados
- `feat:` - Nueva funcionalidad
- `fix:` - Corrección de bug
- `docs:` - Documentación
- `style:` - Formato de código
- `refactor:` - Refactorización
- `test:` - Agregar tests
- `chore:` - Tareas de mantenimiento

---

## 📞 Ayuda

Si tienes problemas:

1. **Error de autenticación**: Verifica credenciales de GitHub
2. **Error de push**: Asegúrate de tener permisos en el repositorio
3. **Conflictos**: Haz `git pull` antes de `git push`
4. **Archivo muy grande**: Verifica que esté en `.gitignore`

---

**¡Tu proyecto ahora está listo para GitHub!** 🎉
