from rest_framework import serializers

from ..models import Impuesto


class ImpuestoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Impuesto
        fields = "__all__"
        read_only_fields = ["id", "fecha_creacion", "fecha_actualizacion"]

