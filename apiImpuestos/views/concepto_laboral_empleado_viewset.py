from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from apiUsuarios.permissions import RoleScopePermission, IsAdministradorOrInterno, scope_queryset
from apiUsuarios.rbac_contracts import Resources

from ..models import ConceptoLaboralEmpleado, SnapshotImpuestoTransaccional
from ..serializers import ConceptoLaboralEmpleadoSerializer
from ..services import calcular_impuestos_y_snapshots


class ConceptoLaboralEmpleadoViewSet(viewsets.ModelViewSet):
    queryset = ConceptoLaboralEmpleado.objects.select_related("empleado", "empleado__usuario").all()
    serializer_class = ConceptoLaboralEmpleadoSerializer
    permission_classes = [RoleScopePermission]
    rbac_resource = Resources.IMPUESTO
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["empleado", "fecha"]
    ordering_fields = ["fecha_creacion", "monto_base", "monto_total"]
    ordering = ["-fecha_creacion", "id"]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [RoleScopePermission(), IsAdministradorOrInterno()]
        return [RoleScopePermission()]

    def get_queryset(self):
        queryset = super().get_queryset()
        scope = getattr(self.request, "_eft_scope", "OWN")
        return scope_queryset(queryset, self.request.user, scope)

    def perform_create(self, serializer):
        concepto = serializer.save()
        SnapshotImpuestoTransaccional.objects.filter(
            origen="EMPLEADO_CONCEPTO",
            origen_id=concepto.id,
        ).delete()
        monto_impuesto = calcular_impuestos_y_snapshots(
            origen="EMPLEADO_CONCEPTO",
            origen_id=concepto.id,
            tipo_sujeto="EMPLEADO",
            subtotal=concepto.monto_base,
            empleado=concepto.empleado,
            monto_explicito=concepto.monto_base,
        )
        concepto.monto_impuesto = monto_impuesto
        concepto.monto_total = concepto.monto_base + monto_impuesto
        concepto.save(update_fields=["monto_impuesto", "monto_total"])

    def perform_update(self, serializer):
        concepto = serializer.save()
        SnapshotImpuestoTransaccional.objects.filter(
            origen="EMPLEADO_CONCEPTO",
            origen_id=concepto.id,
        ).delete()
        monto_impuesto = calcular_impuestos_y_snapshots(
            origen="EMPLEADO_CONCEPTO",
            origen_id=concepto.id,
            tipo_sujeto="EMPLEADO",
            subtotal=concepto.monto_base,
            empleado=concepto.empleado,
            monto_explicito=concepto.monto_base,
        )
        concepto.monto_impuesto = monto_impuesto
        concepto.monto_total = concepto.monto_base + monto_impuesto
        concepto.save(update_fields=["monto_impuesto", "monto_total"])

