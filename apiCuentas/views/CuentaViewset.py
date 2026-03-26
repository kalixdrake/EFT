from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from apiCuentas.models.cuenta_model import Cuenta
from apiCuentas.serializers.cuenta_serializer import CuentaSerializer
from apiCuentas.filters.cuenta_filter import CuentaFilter

class CuentaViewSet(viewsets.ModelViewSet):
    queryset = Cuenta.objects.all()
    serializer_class = CuentaSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CuentaFilter
