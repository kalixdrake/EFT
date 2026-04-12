from rest_framework import serializers

from ..models import AsignacionImpuesto


class AsignacionImpuestoSerializer(serializers.ModelSerializer):
    impuesto = serializers.PrimaryKeyRelatedField(source="regla.impuesto", read_only=True)

    class Meta:
        model = AsignacionImpuesto
        fields = [
            "id",
            "regla",
            "impuesto",
            "ambito",
            "producto",
            "empleado",
            "activo",
            "prioridad_local",
            "fecha_creacion",
            "fecha_actualizacion",
        ]
        read_only_fields = ["id", "fecha_creacion", "fecha_actualizacion"]

