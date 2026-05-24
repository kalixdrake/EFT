from django.urls import path

from products.views import CategoryListView, ProductDetailView, ProductListView

urlpatterns = [
    path('', ProductListView.as_view(), name='product-list'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
]