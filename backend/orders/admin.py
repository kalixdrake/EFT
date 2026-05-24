from django.contrib import admin

from orders.models import Cart, CartItem, Order, OrderItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    autocomplete_fields = ('product',)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    autocomplete_fields = ('product',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'updated_at')
    search_fields = ('user__email', 'user__username')
    list_select_related = ('user',)
    inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'product', 'quantity')
    list_select_related = ('cart', 'product')
    search_fields = ('cart__user__email', 'product__name', 'product__sku')
    autocomplete_fields = ('cart', 'product')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total', 'shipping_city', 'created_at')
    list_filter = ('status', 'shipping_department', 'created_at')
    search_fields = ('user__email', 'user__username', 'shipping_city', 'shipping_address')
    list_select_related = ('user',)
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product_name', 'price', 'quantity')
    list_select_related = ('order', 'product')
    search_fields = ('product_name', 'order__user__email', 'order__id', 'product__sku')
    autocomplete_fields = ('order', 'product')
