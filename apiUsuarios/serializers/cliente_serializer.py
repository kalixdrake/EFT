from rest_framework import serializers

from ..models import Cliente


class ClienteSerializer(serializers.ModelSerializer):
    usuario_username = serializers.CharField(source="usuario.username", read_only=True)
    usuario_nombre = serializers.CharField(source="usuario.get_full_name", read_only=True)

    class Meta:
        model = Cliente
        fields = [
            "id",
            "usuario",
            "usuario_username",
            "usuario_nombre",
            "rif",
            "nombre_comercial",
            "fecha_afiliacion",
            "estado",
        ]
        read_only_fields = ["id", "fecha_afiliacion"]
