from rest_framework import serializers
from ..models import Nomina


class NominaSerializer(serializers.ModelSerializer):
    """Serializer para Nóminas"""
    
    empleado_nombre = serializers.CharField(source='empleado.get_full_name', read_only=True)
    aprobado_por_nombre = serializers.CharField(source='aprobado_por.get_full_name', read_only=True, allow_null=True)
    salario_neto = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    esta_vencido = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Nomina
        fields = [
            'id', 'empleado', 'empleado_nombre', 'salario_base', 'periodicidad',
            'bonos', 'deducciones', 'salario_neto', 'periodo_inicio', 'periodo_fin',
            'fecha_pago_programada', 'fecha_pago_efectiva', 'estado',
            'notas', 'aprobado_por', 'aprobado_por_nombre', 'esta_vencido',
            'fecha_creacion'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'aprobado_por']


class NominaCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear nóminas"""
    
    class Meta:
        model = Nomina
        fields = [
            'empleado', 'salario_base', 'periodicidad', 'bonos', 'deducciones',
            'periodo_inicio', 'periodo_fin', 'fecha_pago_programada', 'notas'
        ]
    
    def validate_empleado(self, value):
        if not hasattr(value, 'empleado'):
            raise serializers.ValidationError("Solo se pueden crear nóminas para usuarios con entidad Empleado.")
        return value
    
    def validate(self, attrs):
        """Validar que las fechas sean coherentes"""
        if attrs['periodo_inicio'] >= attrs['periodo_fin']:
            raise serializers.ValidationError({
                'periodo_fin': 'La fecha de fin debe ser posterior a la fecha de inicio'
            })
        
        if attrs['fecha_pago_programada'] < attrs['periodo_fin']:
            raise serializers.ValidationError({
                'fecha_pago_programada': 'La fecha de pago debe ser igual o posterior al fin del periodo'
            })
        
        return attrs
