from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from ..models import Cliente
from ..permissions import IsAdministradorOrInterno, RoleScopePermission, scope_queryset
from ..rbac_contracts import Resources
from ..serializers import ClienteSerializer


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.select_related("usuario").all()
    serializer_class = ClienteSerializer
    permission_classes = [RoleScopePermission]
    rbac_resource = Resources.USER
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["estado"]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [RoleScopePermission(), IsAdministradorOrInterno()]
        return [RoleScopePermission()]

    def get_queryset(self):
        queryset = super().get_queryset()
        scope = getattr(self.request, "_eft_scope", "OWN")
        return scope_queryset(queryset, self.request.user, scope)
