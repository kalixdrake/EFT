from django.contrib import admin

from locations.models import Address, Department, Municipality


class MunicipalityInline(admin.TabularInline):
    model = Municipality
    extra = 1


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    inlines = [MunicipalityInline]


@admin.register(Municipality)
class MunicipalityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'department')
    list_filter = ('department',)
    search_fields = ('name', 'department__name')
    list_select_related = ('department',)
    autocomplete_fields = ('department',)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'line', 'municipality', 'label', 'is_default', 'updated_at')
    list_filter = ('is_default', 'municipality__department')
    search_fields = ('line', 'label', 'user__email', 'municipality__name')
    list_select_related = ('user', 'municipality', 'municipality__department')
    autocomplete_fields = ('user', 'municipality')
