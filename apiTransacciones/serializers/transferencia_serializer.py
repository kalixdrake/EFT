from rest_framework import serializers
from datetime import date
from django.utils import timezone
from django.db import transaction
from apiCuentas.models.cuenta_model import Cuenta
from apiTransacciones.models.transaccion_model import Transaccion
from apiTransacciones.models.categorias_model import Categoria
from apiTransacciones.serializers.transaccion_serializer import TransaccionSerializer


class TransferenciaSerializer(serializers.Serializer):
    cuenta_origen = serializers.PrimaryKeyRelatedField(queryset=Cuenta.objects.all())
    cuenta_destino = serializers.PrimaryKeyRelatedField(queryset=Cuenta.objects.all())
    monto = serializers.DecimalField(max_digits=32, decimal_places=2)
    descripcion = serializers.CharField(max_length=255)
    fecha_ejecucion = serializers.DateTimeField(required=False, allow_null=True)

    def validate(self, data):
        if data['cuenta_origen'] == data['cuenta_destino']:
            raise serializers.ValidationError("La cuenta origen y destino no pueden ser la misma.")

        fecha_ejecucion = data.get('fecha_ejecucion')
        # Validar fecha futura
        if fecha_ejecucion and fecha_ejecucion > timezone.now():
            raise serializers.ValidationError({
                'fecha_ejecucion': 'La fecha de ejecución no puede ser mayor que la fecha actual. '
                                   'Para programar transacciones use los endpoints de apiProgramacion.'
            })

        # Validar saldo en cuenta origen para transacciones inmediatas (fecha nula o <= ahora)
        if fecha_ejecucion is None or fecha_ejecucion <= timezone.now():
            if data['cuenta_origen'].saldo < data['monto']:
                raise serializers.ValidationError({"monto": "Saldo insuficiente en cuenta origen."})

        return data

    @transaction.atomic
    def create(self, validated_data):
        cuenta_origen = validated_data['cuenta_origen']
        cuenta_destino = validated_data['cuenta_destino']
        monto = validated_data['monto']
        descripcion = validated_data['descripcion']
        fecha_ejecucion = validated_data.get('fecha_ejecucion')

        # Si no se especificó fecha, se usa la actual (transacción inmediata)
        if fecha_ejecucion is None:
            fecha_ejecucion = timezone.now()

        # Obtener categorías fijas: egreso (9) e ingreso (10)
        try:
            categoria_egreso = Categoria.objects.get(id=9)
            categoria_ingreso = Categoria.objects.get(id=10)
        except Categoria.DoesNotExist:
            raise serializers.ValidationError("Categorías de transferencia no encontradas.")

        # Datos para transacción de egreso (cuenta origen)
        data_egreso = {
            'cuenta': cuenta_origen.id,
            'categoria': categoria_egreso.id,
            'monto': monto,
            'descripcion': descripcion,
            'fecha_ejecucion': fecha_ejecucion,
        }
        # Datos para transacción de ingreso (cuenta destino)
        data_ingreso = {
            'cuenta': cuenta_destino.id,
            'categoria': categoria_ingreso.id,
            'monto': monto,
            'descripcion': descripcion,
            'fecha_ejecucion': fecha_ejecucion,
        }

        # Crear serializers y guardar
        serializer_egreso = TransaccionSerializer(data=data_egreso)
        serializer_ingreso = TransaccionSerializer(data=data_ingreso)

        # Validar y guardar ambas dentro de la transacción atómica
        if not serializer_egreso.is_valid():
            raise serializers.ValidationError(serializer_egreso.errors)
        if not serializer_ingreso.is_valid():
            raise serializers.ValidationError(serializer_ingreso.errors)

        tx_egreso = serializer_egreso.save()
        tx_ingreso = serializer_ingreso.save()

        # Retornar ambas (aunque la vista no lo usa, es útil para debugging)
        return {
            'egreso': tx_egreso,
            'ingreso': tx_ingreso,
        }