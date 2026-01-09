# 📱 PLAN DE DESARROLLO: PORTAL WEB PADRES
**Estimación:** 1.5-2 semanas ⬇️⬇️ (reducido por MetrePay + Tigo Money existentes)  
**Estado:** Planificado  
**Prioridad:** Alta

---

## 📋 RESUMEN EJECUTIVO

Portal web para padres/responsables que permite:
- Consultar saldo de tarjetas de hijos
- Ver historial de consumos y recargas
- Realizar recargas online
- Gestionar datos de hijos y tarjetas
- Recibir notificaciones y alertas

---

## 🎯 FUNCIONALIDADES PRINCIPALES

### 1. AUTENTICACIÓN Y REGISTRO
**Tiempo estimado:** 2-3 días

#### Registro de padres
- Formulario de registro con validación
- Campos: Nombres, Apellidos, Email, Teléfono, Contraseña
- Verificación de email
- Términos y condiciones

#### Login/Logout
- Formulario de login (email + contraseña)
- Recuperación de contraseña
- Sesión persistente (Remember me)
- Logout seguro

#### Perfil de usuario
- Editar datos personales
- Cambiar contraseña
- Configurar notificaciones

**Tablas requeridas:**
- ✅ `clientes` (ya existe)
- 🆕 `usuarios_portal` (nueva - para credenciales web)
- 🆕 `tokens_verificacion` (nueva - para reset password)

---

### 2. GESTIÓN DE HIJOS Y TARJETAS
**Tiempo estimado:** 2-3 días

#### Visualización de hijos
- Lista de hijos asociados al responsable
- Datos: Nombre, Apellido, Grado, Foto
- Tarjeta asociada con número y estado

#### Gestión de hijos
- Agregar nuevo hijo
- Editar datos de hijo
- Subir foto de hijo
- Asociar/desasociar tarjeta

#### Información de tarjetas
- Número de tarjeta
- Saldo actual
- Estado (Activa/Bloqueada/Suspendida)
- Fecha de última recarga
- Fecha de último consumo

**Tablas requeridas:**
- ✅ `hijos` (ya existe)
- ✅ `tarjetas` (ya existe)
- ✅ Relaciones ya configuradas

---

### 3. CONSULTA DE SALDO
**Tiempo estimado:** 1-2 días

#### Dashboard por hijo
- Saldo actual destacado
- Gráfico de evolución de saldo (últimos 30 días)
- Resumen de consumos del mes
- Resumen de recargas del mes

#### Consulta rápida
- Vista de tarjeta digital con saldo
- Actualización en tiempo real
- Indicador de saldo bajo

**APIs a crear:**
```python
# gestion/portal_api.py

@api_view(['GET'])
def obtener_saldo_hijo(request, id_hijo):
    """Obtiene saldo actual de tarjeta de un hijo"""
    
@api_view(['GET'])
def obtener_resumen_mes(request, id_hijo):
    """Resumen de consumos y recargas del mes"""
    
@api_view(['GET'])
def obtener_grafico_saldo(request, id_hijo, dias=30):
    """Datos para gráfico de evolución de saldo"""
```

---

### 4. HISTORIAL DE CONSUMOS
**Tiempo estimado:** 2-3 días

#### Vista de consumos
- Tabla paginada de consumos
- Filtros: Fecha inicio/fin, Tipo de producto
- Columnas: Fecha, Hora, Producto, Cantidad, Monto
- Exportar a PDF/Excel

#### Detalles de consumo
- Modal con información completa
- Productos consumidos
- Método de pago (tarjeta/efectivo)
- Lugar de compra (si aplica)

#### Estadísticas
- Productos más consumidos
- Gasto promedio diario/semanal
- Gráficos de consumo por categoría

**Vistas MySQL a usar:**
- ✅ `v_tarjetas_detalle` (ya existe y funciona)
- 🆕 Vista nueva para historial detallado

---

### 5. HISTORIAL DE RECARGAS
**Tiempo estimado:** 1-2 días

#### Vista de recargas
- Tabla paginada de recargas
- Filtros: Fecha inicio/fin, Método de pago
- Columnas: Fecha, Hora, Monto, Método, Estado
- Exportar a PDF/Excel

