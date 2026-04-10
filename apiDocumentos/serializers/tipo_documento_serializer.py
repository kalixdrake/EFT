from rest_framework import serializers

from ..models import TipoDocumento


class TipoDocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDocumento
        fields = "__all__"
        read_only_fields = ["id", "fecha_creacion", "fecha_actualizacion"]

