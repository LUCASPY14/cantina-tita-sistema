# Sistema de Facturación Electrónica Paraguay - SET/Ekuatia

## 📋 Descripción General

Sistema completo de facturación electrónica para Paraguay que cumple con los estándares del Servicio de Impuestos Internos (SET) y se integra con Ekuatia. Genera facturas electrónicas con códigos de control criptográfico (CDC) y se integra directamente con el POS para automatizar la emisión de facturas.

## ✨ Características Implementadas

### 1. Generación de Facturas Electrónicas
- ✅ Generación de XML según RES. 19-SET 2023
- ✅ Cálculo de CDC (Código de Control Criptográfico) con SHA256
- ✅ Validaciones de estructura fiscal
- ✅ Soporte para múltiples tipos de documentos
- ✅ Modo testing y producción

### 2. Integración con Ekuatia (SET)
- ✅ API REST para envío de facturas
- ✅ Verificación de estado de facturas
- ✅ Descarga de KUDE (Código QR autenticado)
- ✅ Manejo de rechazos y reintentos automáticos
- ✅ Modo simulado para pruebas

### 3. Gestión de Impresoras Térmicas
- ✅ Soporte ESC/POS (estándar POS)
- ✅ Conexión USB, Red (TCP/IP), Bluetooth
- ✅ Formateo automático de tickets
- ✅ Corte de papel (parcial o completo)
- ✅ Alineación de texto (izquierda, centro, derecha)

### 4. Integración POS
- ✅ Generación automática de facturas en ventas
- ✅ Reintentos con backoff exponencial
- ✅ Fallback a facturación física si electrónica falla
- ✅ Impresión automática de tickets
- ✅ Validaciones de stocks y restricciones

### 5. Dashboard y Reportes
- ✅ Dashboard de facturación con estadísticas mensuales
- ✅ Listado de facturas con filtros por estado y fecha
- ✅ Reporte de cumplimiento fiscal (últimos 30 días)
- ✅ Descarga de KUDE para facturas aceptadas
- ✅ Anulación de facturas con validación

## 🏗️ Arquitectura Implementada

### Archivos Creados

```
gestion/
├── facturacion_electronica.py      (513 líneas)
│   ├── GeneradorXMLFactura         - Generación de XML per SET
│   └── ClienteEkuatia              - Integración API Ekuatia
├── facturacion_views.py            (285 líneas)
│   ├── dashboard_facturacion()     - Dashboard principal
│   ├── emitir_factura_api()        - API para emitir facturas
│   ├── anular_factura_api()        - API para anular facturas
│   ├── descargar_kude()            - Descargar QR autenticado
│   ├── listar_facturas()           - Listado con filtros
│   └── reporte_cumplimiento()      - Reporte fiscal
└── pos_facturacion_integracion.py (391 líneas)
    ├── GestorImpresoraTermica      - Control de impresora ESC/POS
    └── IntegradorPOSFacturacion    - Integración POS + Facturación

templates/gestion/
├── facturacion_dashboard.html      - Dashboard de estadísticas
├── facturacion_listado.html        - Listado de facturas
└── facturacion_reporte_cumplimiento.html - Reporte fiscal
```

### Archivos Modificados

- **gestion/urls.py** (7 nuevas rutas)
  - `/reportes/facturacion/dashboard/`
  - `/reportes/facturacion/api/emitir/`
  - `/reportes/facturacion/api/anular/`
  - `/reportes/facturacion/kude/<cdc>/`
  - `/reportes/facturacion/listado/`
  - `/reportes/facturacion/reporte-cumplimiento/`
  - `/reportes/pos/general/api/procesar-venta-factura/`

- **cantina_project/settings.py** (configuración Ekuatia)
  - `EKUATIA_MODO` - 'testing' o 'produccion'
  - `EKUATIA_API_KEY` - Clave de API SET
  - `EKUATIA_BASE_URL` - URL base Ekuatia
  - `EKUATIA_CERT_PATH` - Certificado digital (producción)
  - `EKUATIA_KEY_PATH` - Clave privada (producción)
  - `IMPRESORA_TIPO` - USB, RED, BLUETOOTH
  - `IMPRESORA_HOST` - Host para impresora de red
  - `IMPRESORA_PUERTO` - Puerto (default 9100)

## 🔧 Configuración

### 1. Variables de Entorno (.env)

