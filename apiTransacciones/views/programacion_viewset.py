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
    PresupuestoConsolidadoPorCuentaSerializer
)

from apiTransacciones.filters.programacion_filter import ProgramacionTransaccionFilter


class ProgramacionTransaccionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing programmed/future transactions
    
    Provides CRUD operations and custom actions for programmed transactions.
    """
    queryset = ProgramacionTransaccion.objects.all()
    serializer_class = ProgramacionTransaccionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProgramacionTransaccionFilter
    
    def get_serializer_class(self):
        """Return different serializers based on the action"""
        if self.action == 'list':
            return ProgramacionTransaccionListSerializer
        elif self.action == 'retrieve':
            return ProgramacionTransaccionDetailSerializer
        return ProgramacionTransaccionSerializer
    
    @action(detail=False, methods=['get'], url_path='pendientes')
    def pendientes(self, request):
        """Get all pending programmed transactions"""
        programaciones = ProgramacionTransaccion.objects.filter(
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
        programaciones = ProgramacionTransaccion.objects.filter(activa=True)
        
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

        # Validate state
        if programacion.estado != 'PENDIENTE':
            return Response(
                {'error': f'No se puede ejecutar una transacción en estado {programacion.estado}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not programacion.activa:
            return Response(
                {'error': 'La transacción programada está desactivada'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Intenta obtener la fecha desde la request, si no, pone la fecha actual.
        fecha_ejecucion = request.data.get('fecha_ejecucion')
        if fecha_ejecucion:
            try:
                fecha_ejecucion = datetime.fromisoformat(fecha_ejecucion.replace('Z', '+00:00'))
            except ValueError:
                return Response(
                    {'error': 'Formato de fecha inválido para fecha_ejecucion'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            fecha_ejecucion = timezone.now()

        # Create the actual transaction
        try:
            transaccion_data = {
                'monto':programacion.monto,
                'descripcion':programacion.descripcion,
                'fecha_ejecucion':fecha_ejecucion,
                'categoria':programacion.categoria.id,
                'cuenta':programacion.cuenta.id,
                'programacion':programacion.id
            }
            transaccion_serializer = TransaccionSerializer(data=transaccion_data)
            transaccion_serializer.is_valid(raise_exception=True)
            transaccion = transaccion_serializer.save()

        except Exception as e:
            return Response(
                {'error': f'Error al crear la transacción: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Handle recurrence
        if programacion.frecuencia == 'UNICA':
            # One-time: mark as executed
            programacion.estado = 'EJECUTADA'
            programacion.activa = False
            programacion.fecha_ultima_ejecucion = fecha_ejecucion
            programacion.save()
            message = 'Transacción ejecutada y programación finalizada.'
        else:
            # Recurring: calculate next occurrence
            next_date = _calculate_next_date(programacion.fecha_programada, programacion.frecuencia)
            # If next_date is beyond fecha_fin_repeticion, stop recurring
            if programacion.fecha_fin_repeticion and next_date > programacion.fecha_fin_repeticion:
                programacion.estado = 'EJECUTADA'  # or maybe keep as 'PENDIENTE' but deactivate?
                programacion.activa = False
                message = 'Transacción ejecutada. La recurrencia ha finalizado.'
            else:
                # Update for next occurrence
                programacion.fecha_programada = next_date
                programacion.fecha_ultima_ejecucion = fecha_ejecucion
                # Keep estado as PENDIENTE and activa as True
                message = 'Transacción ejecutada. Próxima ejecución programada para {}'.format(next_date)
            programacion.save()

        # Return success with transaction details and updated program info
        transaccion_url = request.build_absolute_uri(
            reverse('transaccion-detail', args=[transaccion.id]))
        programacion_url = request.build_absolute_uri(
            reverse('programacion-detail', args=[programacion.id])
        )

        return Response({
            'status': message,
            'transaccion': {
                'id': transaccion.id,
                'url': transaccion_url,
            },
            'programacion': {
                'id': programacion.id,
                'url': programacion_url,
            }
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='presupuesto-consolidado')
    def presupuesto_consolidado(self, request):
        cuentas_ids = request.query_params.getlist('cuentas')
        if cuentas_ids:
            cuentas = Cuenta.objects.filter(id__in=cuentas_ids)
        else:
            cuentas = Cuenta.objects.all()

        programaciones = ProgramacionTransaccion.objects.filter(
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