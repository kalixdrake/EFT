from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from ..models import Cliente
from ..permissions import RoleScopePermission
from ..rbac_contracts import Resources
from ..serializers import ClienteSerializer


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.select_related("usuario").all()
    serializer_class = ClienteSerializer
    permission_classes = [RoleScopePermission]
    rbac_resource = Resources.USER
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["estado"]
