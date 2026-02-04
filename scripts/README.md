# Scripts - Sistema de Gestión de Cantina

Esta carpeta contiene scripts utilitarios organizados por categoría.

## 📁 Estructura

```
scripts/
├── setup/          # Scripts de configuración inicial
├── database/       # Scripts de base de datos (migraciones, backups, DER)
├── maintenance/    # Scripts de mantenimiento y limpieza
├── audit/          # Scripts de auditoría y análisis
└── dev/            # Scripts de desarrollo
```

## 🔧 Categorías

### setup/
Scripts de configuración inicial del proyecto:
- Configuración de producción
- Setup de servicios externos
- Inicialización del sistema

### database/
Scripts relacionados con base de datos:
- Ejecutar migraciones
- Backups y restore
- Generación de diagramas DER
- Optimización de BD
- Análisis de schema

### maintenance/
Scripts de mantenimiento:
- Limpieza de archivos temporales
- Limpieza de datos obsoletos
- Reorganización de código
- Optimización de templates

### audit/
Scripts de auditoría y análisis:
- Auditoría de seguridad
- Auditoría de templates
- Análisis de performance
- Análisis de buenas prácticas
- Verificación de sistema

### dev/
Scripts de desarrollo:
- Servidor de desarrollo
- Coverage de tests
- Generación de reportes
- Validaciones

## 📝 Uso

Ejecutar desde la raíz del proyecto:

```bash
# Ejemplo: ejecutar script de auditoría
python scripts/audit/auditoria_completa.py

# Ejemplo: generar DER
python scripts/database/generar_der_completo.py
```

## ⚠️ Nota

Scripts de una sola vez ya ejecutados se encuentran en `/archived_scripts/`
