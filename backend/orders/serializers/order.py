from rest_framework import serializers

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

    class Meta:
        model = Order
        fields = ('id', 'status', 'total', 'created_at', 'shipping_city', 'item_count')

    def get_item_count(self, obj):
        return getattr(obj, 'items_total', obj.items.count())


class OrderDetailSerializer(OrderListSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    shipping_address = serializers.CharField(read_only=True)
    shipping_department = serializers.CharField(read_only=True)
    user_email = serializers.SerializerMethodField()

    class Meta(OrderListSerializer.Meta):
        fields = OrderListSerializer.Meta.fields + ('items', 'shipping_address', 'shipping_department', 'user_email')

    def get_user_email(self, obj):
        return obj.user.email


class CreateOrderSerializer(serializers.Serializer):
    shipping_address = serializers.CharField()
    shipping_city = serializers.CharField()
    shipping_department = serializers.CharField()