from django.db.models import Q
from rest_framework import generics
from rest_framework.permissions import AllowAny

from products.models import Category, Product
from products.serializers import CategorySerializer, ProductDetailSerializer, ProductListSerializer


class ProductListView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Product.objects.select_related('category').prefetch_related('images')
        user = self.request.user if self.request.user.is_authenticated else None
        if not (user and getattr(user, 'is_privileged', False)):
            queryset = queryset.filter(is_active=True)

        category_slug = self.request.query_params.get('category')
        search = self.request.query_params.get('search')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(description__icontains=search)
                | Q(sku__icontains=search)
                | Q(category__name__icontains=search)
            )
        return queryset


class ProductDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = ProductDetailSerializer

    def get_queryset(self):
        queryset = Product.objects.select_related('category').prefetch_related('images')
        user = self.request.user if self.request.user.is_authenticated else None
        if not (user and getattr(user, 'is_privileged', False)):
            queryset = queryset.filter(is_active=True)
        return queryset


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]