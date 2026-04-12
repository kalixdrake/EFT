from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import Socio
from ..permissions import IsAdministradorOrInterno
from ..permissions import RoleScopePermission, scope_queryset
from ..rbac_contracts import Actions, Resources
from ..serializers import SocioSerializer


class SocioViewSet(viewsets.ModelViewSet):
    queryset = Socio.objects.select_related("usuario").all()
    serializer_class = SocioSerializer
    permission_classes = [RoleScopePermission]
    rbac_resource = Resources.USER
    rbac_action_map = {"ajustar_saldo": Actions.UPDATE}
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["activo", "fecha_acuerdo"]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy", "ajustar_saldo"]:
            return [RoleScopePermission(), IsAdministradorOrInterno()]
        return [RoleScopePermission()]

    def get_queryset(self):
        queryset = super().get_queryset()
        scope = getattr(self.request, "_eft_scope", "OWN")
        return scope_queryset(queryset, self.request.user, scope)

    @action(detail=True, methods=["post"])
    def ajustar_saldo(self, request, pk=None):
        socio = self.get_object()
        monto = request.data.get("monto")
        if monto is None:
            return Response({"error": "Debe proporcionar un monto"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            monto = float(monto)
            socio.saldo_pendiente += monto
            if socio.saldo_pendiente < 0:
                socio.saldo_pendiente = 0
            socio.save()
            serializer = self.get_serializer(socio)
            return Response(serializer.data)
        except ValueError:
            return Response({"error": "Monto inválido"}, status=status.HTTP_400_BAD_REQUEST)
