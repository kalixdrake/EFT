from rest_framework import serializers

from ..models import VersionDocumento


class VersionDocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = VersionDocumento
        fields = "__all__"
        read_only_fields = ["id", "fecha_creacion"]

