from decimal import Decimal

from rest_framework import serializers


def calculate_shipping_metrics(items):
    if not items:
        raise serializers.ValidationError('No hay productos para cotizar.')

    total_weight = Decimal('0.000')
    max_length = Decimal('0.00')
    max_width = Decimal('0.00')
    max_height = Decimal('0.00')
    shipping_credit = Decimal('0.00')

    for item in items:
        product = item['product']
        quantity = item['quantity']
        if product.weight_kg <= 0:
            raise serializers.ValidationError(f'Peso inválido para {product.name}.')
        if product.box_length_cm <= 0 or product.box_width_cm <= 0 or product.box_height_cm <= 0:
            raise serializers.ValidationError(f'Dimensiones inválidas para {product.name}.')

        total_weight += product.weight_kg * quantity
        max_length = max(max_length, product.box_length_cm)
        max_width = max(max_width, product.box_width_cm)
        max_height = max(max_height, product.box_height_cm)
        shipping_credit += product.shipping_credit_cop * quantity

    return {
        'weight_kg': total_weight,
        'dimensions': {
            'length': max_length,
            'width': max_width,
            'height': max_height,
        },
        'shipping_credit': shipping_credit,
    }
