from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from apiUsuarios.permissions import IsAdministradorOrInterno, RoleScopePermission
from apiUsuarios.rbac_contracts import Resources

from ..models import TipoDocumento
from ..serializers import TipoDocumentoSerializer


class TipoDocumentoViewSet(viewsets.ModelViewSet):
    queryset = TipoDocumento.objects.all()
    serializer_class = TipoDocumentoSerializer
    permission_classes = [RoleScopePermission]
    rbac_resource = Resources.DOCUMENTO
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["activo", "propietario_permitido", "requiere_vencimiento"]
    search_fields = ["codigo", "nombre", "descripcion"]
    ordering_fields = ["codigo", "nombre", "fecha_creacion"]
    ordering = ["nombre"]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [RoleScopePermission(), IsAdministradorOrInterno()]
        return [RoleScopePermission()]

    def get_queryset(self):
        return super().get_queryset().filter(activo=True)
