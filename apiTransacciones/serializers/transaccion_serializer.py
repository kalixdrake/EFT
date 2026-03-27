import calendar
from datetime import datetime, timedelta
from django.utils import timezone
from rest_framework import serializers
from django.utils import timezone
from apiTransacciones.models.transaccion_model import Transaccion


class TransaccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaccion
        fields = '__all__'

    def validate(self, data):
        fecha_ejecucion = data.get('fecha_ejecucion')
        categoria = data.get('categoria')
        cuenta = data.get('cuenta')
        monto = data.get('monto')

        if isinstance(fecha_ejecucion, str):
            fecha_ejecucion = datetime.strptime(fecha_ejecucion, "%Y-%m-%d")

        if fecha_ejecucion:
            if fecha_ejecucion > timezone.now():
                raise serializers.ValidationError({'fecha_ejecucion':'La fecha de ejecucion no puede ser mayor que la fecha actual, para programar transacciones hacer uso de los endpoints de apiProgramacion'})
            
            if getattr(categoria, 'egreso', False) and cuenta and monto:
                if cuenta.saldo < monto:
                    raise serializers.ValidationError({'monto': 'Saldo insuficiente en la cuenta.'})
        else:
            raise serializers.ValidationError({'fecha_ejecucion':'No se puede crear una transaccion sin fecha de ejecucion'})
        
        return data

    def create(self, validated_data):
        monto = validated_data.get('monto')
        cuenta = validated_data.get('cuenta')
        categoria = validated_data.get('categoria')
        
        tx = super().create(validated_data)
        
        if not validated_data.get('mes') and validated_data.get('fecha_ejecucion'):
            if getattr(categoria, 'egreso', False):
                cuenta.saldo -= monto
            else:
                cuenta.saldo += monto
            cuenta.save()
            
        return tx

