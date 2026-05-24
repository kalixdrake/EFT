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
        client = SkydropxClient()
        try:
            quotes = client.get_quotes(
                zip_from=settings.SKYDROPX_ORIGIN_POSTAL_CODE,
                zip_to=serializer.validated_data['destination_postal_code'],
                parcel=parcel,
                carriers=settings.SHIPPING_CARRIERS or None,
            )
        except SkydropxError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

        if not quotes:
            return Response({'detail': 'No hay cotizaciones disponibles.'}, status=status.HTTP_404_NOT_FOUND)

        response_quotes = []
        for quote in quotes:
            stored = ShippingQuote.objects.create(
                user=request.user,
                carrier=quote.carrier,
                service=quote.service,
                service_code=quote.service_code,
                estimated_days=quote.estimated_days,
                cost_cop=quote.cost,
                skydropx_quote_id=quote.raw.get('id', ''),
                destination_city=serializer.validated_data['destination_city'],
                destination_postal_code=serializer.validated_data['destination_postal_code'],
                weight_kg=metrics['weight_kg'],
                dimensions=metrics['dimensions'],
                shipping_credit_available=metrics['shipping_credit'],
                metadata={'raw_quote': quote.raw, 'items': serializer.validated_data['cart_items']},
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
