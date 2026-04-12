import calendar
from datetime import datetime, timedelta
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from apiTransacciones.models.transaccion_model import Transaccion


class TransaccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaccion
        fields = '__all__'

    def validate(self, data):
        instance = getattr(self, 'instance', None)
        if instance is None:
            # ----- CREACIÓN -----
            fecha_ejecucion = data.get('fecha_ejecucion')
            categoria = data.get('categoria')
            cuenta = data.get('cuenta')
            monto = data.get('monto')

            if isinstance(fecha_ejecucion, str):
                fecha_ejecucion = datetime.strptime(fecha_ejecucion, "%Y-%m-%d")

            if fecha_ejecucion:
                if fecha_ejecucion > timezone.now():
                    raise serializers.ValidationError({
                        'fecha_ejecucion': 'La fecha de ejecución no puede ser mayor que la fecha actual. '
                                           'Para programar transacciones use los endpoints de apiProgramacion.'
                    })
                if getattr(categoria, 'egreso', False) and cuenta and monto:
                    if cuenta.saldo < monto:
                        raise serializers.ValidationError({'monto': 'Saldo insuficiente en la cuenta.'})
            else:
                raise serializers.ValidationError({'fecha_ejecucion': 'No se puede crear una transacción sin fecha de ejecución.'})
        else:
            # ----- ACTUALIZACIÓN -----
            old_cuenta = instance.cuenta
            old_monto = instance.monto
            old_categoria = instance.categoria
            old_egreso = old_categoria.egreso

            new_cuenta = data.get('cuenta', old_cuenta)
            new_monto = data.get('monto', old_monto)
            new_categoria = data.get('categoria', old_categoria)
            new_egreso = new_categoria.egreso

            fecha_ejecucion = data.get('fecha_ejecucion', instance.fecha_ejecucion)
            if fecha_ejecucion is None:
                raise serializers.ValidationError({'fecha_ejecucion': 'No se puede tener una transacción sin fecha de ejecución.'})
            if isinstance(fecha_ejecucion, str):
                fecha_ejecucion = datetime.strptime(fecha_ejecucion, "%Y-%m-%d")

            # Si la transacción fue generada por una programación, no se permite cambiar la fecha
            if instance.programacion:
                if fecha_ejecucion != instance.fecha_ejecucion:
                    raise serializers.ValidationError({
                        'fecha_ejecucion': 'No se puede cambiar la fecha de una transacción programada.'
                    })
            else:
                if fecha_ejecucion > timezone.now():
                    raise serializers.ValidationError({
                        'fecha_ejecucion': 'La fecha de ejecución no puede ser mayor que la fecha actual. '
                                           'Para programar transacciones use los endpoints de apiProgramacion.'
                    })

            # --- Validación de saldos ---
            # Efecto original (lo que ya está aplicado en la cuenta)
            old_effect = -old_monto if old_egreso else old_monto
            # Saldo de la cuenta original después de revertir el efecto
            old_account_new_balance = old_cuenta.saldo - old_effect
            if old_account_new_balance < 0:
                raise serializers.ValidationError({
                    'cuenta': 'La reversión de la transacción original dejaría la cuenta con saldo negativo.'
                })

            # Efecto nuevo (lo que se aplicará después de la actualización)
            new_effect = -new_monto if new_egreso else new_monto
            new_account_final_balance = new_cuenta.saldo + new_effect
            if new_egreso and new_account_final_balance < 0:
                raise serializers.ValidationError({'monto': 'Saldo insuficiente en la cuenta destino.'})

        return data

    def create(self, validated_data):
        monto = validated_data.get('monto')
        cuenta = validated_data.get('cuenta')
        categoria = validated_data.get('categoria')

        tx = super().create(validated_data)

        if validated_data.get('fecha_ejecucion'):
            if getattr(categoria, 'egreso', False):
                cuenta.saldo -= monto
            else:
                cuenta.saldo += monto
            cuenta.save()

        return tx

    def update(self, instance, validated_data):
        with transaction.atomic():
            old_cuenta = instance.cuenta
            old_monto = instance.monto
            old_categoria = instance.categoria
            old_egreso = old_categoria.egreso

            new_cuenta = validated_data.get('cuenta', old_cuenta)
            new_monto = validated_data.get('monto', old_monto)
            new_categoria = validated_data.get('categoria', old_categoria)
            new_egreso = new_categoria.egreso

            # 1. Revertir el efecto de la transacción antigua
            if old_egreso:
                old_cuenta.saldo += old_monto
            else:
                old_cuenta.saldo -= old_monto
            old_cuenta.save()

            # 2. Actualizar los campos de la transacción
            instance = super().update(instance, validated_data)

            # 3. Aplicar el nuevo efecto sobre la cuenta destino (puede ser la misma o distinta)
            if new_egreso:
                new_cuenta.saldo -= new_monto
            else:
                new_cuenta.saldo += new_monto
            new_cuenta.save()

            return instance