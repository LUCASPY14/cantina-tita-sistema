# Corrección: Error al Verificar Tarjeta en POS Bootstrap

## Problema Reportado
```
Error al verificar tarjeta: Invalid field name(s) given in select_related: 'id_cliente'. 
Choices are: id_cliente_responsable
```

## Root Cause
La relación de modelos Django estaba mal mapeada:
- **Incorrecto**: `Tarjeta.select_related('id_hijo', 'id_hijo__id_cliente')`
- **Correcto**: `Tarjeta.select_related('id_hijo', 'id_hijo__id_cliente_responsable')`

### Estructura Correcta de Relaciones
```
Tarjeta
  ├── id_hijo (OneToOneField → Hijo)
  │   └── id_cliente_responsable (ForeignKey → Cliente)
  │       └── nombre_completo
```

## Cambios Realizados

### 1. Archivo: `gestion/pos_general_views.py` (Líneas 166-239)
**Función**: `verificar_tarjeta_api(request)`

#### Antes:
```python
tarjeta = Tarjeta.objects.filter(
    nro_tarjeta=nro_tarjeta,
    estado='Activa'
).select_related('id_hijo', 'id_hijo__id_cliente').first()  # ❌ INCORRECTO

return JsonResponse({
    'success': True,
    'estudiante': {
        'cliente': tarjeta.id_hijo.id_cliente.nombre_completo,  # ❌ FALLA
    }
})
```

#### Después:
```python
tarjeta = Tarjeta.objects.select_related(
    'id_hijo',
    'id_hijo__id_cliente_responsable'  # ✅ CORRECTO
).filter(
    nro_tarjeta=nro_tarjeta,
    estado='Activa'
).first()

return JsonResponse({
    'success': True,
    'estudiante': {
        'id_hijo': tarjeta.id_hijo.id_hijo,
        'nombre': f"{tarjeta.id_hijo.nombre} {tarjeta.id_hijo.apellido}",
        'saldo': int(tarjeta.saldo_actual),
        'grado': tarjeta.id_hijo.grado or 'N/A',
        'cliente': tarjeta.id_hijo.id_cliente_responsable.nombre_completo,  # ✅ FUNCIONA
        'nro_tarjeta': tarjeta.nro_tarjeta,
        'foto_perfil': tarjeta.id_hijo.foto_perfil or None,
        'restricciones': restricciones
    }
})
```

### 2. Archivo: `gestion/pos_urls.py` (Líneas 10-24)
**Problema**: Había dos rutas `buscar-tarjeta/` que se pisaban mutuamente

#### Antes:
```python
path('buscar-tarjeta/', pos_general_views.verificar_tarjeta_api, name='buscar_tarjeta_api'),
# ... otras rutas ...
path('buscar-tarjeta/', pos_views.buscar_tarjeta, name='buscar_tarjeta'),  # ❌ DUPLICADA
```

#### Después:
```python
# APIs de la interfaz POS mejorada (Bootstrap 5)
path('buscar-tarjeta/', pos_general_views.verificar_tarjeta_api, name='buscar_tarjeta'),
path('buscar-producto/', pos_general_views.buscar_producto_api, name='buscar_producto'),
path('procesar-venta/', pos_general_views.procesar_venta_api, name='procesar_venta_api'),
path('ticket/<int:id_venta>/', pos_general_views.imprimir_ticket_venta, name='ticket_api'),

# Legacy routes (renombradas para evitar conflictos)
path('procesar-venta-legacy/', pos_views.procesar_venta, name='procesar_venta_legacy'),
path('ticket-legacy/<int:venta_id>/', pos_views.ticket_view, name='ticket_legacy'),
```

### 3. Archivo: `templates/pos/pos_bootstrap.html` (Lines ~320-380)
**Mejora**: Mejor visualización de datos de tarjeta con restricciones

#### Mostraba:
```javascript
<strong>✓ Juan Pérez</strong>
Saldo: Gs. 50,000
```

#### Ahora muestra:
```javascript
<strong>✓ Juan Pérez</strong>
Grado: 5to Grado
Responsable: María Pérez
Saldo: Gs. 50,000

⚠️ Restricciones:
• Alergia al maní (Severa)
• Celíaco (Moderada)
```

## Estructura de Respuesta API

**Endpoint**: `POST /pos/buscar-tarjeta/`

**Request**:
```json
{
  "nro_tarjeta": "01024"
}
```

**Response Success**:
```json
{
  "success": true,
  "estudiante": {
    "id_hijo": 10,
    "nombre": "PEDRO PERÉZ",
    "saldo": 125000,
    "grado": "5to Grado",
    "cliente": "María Peréz (Madre)",
    "nro_tarjeta": "01024",
    "foto_perfil": "hijos/foto_pedido_123.jpg",
    "restricciones": [
      {
        "tipo_restriccion": "Alergia al maní",
        "descripcion": "Alergia comprobada",
        "severidad": "Severa"
      }
    ]
  }
}
```

**Response Error**:
```json
{
  "success": false,
  "error": "Tarjeta no encontrada o inactiva"
}
```

## Testing Validado

✅ Tarjeta `01024` se verifica correctamente
✅ Datos del estudiante se cargan sin errores
✅ Restricciones se muestran correctamente
✅ Carrito maneja datos correctamente
✅ Rutas consolidadas sin conflictos
✅ API retorna JSON válido

## Cómo Probar

1. Ir a http://localhost:8000/pos/
2. Escribir un número de tarjeta: `01024`
3. Presionar Enter
4. Debería mostrar los datos del estudiante sin errores

## Notas Importantes

- La relación `id_cliente_responsable` viene del modelo `Hijo`, no directamente de `Tarjeta`
- El anterior `pos_views.py` usaba la estructura correcta: `id_hijo__id_cliente_responsable`
- Las restricciones se cargan desde `RestriccionesHijos` relacionadas al `Hijo`
- El saldo viene del campo `Tarjeta.saldo_actual`

## Archivos Modificados

1. ✅ `gestion/pos_general_views.py` - Corrección select_related y respuesta JSON
2. ✅ `gestion/pos_urls.py` - Eliminación de rutas duplicadas
3. ✅ `templates/pos/pos_bootstrap.html` - Mejora visualización de restricciones
