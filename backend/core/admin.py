from django.contrib import admin
from .models import Address, Contact, ActivityLog

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['street', 'city', 'region', 'country']
    list_filter = ['city', 'region', 'country']
    search_fields = ['street', 'city', 'region']

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['phone_primary', 'phone_secondary', 'email', 'whatsapp']
    search_fields = ['phone_primary', 'phone_secondary', 'email']

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'model_name', 'created_at']
    list_filter = ['action', 'model_name', 'created_at']
    search_fields = ['user__username', 'action', 'model_name']
    readonly_fields = ['user', 'action', 'model_name', 'object_id', 'details', 'ip_address', 'created_at']
