from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from ..models import Empleado
from ..permissions import IsAdministradorOrInterno, RoleScopePermission, scope_queryset
from ..rbac_contracts import Resources
from ..serializers import EmpleadoSerializer


class EmpleadoViewSet(viewsets.ModelViewSet):
    queryset = Empleado.objects.select_related("usuario").all()
    serializer_class = EmpleadoSerializer
    permission_classes = [RoleScopePermission]
    rbac_resource = Resources.USER
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["estado", "departamento"]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [RoleScopePermission(), IsAdministradorOrInterno()]
        return [RoleScopePermission()]

    def get_queryset(self):
        queryset = super().get_queryset()
        scope = getattr(self.request, "_eft_scope", "OWN")
        return scope_queryset(queryset, self.request.user, scope)