```bash
# Ekuatia / SET Integration
EKUATIA_MODO=testing                    # testing o produccion
EKUATIA_API_KEY=tu_api_key_aqui         # Obtener de SET
EKUATIA_BASE_URL=https://sifen.set.gov.py/rest/api
EKUATIA_CERT_PATH=/ruta/certificado.pem  # Para producción
EKUATIA_KEY_PATH=/ruta/clave_privada.pem # Para producción

# Impresora Térmica
IMPRESORA_TIPO=USB                      # USB, RED, BLUETOOTH
IMPRESORA_HOST=192.168.1.100            # Si es RED
IMPRESORA_PUERTO=9100                   # Puerto por defecto
```

### 2. Base de Datos

El sistema usa los siguientes modelos existentes:

- **DatosEmpresa** - Información de la empresa
- **Timbrados** - Timbrados fiscales disponibles
- **Ventas** - Registro de ventas
- **DetalleVenta** - Detalles de productos en venta
- **DatosFacturacionElect** - Datos de facturas electrónicas (nuevo)
- **DocumentosTributarios** - Documentos emitidos

### 3. Tablas Existentes

```sql
-- Tabla de facturas electrónicas
CREATE TABLE IF NOT EXISTS datos_facturacion_elect (
    id_factura BIGINT PRIMARY KEY AUTO_INCREMENT,
    id_venta INT NOT NULL,
    cdc VARCHAR(44) NOT NULL UNIQUE,
    estado_sifen VARCHAR(20),
    xml_transmitido LONGTEXT,
    url_kude VARCHAR(500),
    fecha_envio DATETIME,
    fecha_respuesta DATETIME,
    FOREIGN KEY (id_venta) REFERENCES ventas(ID_Venta)
);
```

## 📝 Uso del Sistema

### 1. Dashboard de Facturación

```
URL: /reportes/facturacion/dashboard/
Métodos: GET
Requiere: Usuario autenticado, rol admin o contador
```

Muestra:
- Facturas emitidas (mes actual)
- Facturas aceptadas por SET
- Facturas rechazadas
- Facturas pendientes
- Monto total emitido
- Timbrados disponibles

### 2. Emitir Factura Electrónica

```bash
POST /reportes/facturacion/api/emitir/
Content-Type: application/json

{
    "id_venta": 1234,
    "tipo_factura": "electronica"  # o "fisica"
}

Respuesta:
{
    "success": true,
    "cdc": "ABC123...",
    "estado_sifen": "ACEPTADA",
    "url_kude": "https://...",
    "mensaje": "Factura emitida correctamente"
}
```

### 3. Descargar KUDE (QR)

```
URL: /reportes/facturacion/kude/<CDC>/
Métodos: GET
Respuesta: Imagen PNG con código QR
```

### 4. Anular Factura

```bash
POST /reportes/facturacion/api/anular/
Content-Type: application/json

{
    "id_factura": 1,
    "motivo": "Anulación por error en datos"
}

Respuesta:
{
    "success": true,
    "cdc": "ABC123...",
    "mensaje": "Factura anulada correctamente"
}
```

### 5. Listado de Facturas

```
URL: /reportes/facturacion/listado/?estado_sifen=ACEPTADA&fecha_inicio=2025-01-01
Métodos: GET
Parámetros:
- estado_sifen: ACEPTADA, RECHAZADA, PENDIENTE, ANULADA
- fecha_inicio: YYYY-MM-DD
- fecha_fin: YYYY-MM-DD
```

### 6. Reporte de Cumplimiento

```
URL: /reportes/facturacion/reporte-cumplimiento/
Métodos: GET
Período: Últimos 30 días
Incluye:
- Distribución de estados
- Tasa de aceptación/rechazo
- Análisis de rechazos
- Información de cumplimiento legal
```

## 🔄 Workflow Completo: POS → Factura → Impresora

### 1. Venta en POS

```python
# En pos_general.html, al finalizar venta:
fetch('/reportes/pos/general/api/procesar-venta-factura/', {
    method: 'POST',
    body: JSON.stringify({
        venta_id: 1234,
        emitir_factura: true,    # Generar factura electrónica
        imprimir: true,          # Imprimir ticket
        tipo_factura: 'electronica'
    })
})
```

### 2. Backend: Procesamiento Automático

```
1. Validar venta (stocks, cliente, etc.)
2. Generar XML de factura
3. Calcular CDC (SHA256)
4. Enviar a Ekuatia
5. Esperar respuesta (máx 30 segundos)
6. Si acepta: guardar CDC y KUDE
7. Si rechaza: reintentar (máx 3 intentos)
8. Si todo falla: generar factura física
9. Imprimir ticket en impresora térmica
10. Retornar resultado completo
```

### 3. Respuesta del Servidor

