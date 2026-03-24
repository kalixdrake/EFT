from rest_framework import serializers
from apiPresupuestos.models.presupuesto_model import TransaccionProgramada

class TransaccionProgramadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransaccionProgramada
        fields = '__all__'
        read_only_fields = ('estado', 'transaccion_aplicada', 'fecha_creacion')

