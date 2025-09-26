from django.contrib import admin
from .models import MembershipType, Member, MembershipFee, FamilyMember

@admin.register(MembershipType)
class MembershipTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'monthly_fee', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']

class FamilyMemberInline(admin.TabularInline):
    model = FamilyMember
    extra = 0

class MembershipFeeInline(admin.TabularInline):
    model = MembershipFee
    extra = 0
    readonly_fields = ['receipt_number']

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['membership_number', 'user', 'membership_type', 'status', 'join_date']
    list_filter = ['membership_type', 'status', 'gender', 'join_date']
    search_fields = ['membership_number', 'user__first_name', 'user__last_name', 'user__email']
    readonly_fields = ['membership_number']
    inlines = [FamilyMemberInline, MembershipFeeInline]
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('user', 'membership_number', 'membership_type', 'status')
        }),
        ('Informations personnelles', {
            'fields': ('birth_date', 'gender', 'nationality', 'id_number', 'profession')
        }),
        ('Contact', {
            'fields': ('address', 'contact')
        }),
        ('Contact d\'urgence', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relation')
        }),
        ('Adhésion', {
            'fields': ('join_date', 'skills', 'specialties')
        }),
        ('Documents', {
            'fields': ('photo', 'id_document')
        }),
    )

@admin.register(MembershipFee)
class MembershipFeeAdmin(admin.ModelAdmin):
    list_display = ['member', 'amount', 'period_month', 'period_year', 'payment_date', 'payment_method']
    list_filter = ['period_year', 'period_month', 'payment_method', 'payment_date']
    search_fields = ['member__membership_number', 'member__user__first_name', 'member__user__last_name', 'receipt_number']
