from django.contrib import admin

from payments.models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'amount', 'status', 'transaction_id', 'bold_reference')
    list_filter = ('status',)
    search_fields = ('transaction_id', 'bold_reference', 'order__id', 'order__user__email')
    list_select_related = ('order',)
