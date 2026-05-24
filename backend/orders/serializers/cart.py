from rest_framework import serializers

from orders.models import CartItem
from products.models import Product


class CartItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), write_only=True, required=False)
    product_id = serializers.SerializerMethodField()
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=12, decimal_places=2, read_only=True)
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ('id', 'product', 'product_id', 'product_name', 'product_price', 'product_image', 'quantity')

    def get_product_id(self, obj):
        return obj.product_id

    def get_product_image(self, obj):
        if not obj.product or not obj.product.image:
            return None
        request = self.context.get('request')
        url = obj.product.image.url
        return request.build_absolute_uri(url) if request else url


class CartSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    def get_total(self, obj):
        total = 0
        for item in obj.items.select_related('product').all():
            total += item.product.price * item.quantity
        return total


class AddCartItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

    def validate_product_id(self, value):
        try:
            product = Product.objects.get(pk=value, is_active=True)
        except Product.DoesNotExist as exc:
            raise serializers.ValidationError('Product not found.') from exc
        self.context['product'] = product
        return value


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)