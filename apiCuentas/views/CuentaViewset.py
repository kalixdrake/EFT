from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from apiCuentas.models.cuenta_model import Cuenta
from apiCuentas.serializers.cuenta_serializer import CuentaSerializer
from apiCuentas.filters.cuenta_filter import CuentaFilter
from apiUsuarios.permissions import RoleScopePermission, scope_queryset
from apiUsuarios.rbac_contracts import Resources

class CuentaViewSet(viewsets.ModelViewSet):
    queryset = Cuenta.objects.all()
    serializer_class = CuentaSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CuentaFilter
    permission_classes = [RoleScopePermission]
    rbac_resource = Resources.CUENTA

    def get_queryset(self):
        queryset = super().get_queryset()
        scope = getattr(self.request, "_eft_scope", "OWN")
        return scope_queryset(queryset, self.request.user, scope)
