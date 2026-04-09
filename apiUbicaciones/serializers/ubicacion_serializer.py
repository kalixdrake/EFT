from rest_framework import serializers

from ..models import (
    Ciudad,
    ClienteUbicacion,
    Departamento,
    EmpleadoUbicacion,
    Pais,
    SocioUbicacion,
    Ubicacion,
)


class PaisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pais
        fields = ["id", "nombre", "codigo_iso", "activo"]


class DepartamentoSerializer(serializers.ModelSerializer):
    pais_nombre = serializers.CharField(source="pais.nombre", read_only=True)

    class Meta:
        model = Departamento
        fields = ["id", "pais", "pais_nombre", "nombre", "codigo", "activo"]


class CiudadSerializer(serializers.ModelSerializer):
    departamento_nombre = serializers.CharField(source="departamento.nombre", read_only=True)
    pais_id = serializers.IntegerField(source="departamento.pais.id", read_only=True)
    pais_nombre = serializers.CharField(source="departamento.pais.nombre", read_only=True)

    class Meta:
        model = Ciudad
        fields = [
            "id",
            "departamento",
            "departamento_nombre",
            "pais_id",
            "pais_nombre",
            "nombre",
            "codigo_postal",
            "activo",
        ]


class UbicacionSerializer(serializers.ModelSerializer):
    ciudad_nombre = serializers.CharField(source="ciudad.nombre", read_only=True)
    departamento_id = serializers.IntegerField(source="ciudad.departamento.id", read_only=True)
    departamento_nombre = serializers.CharField(source="ciudad.departamento.nombre", read_only=True)
    pais_id = serializers.IntegerField(source="ciudad.departamento.pais.id", read_only=True)
    pais_nombre = serializers.CharField(source="ciudad.departamento.pais.nombre", read_only=True)

    class Meta:
        model = Ubicacion
        fields = [
            "id",
            "ciudad",
            "ciudad_nombre",
            "departamento_id",
            "departamento_nombre",
            "pais_id",
            "pais_nombre",
            "nombre",
            "direccion",
            "referencia",
            "latitud",
            "longitud",
            "tipo",
            "activo",
        ]


class ClienteUbicacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClienteUbicacion
        fields = ["id", "cliente", "ubicacion", "es_principal", "activo", "fecha_creacion"]
        read_only_fields = ["id", "fecha_creacion"]


class SocioUbicacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocioUbicacion
        fields = ["id", "socio", "ubicacion", "es_principal", "activo", "fecha_creacion"]
        read_only_fields = ["id", "fecha_creacion"]


class EmpleadoUbicacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmpleadoUbicacion
        fields = ["id", "empleado", "ubicacion", "es_principal", "activo", "fecha_creacion"]
        read_only_fields = ["id", "fecha_creacion"]
