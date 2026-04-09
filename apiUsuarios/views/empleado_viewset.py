from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from ..models import Empleado
from ..permissions import RoleScopePermission
from ..rbac_contracts import Resources
from ..serializers import EmpleadoSerializer


class EmpleadoViewSet(viewsets.ModelViewSet):
    queryset = Empleado.objects.select_related("usuario").all()
    serializer_class = EmpleadoSerializer
    permission_classes = [RoleScopePermission]
    rbac_resource = Resources.USER
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["estado", "departamento"]