#### Detalles de recarga
- Modal con información completa
- Comprobante digital
- Método de pago usado
- Usuario que realizó la recarga

**Tablas a usar:**
- ✅ `cargas_saldo` (ya existe)
- ✅ `ventas` (ya existe - para recargas registradas como venta)

---

### 6. RECARGAS ONLINE
**Tiempo estimado:** 2-3 días ⬇️ (reducido por integración existente)

#### Proceso de recarga
1. Seleccionar hijo/tarjeta
2. Ingresar monto a recargar
3. Seleccionar método de pago
4. Confirmar y pagar
5. Recibir comprobante

#### Métodos de pago
- **MetrePay** ⭐ (tarjetas crédito/débito) - ✅ YA INTEGRADO 100%
- **Tigo Money** 📱 (billetera digital) - ✅ YA INTEGRADO 100%
- **Transferencia bancaria** (confirmación manual)

#### Integración de pagos
✅ **MetrePay ya está integrado al 100%**

**Función existente:** `gestion.cliente_views.procesar_pago_metrepay()`

```python
# Solo necesitas reutilizar la función existente:
from gestion.cliente_views import procesar_pago_metrepay

# En tu vista de recarga del portal de padres:
exito, referencia, payment_url, custom_id = procesar_pago_metrepay(
    monto=monto_decimal,
    metodo_pago='metrepay',
    request=request,
    tipo_pago='RECARGA_PORTAL'  # Nuevo tipo
)

if exito:
    # Registrar transacción en TransaccionOnline
    # Redirigir a payment_url
```

**Tigo Money ✅ YA INTEGRADO:**
```python
from gestion.tigo_money_gateway import procesar_pago_tigo_money

exito, transaction_id, instrucciones, custom_id = procesar_pago_tigo_money(
    telefono="0981123456",
    monto=monto_decimal,
    descripcion="Recarga de saldo",
    request=request,
    tipo_pago='RECARGA_PORTAL'
)

if exito:
    # Mostrar instrucciones (incluye código *555#)
    # Usuario confirma en su celular
```

**Documentación completa:** Ver [TIGO_MONEY_INTEGRACION.md](TIGO_MONEY_INTEGRACION.md)

**Documentación completa:** Ver [METREPAY_INTEGRACION_EXISTENTE.md](METREPAY_INTEGRACION_EXISTENTE.md)

#### Seguridad
- HTTPS obligatorio
- Tokens de pago únicos
- No almacenar datos de tarjetas de crédito
- Registro de todas las transacciones

**Tablas requeridas:**
- ✅ `cargas_saldo` (ya existe)
- ✅ `metodos_pago` (ya existe)
- 🆕 `transacciones_online` (nueva - para pagos web)
- 🆕 `logs_pagos` (nueva - auditoría)

---

### 7. NOTIFICACIONES Y ALERTAS
**Tiempo estimado:** 2 días

#### Tipos de notificaciones
- Saldo bajo (< $5,000)
- Recarga exitosa
- Consumo realizado
- Tarjeta bloqueada
- Restricciones aplicadas

#### Canales
- Email
- SMS (opcional)
- Notificaciones push (opcional - futura fase)
- En el portal (campana de notificaciones)

#### Configuración
- Activar/desactivar por tipo
- Configurar umbrales (ej: saldo mínimo)
- Elegir canales preferidos

**Tablas requeridas:**
- 🆕 `notificaciones` (nueva)
- 🆕 `preferencias_notificacion` (nueva)

---

## 🏗️ ARQUITECTURA TÉCNICA

### Backend (Django)
```
gestion/
├── portal_views.py         # Vistas del portal web
├── portal_api.py           # APIs REST para frontend
├── payment_gateway.py      # Integración pagos
├── notifications.py        # Sistema de notificaciones
└── forms/
    ├── registro_form.py
    ├── login_form.py
    └── recarga_form.py
```

