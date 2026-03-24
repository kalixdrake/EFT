from rest_framework import serializers
from apiTransacciones.models.transaccion_model import Transaccion, TipoTransaccion, CategoriaTransaccion
from apiCuentas.models.cuenta_model import Cuenta

class TipoTransaccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoTransaccion
        fields = '__all__'

class CategoriaTransaccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaTransaccion
        fields = '__all__'

class TransaccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaccion
        fields = '__all__'

    def validate(self, data):
        tipo = data.get('tipo')
        cuenta_origen = data.get('cuenta_origen')
        cuenta_destino = data.get('cuenta_destino')

        if not tipo:
            return data

        # TRANSFERENCIA
        if tipo.id == 3:
            if not cuenta_origen or not cuenta_destino:
                raise serializers.ValidationError("Las transferencias requieren 'cuenta_origen' y 'cuenta_destino'.")

        # RETIRO EN EFECTIVO
        elif tipo.id == 4:
            if not cuenta_origen:
                raise serializers.ValidationError("El retiro en efectivo requiere 'cuenta_origen'.")
            efectivo_cuenta = Cuenta.objects.filter(banco__nombre__icontains='Efectivo').first()
            if not efectivo_cuenta:
                # O si tienen una lógica específica para buscar la cuenta "Efectivo", ajústalo.
                # Asumiremos que el id o el banco es "Efectivo"
                pass
            data['cuenta_destino'] = efectivo_cuenta

        # CONSIGNACION
        elif tipo.id == 5:
            if not cuenta_destino:
                raise serializers.ValidationError("La consignación requiere 'cuenta_destino'.")
            efectivo_cuenta = Cuenta.objects.filter(banco__nombre__icontains='Efectivo').first()
            data['cuenta_origen'] = efectivo_cuenta

        return data

