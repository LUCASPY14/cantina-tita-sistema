# gestion/models/__init__.py
# Importar todos los modelos para acceso directo
from .base import ManagedModel
from .catalogos import *
from .clientes import *
from .productos import *
from .empleados import *
from .tarjetas import *
from .ventas import *
from .compras import *
from .fiscal import *
from .almuerzos import *
from .seguridad import *
from .portal import *
from .promociones import *
from .alergenos import *
from .vistas import *

# Asegurar que se importen todas las clases necesarias
__all__ = [
    # Base
    'ManagedModel',
    
    # Catálogos
    'TipoCliente', 'ListaPrecios', 'Categoria', 'UnidadMedida', 'Impuesto',
    'TipoRolGeneral', 'TiposPago', 'MediosPago', 'TarifasComision', 'Grado',
    
    # Clientes
    'Cliente', 'Hijo', 'RestriccionesHijos',
    
    # Productos
    'Producto', 'StockUnico', 'PreciosPorLista', 'CostosHistoricos',
    'HistoricoPrecios', 'MovimientosStock',
    
    # Empleados
    'Empleado',
    
    # Tarjetas
    'Tarjeta', 'ConsumoTarjeta', 'CargasSaldo',
    
    # Ventas
    'Ventas', 'DetalleVenta', 'PagosVenta', 'AplicacionPagosVentas',
    'DetalleComisionVenta', 'NotasCreditoCliente', 'DetalleNota',
    'AutorizacionSaldoNegativo',
    
    # Compras (incluye ConciliacionPagos)
    'Proveedor', 'Compras', 'DetalleCompra', 'NotasCreditoProveedor',
    'DetalleNotaCreditoProveedor', 'PagosProveedores', 'AplicacionPagosCompras',
    'ConciliacionPagos',
    
    # Fiscal
    'DatosEmpresa', 'PuntosExpedicion', 'Timbrados', 'DocumentosTributarios',
    'DatosFacturacionElect', 'DatosFacturacionFisica', 'Cajas', 'CierresCaja',
    
    # Almuerzos
    'TipoAlmuerzo', 'PlanesAlmuerzo', 'SuscripcionesAlmuerzo',
    'PagosAlmuerzoMensual', 'RegistroConsumoAlmuerzo', 'CuentaAlmuerzoMensual',
    'PagoCuentaAlmuerzo',
    
    # Seguridad
    'LogAutorizacion', 'TarjetaAutorizacion', 'HistorialGradoHijo',
    'IntentoLogin', 'AuditoriaOperacion', 'AuditoriaEmpleados',
    'AuditoriaUsuariosWeb', 'AuditoriaComisiones', 'TokenRecuperacion',
    'BloqueoCuenta', 'PatronAcceso', 'AnomaliaDetectada', 'SesionActiva',
    'Autenticacion2Fa', 'RestriccionHoraria', 'Intento2Fa', 'RenovacionSesion',
    'AjustesInventario', 'DetalleAjuste',
    
    # Portal
    'UsuariosWebClientes', 'UsuarioPortal', 'TokenVerificacion',
    'TransaccionOnline', 'Notificacion', 'PreferenciaNotificacion',
    'NotificacionSaldo', 'AlertasSistema', 'SolicitudesNotificacion',
    
    # Promociones
    'Promocion', 'ProductoPromocion', 'CategoriaPromocion', 'PromocionAplicada',
    
    # Alérgenos
    'Alergeno', 'ProductoAlergeno',
    
    # Vistas
    'VistaStockAlerta', 'VistaSaldoClientes', 'VistaVentasDiaDetallado',
    'VistaConsumosEstudiante', 'VistaStockCriticoAlertas',
    'VistaRecargasHistorial', 'VistaResumenCajaDiario',
    'VistaNotasCreditoDetallado', 'VistaAlmuerzosDiarios',
    'VistaCuentasAlmuerzoDetallado', 'VistaReporteMensualSeparado',
]