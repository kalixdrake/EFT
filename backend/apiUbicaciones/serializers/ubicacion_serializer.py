from django_bolt.serializers import Serializer
from typing import Optional


class UbicacionCreateSerializer(Serializer):
    municipio_id: str
    name: str
    phone: str
    street: str
    # These Optional fields allow zero-cost validation where Envia API can fill them later
    postalCode: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class UbicacionSerializer(Serializer):
    id: int
    usuario_id: int
    municipio_id: str
    name: str
    phone: str
    street: str
    city: str
    state: str
    country: str
    postalCode: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]