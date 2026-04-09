from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from apiUsuarios.permissions import RoleScopePermission, IsAdministradorOrInterno, scope_queryset
from apiUsuarios.rbac_contracts import Resources

from ..models import ReglaImpuesto
from ..serializers import ReglaImpuestoSerializer


class ReglaImpuestoViewSet(viewsets.ModelViewSet):
    queryset = ReglaImpuesto.objects.select_related("impuesto").all()
    serializer_class = ReglaImpuestoSerializer
    permission_classes = [RoleScopePermission]
    rbac_resource = Resources.IMPUESTO
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["tipo_sujeto", "base_imponible", "activo", "impuesto"]
    ordering_fields = ["prioridad", "fecha_inicio", "fecha_creacion"]
    ordering = ["prioridad", "id"]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [RoleScopePermission(), IsAdministradorOrInterno()]
        return [RoleScopePermission()]

    def get_queryset(self):
        queryset = super().get_queryset()
        scope = getattr(self.request, "_eft_scope", "OWN")
        return scope_queryset(queryset, self.request.user, scope)

