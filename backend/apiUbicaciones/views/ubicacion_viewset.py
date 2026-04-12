from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from apiUsuarios.permissions import IsAdministradorOrInterno, RoleScopePermission, scope_queryset
from apiUsuarios.rbac_contracts import Resources

from ..models import (
    Ciudad,
    ClienteUbicacion,
    Departamento,
    EmpleadoUbicacion,
    Pais,
    SocioUbicacion,
    Ubicacion,
)
from ..serializers import (
    CiudadSerializer,
    ClienteUbicacionSerializer,
    DepartamentoSerializer,
    EmpleadoUbicacionSerializer,
    PaisSerializer,
    SocioUbicacionSerializer,
    UbicacionSerializer,
)


class _BaseUbicacionViewSet(viewsets.ModelViewSet):
    permission_classes = [RoleScopePermission]
    rbac_resource = Resources.PEDIDO
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [RoleScopePermission(), IsAdministradorOrInterno()]
        return [RoleScopePermission()]

    def get_queryset(self):
        queryset = super().get_queryset()
        scope = getattr(self.request, "_eft_scope", "OWN")
        return scope_queryset(queryset, self.request.user, scope)


class PaisViewSet(_BaseUbicacionViewSet):
    queryset = Pais.objects.all()
    serializer_class = PaisSerializer
    search_fields = ["nombre", "codigo_iso"]
    filterset_fields = ["activo"]
    ordering_fields = ["nombre", "codigo_iso"]
    ordering = ["nombre"]


class DepartamentoViewSet(_BaseUbicacionViewSet):
    queryset = Departamento.objects.select_related("pais").all()
    serializer_class = DepartamentoSerializer
    search_fields = ["nombre", "codigo", "pais__nombre"]
    filterset_fields = ["pais", "activo"]
    ordering_fields = ["nombre", "pais__nombre"]
    ordering = ["nombre"]


class CiudadViewSet(_BaseUbicacionViewSet):
    queryset = Ciudad.objects.select_related("departamento", "departamento__pais").all()
    serializer_class = CiudadSerializer
    search_fields = ["nombre", "codigo_postal", "departamento__nombre", "departamento__pais__nombre"]
    filterset_fields = ["departamento", "departamento__pais", "activo"]
    ordering_fields = ["nombre", "departamento__nombre"]
    ordering = ["nombre"]


class UbicacionViewSet(_BaseUbicacionViewSet):
    queryset = Ubicacion.objects.select_related("ciudad", "ciudad__departamento", "ciudad__departamento__pais").all()
    serializer_class = UbicacionSerializer
    search_fields = [
        "nombre",
        "direccion",
        "referencia",
        "ciudad__nombre",
        "ciudad__departamento__nombre",
        "ciudad__departamento__pais__nombre",
    ]
    filterset_fields = ["tipo", "activo", "ciudad", "ciudad__departamento", "ciudad__departamento__pais"]
    ordering_fields = ["nombre", "tipo", "ciudad__nombre"]
    ordering = ["nombre"]


class ClienteUbicacionViewSet(_BaseUbicacionViewSet):
    queryset = ClienteUbicacion.objects.select_related("cliente", "cliente__usuario", "ubicacion").all()
    serializer_class = ClienteUbicacionSerializer
    search_fields = ["cliente__usuario__username", "ubicacion__nombre", "ubicacion__direccion"]
    filterset_fields = ["cliente", "es_principal", "activo", "ubicacion__tipo"]
    ordering_fields = ["fecha_creacion", "cliente__usuario__username"]
    ordering = ["-fecha_creacion"]


class SocioUbicacionViewSet(_BaseUbicacionViewSet):
    queryset = SocioUbicacion.objects.select_related("socio", "socio__usuario", "ubicacion").all()
    serializer_class = SocioUbicacionSerializer
    search_fields = ["socio__usuario__username", "ubicacion__nombre", "ubicacion__direccion"]
    filterset_fields = ["socio", "es_principal", "activo", "ubicacion__tipo"]
    ordering_fields = ["fecha_creacion", "socio__usuario__username"]
    ordering = ["-fecha_creacion"]


class EmpleadoUbicacionViewSet(_BaseUbicacionViewSet):
    queryset = EmpleadoUbicacion.objects.select_related("empleado", "empleado__usuario", "ubicacion").all()
    serializer_class = EmpleadoUbicacionSerializer
    search_fields = ["empleado__usuario__username", "ubicacion__nombre", "ubicacion__direccion"]
    filterset_fields = ["empleado", "es_principal", "activo", "ubicacion__tipo"]
    ordering_fields = ["fecha_creacion", "empleado__usuario__username"]
    ordering = ["-fecha_creacion"]
