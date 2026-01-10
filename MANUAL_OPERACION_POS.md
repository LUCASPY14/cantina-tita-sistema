# MANUAL DE OPERACION Y MANTENIMIENTO - SISTEMA POS

**Versión:** 1.0  
**Última Actualización:** 10 de Enero de 2026  
**Estado:** Producción Ready ✅

---

## 1. INICIO RÁPIDO

### Iniciar el Servidor
```bash
cd D:\anteproyecto20112025
.\.venv\Scripts\Activate.ps1
python manage.py runserver 0.0.0.0:8000
```

### Acceder al POS
```
URL: http://localhost:8000/pos/
Usuario: Automático (sin login requerido para POS)
```

### Cerrar el Servidor
```bash
Ctrl + C en la terminal
```

---

## 2. FLUJO DE OPERACIÓN DEL POS

### Paso 1: Verificar Tarjeta
1. Ingrese número de tarjeta en campo "Nro. Tarjeta"
2. Presione Enter o botón "Verificar Tarjeta"
3. El sistema cargará datos del estudiante (nombre, saldo, grado)
4. Cualquier restricción alimentaria se mostrará

### Paso 2: Agregar Productos
1. En la sección "Productos", busque por nombre
2. Haga clic en producto para agregarlo al carrito
3. Ajuste cantidad si es necesario
4. El carrito se actualiza automáticamente

### Paso 3: Revisar Carrito
1. Carrito muestra: producto, cantidad, precio unitario, subtotal
2. Verificar total en la sección "Totales"
3. Opción de eliminar items si es necesario

### Paso 4: Seleccionar Medio de Pago
1. Dropdown "Medio de Pago" ofrece 6 opciones:
   - Efectivo
   - Transferencia
   - Débito/QR
   - Crédito/QR
   - Giros TIGO
   - Tarjeta Estudiantil
2. Seleccione el medio utilizado

### Paso 5: Procesar Venta
1. Botón "PROCESAR PAGO" (color verde)
2. Sistema valida todo automáticamente
3. En caso de error, mostrará mensaje
4. Éxito: abre PDF del ticket automáticamente

### Paso 6: Imprimir Ticket
1. PDF se abre en ventana emergente
2. Presione Ctrl+P o botón imprimir del navegador
3. Seleccione impresora térmica (80mm)
4. Presione "Imprimir"

---

## 3. FUNCIONALIDADES CLAVE

### Validaciones Automáticas
- ✅ Verifica que tarjeta exista y esté activa
- ✅ Verifica que productos estén en stock
- ✅ Verifica que suma de pagos = total
- ✅ Valida medio de pago
- ✅ Detecta restricciones alimentarias
- ✅ Actualiza stock automáticamente

### Medios de Pago Soportados
```
1. Efectivo              (Pago inmediato)
2. Transferencia         (Requiere comprobante)
3. Débito/QR             (Lector QR)
4. Crédito/QR            (Lector QR)
5. Giros TIGO            (Código de giro)
6. Tarjeta Estudiantil   (Saldo de tarjeta)
```

### Stock y Inventario
- Stock actualiza automáticamente al procesar venta
- Permite stock negativo si está configurado
- Muestra stock disponible en búsqueda de productos

---

## 4. ENDPOINTS API (para desarrollo)

### Buscar Tarjeta
```
POST /pos/buscar-tarjeta/
Content-Type: application/json

{
    "nro_tarjeta": "00203"
}

Response: {
    "success": true,
    "id_hijo": 11,
    "nombre_estudiante": "ROMINA MONGELOS",
    "saldo": 1000,
    "grado": "2do A",
    "restricciones": []
}
```

### Buscar Producto
```
POST /pos/buscar-producto/
Content-Type: application/json

{
    "query": "coca",
    "limite": 10
}

Response: {
    "success": true,
    "productos": [
        {
            "id": 12,
            "descripcion": "COCA COLA 250 ML",
            "precio": 5000,
            "stock": 45.0
        }
    ],
    "total": 1
}
```

### Procesar Venta
```
POST /pos/procesar-venta/
Content-Type: application/json

{
    "id_hijo": 11,
    "productos": [
        {
            "id_producto": 12,
            "cantidad": 1,
            "precio_unitario": 5000
        }
    ],
    "pagos": [
        {
            "id_medio_pago": 1,
            "monto": 5000,
            "nro_tarjeta": "00203"
        }
    ],
    "tipo_venta": "CONTADO",
    "emitir_factura": false,
    "medio_pago_id": 1
}

Response: {
    "success": true,
    "id_venta": 95,
    "monto_total": 5000,
    "nro_factura": null,
    "mensaje": "✅ Venta procesada exitosamente"
}
```

### Obtener Ticket PDF
```
GET /pos/ticket/95/

Response: PDF (application/pdf)
```

---

## 5. MANTENIMIENTO Y DIAGNOSTICO

### Ver Ventas Recientes
```bash
python manage.py shell
>>> from gestion.models import Ventas
>>> Ventas.objects.order_by('-id_venta')[:10]
```

