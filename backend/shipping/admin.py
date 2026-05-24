from django.contrib import admin

from shipping.models import Shipment, ShippingQuote


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'order',
        'carrier',
        'tracking_number',
        'status',
        'cost',
        'estimated_days',
        'weight_kg',
    )
    list_filter = ('status', 'carrier')
    search_fields = ('tracking_number', 'carrier', 'order__id', 'order__user__email')
    list_select_related = ('order',)


@admin.register(ShippingQuote)
class ShippingQuoteAdmin(admin.ModelAdmin):
    list_display = ('quote_id', 'user', 'carrier', 'service', 'cost_cop', 'estimated_days', 'created_at')
    list_filter = ('carrier',)
    search_fields = ('quote_id', 'user__email', 'carrier', 'service')
    list_select_related = ('user',)
