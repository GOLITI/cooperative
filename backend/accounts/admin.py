"""
Administration des comptes utilisateurs et permissions.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import (
    UserRole, UserProfile, PermissionLog, 
    LoginAttempt, SessionActivity, CooperativeAccess
)


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = [
        'display_name', 'name', 'colored_badge', 'priority', 
        'can_access_admin', 'can_manage_finance', 'is_active'
    ]
    list_filter = [
        'is_active', 'can_access_admin', 'can_manage_finance',
        'can_manage_members', 'can_manage_inventory'
    ]
    search_fields = ['name', 'display_name', 'description']
    ordering = ['priority', 'name']
    
    fieldsets = (
        (_('Informations générales'), {
            'fields': ('name', 'display_name', 'description', 'color', 'priority', 'is_active')
        }),
        (_('Permissions globales'), {
            'fields': (
                'can_access_admin', 'can_view_reports',
                'can_manage_members', 'can_manage_inventory',
                'can_manage_sales', 'can_manage_finance',
                'can_validate_transactions'
            )
        }),
    )
    
    def colored_badge(self, obj):
        """Badge coloré pour le rôle."""
        return format_html(
            '<span style="color: {}; font-weight: bold;">● {}</span>',
            obj.color,
            obj.display_name
        )
    colored_badge.short_description = _('Rôle')


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = _('Profil')
    
    fieldsets = (
        (_('Rôle et Membre'), {
            'fields': ('role', 'member')
        }),
        (_('Informations personnelles'), {
            'fields': ('phone', 'avatar', 'bio')
        }),
        (_('Préférences'), {
            'fields': ('language', 'theme', 'timezone')
        }),
        (_('Notifications'), {
            'fields': ('email_notifications', 'sms_notifications')
        }),
        (_('Sécurité'), {
            'fields': ('two_factor_enabled', 'last_password_change', 'password_expires_at')
        }),
    )


class CooperativeAccessInline(admin.StackedInline):
    model = CooperativeAccess
    can_delete = False
    verbose_name_plural = _('Accès Coopérative')
    
    fieldsets = (
        (_('Accès général'), {
            'fields': ('can_view_dashboard', 'can_manage_own_profile')
        }),
        (_('Gestion des membres'), {
            'fields': (
                'can_view_members', 'can_add_members',
                'can_edit_members', 'can_delete_members'
            )
        }),
        (_('Gestion de l\'inventaire'), {
            'fields': (
                'can_view_inventory', 'can_add_products',
                'can_edit_products', 'can_delete_products', 'can_manage_stock'
            )
        }),
        (_('Gestion des ventes'), {
            'fields': (
                'can_view_sales', 'can_create_sales',
                'can_edit_sales', 'can_delete_sales', 'can_process_payments'
            )
        }),
        (_('Gestion financière'), {
            'fields': (
                'can_view_finances', 'can_create_transactions',
                'can_validate_transactions', 'can_manage_accounts', 'can_manage_loans'
            )
        }),
        (_('Rapports et administration'), {
            'fields': (
                'can_view_basic_reports', 'can_view_financial_reports',
                'can_export_data', 'can_manage_users', 'can_manage_permissions',
                'can_view_logs', 'can_backup_data'
            )
        }),
    )


# Étendre l'admin User existant
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline, CooperativeAccessInline)
    
    def get_inline_instances(self, request, obj=None):
        """Créer les profils manquants."""
        if obj:
            # Créer le profil s'il n'existe pas
            if not hasattr(obj, 'profile'):
                UserProfile.objects.get_or_create(user=obj)
            # Créer les accès s'ils n'existent pas
            if not hasattr(obj, 'cooperative_access'):
                CooperativeAccess.objects.get_or_create(user=obj)
        
        return super().get_inline_instances(request, obj)


# Réenregistrer le modèle User avec notre admin étendu
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'role', 'member', 'display_name', 
        'language', 'theme', 'two_factor_enabled', 'is_active'
    ]
    list_filter = [
        'role', 'language', 'theme', 'two_factor_enabled',
        'email_notifications', 'is_active'
    ]
    search_fields = [
        'user__username', 'user__first_name', 'user__last_name',
        'user__email', 'phone'
    ]
    raw_id_fields = ['user', 'member']
    
    fieldsets = (
        (_('Utilisateur et Rôle'), {
            'fields': ('user', 'role', 'member')
        }),
        (_('Informations personnelles'), {
            'fields': ('phone', 'avatar', 'bio')
        }),
        (_('Préférences'), {
            'fields': ('language', 'theme', 'timezone')
        }),
        (_('Notifications'), {
            'fields': ('email_notifications', 'sms_notifications')
        }),
        (_('Sécurité'), {
            'fields': ('two_factor_enabled', 'last_password_change', 'password_expires_at')
        }),
        (_('Statistiques'), {
            'fields': ('last_login_ip', 'login_count'),
            'classes': ('collapse',)
        }),
        (_('Système'), {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']


@admin.register(PermissionLog)
class PermissionLogAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'permission_name', 'action', 
        'changed_by', 'created_at', 'ip_address'
    ]
    list_filter = ['action', 'created_at']
    search_fields = [
        'user__username', 'permission_name', 
        'changed_by__username', 'ip_address'
    ]
    readonly_fields = ['created_at']
    raw_id_fields = ['user', 'changed_by']
    
    def has_add_permission(self, request):
        return False  # Lecture seule
    
    def has_change_permission(self, request, obj=None):
        return False  # Lecture seule


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = [
        'username', 'success', 'ip_address', 
        'created_at', 'failure_reason'
    ]
    list_filter = ['success', 'created_at']
    search_fields = ['username', 'ip_address', 'failure_reason']
    readonly_fields = ['created_at']
    
    def has_add_permission(self, request):
        return False  # Lecture seule
    
    def has_change_permission(self, request, obj=None):
        return False  # Lecture seule


@admin.register(SessionActivity)
class SessionActivityAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'ip_address', 'login_time', 
        'logout_time', 'is_active', 'country'
    ]
    list_filter = ['login_time', 'logout_time', 'country']
    search_fields = ['user__username', 'ip_address', 'country', 'city']
    readonly_fields = ['login_time', 'logout_time', 'last_activity']
    raw_id_fields = ['user']
    
    def has_add_permission(self, request):
        return False  # Lecture seule


@admin.register(CooperativeAccess)
class CooperativeAccessAdmin(admin.ModelAdmin):
    list_display = ['user', 'can_view_dashboard', 'can_view_members', 'can_view_sales']
    list_filter = [
        'can_view_dashboard', 'can_view_members', 
        'can_view_inventory', 'can_view_sales', 'can_view_finances'
    ]
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    raw_id_fields = ['user']
    
    fieldsets = (
        (_('Utilisateur'), {
            'fields': ('user',)
        }),
        (_('Accès général'), {
            'fields': ('can_view_dashboard', 'can_manage_own_profile')
        }),
        (_('Gestion des membres'), {
            'fields': (
                'can_view_members', 'can_add_members',
                'can_edit_members', 'can_delete_members'
            )
        }),
        (_('Gestion de l\'inventaire'), {
            'fields': (
                'can_view_inventory', 'can_add_products',
                'can_edit_products', 'can_delete_products', 'can_manage_stock'
            )
        }),
        (_('Gestion des ventes'), {
            'fields': (
                'can_view_sales', 'can_create_sales',
                'can_edit_sales', 'can_delete_sales', 'can_process_payments'
            )
        }),
        (_('Gestion financière'), {
            'fields': (
                'can_view_finances', 'can_create_transactions',
                'can_validate_transactions', 'can_manage_accounts', 'can_manage_loans'
            )
        }),
        (_('Rapports et administration'), {
            'fields': (
                'can_view_basic_reports', 'can_view_financial_reports',
                'can_export_data', 'can_manage_users', 'can_manage_permissions',
                'can_view_logs', 'can_backup_data'
            )
        }),
    )
