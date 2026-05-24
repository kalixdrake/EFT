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
        'name': settings.SHIPPING_ORIGIN_NAME,
        'address1': settings.SHIPPING_ORIGIN_ADDRESS,
        'city': settings.SHIPPING_ORIGIN_CITY,
        'province': settings.SHIPPING_ORIGIN_STATE,
        'zip': settings.SKYDROPX_ORIGIN_POSTAL_CODE,
        'country': settings.SHIPPING_ORIGIN_COUNTRY,
        'phone': settings.SHIPPING_ORIGIN_PHONE,
        'email': settings.SHIPPING_ORIGIN_EMAIL,
    }
    if not all(required.values()):
        raise serializers.ValidationError('Faltan datos de origen para generar envíos.')
    return required


def _destination_address(order):
    user = order.user
    address = order.address
    return {
        'name': f'{user.first_name} {user.last_name}'.strip() or user.username,
        'company': '-',
        'address1': address.line,
        'address2': address.label or '',
        'city': address.municipality.name,
        'province': address.municipality.department.name,
        'zip': address.postal_code,
        'country': settings.SHIPPING_DESTINATION_COUNTRY,
        'phone': user.phone or '',
        'email': user.email,
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
    parcel = {
        'weight': str(metrics['weight_kg']),
        'height': str(metrics['dimensions']['height']),
        'width': str(metrics['dimensions']['width']),
        'length': str(metrics['dimensions']['length']),
    }
    try:
        shipment_data = client.create_shipment(
            address_from=_origin_address(),
            address_to=_destination_address(order),
            parcel=parcel,
            carrier=quote.carrier,
            service_code=quote.service_code,
            order_reference=order.order_number,
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

        order.status = Order.Status.SHIPPED
        order.save(update_fields=['status'])
