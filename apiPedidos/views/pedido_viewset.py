from django.db import models
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from ..models import Pedido, DetallePedido
from ..serializers import (
    PedidoSerializer,
    PedidoCreateSerializer,
    PedidoListSerializer,
    DetallePedidoSerializer
)
from apiUsuarios.permissions import IsAdministrador, IsAdministradorOrInterno
from apiInventario.models import MovimientoInventario


class PedidoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar pedidos.
    
    Lógica por roles:
    - CLIENTE: Puede crear VENTA_CLIENTE y ver sus propios pedidos
    - SOCIO: Puede crear APARTADO_SOCIO (con estado PENDIENTE_APROBACION) y ver sus propios
    - INTERNO: Puede actualizar estados, ver todos, asignar pedidos
    - ADMINISTRADOR: Puede crear RE_STOCK, aprobar APARTADOS, acceso total
    """
    
    queryset = Pedido.objects.select_related('cliente', 'interno_asignado').prefetch_related('detalles__producto').all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['tipo', 'estado', 'cliente']
    search_fields = ['cliente__username', 'cliente__first_name', 'cliente__last_name', 'notas']
    ordering_fields = ['fecha_creacion', 'total']
    ordering = ['-fecha_creacion']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PedidoCreateSerializer
        elif self.action == 'list':
            return PedidoListSerializer
        return PedidoSerializer
    
    def get_permissions(self):
        # Todos los usuarios autenticados pueden crear pedidos (con restricciones por tipo)
        # Las validaciones específicas están en los serializers
        return [IsAuthenticated()]
    
    def get_queryset(self):
        """Filtrar queryset según el rol del usuario"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # Administradores e internos ven todos
        if user.es_administrador() or user.es_interno():
            return queryset
        
        # Clientes y socios solo ven sus propios pedidos
        return queryset.filter(cliente=user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdministrador])
    def aprobar(self, request, pk=None):
        """Permite a administradores aprobar pedidos de socios"""
        pedido = self.get_object()
        
        if pedido.tipo != 'APARTADO_SOCIO':
            return Response(
                {'error': 'Solo se pueden aprobar apartados de socios'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if pedido.estado != 'PENDIENTE_APROBACION':
            return Response(
                {'error': 'El pedido no está pendiente de aprobación'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        pedido.estado = 'APROBADO'
        pedido.save()
        
        serializer = self.get_serializer(pedido)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdministradorOrInterno])
    def cambiar_estado(self, request, pk=None):
        """Permite a internos/admins cambiar el estado de un pedido"""
        pedido = self.get_object()
        nuevo_estado = request.data.get('estado')
        
        if nuevo_estado not in dict(Pedido.EstadoPedido.choices):
            return Response(
                {'error': 'Estado inválido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Si se marca como completado, registrar fecha
        if nuevo_estado == 'COMPLETADO' and pedido.estado != 'COMPLETADO':
            pedido.fecha_completado = timezone.now()
            
            # Descontar stock si es venta o apartado
            if pedido.tipo in ['VENTA_CLIENTE', 'APARTADO_SOCIO']:
                for detalle in pedido.detalles.all():
                    MovimientoInventario.objects.create(
                        producto=detalle.producto,
                        tipo='SALIDA',
                        cantidad=detalle.cantidad,
                        usuario=request.user,
                        motivo=f'Pedido #{pedido.id} completado',
                        referencia=str(pedido.id)
                    )
        
        pedido.estado = nuevo_estado
        pedido.save()
        
        serializer = self.get_serializer(pedido)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdministradorOrInterno])
    def registrar_pago(self, request, pk=None):
        """Registra un pago parcial o total para un pedido"""
        pedido = self.get_object()
        monto = request.data.get('monto')
        
        if monto is None:
            return Response(
                {'error': 'Debe proporcionar un monto'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            monto = float(monto)
            if monto <= 0:
                raise ValueError("El monto debe ser positivo")
            
            pedido.monto_pagado += monto
            
            # Actualizar estado según el pago
            if pedido.esta_pagado():
                pedido.estado = 'PAGADO_PARCIAL' if pedido.estado == 'PENDIENTE' else pedido.estado
                if pedido.monto_pagado >= pedido.total:
                    # Si ya está completamente pagado, podría cambiar a completado
                    pass  # La lógica de negocio determina si pago = completado
            
            pedido.save()
            
            # Actualizar saldo del socio si aplica
            if pedido.tipo == 'APARTADO_SOCIO' and hasattr(pedido.cliente, 'perfil_socio'):
                perfil = pedido.cliente.perfil_socio
                perfil.saldo_pendiente = max(0, perfil.saldo_pendiente - monto)
                perfil.save()
            
            serializer = self.get_serializer(pedido)
            return Response(serializer.data)
            
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdministradorOrInterno])
    def asignar_interno(self, request, pk=None):
        """Asigna un usuario interno al pedido"""
        pedido = self.get_object()
        interno_id = request.data.get('interno_id')
        
        if not interno_id:
            return Response(
                {'error': 'Debe proporcionar un interno_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from apiUsuarios.models import Usuario
        try:
            interno = Usuario.objects.get(id=interno_id, rol__in=['INTERNO', 'ADMINISTRADOR'])
            pedido.interno_asignado = interno
            pedido.save()
            
            serializer = self.get_serializer(pedido)
            return Response(serializer.data)
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Usuario interno no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def mis_pedidos(self, request):
        """Endpoint para que usuarios vean sus propios pedidos"""
        pedidos = self.queryset.filter(cliente=request.user)
        serializer = PedidoListSerializer(pedidos, many=True)
        return Response(serializer.data)
