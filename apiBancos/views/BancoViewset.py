from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from apiBancos.models.banco_model import Banco
from apiBancos.serializers.banco_serializer import BancoSerializer
from apiBancos.filters.banco_filter import BancoFilter
from apiUsuarios.permissions import IsAdministradorOrInterno, RoleScopePermission, scope_queryset
from apiUsuarios.rbac_contracts import Resources

class BancoViewSet(viewsets.ModelViewSet):
    queryset = Banco.objects.all()
    serializer_class = BancoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = BancoFilter
    permission_classes = [RoleScopePermission]
    rbac_resource = Resources.BANCO

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [RoleScopePermission(), IsAdministradorOrInterno()]
        return [RoleScopePermission()]

    def get_queryset(self):
        queryset = super().get_queryset()
        scope = getattr(self.request, "_eft_scope", "OWN")
        return scope_queryset(queryset, self.request.user, scope)
