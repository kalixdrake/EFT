from rest_framework import serializers
from datetime import date
from django.utils import timezone
from apiCuentas.models.cuenta_model import Cuenta
from apiTransacciones.models.transaccion_model import Transaccion
from django.db import transaction

class TransferenciaSerializer(serializers.Serializer):
    cuenta_origen = serializers.PrimaryKeyRelatedField(queryset=Cuenta.objects.all())
    cuenta_destino = serializers.PrimaryKeyRelatedField(queryset=Cuenta.objects.all())
    monto = serializers.DecimalField(max_digits=32, decimal_places=2)
    descripcion = serializers.CharField(max_length=255)
    fecha_ejecucion = serializers.DateTimeField(required=False, allow_null=True)

    class Meta:
        model = Transaccion
        fields = [
            'cuenta_origen',
            'cuenta_destino',
            'monto',
            'descripcion',
            'fecha_ejecucion'
        ]

    def validate(self, data):
        if data['cuenta_origen'] == data['cuenta_destino']:
            raise serializers.ValidationError("La cuenta origen y destino no pueden ser la misma.")
        
        fecha_ejecucion = data.get('fecha_ejecucion')
        if fecha_ejecucion and fecha_ejecucion > timezone.now(): # Validation for future transactions
            raise serializers.ValidationError({'fecha_ejecucion':'La fecha de ejecucion no puede ser mayor que la fecha actual, para programar transacciones hacer uso de los endpoints de apiProgramacion'})
        
        # Balance validation (only if it's not a future transaction where it hasn't executed yet)
        if data.get('fecha_ejecucion'):
            if data['cuenta_origen'].saldo < data['monto']:
                raise serializers.ValidationError({"monto": "Saldo insuficiente en cuenta origen."})
        
        return data

    @transaction.atomic
    def create(self, validated_data):
        cuenta_origen = validated_data['cuenta_origen']
        cuenta_destino = validated_data['cuenta_destino']
        monto = validated_data['monto']
        descripcion = validated_data['descripcion']
        
        # transferencia_ing = 10, transferencia_egr = 9
        
        # Egreso transaccion
        tx_egreso = Transaccion.objects.create(
            cuenta=cuenta_origen,
            categoria_id=9,
            monto=monto,
            descripcion=descripcion,
            fecha_ejecucion=validated_data.get('fecha_ejecucion')
        )
        # Ingreso transaccion
        tx_ingreso = Transaccion.objects.create(
            cuenta=cuenta_destino,
            categoria_id=10,
            monto=monto, # could be positive everywhere, model depends on `egreso` in categoria
            descripcion=descripcion,
            fecha_ejecucion=validated_data.get('fecha_ejecucion')
        )
        
        # If it's modifying immediately:
        if validated_data.get('fecha_ejecucion'):
            cuenta_origen.saldo -= monto
            cuenta_origen.save()
            
            cuenta_destino.saldo += monto
            cuenta_destino.save()

        return tx_egreso # return one representation or arbitrary dict

    