### Frontend (Templates)
```
templates/portal/
├── base_portal.html        # Template base del portal
├── login.html              # Página de login
├── registro.html           # Página de registro
├── dashboard.html          # Dashboard principal
├── hijos/
│   ├── lista.html
│   ├── detalle.html
│   └── editar.html
├── saldo/
│   ├── consulta.html
│   └── grafico.html
├── historial/
│   ├── consumos.html
│   └── recargas.html
├── recarga/
│   ├── paso1_seleccionar.html
│   ├── paso2_monto.html
│   ├── paso3_pago.html
│   └── confirmacion.html
└── perfil/
    ├── editar.html
    └── notificaciones.html
```

### JavaScript/Alpine.js
```javascript
// static/js/portal/
├── dashboard.js            // Lógica del dashboard
├── recarga.js              // Proceso de recarga
├── graficos.js             // Charts y gráficos
└── notificaciones.js       // Sistema de notificaciones
```

### CSS/Estilos
```css
/* static/css/portal/ */
├── portal.css              // Estilos generales
├── dashboard.css           // Estilos dashboard
└── responsive.css          // Estilos responsive
```

---

## 📊 MODELOS DE DATOS NUEVOS

### UsuarioPortal
```python
class UsuarioPortal(models.Model):
    cliente = models.OneToOneField('Cliente', on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)
    email_verificado = models.BooleanField(default=False)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    ultimo_acceso = models.DateTimeField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'usuarios_portal'
```

### TokenVerificacion
```python
class TokenVerificacion(models.Model):
    usuario = models.ForeignKey('UsuarioPortal', on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    tipo = models.CharField(max_length=50)  # 'email_verification', 'password_reset'
    expira_en = models.DateTimeField()
    usado = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'tokens_verificacion'
```

### TransaccionOnline
```python
class TransaccionOnline(models.Model):
    tarjeta = models.ForeignKey('Tarjeta', on_delete=models.CASCADE)
    usuario_portal = models.ForeignKey('UsuarioPortal', on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.ForeignKey('MetodoPago', on_delete=models.CASCADE)
    estado = models.CharField(max_length=50)  # 'pendiente', 'completada', 'fallida'
    referencia_pago = models.CharField(max_length=255, null=True)
    fecha_transaccion = models.DateTimeField(auto_now_add=True)
    ip_origen = models.GenericIPAddressField()
    
    class Meta:
        db_table = 'transacciones_online'
```

### Notificacion
```python
class Notificacion(models.Model):
    usuario_portal = models.ForeignKey('UsuarioPortal', on_delete=models.CASCADE)
    tipo = models.CharField(max_length=50)
    titulo = models.CharField(max_length=255)
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_leida = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'notificaciones'
```

### PreferenciaNotificacion
```python
class PreferenciaNotificacion(models.Model):
    usuario_portal = models.ForeignKey('UsuarioPortal', on_delete=models.CASCADE)
    tipo_notificacion = models.CharField(max_length=50)
    email_activo = models.BooleanField(default=True)
    sms_activo = models.BooleanField(default=False)
    push_activo = models.BooleanField(default=False)
    umbral_saldo_bajo = models.DecimalField(max_digits=10, decimal_places=2, default=5000)
    
    class Meta:
        db_table = 'preferencias_notificacion'
```

---

## 🔐 SEGURIDAD

### Autenticación
- Contraseñas hasheadas con bcrypt
- Tokens JWT para sesiones
- Protección contra CSRF
- Rate limiting en login

### Autorización
- Middleware de autenticación
- Decoradores @login_required
- Verificación de permisos por hijo (solo ver propios hijos)

### Datos sensibles
- HTTPS obligatorio en producción
- No almacenar datos de tarjetas de crédito
- Encriptar tokens de pago
- Logs de acceso y transacciones

### Validaciones
- Validación de formularios server-side
- Sanitización de inputs
- Protección XSS
- SQL injection prevention (ORM Django)

---

## 📅 CRONOGRAMA DETALLADO

### Semana 1: Fundamentos
**Días 1-2:** Autenticación
- Crear modelos UsuarioPortal, TokenVerificacion
- Implementar registro y login
- Email de verificación
- Recuperación de contraseña

**Días 3-4:** Gestión de hijos
- Dashboard principal
- Lista de hijos y tarjetas
- Vista de detalle de hijo
- Edición de datos básicos

