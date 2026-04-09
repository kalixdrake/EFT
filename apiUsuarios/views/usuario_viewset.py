from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from ..models import Usuario
from ..serializers import (
    UsuarioSerializer,
    UsuarioCreateSerializer,
    UsuarioListSerializer
)
from ..permissions import IsPropietarioOAdministrador
from ..permissions import RoleScopePermission, scope_queryset
from ..rbac_contracts import Resources


class UsuarioViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar usuarios del sistema."""
    
    queryset = Usuario.objects.all()
    permission_classes = [RoleScopePermission]
    rbac_resource = Resources.USER
    rbac_action_map = {}
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['activo_comercialmente', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'telefono']
    ordering_fields = ['fecha_registro', 'username']
    ordering = ['-fecha_registro']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UsuarioCreateSerializer
        elif self.action == 'list':
            return UsuarioListSerializer
        return UsuarioSerializer
    
    def get_permissions(self):
        if self.action == 'update' or self.action == 'partial_update':
            return [RoleScopePermission(), IsPropietarioOAdministrador()]
        return [RoleScopePermission()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        scope = getattr(self.request, "_eft_scope", "OWN")
        return scope_queryset(queryset, self.request.user, scope)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Endpoint para obtener información del usuario actual"""
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data)
