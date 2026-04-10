from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets
from rest_framework.filters import OrderingFilter

from apiUsuarios.permissions import RoleScopePermission, scope_queryset
from apiUsuarios.rbac_contracts import Resources

from ..models import AccesoDocumento
from ..serializers import AccesoDocumentoSerializer


class AccesoDocumentoViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = AccesoDocumento.objects.select_related("documento", "version_documento", "usuario").all()
    serializer_class = AccesoDocumentoSerializer
    permission_classes = [RoleScopePermission]
    rbac_resource = Resources.DOCUMENTO
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["documento", "usuario", "tipo_evento"]
    ordering_fields = ["fecha_evento"]
    ordering = ["-fecha_evento"]

    def get_queryset(self):
        queryset = super().get_queryset()
        scope = getattr(self.request, "_eft_scope", "OWN")
        return scope_queryset(queryset, self.request.user, scope)

