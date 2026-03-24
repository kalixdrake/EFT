from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from apiBancos.models.banco_model import Banco
from apiBancos.serializers.banco_serializer import BancoSerializer
from apiBancos.filters.banco_filter import BancoFilter

class BancoViewSet(viewsets.ModelViewSet):
    queryset = Banco.objects.all()
    serializer_class = BancoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = BancoFilter
