from rest_framework import serializers

from locations.models import Address
from locations.serializers import AddressSerializer
from orders.models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_name', 'price', 'quantity')

    def get_product(self, obj):
        return obj.product_id


class OrderListSerializer(serializers.ModelSerializer):
    item_count = serializers.SerializerMethodField()
    address = AddressSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'order_number', 'status', 'total', 'created_at', 'address', 'item_count')

    def get_item_count(self, obj):
        return getattr(obj, 'items_total', obj.items.count())


class OrderDetailSerializer(OrderListSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_email = serializers.SerializerMethodField()

    class Meta(OrderListSerializer.Meta):
        fields = OrderListSerializer.Meta.fields + ('items', 'user_email')

    def get_user_email(self, obj):
        return obj.user.email


class CreateOrderSerializer(serializers.Serializer):
    address_id = serializers.IntegerField()

    def validate_address_id(self, value):
        request = self.context.get('request')
        if request is None:
            raise serializers.ValidationError('Request context is required.')
        if not Address.objects.filter(pk=value, user=request.user).exists():
            raise serializers.ValidationError('Address not found.')
        return value
