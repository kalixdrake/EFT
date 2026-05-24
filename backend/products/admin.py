from django.contrib import admin

from products.models import Category, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'order')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'sku', 'category', 'price', 'cost_price', 'stock', 'is_active')
    list_filter = ('is_active', 'category')
    search_fields = ('name', 'sku', 'description', 'category__name')
    list_select_related = ('category',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]
