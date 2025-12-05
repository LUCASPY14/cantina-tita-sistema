from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# =============================================================================
# MODELOS DE LA BASE DE DATOS EXISTENTE
# Estos modelos usan managed=False para mapear a tablas existentes sin modificarlas
# =============================================================================

# ==================== TIPOS Y CATÁLOGOS ====================

class TipoCliente(models.Model):
    '''Tabla tipos_cliente - Tipos de cliente existentes'''
    id_tipo_cliente = models.AutoField(db_column='ID_Tipo_Cliente', primary_key=True)
    nombre_tipo = models.CharField(db_column='Nombre_Tipo', max_length=50, unique=True)
    descripcion = models.CharField(db_column='Descripcion', max_length=100, blank=True, null=True)
    activo = models.BooleanField(db_column='Activo', default=True)

    class Meta:
        managed = False
        db_table = 'tipos_cliente'
        verbose_name = 'Tipo de Cliente'
        verbose_name_plural = 'Tipos de Cliente'

    def __str__(self):
        return self.nombre_tipo


class ListaPrecios(models.Model):
    '''Tabla listas_precios - Listas de precios'''
    id_lista = models.AutoField(db_column='ID_Lista', primary_key=True)
    nombre_lista = models.CharField(db_column='Nombre_Lista', max_length=100, unique=True)
    fecha_vigencia = models.DateField(db_column='Fecha_Vigencia', blank=True, null=True)
    moneda = models.CharField(db_column='Moneda', max_length=3, default='PYG')
    activo = models.BooleanField(db_column='Activo', default=True)

    class Meta:
        managed = False
        db_table = 'listas_precios'
        verbose_name = 'Lista de Precios'
        verbose_name_plural = 'Listas de Precios'

    def __str__(self):
        return self.nombre_lista


class Categoria(models.Model):
    '''Tabla categorias - Categorías de productos'''
    id_categoria = models.AutoField(db_column='ID_Categoria', primary_key=True)
    nombre = models.CharField(db_column='Nombre', max_length=100)
    id_categoria_padre = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        db_column='ID_Categoria_Padre',
        blank=True, 
        null=True,
        related_name='subcategorias'
    )
    activo = models.BooleanField(db_column='Activo', default=True)

    class Meta:
        managed = False
        db_table = 'categorias'
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'

    def __str__(self):
        return self.nombre


class UnidadMedida(models.Model):
    '''Tabla unidades_medida'''
    id_unidad_de_medida = models.AutoField(db_column='ID_Unidad_de_Medida', primary_key=True)
    nombre = models.CharField(db_column='Nombre', max_length=50)
    abreviatura = models.CharField(db_column='Abreviatura', max_length=10)
    activo = models.BooleanField(db_column='Activo', default=True)

    class Meta:
        managed = False
        db_table = 'unidades_medida'
        verbose_name = 'Unidad de Medida'
        verbose_name_plural = 'Unidades de Medida'

    def __str__(self):
        return f'{self.nombre} ({self.abreviatura})'


class Impuesto(models.Model):
    '''Tabla impuestos'''
    id_impuesto = models.AutoField(db_column='ID_Impuesto', primary_key=True)
    nombre_impuesto = models.CharField(db_column='Nombre_Impuesto', max_length=50, unique=True)
    porcentaje = models.DecimalField(db_column='Porcentaje', max_digits=4, decimal_places=2)
    vigente_desde = models.DateField(db_column='Vigente_Desde')
    vigente_hasta = models.DateField(db_column='Vigente_Hasta', blank=True, null=True)
    activo = models.BooleanField(db_column='Activo', default=True)

    class Meta:
        managed = False
        db_table = 'impuestos'
        verbose_name = 'Impuesto'
        verbose_name_plural = 'Impuestos'

    def __str__(self):
        return f'{self.nombre_impuesto} ({self.porcentaje}%)'


class TipoRolGeneral(models.Model):
    '''Tabla tipos_rol_general'''
    id_rol = models.AutoField(db_column='ID_Rol', primary_key=True)
    nombre_rol = models.CharField(db_column='Nombre_Rol', max_length=50, unique=True)
    descripcion = models.CharField(db_column='Descripcion', max_length=100, blank=True, null=True)
    activo = models.BooleanField(db_column='Activo', default=True)

    class Meta:
        managed = False
        db_table = 'tipos_rol_general'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.nombre_rol


# ==================== CLIENTES ====================

class Cliente(models.Model):
    '''Tabla clientes - Clientes existentes en la BD'''
    id_cliente = models.AutoField(db_column='ID_Cliente', primary_key=True)
    id_lista = models.ForeignKey(
        ListaPrecios, 
        on_delete=models.PROTECT, 
        db_column='ID_Lista'
    )
    id_tipo_cliente = models.ForeignKey(
        TipoCliente, 
        on_delete=models.PROTECT, 
        db_column='ID_Tipo_Cliente'
    )
    nombres = models.CharField(db_column='Nombres', max_length=100)
    apellidos = models.CharField(db_column='Apellidos', max_length=100)
    razon_social = models.CharField(db_column='Razon_Social', max_length=255, blank=True, null=True)
    ruc_ci = models.CharField(db_column='Ruc_CI', max_length=20, unique=True)
    direccion = models.CharField(db_column='Direccion', max_length=255, blank=True, null=True)
    ciudad = models.CharField(db_column='Ciudad', max_length=100, blank=True, null=True)
    telefono = models.CharField(db_column='Telefono', max_length=20, blank=True, null=True)
    email = models.EmailField(db_column='Email', blank=True, null=True)
    limite_credito = models.DecimalField(db_column='Limite_Credito', max_digits=12, decimal_places=2, blank=True, null=True)
    activo = models.BooleanField(db_column='Activo', default=True)
    fecha_registro = models.DateTimeField(db_column='Fecha_Registro', auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'clientes'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return f'{self.apellidos}, {self.nombres} ({self.ruc_ci})'

    @property
    def nombre_completo(self):
        return f'{self.nombres} {self.apellidos}'


class Hijo(models.Model):
    '''Tabla hijos - Hijos de clientes para control de almuerzos'''
    id_hijo = models.AutoField(db_column='ID_Hijo', primary_key=True)
    id_cliente_responsable = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        db_column='ID_Cliente_Responsable',
        related_name='hijos'
    )
    nombre = models.CharField(db_column='Nombre', max_length=100)
    apellido = models.CharField(db_column='Apellido', max_length=100)
    fecha_nacimiento = models.DateField(db_column='Fecha_Nacimiento', blank=True, null=True)
    activo = models.BooleanField(db_column='Activo', default=True)

    class Meta:
        managed = False
        db_table = 'hijos'
        verbose_name = 'Hijo'
        verbose_name_plural = 'Hijos'

    def __str__(self):
        return f'{self.apellido}, {self.nombre}'

    @property
    def nombre_completo(self):
        return f'{self.nombre} {self.apellido}'


