from apiTransacciones.models.categorias_model import Categoria
from apiTransacciones.serializers.categoria_serializer import CategoriaSerializer
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from apiTransacciones.filters.categoria_filter import CategoriaFilter
from apiUsuarios.permissions import RoleScopePermission, scope_queryset
from apiUsuarios.rbac_contracts import Resources

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = CategoriaFilter
    serializer_class = CategoriaSerializer
    permission_classes = [RoleScopePermission]
    rbac_resource = Resources.TRANSACCION

    def get_queryset(self):
        queryset = super().get_queryset()
        scope = getattr(self.request, "_eft_scope", "OWN")
        return scope_queryset(queryset, self.request.user, scope)
