#!/usr/bin/env python
"""
Script pour configurer les permissions d'admin.
"""
import os
import sys
import django

# Configuration Django
sys.path.append('/home/marc-goliti/PROJETS/DJANGO/cooperative/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cooperative.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import CooperativeAccess

def setup_admin_permissions():
    """Configure toutes les permissions pour l'admin."""
    
    try:
        # Récupérer l'utilisateur admin
        admin = User.objects.get(username='admin')
        print(f'✅ Admin trouvé: {admin.username}')
        
        # Créer ou récupérer CooperativeAccess
        access, created = CooperativeAccess.objects.get_or_create(
            user=admin,
            defaults={
                # Permissions générales
                'can_view_dashboard': True,
                'can_manage_own_profile': True,
                
                # Membres
                'can_view_members': True,
                'can_add_members': True,
                'can_edit_members': True,
                'can_delete_members': True,
                
                # Inventaire  
                'can_view_inventory': True,
                'can_add_products': True,
                'can_edit_products': True,
                'can_delete_products': True,
                'can_manage_stock': True,
                
                # Ventes
                'can_view_sales': True,
                'can_create_sales': True,
                'can_edit_sales': True,
                'can_delete_sales': True,
                'can_process_payments': True,
                
                # Finances
                'can_view_finances': True,
                'can_create_transactions': True,
                'can_validate_transactions': True,
                'can_manage_accounts': True,
                'can_manage_loans': True,
                
                # Rapports
                'can_view_basic_reports': True,
                'can_view_financial_reports': True,
                'can_export_data': True,
            }
        )
        
        if created:
            print('✅ Permissions créées pour admin')
        else:
            # Mettre à jour toutes les permissions
            access.can_view_dashboard = True
            access.can_manage_own_profile = True
            access.can_view_members = True
            access.can_add_members = True
            access.can_edit_members = True
            access.can_delete_members = True
            access.can_view_inventory = True
            access.can_add_products = True
            access.can_edit_products = True
            access.can_delete_products = True
            access.can_manage_stock = True
            access.can_view_sales = True
            access.can_create_sales = True
            access.can_edit_sales = True
            access.can_delete_sales = True
            access.can_process_payments = True
            access.can_view_finances = True
            access.can_create_transactions = True
            access.can_validate_transactions = True
            access.can_manage_accounts = True
            access.can_manage_loans = True
            access.can_view_basic_reports = True
            access.can_view_financial_reports = True
            access.can_export_data = True
            access.save()
            print('✅ Permissions mises à jour pour admin')
        
        print('🎉 Configuration terminée !')
        
        # Vérification
        print('\n📋 Permissions accordées:')
        print(f'  • Voir ventes: {access.can_view_sales}')
        print(f'  • Créer ventes: {access.can_create_sales}')
        print(f'  • Voir inventaire: {access.can_view_inventory}')
        print(f'  • Voir membres: {access.can_view_members}')
        
        return True
        
    except User.DoesNotExist:
        print('❌ Utilisateur admin non trouvé')
        return False
    except Exception as e:
        print(f'❌ Erreur: {e}')
        return False

if __name__ == '__main__':
    setup_admin_permissions()