"""
Classes de permissions personnalisées pour l'API de la coopérative.
"""
from rest_framework import permissions
from django.contrib.auth.models import User


class BaseCooperativePermission(permissions.BasePermission):
    """
    Permission de base pour la coopérative.
    Vérifie les permissions via le modèle CooperativeAccess.
    """
    
    def has_permission(self, request, view):
        """Vérifier si l'utilisateur a l'autorisation générale."""
        if not request.user.is_authenticated:
            return False
        
        # Les superutilisateurs ont toujours accès
        if request.user.is_superuser:
            return True
        
        # Vérifier si l'utilisateur a un profil actif
        if not hasattr(request.user, 'profile') or not request.user.profile.is_active:
            return False
        
        return True
    
    def has_object_permission(self, request, view, obj):
        """Vérifier l'autorisation sur un objet spécifique."""
        return self.has_permission(request, view)


class IsOwnerOrReadOnly(BaseCooperativePermission):
    """
    Permission qui permet seulement au propriétaire d'un objet de le modifier.
    """
    
    def has_object_permission(self, request, view, obj):
        # Permissions de lecture pour tous les utilisateurs authentifiés
        if request.method in permissions.SAFE_METHODS:
            return super().has_permission(request, view)
        
        # Permissions d'écriture seulement pour le propriétaire
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        elif isinstance(obj, User):
            return obj == request.user
        
        return False


class CanManageUsers(BaseCooperativePermission):
    """Permission pour gérer les utilisateurs."""
    
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        
        access = getattr(request.user, 'cooperative_access', None)
        return access and access.can_manage_users


class CanViewMembers(BaseCooperativePermission):
    """Permission pour voir les membres."""
    
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        
        access = getattr(request.user, 'cooperative_access', None)
        return access and access.can_view_members


class CanManageMembers(BaseCooperativePermission):
    """Permission pour gérer les membres."""
    
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        
        access = getattr(request.user, 'cooperative_access', None)
        
        if request.method in permissions.SAFE_METHODS:
            return access and access.can_view_members
        elif request.method == 'POST':
            return access and access.can_add_members
        elif request.method in ['PUT', 'PATCH']:
            return access and access.can_edit_members
        elif request.method == 'DELETE':
            return access and access.can_delete_members
        
        return False


class CanViewInventory(BaseCooperativePermission):
    """Permission pour voir l'inventaire."""
    
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        
        access = getattr(request.user, 'cooperative_access', None)
        return access and access.can_view_inventory


class CanManageInventory(BaseCooperativePermission):
    """Permission pour gérer l'inventaire."""
    
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        
        access = getattr(request.user, 'cooperative_access', None)
        
        if request.method in permissions.SAFE_METHODS:
            return access and access.can_view_inventory
        elif request.method == 'POST':
            return access and access.can_add_products
        elif request.method in ['PUT', 'PATCH']:
            return access and access.can_edit_products
        elif request.method == 'DELETE':
            return access and access.can_delete_products
        
        return False


class CanManageStock(BaseCooperativePermission):
    """Permission pour gérer le stock."""
    
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        
        access = getattr(request.user, 'cooperative_access', None)
        return access and access.can_manage_stock


class CanViewSales(BaseCooperativePermission):
    """Permission pour voir les ventes."""
    
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        
        access = getattr(request.user, 'cooperative_access', None)
        return access and access.can_view_sales


class CanManageSales(BaseCooperativePermission):
    """Permission pour gérer les ventes."""
    
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        
        access = getattr(request.user, 'cooperative_access', None)
        
        if request.method in permissions.SAFE_METHODS:
            return access and access.can_view_sales
        elif request.method == 'POST':
            return access and access.can_create_sales
        elif request.method in ['PUT', 'PATCH']:
            return access and access.can_edit_sales
        elif request.method == 'DELETE':
            return access and access.can_delete_sales
        
        return False


class CanProcessPayments(BaseCooperativePermission):
    """Permission pour traiter les paiements."""
    
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        
        access = getattr(request.user, 'cooperative_access', None)
        return access and access.can_process_payments


class CanViewFinances(BaseCooperativePermission):
    """Permission pour voir les finances."""
    
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        
        access = getattr(request.user, 'cooperative_access', None)
        return access and access.can_view_finances


class CanManageFinances(BaseCooperativePermission):
    """Permission pour gérer les finances."""
    
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        
        access = getattr(request.user, 'cooperative_access', None)
        
        if request.method in permissions.SAFE_METHODS:
            return access and access.can_view_finances
        elif request.method == 'POST':
            return access and access.can_create_transactions
        elif request.method in ['PUT', 'PATCH']:
            return access and (access.can_create_transactions or access.can_validate_transactions)
        elif request.method == 'DELETE':
            return access and access.can_validate_transactions
        
        return False


class CanValidateTransactions(BaseCooperativePermission):
    """Permission pour valider les transactions."""
    
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        
        access = getattr(request.user, 'cooperative_access', None)
        return access and access.can_validate_transactions


class CanManageAccounts(BaseCooperativePermission):
    """Permission pour gérer les comptes financiers."""
    
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        
        access = getattr(request.user, 'cooperative_access', None)
        return access and access.can_manage_accounts


class CanManageLoans(BaseCooperativePermission):
    """Permission pour gérer les prêts."""
    
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        
        access = getattr(request.user, 'cooperative_access', None)
        return access and access.can_manage_loans


class CanViewReports(BaseCooperativePermission):
    """Permission pour voir les rapports."""
    
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        
        access = getattr(request.user, 'cooperative_access', None)
        return access and (access.can_view_basic_reports or access.can_view_financial_reports)


class CanViewFinancialReports(BaseCooperativePermission):
    """Permission pour voir les rapports financiers."""
    
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        
        access = getattr(request.user, 'cooperative_access', None)
        return access and access.can_view_financial_reports


class CanExportData(BaseCooperativePermission):
    """Permission pour exporter des données."""
    
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        
        access = getattr(request.user, 'cooperative_access', None)
        return access and access.can_export_data


class CanViewLogs(BaseCooperativePermission):
    """Permission pour voir les logs."""
    
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        
        access = getattr(request.user, 'cooperative_access', None)
        return access and access.can_view_logs


class CanBackupData(BaseCooperativePermission):
    """Permission pour sauvegarder les données."""
    
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        
        access = getattr(request.user, 'cooperative_access', None)
        return access and access.can_backup_data