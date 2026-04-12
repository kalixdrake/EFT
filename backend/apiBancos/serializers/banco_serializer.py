from rest_framework import serializers
from apiBancos.models.banco_model import Banco

class BancoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banco
        fields = '__all__'