from django.contrib import admin

from payments.models import Payment, PaymentLog


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'amount', 'currency', 'status', 'transaction_id', 'bold_reference')
    list_filter = ('status',)
    search_fields = ('transaction_id', 'bold_reference', 'order__id', 'order__user__email')
    list_select_related = ('order',)


@admin.register(PaymentLog)
class PaymentLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'payment', 'event', 'created_at')
    list_filter = ('event',)
    search_fields = ('payment__order__order_number', 'payment__transaction_id')
    list_select_related = ('payment',)
