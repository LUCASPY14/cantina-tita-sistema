# gestion/models/fiscal.py

from django.db import models
from .base import ManagedModel
from .empleados import Empleado

class DatosEmpresa(ManagedModel):
    '''Tabla datos_empresa - Información de la empresa'''
    id_empresa = models.IntegerField(db_column='id_empresa', primary_key=True)
    ruc = models.CharField(db_column='ruc', max_length=20)
    razon_social = models.CharField(db_column='razon_social', max_length=255)
    direccion = models.CharField(db_column='direccion', max_length=255, blank=True, null=True)
    ciudad = models.CharField(db_column='ciudad', max_length=100, blank=True, null=True)
    pais = models.CharField(db_column='pais', max_length=100, blank=True, null=True)
    telefono = models.CharField(db_column='telefono', max_length=20, blank=True, null=True)
    email = models.CharField(db_column='email', max_length=100, blank=True, null=True)
    activo = models.IntegerField(db_column='activo', blank=True, null=True)

    class Meta(ManagedModel.Meta):
        db_table = 'datos_empresa'
        verbose_name = 'Datos de la Empresa'
        verbose_name_plural = 'Datos de la Empresa'

    def __str__(self):
        return self.razon_social


class PuntosExpedicion(ManagedModel):
    '''Tabla puntos_expedicion - Puntos de expedición de documentos fiscales'''
    id_punto = models.AutoField(db_column='id_punto', primary_key=True)
    codigo_establecimiento = models.CharField(db_column='codigo_establecimiento', max_length=3)
    codigo_punto_expedicion = models.CharField(db_column='codigo_punto_expedicion', max_length=3)
    descripcion_ubicacion = models.CharField(db_column='descripcion_ubicacion', max_length=100, blank=True, null=True)
    activo = models.BooleanField(db_column='activo', default=True)

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

    nro_timbrado = models.IntegerField(db_column='nro_timbrado', primary_key=True)
    id_punto = models.ForeignKey(
        PuntosExpedicion,
        on_delete=models.PROTECT,
        db_column='id_punto'
    )
    tipo_documento = models.CharField(db_column='tipo_documento', max_length=12, choices=TIPO_DOCUMENTO_CHOICES)
    fecha_inicio = models.DateField(db_column='fecha_inicio')
    fecha_fin = models.DateField(db_column='fecha_fin')
    nro_inicial = models.IntegerField(db_column='nro_inicial')
    nro_final = models.IntegerField(db_column='nro_final')
    es_electronico = models.BooleanField(db_column='es_electronico', default=False)
    activo = models.BooleanField(db_column='activo', default=True)

    class Meta(ManagedModel.Meta):
        db_table = 'timbrados'
        verbose_name = 'Timbrado'
        verbose_name_plural = 'Timbrados'

    def __str__(self):
        return f'Timbrado {self.nro_timbrado} - {self.tipo_documento}'


class DocumentosTributarios(ManagedModel):
    '''Tabla documentos_tributarios - Documentos tributarios emitidos'''
    id_documento = models.BigAutoField(db_column='id_documento', primary_key=True)
    nro_timbrado = models.ForeignKey(
        Timbrados,
        on_delete=models.PROTECT,
        db_column='nro_timbrado'
    )
    nro_secuencial = models.IntegerField(db_column='nro_secuencial')
    fecha_emision = models.DateTimeField(db_column='fecha_emision')
    monto_total = models.BigIntegerField(db_column='monto_total')
    monto_exento = models.DecimalField(db_column='monto_exento', max_digits=12, decimal_places=2, blank=True, null=True)
    monto_gravado_5 = models.DecimalField(db_column='monto_gravado_5', max_digits=12, decimal_places=2, blank=True, null=True)
    monto_iva_5 = models.DecimalField(db_column='monto_iva_5', max_digits=10, decimal_places=2, blank=True, null=True)
    monto_gravado_10 = models.DecimalField(db_column='monto_gravado_10', max_digits=12, decimal_places=2, blank=True, null=True)
    monto_iva_10 = models.DecimalField(db_column='monto_iva_10', max_digits=10, decimal_places=2, blank=True, null=True)

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
        db_column='id_documento',
        primary_key=True
    )
    cdc = models.CharField(db_column='cdc', max_length=44, unique=True)
    url_kude = models.CharField(db_column='url_kude', max_length=255, blank=True, null=True)
    xml_transmitido = models.TextField(db_column='xml_transmitido', blank=True, null=True)
    estado_sifen = models.CharField(db_column='estado_sifen', max_length=9, blank=True, null=True)
    fecha_envio = models.DateTimeField(db_column='fecha_envio', blank=True, null=True)
    fecha_respuesta = models.DateTimeField(db_column='fecha_respuesta', blank=True, null=True)

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
        db_column='id_documento',
        primary_key=True
    )
    nro_preimpreso_interno = models.CharField(db_column='nro_preimpreso_interno', max_length=20, unique=True)

    class Meta(ManagedModel.Meta):
        db_table = 'datos_facturacion_fisica'
        verbose_name = 'Datos Facturación Física'
        verbose_name_plural = 'Datos Facturación Física'

    def __str__(self):
        return f'Factura Física {self.nro_preimpreso_interno}'


class Cajas(ManagedModel):
    '''Tabla cajas - Cajas de punto de venta'''
    id_caja = models.AutoField(db_column='id_caja', primary_key=True)
    nombre_caja = models.CharField(db_column='nombre_caja', max_length=50)
    ubicacion = models.CharField(db_column='ubicacion', max_length=100, blank=True, null=True)
    activo = models.IntegerField(db_column='activo', blank=True, null=True)

    class Meta(ManagedModel.Meta):
        db_table = 'cajas'
        verbose_name = 'Caja'
        verbose_name_plural = 'Cajas'

    def __str__(self):
        return f'{self.nombre_caja}'


class CierresCaja(ManagedModel):
    '''Tabla cierres_caja - Cierres de caja'''
    id_cierre = models.BigAutoField(db_column='id_cierre', primary_key=True)
    id_caja = models.ForeignKey(
        Cajas,
        on_delete=models.PROTECT,
        db_column='id_caja'
    )
    id_empleado = models.ForeignKey(
        Empleado,
        on_delete=models.PROTECT,
        db_column='id_empleado'
    )
    fecha_hora_apertura = models.DateTimeField(db_column='fecha_hora_apertura')
    fecha_hora_cierre = models.DateTimeField(db_column='fecha_hora_cierre', blank=True, null=True)
    monto_inicial = models.DecimalField(db_column='monto_inicial', max_digits=10, decimal_places=2, blank=True, null=True)
    monto_contado_fisico = models.DecimalField(db_column='monto_contado_fisico', max_digits=10, decimal_places=2, blank=True, null=True)
    diferencia_efectivo = models.DecimalField(db_column='diferencia_efectivo', max_digits=10, decimal_places=2, blank=True, null=True)
    estado = models.CharField(db_column='estado', max_length=7, blank=True, null=True)

    class Meta(ManagedModel.Meta):
        db_table = 'cierres_caja'
        verbose_name = 'Cierre de Caja'
        verbose_name_plural = 'Cierres de Caja'

    def __str__(self):
        return f'Cierre #{self.id_cierre} - {self.id_caja.nombre_caja}'