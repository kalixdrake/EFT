from decimal import Decimal

from django.conf import settings
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from shipping.models import ShippingQuote, ShippingOrigin
from shipping.serializers import ShippingQuoteRequestSerializer
from shipping.services.skydropx import SkydropxClient, SkydropxError
from shipping.utils import calculate_shipping_metrics


class ShippingQuoteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ShippingQuoteRequestSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        items = serializer.validated_data['cart_items']

        metrics = calculate_shipping_metrics(items)

        origin = ShippingOrigin.get_active()
        if not origin:
            return Response(
                {'detail': 'Origen de envío no configurado.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        parcel = {
            'weight': str(metrics['weight_kg']),
            'height': str(metrics['dimensions']['height']),
            'width': str(metrics['dimensions']['width']),
            'length': str(metrics['dimensions']['length']),
        }

        address_from = {
            'country_code': origin.country_code,
            'postal_code': origin.postal_code,
            'area_level1': origin.state,
            'area_level2': origin.city,
            'area_level3': origin.city,
            'street1': origin.address,
            'name': origin.name,
            'phone': origin.phone,
            'email': origin.email,
        }

        dest_city = serializer.validated_data['destination_city']
        address_to = {
            'country_code': origin.country_code,
            'postal_code': serializer.validated_data['destination_postal_code'],
            'area_level1': serializer.validated_data.get('destination_area_level1') or dest_city,
            'area_level2': dest_city,
            'area_level3': serializer.validated_data.get('destination_area_level3') or dest_city,
        }

        client = SkydropxClient()
        declared_amount = float(sum(
            item['product'].price * item['quantity'] for item in items
        ))
        try:
            quotes = client.get_quotes(
                address_from=address_from,
                address_to=address_to,
                parcel=parcel,
                carriers=settings.SHIPPING_CARRIERS or None,
                declared_amount=declared_amount,
            )
        except SkydropxError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

        if not quotes:
            return Response({'detail': 'No hay cotizaciones disponibles.'}, status=status.HTTP_404_NOT_FOUND)

        response_quotes = []
        items_metadata = [
            {'product_id': item['product'].id, 'quantity': item['quantity']} for item in items
        ]
        for quote in quotes:
            stored = ShippingQuote.objects.create(
                user=request.user,
                carrier=quote.carrier,
                service=quote.service,
                service_code=quote.service_code,
                estimated_days=quote.estimated_days,
                cost_cop=quote.cost,
                skydropx_quote_id=quote.rate_id,
                skydropx_quotation_id=quote.quotation_id,
                skydropx_rate_id=quote.rate_id,
                destination_city=dest_city,
                destination_postal_code=serializer.validated_data['destination_postal_code'],
                weight_kg=metrics['weight_kg'],
                dimensions={k: float(v) for k, v in metrics['dimensions'].items()},
                shipping_credit_available=metrics['shipping_credit'],
                metadata={'raw_quote': quote.raw, 'items': items_metadata},
            )
            cost_after_credit = max(Decimal('0.00'), quote.cost - metrics['shipping_credit'])
            response_quotes.append(
                {
                    'quote_id': str(stored.quote_id),
                    'carrier': quote.carrier,
                    'service': quote.service,
                    'estimated_days': quote.estimated_days,
                    'cost_cop': quote.cost,
                    'cost_after_credit': cost_after_credit,
                    'available': True,
                }
            )

        return Response(
            {
                'quotes': response_quotes,
                'weight_kg': metrics['weight_kg'],
                'shipping_credit_available': metrics['shipping_credit'],
                'dimensions': metrics['dimensions'],
            }
        )