class Tarjeta(models.Model):
    '''Tabla tarjetas - Tarjetas de estudiantes'''
    ESTADO_CHOICES = [
        ('Activa', 'Activa'),
        ('Bloqueada', 'Bloqueada'),
        ('Vencida', 'Vencida'),
    ]

    nro_tarjeta = models.CharField(db_column='Nro_Tarjeta', max_length=20, primary_key=True)
    id_hijo = models.OneToOneField(
        Hijo,
        on_delete=models.PROTECT,
        db_column='ID_Hijo',
        unique=True
    )
    saldo_actual = models.BigIntegerField(db_column='Saldo_Actual', default=0)
    estado = models.CharField(db_column='Estado', max_length=20, choices=ESTADO_CHOICES, default='Activa')
    fecha_vencimiento = models.DateField(db_column='Fecha_Vencimiento', blank=True, null=True)
    saldo_alerta = models.DecimalField(db_column='Saldo_Alerta', max_digits=10, decimal_places=2, blank=True, null=True)
    fecha_creacion = models.DateTimeField(db_column='Fecha_Creacion', auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'tarjetas'
        verbose_name = 'Tarjeta'
        verbose_name_plural = 'Tarjetas'

    def __str__(self):
        return f'{self.nro_tarjeta} - {self.id_hijo.nombre_completo}'


# ==================== PRODUCTOS ====================

class Producto(models.Model):
    '''Tabla productos - Productos existentes en la BD'''
    id_producto = models.AutoField(db_column='ID_Producto', primary_key=True)
    id_categoria = models.ForeignKey(
        Categoria, 
        on_delete=models.PROTECT, 
        db_column='ID_Categoria',
        related_name='productos'
    )
    id_unidad_de_medida = models.ForeignKey(
        UnidadMedida, 
        on_delete=models.PROTECT, 
        db_column='ID_Unidad_de_Medida'
    )
    id_impuesto = models.ForeignKey(
        Impuesto, 
        on_delete=models.PROTECT, 
        db_column='ID_Impuesto'
    )
    codigo_barra = models.CharField(db_column='Codigo_Barra', max_length=50, unique=True, blank=True, null=True)
    descripcion = models.CharField(db_column='Descripcion', max_length=255)
    stock_minimo = models.DecimalField(db_column='Stock_Minimo', max_digits=10, decimal_places=3, blank=True, null=True)
    permite_stock_negativo = models.BooleanField(db_column='Permite_Stock_Negativo', default=False, help_text='Permite que el producto tenga stock negativo (ej: almuerzos preparados bajo demanda)')
    activo = models.BooleanField(db_column='Activo', default=True)

    class Meta:
        managed = False
        db_table = 'productos'
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'

    def __str__(self):
        return f'{self.codigo_barra} - {self.descripcion}'


class StockUnico(models.Model):
    '''Tabla stock_unico - Stock actual de productos'''
    id_producto = models.OneToOneField(
        Producto, 
        on_delete=models.CASCADE, 
        db_column='ID_Producto',
        primary_key=True,
        related_name='stock'
    )
    stock_actual = models.DecimalField(db_column='Stock_Actual', max_digits=10, decimal_places=3)
    fecha_ultima_actualizacion = models.DateTimeField(db_column='Fecha_Ultima_Actualizacion', auto_now=True)

    class Meta:
        managed = False
        db_table = 'stock_unico'
        verbose_name = 'Stock'
        verbose_name_plural = 'Stock de Productos'

    def __str__(self):
        return f'Stock de {self.id_producto.descripcion}: {self.stock_actual}'


# ==================== PROVEEDORES ====================

class Proveedor(models.Model):
    '''Tabla proveedores'''
    id_proveedor = models.AutoField(db_column='ID_Proveedor', primary_key=True)
    ruc = models.CharField(db_column='RUC', max_length=20, unique=True)
    razon_social = models.CharField(db_column='Razon_Social', max_length=255)
    telefono = models.CharField(db_column='Telefono', max_length=20, blank=True, null=True)
    email = models.EmailField(db_column='Email', blank=True, null=True)
    direccion = models.CharField(db_column='Direccion', max_length=255, blank=True, null=True)
    ciudad = models.CharField(db_column='Ciudad', max_length=100, blank=True, null=True)
    activo = models.BooleanField(db_column='Activo', default=True)
    fecha_registro = models.DateTimeField(db_column='Fecha_Registro', auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'proveedores'
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'

    def __str__(self):
        return self.razon_social


# ==================== EMPLEADOS ====================

class Empleado(models.Model):
    '''Tabla empleados'''
    id_empleado = models.AutoField(db_column='ID_Empleado', primary_key=True)
    id_rol = models.ForeignKey(
        TipoRolGeneral, 
        on_delete=models.PROTECT, 
        db_column='ID_Rol'
    )
    nombre = models.CharField(db_column='Nombre', max_length=100)
    apellido = models.CharField(db_column='Apellido', max_length=100)
    usuario = models.CharField(db_column='Usuario', max_length=50, unique=True)
    contrasena_hash = models.CharField(db_column='Contrasena_Hash', max_length=60)
    fecha_ingreso = models.DateTimeField(db_column='Fecha_Ingreso', auto_now_add=True)
    direccion = models.CharField(db_column='Direccion', max_length=255, blank=True, null=True)
    ciudad = models.CharField(db_column='Ciudad', max_length=100, blank=True, null=True)
    pais = models.CharField(db_column='Pais', max_length=100, blank=True, null=True)
    telefono = models.CharField(db_column='Telefono', max_length=20, blank=True, null=True)
    email = models.EmailField(db_column='Email', blank=True, null=True)
    activo = models.BooleanField(db_column='Activo', default=True)
    fecha_baja = models.DateTimeField(db_column='Fecha_Baja', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'empleados'
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'

    def __str__(self):
        return f'{self.apellido}, {self.nombre}'

    @property
    def nombre_completo(self):
        return f'{self.nombre} {self.apellido}'


# ==================== INFRAESTRUCTURA Y EMPRESA ====================

class DatosEmpresa(models.Model):
    '''Tabla datos_empresa - Información de la empresa'''
    id_empresa = models.IntegerField(db_column='ID_Empresa', primary_key=True)
    ruc = models.CharField(db_column='RUC', max_length=20)
    razon_social = models.CharField(db_column='Razon_Social', max_length=255)
    direccion = models.CharField(db_column='Direccion', max_length=255, blank=True, null=True)
    ciudad = models.CharField(db_column='Ciudad', max_length=100, blank=True, null=True)
    pais = models.CharField(db_column='Pais', max_length=100, blank=True, null=True)
    telefono = models.CharField(db_column='Telefono', max_length=20, blank=True, null=True)
    email = models.CharField(db_column='Email', max_length=100, blank=True, null=True)
    activo = models.IntegerField(db_column='Activo', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'datos_empresa'
        verbose_name = 'Datos de la Empresa'
        verbose_name_plural = 'Datos de la Empresa'

    def __str__(self):
        return self.razon_social


# ==================== PRECIOS Y COSTOS ====================

class PreciosPorLista(models.Model):
    '''Tabla precios_por_lista - Precios de productos por lista'''
    id_precio = models.AutoField(db_column='ID_Precio', primary_key=True)
    id_producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        db_column='ID_Producto',
        related_name='precios'
    )
    id_lista = models.ForeignKey(
        ListaPrecios,
        on_delete=models.CASCADE,
        db_column='ID_Lista'
    )
    precio_unitario_neto = models.BigIntegerField(db_column='Precio_Unitario_Neto')
    fecha_vigencia = models.DateTimeField(db_column='Fecha_Vigencia', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'precios_por_lista'
        verbose_name = 'Precio por Lista'
        verbose_name_plural = 'Precios por Lista'
        unique_together = (('id_producto', 'id_lista'),)

    def __str__(self):
        return f'{self.id_producto.descripcion} - {self.id_lista.nombre_lista}: Gs. {self.precio_unitario_neto}'


class CostosHistoricos(models.Model):
    '''Tabla costos_historicos - Historial de costos de productos'''
    id_costo_historico = models.BigAutoField(db_column='ID_Costo_Historico', primary_key=True)
    id_producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        db_column='ID_Producto',
        related_name='costos_historicos'
    )
    id_compra = models.ForeignKey(
        'Compras',
        on_delete=models.SET_NULL,
        db_column='ID_Compra',
        blank=True,
        null=True
    )
    costo_unitario_neto = models.DecimalField(db_column='Costo_Unitario_Neto', max_digits=10, decimal_places=2)
    fecha_compra = models.DateTimeField(db_column='Fecha_Compra')

    class Meta:
        managed = False
        db_table = 'costos_historicos'
        verbose_name = 'Costo Histórico'
        verbose_name_plural = 'Costos Históricos'

    def __str__(self):
        return f'{self.id_producto.descripcion}: Gs. {self.costo_unitario} ({self.fecha_costo})'


class HistoricoPrecios(models.Model):
    '''Tabla historico_precios - Historial de cambios de precios'''
    id_historico = models.BigAutoField(db_column='ID_Historico', primary_key=True)
    id_precio = models.ForeignKey(
        PreciosPorLista,
        on_delete=models.CASCADE,
        db_column='ID_Precio'
    )
    id_producto = models.IntegerField(db_column='ID_Producto')
    id_lista = models.IntegerField(db_column='ID_Lista')
    precio_anterior = models.DecimalField(db_column='Precio_Anterior', max_digits=10, decimal_places=2)
    precio_nuevo = models.DecimalField(db_column='Precio_Nuevo', max_digits=10, decimal_places=2)
    fecha_cambio = models.DateTimeField(db_column='Fecha_Cambio')
    id_empleado_modifico = models.ForeignKey(
        Empleado,
        on_delete=models.SET_NULL,
        db_column='ID_Empleado_Modifico',
        blank=True,
        null=True
    )

    class Meta:
        managed = False
        db_table = 'historico_precios'
        verbose_name = 'Histórico de Precio'
        verbose_name_plural = 'Históricos de Precios'

    def __str__(self):
        return f'Cambio de precio: Gs. {self.precio_anterior} → Gs. {self.precio_nuevo}'


# ==================== COMPRAS Y PROVEEDORES ====================

class Compras(models.Model):
    '''Tabla compras - Compras a proveedores'''
    id_compra = models.BigAutoField(db_column='ID_Compra', primary_key=True)
    id_proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.PROTECT,
        db_column='ID_Proveedor',
        related_name='compras'
    )
    fecha = models.DateTimeField(db_column='Fecha')
    monto_total = models.DecimalField(db_column='Monto_Total', max_digits=12, decimal_places=2)
    saldo_pendiente = models.DecimalField(db_column='Saldo_Pendiente', max_digits=12, decimal_places=2, blank=True, null=True)
    estado_pago = models.CharField(
        db_column='Estado_Pago',
        max_length=10,
        choices=[('PENDIENTE', 'Pendiente'), ('PARCIAL', 'Parcial'), ('PAGADA', 'Pagada')],
        default='PENDIENTE'
    )
    nro_factura = models.CharField(db_column='Nro_Factura', max_length=50, blank=True, null=True)
    observaciones = models.TextField(db_column='Observaciones', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'compras'
        verbose_name = 'Compra'
        verbose_name_plural = 'Compras'

    def __str__(self):
        return f'Compra #{self.id_compra} - {self.id_proveedor.razon_social}'


class DetalleCompra(models.Model):
    '''Tabla detalle_compra - Detalle de productos comprados'''
    id_detalle = models.BigAutoField(db_column='ID_Detalle', primary_key=True)
    id_compra = models.ForeignKey(
        Compras,
        on_delete=models.CASCADE,
        db_column='ID_Compra',
        related_name='detalles'
    )
    id_producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        db_column='ID_Producto'
    )
    costo_unitario_neto = models.DecimalField(db_column='Costo_Unitario_Neto', max_digits=10, decimal_places=2)
    cantidad = models.DecimalField(db_column='Cantidad', max_digits=8, decimal_places=3)
    subtotal_neto = models.DecimalField(db_column='Subtotal_Neto', max_digits=12, decimal_places=2)
    monto_iva = models.DecimalField(db_column='Monto_IVA', max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'detalle_compra'
        verbose_name = 'Detalle de Compra'
        verbose_name_plural = 'Detalles de Compra'
        unique_together = (('id_compra', 'id_producto'),)

    def __str__(self):
        return f'{self.id_producto.descripcion} x {self.cantidad}'


class NotasCreditoProveedor(models.Model):
    '''Tabla notas_credito_proveedor - Notas de crédito de proveedores'''
    ESTADO_CHOICES = [
        ('EMITIDA', 'Emitida'),
        ('APLICADA', 'Aplicada'),
        ('ANULADA', 'Anulada'),
    ]

    id_nota_proveedor = models.BigAutoField(db_column='ID_Nota_Proveedor', primary_key=True)
    nro_factura_compra = models.BigIntegerField(db_column='Nro_Factura_Compra', blank=True, null=True)
    id_proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.PROTECT,
        db_column='ID_Proveedor',
        related_name='notas_credito'
    )
    id_compra_original = models.ForeignKey(
        Compras,
        on_delete=models.SET_NULL,
        db_column='ID_Compra_Original',
        blank=True,
        null=True
    )
    fecha = models.DateTimeField(db_column='Fecha')
    monto_total = models.DecimalField(db_column='Monto_Total', max_digits=12, decimal_places=2)
    observacion = models.CharField(db_column='Observacion', max_length=255, blank=True, null=True)
    estado = models.CharField(db_column='Estado', max_length=10, choices=ESTADO_CHOICES, default='EMITIDA')
    fecha_creacion = models.DateTimeField(db_column='Fecha_Creacion', auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'notas_credito_proveedor'
        verbose_name = 'Nota de Crédito Proveedor'
        verbose_name_plural = 'Notas de Crédito Proveedores'

    def __str__(self):
        return f'NC Proveedor #{self.id_nota_proveedor} - {self.id_proveedor.razon_social}: Gs. {self.monto_total}'


class DetalleNotaCreditoProveedor(models.Model):
    '''Tabla detalle_nota_credito_proveedor - Detalle de notas de crédito a proveedores'''
    id_detalle_nc_proveedor = models.BigAutoField(db_column='ID_Detalle_NC_Proveedor', primary_key=True)
    id_nota_proveedor = models.ForeignKey(
        NotasCreditoProveedor,
        on_delete=models.CASCADE,
        db_column='ID_Nota_Proveedor',
        related_name='detalles'
    )
    id_producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        db_column='ID_Producto'
    )
    cantidad = models.DecimalField(db_column='Cantidad', max_digits=10, decimal_places=3)
    precio_unitario = models.DecimalField(db_column='Precio_Unitario', max_digits=12, decimal_places=2)
    subtotal = models.DecimalField(db_column='Subtotal', max_digits=12, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'detalle_nota_credito_proveedor'
        verbose_name = 'Detalle NC Proveedor'
        verbose_name_plural = 'Detalles NC Proveedores'

    def __str__(self):
        return f'{self.id_producto.descripcion} x {self.cantidad}'


class CargasSaldo(models.Model):
    '''Tabla cargas_saldo - Cargas de saldo a tarjetas'''
    id_carga = models.BigAutoField(db_column='ID_Carga', primary_key=True)
    nro_tarjeta = models.ForeignKey(
        Tarjeta,
        on_delete=models.PROTECT,
        db_column='Nro_Tarjeta'
    )
    id_cliente_origen = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        db_column='ID_Cliente_Origen',
        related_name='cargas_origen',
        blank=True,
        null=True
    )
    id_nota = models.ForeignKey(
        'NotasCreditoCliente',
        on_delete=models.PROTECT,
        db_column='ID_Nota',
        blank=True,
        null=True
    )
    fecha_carga = models.DateTimeField(db_column='Fecha_Carga')
    monto_cargado = models.DecimalField(db_column='Monto_Cargado', max_digits=10, decimal_places=2)
    referencia = models.CharField(db_column='Referencia', max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cargas_saldo'
        verbose_name = 'Carga de Saldo'
        verbose_name_plural = 'Cargas de Saldo'

    def __str__(self):
        return f'Carga #{self.id_carga} - Tarjeta {self.nro_tarjeta}: Gs. {self.monto_cargado}'


# ==================== USUARIOS WEB ====================

class UsuariosWebClientes(models.Model):
    '''Tabla usuarios_web_clientes - Usuarios web para clientes'''
    id_cliente = models.OneToOneField(
        Cliente,
        on_delete=models.CASCADE,
        db_column='ID_Cliente',
        primary_key=True,
        related_name='usuario_web'
    )
    usuario = models.CharField(db_column='Usuario', max_length=50, unique=True)
    contrasena_hash = models.CharField(db_column='Contrasena_Hash', max_length=60)
    ultimo_acceso = models.DateTimeField(db_column='Ultimo_Acceso', blank=True, null=True)
    activo = models.BooleanField(db_column='Activo', default=True)

    class Meta:
        managed = False
        db_table = 'usuarios_web_clientes'
        verbose_name = 'Usuario Web Cliente'
        verbose_name_plural = 'Usuarios Web Clientes'

    def __str__(self):
        return f'{self.usuario} ({self.id_cliente.nombre_completo})'


# ==================== FISCALIZACIÓN Y FACTURACIÓN ====================

class PuntosExpedicion(models.Model):
    '''Tabla puntos_expedicion - Puntos de expedición de documentos fiscales'''
    id_punto = models.AutoField(db_column='ID_Punto', primary_key=True)
    codigo_establecimiento = models.CharField(db_column='Codigo_Establecimiento', max_length=3)
    codigo_punto_expedicion = models.CharField(db_column='Codigo_Punto_Expedicion', max_length=3)
    descripcion_ubicacion = models.CharField(db_column='Descripcion_Ubicacion', max_length=100, blank=True, null=True)
    activo = models.BooleanField(db_column='Activo', default=True)

    class Meta:
        managed = False
        db_table = 'puntos_expedicion'
        verbose_name = 'Punto de Expedición'
        verbose_name_plural = 'Puntos de Expedición'
        unique_together = (('codigo_establecimiento', 'codigo_punto_expedicion'),)

    def __str__(self):
        return f'{self.codigo_establecimiento}-{self.codigo_punto_expedicion}'


class Timbrados(models.Model):
    '''Tabla timbrados - Timbrados fiscales'''
    TIPO_DOCUMENTO_CHOICES = [
        ('Factura', 'Factura'),
        ('Boleta', 'Boleta'),
        ('Nota Crédito', 'Nota Crédito'),
        ('Nota Débito', 'Nota Débito'),
    ]

    nro_timbrado = models.IntegerField(db_column='Nro_Timbrado', primary_key=True)
    id_punto = models.ForeignKey(
        PuntosExpedicion,
        on_delete=models.PROTECT,
        db_column='ID_Punto'
    )
    tipo_documento = models.CharField(db_column='Tipo_Documento', max_length=12, choices=TIPO_DOCUMENTO_CHOICES)
    fecha_inicio = models.DateField(db_column='Fecha_Inicio')
    fecha_fin = models.DateField(db_column='Fecha_Fin')
    nro_inicial = models.IntegerField(db_column='Nro_Inicial')
    nro_final = models.IntegerField(db_column='Nro_Final')
    es_electronico = models.BooleanField(db_column='Es_Electronico', default=False)
    activo = models.BooleanField(db_column='Activo', default=True)

    class Meta:
        managed = False
        db_table = 'timbrados'
        verbose_name = 'Timbrado'
        verbose_name_plural = 'Timbrados'

    def __str__(self):
        return f'Timbrado {self.nro_timbrado} - {self.tipo_documento}'


class DocumentosTributarios(models.Model):
    '''Tabla documentos_tributarios - Documentos tributarios emitidos'''
    id_documento = models.BigAutoField(db_column='ID_Documento', primary_key=True)
    nro_timbrado = models.ForeignKey(
        Timbrados,
        on_delete=models.PROTECT,
        db_column='Nro_Timbrado'
    )
    nro_secuencial = models.IntegerField(db_column='Nro_Secuencial')
    fecha_emision = models.DateTimeField(db_column='Fecha_Emision')
    monto_total = models.BigIntegerField(db_column='Monto_Total')
    monto_exento = models.DecimalField(db_column='Monto_Exento', max_digits=12, decimal_places=2, blank=True, null=True)
    monto_gravado_5 = models.DecimalField(db_column='Monto_Gravado_5', max_digits=12, decimal_places=2, blank=True, null=True)
    monto_iva_5 = models.DecimalField(db_column='Monto_IVA_5', max_digits=10, decimal_places=2, blank=True, null=True)
    monto_gravado_10 = models.DecimalField(db_column='Monto_Gravado_10', max_digits=12, decimal_places=2, blank=True, null=True)
    monto_iva_10 = models.DecimalField(db_column='Monto_IVA_10', max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'documentos_tributarios'
        verbose_name = 'Documento Tributario'
        verbose_name_plural = 'Documentos Tributarios'
        unique_together = (('nro_timbrado', 'nro_secuencial'),)

    def __str__(self):
        return f'Doc {self.id_documento} - Timbrado {self.nro_timbrado_id}: Gs. {self.monto_total}'


class DatosFacturacionElect(models.Model):
    '''Tabla datos_facturacion_elect - Datos específicos de facturación electrónica'''
    id_documento = models.OneToOneField(
        DocumentosTributarios,
        on_delete=models.CASCADE,
        db_column='ID_Documento',
        primary_key=True
    )
    cdc = models.CharField(db_column='CDC', max_length=44, unique=True)
    url_kude = models.CharField(db_column='URL_KuDE', max_length=255, blank=True, null=True)
    xml_transmitido = models.TextField(db_column='XML_Transmitido', blank=True, null=True)
    estado_sifen = models.CharField(db_column='Estado_SIFEN', max_length=9, blank=True, null=True)
    fecha_envio = models.DateTimeField(db_column='Fecha_Envio', blank=True, null=True)
    fecha_respuesta = models.DateTimeField(db_column='Fecha_Respuesta', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'datos_facturacion_elect'
        verbose_name = 'Datos Facturación Electrónica'
        verbose_name_plural = 'Datos Facturación Electrónica'

    def __str__(self):
        return f'CDC: {self.cdc}'


class DatosFacturacionFisica(models.Model):
    '''Tabla datos_facturacion_fisica - Datos específicos de facturación física'''
    id_documento = models.OneToOneField(
        DocumentosTributarios,
        on_delete=models.CASCADE,
        db_column='ID_Documento',
        primary_key=True
    )
    nro_preimpreso_interno = models.CharField(db_column='Nro_Preimpreso_Interno', max_length=20, unique=True)

    class Meta:
        managed = False
        db_table = 'datos_facturacion_fisica'
        verbose_name = 'Datos Facturación Física'
        verbose_name_plural = 'Datos Facturación Física'

    def __str__(self):
        return f'Factura Física {self.nro_preimpreso_interno}'


# ==================== MOVIMIENTOS DE INVENTARIO ====================

class MovimientosStock(models.Model):
    '''Tabla movimientos_stock - Movimientos de stock'''
    TIPO_MOVIMIENTO_CHOICES = [
        ('Entrada', 'Entrada'),
        ('Salida', 'Salida'),
        ('Ajuste', 'Ajuste'),
    ]

    id_movimientostock = models.BigAutoField(db_column='ID_MovimientoStock', primary_key=True)
    id_producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        db_column='ID_Producto',
        related_name='movimientos'
    )
    id_empleado_autoriza = models.ForeignKey(
        Empleado,
        on_delete=models.PROTECT,
        db_column='ID_Empleado_Autoriza'
    )
    id_venta = models.ForeignKey(
        'Ventas',
        on_delete=models.SET_NULL,
        db_column='ID_Venta',
        blank=True,
        null=True
    )
    id_compra = models.ForeignKey(
        Compras,
        on_delete=models.SET_NULL,
        db_column='ID_Compra',
        blank=True,
        null=True
    )
    fecha_hora = models.DateTimeField(db_column='Fecha_Hora')
    tipo_movimiento = models.CharField(db_column='Tipo_Movimiento', max_length=7, choices=TIPO_MOVIMIENTO_CHOICES)
    cantidad = models.DecimalField(db_column='Cantidad', max_digits=10, decimal_places=3)
    stock_resultante = models.DecimalField(
        db_column='Stock_Resultante', 
        max_digits=10, 
        decimal_places=3,
        default=0,
        help_text='Se calcula automáticamente por el trigger trg_stock_unico_after_movement'
    )
    referencia_documento = models.CharField(db_column='Referencia_Documento', max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'movimientos_stock'
        verbose_name = 'Movimiento de Stock'
        verbose_name_plural = 'Movimientos de Stock'

    def __str__(self):
        return f'{self.tipo_movimiento}: {self.id_producto.descripcion} ({self.cantidad})'


class AjustesInventario(models.Model):
    '''Tabla ajustes_inventario - Ajustes de inventario'''
    TIPO_AJUSTE_CHOICES = [
        ('Reconteo', 'Reconteo'),
        ('Merma', 'Merma'),
        ('Robo', 'Robo'),
        ('Daño', 'Daño'),
        ('Otro', 'Otro'),
    ]

    ESTADO_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('Aprobado', 'Aprobado'),
        ('Rechazado', 'Rechazado'),
    ]

    id_ajuste = models.BigAutoField(db_column='ID_Ajuste', primary_key=True)
    id_empleado_responsable = models.ForeignKey(
        Empleado,
        on_delete=models.PROTECT,
        db_column='ID_Empleado_Responsable'
    )
    fecha_hora = models.DateTimeField(db_column='Fecha_Hora')
    tipo_ajuste = models.CharField(db_column='Tipo_Ajuste', max_length=8, choices=TIPO_AJUSTE_CHOICES)
    motivo = models.CharField(db_column='Motivo', max_length=255)
    estado = models.CharField(db_column='Estado', max_length=10, choices=ESTADO_CHOICES)

    class Meta:
        managed = False
        db_table = 'ajustes_inventario'
        verbose_name = 'Ajuste de Inventario'
        verbose_name_plural = 'Ajustes de Inventario'

    def __str__(self):
        return f'Ajuste #{self.id_ajuste} - {self.tipo_ajuste}'


class DetalleAjuste(models.Model):
    '''Tabla detalle_ajuste - Detalle de ajustes de inventario'''
    id_detalle = models.BigAutoField(db_column='ID_Detalle', primary_key=True)
    id_ajuste = models.ForeignKey(
        AjustesInventario,
        on_delete=models.CASCADE,
        db_column='ID_Ajuste',
        related_name='detalles'
    )
    id_producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        db_column='ID_Producto'
    )
    id_movimientostock = models.OneToOneField(
        MovimientosStock,
        on_delete=models.CASCADE,
        db_column='ID_MovimientoStock'
    )
    cantidad_ajustada = models.DecimalField(db_column='Cantidad_Ajustada', max_digits=8, decimal_places=3)

    class Meta:
        managed = False
        db_table = 'detalle_ajuste'
        verbose_name = 'Detalle de Ajuste'
        verbose_name_plural = 'Detalles de Ajuste'
        unique_together = (('id_ajuste', 'id_producto'),)

    def __str__(self):
        return f'Ajuste {self.id_ajuste_id}: {self.id_producto.descripcion} ({self.cantidad_ajustada})'


# ==================== MEDIOS DE PAGO Y CAJAS ====================

class TiposPago(models.Model):
    '''Tabla tipos_pago - Tipos de pago'''
    id_tipo_pago = models.AutoField(db_column='ID_Tipo_Pago', primary_key=True)
    descripcion = models.CharField(db_column='Descripcion', max_length=50, unique=True)
    activo = models.BooleanField(db_column='Activo', default=True)

    class Meta:
        managed = False
        db_table = 'tipos_pago'
        verbose_name = 'Tipo de Pago'
        verbose_name_plural = 'Tipos de Pago'

    def __str__(self):
        return self.descripcion


class MediosPago(models.Model):
    '''Tabla medios_pago - Medios de pago'''
    id_medio_pago = models.AutoField(db_column='ID_Medio_Pago', primary_key=True)
    descripcion = models.CharField(db_column='Descripcion', max_length=50, unique=True)
    genera_comision = models.BooleanField(db_column='Genera_Comision', default=False)
    requiere_validacion = models.BooleanField(db_column='Requiere_Validacion', default=False)
    activo = models.BooleanField(db_column='Activo', default=True)

    class Meta:
        managed = False
        db_table = 'medios_pago'
        verbose_name = 'Medio de Pago'
        verbose_name_plural = 'Medios de Pago'

    def __str__(self):
        return self.descripcion


class TarifasComision(models.Model):
    '''Tabla tarifas_comision - Tarifas de comisión por medio de pago'''
    id_tarifa = models.AutoField(db_column='ID_Tarifa', primary_key=True)
    id_medio_pago = models.ForeignKey(
        MediosPago,
        on_delete=models.CASCADE,
        db_column='ID_Medio_Pago',
        related_name='tarifas'
    )
    fecha_inicio_vigencia = models.DateTimeField(db_column='Fecha_Inicio_Vigencia')
    fecha_fin_vigencia = models.DateTimeField(db_column='Fecha_Fin_Vigencia', blank=True, null=True)
    porcentaje_comision = models.DecimalField(db_column='Porcentaje_Comision', max_digits=5, decimal_places=4)
    monto_fijo_comision = models.DecimalField(db_column='Monto_Fijo_Comision', max_digits=10, decimal_places=2, blank=True, null=True)
    activo = models.BooleanField(db_column='Activo', default=True)

    class Meta:
        managed = False
        db_table = 'tarifas_comision'
        verbose_name = 'Tarifa de Comisión'
        verbose_name_plural = 'Tarifas de Comisión'

    def __str__(self):
        return f'{self.id_medio_pago.descripcion}: {self.porcentaje_comision}%'


class Cajas(models.Model):
    '''Tabla cajas - Cajas de punto de venta'''
    id_caja = models.AutoField(db_column='ID_Caja', primary_key=True)
    nombre_caja = models.CharField(db_column='Nombre_Caja', max_length=50)
    ubicacion = models.CharField(db_column='Ubicacion', max_length=100, blank=True, null=True)
    activo = models.IntegerField(db_column='Activo', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cajas'
        verbose_name = 'Caja'
        verbose_name_plural = 'Cajas'

    def __str__(self):
        return f'{self.nombre_caja}'


class CierresCaja(models.Model):
    '''Tabla cierres_caja - Cierres de caja'''
    id_cierre = models.BigAutoField(db_column='ID_Cierre', primary_key=True)
    id_caja = models.ForeignKey(
        Cajas,
        on_delete=models.PROTECT,
        db_column='ID_Caja'
    )
    id_empleado = models.ForeignKey(
        Empleado,
        on_delete=models.PROTECT,
        db_column='ID_Empleado'
    )
    fecha_hora_apertura = models.DateTimeField(db_column='Fecha_Hora_Apertura')
    fecha_hora_cierre = models.DateTimeField(db_column='Fecha_Hora_Cierre', blank=True, null=True)
    monto_inicial = models.DecimalField(db_column='Monto_Inicial', max_digits=10, decimal_places=2, blank=True, null=True)
    monto_contado_fisico = models.DecimalField(db_column='Monto_Contado_Fisico', max_digits=10, decimal_places=2, blank=True, null=True)
    diferencia_efectivo = models.DecimalField(db_column='Diferencia_Efectivo', max_digits=10, decimal_places=2, blank=True, null=True)
    estado = models.CharField(db_column='Estado', max_length=7, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cierres_caja'
        verbose_name = 'Cierre de Caja'
        verbose_name_plural = 'Cierres de Caja'

    def __str__(self):
        return f'Cierre #{self.id_cierre} - {self.id_caja.nombre_caja}'


# ==================== VENTAS ====================

class Ventas(models.Model):
    '''Tabla ventas - Ventas realizadas'''
    TIPO_VENTA_CHOICES = [
        ('Venta Directa', 'Venta Directa'),
        ('Consumo Tarjeta', 'Consumo Tarjeta'),
        ('Carga Saldo', 'Carga Saldo'),
        ('Pago Almuerzo', 'Pago Almuerzo'),
    ]

    id_venta = models.BigAutoField(db_column='ID_Venta', primary_key=True)
    nro_factura_venta = models.BigIntegerField(db_column='Nro_Factura_Venta', null=True, blank=True)
    id_cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        db_column='ID_Cliente',
        related_name='ventas'
    )
    id_hijo = models.ForeignKey(
        Hijo,
        on_delete=models.PROTECT,
        db_column='ID_Hijo',
        blank=True,
        null=True
    )
    id_tipo_pago = models.ForeignKey(
        TiposPago,
        on_delete=models.PROTECT,
        db_column='ID_Tipo_Pago'
    )
    id_empleado_cajero = models.ForeignKey(
        Empleado,
        on_delete=models.PROTECT,
        db_column='ID_Empleado_Cajero'
    )
    fecha = models.DateTimeField(db_column='Fecha')
    monto_total = models.BigIntegerField(db_column='Monto_Total')
    saldo_pendiente = models.BigIntegerField(db_column='Saldo_Pendiente', blank=True, null=True)
    estado_pago = models.CharField(
        db_column='Estado_Pago',
        max_length=10,
        choices=[('PENDIENTE', 'Pendiente'), ('PARCIAL', 'Parcial'), ('PAGADA', 'Pagada')],
        default='PENDIENTE'
    )
    estado = models.CharField(
        db_column='Estado',
        max_length=10,
        choices=[('PROCESADO', 'Procesado'), ('ANULADO', 'Anulado')],
        default='PROCESADO'
    )
    tipo_venta = models.CharField(db_column='Tipo_Venta', max_length=20, choices=TIPO_VENTA_CHOICES)

    def clean(self):
        """Validaciones de negocio para Ventas"""
        from django.core.exceptions import ValidationError
        
        # Validar que saldo_pendiente <= monto_total
        if self.saldo_pendiente and self.monto_total:
            if self.saldo_pendiente > self.monto_total:
                raise ValidationError({
                    'saldo_pendiente': 'El saldo pendiente no puede ser mayor al total de la venta'
                })
        
        # Validar consistencia estado_pago con saldo
        if self.estado_pago == 'PAGADA' and self.saldo_pendiente and self.saldo_pendiente > 0:
            raise ValidationError({
                'estado_pago': 'Una venta PAGADA no puede tener saldo pendiente mayor a 0'
            })
        
        if self.estado_pago == 'PENDIENTE' and self.saldo_pendiente != self.monto_total:
            raise ValidationError({
                'estado_pago': 'Una venta PENDIENTE debe tener saldo igual al total'
            })

    class Meta:
        managed = False
        db_table = 'ventas'
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'

    def __str__(self):
        return f'Venta #{self.id_venta} - {self.id_cliente.nombre_completo}: Gs. {self.monto_total}'


class DetalleVenta(models.Model):
    '''Tabla detalle_venta - Detalle de productos vendidos'''
    id_detalle = models.BigAutoField(db_column='ID_Detalle', primary_key=True)
    id_venta = models.ForeignKey(
        Ventas,
        on_delete=models.CASCADE,
        db_column='ID_Venta',
        related_name='detalles'
    )
    id_producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        db_column='ID_Producto'
    )
    cantidad = models.DecimalField(db_column='Cantidad', max_digits=10, decimal_places=3)
    precio_unitario = models.BigIntegerField(db_column='Precio_Unitario')
    subtotal_total = models.BigIntegerField(db_column='Subtotal_Total')

    class Meta:
        managed = False
        db_table = 'detalle_venta'
        verbose_name = 'Detalle de Venta'
        verbose_name_plural = 'Detalles de Venta'
        unique_together = (('id_venta', 'id_producto'),)

    def __str__(self):
        return f'{self.id_producto.descripcion} x {self.cantidad}'


class PagosVenta(models.Model):
    '''Tabla pagos_venta - Pagos aplicados a ventas'''
    id_pago_venta = models.BigAutoField(db_column='ID_Pago_Venta', primary_key=True)
    id_venta = models.ForeignKey(
        Ventas,
        on_delete=models.CASCADE,
        db_column='ID_Venta',
        related_name='pagos'
    )
    id_medio_pago = models.ForeignKey(
        MediosPago,
        on_delete=models.PROTECT,
        db_column='ID_Medio_Pago'
    )
    id_cierre = models.ForeignKey(
        CierresCaja,
        on_delete=models.PROTECT,
        db_column='ID_Cierre',
        blank=True,
        null=True
    )
    nro_tarjeta_usada = models.ForeignKey(
        Tarjeta,
        on_delete=models.PROTECT,
        db_column='Nro_Tarjeta_Usada',
        blank=True,
        null=True
    )
    monto_aplicado = models.BigIntegerField(db_column='Monto_Aplicado')
    referencia_transaccion = models.CharField(db_column='Referencia_Transaccion', max_length=100, blank=True, null=True)
    fecha_pago = models.DateTimeField(db_column='Fecha_Pago', blank=True, null=True)
    estado = models.CharField(
        db_column='Estado',
        max_length=10,
        choices=[('PROCESADO', 'Procesado'), ('ANULADO', 'Anulado')],
        default='PROCESADO'
    )

    class Meta:
        managed = False
        db_table = 'pagos_venta'
        verbose_name = 'Pago de Venta'
        verbose_name_plural = 'Pagos de Venta'

    def __str__(self):
        return f'Pago {self.id_pago_venta} - Venta {self.id_venta_id}: Gs. {self.monto_aplicado}'


# ==================== SISTEMA DE CUENTA CORRIENTE ====================

class PagosProveedores(models.Model):
    '''Tabla pagos_proveedores - Pagos realizados a proveedores'''
    id_pago_proveedor = models.BigAutoField(db_column='ID_Pago_Proveedor', primary_key=True)
    id_compra = models.ForeignKey(
        Compras,
        on_delete=models.PROTECT,
        db_column='ID_Compra',
        related_name='pagos'
    )
    monto_aplicado = models.DecimalField(db_column='Monto_Aplicado', max_digits=12, decimal_places=2)
    fecha_pago = models.DateTimeField(db_column='Fecha_Pago')
    id_medio_pago = models.ForeignKey(
        MediosPago,
        on_delete=models.PROTECT,
        db_column='ID_Medio_Pago'
    )
    referencia_transaccion = models.CharField(db_column='Referencia_Transaccion', max_length=100, blank=True, null=True)
    estado = models.CharField(
        db_column='Estado',
        max_length=10,
        choices=[('PROCESADO', 'Procesado'), ('ANULADO', 'Anulado')],
        default='PROCESADO'
    )
    observaciones = models.TextField(db_column='Observaciones', blank=True, null=True)
    fecha_creacion = models.DateTimeField(db_column='Fecha_Creacion', auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'pagos_proveedores'
        verbose_name = 'Pago a Proveedor'
        verbose_name_plural = 'Pagos a Proveedores'

    def __str__(self):
        return f'Pago #{self.id_pago_proveedor} - Compra {self.id_compra_id}: Gs. {self.monto_aplicado}'


class AplicacionPagosVentas(models.Model):
    '''Tabla aplicacion_pagos_ventas - Aplicación de pagos a ventas'''
    id_aplicacion = models.BigAutoField(db_column='ID_Aplicacion', primary_key=True)
    id_pago_venta = models.ForeignKey(
        PagosVenta,
        on_delete=models.CASCADE,
        db_column='ID_Pago_Venta'
    )
    id_venta = models.ForeignKey(
        Ventas,
        on_delete=models.CASCADE,
        db_column='ID_Venta'
    )
    monto_aplicado = models.BigIntegerField(db_column='Monto_Aplicado')

    class Meta:
        managed = False
        db_table = 'aplicacion_pagos_ventas'
        verbose_name = 'Aplicación de Pago a Venta'
        verbose_name_plural = 'Aplicaciones de Pagos a Ventas'

    def __str__(self):
        return f'Aplicación {self.id_aplicacion} - Pago {self.id_pago_venta_id} a Venta {self.id_venta_id}'


class AplicacionPagosCompras(models.Model):
    '''Tabla aplicacion_pagos_compras - Aplicación de pagos a compras'''
    id_aplicacion = models.BigAutoField(db_column='ID_Aplicacion', primary_key=True)
    id_pago_proveedor = models.ForeignKey(
        PagosProveedores,
        on_delete=models.CASCADE,
        db_column='ID_Pago_Proveedor'
    )
    id_compra = models.ForeignKey(
        Compras,
        on_delete=models.CASCADE,
        db_column='ID_Compra'
    )
    monto_aplicado = models.DecimalField(db_column='Monto_Aplicado', max_digits=12, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'aplicacion_pagos_compras'
        verbose_name = 'Aplicación de Pago a Compra'
        verbose_name_plural = 'Aplicaciones de Pagos a Compras'

    def __str__(self):
        return f'Aplicación {self.id_aplicacion} - Pago {self.id_pago_proveedor_id} a Compra {self.id_compra_id}'


class DetalleComisionVenta(models.Model):
    '''Tabla detalle_comision_venta - Comisiones por medio de pago'''
    id_detalle_comision = models.BigAutoField(db_column='ID_Detalle_Comision', primary_key=True)
    id_pago_venta = models.ForeignKey(
        PagosVenta,
        on_delete=models.CASCADE,
        db_column='ID_Pago_Venta',
        related_name='comisiones'
    )
    id_tarifa = models.ForeignKey(
        TarifasComision,
        on_delete=models.PROTECT,
        db_column='ID_Tarifa'
    )
    monto_comision_calculada = models.DecimalField(db_column='Monto_Comision_Calculada', max_digits=10, decimal_places=2)
    porcentaje_aplicado = models.DecimalField(db_column='Porcentaje_Aplicado', max_digits=5, decimal_places=4)

    class Meta:
        managed = False
        db_table = 'detalle_comision_venta'
        verbose_name = 'Detalle de Comisión'
        verbose_name_plural = 'Detalles de Comisión'

    def __str__(self):
        return f'Comisión Pago {self.id_pago_venta_id}: Gs. {self.monto_comision_calculada}'


class ConciliacionPagos(models.Model):
    '''Tabla conciliacion_pagos - Conciliación de pagos con entidades'''
    id_conciliacion = models.BigAutoField(db_column='ID_Conciliacion', primary_key=True)
    id_pago_venta = models.OneToOneField(
        PagosVenta,
        on_delete=models.CASCADE,
        db_column='ID_Pago_Venta'
    )
    fecha_acreditacion = models.DateTimeField(db_column='Fecha_Acreditacion', blank=True, null=True)
    monto_acreditado = models.DecimalField(db_column='Monto_Acreditado', max_digits=10, decimal_places=2, blank=True, null=True)
    estado = models.CharField(db_column='Estado', max_length=10, blank=True, null=True)
    observaciones = models.TextField(db_column='Observaciones', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'conciliacion_pagos'
        verbose_name = 'Conciliación de Pago'
        verbose_name_plural = 'Conciliaciones de Pagos'

    def __str__(self):
        return f'Conciliación #{self.id_conciliacion} - {self.estado}'


# ==================== NOTAS DE CRÉDITO ====================

class NotasCreditoCliente(models.Model):
    '''Tabla notas_credito_cliente - Notas de crédito emitidas'''
    ESTADO_CHOICES = [
        ('Emitida', 'Emitida'),
        ('Aplicada', 'Aplicada'),
        ('Anulada', 'Anulada'),
    ]

    id_nota = models.BigAutoField(db_column='ID_Nota', primary_key=True)
    nro_factura_venta = models.BigIntegerField(db_column='Nro_Factura_Venta')
    id_cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        db_column='ID_Cliente',
        related_name='notas_credito'
    )
    id_venta_original = models.ForeignKey(
        Ventas,
        on_delete=models.SET_NULL,
        db_column='ID_Venta_Original',
        blank=True,
        null=True
    )
    fecha = models.DateTimeField(db_column='Fecha')
    monto_total = models.DecimalField(db_column='Monto_Total', max_digits=12, decimal_places=2)
    observacion = models.CharField(db_column='Observacion', max_length=255, blank=True, null=True)
    estado = models.CharField(db_column='Estado', max_length=8, choices=ESTADO_CHOICES, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'notas_credito_cliente'
        verbose_name = 'Nota de Crédito Cliente'
        verbose_name_plural = 'Notas de Crédito Cliente'

    def __str__(self):
        return f'NC #{self.id_nota} - {self.id_cliente.nombre_completo}: Gs. {self.monto_total}'


class DetalleNota(models.Model):
    '''Tabla detalle_nota - Detalle de notas de crédito'''
    id_detalle = models.BigAutoField(db_column='ID_Detalle', primary_key=True)
    id_nota = models.ForeignKey(
        NotasCreditoCliente,
        on_delete=models.CASCADE,
        db_column='ID_Nota',
        related_name='detalles'
    )
    id_producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        db_column='ID_Producto'
    )
    cantidad = models.DecimalField(db_column='Cantidad', max_digits=8, decimal_places=3)
    precio_unitario = models.DecimalField(db_column='Precio_Unitario', max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(db_column='Subtotal', max_digits=12, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'detalle_nota'
        verbose_name = 'Detalle de Nota de Crédito'
        verbose_name_plural = 'Detalles de Notas de Crédito'
        unique_together = (('id_nota', 'id_producto'),)

    def __str__(self):
        return f'{self.id_producto.descripcion} x {self.cantidad}'


# ==================== SISTEMA DE ALMUERZOS ====================

class PlanesAlmuerzo(models.Model):
    '''Tabla planes_almuerzo - Planes de almuerzo disponibles'''
    id_plan_almuerzo = models.AutoField(db_column='ID_Plan_Almuerzo', primary_key=True)
    nombre_plan = models.CharField(db_column='Nombre_Plan', max_length=100, unique=True)
    descripcion = models.TextField(db_column='Descripcion', blank=True, null=True)
    precio_mensual = models.DecimalField(db_column='Precio_Mensual', max_digits=10, decimal_places=2)
    dias_semana_incluidos = models.CharField(db_column='Dias_Semana_Incluidos', max_length=60)
    fecha_creacion = models.DateTimeField(db_column='Fecha_Creacion', blank=True, null=True)
    activo = models.BooleanField(db_column='Activo', default=True)

    class Meta:
        managed = False
        db_table = 'planes_almuerzo'
        verbose_name = 'Plan de Almuerzo'
        verbose_name_plural = 'Planes de Almuerzo'

    def __str__(self):
        return f'{self.nombre_plan} - Gs. {self.precio_mensual}'


class SuscripcionesAlmuerzo(models.Model):
    '''Tabla suscripciones_almuerzo - Suscripciones de almuerzos'''
    ESTADO_CHOICES = [
        ('Activa', 'Activa'),
        ('Suspendida', 'Suspendida'),
        ('Cancelada', 'Cancelada'),
    ]

    id_suscripcion = models.BigAutoField(db_column='ID_Suscripcion', primary_key=True)
    id_hijo = models.ForeignKey(
        Hijo,
        on_delete=models.PROTECT,
        db_column='ID_Hijo',
        related_name='suscripciones'
    )
    id_plan_almuerzo = models.ForeignKey(
        PlanesAlmuerzo,
        on_delete=models.PROTECT,
        db_column='ID_Plan_Almuerzo'
    )
    fecha_inicio = models.DateField(db_column='Fecha_Inicio')
    fecha_fin = models.DateField(db_column='Fecha_Fin', blank=True, null=True)
    estado = models.CharField(db_column='Estado', max_length=10, choices=ESTADO_CHOICES, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'suscripciones_almuerzo'
        verbose_name = 'Suscripción de Almuerzo'
        verbose_name_plural = 'Suscripciones de Almuerzo'
        unique_together = (('id_hijo', 'id_plan_almuerzo', 'estado'),)

    def __str__(self):
        return f'{self.id_hijo.nombre_completo} - {self.id_plan_almuerzo.nombre_plan}'


class PagosAlmuerzoMensual(models.Model):
    '''Tabla pagos_almuerzo_mensual - Pagos mensuales de almuerzos'''
    ESTADO_CHOICES = [
        ('Pagado', 'Pagado'),
        ('Pendiente', 'Pendiente'),
        ('Vencido', 'Vencido'),
    ]

    id_pago_almuerzo = models.BigAutoField(db_column='ID_Pago_Almuerzo', primary_key=True)
    id_suscripcion = models.ForeignKey(
        SuscripcionesAlmuerzo,
        on_delete=models.PROTECT,
        db_column='ID_Suscripcion',
        related_name='pagos'
    )
    fecha_pago = models.DateTimeField(db_column='Fecha_Pago')
    monto_pagado = models.DecimalField(db_column='Monto_Pagado', max_digits=10, decimal_places=2)
    mes_pagado = models.DateField(db_column='Mes_Pagado')
    id_venta = models.OneToOneField(
        Ventas,
        on_delete=models.SET_NULL,
        db_column='ID_Venta',
        blank=True,
        null=True
    )
    estado = models.CharField(db_column='Estado', max_length=9, choices=ESTADO_CHOICES, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pagos_almuerzo_mensual'
        verbose_name = 'Pago de Almuerzo Mensual'
        verbose_name_plural = 'Pagos de Almuerzo Mensual'
        unique_together = (('id_suscripcion', 'mes_pagado'),)

    def __str__(self):
        return f'Pago {self.mes_pagado} - {self.id_suscripcion.id_hijo.nombre_completo}'


# ==================== ALERTAS Y NOTIFICACIONES ====================

class AlertasSistema(models.Model):
    '''Tabla alertas_sistema - Alertas del sistema'''
    TIPO_CHOICES = [
        ('Stock Bajo', 'Stock Bajo'),
        ('Saldo Bajo', 'Saldo Bajo'),
        ('Timbrado Próximo a Vencer', 'Timbrado Próximo a Vencer'),
        ('Sistema', 'Sistema'),
    ]

    ESTADO_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('Leída', 'Leída'),
        ('Resuelta', 'Resuelta'),
    ]

    id_alerta = models.BigAutoField(db_column='ID_Alerta', primary_key=True)
    tipo = models.CharField(db_column='Tipo', max_length=30, choices=TIPO_CHOICES)
    mensaje = models.CharField(db_column='Mensaje', max_length=500)
    fecha_creacion = models.DateTimeField(db_column='Fecha_Creacion')
    fecha_leida = models.DateTimeField(db_column='Fecha_Leida', blank=True, null=True)
    estado = models.CharField(db_column='Estado', max_length=9, choices=ESTADO_CHOICES, blank=True, null=True)
    id_empleado_resuelve = models.BigIntegerField(db_column='ID_Empleado_Resuelve', blank=True, null=True)
    fecha_resolucion = models.DateTimeField(db_column='Fecha_Resolucion', blank=True, null=True)
    observaciones = models.TextField(db_column='Observaciones', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'alertas_sistema'
        verbose_name = 'Alerta del Sistema'
        verbose_name_plural = 'Alertas del Sistema'

    def __str__(self):
        return f'{self.tipo} - {self.estado}'


class SolicitudesNotificacion(models.Model):
    '''Tabla solicitudes_notificacion - Solicitudes de notificación'''
    DESTINO_CHOICES = [
        ('SMS', 'SMS'),
        ('Email', 'Email'),
        ('WhatsApp', 'WhatsApp'),
    ]

    ESTADO_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('Enviada', 'Enviada'),
        ('Fallida', 'Fallida'),
    ]

    id_solicitud = models.BigAutoField(db_column='ID_Solicitud', primary_key=True)
    id_cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        db_column='ID_Cliente',
        related_name='notificaciones'
    )
    nro_tarjeta = models.ForeignKey(
        Tarjeta,
        on_delete=models.CASCADE,
        db_column='Nro_Tarjeta'
    )
    saldo_alerta = models.DecimalField(db_column='Saldo_Alerta', max_digits=10, decimal_places=2)
    mensaje = models.CharField(db_column='Mensaje', max_length=255)
    destino = models.CharField(db_column='Destino', max_length=8, choices=DESTINO_CHOICES)
    estado = models.CharField(db_column='Estado', max_length=9, choices=ESTADO_CHOICES, blank=True, null=True)
    fecha_solicitud = models.DateTimeField(db_column='Fecha_Solicitud')
    fecha_envio = models.DateTimeField(db_column='Fecha_Envio', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'solicitudes_notificacion'
        verbose_name = 'Solicitud de Notificación'
        verbose_name_plural = 'Solicitudes de Notificación'

    def __str__(self):
        return f'{self.id_cliente.nombre_completo} - {self.destino} - {self.estado}'


# ==================== AUDITORÍA ====================

class AuditoriaEmpleados(models.Model):
    '''Tabla auditoria_empleados - Auditoría de acciones de empleados'''
    id_auditoria = models.BigAutoField(db_column='ID_Auditoria', primary_key=True)
    id_empleado = models.ForeignKey(
        Empleado,
        on_delete=models.CASCADE,
        db_column='ID_Empleado',
        related_name='auditorias'
    )
    fecha_cambio = models.DateTimeField(db_column='Fecha_Cambio')
    campo_modificado = models.CharField(db_column='Campo_Modificado', max_length=50)
    valor_anterior = models.TextField(db_column='Valor_Anterior', blank=True, null=True)
    valor_nuevo = models.TextField(db_column='Valor_Nuevo', blank=True, null=True)
    ip_origen = models.CharField(db_column='IP_Origen', max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'auditoria_empleados'
        verbose_name = 'Auditoría de Empleado'
        verbose_name_plural = 'Auditorías de Empleados'

    def __str__(self):
        return f'{self.id_empleado.nombre_completo} - {self.campo_modificado} ({self.fecha_cambio})'


class AuditoriaUsuariosWeb(models.Model):
    '''Tabla auditoria_usuarios_web - Auditoría de usuarios web'''
    id_auditoria = models.BigAutoField(db_column='ID_Auditoria', primary_key=True)
    id_cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        db_column='ID_Cliente',
        related_name='auditorias_web'
    )
    fecha_cambio = models.DateTimeField(db_column='Fecha_Cambio')
    campo_modificado = models.CharField(db_column='Campo_Modificado', max_length=50)
    valor_anterior = models.TextField(db_column='Valor_Anterior', blank=True, null=True)
    valor_nuevo = models.TextField(db_column='Valor_Nuevo', blank=True, null=True)
    ip_origen = models.CharField(db_column='IP_Origen', max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'auditoria_usuarios_web'
        verbose_name = 'Auditoría de Usuario Web'
        verbose_name_plural = 'Auditorías de Usuarios Web'

    def __str__(self):
        return f'{self.id_cliente.nombre_completo} - {self.campo_modificado} ({self.fecha_cambio})'


class AuditoriaComisiones(models.Model):
    '''Tabla auditoria_comisiones - Auditoría de cálculos de comisiones'''
    id_auditoria = models.BigAutoField(db_column='ID_Auditoria', primary_key=True)
    id_tarifa = models.ForeignKey(
        TarifasComision,
        on_delete=models.CASCADE,
        db_column='ID_Tarifa'
    )
    fecha_cambio = models.DateTimeField(db_column='Fecha_Cambio')
    campo_modificado = models.CharField(db_column='Campo_Modificado', max_length=50)
    valor_anterior = models.DecimalField(db_column='Valor_Anterior', max_digits=10, decimal_places=4, blank=True, null=True)
    valor_nuevo = models.DecimalField(db_column='Valor_Nuevo', max_digits=10, decimal_places=4, blank=True, null=True)
    id_empleado_modifico = models.ForeignKey(
        Empleado,
        on_delete=models.CASCADE,
        db_column='ID_Empleado_Modifico',
        blank=True,
        null=True
    )

    class Meta:
        managed = False
        db_table = 'auditoria_comisiones'
        verbose_name = 'Auditoría de Comisión'
        verbose_name_plural = 'Auditorías de Comisiones'

    def __str__(self):
        return f'Auditoría Comisión #{self.id_detalle_comision_id} - Gs. {self.monto_comision}'


# ==================== VISTAS DE LA BASE DE DATOS ====================
# Las vistas MySQL están activas en la base de datos

class VistaStockAlerta(models.Model):
    '''Vista v_stock_alerta - Productos con stock bajo'''
    id_producto = models.IntegerField(db_column='ID_Producto', primary_key=True)
    codigo_barra = models.CharField(db_column='Codigo_Barra', max_length=50, blank=True, null=True)
    descripcion = models.CharField(db_column='Descripcion', max_length=255)
    categoria = models.CharField(db_column='Categoria', max_length=100)
    stock_actual = models.DecimalField(db_column='Stock_Actual', max_digits=10, decimal_places=3)
    stock_minimo = models.DecimalField(db_column='Stock_Minimo', max_digits=10, decimal_places=3)
    diferencia = models.DecimalField(db_column='Diferencia', max_digits=11, decimal_places=3)
    nivel_alerta = models.CharField(db_column='Nivel_Alerta', max_length=7)
    fecha_ultima_actualizacion = models.DateTimeField(db_column='Fecha_Ultima_Actualizacion', blank=True, null=True)
    unidad_medida = models.CharField(db_column='Unidad_Medida', max_length=50)

    class Meta:
        managed = False
        db_table = 'v_stock_alerta'
        verbose_name = 'Alerta de Stock'
        verbose_name_plural = 'Alertas de Stock'

    def __str__(self):
        return f'{self.descripcion} - {self.nivel_alerta} (Stock: {self.stock_actual})'


class VistaSaldoClientes(models.Model):
    '''Vista v_saldo_clientes - Saldos de cuenta corriente'''
    id_cliente = models.IntegerField(db_column='ID_Cliente', primary_key=True)
    nombres = models.CharField(db_column='Nombres', max_length=100)
    apellidos = models.CharField(db_column='Apellidos', max_length=100)
    nombre_completo = models.CharField(db_column='nombre_completo', max_length=201)
    ruc_ci = models.CharField(db_column='Ruc_CI', max_length=20)
    tipo_cliente = models.CharField(db_column='tipo_cliente', max_length=50)
    saldo_actual = models.DecimalField(db_column='saldo_actual', max_digits=30, decimal_places=2)
    ultima_actualizacion = models.DateField(db_column='ultima_actualizacion', blank=True, null=True)
    total_movimientos = models.BigIntegerField(db_column='total_movimientos')

    class Meta:
        managed = False
        db_table = 'v_saldo_clientes'
        verbose_name = 'Saldo de Cliente'
        verbose_name_plural = 'Saldos de Clientes'

    def __str__(self):
        return f'{self.nombre_completo}: Gs. {self.saldo_actual:,.0f}'


# =============================================================================
# MODELOS PARA FUNCIONALIDADES FUTURAS (Ventas y Compras)
# Estos modelos crearán nuevas tablas cuando se ejecuten las migraciones
# =============================================================================

# Nota: Estos modelos están deshabilitados temporalmente
# Para habilitarlos, descomentar el código y ejecutar makemigrations/migrate

# class Venta(models.Model):
#     '''Registro de ventas'''
#     METODO_PAGO = [
#         ('efectivo', 'Efectivo'),
#         ('tarjeta', 'Tarjeta'),
#         ('credito', 'Crédito'),
#         ('transferencia', 'Transferencia'),
#     ]
#
#     ESTADO = [
#         ('pendiente', 'Pendiente'),
#         ('completada', 'Completada'),
#         ('cancelada', 'Cancelada'),
#     ]
#
#     numero_venta = models.CharField(max_length=50, unique=True)
#     cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='ventas', null=True, blank=True)
#     usuario = models.ForeignKey(User, on_delete=models.PROTECT, related_name='ventas_realizadas')
#     fecha_venta = models.DateTimeField(default=timezone.now)
#     subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO, default='efectivo')
#     estado = models.CharField(max_length=20, choices=ESTADO, default='completada')
#     notas = models.TextField(blank=True, null=True)
#
#     class Meta:
#         verbose_name = 'Venta'
#         verbose_name_plural = 'Ventas'
#         ordering = ['-fecha_venta']
#
#     def __str__(self):
#         return f'Venta {self.numero_venta} - Gs. {self.total}'
#
#     def calcular_total(self):
#         '''Calcula el total de la venta basado en los detalles'''
#         self.subtotal = sum(detalle.subtotal for detalle in self.detalles.all())
#         self.total = self.subtotal - self.descuento
#         self.save()


# class DetalleVenta(models.Model):
#     '''Detalle de productos vendidos en cada venta'''
#     venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
#     producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
#     cantidad = models.IntegerField(default=1)
#     precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
#     subtotal = models.DecimalField(max_digits=10, decimal_places=2)
#
#     class Meta:
#         verbose_name = 'Detalle de Venta'
#         verbose_name_plural = 'Detalles de Venta'
#
#     def __str__(self):
#         return f'{self.producto.descripcion} x{self.cantidad}'
#
#     def save(self, *args, **kwargs):
#         '''Calcula el subtotal antes de guardar'''
#         self.subtotal = self.cantidad * self.precio_unitario
#         super().save(*args, **kwargs)


# class CompraProveedor(models.Model):
#     '''Compras realizadas a proveedores'''
#     ESTADO = [
#         ('pendiente', 'Pendiente'),
#         ('recibida', 'Recibida'),
#         ('cancelada', 'Cancelada'),
#     ]
#
#     numero_compra = models.CharField(max_length=50, unique=True)
#     proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, related_name='compras')
#     usuario = models.ForeignKey(User, on_delete=models.PROTECT, related_name='compras_realizadas')
#     fecha_compra = models.DateTimeField(default=timezone.now)
#     fecha_recepcion = models.DateTimeField(blank=True, null=True)
#     total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     estado = models.CharField(max_length=20, choices=ESTADO, default='pendiente')
#     notas = models.TextField(blank=True, null=True)
#
#     class Meta:
#         verbose_name = 'Compra a Proveedor'
#         verbose_name_plural = 'Compras a Proveedores'
#         ordering = ['-fecha_compra']
#
#     def __str__(self):
#         return f'Compra {self.numero_compra} - {self.proveedor.razon_social}'


# class DetalleCompra(models.Model):
#     '''Detalle de productos comprados'''
#     compra = models.ForeignKey(CompraProveedor, on_delete=models.CASCADE, related_name='detalles')
#     producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
#     cantidad = models.IntegerField(default=1)
#     precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
#     subtotal = models.DecimalField(max_digits=10, decimal_places=2)
#
#     class Meta:
#         verbose_name = 'Detalle de Compra'
#         verbose_name_plural = 'Detalles de Compra'
#
#     def __str__(self):
#         return f'{self.producto.descripcion} x{self.cantidad}'
#
#     def save(self, *args, **kwargs):
#         '''Calcula el subtotal antes de guardar'''
#         self.subtotal = self.cantidad * self.precio_unitario
#         super().save(*args, **kwargs)


# =============================================================================
# NUEVOS MODELOS - 26 NOVIEMBRE 2025
# =============================================================================

class ConsumoTarjeta(models.Model):
    '''Tabla consumos_tarjeta - Historial de consumos con tarjeta'''
    id_consumo = models.BigAutoField(db_column='ID_Consumo', primary_key=True)
    nro_tarjeta = models.ForeignKey(
        Tarjeta,
        on_delete=models.PROTECT,
        db_column='Nro_Tarjeta',
        related_name='consumos'
    )
    fecha_consumo = models.DateTimeField(db_column='Fecha_Consumo')
    monto_consumido = models.DecimalField(db_column='Monto_Consumido', max_digits=10, decimal_places=2)
    detalle = models.CharField(db_column='Detalle', max_length=200, blank=True, null=True)
    saldo_anterior = models.DecimalField(db_column='Saldo_Anterior', max_digits=10, decimal_places=2)
    saldo_posterior = models.DecimalField(db_column='Saldo_Posterior', max_digits=10, decimal_places=2)
    id_empleado_registro = models.ForeignKey(
        'Empleado',
        on_delete=models.SET_NULL,
        db_column='ID_Empleado_Registro',
        blank=True,
        null=True,
        related_name='consumos_registrados'
    )

    class Meta:
        managed = False
        db_table = 'consumos_tarjeta'
        verbose_name = 'Consumo con Tarjeta'
        verbose_name_plural = 'Consumos con Tarjeta'
        ordering = ['-fecha_consumo']

    def __str__(self):
        return f'Consumo {self.nro_tarjeta} - Gs. {self.monto_consumido:,.0f}'


# =============================================================================
# VISTAS SQL - 26 NOVIEMBRE 2025
# =============================================================================

class VistaVentasDiaDetallado(models.Model):
    '''Vista v_ventas_dia_detallado - Ventas con detalles completos'''
    id_venta = models.BigIntegerField(db_column='ID_Venta', primary_key=True)
    fecha = models.DateTimeField(db_column='Fecha')
    monto_total = models.BigIntegerField(db_column='Monto_Total')
    nombres = models.CharField(db_column='Nombres', max_length=100)
    apellidos = models.CharField(db_column='Apellidos', max_length=100)
    cliente_completo = models.CharField(db_column='Cliente_Completo', max_length=201)
    empleado = models.CharField(db_column='Empleado', max_length=100)
    nro_timbrado = models.IntegerField(db_column='Nro_Timbrado')
    nro_secuencial = models.IntegerField(db_column='Nro_Secuencial')
    cantidad_items = models.BigIntegerField(db_column='Cantidad_Items')
    productos = models.TextField(db_column='Productos')
    total_pagado = models.DecimalField(db_column='Total_Pagado', max_digits=32, decimal_places=0)
    saldo_pendiente = models.DecimalField(db_column='Saldo_Pendiente', max_digits=33, decimal_places=0)

    class Meta:
        managed = False
        db_table = 'v_ventas_dia_detallado'
        verbose_name = 'Vista: Ventas del Día Detallado'
        verbose_name_plural = 'Vista: Ventas del Día Detallado'

    def __str__(self):
        return f'Venta {self.id_venta} - {self.cliente_completo}'


class VistaConsumosEstudiante(models.Model):
    '''Vista v_consumos_estudiante - Resumen de consumos por estudiante'''
    id_hijo = models.IntegerField(db_column='ID_Hijo', primary_key=True)
    estudiante = models.CharField(db_column='Estudiante', max_length=202)
    responsable_nombre = models.CharField(db_column='Responsable_Nombre', max_length=100)
    responsable_apellido = models.CharField(db_column='Responsable_Apellido', max_length=100)
    nro_tarjeta = models.CharField(db_column='Nro_Tarjeta', max_length=20)
    saldo_actual = models.BigIntegerField(db_column='Saldo_Actual')
    total_consumos = models.BigIntegerField(db_column='Total_Consumos')
    total_consumido = models.DecimalField(db_column='Total_Consumido', max_digits=32, decimal_places=2)
    ultimo_consumo = models.DateTimeField(db_column='Ultimo_Consumo')
    total_recargas = models.BigIntegerField(db_column='Total_Recargas')
    total_recargado = models.DecimalField(db_column='Total_Recargado', max_digits=32, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'v_consumos_estudiante'
        verbose_name = 'Vista: Consumos por Estudiante'
        verbose_name_plural = 'Vista: Consumos por Estudiante'

    def __str__(self):
        return f'{self.estudiante} - Saldo: Gs. {self.saldo_actual:,.0f}'


class VistaStockCriticoAlertas(models.Model):
    '''Vista v_stock_critico_alertas - Productos con stock crítico'''
    id_producto = models.IntegerField(db_column='ID_Producto', primary_key=True)
    codigo_barra = models.CharField(db_column='Codigo_Barra', max_length=50)
    descripcion = models.CharField(db_column='Descripcion', max_length=255)
    categoria = models.CharField(db_column='Categoria', max_length=100)
    stock_actual = models.DecimalField(db_column='Stock_Actual', max_digits=10, decimal_places=3)
    stock_minimo = models.DecimalField(db_column='Stock_Minimo', max_digits=10, decimal_places=3)

    class Meta:
        managed = False
        db_table = 'v_stock_critico_alertas'
        verbose_name = 'Vista: Stock Crítico'
        verbose_name_plural = 'Vista: Stock Crítico'

    def __str__(self):
        return f'{self.codigo_barra} - {self.descripcion}'


class VistaRecargasHistorial(models.Model):
    '''Vista v_recargas_historial - Historial de recargas'''
    id_carga = models.BigIntegerField(db_column='ID_Carga', primary_key=True)
    fecha_carga = models.DateTimeField(db_column='Fecha_Carga')
    monto_cargado = models.DecimalField(db_column='Monto_Cargado', max_digits=10, decimal_places=2)
    nro_tarjeta = models.CharField(db_column='Nro_Tarjeta', max_length=20)
    estudiante = models.CharField(db_column='Estudiante', max_length=202)
    responsable = models.CharField(db_column='Responsable', max_length=201)
    telefono = models.CharField(db_column='Telefono', max_length=20)
    empleado_registro = models.CharField(db_column='Empleado_Registro', max_length=100)
    saldo_actual_tarjeta = models.BigIntegerField(db_column='Saldo_Actual_Tarjeta')

    class Meta:
        managed = False
        db_table = 'v_recargas_historial'
        verbose_name = 'Vista: Historial de Recargas'
        verbose_name_plural = 'Vista: Historial de Recargas'

    def __str__(self):
        return f'Recarga {self.id_carga} - {self.estudiante}'


class VistaResumenCajaDiario(models.Model):
    '''Vista v_resumen_caja_diario - Resumen financiero diario'''
    fecha = models.DateField(db_column='Fecha', primary_key=True)
    total_ventas = models.BigIntegerField(db_column='Total_Ventas')
    monto_total_ventas = models.DecimalField(db_column='Monto_Total_Ventas', max_digits=32, decimal_places=0)
    total_recargas = models.BigIntegerField(db_column='Total_Recargas')
    monto_total_recargas = models.DecimalField(db_column='Monto_Total_Recargas', max_digits=32, decimal_places=2)
    total_ingresos_dia = models.DecimalField(db_column='Total_Ingresos_Dia', max_digits=33, decimal_places=2)
    total_transacciones_pago = models.BigIntegerField(db_column='Total_Transacciones_Pago')
    total_efectivo = models.DecimalField(db_column='Total_Efectivo', max_digits=32, decimal_places=0)
    total_tarjeta_debito = models.DecimalField(db_column='Total_Tarjeta_Debito', max_digits=32, decimal_places=0)
    total_tarjeta_credito = models.DecimalField(db_column='Total_Tarjeta_Credito', max_digits=32, decimal_places=0)
    total_transferencias = models.DecimalField(db_column='Total_Transferencias', max_digits=32, decimal_places=0)

    class Meta:
        managed = False
        db_table = 'v_resumen_caja_diario'
        verbose_name = 'Vista: Resumen de Caja Diario'
        verbose_name_plural = 'Vista: Resumen de Caja Diario'

    def __str__(self):
        return f'Caja {self.fecha} - Gs. {self.total_ingresos_dia:,.0f}'


class VistaNotasCreditoDetallado(models.Model):
    '''Vista v_notas_credito_detallado - Notas de crédito con detalles'''
    id_nota = models.BigIntegerField(db_column='ID_Nota', primary_key=True)
    fecha = models.DateTimeField(db_column='Fecha')
    monto_total = models.DecimalField(db_column='Monto_Total', max_digits=12, decimal_places=2)
    estado = models.CharField(db_column='Estado', max_length=20)
    observacion = models.CharField(db_column='Observacion', max_length=255, blank=True, null=True)
    cliente = models.CharField(db_column='Cliente', max_length=201)
    venta_original = models.BigIntegerField(db_column='Venta_Original', blank=True, null=True)
    fecha_venta_original = models.DateTimeField(db_column='Fecha_Venta_Original', blank=True, null=True)
    monto_venta_original = models.DecimalField(db_column='Monto_Venta_Original', max_digits=12, decimal_places=2, blank=True, null=True)
    cantidad_items = models.IntegerField(db_column='Cantidad_Items')
    productos = models.TextField(db_column='Productos', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'v_notas_credito_detallado'
        verbose_name = 'Vista: Notas de Crédito Detallado'
        verbose_name_plural = 'Vista: Notas de Crédito Detallado'

    def __str__(self):
        return f'NC {self.id_nota} - {self.cliente}'


# =============================================================================
# MÓDULO DE ALMUERZOS - Diciembre 2025
# =============================================================================

class TipoAlmuerzo(models.Model):
    '''Tabla tipos_almuerzo - Catálogo de tipos de almuerzo'''
    id_tipo_almuerzo = models.AutoField(db_column='ID_Tipo_Almuerzo', primary_key=True)
    nombre = models.CharField(db_column='Nombre', max_length=100)
    descripcion = models.TextField(db_column='Descripcion', blank=True, null=True)
    precio_unitario = models.DecimalField(db_column='Precio_Unitario', max_digits=10, decimal_places=2)
    fecha_creacion = models.DateTimeField(db_column='Fecha_Creacion', auto_now_add=True)
    activo = models.BooleanField(db_column='Activo', default=True)

    class Meta:
        managed = False
        db_table = 'tipos_almuerzo'
        verbose_name = 'Tipo de Almuerzo'
        verbose_name_plural = 'Tipos de Almuerzo'

    def __str__(self):
        return f'{self.nombre} - Gs. {self.precio_unitario:,.0f}'


class RegistroConsumoAlmuerzo(models.Model):
    '''Tabla registro_consumo_almuerzo - Registro diario de almuerzos'''
    id_registro_consumo = models.BigAutoField(db_column='ID_Registro_Consumo', primary_key=True)
    id_hijo = models.ForeignKey(
        Hijo,
        on_delete=models.PROTECT,
        db_column='ID_Hijo'
    )
    nro_tarjeta = models.ForeignKey(
        Tarjeta,
        on_delete=models.PROTECT,
        db_column='Nro_Tarjeta',
        blank=True,
        null=True,
        related_name='registros_almuerzo'
    )
    id_tipo_almuerzo = models.ForeignKey(
        TipoAlmuerzo,
        on_delete=models.PROTECT,
        db_column='ID_Tipo_Almuerzo',
        blank=True,
        null=True
    )
    fecha_consumo = models.DateField(db_column='Fecha_Consumo', auto_now_add=True)
    costo_almuerzo = models.DecimalField(db_column='Costo_Almuerzo', max_digits=10, decimal_places=2, blank=True, null=True)
    marcado_en_cuenta = models.BooleanField(db_column='Marcado_En_Cuenta', default=False)
    id_suscripcion = models.BigIntegerField(db_column='ID_Suscripcion', blank=True, null=True)
    hora_registro = models.TimeField(db_column='Hora_Registro', auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'registro_consumo_almuerzo'
        verbose_name = 'Registro de Almuerzo'
        verbose_name_plural = 'Registros de Almuerzos'
        ordering = ['-fecha_consumo', '-hora_registro']

    def __str__(self):
        return f'{self.id_hijo.nombre_completo} - {self.fecha_consumo}'


class CuentaAlmuerzoMensual(models.Model):
    '''Tabla cuentas_almuerzo_mensual - Cuentas mensuales de almuerzo'''
    FORMA_COBRO_CHOICES = [
        ('CONTADO_ANTICIPADO', 'Contado Anticipado'),
        ('CREDITO_MENSUAL', 'Crédito Mensual'),
    ]
    
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('PARCIAL', 'Parcial'),
        ('PAGADO', 'Pagado'),
    ]

    id_cuenta = models.BigAutoField(db_column='ID_Cuenta', primary_key=True)
    id_hijo = models.ForeignKey(
        Hijo,
        on_delete=models.PROTECT,
        db_column='ID_Hijo'
    )
    anio = models.IntegerField(db_column='Anio')
    mes = models.SmallIntegerField(db_column='Mes')
    cantidad_almuerzos = models.IntegerField(db_column='Cantidad_Almuerzos', default=0)
    monto_total = models.DecimalField(db_column='Monto_Total', max_digits=10, decimal_places=2, default=0)
    forma_cobro = models.CharField(db_column='Forma_Cobro', max_length=20, choices=FORMA_COBRO_CHOICES)
    monto_pagado = models.DecimalField(db_column='Monto_Pagado', max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(db_column='Estado', max_length=10, choices=ESTADO_CHOICES, default='PENDIENTE')
    fecha_generacion = models.DateField(db_column='Fecha_Generacion')
    fecha_actualizacion = models.DateTimeField(db_column='Fecha_Actualizacion', auto_now=True)
    observaciones = models.TextField(db_column='Observaciones', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cuentas_almuerzo_mensual'
        verbose_name = 'Cuenta Mensual de Almuerzo'
        verbose_name_plural = 'Cuentas Mensuales de Almuerzo'
        unique_together = [['id_hijo', 'anio', 'mes']]
        ordering = ['-anio', '-mes']

    def __str__(self):
        return f'{self.id_hijo.nombre_completo} - {self.mes}/{self.anio}'
    
    @property
    def saldo_pendiente(self):
        return self.monto_total - self.monto_pagado
    
    @property
    def nombre_mes(self):
        meses = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        return meses[self.mes] if 1 <= self.mes <= 12 else ''


class PagoCuentaAlmuerzo(models.Model):
    '''Tabla pagos_cuentas_almuerzo - Pagos de cuentas de almuerzo'''
    MEDIO_PAGO_CHOICES = [
        ('EFECTIVO', 'Efectivo'),
        ('DEBITO', 'Débito'),
        ('CREDITO', 'Crédito'),
        ('TRANSFERENCIA', 'Transferencia'),
        ('OTRO', 'Otro'),
    ]

    id_pago = models.BigAutoField(db_column='ID_Pago', primary_key=True)
    id_cuenta = models.ForeignKey(
        CuentaAlmuerzoMensual,
        on_delete=models.PROTECT,
        db_column='ID_Cuenta',
        related_name='pagos'
    )
    fecha_pago = models.DateTimeField(db_column='Fecha_Pago', auto_now_add=True)
    medio_pago = models.CharField(db_column='Medio_Pago', max_length=15, choices=MEDIO_PAGO_CHOICES)
    monto = models.DecimalField(db_column='Monto', max_digits=10, decimal_places=2)
    referencia = models.CharField(db_column='Referencia', max_length=50, blank=True, null=True)
    observaciones = models.TextField(db_column='Observaciones', blank=True, null=True)
    id_empleado_registro = models.ForeignKey(
        'Empleado',
        on_delete=models.SET_NULL,
        db_column='ID_Empleado_Registro',
        blank=True,
        null=True
    )

    class Meta:
        managed = False
        db_table = 'pagos_cuentas_almuerzo'
        verbose_name = 'Pago de Cuenta de Almuerzo'
        verbose_name_plural = 'Pagos de Cuentas de Almuerzo'
        ordering = ['-fecha_pago']

    def __str__(self):
        return f'Pago #{self.id_pago} - Gs. {self.monto:,.0f}'


# =============================================================================
# VISTAS DEL MÓDULO DE ALMUERZOS
# =============================================================================

class VistaAlmuerzosDiarios(models.Model):
    '''Vista v_almuerzos_diarios - Almuerzos registrados con detalles'''
    id_registro_consumo = models.BigIntegerField(db_column='ID_Registro_Consumo', primary_key=True)
    fecha_consumo = models.DateField(db_column='Fecha_Consumo')
    hora_registro = models.TimeField(db_column='Hora_Registro')
    id_hijo = models.IntegerField(db_column='ID_Hijo')
    estudiante = models.CharField(db_column='Estudiante', max_length=202)
    responsable_nombre = models.CharField(db_column='Responsable_Nombre', max_length=100)
    responsable_apellido = models.CharField(db_column='Responsable_Apellido', max_length=100)
    nro_tarjeta = models.CharField(db_column='Nro_Tarjeta', max_length=20, blank=True, null=True)
    tipo_almuerzo = models.CharField(db_column='Tipo_Almuerzo', max_length=100, blank=True, null=True)
    descripcion_almuerzo = models.TextField(db_column='Descripcion_Almuerzo', blank=True, null=True)
    costo_almuerzo = models.DecimalField(db_column='Costo_Almuerzo', max_digits=10, decimal_places=2, blank=True, null=True)
    marcado_en_cuenta = models.BooleanField(db_column='Marcado_En_Cuenta')
    origen = models.CharField(db_column='Origen', max_length=11)
    id_suscripcion = models.BigIntegerField(db_column='ID_Suscripcion', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'v_almuerzos_diarios'
        verbose_name = 'Vista: Almuerzos Diarios'
        verbose_name_plural = 'Vista: Almuerzos Diarios'

    def __str__(self):
        return f'{self.estudiante} - {self.fecha_consumo}'


class VistaCuentasAlmuerzoDetallado(models.Model):
    '''Vista v_cuentas_almuerzo_detallado - Cuentas mensuales con detalles'''
    id_cuenta = models.BigIntegerField(db_column='ID_Cuenta', primary_key=True)
    id_hijo = models.IntegerField(db_column='ID_Hijo')
    estudiante = models.CharField(db_column='Estudiante', max_length=202)
    responsable_nombre = models.CharField(db_column='Responsable_Nombre', max_length=100)
    responsable_apellido = models.CharField(db_column='Responsable_Apellido', max_length=100)
    responsable_telefono = models.CharField(db_column='Responsable_Telefono', max_length=20, blank=True, null=True)
    anio = models.IntegerField(db_column='Anio')
    mes = models.SmallIntegerField(db_column='Mes')
    cantidad_almuerzos = models.IntegerField(db_column='Cantidad_Almuerzos')
    monto_total = models.DecimalField(db_column='Monto_Total', max_digits=10, decimal_places=2)
    forma_cobro = models.CharField(db_column='Forma_Cobro', max_length=20)
    monto_pagado = models.DecimalField(db_column='Monto_Pagado', max_digits=10, decimal_places=2)
    saldo_pendiente = models.DecimalField(db_column='Saldo_Pendiente', max_digits=11, decimal_places=2)
    estado = models.CharField(db_column='Estado', max_length=10)
    fecha_generacion = models.DateField(db_column='Fecha_Generacion')
    fecha_actualizacion = models.DateTimeField(db_column='Fecha_Actualizacion')
    cantidad_pagos = models.BigIntegerField(db_column='Cantidad_Pagos')

    class Meta:
        managed = False
        db_table = 'v_cuentas_almuerzo_detallado'
        verbose_name = 'Vista: Cuentas de Almuerzo Detallado'
        verbose_name_plural = 'Vista: Cuentas de Almuerzo Detallado'

    def __str__(self):
        return f'{self.estudiante} - {self.mes}/{self.anio}'


class VistaReporteMensualSeparado(models.Model):
    '''Vista v_reporte_mensual_separado - Reporte mensual: almuerzos vs tarjeta'''
    id_hijo = models.IntegerField(db_column='ID_Hijo', primary_key=True)
    estudiante = models.CharField(db_column='Estudiante', max_length=202)
    nro_tarjeta = models.CharField(db_column='Nro_Tarjeta', max_length=20, blank=True, null=True)
    saldo_tarjeta_actual = models.BigIntegerField(db_column='Saldo_Tarjeta_Actual', blank=True, null=True)
    almuerzos_mes_actual = models.DecimalField(db_column='Almuerzos_Mes_Actual', max_digits=23, decimal_places=0)
    total_almuerzos_mes = models.DecimalField(db_column='Total_Almuerzos_Mes', max_digits=32, decimal_places=2)
    consumos_tarjeta_mes = models.DecimalField(db_column='Consumos_Tarjeta_Mes', max_digits=32, decimal_places=2)
    cargas_tarjeta_mes = models.DecimalField(db_column='Cargas_Tarjeta_Mes', max_digits=32, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'v_reporte_mensual_separado'
        verbose_name = 'Vista: Reporte Mensual Separado'
        verbose_name_plural = 'Vista: Reportes Mensuales Separados'

    def __str__(self):
        return f'{self.estudiante} - Mes Actual'
