from decimal import Decimal

from django.db import transaction
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from orders.models import Order
from payments.models import Payment, PaymentLog
from payments.services.bold import validate_signature
from shipping.tasks import crear_guia_envio


class BoldWebhookAPIView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'bold_webhook'

    def post(self, request):
        signature = request.headers.get('X-Bold-Signature', '')
        if not validate_signature(request.body, signature):
            return Response({'detail': 'Firma inválida.'}, status=status.HTTP_400_BAD_REQUEST)

        payload = request.data
        event = payload.get('event')
        transaction_id = payload.get('transaction_id')
        order_reference = payload.get('order_reference')
        amount = payload.get('amount')
        currency = payload.get('currency') or 'COP'

        if not all([event, transaction_id, order_reference, amount]):
            return Response({'detail': 'Payload incompleto.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(order_number=order_reference)
        except Order.DoesNotExist:
            return Response({'detail': 'Orden no encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        approved_events = {'SALE_APPROVED'}
        rejected_events = {'SALE_REJECTED'}

        with transaction.atomic():
            payment = Payment.objects.select_for_update().filter(transaction_id=transaction_id).first()
            if payment and payment.order_id != order.id:
                PaymentLog.objects.create(
                    payment=payment,
                    event=event,
                    payload={'note': 'Transaction id reused', **payload},
                )
                return Response({'status': 'received'})

            if not payment:
                payment = Payment.objects.select_for_update().filter(order=order).first()
                if not payment:
                    payment = Payment.objects.create(
                        order=order,
                        transaction_id=transaction_id,
                        amount=Decimal(str(amount)),
                        currency=currency,
                        status=Payment.Status.PENDING,
                        metadata=payload,
                    )
                else:
                    payment.transaction_id = transaction_id
                    payment.amount = Decimal(str(amount))
                    payment.currency = currency
                    payment.metadata = payload

            if event in approved_events:
                payment.status = Payment.Status.APPROVED
                order.status = Order.Status.CONFIRMED
            elif event in rejected_events:
                payment.status = Payment.Status.REJECTED

            payment.save()
            order.save(update_fields=['status'])

            PaymentLog.objects.create(payment=payment, event=event, payload=payload)

        if event in approved_events:
            try:
                crear_guia_envio.delay(order.id)
            except Exception:
                # Task failures are handled internally (retries/logs); never block the 200 response
                pass

        return Response({'status': 'received'})
