#!/usr/bin/env python
"""
Script para ayudar a alcanzar 100% de modelos correctos
Opciones:
1. Generar scripts SQL para crear tablas faltantes
2. Generar migraciones de Django
3. Marcar modelos como managed=False (desactivarlos)
"""

# Categorías de modelos faltantes
MODELOS_FALTANTES = {
    'PRIORIDAD_ALTA': {
        'Almuerzos': [
            'TipoAlmuerzo', 'PlanesAlmuerzo', 'SuscripcionesAlmuerzo',
            'PagosAlmuerzoMensual', 'CuentaAlmuerzoMensual', 
            'RegistroConsumoAlmuerzo', 'PagoCuentaAlmuerzo'
        ],
        'Cajas_Facturacion': [
            'Cajas', 'CierresCaja', 'DatosEmpresa', 
            'DatosFacturacionElect', 'DatosFacturacionFisica'
        ],
        'Inventario': [
            'StockUnico', 'MovimientosStock', 'CostosHistoricos', 'ProductoAlergeno'
        ],
        'Tarjetas_Recargas': [
            'CargasSaldo', 'ConsumoTarjeta'
        ],
        'Notas_Credito': [
            'NotasCreditoCliente', 'DetalleNota',
            'NotasCreditoProveedor', 'DetalleNotaCreditoProveedor'
        ],
        'Ventas_Comisiones': [
            'DetalleComisionVenta', 'AutorizacionSaldoNegativo', 'PromocionAplicada'
        ],
        'Catalogos': [
            'TarifasComision', 'Grado'
        ],
        'Clientes': [
            'RestriccionesHijos'
        ],
        'Compras': [
            'ConciliacionPagos'
        ]
    },
    'PRIORIDAD_MEDIA': {
        'Seguridad_Auditoria': [
            'IntentoLogin', 'AuditoriaOperacion', 'AuditoriaEmpleados',
            'AuditoriaComisiones', 'AuditoriaUsuariosWeb', 'BloqueoCuenta',
            'AnomaliaDetectada', 'PatronAcceso', 'AlertasSistema', 'DetalleAjuste'
        ],
        'Autenticacion_2FA': [
            'Autenticacion2Fa', 'Intento2Fa', 'SesionActiva',
            'RestriccionHoraria', 'RenovacionSesion', 'TokenRecuperacion'
        ]
    },
    'PRIORIDAD_BAJA': {
        'Portal_Web': [
            'UsuariosWebClientes', 'UsuarioPortal', 'TokenVerificacion',
            'TransaccionOnline'
        ],
        'Notificaciones_Portal': [
            'PreferenciaNotificacion', 'Notificacion', 'NotificacionSaldo',
            'SolicitudesNotificacion'
        ],
        'Vistas_Reportes': [
            'VistaStockAlerta', 'VistaSaldoClientes', 'VistaConsumosEstudiante',
            'VistaStockCriticoAlertas', 'VistaVentasDiaDetallado',
            'VistaRecargasHistorial', 'VistaResumenCajaDiario',
            'VistaNotasCreditoDetallado', 'VistaAlmuerzosDiarios',
            'VistaCuentasAlmuerzoDetallado', 'VistaReporteMensualSeparado'
        ]
    }
}

def mostrar_menu():
    print("\n" + "="*70)
    print("🎯 AYUDA PARA ALCANZAR 100% DE MODELOS CORRECTOS")
    print("="*70)
    print("\nESTADO ACTUAL: 37/101 modelos correctos (36%)")
    print("FALTANTES: 64 modelos sin tabla en MySQL")
    print("\n" + "-"*70)
    print("\nOPCIONES:")
    print("1. 📊 Ver resumen detallado por categoría")
    print("2. 🔨 Generar migraciones de Django (recomendado)")
    print("3. 📝 Generar scripts SQL directos")
    print("4. ⚙️  Marcar modelos como managed=False (desactivar)")
    print("5. 🎯 Generar solo categoría específica")
    print("0. ❌ Salir")
    print("-"*70)

def mostrar_resumen():
    print("\n" + "="*70)
    print("📊 RESUMEN DE MODELOS FALTANTES")
    print("="*70)
    
    total = 0
    for prioridad, categorias in MODELOS_FALTANTES.items():
        print(f"\n🔸 {prioridad.replace('_', ' ')}")
        print("-" * 70)
        subtotal = 0
        for categoria, modelos in categorias.items():
            count = len(modelos)
            subtotal += count
            print(f"  • {categoria.replace('_', ' ')}: {count} modelos")
        print(f"  └─ Subtotal: {subtotal} modelos")
        total += subtotal
    
    print("\n" + "="*70)
    print(f"TOTAL: {total} modelos sin tabla")
    print("="*70)

