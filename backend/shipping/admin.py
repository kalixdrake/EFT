from django.contrib import admin

from shipping.models import Shipment


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'carrier', 'tracking_number', 'status', 'cost', 'estimated_days')
    list_filter = ('status', 'carrier')
    search_fields = ('tracking_number', 'carrier', 'order__id', 'order__user__email')
    list_select_related = ('order',)
