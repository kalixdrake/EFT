from rest_framework import serializers

from ..models import Documento


class DocumentoSerializer(serializers.ModelSerializer):
    requiere_alerta_vencimiento = serializers.BooleanField(read_only=True)

    class Meta:
        model = Documento
        fields = "__all__"
        read_only_fields = [
            "id",
            "fecha_creacion",
            "fecha_actualizacion",
            "ultima_version",
            "usuario_creador",
            "usuario_actualizador",
            "requiere_alerta_vencimiento",
        ]

