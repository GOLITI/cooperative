"""
Signaux pour la gestion automatique des profils et accès utilisateurs.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, CooperativeAccess, UserRole


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Créer automatiquement un profil utilisateur à la création.
    """
    if created:
        # Assigner le rôle membre par défaut
        default_role = UserRole.objects.filter(name='member').first()
        
        UserProfile.objects.create(
            user=instance,
            role=default_role
        )


@receiver(post_save, sender=User)
def create_user_cooperative_access(sender, instance, created, **kwargs):
    """
    Créer automatiquement les accès coopérative à la création.
    """
    if created:
        CooperativeAccess.objects.create(
            user=instance,
            can_view_dashboard=True,
            can_manage_own_profile=True
        )


@receiver(post_save, sender=UserProfile)
def update_cooperative_access_on_role_change(sender, instance, **kwargs):
    """
    Mettre à jour les accès coopérative selon le rôle.
    """
    if instance.role and hasattr(instance.user, 'cooperative_access'):
        access = instance.user.cooperative_access
        role = instance.role
        
        # Permissions basées sur le rôle
        permission_map = {
            'admin': {
                'can_view_dashboard': True,
                'can_manage_own_profile': True,
                'can_view_members': True,
                'can_add_members': True,
                'can_edit_members': True,
                'can_delete_members': True,
                'can_view_inventory': True,
                'can_add_products': True,
                'can_edit_products': True,
                'can_delete_products': True,
                'can_manage_stock': True,
                'can_view_sales': True,
                'can_create_sales': True,
                'can_edit_sales': True,
                'can_delete_sales': True,
                'can_process_payments': True,
                'can_view_finances': True,
                'can_create_transactions': True,
                'can_validate_transactions': True,
                'can_manage_accounts': True,
                'can_manage_loans': True,
                'can_view_basic_reports': True,
                'can_view_financial_reports': True,
                'can_export_data': True,
                'can_manage_users': True,
                'can_manage_permissions': True,
                'can_view_logs': True,
                'can_backup_data': True,
            },
            'manager': {
                'can_view_dashboard': True,
                'can_manage_own_profile': True,
                'can_view_members': True,
                'can_add_members': True,
                'can_edit_members': True,
                'can_delete_members': False,
                'can_view_inventory': True,
                'can_add_products': True,
                'can_edit_products': True,
                'can_delete_products': False,
                'can_manage_stock': True,
                'can_view_sales': True,
                'can_create_sales': True,
                'can_edit_sales': True,
                'can_delete_sales': False,
                'can_process_payments': True,
                'can_view_finances': True,
                'can_create_transactions': False,
                'can_validate_transactions': True,
                'can_manage_accounts': False,
                'can_manage_loans': True,
                'can_view_basic_reports': True,
                'can_view_financial_reports': True,
                'can_export_data': True,
                'can_manage_users': False,
                'can_manage_permissions': False,
                'can_view_logs': False,
                'can_backup_data': False,
            },
            'accountant': {
                'can_view_dashboard': True,
                'can_manage_own_profile': True,
                'can_view_members': True,
                'can_add_members': False,
                'can_edit_members': False,
                'can_delete_members': False,
                'can_view_inventory': False,
                'can_add_products': False,
                'can_edit_products': False,
                'can_delete_products': False,
                'can_manage_stock': False,
                'can_view_sales': True,
                'can_create_sales': False,
                'can_edit_sales': False,
                'can_delete_sales': False,
                'can_process_payments': True,
                'can_view_finances': True,
                'can_create_transactions': True,
                'can_validate_transactions': True,
                'can_manage_accounts': True,
                'can_manage_loans': True,
                'can_view_basic_reports': True,
                'can_view_financial_reports': True,
                'can_export_data': True,
                'can_manage_users': False,
                'can_manage_permissions': False,
                'can_view_logs': False,
                'can_backup_data': False,
            },
            'salesperson': {
                'can_view_dashboard': True,
                'can_manage_own_profile': True,
                'can_view_members': True,
                'can_add_members': True,
                'can_edit_members': False,
                'can_delete_members': False,
                'can_view_inventory': True,
                'can_add_products': False,
                'can_edit_products': False,
                'can_delete_products': False,
                'can_manage_stock': False,
                'can_view_sales': True,
                'can_create_sales': True,
                'can_edit_sales': True,
                'can_delete_sales': False,
                'can_process_payments': True,
                'can_view_finances': False,
                'can_create_transactions': False,
                'can_validate_transactions': False,
                'can_manage_accounts': False,
                'can_manage_loans': False,
                'can_view_basic_reports': True,
                'can_view_financial_reports': False,
                'can_export_data': False,
                'can_manage_users': False,
                'can_manage_permissions': False,
                'can_view_logs': False,
                'can_backup_data': False,
            },
            'stockkeeper': {
                'can_view_dashboard': True,
                'can_manage_own_profile': True,
                'can_view_members': False,
                'can_add_members': False,
                'can_edit_members': False,
                'can_delete_members': False,
                'can_view_inventory': True,
                'can_add_products': True,
                'can_edit_products': True,
                'can_delete_products': False,
                'can_manage_stock': True,
                'can_view_sales': True,
                'can_create_sales': False,
                'can_edit_sales': False,
                'can_delete_sales': False,
                'can_process_payments': False,
                'can_view_finances': False,
                'can_create_transactions': False,
                'can_validate_transactions': False,
                'can_manage_accounts': False,
                'can_manage_loans': False,
                'can_view_basic_reports': True,
                'can_view_financial_reports': False,
                'can_export_data': False,
                'can_manage_users': False,
                'can_manage_permissions': False,
                'can_view_logs': False,
                'can_backup_data': False,
            },
            'member': {
                'can_view_dashboard': True,
                'can_manage_own_profile': True,
                'can_view_members': False,
                'can_add_members': False,
                'can_edit_members': False,
                'can_delete_members': False,
                'can_view_inventory': False,
                'can_add_products': False,
                'can_edit_products': False,
                'can_delete_products': False,
                'can_manage_stock': False,
                'can_view_sales': False,
                'can_create_sales': False,
                'can_edit_sales': False,
                'can_delete_sales': False,
                'can_process_payments': False,
                'can_view_finances': False,
                'can_create_transactions': False,
                'can_validate_transactions': False,
                'can_manage_accounts': False,
                'can_manage_loans': False,
                'can_view_basic_reports': False,
                'can_view_financial_reports': False,
                'can_export_data': False,
                'can_manage_users': False,
                'can_manage_permissions': False,
                'can_view_logs': False,
                'can_backup_data': False,
            },
            'visitor': {
                'can_view_dashboard': False,
                'can_manage_own_profile': True,
                'can_view_members': False,
                'can_add_members': False,
                'can_edit_members': False,
                'can_delete_members': False,
                'can_view_inventory': False,
                'can_add_products': False,
                'can_edit_products': False,
                'can_delete_products': False,
                'can_manage_stock': False,
                'can_view_sales': False,
                'can_create_sales': False,
                'can_edit_sales': False,
                'can_delete_sales': False,
                'can_process_payments': False,
                'can_view_finances': False,
                'can_create_transactions': False,
                'can_validate_transactions': False,
                'can_manage_accounts': False,
                'can_manage_loans': False,
                'can_view_basic_reports': False,
                'can_view_financial_reports': False,
                'can_export_data': False,
                'can_manage_users': False,
                'can_manage_permissions': False,
                'can_view_logs': False,
                'can_backup_data': False,
            }
        }
        
        # Appliquer les permissions selon le rôle
        permissions = permission_map.get(role.name, permission_map['member'])
        
        for permission, value in permissions.items():
            if hasattr(access, permission):
                setattr(access, permission, value)
        
        access.save()