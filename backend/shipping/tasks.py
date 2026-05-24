from decimal import Decimal

from celery import shared_task
from django.conf import settings
from django.db import transaction
from rest_framework import serializers

from orders.models import Order
from shipping.models import Shipment, ShippingQuote
from shipping.services.skydropx import SkydropxClient, SkydropxError
from shipping.utils import calculate_shipping_metrics


def _origin_address():
    required = {
        'country_code': settings.SHIPPING_ORIGIN_COUNTRY,
        'postal_code': settings.SKYDROPX_ORIGIN_POSTAL_CODE,
        'area_level1': settings.SHIPPING_ORIGIN_STATE,
        'area_level2': settings.SHIPPING_ORIGIN_CITY,
        'area_level3': settings.SHIPPING_ORIGIN_CITY,
        'street1': settings.SHIPPING_ORIGIN_ADDRESS,
        'name': settings.SHIPPING_ORIGIN_NAME,
        'phone': settings.SHIPPING_ORIGIN_PHONE,
        'email': settings.SHIPPING_ORIGIN_EMAIL,
        'reference': settings.SHIPPING_ORIGIN_ADDRESS,
    }
    if not all([required['postal_code'], required['area_level1'], required['area_level2'], required['name']]):
        raise serializers.ValidationError('Faltan datos de origen para generar envíos.')
    return required


def _destination_address(order):
    user = order.user
    address = order.address
    phone = getattr(user, 'phone', '') or ''
    return {
        'country_code': settings.SHIPPING_DESTINATION_COUNTRY,
        'postal_code': address.postal_code or '',
        'area_level1': address.municipality.department.name,
        'area_level2': address.municipality.name,
        'area_level3': address.municipality.name,
        'street1': address.line,
        'name': f'{user.first_name} {user.last_name}'.strip() or user.email.split('@')[0],
        'company': '',
        'phone': phone or settings.SHIPPING_ORIGIN_PHONE,  # fallback to store phone if needed
        'email': user.email,
        'reference': address.label or address.line or 'Sin referencia',
    }


@shared_task(bind=True, max_retries=3)
def crear_guia_envio(self, order_id):
    order = (
        Order.objects.select_related('address__municipality__department', 'user', 'shipping_quote')
        .prefetch_related('items__product')
        .get(pk=order_id)
    )
    if not order.shipping_quote_id:
        raise serializers.ValidationError('La orden no tiene cotización asociada.')

    quote = ShippingQuote.objects.get(pk=order.shipping_quote_id)
    items_payload = []
    for item in order.items.all():
        if not item.product:
            raise serializers.ValidationError('Producto inválido para crear envío.')
        items_payload.append({'product': item.product, 'quantity': item.quantity})

    metrics = calculate_shipping_metrics(items_payload)
    package_type = (
        Shipment.PackageType.BOX if metrics['weight_kg'] <= Decimal('8.000') else Shipment.PackageType.MERCHANDISE
    )

    client = SkydropxClient()
    try:
        shipment_data = client.create_shipment(
            quotation_id=quote.skydropx_quotation_id,
            rate_id=quote.skydropx_rate_id,
            address_from=_origin_address(),
            address_to=_destination_address(order),
        )
    except SkydropxError as exc:
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)

    with transaction.atomic():
        shipment, created = Shipment.objects.select_for_update().get_or_create(
            order=order,
            defaults={
                'carrier': quote.carrier,
                'tracking_number': shipment_data.tracking_number,
                'label_url': shipment_data.label_url,
                'weight_kg': metrics['weight_kg'],
                'package_type': package_type,
                'status': Shipment.Status.PENDING,
                'skydropx_shipment_id': shipment_data.shipment_id,
                'cost': order.shipping_cost_before_credit,
                'estimated_days': quote.estimated_days,
            },
        )
        if not created:
            shipment.carrier = quote.carrier
            shipment.tracking_number = shipment.tracking_number or shipment_data.tracking_number
            shipment.label_url = shipment.label_url or shipment_data.label_url
            shipment.weight_kg = metrics['weight_kg']
            shipment.package_type = package_type
            shipment.skydropx_shipment_id = shipment.skydropx_shipment_id or shipment_data.shipment_id
            shipment.save()

        if order.status not in {
            Order.Status.PENDING_COD,
            Order.Status.CANCELLED,
            Order.Status.DELIVERED,
        }:
            order.status = Order.Status.SHIPPED
            order.save(update_fields=['status'])
