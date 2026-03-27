from datetime import datetime, timedelta
from django.utils import timezone
from rest_framework import serializers
from apiTransacciones.models.programacion_model import ProgramacionTransaccion


class ProgramacionTransaccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramacionTransaccion
        fields = '__all__'
    
    def validate(self, data):
        """
        Validate programmed transaction data
        """
        fecha_programada = data.get('fecha_programada')
        categoria = data.get('categoria')
        cuenta = data.get('cuenta')
        monto = data.get('monto')
        frecuencia = data.get('frecuencia', 'UNICA')
        fecha_fin_repeticion = data.get('fecha_fin_repeticion')
        
        # Convert string dates if necessary
        if isinstance(fecha_programada, str):
            try:
                fecha_programada = datetime.fromisoformat(fecha_programada.replace('Z', '+00:00'))
                data['fecha_programada'] = fecha_programada
            except ValueError:
                raise serializers.ValidationError({'fecha_programada': 'Formato de fecha inválido'})
        
        # Validate that fecha_programada is in the future
        if fecha_programada and fecha_programada <= timezone.now():
            raise serializers.ValidationError({'fecha_programada': 'La fecha programada debe ser en el futuro'})
        
        # Validate monto
        if monto and monto <= 0:
            raise serializers.ValidationError({'monto': 'El monto debe ser mayor a cero'})
        
        # Validate that categoria and cuenta exist
        if not categoria:
            raise serializers.ValidationError({'categoria': 'La categoría es requerida'})
        if not cuenta:
            raise serializers.ValidationError({'cuenta': 'La cuenta es requerida'})
        
        # Validate for recurrent transactions
        if frecuencia != 'UNICA':
            if not fecha_fin_repeticion:
                raise serializers.ValidationError({'fecha_fin_repeticion': 'La fecha de fin de repetición es requerida para transacciones recurrentes'})
            
            if isinstance(fecha_fin_repeticion, str):
                try:
                    fecha_fin_repeticion = datetime.fromisoformat(fecha_fin_repeticion.replace('Z', '+00:00'))
                    data['fecha_fin_repeticion'] = fecha_fin_repeticion
                except ValueError:
                    raise serializers.ValidationError({'fecha_fin_repeticion': 'Formato de fecha inválido'})
            
            if fecha_fin_repeticion <= fecha_programada:
                raise serializers.ValidationError({'fecha_fin_repeticion': 'La fecha de fin debe ser posterior a la fecha programada'})
        
        return data


class ProgramacionTransaccionListSerializer(serializers.ModelSerializer):
    """Serializer for list view with minimal fields"""
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    cuenta_nombre = serializers.CharField(source='cuenta.nombre', read_only=True)
    
    class Meta:
        model = ProgramacionTransaccion
        fields = [
            'id', 'monto', 'descripcion', 'fecha_programada', 
            'estado', 'frecuencia', 'categoria_nombre', 'cuenta_nombre',
            'activa'
        ]


class ProgramacionTransaccionDetailSerializer(serializers.ModelSerializer):
    """Serializer for detail view with all fields"""
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    cuenta_nombre = serializers.CharField(source='cuenta.nombre', read_only=True)
    
    class Meta:
        model = ProgramacionTransaccion
        fields = '__all__'
