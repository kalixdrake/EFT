from rest_framework import serializers

from ..models import AccesoDocumento


class AccesoDocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccesoDocumento
        fields = "__all__"
        read_only_fields = ["id", "fecha_evento"]

