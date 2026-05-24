from decimal import Decimal

from django.conf import settings
from django.db import transaction
from django.db.models import Count, F
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from locations.models import Address
from orders.models import Cart, CartItem, Order, OrderItem
from orders.serializers import (
    AddCartItemSerializer,
    CartSerializer,
    CreateOrderSerializer,
    OrderDetailSerializer,
    OrderListSerializer,
    UpdateCartItemSerializer,
)
from payments.models import Payment
from payments.services.bold import calculate_integrity_hash
from products.models import Product
from shipping.models import ShippingQuote
from shipping.services.skydropx import SkydropxClient, SkydropxError
from shipping.tasks import crear_guia_envio


class CartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_cart(self, user):
        cart, _ = Cart.objects.get_or_create(user=user)
        return Cart.objects.prefetch_related('items__product').get(pk=cart.pk)

    def get(self, request):
        cart = self._get_cart(request.user)
        serializer = CartSerializer(cart, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        serializer = AddCartItemSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        product = serializer.context['product']
        quantity = serializer.validated_data['quantity']
        cart = self._get_cart(request.user)
        item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity': quantity})
        if not created:
            new_quantity = item.quantity + quantity
            if new_quantity > product.stock:
                return Response({'detail': 'Insufficient stock.'}, status=status.HTTP_400_BAD_REQUEST)
            item.quantity = new_quantity
            item.save(update_fields=['quantity'])
        elif quantity > product.stock:
            item.delete()
            return Response({'detail': 'Insufficient stock.'}, status=status.HTTP_400_BAD_REQUEST)
        cart = self._get_cart(request.user)
        return Response(CartSerializer(cart, context={'request': request}).data, status=status.HTTP_200_OK)


class CartItemUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_cart_item(self, user, item_id):
        return CartItem.objects.select_related('cart', 'product').get(pk=item_id, cart__user=user)

    def put(self, request, item_id):
        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = self._get_cart_item(request.user, item_id)
        quantity = serializer.validated_data['quantity']
        if quantity > item.product.stock:
            return Response({'detail': 'Insufficient stock.'}, status=status.HTTP_400_BAD_REQUEST)
        item.quantity = quantity
        item.save(update_fields=['quantity'])
        cart = Cart.objects.prefetch_related('items__product').get(user=request.user)
        return Response(CartSerializer(cart, context={'request': request}).data)


class CartItemDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, item_id):
        item = CartItem.objects.select_related('cart').get(pk=item_id, cart__user=request.user)
        item.delete()
        cart = Cart.objects.prefetch_related('items__product').get(user=request.user)
        return Response(CartSerializer(cart, context={'request': request}).data)


class OrderListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderListSerializer

    def get_queryset(self):
        queryset = (
            Order.objects.select_related('user', 'address__municipality__department')
            .annotate(items_total=Count('items'))
            .prefetch_related('items')
        )
        user = self.request.user
        if not getattr(user, 'is_privileged', False) and not user.is_staff and not user.is_superuser:
            queryset = queryset.filter(user=user)
        return queryset.order_by('-created_at')


class OrderDetailAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderDetailSerializer

    def get_queryset(self):
        queryset = (
            Order.objects.select_related('user', 'address__municipality__department')
            .prefetch_related('items__product')
            .annotate(items_total=Count('items'))
        )
        user = self.request.user
        if not getattr(user, 'is_privileged', False) and not user.is_staff and not user.is_superuser:
            queryset = queryset.filter(user=user)
        return queryset


class OrderCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        try:
            quote = ShippingQuote.objects.get(
                quote_id=serializer.validated_data['shipping_quote_id'],
                user=request.user,
            )
        except ShippingQuote.DoesNotExist:
            return Response({'detail': 'Cotización inválida.'}, status=status.HTTP_400_BAD_REQUEST)
        address = Address.objects.select_related('municipality__department').get(
            pk=serializer.validated_data['address_id'],
            user=request.user,
        )

        with transaction.atomic():
            cart, _ = Cart.objects.select_for_update().get_or_create(user=request.user)
            cart = Cart.objects.select_for_update().prefetch_related('items__product').get(pk=cart.pk)
            items = list(cart.items.select_related('product').select_for_update())
            if not items:
                return Response({'detail': 'Cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)

            for item in items:
                if item.quantity > item.product.stock:
                    return Response({'detail': f'Insufficient stock for {item.product.name}.'}, status=status.HTTP_400_BAD_REQUEST)

            order = Order.objects.create(user=request.user, address=address)
            total = Decimal('0.00')
            shipping_credit_available = Decimal('0.00')
            for item in items:
                Product.objects.filter(pk=item.product_id).update(stock=F('stock') - item.quantity)
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    price=item.product.price,
                    quantity=item.quantity,
                )
                total += item.product.price * item.quantity
                shipping_credit_available += item.product.shipping_credit_cop * item.quantity

            shipping_cost_before_credit = quote.cost_cop
            shipping_credit_applied = min(shipping_credit_available, shipping_cost_before_credit)
            shipping_cost = max(Decimal('0.00'), shipping_cost_before_credit - shipping_credit_applied)

            order.shipping_quote = quote
            order.shipping_method = quote.carrier
            order.payment_method = serializer.validated_data['payment_method']
            order.notes = serializer.validated_data.get('notes', '')
            order.shipping_cost_before_credit = shipping_cost_before_credit
            order.shipping_credit_applied = shipping_credit_applied
            order.shipping_cost = shipping_cost
            order.is_free_shipping = shipping_cost == Decimal('0.00')
            order.total = total + shipping_cost
            if order.payment_method == Order.PaymentMethod.COD:
                order.status = Order.Status.PENDING_COD
            order.save(
                update_fields=[
                    'shipping_quote',
                    'shipping_method',
                    'payment_method',
                    'notes',
                    'shipping_cost_before_credit',
                    'shipping_credit_applied',
                    'shipping_cost',
                    'is_free_shipping',
                    'total',
                    'status',
                ]
            )

            if order.payment_method == Order.PaymentMethod.COD:
                Payment.objects.create(
                    order=order,
                    amount=shipping_cost,
                    currency='COP',
                    status=Payment.Status.PENDING_DELIVERY,
                )
            else:
                Payment.objects.create(
                    order=order,
                    amount=order.total,
                    currency='COP',
                    status=Payment.Status.PENDING,
                )
            cart.items.all().delete()

        order = (
            Order.objects.select_related('user', 'address__municipality__department')
            .prefetch_related('items__product')
            .annotate(items_total=Count('items'))
            .get(pk=order.pk)
        )
        response_data = OrderDetailSerializer(order).data
        if order.payment_method == Order.PaymentMethod.BOLD:
            amount_cents = int(order.total * 100)
            response_data['bold_data'] = {
                'order_reference': order.order_number,
                'amount_cents': amount_cents,
                'currency': 'COP',
                'integrity_hash': calculate_integrity_hash(order.order_number, amount_cents, 'COP'),
                'redirect_url': settings.BOLD_REDIRECT_URL,
                'checkout_url': settings.BOLD_CHECKOUT_URL,
                'public_key': settings.BOLD_PUBLIC_KEY,
            }
        else:
            response_data['bold_data'] = None

        if order.payment_method == Order.PaymentMethod.COD:
            crear_guia_envio.delay(order.id)

        return Response(response_data, status=status.HTTP_201_CREATED)


class OrderTrackingAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            order = Order.objects.select_related('shipment', 'user').get(pk=pk)
        except Order.DoesNotExist:
            return Response({'detail': 'Orden no encontrada.'}, status=status.HTTP_404_NOT_FOUND)
        user = request.user
        if not getattr(user, 'is_privileged', False) and not user.is_staff and not user.is_superuser:
            if order.user_id != user.id:
                return Response({'detail': 'No autorizado.'}, status=status.HTTP_403_FORBIDDEN)

        shipment = getattr(order, 'shipment', None)
        if not shipment or not shipment.skydropx_shipment_id:
            return Response({'detail': 'Envío no disponible.'}, status=status.HTTP_404_NOT_FOUND)

        client = SkydropxClient()
        try:
            tracking_data = client.get_tracking(shipment.skydropx_shipment_id)
        except SkydropxError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

        events = tracking_data.get('tracking_history') or tracking_data.get('events') or []
        return Response(
            {
                'tracking_number': shipment.tracking_number,
                'carrier': shipment.carrier,
                'current_status': shipment.status,
                'estimated_delivery': tracking_data.get('estimated_delivery'),
                'events': events,
            }
        )