### Ver Detalles de Venta
```bash
>>> venta = Ventas.objects.get(id_venta=95)
>>> venta.detalles.all()
>>> venta.pagos.all()
```

### Actualizar Stock
```bash
>>> from gestion.models import Producto, StockUnico
>>> p = Producto.objects.get(id_producto=12)
>>> p.stock.stock_actual = 100
>>> p.stock.save()
```

### Crear Cliente Público (si falta)
```bash
python crear_datos_iniciales.py
```

### Ejecutar Tests
```bash
# Test completo de endpoints
python test_endpoints_completos.py

# Test de auditoría
python auditoria_completa.py

# Test específico de procesar venta
python test_procesar_venta.py
```

---

## 6. TROUBLESHOOTING

### "Tarjeta no encontrada"
**Causa:** La tarjeta no existe o está inactiva  
**Solución:**
```bash
python manage.py shell
>>> from gestion.models import Tarjeta
>>> Tarjeta.objects.filter(estado='Activa')  # Ver tarjetas activas
>>> t = Tarjeta.objects.get(nro_tarjeta='00203')
>>> t.estado = 'Activa'  # Activar si está inactiva
>>> t.save()
```

### "Cliente público no configurado"
**Causa:** No existe cliente llamado "público"  
**Solución:**
```bash
python crear_datos_iniciales.py
```

### "Stock insuficiente"
**Causa:** Producto no tiene stock disponible  
**Solución:**
```bash
python manage.py shell
>>> from gestion.models import Producto
>>> p = Producto.objects.get(id_producto=12)
>>> p.stock.stock_actual = 50
>>> p.stock.save()
```

### "Venta no se procesa"
**Causa:** Error en validación  
**Solución:** Ver mensaje de error y revisar:
- Tarjeta activa: ✓
- Productos en stock: ✓
- Total de pagos = total venta: ✓
- Medio de pago válido: ✓

### "PDF no genera"
**Causa:** Problema con ReportLab  
**Solución:**
```bash
pip install reportlab --upgrade
python manage.py runserver
```

---

## 7. MONITOREO

### Verificar Salud del Sistema
```bash
python manage.py check
```

### Ver Queries Ejecutadas (DEBUG)
En `cantina_project/settings.py`:
```python
DEBUG = True  # Para desarrollo
DEBUG = False # Para producción
```

### Logs de Servidor
Revisar errores en:
- Terminal donde corre `manage.py runserver`
- Base de datos error logs

---

## 8. COPIA DE SEGURIDAD

### Backup de Base de Datos
```bash
# Exportar BD MySQL
mysqldump -u root -p nombre_bd > backup_$(date +%Y%m%d).sql

# Restaurar
mysql -u root -p nombre_bd < backup_20260110.sql
```

### Backup de Archivos Críticos
```bash
# Carpetas importantes
- gestion/
- templates/pos/
- cantina_project/
- manage.py
- requirements.txt
```

---

## 9. SEGURIDAD

### Contraseñas (Django)
```bash
# Crear superusuario
python manage.py createsuperuser

# Acceder a admin
http://localhost:8000/admin/
```

### CSRF Token
- Automático en formularios Django
- Para APIs: incluir `X-CSRFToken` header

### SQL Injection
- Django ORM previene automáticamente
- Nunca usar concatenación directa en queries

---

## 10. METRICAS Y REPORTES

### Ventas por Día
```bash
python manage.py shell
>>> from django.db.models import Sum
>>> from gestion.models import Ventas
>>> from datetime import date
>>> Ventas.objects.filter(fecha__date=date(2026,1,10)).aggregate(Sum('monto_total'))
```

### Productos Más Vendidos
```bash
>>> from gestion.models import DetalleVenta
>>> DetalleVenta.objects.values('id_producto__descripcion').annotate(total=Sum('cantidad')).order_by('-total')[:10]
```

### Ingresos por Medio de Pago
```bash
>>> from gestion.models import PagosVenta
>>> PagosVenta.objects.values('id_medio_pago__descripcion').annotate(total=Sum('monto_aplicado')).order_by('-total')
```

---

## 11. PRÓXIMAS MEJORAS PLANEADAS

- [ ] Validación de restricciones alimentarias
- [ ] Integración con factura electrónica (SET)
- [ ] Dashboard de ventas en tiempo real
- [ ] Reportes PDF automáticos
- [ ] Notificaciones por email
- [ ] Integración con sistema de pagos en línea

---

## 12. CONTACTO Y SOPORTE

**Sistema:** POS Bootstrap - Cantina Escolar  
**Versión:** 1.0  
**Desarrollador:** Sistema de Desarrollo Automatizado  
**Fecha:** 10 de Enero de 2026

Para reportar problemas o solicitar mejoras, documentar:
1. Pasos para reproducir
2. Mensaje de error exacto
3. Usuario/Tarjeta utilizada
4. Fecha y hora del incidente

---

✅ **MANUAL DE OPERACION COMPLETO**
