from rest_framework import serializers

from ..models import ConceptoLaboralEmpleado


class ConceptoLaboralEmpleadoSerializer(serializers.ModelSerializer):
    empleado_numero = serializers.CharField(source="empleado.numero_empleado", read_only=True)

    class Meta:
        model = ConceptoLaboralEmpleado
        fields = [
            "id",
            "empleado",
            "empleado_numero",
            "descripcion",
            "monto_base",
            "monto_impuesto",
            "monto_total",
            "fecha",
            "fecha_creacion",
            "fecha_actualizacion",
        ]
        read_only_fields = ["id", "monto_impuesto", "monto_total", "fecha", "fecha_creacion", "fecha_actualizacion"]