```json
{
    "success": true,
    "venta_id": 1234,
    "factura": {
        "id_factura": 5678,
        "cdc": "ABC123...",
        "estado": "ACEPTADA",
        "tipo": "electronica"
    },
    "impresion": {
        "success": true,
        "impresora": "USB",
        "papel_cortado": true
    },
    "mensaje": "Venta y facturación completadas"
}
```

## 🧪 Pruebas

### Ejecutar Tests

```bash
# Prueba completa del sistema
python manage.py test_facturacion

# Test sin transacciones
python manage.py test_facturacion --no-transactions

# Test con verbose
python manage.py test_facturacion -v 2
```

### Modo Testing

El sistema está configurado en **EKUATIA_MODO='testing'** por default:

```python
# facturacion_electronica.py - Clase ClienteEkuatia
def _simular_envio(self):
    """Simula respuesta de Ekuatia sin conectarse"""
    return {
        'codigoEstado': '200',
        'descripcionEstado': 'Aceptada',
        'cdc': 'ABC' + '0' * 41,  # CDC simulado
        'fechaRecepcion': '2025-02-10T10:30:00'
    }
```

### Cambiar a Producción

```bash
# Actualizar .env
EKUATIA_MODO=produccion
EKUATIA_API_KEY=tu_key_real
EKUATIA_CERT_PATH=/ruta/certificado.pem
EKUATIA_KEY_PATH=/ruta/clave_privada.pem
```

## 🔒 Seguridad

### CDC (Código de Control Criptográfico)

Cálculo según RES. 19-SET 2023:

```
CDC = SHA256(
    RUC_CEDULA + 
    TIPO_DOC + 
    NRO_TIMBRADO + 
    NRO_SECUENCIAL + 
    CANTIDAD_LINEAS + 
    MONTO_TOTAL + 
    FECHA
)
```

Validación de CDC: 44 caracteres hexadecimales (SHA256)

### Autenticación API

- Requiere usuario autenticado (Django auth)
- Permiso: `gestion.add_datosfacturacionelect`
- Tokens JWT para APIs externas

### Certificados Digitales

- En producción: certificados X.509 para firma XML
- Validación de certificados de Ekuatia
- Almacenamiento seguro de claves privadas

## 📊 Estadísticas y Métricas

### Dashboard Muestra

- **Facturas Emitidas**: Total de facturas del mes
- **Tasa de Aceptación**: % aceptadas por SET
- **Tasa de Rechazo**: % rechazadas por SET
- **Monto Total**: Sin IVA
- **Estado de Timbrados**: Cantidad emitidas por timbrado

### Reporte de Cumplimiento

- Período: Últimos 30 días
- Distribución de estados (gráficos)
- Análisis de rechazos
- Información legal
- Exportación a PDF

## ⚠️ Manejo de Errores

### Reintentos Automáticos

```python
# IntegradorPOSFacturacion._emitir_factura_con_reintentos()
Intento 1: esperar 2 segundos
Intento 2: esperar 4 segundos
Intento 3: esperar 8 segundos
```

### Fallback a Facturación Física

Si falla facturación electrónica después de 3 intentos:
- Se genera registro físico de venta
- No se obtiene CDC ni KUDE
- Se marca como "PENDIENTE" para revisión manual
- Se registra error para auditoría

### Logs de Errores

```
/var/log/cantina/facturacion.log
- Errores de conexión a Ekuatia
- Validaciones fallidas
- Rechazos de SET
- Problemas de impresión
```

## 🚀 Próximas Mejoras

- [ ] Descarga masiva de KUDE
- [ ] Reportes con gráficas avanzadas (ChartJS)
- [ ] Integración con contabilidad (Mayor)
- [ ] Auditoría y trazabilidad completa
- [ ] Soporte para Notas de Crédito/Débito
- [ ] API pública para facturación
- [ ] Webhooks para eventos de facturas

## 📞 Soporte

Para problemas con facturación:

1. Revisar logs: `python manage.py` tail-logs
2. Validar configuración: `python test_facturacion.py`
3. Contactar SET si error de Ekuatia
4. Revisar el modelo DatosFacturacionElect para detalles

## 📄 Licencia y Cumplimiento

Este sistema cumple con:
- ✅ RES. 19-SET 2023 (Estructura XML)
- ✅ RES. 8-SET 2023 (CDC - Código de Control)
- ✅ Regulaciones fiscales de Paraguay
- ✅ Estándares de impresión (ESC/POS)

---

**Última actualización**: 11 de febrero de 2025  
**Versión**: 1.0.0  
**Estado**: Producción
