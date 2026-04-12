from rest_framework import serializers

from ..models import SnapshotImpuestoTransaccional


class SnapshotImpuestoTransaccionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = SnapshotImpuestoTransaccional
        fields = "__all__"
        read_only_fields = ["id", "fecha_creacion"]