def mostrar_categorias():
    print("\n📁 CATEGORÍAS DISPONIBLES:")
    print("-" * 70)
    idx = 1
    categorias_map = {}
    for prioridad, cats in MODELOS_FALTANTES.items():
        for categoria, modelos in cats.items():
            print(f"{idx}. {categoria.replace('_', ' ')} ({len(modelos)} modelos)")
            categorias_map[idx] = (prioridad, categoria, modelos)
            idx += 1
    return categorias_map

def generar_comando_migracion(modelos_seleccionados):
    """Genera comandos para crear migraciones de Django"""
    print("\n" + "="*70)
    print("🔨 COMANDOS PARA GENERAR MIGRACIONES")
    print("="*70)
    
    print("\n# Paso 1: Asegúrate que los modelos tengan managed=True")
    print("# (Ya deberían tenerlo en tu código)")
    
    print("\n# Paso 2: Genera las migraciones")
    print("python manage.py makemigrations gestion")
    
    print("\n# Paso 3: Revisa las migraciones generadas")
    print("# Se crearán en: backend/gestion/migrations/")
    
    print("\n# Paso 4: Aplica las migraciones")
    print("python manage.py migrate gestion")
    
    print("\n# Paso 5: Verifica que las tablas se crearon")
    print("python manage.py dbshell")
    print("SHOW TABLES;")
    
    print("\n💡 NOTA: Django creará automáticamente las tablas basándose")
    print("   en los modelos definidos en tu código.")
    print("="*70)

def generar_sql_ejemplo():
    """Genera ejemplo de SQL para crear tablas"""
    print("\n" + "="*70)
    print("📝 EJEMPLO: SQL PARA CREAR TABLAS")
    print("="*70)
    
    print("""
-- Ejemplo: Crear tabla para TipoAlmuerzo
CREATE TABLE tipos_almuerzo (
    id_tipo_almuerzo INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    precio_unitario DECIMAL(12, 2) NOT NULL,
    activo TINYINT(1) DEFAULT 1,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Ejemplo: Crear tabla para CargasSaldo
CREATE TABLE cargas_saldo (
    id_carga BIGINT AUTO_INCREMENT PRIMARY KEY,
    nro_tarjeta VARCHAR(20) NOT NULL,
    id_cliente_origen INT,
    fecha_carga DATETIME DEFAULT CURRENT_TIMESTAMP,
    monto_cargado BIGINT NOT NULL,
    referencia VARCHAR(100),
    FOREIGN KEY (nro_tarjeta) REFERENCES tarjetas(nro_tarjeta),
    FOREIGN KEY (id_cliente_origen) REFERENCES clientes(id_cliente)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

💡 RECOMENDACIÓN: Es mejor usar migraciones de Django (opción 2)
   Django generará el SQL automáticamente basándose en tus modelos.
""")
    print("="*70)

def marcar_como_no_administrados():
    """Genera código para marcar modelos como managed=False"""
    print("\n" + "="*70)
    print("⚙️  DESACTIVAR MODELOS (managed=False)")
    print("="*70)
    
    print("""
Si NO necesitas estos modelos, puedes desactivarlos cambiando:

    class Meta:
        managed = True      # ← Cambiar esto
        db_table = 'tabla'
        
A:

    class Meta:
        managed = False     # ← Django ignora este modelo
        db_table = 'tabla'

Esto evitará que Django intente crear/migrar estas tablas.

⚠️  ADVERTENCIA: Perderás estas funcionalidades si las desactivas.
    Solo hazlo si estás SEGURO que no las necesitas.

Archivos a editar:
- backend/gestion/models/almuerzos.py
- backend/gestion/models/seguridad.py  
- backend/gestion/models/portal.py
- backend/gestion/models/fiscal.py
- etc.
""")
    print("="*70)

def main():
    while True:
        mostrar_menu()
        opcion = input("\nSelecciona una opción: ").strip()
        
        if opcion == '0':
            print("\n👋 ¡Hasta luego!")
            break
            
        elif opcion == '1':
            mostrar_resumen()
            
        elif opcion == '2':
            generar_comando_migracion([])
            
        elif opcion == '3':
            generar_sql_ejemplo()
            
        elif opcion == '4':
            marcar_como_no_administrados()
            
        elif opcion == '5':
            categorias_map = mostrar_categorias()
            cat_num = input("\n¿Qué categoría quieres procesar? (número): ").strip()
            try:
                cat_num = int(cat_num)
                if cat_num in categorias_map:
                    prioridad, categoria, modelos = categorias_map[cat_num]
                    print(f"\n✅ Seleccionaste: {categoria.replace('_', ' ')}")
                    print(f"   Modelos ({len(modelos)}):")
                    for modelo in modelos:
                        print(f"   • {modelo}")
                    print("\n💡 Usa la opción 2 para generar migraciones para estos modelos")
                else:
                    print("❌ Número inválido")
            except ValueError:
                print("❌ Por favor ingresa un número")
        else:
            print("❌ Opción inválida")
        
        input("\nPresiona ENTER para continuar...")

if __name__ == '__main__':
    main()
