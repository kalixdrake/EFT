from rest_framework import serializers

from ..models import (
    CategoriaActivo,
    ActivoFijo,
    DepreciacionActivo,
    MantenimientoActivo,
    MovimientoActivo,
)


class CategoriaActivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaActivo
        fields = "__all__"
        read_only_fields = ["id", "fecha_creacion", "fecha_actualizacion"]


class ActivoFijoSerializer(serializers.ModelSerializer):
    valor_depreciable = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    depreciacion_mensual_estimado = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = ActivoFijo
        fields = "__all__"
        read_only_fields = ["id", "fecha_creacion", "fecha_actualizacion", "valor_depreciable", "depreciacion_mensual_estimado"]


class DepreciacionActivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepreciacionActivo
        fields = "__all__"
        read_only_fields = ["id", "fecha_creacion"]


class MantenimientoActivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MantenimientoActivo
        fields = "__all__"
        read_only_fields = ["id", "alerta_vencida", "fecha_creacion", "fecha_actualizacion"]


class MovimientoActivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovimientoActivo
        fields = "__all__"
        read_only_fields = ["id", "responsable_anterior", "ubicacion_anterior", "fecha_movimiento"]

