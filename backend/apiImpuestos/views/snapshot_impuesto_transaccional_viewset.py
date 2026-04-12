from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from apiUsuarios.permissions import RoleScopePermission, scope_queryset
from apiUsuarios.rbac_contracts import Resources

from ..models import SnapshotImpuestoTransaccional
from ..serializers import SnapshotImpuestoTransaccionalSerializer


class SnapshotImpuestoTransaccionalViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SnapshotImpuestoTransaccional.objects.select_related("impuesto").all()
    serializer_class = SnapshotImpuestoTransaccionalSerializer
    permission_classes = [RoleScopePermission]
    rbac_resource = Resources.IMPUESTO
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["origen", "origen_id", "codigo_impuesto", "impuesto"]
    ordering_fields = ["fecha_creacion", "prioridad"]
    ordering = ["-fecha_creacion", "id"]

    def get_queryset(self):
        queryset = super().get_queryset()
        scope = getattr(self.request, "_eft_scope", "OWN")
        return scope_queryset(queryset, self.request.user, scope)

