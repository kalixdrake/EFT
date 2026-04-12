from rest_framework import serializers

from ..models import Empleado


class EmpleadoSerializer(serializers.ModelSerializer):
    usuario_username = serializers.CharField(source="usuario.username", read_only=True)

    class Meta:
        model = Empleado
        fields = [
            "id",
            "usuario",
            "usuario_username",
            "numero_empleado",
            "departamento",
            "fecha_contratacion",
            "salario_base",
            "estado",
        ]
        read_only_fields = ["id", "fecha_contratacion"]
