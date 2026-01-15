# INSTRUCCIONES DE INSTALACIÓN DE GRAPHVIZ

## ⚠️ IMPORTANTE: Graphviz no está instalado en su sistema

Para que los scripts funcionen correctamente, necesita instalar **Graphviz** en su sistema Windows.

## 📥 Instalación de Graphviz en Windows

### Opción 1: Instalador MSI (Recomendado)

1. **Descargar Graphviz:**
   - Visite: https://graphviz.org/download/
   - Descargue la versión para Windows (archivo .msi)
   - Ejemplo: `stable_windows_10_cmake_Release_graphviz-install-XXX-win64.exe`

2. **Instalar:**
   - Ejecute el instalador descargado
   - Durante la instalación, MARQUE la opción: **"Add Graphviz to the system PATH"**
   - Complete la instalación

3. **Verificar instalación:**
   ```powershell
   # Reinicie PowerShell/Terminal
   dot -V
   ```
   
   Debería ver algo como:
   ```
   dot - graphviz version 2.50.0 (20211204.2007)
   ```

### Opción 2: Chocolatey (si tiene Chocolatey instalado)

```powershell
choco install graphviz
```

### Opción 3: Scoop (si tiene Scoop instalado)

```powershell
scoop install graphviz
```

### Opción 4: winget (Windows Package Manager)

```powershell
winget install graphviz
```

## 🔧 Configuración Post-Instalación

Si después de instalar Graphviz el comando `dot -V` no funciona:

1. **Agregar manualmente al PATH:**
   - Busque la carpeta de instalación (generalmente: `C:\Program Files\Graphviz\bin`)
   - Agregue esa ruta a las variables de entorno PATH del sistema:
     - Windows Key + "Variables de entorno"
     - "Variables de entorno" → "Path" (del sistema) → "Editar"
     - "Nuevo" → Agregar: `C:\Program Files\Graphviz\bin`
     - "Aceptar" en todas las ventanas

2. **Reiniciar Terminal:**
   - Cierre completamente VS Code o PowerShell
   - Vuelva a abrir
   - Pruebe: `dot -V`

## ✅ Una vez instalado Graphviz

Ejecute el script principal:

```powershell
D:/anteproyecto20112025/.venv/Scripts/python.exe generar_todos_los_der.py
```

O los scripts individuales:

```powershell
# DER Completo (Lógico y Físico)
D:/anteproyecto20112025/.venv/Scripts/python.exe generar_der_completo.py

# DER Modular
D:/anteproyecto20112025/.venv/Scripts/python.exe generar_der_modular.py
```

## 🚀 Ejecución Rápida

También puede usar:

```powershell
# Activar entorno virtual (si no está activado)
.\.venv\Scripts\Activate.ps1

# Ejecutar script
python generar_todos_los_der.py
```

## 📦 Dependencias de Python (Ya instaladas)

✅ SQLAlchemy - Instalado
✅ PyMySQL - Instalado  
✅ python-decouple - Instalado
✅ graphviz (Python package) - Instalado

❌ Graphviz (Sistema) - **PENDIENTE DE INSTALACIÓN**

## 🆘 Problemas Comunes

### "dot: command not found" o "dot no se reconoce"
- Graphviz no está instalado o no está en PATH
- Solución: Siga los pasos de instalación arriba

### "Permission denied" al instalar
- Ejecute el instalador como Administrador
- Click derecho → "Ejecutar como administrador"

### El comando funciona pero los scripts fallan
- Asegúrese de haber reiniciado la terminal después de instalar
- Verifique que `dot -V` funcione correctamente

## 📞 Soporte

Si después de seguir estos pasos aún tiene problemas:
1. Verifique la versión de Graphviz instalada: `dot -V`
2. Verifique que esté en PATH: `where.exe dot`
3. Revise los mensajes de error específicos del script

---

**Nota:** La instalación de Graphviz es necesaria solo una vez por sistema.
