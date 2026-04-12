from rest_framework import serializers
from apiCuentas.models.cuenta_model import Cuenta

class CuentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuenta
        fields = '__all__'

