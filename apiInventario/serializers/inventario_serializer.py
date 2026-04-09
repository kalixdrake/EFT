from rest_framework import serializers
from ..models import Producto, MovimientoInventario


class ProductoSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Producto"""
    
    necesita_reabastecimiento = serializers.BooleanField(
        read_only=True,
        source='necesita_reabastecimiento'
    )
    
    valor_inventario = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True,
        source='valor_inventario'
    )
    
    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'sku', 'descripcion', 'precio_base',
            'stock_actual',
            'stock_minimo', 'necesita_reabastecimiento', 'valor_inventario',
            'activo', 'imagen', 'fecha_creacion', 'fecha_actualizacion'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']


class ProductoListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listar productos"""
    
    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'sku', 'precio_base',
            'stock_actual', 'activo'
        ]


class MovimientoInventarioSerializer(serializers.ModelSerializer):
    """Serializer para MovimientoInventario"""
    
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    usuario_nombre = serializers.CharField(source='usuario.get_full_name', read_only=True)
    
    class Meta:
        model = MovimientoInventario
        fields = [
            'id', 'producto', 'producto_nombre', 'tipo', 'cantidad',
            'stock_anterior', 'stock_nuevo', 'usuario', 'usuario_nombre',
            'motivo', 'referencia', 'fecha_movimiento'
        ]
        read_only_fields = ['id', 'stock_anterior', 'stock_nuevo', 'fecha_movimiento', 'usuario']
    
    def validate(self, attrs):
        """Validación adicional"""
        producto = attrs.get('producto')
        tipo = attrs.get('tipo')
        cantidad = attrs.get('cantidad')
        
        if tipo == 'SALIDA' and producto.stock_actual < cantidad:
            raise serializers.ValidationError({
                'cantidad': f'Stock insuficiente. Disponible: {producto.stock_actual}'
            })
        
        return attrs
    
    def create(self, validated_data):
        """Asignar automáticamente el usuario actual"""
        validated_data['usuario'] = self.context['request'].user
        return super().create(validated_data)


class MovimientoInventarioCreateSerializer(serializers.ModelSerializer):
    """Serializer simplificado para crear movimientos"""
    
    class Meta:
        model = MovimientoInventario
        fields = ['producto', 'tipo', 'cantidad', 'motivo', 'referencia']
    
    def validate(self, attrs):
        """Validación adicional"""
        producto = attrs.get('producto')
        tipo = attrs.get('tipo')
        cantidad = attrs.get('cantidad')
        
        if tipo == 'SALIDA' and producto.stock_actual < cantidad:
            raise serializers.ValidationError({
                'cantidad': f'Stock insuficiente. Disponible: {producto.stock_actual}'
            })
        
        return attrs
    
    def create(self, validated_data):
        """Asignar automáticamente el usuario actual"""
        validated_data['usuario'] = self.context['request'].user
        return super().create(validated_data)
