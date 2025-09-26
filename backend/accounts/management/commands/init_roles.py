"""
Commande pour initialiser les rôles par défaut du système.
Usage: python manage.py init_roles
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from accounts.models import UserRole, CooperativeAccess
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Initialise les rôles par défaut pour le système de coopératives'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Remet à zéro tous les rôles existants',
        )

    def handle(self, *args, **options):
        with transaction.atomic():
            if options['reset']:
                self.stdout.write('Suppression des rôles existants...')
                UserRole.objects.all().delete()

            # Définition des rôles par défaut
            roles_data = [
                {
                    'name': 'admin',
                    'display_name': 'Administrateur',
                    'description': 'Accès complet au système, gestion des utilisateurs et paramètres',
                    'color': '#dc3545',
                    'priority': 1,
                    'permissions': {
                        'can_access_admin': True,
                        'can_view_reports': True,
                        'can_manage_members': True,
                        'can_manage_inventory': True,
                        'can_manage_sales': True,
                        'can_manage_finance': True,
                        'can_validate_transactions': True,
                    }
                },
                {
                    'name': 'manager',
                    'display_name': 'Gestionnaire',
                    'description': 'Gestion opérationnelle de la coopérative, rapports et supervision',
                    'color': '#fd7e14',
                    'priority': 2,
                    'permissions': {
                        'can_access_admin': True,
                        'can_view_reports': True,
                        'can_manage_members': True,
                        'can_manage_inventory': True,
                        'can_manage_sales': True,
                        'can_manage_finance': False,
                        'can_validate_transactions': True,
                    }
                },
                {
                    'name': 'accountant',
                    'display_name': 'Comptable',
                    'description': 'Gestion financière, comptabilité et transactions',
                    'color': '#20c997',
                    'priority': 3,
                    'permissions': {
                        'can_access_admin': False,
                        'can_view_reports': True,
                        'can_manage_members': False,
                        'can_manage_inventory': False,
                        'can_manage_sales': False,
                        'can_manage_finance': True,
                        'can_validate_transactions': True,
                    }
                },
                {
                    'name': 'salesperson',
                    'display_name': 'Vendeur',
                    'description': 'Gestion des ventes et des clients',
                    'color': '#0d6efd',
                    'priority': 4,
                    'permissions': {
                        'can_access_admin': False,
                        'can_view_reports': False,
                        'can_manage_members': False,
                        'can_manage_inventory': False,
                        'can_manage_sales': True,
                        'can_manage_finance': False,
                        'can_validate_transactions': False,
                    }
                },
                {
                    'name': 'stockkeeper',
                    'display_name': 'Gestionnaire de Stock',
                    'description': 'Gestion de l\'inventaire et des mouvements de stock',
                    'color': '#6f42c1',
                    'priority': 5,
                    'permissions': {
                        'can_access_admin': False,
                        'can_view_reports': False,
                        'can_manage_members': False,
                        'can_manage_inventory': True,
                        'can_manage_sales': False,
                        'can_manage_finance': False,
                        'can_validate_transactions': False,
                    }
                },
                {
                    'name': 'member',
                    'display_name': 'Membre',
                    'description': 'Membre de la coopérative avec accès limité',
                    'color': '#198754',
                    'priority': 6,
                    'permissions': {
                        'can_access_admin': False,
                        'can_view_reports': False,
                        'can_manage_members': False,
                        'can_manage_inventory': False,
                        'can_manage_sales': False,
                        'can_manage_finance': False,
                        'can_validate_transactions': False,
                    }
                },
                {
                    'name': 'visitor',
                    'display_name': 'Visiteur',
                    'description': 'Accès minimal au système',
                    'color': '#6c757d',
                    'priority': 7,
                    'permissions': {
                        'can_access_admin': False,
                        'can_view_reports': False,
                        'can_manage_members': False,
                        'can_manage_inventory': False,
                        'can_manage_sales': False,
                        'can_manage_finance': False,
                        'can_validate_transactions': False,
                    }
                },
            ]

            created_count = 0
            updated_count = 0

            for role_data in roles_data:
                permissions = role_data.pop('permissions')
                
                # Fusionner les permissions avec les données de base
                role_defaults = {**role_data, **permissions}
                
                role, created = UserRole.objects.get_or_create(
                    name=role_data['name'],
                    defaults=role_defaults
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Rôle créé: {role.display_name}')
                    )
                else:
                    # Mise à jour des permissions si le rôle existe déjà
                    updated = False
                    for key, value in role_defaults.items():
                        if hasattr(role, key) and getattr(role, key) != value:
                            setattr(role, key, value)
                            updated = True
                    
                    if updated:
                        role.save()
                        updated_count += 1
                        self.stdout.write(
                            self.style.WARNING(f'↻ Rôle mis à jour: {role.display_name}')
                        )
                    else:
                        self.stdout.write(
                            self.style.HTTP_INFO(f'→ Rôle inchangé: {role.display_name}')
                        )

            self.stdout.write('\n' + '='*50)
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Initialisation terminée !\n'
                    f'   - {created_count} rôles créés\n'
                    f'   - {updated_count} rôles mis à jour'
                )
            )
            
            # Mise à jour du profil admin si il existe
            try:
                admin_user = User.objects.filter(is_superuser=True).first()
                if admin_user and hasattr(admin_user, 'profile'):
                    admin_role = UserRole.objects.get(name='admin')
                    admin_user.profile.role = admin_role
                    admin_user.profile.save()
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Rôle admin assigné à {admin_user.username}')
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'⚠ Impossible d\'assigner le rôle admin: {e}')
                )

            self.stdout.write('\n' + self.style.SUCCESS('🎉 Configuration des rôles terminée !'))