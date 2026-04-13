from django_bolt.serializers import Serializer

class DepartamentoSerializer(Serializer):
    codigo_dane: str
    nombre: str