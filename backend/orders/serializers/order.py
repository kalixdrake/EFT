from decimal import Decimal

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
    payment_status = serializers.SerializerMethodField()
    shipment_status = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            'id',
            'order_number',
            'status',
            'total',
            'created_at',
            'address',
            'item_count',
            'shipping_cost',
            'shipping_cost_before_credit',
            'shipping_credit_applied',
            'is_free_shipping',
            'shipping_method',
            'payment_method',
            'payment_status',
            'shipment_status',
        )

    def get_item_count(self, obj):
        return getattr(obj, 'items_total', obj.items.count())

    def get_payment_status(self, obj):
        payment = getattr(obj, 'payment', None)
        return payment.status if payment else None

    def get_shipment_status(self, obj):
        shipment = getattr(obj, 'shipment', None)
        return shipment.status if shipment else None


class OrderDetailSerializer(OrderListSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_email = serializers.SerializerMethodField()
    subtotal = serializers.SerializerMethodField()
    shipment = serializers.SerializerMethodField()

    class Meta(OrderListSerializer.Meta):
        fields = OrderListSerializer.Meta.fields + ('items', 'user_email', 'subtotal', 'shipment')

    def get_user_email(self, obj):
        return obj.user.email

    def get_subtotal(self, obj):
        total = Decimal('0.00')
        for item in obj.items.all():
            total += item.price * item.quantity
        return total

    def get_shipment(self, obj):
        shipment = getattr(obj, 'shipment', None)
        if not shipment:
            return None
        return {
            'carrier': shipment.carrier,
            'tracking_number': shipment.tracking_number,
            'label_url': shipment.label_url,
            'status': shipment.status,
        }


class CreateOrderSerializer(serializers.Serializer):
    address_id = serializers.IntegerField()
    shipping_quote_id = serializers.UUIDField()
    payment_method = serializers.ChoiceField(choices=Order.PaymentMethod.choices)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_address_id(self, value):
        request = self.context.get('request')
        if request is None:
            raise serializers.ValidationError('Request context is required.')
        if not Address.objects.filter(pk=value, user=request.user).exists():
            raise serializers.ValidationError('Address not found.')
        return value
