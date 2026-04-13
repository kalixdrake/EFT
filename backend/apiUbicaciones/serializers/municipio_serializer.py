from django_bolt.serializers import Serializer


class MunicipioSerializer(Serializer):
    codigo_dane: str
    nombre: str
    departamento_id: str