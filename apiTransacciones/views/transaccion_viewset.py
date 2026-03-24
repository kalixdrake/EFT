from rest_framework import viewsets
from apiTransacciones.models.transaccion_model import Transaccion, TipoTransaccion, CategoriaTransaccion
from apiTransacciones.serializers.transaccion_serializer import TransaccionSerializer, TipoTransaccionSerializer, CategoriaTransaccionSerializer

class TipoTransaccionViewSet(viewsets.ModelViewSet):
    queryset = TipoTransaccion.objects.all()
    serializer_class = TipoTransaccionSerializer

class CategoriaTransaccionViewSet(viewsets.ModelViewSet):
    queryset = CategoriaTransaccion.objects.all()
    serializer_class = CategoriaTransaccionSerializer

class TransaccionViewSet(viewsets.ModelViewSet):
    queryset = Transaccion.objects.all()
    serializer_class = TransaccionSerializer