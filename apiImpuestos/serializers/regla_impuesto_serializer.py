from rest_framework import serializers

from ..models import ReglaImpuesto


class ReglaImpuestoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReglaImpuesto
        fields = "__all__"
        read_only_fields = ["id", "fecha_creacion", "fecha_actualizacion"]

