from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apiUsuarios.permissions import RoleScopePermission, IsAdministradorOrInterno, scope_queryset
from apiUsuarios.rbac_contracts import Resources, Actions

from ..models import Impuesto
from ..serializers import ImpuestoSerializer


class ImpuestoViewSet(viewsets.ModelViewSet):
    queryset = Impuesto.objects.all()
    serializer_class = ImpuestoSerializer
    permission_classes = [RoleScopePermission]
    rbac_resource = Resources.IMPUESTO
    rbac_action_map = {}
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["tipo_impuesto", "tipo_calculo", "activo"]
    search_fields = ["nombre", "codigo"]
    ordering_fields = ["nombre", "fecha_creacion"]
    ordering = ["nombre"]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [RoleScopePermission(), IsAdministradorOrInterno()]
        return [RoleScopePermission()]

    def get_queryset(self):
        queryset = super().get_queryset()
        scope = getattr(self.request, "_eft_scope", "OWN")
        return scope_queryset(queryset, self.request.user, scope)

