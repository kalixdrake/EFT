from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.urls import reverse

from apiCuentas.models.cuenta_model import Cuenta

from apiTransacciones.helpers.next_date import _calculate_next_date
from django.utils import timezone
from datetime import datetime, date, timedelta
import calendar
from django.db.models import Sum

from decimal import Decimal

from django_filters.rest_framework import DjangoFilterBackend

from apiTransacciones.models.transaccion_model import Transaccion
from apiTransacciones.serializers.transaccion_serializer import TransaccionSerializer

from apiTransacciones.models.programacion_model import ProgramacionTransaccion
from apiTransacciones.serializers.programacion_serializer import (
    ProgramacionTransaccionSerializer,
    ProgramacionTransaccionListSerializer,
    ProgramacionTransaccionDetailSerializer,
    PresupuestoConsolidadoPorCuentaSerializer,
    EjecutarProgramacionSerializer
)

from apiTransacciones.filters.programacion_filter import ProgramacionTransaccionFilter
from apiUsuarios.permissions import RoleScopePermission, scope_queryset
from apiUsuarios.permissions import IsAdministradorOrInterno
from apiUsuarios.rbac_contracts import Resources, Actions


class ProgramacionTransaccionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing programmed/future transactions
    
    Provides CRUD operations and custom actions for programmed transactions.
    """
    queryset = ProgramacionTransaccion.objects.all()
    serializer_class = ProgramacionTransaccionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProgramacionTransaccionFilter
    permission_classes = [RoleScopePermission]
    rbac_resource = Resources.TRANSACCION
    rbac_action_map = {
        "pendientes": Actions.READ,
        "activas": Actions.READ,
        "activar": Actions.UPDATE,
        "desactivar": Actions.UPDATE,
        "cancelar": Actions.UPDATE,
        "ejecutar": Actions.UPDATE,
        "presupuesto_consolidado": Actions.READ,
    }
    
    def get_serializer_class(self):
        """Return different serializers based on the action"""
        if self.action == 'list':
            return ProgramacionTransaccionListSerializer
        elif self.action == 'retrieve':
            return ProgramacionTransaccionDetailSerializer
        return ProgramacionTransaccionSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        scope = getattr(self.request, "_eft_scope", "OWN")
        return scope_queryset(queryset, self.request.user, scope)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy", "activar", "desactivar", "cancelar", "ejecutar"]:
            return [RoleScopePermission(), IsAdministradorOrInterno()]
        return [RoleScopePermission()]
    
    @action(detail=False, methods=['get'], url_path='pendientes')
    def pendientes(self, request):
        """Get all pending programmed transactions"""
        programaciones = self.get_queryset().filter(
            estado='PENDIENTE',
            activa=True
        )
        
        filterset = ProgramacionTransaccionFilter(request.query_params, queryset=programaciones)
        programaciones = filterset.qs
        
        serializer = ProgramacionTransaccionListSerializer(programaciones, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='activas')
    def activas(self, request):
        """Get all active programmed transactions"""
        programaciones = self.get_queryset().filter(activa=True)
        
        filterset = ProgramacionTransaccionFilter(request.query_params, queryset=programaciones)
        programaciones = filterset.qs
        
        serializer = ProgramacionTransaccionListSerializer(programaciones, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], url_path='activar')
    def activar(self, request, pk=None):
        """Activate a programmed transaction"""
        try:
            programacion = self.get_object()
            programacion.activa = True
            programacion.save()
            programacion_url = request.build_absolute_uri(
                reverse('programacion-detail', args=[programacion.id])
            )
            return Response({
                'status': 'Programación activada exitosamente',
                'programacion': {
                    'id': programacion.id,
                    'url': programacion_url,
                }
            }, status=status.HTTP_200_OK)
        except ProgramacionTransaccion.DoesNotExist:
            return Response(
                {'error': 'Programación no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'], url_path='desactivar')
    def desactivar(self, request, pk=None):
        """Deactivate a programmed transaction"""
        try:
            programacion = self.get_object()
            programacion.activa = False
            programacion.save()
            programacion_url = request.build_absolute_uri(
                reverse('programacion-detail', args=[programacion.id])
            )
            return Response({
                'status': 'Programación desactivada exitosamente',
                'programacion': {
                    'id': programacion.id,
                    'url': programacion_url,
                }
            }, status=status.HTTP_200_OK)
        except ProgramacionTransaccion.DoesNotExist:
            return Response(
                {'error': 'Programación no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'], url_path='cancelar')
    def cancelar(self, request, pk=None):
        """Cancel a programmed transaction"""
        try:
            programacion = self.get_object()
            
            if programacion.estado == 'EJECUTADA':
                return Response(
                    {'error': 'No se puede cancelar una transacción que ya fue ejecutada'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            programacion.estado = 'CANCELADA'
            programacion.activa = False
            programacion.save()
            programacion_url = request.build_absolute_uri(
                reverse('programacion-detail', args=[programacion.id])
            )
            return Response({
                'status': 'Programación cancelada exitosamente',
                'programacion': {
                    'id': programacion.id,
                    'url': programacion_url,
                }
            }, status=status.HTTP_200_OK)
        except ProgramacionTransaccion.DoesNotExist:
            return Response(
                {'error': 'Programación no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'], url_path='ejecutar')
    def ejecutar(self, request, pk=None):
        """
        Manually execute a programmed transaction, creating an actual transaction record.
        Handles both one-time and recurring transactions.
        """
        programacion = self.get_object()
        serializer = EjecutarProgramacionSerializer(data=request.data,context={'programacion': programacion})
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        transaccion = result['transaccion']
        programacion = result['programacion']

        # Construir URLs para la respuesta
        transaccion_url = request.build_absolute_uri(
            reverse('transaccion-detail', args=[transaccion.id])
        )
        programacion_url = request.build_absolute_uri(
            reverse('programacion-detail', args=[programacion.id])
        )

        return Response({'status': result['message'],
                         'transaccion': {
                             'id': transaccion.id,
                             'url': transaccion_url,
                             },
                         'programacion': {
                             'id': programacion.id,
                             'url': programacion_url,
                             }
                        },
                     status=status.HTTP_200_OK
                    )
    
    @action(detail=False, methods=['get'], url_path='presupuesto-consolidado')
    def presupuesto_consolidado(self, request):
        scope = getattr(request, "_eft_scope", "OWN")
        cuentas_scope = scope_queryset(Cuenta.objects.all(), request.user, scope)
        cuentas_ids = request.query_params.getlist('cuentas')
        if cuentas_ids:
            cuentas = cuentas_scope.filter(id__in=cuentas_ids)
        else:
            cuentas = cuentas_scope

        programaciones = self.get_queryset().filter(
            estado='PENDIENTE',
            activa=True
        )

        # Usar el serializador por cuenta con many=True
        serializer = PresupuestoConsolidadoPorCuentaSerializer(
            cuentas,
            many=True,
            context={'programaciones': programaciones}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
