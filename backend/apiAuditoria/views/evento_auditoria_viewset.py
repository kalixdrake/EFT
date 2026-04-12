from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets
from rest_framework.filters import OrderingFilter

from apiUsuarios.permissions import RoleScopePermission, scope_queryset
from apiUsuarios.rbac_contracts import Resources

from apiAuditoria.models import EventoAuditoria
from apiAuditoria.serializers import EventoAuditoriaSerializer


class EventoAuditoriaViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = EventoAuditoria.objects.select_related("usuario").all()
    serializer_class = EventoAuditoriaSerializer
    permission_classes = [RoleScopePermission]
    rbac_resource = Resources.AUDITORIA
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["recurso", "accion", "resultado", "usuario", "metodo_http", "codigo_estado"]
    ordering_fields = ["fecha_evento", "codigo_estado", "recurso", "accion"]
    ordering = ["-fecha_evento"]

    def get_queryset(self):
        queryset = super().get_queryset()
        scope = getattr(self.request, "_eft_scope", "OWN")
        return scope_queryset(queryset, self.request.user, scope)