**Día 5:** Consulta de saldo
- API de saldo
- Vista de saldo por hijo
- Gráfico básico de evolución

---

### Semana 2: Funcionalidades core
**Días 1-2:** Historial de consumos
- Vista paginada de consumos
- Filtros por fecha
- Exportar a PDF
- Gráficos de consumo

**Día 3:** Historial de recargas
- Vista paginada de recargas
- Detalles de recarga
- Comprobantes digitalesy Tigo Money ✅
- ✅ **Ambas pasarelas YA integradas** (ahorra 3 días completos)
- Adaptar funciones existentes para portal padres
- Crear tabla TransaccionOnline
- Proceso de recarga paso a paso (UI)
- Confirmación y comprobantes

**Día 3:** Pulido de UX
- Mejorar interfaz de selección de método de pago
- Instrucciones claras para cada método
- Manejo de estados (pendiente, confirmado, fallido)

**Días 4-5:** Testing y deployment
- Pruebas de integración con MetrePay (sandbox)
- Pruebas de integración con Tigo Monete** (ahorra 2 días)
- Adaptar `procesar_pago_metrepay()` para portal padres
- Crear tabla TransaccionOnline
- Proceso de recarga paso a paso (UI)
- Confirmación y comprobante

**Día 3:** Tigo Money (opcional - Fase 2)
- Investigar API de Tigo Money
- Implementación básica si hay tiempo

**Días 4-5:** Testing y ajustes
- Pruebas de integración con MetrePay (sandbox)
- Pruebas de seguridad
- Ajustes de UI/UX
- Documentación

---

## 🧪 TESTING

### Tests unitarios
```python
# tests/test_portal.py
class PortalTestCase(TestCase):
    def test_registro_usuario(self):
        """Test registro de nuevo usuario"""
        
    def test_login_usuario(self):
        """Test login con credenciales válidas"""
        
    def test_consulta_saldo(self):
        """Test consulta de saldo de hijo"""
        
    def test_proceso_recarga(self):
        """Test proceso completo de recarga"""
```

### Tests de integración
- Flujo completo de registro → login → recarga
- Integración con pasarela de pago (sandbox)
- Envío de notificaciones

### Tests de seguridad
- Intentos de SQL injection
- XSS attacks
- CSRF protection
- Rate limiting

---

## 📦 DEPENDENCIAS ADICIONALES

```python
# requirements.txt (añadir)
requests==2.31.0           # Para APIs de pago (✅ ya instalado)
python-decouple==3.8       # Variables de entorno
celery==5.3.0              # Tareas asíncronas (notificaciones)
redis==4.5.5               # Cache y broker para Celery
Pillow==10.0.0             # Procesamiento de imágenes (fotos hijos)
reportlab==4.0.4           # Generación de PDFs
pandas==2.0.3              # Exportar a Excel
django-crispy-forms==2.0   # Formularios bonitos
```

---

## 🚀 DEPLOYMENT

### Configuración de producción
```python
# settings.py - producción
DEBUG = False
ALLOWED_HOSTS = ['portal.cantina.edu.py']
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# MetrePay (✅ ya configurado en .env.production)
METREPAY_API_TOKEN = os.getenv('METREPAY_API_TOKEN')
METREPAY_BASE_URL = os.getenv('METREPAY_BASE_URL', 'https://api.metrepay.com')

# Tigo Money (a configurar)
TIGO_MONEY_API_KEY = os.getenv('TIGO_MONEY_API_KEY')
TIGO_MONEY_MERCHANT_ID = os.getenv('TIGO_MONEY_MERCHANT_ID')
```

