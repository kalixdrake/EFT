from django.db import models
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from ..models import Nomina
from ..serializers import NominaSerializer, NominaCreateSerializer
from apiUsuarios.permissions import IsAdministrador, IsAdministradorOrInterno


class NominaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar nóminas.
    
    Permisos:
    - Solo ADMINISTRADORES pueden CREAR, ACTUALIZAR, ELIMINAR
    - INTERNOS pueden VER sus propias nóminas
    - ADMINISTRADORES pueden ver todas
    """
    
    queryset = Nomina.objects.select_related('empleado', 'aprobado_por').all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['estado', 'periodicidad', 'empleado']
    search_fields = ['empleado__username', 'empleado__first_name', 'empleado__last_name', 'notas']
    ordering_fields = ['fecha_pago_programada', 'salario_base']
    ordering = ['-fecha_pago_programada']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return NominaCreateSerializer
        return NominaSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Solo administradores pueden gestionar nóminas
            permission_classes = [IsAdministrador]
        else:
            # Internos y admins pueden ver
            permission_classes = [IsAdministradorOrInterno]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Filtrar queryset según el rol del usuario"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # Administradores ven todas
        if user.es_administrador():
            return queryset
        
        # Internos solo ven sus propias nóminas
        return queryset.filter(empleado=user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdministrador])
    def aprobar_pago(self, request, pk=None):
        """Permite a administradores aprobar y marcar como pagada una nómina"""
        nomina = self.get_object()
        
        if nomina.estado == 'PAGADO':
            return Response(
                {'error': 'La nómina ya está marcada como pagada'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        nomina.estado = 'PAGADO'
        nomina.fecha_pago_efectiva = timezone.now().date()
        nomina.aprobado_por = request.user
        nomina.save()
        
        serializer = self.get_serializer(nomina)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAdministrador])
    def pendientes(self, request):
        """Lista nóminas pendientes de pago"""
        nominas = self.queryset.filter(estado='PENDIENTE')
        serializer = NominaSerializer(nominas, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAdministrador])
    def retrasadas(self, request):
        """Lista nóminas retrasadas (pendientes con fecha vencida)"""
        hoy = timezone.now().date()
        nominas = self.queryset.filter(
            estado='PENDIENTE',
            fecha_pago_programada__lt=hoy
        )
        serializer = NominaSerializer(nominas, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAdministrador])
    def resumen_mensual(self, request):
        """Calcula el gasto total en nóminas del mes actual"""
        hoy = timezone.now().date()
        inicio_mes = hoy.replace(day=1)
        
        nominas_mes = self.queryset.filter(
            fecha_pago_programada__gte=inicio_mes,
            fecha_pago_programada__lte=hoy
        )
        
        total = sum(n.salario_neto() for n in nominas_mes)
        pendientes = nominas_mes.filter(estado='PENDIENTE').count()
        pagadas = nominas_mes.filter(estado='PAGADO').count()
        
        return Response({
            'mes': hoy.strftime('%Y-%m'),
            'total_nominas': nominas_mes.count(),
            'total_monto': total,
            'pendientes': pendientes,
            'pagadas': pagadas
        })
