from rest_framework import serializers

from ..models import Socio


class SocioSerializer(serializers.ModelSerializer):
    usuario_username = serializers.CharField(source="usuario.username", read_only=True)
    credito_disponible = serializers.SerializerMethodField()

    class Meta:
        model = Socio
        fields = [
            "id",
            "usuario",
            "usuario_username",
            "porcentaje_anticipo",
            "limite_credito",
            "saldo_pendiente",
            "credito_disponible",
            "descuento_especial",
            "fecha_acuerdo",
            "activo",
            "notas_internas",
        ]
        read_only_fields = ["id", "fecha_acuerdo", "credito_disponible"]

    def get_credito_disponible(self, obj):
        return obj.credito_disponible()
