from rest_framework import serializers

from products.models import Product


class ShippingQuoteItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class ShippingQuoteRequestSerializer(serializers.Serializer):
    cart_items = ShippingQuoteItemSerializer(many=True)
    destination_city = serializers.CharField()
    destination_postal_code = serializers.CharField()
    destination_area_level1 = serializers.CharField(
        help_text='Departamento/estado de destino (ej. "Antioquia")',
        required=False,
        allow_blank=True,
        default='',
    )
    destination_area_level3 = serializers.CharField(
        help_text='Barrio/colonia de destino (opcional)',
        required=False,
        allow_blank=True,
        default='',
    )

    def validate_cart_items(self, value):
        if not value:
            raise serializers.ValidationError('El carrito está vacío.')
        product_ids = [item['product_id'] for item in value]
        products = Product.objects.filter(pk__in=product_ids, is_active=True)
        products_map = {product.id: product for product in products}
        missing = [str(pid) for pid in product_ids if pid not in products_map]
        if missing:
            raise serializers.ValidationError(f'Productos no encontrados: {", ".join(missing)}.')
        for item in value:
            item['product'] = products_map[item['product_id']]
        return value
