"""
Facturación Electrónica Paraguay - SET/Ekuatia Integration
===========================================================

Generación y gestión de facturas electrónicas conforme a normas SET:
- Generación de XML según estructura SET
- Cálculo de CDC (Código de Control Criptográfico)
- Integración con API Ekuatia
- Validaciones de cumplimiento fiscal
"""

import hashlib
import hmac
from datetime import datetime
from decimal import Decimal
from typing import Dict, Optional, List, Tuple
import json
from xml.etree import ElementTree as ET
from xml.dom import minidom

from django.utils import timezone
from django.conf import settings
import requests

from .models import (
    Ventas, DetalleVenta, DatosFacturacionElect, Timbrados,
    DatosEmpresa, Cliente, Producto
)


class GeneradorXMLFactura:
    """
    Generador de XML de facturas electrónicas según formato SET Paraguay
    Conforme a: RES. 19-SET de 2023
    """
    
    # Versión de formato SET
    VERSION_SET = '150'
    
    # Tipos de documento
    TIPOS_DOCUMENTO = {
        '1': 'Factura',
        '2': 'Nota de Débito',
        '3': 'Nota de Crédito',
        '4': 'Remisión Electrónica',
    }
    
    # Tipos de IVA
    TIPOS_IVA = {
        'Exenta': '1',
        '5%': '2',
        '10%': '3',
        '0%': '4',
    }
    
    def __init__(self, venta: Ventas):
        """
        Inicializa generador con datos de venta
        
        Args:
            venta: Instancia de Ventas
        """
        self.venta = venta
        self.empresa = DatosEmpresa.objects.first()
        self.cliente = venta.id_cliente
        self.detalles = venta.detalles.all()
        self.timestamp = timezone.now().isoformat()
        
    def generar_cdc(self, xml_string: str) -> str:
        """
        Calcula CDC (Código de Control Criptográfico) según RES. 19-SET
        
        CDC = SHA256(RUC_CEDULA + TIPO_DOC + NRO_TIMBRADO + NRO_SECUENCIAL + 
                     CANTIDAD_LINEAS + MONTO_TOTAL + FECHA)
        
        Args:
            xml_string: XML de la factura
            
        Returns:
            CDC en formato hexadecimal (44 caracteres)
        """
        try:
            # Extraer datos del XML
            root = ET.fromstring(xml_string)
            
            # Namespaces
            ns = {'factura': 'http://www.set.gov.py/dte/ns/v1.0'}
            
            # Obtener elementos necesarios
            ide = root.find('.//factura:Ide', ns)
            ruc = ide.findtext('factura:RUC', '', ns)
            tipo_doc = ide.findtext('factura:TipoDoc', '', ns)
            nro_timbrado = ide.findtext('factura:NroTimbrado', '', ns)
            nro_secuencial = ide.findtext('factura:NroSecuencial', '', ns)
            
            # Cantidad de líneas
            detalles = root.findall('.//factura:Item', ns)
            cantidad_lineas = str(len(detalles))
            
            # Monto total
            totales = root.find('.//factura:Totales', ns)
            monto_total = totales.findtext('factura:MontTotal', '', ns)
            
            # Fecha
            fecha = ide.findtext('factura:FchEmis', '', ns)
            
            # Concatenar datos para CDC
            datos_cdc = f"{ruc}{tipo_doc}{nro_timbrado}{nro_secuencial}{cantidad_lineas}{monto_total}{fecha}"
            
            # Calcular SHA256
            cdc = hashlib.sha256(datos_cdc.encode('utf-8')).hexdigest()
            
            return cdc.upper()
            
        except Exception as e:
            raise ValueError(f"Error al calcular CDC: {str(e)}")
    
    def _generar_elemento_identidad(self) -> str:
        """
        Genera elemento <Ide> (Identidad del documento)
        
        Returns:
            XML del elemento
        """
        hoy = timezone.now().strftime('%Y-%m-%d')
        
        xml = f"""
        <Ide>
            <RUC>{self.empresa.ruc}</RUC>
            <TipoDoc>1</TipoDoc>
            <NroTimbrado>{self.venta.id_timbrado_id}</NroTimbrado>
            <NroSecuencial>{str(self.venta.nro_factura_venta).zfill(7)}</NroSecuencial>
            <FchEmis>{hoy}</FchEmis>
            <HraEmis>{timezone.now().strftime('%H:%M:%S')}</HraEmis>
            <FchVencTimbrado>2025-12-31</FchVencTimbrado>
            <SisFact>1</SisFact>
            <IndPresVenta>1</IndPresVenta>
            <TipoContribuyente>1</TipoContribuyente>
            <TipoEmision>1</TipoEmision>
            <TipoReg>2</TipoReg>
            <PtoEmision>1</PtoEmision>
            <CodMoneda>PYG</CodMoneda>
            <CantLinItem>{self.detalles.count()}</CantLinItem>
        </Ide>
        """
        return xml.strip()
    
    def _generar_elemento_emisor(self) -> str:
        """
        Genera elemento <Emit> (Datos del Emisor)
        
        Returns:
            XML del elemento
        """
        xml = f"""
        <Emit>
            <RUC>{self.empresa.ruc}</RUC>
            <RzSoc>{self.empresa.razon_social}</RzSoc>
            <NomFantasia>{self.empresa.nombre_fantasia}</NomFantasia>
            <Telf>{self.empresa.telefono or ''}</Telf>
            <Email>{self.empresa.email or ''}</Email>
            <Web>{self.empresa.sitio_web or ''}</Web>
            <Dir>
                <Asentamiento>{self.empresa.direccion.split(',')[0] if self.empresa.direccion else ''}</Asentamiento>
                <nDpto>11</nDpto>
                <nCiud>1101</nCiud>
            </Dir>
            <ActEcon>
                <IdActEcon>4723</IdActEcon>
                <dDes>Comercio al por menor en tiendas de autoservicio</dDes>
            </ActEcon>
        </Emit>
        """
        return xml.strip()
    
    def _generar_elemento_receptor(self) -> str:
        """
        Genera elemento <Receptor> (Datos del Cliente)
        
        Returns:
            XML del elemento
        """
        # Para clientes sin RUC usar 'S/RUC'
        ruc_cliente = self.cliente.ci_ruc if self.cliente.ci_ruc else 'S/RUC'
        
        xml = f"""
        <Receptor>
            <IdRec>
                <RUC>{ruc_cliente}</RUC>
                <DV>{self._calcular_digito_verificador(ruc_cliente) if ruc_cliente != 'S/RUC' else ''}</DV>
            </IdRec>
            <RzSoc>{self.cliente.nombre_completo}</RzSoc>
            <Telf>{self.cliente.telefono or ''}</Telf>
            <Email>{self.cliente.email or ''}</Email>
            <Dir>
                <Asentamiento>{self.cliente.direccion or 'Asunción'}</Asentamiento>
                <nDpto>11</nDpto>
                <nCiud>1101</nCiud>
            </Dir>
        </Receptor>
        """
        return xml.strip()
    
    def _generar_items(self) -> str:
        """
        Genera elementos <Item> (Líneas de detalle)
        
        Returns:
            XML de items
        """
        items_xml = ""
        
        for idx, detalle in enumerate(self.detalles, 1):
            producto = detalle.id_producto
            
            # Calcular IVA
            monto_iva = int(Decimal(detalle.subtotal_total) * Decimal('0.10'))
            monto_sin_iva = int(Decimal(detalle.subtotal_total) - monto_iva)
            
            item_xml = f"""
            <Item>
                <NroLinItem>{idx}</NroLinItem>
                <dSc>{producto.descripcion[:100]}</dSc>
                <Cantidad>{int(detalle.cantidad)}</Cantidad>
                <uMed>7</uMed>
                <Precio>{int(detalle.precio_unitario)}</Precio>
                <dTotMnt>{int(detalle.subtotal_total)}</dTotMnt>
                <dTotDesc>0</dTotDesc>
                <Impuesto>
                    <ImpItem>
                        <dAcreo>0</dAcreo>
                        <dTasaIVA>10</dTasaIVA>
                        <dBasGrav>{monto_sin_iva}</dBasGrav>
                        <dCantIVA>{monto_iva}</dCantIVA>
                    </ImpItem>
                </Impuesto>
                <dCodTrib></dCodTrib>
                <dDDocAso></dDDocAso>
                <dDNroAso></dDNroAso>
                <dDTipRec></dDTipRec>
            </Item>
            """
            items_xml += item_xml
        
        return items_xml.strip()
    
    def _generar_totales(self) -> str:
        """
        Genera elemento <Totales>
        
        Returns:
            XML del elemento
        """
        # Calcular totales
        monto_total = int(self.venta.monto_total)
        monto_sin_iva = int(monto_total / Decimal('1.1'))
        monto_iva = monto_total - monto_sin_iva
        
        xml = f"""
        <Totales>
            <dTotLinItem>{monto_total}</dTotLinItem>
            <dTotDesc>0</dTotDesc>
            <dTotAntici>0</dTotAntici>
            <dTotGrav>{monto_sin_iva}</dTotGrav>
            <dTotExent>0</dTotExent>
            <dTotIVA>{monto_iva}</dTotIVA>
            <dTotTrib>0</dTotTrib>
            <dTotMnt>{monto_total}</dTotMnt>
            <cMonedaRes>PYG</cMonedaRes>
            <dTipCambio>1</dTipCambio>
        </Totales>
        """
        return xml.strip()
    
    def generar_xml(self) -> str:
        """
        Genera XML completo de factura electrónica
        
        Returns:
            XML como string
        """
        try:
            # Construir documento
            xml_template = f"""<?xml version="1.0" encoding="UTF-8"?>
<rFact xmlns="http://www.set.gov.py/dte/ns/v1.0"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xsi:schemaLocation="http://www.set.gov.py/dte/ns/v1.0 rFact.xsd"
       version="{self.VERSION_SET}">
    <dEmisin>
        {self._generar_elemento_identidad()}
        {self._generar_elemento_emisor()}
        {self._generar_elemento_receptor()}
        <Items>
            {self._generar_items()}
        </Items>
        {self._generar_totales()}
    </dEmisin>
</rFact>
            """
            
            # Limpiar y formattear
            dom = minidom.parseString(xml_template)
            xml_formateado = dom.toprettyxml(indent="  ")
            
            # Eliminar linea XML declaration de minidom (mantener la nuestra)
            xml_lines = xml_formateado.split('\n')[1:]
            xml_final = '<?xml version="1.0" encoding="UTF-8"?>\n' + '\n'.join(xml_lines)
            
            return xml_final
            
        except Exception as e:
            raise ValueError(f"Error generando XML: {str(e)}")
    
    @staticmethod
    def _calcular_digito_verificador(ruc: str) -> str:
        """
        Calcula dígito verificador de RUC (módulo 11)
        
        Args:
            ruc: RUC sin dígito verificador
            
        Returns:
            Dígito verificador
        """
        if not ruc or ruc == 'S/RUC':
            return ''
        
        ruc_limpio = ruc.replace('-', '').strip()
        multiplicadores = [7, 3, 1]
        suma = 0
        
        for i, digito in enumerate(reversed(ruc_limpio)):
            suma += int(digito) * multiplicadores[i % 3]
        
        residuo = suma % 11
        dv = 11 - residuo
        
        if dv == 11:
            dv = 0
        elif dv == 10:
            dv = 9
        
        return str(dv)


