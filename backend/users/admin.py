from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('id', 'email', 'username', 'first_name', 'last_name', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('email', 'username', 'first_name', 'last_name', 'phone', 'document_number')
    ordering = ('id',)
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom fields', {'fields': ('role', 'phone', 'document_type', 'document_number')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Custom fields', {'fields': ('role', 'phone', 'document_type', 'document_number')}),
    )
