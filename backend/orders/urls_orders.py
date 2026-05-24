from django.urls import path

from orders.views import OrderCreateAPIView, OrderDetailAPIView, OrderListAPIView, OrderTrackingAPIView

urlpatterns = [
    path('', OrderListAPIView.as_view(), name='order-list'),
    path('create/', OrderCreateAPIView.as_view(), name='order-create'),
    path('<int:pk>/', OrderDetailAPIView.as_view(), name='order-detail'),
    path('<int:pk>/tracking/', OrderTrackingAPIView.as_view(), name='order-tracking'),
]
