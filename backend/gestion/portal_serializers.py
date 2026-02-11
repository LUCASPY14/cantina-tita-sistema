# Portal de Padres - Serializers para API REST
# Serialización de modelos para endpoints móviles

from rest_framework import serializers
from .models import (
    Tarjeta, ConsumoTarjeta, CargasSaldo, Hijo,
    TransaccionOnline, Notificacion
)


class HijoSerializer(serializers.ModelSerializer):
    """Serializer para información básica del hijo"""
    
    nombre_completo = serializers.SerializerMethodField()
    grado_actual = serializers.CharField(source='grado', read_only=True)
    
    class Meta:
        model = Hijo
        fields = [
            'id_hijo',
            'nombres',
            'apellidos',
            'nombre_completo',
            'grado_actual',
            'seccion',
            'foto_perfil'
        ]
    
    def get_nombre_completo(self, obj):
        return f"{obj.nombres} {obj.apellidos}"


class TarjetaSerializer(serializers.ModelSerializer):
    """Serializer para tarjeta con información del hijo"""
    
    hijo = HijoSerializer(source='id_hijo', read_only=True)
    saldo_formateado = serializers.SerializerMethodField()
    estado_badge = serializers.SerializerMethodField()
    dias_vencimiento = serializers.SerializerMethodField()
    
    class Meta:
        model = Tarjeta
        fields = [
            'nro_tarjeta',
            'hijo',
            'saldo_actual',
            'saldo_formateado',
            'estado',
            'estado_badge',
            'fecha_vencimiento',
            'dias_vencimiento',
            'saldo_alerta',
            'tipo_autorizacion'
        ]
    
    def get_saldo_formateado(self, obj):
        """Formatear saldo con separadores de miles"""
        return f"₲ {obj.saldo_actual:,.0f}"
    
    def get_estado_badge(self, obj):
        """Devolver clase CSS para el badge del estado"""
        badges = {
            'Activa': 'badge-success',
            'Bloqueada': 'badge-error',
            'Vencida': 'badge-warning'
        }
        return badges.get(obj.estado, 'badge-neutral')
    
    def get_dias_vencimiento(self, obj):
        """Calcular días hasta el vencimiento"""
        from django.utils import timezone
        if obj.fecha_vencimiento:
            delta = obj.fecha_vencimiento - timezone.now().date()
            return delta.days
        return None


class ConsumoTarjetaSerializer(serializers.ModelSerializer):
    """Serializer para consumos de tarjeta"""
    
    monto_formateado = serializers.SerializerMethodField()
    producto_nombre = serializers.SerializerMethodField()
    
    class Meta:
        model = ConsumoTarjeta
        fields = [
            'id_consumo',
            'nro_tarjeta',
            'monto',
            'monto_formateado',
            'cantidad',
            'producto_nombre',
            'fecha_consumo',
            'tipo_consumo'
        ]
        read_only_fields = ['id_consumo', 'fecha_consumo']
    
    def get_monto_formateado(self, obj):
        return f"₲ {obj.monto:,.0f}"
    
    def get_producto_nombre(self, obj):
        # Aquí asumo que hay una relación con Producto
        # Ajustar según tu modelo
        return "Consumo"


class CargaSaldoSerializer(serializers.ModelSerializer):
    """Serializer para recargas de saldo"""
    
    monto_formateado = serializers.SerializerMethodField()
    metodo_pago_nombre = serializers.SerializerMethodField()
    
    class Meta:
        model = CargasSaldo
        fields = [
            'id_carga',
            'nro_tarjeta',
            'monto',
            'monto_formateado',
            'fecha_carga',
            'metodo_pago',
            'metodo_pago_nombre',
            'referencia_pago'
        ]
        read_only_fields = ['id_carga', 'fecha_carga']
    
    def get_monto_formateado(self, obj):
        return f"₲ {obj.monto:,.0f}"
    
    def get_metodo_pago_nombre(self, obj):
        # Obtener nombre del medio de pago si existe la relación
        if hasattr(obj, 'metodo_pago') and obj.metodo_pago:
            return obj.metodo_pago.nombre
        return "No especificado"


class TransaccionOnlineSerializer(serializers.ModelSerializer):
    """Serializer para transacciones online del portal"""
    
    monto_formateado = serializers.SerializerMethodField()
    metodo_pago_display = serializers.CharField(source='get_metodo_pago_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    class Meta:
        model = TransaccionOnline
        fields = [
            'id_transaccion',
            'nro_tarjeta',
            'monto',
            'monto_formateado',
            'metodo_pago',
            'metodo_pago_display',
            'estado',
            'estado_display',
            'referencia_pago',
            'id_transaccion_externa',
            'fecha_transaccion'
        ]
        read_only_fields = ['id_transaccion', 'fecha_transaccion']
    
    def get_monto_formateado(self, obj):
        return f"₲ {obj.monto:,.0f}"


class NotificacionSerializer(serializers.ModelSerializer):
    """Serializer para notificaciones del usuario"""
    
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    tiempo_transcurrido = serializers.SerializerMethodField()
    
    class Meta:
        model = Notificacion
        fields = [
            'id_notificacion',
            'tipo',
            'tipo_display',
            'titulo',
            'mensaje',
            'leida',
            'fecha_envio',
            'tiempo_transcurrido'
        ]
        read_only_fields = ['id_notificacion', 'fecha_envio']
    
    def get_tiempo_transcurrido(self, obj):
        """Devolver tiempo transcurrido en formato legible"""
        from django.utils import timezone
        delta = timezone.now() - obj.fecha_envio
        
        if delta.days > 0:
            return f"Hace {delta.days} día(s)"
        elif delta.seconds >= 3600:
            horas = delta.seconds // 3600
            return f"Hace {horas} hora(s)"
        elif delta.seconds >= 60:
            minutos = delta.seconds // 60
            return f"Hace {minutos} minuto(s)"
        else:
            return "Hace unos segundos"


# Serializers para creación/actualización

class RecargaTarjetaSerializer(serializers.Serializer):
    """Serializer para solicitudes de recarga"""
    
    nro_tarjeta = serializers.CharField(max_length=20)
    monto = serializers.IntegerField(min_value=1000)
    metodo_pago = serializers.ChoiceField(choices=['metrepay', 'tigo_money'])
    telefono = serializers.CharField(max_length=20, required=False)
    
    def validate_monto(self, value):
        """Validar que el monto sea múltiplo de 1000"""
        if value % 1000 != 0:
            raise serializers.ValidationError(
                "El monto debe ser múltiplo de 1.000 Guaraníes"
            )
        if value > 1000000:
            raise serializers.ValidationError(
                "El monto máximo por recarga es 1.000.000 Guaraníes"
            )
        return value
    
    def validate(self, data):
        """Validar datos según método de pago"""
        metodo = data.get('metodo_pago')
        
        if metodo == 'tigo_money':
            if not data.get('telefono'):
                raise serializers.ValidationError({
                    'telefono': 'El teléfono es requerido para Tigo Money'
                })
        
        return data
