from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from ..models import Usuario, PerfilSocio
from ..serializers import (
    UsuarioSerializer,
    UsuarioCreateSerializer,
    UsuarioListSerializer,
    PerfilSocioSerializer
)
from ..permissions import IsAdministradorOrInterno, IsAdministrador, IsPropietarioOAdministrador


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar usuarios del sistema.
    
    - list: Lista usuarios (filtrado por rol para no-administradores)
    - retrieve: Obtiene detalles de un usuario
    - create: Crea nuevo usuario (solo admins/internos)
    - update/partial_update: Actualiza usuario
    - destroy: Elimina usuario (solo admins)
    """
    
    queryset = Usuario.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['rol', 'activo_comercialmente', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'telefono']
    ordering_fields = ['fecha_registro', 'username', 'rol']
    ordering = ['-fecha_registro']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UsuarioCreateSerializer
        elif self.action == 'list':
            return UsuarioListSerializer
        return UsuarioSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            # Solo admins/internos pueden crear o eliminar usuarios
            permission_classes = [IsAdministradorOrInterno]
        elif self.action in ['update', 'partial_update']:
            # El propietario o admins pueden actualizar
            permission_classes = [IsPropietarioOAdministrador]
        else:
            # Cualquier usuario autenticado puede listar/ver
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Filtrar queryset según el rol del usuario"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # Administradores e internos ven todos
        if user.es_administrador() or user.es_interno():
            return queryset
        
        # Clientes y socios solo se ven a sí mismos
        return queryset.filter(id=user.id)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Endpoint para obtener información del usuario actual"""
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdministrador])
    def cambiar_rol(self, request, pk=None):
        """Permite a administradores cambiar el rol de un usuario"""
        usuario = self.get_object()
        nuevo_rol = request.data.get('rol')
        
        if nuevo_rol not in dict(Usuario.Rol.choices):
            return Response(
                {'error': 'Rol inválido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        usuario.rol = nuevo_rol
        usuario.save()
        
        serializer = UsuarioSerializer(usuario)
        return Response(serializer.data)


class PerfilSocioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar perfiles de socios.
    Solo administradores e internos pueden gestionar perfiles.
    """
    
    queryset = PerfilSocio.objects.select_related('usuario').all()
    serializer_class = PerfilSocioSerializer
    permission_classes = [IsAdministradorOrInterno]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['activo', 'fecha_acuerdo']
    search_fields = ['usuario__username', 'usuario__email', 'usuario__first_name', 'usuario__last_name']
    ordering = ['-fecha_acuerdo']
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdministrador])
    def ajustar_saldo(self, request, pk=None):
        """Permite ajustar el saldo pendiente de un socio"""
        perfil = self.get_object()
        monto = request.data.get('monto')
        
        if monto is None:
            return Response(
                {'error': 'Debe proporcionar un monto'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            monto = float(monto)
            perfil.saldo_pendiente += monto
            if perfil.saldo_pendiente < 0:
                perfil.saldo_pendiente = 0
            perfil.save()
            
            serializer = self.get_serializer(perfil)
            return Response(serializer.data)
        except ValueError:
            return Response(
                {'error': 'Monto inválido'},
                status=status.HTTP_400_BAD_REQUEST
            )
