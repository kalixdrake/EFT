from decimal import Decimal

from django.conf import settings
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from shipping.models import ShippingQuote
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
        if not settings.SKYDROPX_ORIGIN_POSTAL_CODE:
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
            'country_code': getattr(settings, 'SHIPPING_ORIGIN_COUNTRY', 'CO'),
            'postal_code': settings.SKYDROPX_ORIGIN_POSTAL_CODE,
            'area_level1': settings.SHIPPING_ORIGIN_STATE,
            'area_level2': settings.SHIPPING_ORIGIN_CITY,
            'area_level3': settings.SHIPPING_ORIGIN_CITY,
            'street1': settings.SHIPPING_ORIGIN_ADDRESS,
            'name': settings.SHIPPING_ORIGIN_NAME,
            'phone': settings.SHIPPING_ORIGIN_PHONE,
            'email': settings.SHIPPING_ORIGIN_EMAIL,
        }

        dest_city = serializer.validated_data['destination_city']
        address_to = {
            'country_code': getattr(settings, 'SHIPPING_DESTINATION_COUNTRY', 'CO'),
            'postal_code': serializer.validated_data['destination_postal_code'],
            'area_level1': serializer.validated_data.get('destination_area_level1') or dest_city,
            'area_level2': dest_city,
            'area_level3': serializer.validated_data.get('destination_area_level3') or dest_city,
        }

        client = SkydropxClient()
        try:
            quotes = client.get_quotes(
                address_from=address_from,
                address_to=address_to,
                parcel=parcel,
                carriers=settings.SHIPPING_CARRIERS or None,
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