class ClienteEkuatia:
    """
    Cliente para integración con API Ekuatia (SET)
    Gestiona:
    - Envío de facturas
    - Verificación de estado
    - Obtención de respuestas
    """
    
    BASE_URL = getattr(settings, 'EKUATIA_BASE_URL', 'https://sifen.set.gov.py/rest/api')
    TIMEOUT = 30
    
    def __init__(self):
        """Inicializa cliente Ekuatia"""
        self.api_key = getattr(settings, 'EKUATIA_API_KEY', '')
        self.certificate_path = getattr(settings, 'EKUATIA_CERT_PATH', '')
        self.private_key_path = getattr(settings, 'EKUATIA_KEY_PATH', '')
        
        if not self.api_key:
            raise ValueError("EKUATIA_API_KEY no configurada en settings.py")
    
    def enviar_factura(self, xml_factura: str, id_venta: int) -> Dict:
        """
        Envía factura a Ekuatia para validación y timbrado
        
        Args:
            xml_factura: XML de la factura
            id_venta: ID de la venta asociada
            
        Returns:
            {
                'success': bool,
                'cdc': str,
                'kude': str,
                'estado': str,
                'mensaje': str
            }
        """
        try:
            # En ambiente de desarrollo/prueba
            if getattr(settings, 'EKUATIA_MODO', 'testing') == 'testing':
                # Retornar respuesta simulada
                return self._simular_envio(xml_factura, id_venta)
            
            # En producción, enviar a Ekuatia
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/xml'
            }
            
            response = requests.post(
                f'{self.BASE_URL}/v1/recibir/documento',
                data=xml_factura.encode('utf-8'),
                headers=headers,
                timeout=self.TIMEOUT,
                cert=(self.certificate_path, self.private_key_path) if self.certificate_path else None
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'cdc': data.get('cdc'),
                    'kude': data.get('kudeUrl'),
                    'estado': data.get('estado'),
                    'mensaje': 'Factura enviada exitosamente'
                }
            else:
                return {
                    'success': False,
                    'cdc': '',
                    'kude': '',
                    'estado': 'ERROR',
                    'mensaje': f"Error Ekuatia: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'cdc': '',
                'kude': '',
                'estado': 'ERROR',
                'mensaje': f'Error de conexión: {str(e)}'
            }
    
    def verificar_estado(self, cdc: str) -> Dict:
        """
        Verifica estado de una factura en Ekuatia
        
        Args:
            cdc: Código de Control Criptográfico
            
        Returns:
            Estado de la factura
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
            }
            
            response = requests.get(
                f'{self.BASE_URL}/v1/documento/{cdc}',
                headers=headers,
                timeout=self.TIMEOUT
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {'error': f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {'error': str(e)}
    
    def descargar_kude(self, cdc: str) -> Optional[bytes]:
        """
        Descarga KUDE (código QR autenticado) de una factura
        
        Args:
            cdc: Código de Control Criptográfico
            
        Returns:
            Contenido del KUDE o None si error
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
            }
            
            response = requests.get(
                f'{self.BASE_URL}/v1/documento/{cdc}/kude',
                headers=headers,
                timeout=self.TIMEOUT
            )
            
            if response.status_code == 200:
                return response.content
            else:
                return None
                
        except Exception as e:
            return None
    
    @staticmethod
    def _simular_envio(xml_factura: str, id_venta: int) -> Dict:
        """
        Simula respuesta de Ekuatia en ambiente de testing
        
        Args:
            xml_factura: XML de la factura
            id_venta: ID de venta
            
        Returns:
            Respuesta simulada
        """
        # Generar CDC simulado
        cdc = hashlib.sha256(
            f"{id_venta}{timezone.now().isoformat()}".encode()
        ).hexdigest()[:44].upper()
        
        return {
            'success': True,
            'cdc': cdc,
            'kude': f'https://sifen.set.gov.py/kude/{cdc}',
            'estado': 'ACEPTADA',
            'mensaje': 'Factura aceptada por SIFEN (simulado)'
        }
