from django.urls import path

from orders.views import CartAPIView, CartItemDeleteAPIView, CartItemUpdateAPIView

urlpatterns = [
    path('', CartAPIView.as_view(), name='cart-detail'),
    path('add/', CartAPIView.as_view(), name='cart-add'),
    path('update/<int:item_id>/', CartItemUpdateAPIView.as_view(), name='cart-item-update'),
    path('remove/<int:item_id>/', CartItemDeleteAPIView.as_view(), name='cart-item-delete'),
]