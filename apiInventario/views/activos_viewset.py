from datetime import date
from decimal import Decimal

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter

from apiUsuarios.permissions import RoleScopePermission, IsAdministradorOrInterno, scope_queryset
from apiUsuarios.rbac_contracts import Resources, Actions

from ..models import CategoriaActivo, ActivoFijo, DepreciacionActivo, MantenimientoActivo, MovimientoActivo
from ..serializers import (
    CategoriaActivoSerializer,
    ActivoFijoSerializer,
    DepreciacionActivoSerializer,
    MantenimientoActivoSerializer,
    MovimientoActivoSerializer,
)


class CategoriaActivoViewSet(viewsets.ModelViewSet):
    queryset = CategoriaActivo.objects.all()
    serializer_class = CategoriaActivoSerializer
    permission_classes = [RoleScopePermission]
    rbac_resource = Resources.INVENTARIO
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["activo"]
    search_fields = ["nombre", "descripcion"]
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


class ActivoFijoViewSet(viewsets.ModelViewSet):
    queryset = ActivoFijo.objects.select_related("categoria", "asignado_a_empleado", "asignado_a_ubicacion").all()
    serializer_class = ActivoFijoSerializer
    permission_classes = [RoleScopePermission]
    rbac_resource = Resources.INVENTARIO
    rbac_action_map = {"resumen_activos": Actions.READ}
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["tipo", "estado", "categoria", "asignado_a_empleado", "asignado_a_ubicacion", "activo"]
    search_fields = ["codigo_activo", "nombre", "descripcion"]
    ordering_fields = ["nombre", "valor_compra", "fecha_adquisicion", "fecha_creacion"]
    ordering = ["nombre"]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [RoleScopePermission(), IsAdministradorOrInterno()]
        return [RoleScopePermission()]

    def get_queryset(self):
        queryset = super().get_queryset()
        scope = getattr(self.request, "_eft_scope", "OWN")
        return scope_queryset(queryset, self.request.user, scope)

    @action(detail=False, methods=["get"])
    def resumen_activos(self, request):
        activos = self.get_queryset()
        total = activos.count()
        en_mantenimiento = activos.filter(estado=ActivoFijo.EstadoActivo.EN_MANTENIMIENTO).count()
        asignados = activos.filter(estado=ActivoFijo.EstadoActivo.ASIGNADO).count()
        baja = activos.filter(estado=ActivoFijo.EstadoActivo.BAJA).count()
        valor_total = sum([a.valor_compra for a in activos], start=Decimal("0"))
        return Response(
            {
                "total_activos": total,
                "asignados": asignados,
                "en_mantenimiento": en_mantenimiento,
                "baja": baja,
                "valor_total_compra": valor_total,
            }
        )


class DepreciacionActivoViewSet(viewsets.ModelViewSet):
    queryset = DepreciacionActivo.objects.select_related("activo").all()
    serializer_class = DepreciacionActivoSerializer
    permission_classes = [RoleScopePermission]
    rbac_resource = Resources.INVENTARIO
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["activo", "metodo", "fecha"]
    ordering_fields = ["fecha", "monto", "valor_en_libros"]
    ordering = ["-fecha", "-id"]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [RoleScopePermission(), IsAdministradorOrInterno()]
        return [RoleScopePermission()]

    def get_queryset(self):
        queryset = super().get_queryset()
        scope = getattr(self.request, "_eft_scope", "OWN")
        return scope_queryset(queryset, self.request.user, scope)

    @action(detail=False, methods=["post"])
    def calcular_mes(self, request):
        fecha = request.data.get("fecha")
        if fecha:
            year, month, day = [int(x) for x in str(fecha).split("-")]
            fecha_obj = date(year, month, day)
        else:
            fecha_obj = date.today()

        activos = ActivoFijo.objects.filter(activo=True).exclude(estado=ActivoFijo.EstadoActivo.BAJA)
        creados = 0
        for activo in activos:
            dep = DepreciacionActivo.registrar_lineal(activo=activo, fecha=fecha_obj)
            if dep:
                creados += 1
        return Response({"depreciaciones_creadas": creados, "fecha": str(fecha_obj)})


class MantenimientoActivoViewSet(viewsets.ModelViewSet):
    queryset = MantenimientoActivo.objects.select_related("activo").all()
    serializer_class = MantenimientoActivoSerializer
    permission_classes = [RoleScopePermission]
    rbac_resource = Resources.INVENTARIO
    rbac_action_map = {"alertas": Actions.READ}
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["activo", "tipo", "estado", "alerta_vencida", "fecha_programada"]
    ordering_fields = ["fecha_programada", "costo", "fecha_creacion"]
    ordering = ["fecha_programada", "id"]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [RoleScopePermission(), IsAdministradorOrInterno()]
        return [RoleScopePermission()]

    def get_queryset(self):
        queryset = super().get_queryset()
        scope = getattr(self.request, "_eft_scope", "OWN")
        return scope_queryset(queryset, self.request.user, scope)

    @action(detail=False, methods=["get"])
    def alertas(self, request):
        qs = self.get_queryset().filter(alerta_vencida=True)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class MovimientoActivoViewSet(viewsets.ModelViewSet):
    queryset = MovimientoActivo.objects.select_related(
        "activo",
        "responsable_anterior",
        "responsable_nuevo",
        "ubicacion_anterior",
        "ubicacion_nueva",
        "usuario",
    ).all()
    serializer_class = MovimientoActivoSerializer
    permission_classes = [RoleScopePermission]
    rbac_resource = Resources.INVENTARIO
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["activo", "tipo", "responsable_nuevo", "ubicacion_nueva", "usuario"]
    ordering_fields = ["fecha_movimiento"]
    ordering = ["-fecha_movimiento", "-id"]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [RoleScopePermission(), IsAdministradorOrInterno()]
        return [RoleScopePermission()]

    def get_queryset(self):
        queryset = super().get_queryset()
        scope = getattr(self.request, "_eft_scope", "OWN")
        return scope_queryset(queryset, self.request.user, scope)

