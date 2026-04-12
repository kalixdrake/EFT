from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from apiUsuarios.permissions import RoleScopePermission, IsAdministradorOrInterno, scope_queryset
from apiUsuarios.rbac_contracts import Resources

from ..models import AsignacionImpuesto
from ..serializers import AsignacionImpuestoSerializer


class AsignacionImpuestoViewSet(viewsets.ModelViewSet):
    queryset = AsignacionImpuesto.objects.select_related("regla", "regla__impuesto", "producto", "empleado").all()
    serializer_class = AsignacionImpuestoSerializer
    permission_classes = [RoleScopePermission]
    rbac_resource = Resources.IMPUESTO
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["ambito", "activo", "regla", "regla__impuesto", "producto", "empleado"]
    ordering_fields = ["prioridad_local", "fecha_creacion"]
    ordering = ["prioridad_local", "id"]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [RoleScopePermission(), IsAdministradorOrInterno()]
        return [RoleScopePermission()]

    def get_queryset(self):
        queryset = super().get_queryset()
        scope = getattr(self.request, "_eft_scope", "OWN")
        return scope_queryset(queryset, self.request.user, scope)

