from rest_framework import serializers

from products.models import Category, Product, ProductImage


def build_image_url(image_field, request):
    if not image_field:
        return None
    url = image_field.url
    return request.build_absolute_uri(url) if request else url


class CategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'image')

    def get_image(self, obj):
        return build_image_url(obj.image, self.context.get('request'))


class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ('id', 'image', 'order')

    def get_image(self, obj):
        return build_image_url(obj.image, self.context.get('request'))


class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    stock = serializers.SerializerMethodField()
    cost_price = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'name', 'price', 'image', 'stock', 'category_name', 'cost_price')

    def get_image(self, obj):
        request = self.context.get('request')
        first_gallery_image = obj.images.first()
        if first_gallery_image:
            return build_image_url(first_gallery_image.image, request)
        return build_image_url(obj.image, request)

    def get_stock(self, obj):
        request = self.context.get('request')
        user = request.user if request else None
        if user and getattr(user, 'is_privileged', False):
            return obj.stock
        return obj.stock if obj.stock > 0 else None

    def get_cost_price(self, obj):
        request = self.context.get('request')
        user = request.user if request else None
        if user and getattr(user, 'is_privileged', False):
            return str(obj.cost_price)
        return None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        user = request.user if request else None
        if not (user and getattr(user, 'is_privileged', False)):
            data.pop('cost_price', None)
        if data.get('stock') is None:
            data.pop('stock', None)
        return data


class ProductDetailSerializer(ProductListSerializer):
    category = CategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta(ProductListSerializer.Meta):
        fields = ProductListSerializer.Meta.fields + ('description', 'sku', 'category', 'images')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not data.get('images') and data.get('image'):
            data['images'] = [{'id': None, 'image': data['image'], 'order': 0}]
        return data
