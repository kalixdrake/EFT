from rest_framework import serializers
from ..models import Pedido, DetallePedido
from apiInventario.models import Producto
from apiUsuarios.models import Cliente, Socio


class DetallePedidoSerializer(serializers.ModelSerializer):
    """Serializer para detalles de pedido"""
    
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True, source='subtotal')
    monto_impuesto = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True, source='monto_impuesto')
    total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True, source='total')
    
    class Meta:
        model = DetallePedido
        fields = [
            'id', 'producto', 'producto_nombre', 'cantidad',
            'precio_unitario', 'subtotal',
            'monto_impuesto', 'total', 'notas'
        ]
        read_only_fields = ['id', 'subtotal', 'monto_impuesto', 'total']
    
    def validate(self, attrs):
        """Validación para verificar stock disponible"""
        producto = attrs.get('producto')
        cantidad = attrs.get('cantidad')
        pedido_tipo = self.context.get('pedido_tipo')
        
        # Solo validar stock para ventas y apartados
        if pedido_tipo in ['VENTA_CLIENTE', 'APARTADO_SOCIO']:
            if producto.stock_actual < cantidad:
                raise serializers.ValidationError({
                    'cantidad': f'Stock insuficiente. Disponible: {producto.stock_actual}'
                })
        
        return attrs


class PedidoSerializer(serializers.ModelSerializer):
    """Serializer completo para pedidos"""
    
    detalles = DetallePedidoSerializer(many=True, read_only=True)
    cliente_nombre = serializers.CharField(source='cliente.get_full_name', read_only=True)
    interno_nombre = serializers.CharField(source='interno_asignado.get_full_name', read_only=True, allow_null=True)
    saldo_pendiente = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True, source='saldo_pendiente')
    esta_pagado = serializers.BooleanField(read_only=True, source='esta_pagado')
    ubicacion_entrega_nombre = serializers.CharField(source='ubicacion_entrega.nombre', read_only=True, allow_null=True)
    
    class Meta:
        model = Pedido
        fields = [
            'id', 'tipo', 'estado', 'cliente', 'cliente_nombre',
            'interno_asignado', 'interno_nombre', 'total', 'monto_pagado',
            'ubicacion_entrega', 'ubicacion_entrega_nombre',
            'saldo_pendiente', 'esta_pagado', 'porcentaje_descuento',
            'notas', 'fecha_creacion', 'fecha_actualizacion',
            'fecha_completado', 'detalles'
        ]
        read_only_fields = ['id', 'total', 'fecha_creacion', 'fecha_actualizacion', 'fecha_completado']


class PedidoCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear pedidos con sus detalles"""
    
    detalles = DetallePedidoSerializer(many=True, write_only=True)
    
    class Meta:
        model = Pedido
        fields = ['tipo', 'cliente', 'ubicacion_entrega', 'detalles', 'notas', 'porcentaje_descuento']
    
    def validate_tipo(self, value):
        """Validar que el tipo de pedido sea apropiado para la entidad del usuario"""
        request = self.context.get('request')
        user = request.user if request else None
        
        if not user:
            raise serializers.ValidationError("Usuario no autenticado")
        
        is_cliente = Cliente.objects.filter(usuario=user).exists()
        is_socio = Socio.objects.filter(usuario=user).exists()
        is_admin = user.es_administrador()

        if is_cliente and value != 'VENTA_CLIENTE':
            raise serializers.ValidationError("Los clientes solo pueden crear pedidos de venta")

        if is_socio and value != 'APARTADO_SOCIO':
            raise serializers.ValidationError("Los socios solo pueden crear apartados")

        if value == 'RE_STOCK' and not is_admin:
            raise serializers.ValidationError("Solo administradores pueden crear pedidos de reabastecimiento")
        
        return value
    
    def create(self, validated_data):
        """Crear pedido con sus detalles"""
        detalles_data = validated_data.pop('detalles')
        request = self.context.get('request')
        
        # Determinar estado inicial según tipo de pedido
        tipo = validated_data['tipo']
        if tipo == 'APARTADO_SOCIO':
            validated_data['estado'] = 'PENDIENTE_APROBACION'
        else:
            validated_data['estado'] = 'PENDIENTE'
        
        # Si es un cliente/socio creando su propio pedido
        if not validated_data.get('cliente'):
            validated_data['cliente'] = request.user
        
        pedido = Pedido.objects.create(**validated_data)
        
        # Crear detalles
        for detalle_data in detalles_data:
            detalle_data.pop("monto_impuesto", None)
            DetallePedido.objects.create(pedido=pedido, **detalle_data)
        
        # Recalcular total
        pedido.calcular_total()
        pedido.save()
        
        return pedido


class PedidoListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listar pedidos"""
    
    cliente_nombre = serializers.CharField(source='cliente.get_full_name', read_only=True)
    
    class Meta:
        model = Pedido
        fields = ['id', 'tipo', 'estado', 'cliente_nombre', 'total', 'fecha_creacion']
