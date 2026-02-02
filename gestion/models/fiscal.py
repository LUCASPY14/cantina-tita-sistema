# gestion/models/fiscal.py

from django.db import models
from .base import ManagedModel
from .empleados import Empleado

class DatosEmpresa(ManagedModel):
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

    class Meta(ManagedModel.Meta):
        db_table = 'datos_empresa'
        verbose_name = 'Datos de la Empresa'
        verbose_name_plural = 'Datos de la Empresa'

    def __str__(self):
        return self.razon_social


class PuntosExpedicion(ManagedModel):
    '''Tabla puntos_expedicion - Puntos de expedición de documentos fiscales'''
    id_punto = models.AutoField(db_column='ID_Punto', primary_key=True)
    codigo_establecimiento = models.CharField(db_column='Codigo_Establecimiento', max_length=3)
    codigo_punto_expedicion = models.CharField(db_column='Codigo_Punto_Expedicion', max_length=3)
    descripcion_ubicacion = models.CharField(db_column='Descripcion_Ubicacion', max_length=100, blank=True, null=True)
    activo = models.BooleanField(db_column='Activo', default=True)

    class Meta(ManagedModel.Meta):
        db_table = 'puntos_expedicion'
        verbose_name = 'Punto de Expedición'
        verbose_name_plural = 'Puntos de Expedición'
        unique_together = (('codigo_establecimiento', 'codigo_punto_expedicion'),)

    def __str__(self):
        return f'{self.codigo_establecimiento}-{self.codigo_punto_expedicion}'


class Timbrados(ManagedModel):
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

    class Meta(ManagedModel.Meta):
        db_table = 'timbrados'
        verbose_name = 'Timbrado'
        verbose_name_plural = 'Timbrados'

    def __str__(self):
        return f'Timbrado {self.nro_timbrado} - {self.tipo_documento}'


class DocumentosTributarios(ManagedModel):
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

    class Meta(ManagedModel.Meta):
        db_table = 'documentos_tributarios'
        verbose_name = 'Documento Tributario'
        verbose_name_plural = 'Documentos Tributarios'
        unique_together = (('nro_timbrado', 'nro_secuencial'),)

    def __str__(self):
        return f'Doc {self.id_documento} - Timbrado {self.nro_timbrado_id}: Gs. {self.monto_total}'


class DatosFacturacionElect(ManagedModel):
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

    class Meta(ManagedModel.Meta):
        db_table = 'datos_facturacion_elect'
        verbose_name = 'Datos Facturación Electrónica'
        verbose_name_plural = 'Datos Facturación Electrónica'

    def __str__(self):
        return f'CDC: {self.cdc}'


class DatosFacturacionFisica(ManagedModel):
    '''Tabla datos_facturacion_fisica - Datos específicos de facturación física'''
    id_documento = models.OneToOneField(
        DocumentosTributarios,
        on_delete=models.CASCADE,
        db_column='ID_Documento',
        primary_key=True
    )
    nro_preimpreso_interno = models.CharField(db_column='Nro_Preimpreso_Interno', max_length=20, unique=True)

    class Meta(ManagedModel.Meta):
        db_table = 'datos_facturacion_fisica'
        verbose_name = 'Datos Facturación Física'
        verbose_name_plural = 'Datos Facturación Física'

    def __str__(self):
        return f'Factura Física {self.nro_preimpreso_interno}'


class Cajas(ManagedModel):
    '''Tabla cajas - Cajas de punto de venta'''
    id_caja = models.AutoField(db_column='ID_Caja', primary_key=True)
    nombre_caja = models.CharField(db_column='Nombre_Caja', max_length=50)
    ubicacion = models.CharField(db_column='Ubicacion', max_length=100, blank=True, null=True)
    activo = models.IntegerField(db_column='Activo', blank=True, null=True)

    class Meta(ManagedModel.Meta):
        db_table = 'cajas'
        verbose_name = 'Caja'
        verbose_name_plural = 'Cajas'

    def __str__(self):
        return f'{self.nombre_caja}'


class CierresCaja(ManagedModel):
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

    class Meta(ManagedModel.Meta):
        db_table = 'cierres_caja'
        verbose_name = 'Cierre de Caja'
        verbose_name_plural = 'Cierres de Caja'

    def __str__(self):
        return f'Cierre #{self.id_cierre} - {self.id_caja.nombre_caja}'