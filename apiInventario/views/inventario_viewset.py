from django.db import models
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from ..models import Producto, MovimientoInventario
from ..serializers import (
    ProductoSerializer,
    ProductoListSerializer,
    MovimientoInventarioSerializer,
    MovimientoInventarioCreateSerializer
)
from apiUsuarios.permissions import IsAdministradorOrInterno


class ProductoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar productos del inventario.
    
    Permisos:
    - CREAR/ACTUALIZAR/ELIMINAR: Solo Administradores e Internos
    - LEER: Todos los usuarios autenticados
    """
    
    queryset = Producto.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['activo', 'porcentaje_impuesto']
    search_fields = ['nombre', 'sku', 'descripcion']
    ordering_fields = ['nombre', 'precio_base', 'stock_actual', 'fecha_creacion']
    ordering = ['nombre']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductoListSerializer
        return ProductoSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Solo administradores e internos pueden modificar productos
            permission_classes = [IsAdministradorOrInterno]
        else:
            # Lectura permitida para todos los autenticados
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def bajo_stock(self, request):
        """Retorna productos con stock bajo (necesitan reabastecimiento)"""
        productos = self.queryset.filter(stock_actual__lte=models.F('stock_minimo'))
        serializer = ProductoListSerializer(productos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def valor_total_inventario(self, request):
        """Calcula el valor total del inventario"""
        from django.db.models import Sum, F
        
        total = self.queryset.aggregate(
            valor_total=Sum(F('precio_base') * F('stock_actual'))
        )
        
        return Response({
            'valor_total_inventario': total['valor_total'] or 0
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdministradorOrInterno])
    def ajustar_stock(self, request, pk=None):
        """Permite ajustar manualmente el stock de un producto"""
        producto = self.get_object()
        nuevo_stock = request.data.get('stock')
        motivo = request.data.get('motivo', 'Ajuste manual de stock')
        
        if nuevo_stock is None:
            return Response(
                {'error': 'Debe proporcionar el nuevo stock'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            nuevo_stock = int(nuevo_stock)
            if nuevo_stock < 0:
                raise ValueError("El stock no puede ser negativo")
            
            # Crear movimiento de ajuste
            MovimientoInventario.objects.create(
                producto=producto,
                tipo='AJUSTE',
                cantidad=nuevo_stock,
                usuario=request.user,
                motivo=motivo
            )
            
            serializer = self.get_serializer(producto)
            return Response(serializer.data)
            
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class MovimientoInventarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar movimientos de inventario.
    
    Permisos:
    - CREAR: Solo Administradores e Internos
    - LEER: Todos los usuarios autenticados
    - ACTUALIZAR/ELIMINAR: No permitido (trazabilidad)
    """
    
    queryset = MovimientoInventario.objects.select_related('producto', 'usuario').all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['tipo', 'producto', 'usuario']
    search_fields = ['producto__nombre', 'producto__sku', 'motivo', 'referencia']
    ordering_fields = ['fecha_movimiento']
    ordering = ['-fecha_movimiento']
    
    # Los movimientos no se pueden editar ni eliminar para mantener trazabilidad
    http_method_names = ['get', 'post', 'head', 'options']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MovimientoInventarioCreateSerializer
        return MovimientoInventarioSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            # Solo administradores e internos pueden crear movimientos
            permission_classes = [IsAdministradorOrInterno]
        else:
            # Lectura permitida para todos los autenticados
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def por_producto(self, request):
        """Obtiene el historial de movimientos de un producto específico"""
        producto_id = request.query_params.get('producto_id')
        
        if not producto_id:
            return Response(
                {'error': 'Debe proporcionar producto_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        movimientos = self.queryset.filter(producto_id=producto_id)
        serializer = self.get_serializer(movimientos, many=True)
        return Response(serializer.data)