### Servidor web
- Nginx como proxy inverso
- Gunicorn para servir Django
- Certificado SSL (Let's Encrypt)

### Base de datos
- MySQL 8.0 (ya configurado)
- Backups automáticos diarios
- Replicación (opcional)

---

## 📈 MÉTRICAS DE ÉXITO

### KPIs a medir
- Número de registros de padres
- % de padres activos mensualmente
- Número de recargas online realizadas
- Monto promedio de recarga
- Tiempo promedio de proceso de recarga
- % de recargas exitosas vs fallidas
- Satisfacción de usuarios (encuestas)

### Analytics
- Google Analytics integrado
- Eventos personalizados (recargas, consultas)
- Funnel de conversión (registro → primera recarga)

---

## 🎨 DISEÑO UI/UX

### Principios de diseño
- **Simple:** Interfaz intuitiva para padres no técnicos
- **Responsive:** Funciona en móvil, tablet y desktop
- **Accesible:** Contraste adecuado, tamaños de fuente legibles
- **Rápido:** Carga rápida, mínimo JavaScript

### Paleta de colores
```css
:root {
    --primary: #2563eb;      /* Azul profesional */
    --secondary: #10b981;    /* Verde éxito */
    --danger: #ef4444;       /* Rojo alerta */
    --warning: #f59e0b;      /* Naranja advertencia */
    --light: #f3f4f6;        /* Fondo claro */
    --dark: #1f2937;         /* Texto oscuro */
}
```

### Componentes clave
- Cards para información de hijos
- Badges para estados (activo, bloqueado)
- Modals para confirmaciones
- Toasts para notificaciones rápidas
- Progress bars para proceso de recarga

---

## 📝 DOCUMENTACIÓN

### Para desarrolladores
- README.md del módulo portal
- Documentación de APIs (Swagger/OpenAPI)
- Diagramas de flujo de procesos
- Guía de deployment

### Para usuarios finales
- Manual de usuario del portal
- FAQs
- Videos tutoriales (opcional)
- Soporte por email/chat

---

## 🔮 FUTURAS MEJORAS (Fase 2)

### Funcionalidades avanzadas
1. **App móvil nativa**
   - iOS y Android
   - Notificaciones push nativas
   - Escaneo QR de tarjetas

2. **Reportes avanzados**
   - Reportes personalizados
   - Comparativas mensuales
   - Alertas inteligentes con ML

3. **Gamificación**
   - Sistema de puntos por consumos saludables
   - Retos y logros
   - Premios y descuentos

4. **Integración con colegios**
   - Menú semanal del comedor
   - Calendario escolar
   - Avisos del colegio

5. **Autorizaciones temporales**
   - Padres autorizan compras específicas
   - Límites temporales por día/semana
   - Control parental de productos

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

### Pre-desarrollo
- [ ] Revisar este plan con stakeholders
- [ ] Aprobar diseño UI/UX
- [ ] Configurar entorno de desarrollo
- [ ] Configurar entorno de staging
- [ ] Obtener credenciales de pasarelas de pago (sandbox)

### Desarrollo - Semana 1
- [ ] Crear modelos nuevos (UsuarioPortal, Token, etc.)
- [ ] Migrar base de datos
- [ ] Implementar registro de usuarios
- [ ] Implementar login/logout
- [ ] Implementar recuperación de contraseña
- [ ] Crear dashboard principal
- [ ] Implementar gestión de hijos
- [ ] Implementar consulta de saldo
- [ ] Tests unitarios semana 1

### Desarrollo - Semana 2
- [ ] Implementar historial de consumos
- [ ] Implementar filtros y paginación
- [ ] Implementar exportar a PDF/Excel
- [ ] Implementar historial de recargas
- [ ] Implementar sistema de notificaciones
- [ ] Configurar envío de emails
- [ ] Implementar preferencias de notificación
- [ ] Tests unitarios semana 2

### Desarrollo - Semana 3 (ahora más corta)
- [x] ~~Integrar pasarelas de pago~~ **✅ MetrePay + Tigo Money ya integrados**
- [ ] Adaptar `procesar_pago_metrepay()` para portal padres
- [ ] Adaptar `procesar_pago_tigo_money()` para portal padres
- [ ] Crear tabla TransaccionOnline
- [ ] Implementar proceso de recarga paso a paso (UI)
- [ ] Selector de método de pago (MetrePay o Tigo Money)
- [ ] Implementar confirmación y comprobantes
- [ ] Manejo de errores de pago
- [ ] Implementar logs de transacciones
- [ ] Tests de integración con ambas pasarelas (sandbox)
- [ ] Tests de seguridad
- [ ] Fix de bugs encontrados

### Testing y QA
- [ ] Testing funcional completo
- [ ] Testing de seguridad
- [ ] Testing de performance
- [ ] Testing en diferentes navegadores
- [ ] Testing responsive (móvil/tablet)
- [ ] User Acceptance Testing (UAT)

### Deployment
- [ ] Configurar servidor de producción
- [ ] Instalar certificado SSL
- [ ] Configurar Nginx
- [ ] Configurar Gunicorn
- [ ] Migrar base de datos a producción
- [ ] Configurar variables de entorno
- [ ] Configurar backups automáticos
- [ ] Configurar monitoreo y logs

### Post-deployment
- [ ] Capacitación a usuarios piloto
- [ ] Monitoreo de errores primeros 3 días
- [ ] Recopilar feedback de usuarios
- [ ] Ajustes basados en feedback
- [ ] Documentación final
- [ ] Celebrar lanzamiento 🎉

---

## 💰 ESTIMACIÓN DE COSTOS

### Desarrollo (Tiempo)
- **1.5-2 semanas de desarrollo:** 80-100 horas ⬇️⬇️
  - ✅ **Ahorro de 4-5 días** por MetrePay + Tigo Money existentes
- **Testing y QA:** +12 horas

### Infraestructura mensual
- **Hosting VPS:** $20-50/mes
- **Certificado SSL:** Gratis (Let's Encrypt)
- **MetrePay:** 2.5-3% por transacción (tarjetas)
- **Tigo Money:** 1-2% por transacción
- **Email service:** $10-20/mes (SendGrid/Mailgun)
- **Backups:** $5-10/mes

### Total estimado
- **One-time:** Desarrollo según tarifa
- **Mensual:** $35-80/mes operación

---

## 📞 CONTACTO Y SOPORTE

### Durante desarrollo
- Reuniones semanales de avance
- Canal de Slack/WhatsApp para dudas
- Demos al final de cada semana

### Post-lanzamiento
- Soporte email: soporte@cantina.edu.py
- Horario: Lunes a viernes 8:00-17:00
- SLA: Respuesta en 24h hábiles

---

## 🎯 CONCLUSIÓN

Este portal web representa una mejora significativa en la experiencia de los padres/responsables, permitiéndoles:

1. ✅ **Transparencia total:** Ver exactamente en qué gastan sus hijos
2. ✅ **Control:** Gestionar saldos y recargas desde casa
3. ✅ **Comodidad:** No necesitar ir presencialmente a recargar
4. ✅ **Seguridad:** Historial completo de todas las operaciones
5. ✅ **Pagos locales:** MetrePay y Tigo Money (métodos paraguayos)

### 🚀 Ventajas competitivas

✅ **MetrePay ya integrado:** Pagos con tarjeta funcionando  
✅ **Tigo Money ya integrado:** Billetera digital lista  
✅ **Métodos de pago paraguayos:** No dependemos de Stripe/PayPal  
✅ **Sistema probado:** Ambas pasarelas funcionan en portal actual  
✅ **Webhooks implementados:** Confirmaciones automáticas de ambos  
✅ **Cobertura total:** 95%+ de usuarios paraguayos cubiertos  

Con una inversión de **1.5-2 semanas** de desarrollo (reducido de 3 semanas originales), se obtiene una plataforma robusta, segura y escalable que mejorará significativamente la adopción y satisfacción del sistema de cantina.

### 📊 Ahorro real

| Concepto | Original | Con ambas pasarelas | Ahorro |
|----------|----------|---------------------|--------|
| Desarrollo recargas online | 3-4 días | 1 día | 2-3 días |
| Integración MetrePay | 2 días | 0 días | 2 días |
| Integración Tigo Money | 2 días | 0 días | 2 días |
| Tests de integración | 1.5 días | 0.5 días | 1 día |
| Documentación API | 0.5 días | 0 días | 0.5 días |
| **TOTAL** | **9-10 días** | **1.5 días** | **7.5-8.5 días** |

**Ahorro en costos:** ~80% en el módulo de pagos 🎉

---

**Fecha de creación:** 2025-01-20  
**Versión:** 1.0  
**Próxima revisión:** Antes de iniciar desarrollo
