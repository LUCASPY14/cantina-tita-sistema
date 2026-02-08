# 🗃️ MANUAL DE OPERACIONES - SISTEMA CANTINATITA

## 📋 INFORMACIÓN GENERAL
- **Sistema**: Base de Datos Cantinatita
- **Ambiente**: Producción
- **Versión**: 1.0.0
- **Última Actualización**: $(date)

## 🎯 OBJETIVO
Este manual describe los procedimientos operativos para el mantenimiento, monitoreo y recuperación de la base de datos Cantinatita.

## 📊 ARQUITECTURA DEL SISTEMA

### Base de Datos Principal
- **Nombre**: `cantinatitadb`
- **Motor**: MySQL 8.0+
- **Collation**: `utf8mb4_0900_ai_ci`
- **Ubicación**: Servidor de producción

### Base de Datos de Pruebas
- **Nombre**: `cantinatitadb_test`
- **Propósito**: Pruebas seguras sin afectar producción

## ⚙️ PROCEDIMIENTOS ALMACENADOS

### Producción
| Procedimiento | Descripción | Frecuencia |
|---------------|-------------|------------|
| `sp_recuperacion_emergencia` | Backup y recuperación | Manual |
| `sp_recolectar_metricas` | Monitoreo de rendimiento | Cada hora |
| `sp_auditoria_seguridad` | Auditoría de seguridad | Diario (03:00) |
| `sp_verificacion_integridad` | Verificación integridad | Manual |

### Pruebas
| Procedimiento | Descripción |
|---------------|-------------|
| `sp_verificacion_integridad_test` | Prueba de integridad |
| `sp_recolectar_metricas_test` | Prueba de métricas |
| `sp_backup_prueba_test` | Prueba de backup |
| `sp_limpiar_pruebas_test` | Limpieza de pruebas |

## ⏰ EVENTOS PROGRAMADOS

### En MySQL
1. **02:00** - `evento_mantenimiento_automatico`
2. **03:00** - `evento_auditoria_seguridad`
3. **Cada hora** - `evento_monitoreo_metricas`

### En Sistema Operativo (Cron)
1. **02:00** - Backup automático completo
2. **03:00 Domingos** - Limpieza de logs antiguos

## 🚨 PROCEDIMIENTOS DE EMERGENCIA

### 1. Recuperación de Base de Datos
```sql
-- Paso 1: Identificar último backup
SELECT * FROM configuracion_recuperacion 
WHERE parametro = 'ultimo_backup_completo';

-- Paso 2: Ejecutar recuperación
CALL sp_recuperacion_emergencia('recuperar');

-- Paso 3: Verificar
CALL sp_verificacion_integridad();