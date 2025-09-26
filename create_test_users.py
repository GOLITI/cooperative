#!/usr/bin/env python3
"""
Script pour créer/mettre à jour les utilisateurs de test pour la coopérative
"""
import os
import sys
import django

# Configuration Django
sys.path.append('/home/marc-goliti/PROJETS/DJANGO/cooperative/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cooperative.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

def create_test_users():
    """Créer ou mettre à jour les utilisateurs de test"""
    
    # Utilisateur admin
    try:
        admin = User.objects.get(username='admin')
        created = False
    except User.DoesNotExist:
        admin = User.objects.create_user(
            username='admin',
            email='admin@cooperative.local',
            password='admin',
            first_name='Admin',
            last_name='Coopérative'
        )
        admin.is_staff = True
        admin.is_superuser = True
        admin.save()
        created = True
    
    # S'assurer que le mot de passe est correct
    admin.set_password('admin')
    admin.save()
    
    # Créer ou récupérer le token pour admin
    token_admin, token_created = Token.objects.get_or_create(user=admin)
    
    print(f"✅ Utilisateur admin {'créé' if created else 'mis à jour'}")
    print(f"   Email: {admin.email}")
    print(f"   Token: {token_admin.key}")
    
    # Utilisateur demo
    try:
        demo = User.objects.get(username='demo')
        created = False
    except User.DoesNotExist:
        demo = User.objects.create_user(
            username='demo',
            email='demo@cooperative.local',
            password='demo123',
            first_name='Demo',
            last_name='User'
        )
        created = True
    
    # S'assurer que le mot de passe est correct
    demo.set_password('demo123')
    demo.save()
    
    # Créer ou récupérer le token pour demo
    token_demo, token_created = Token.objects.get_or_create(user=demo)
    
    print(f"✅ Utilisateur demo {'créé' if created else 'mis à jour'}")
    print(f"   Email: {demo.email}")
    print(f"   Token: {token_demo.key}")
    
    # Afficher tous les utilisateurs
    print("\n📋 Utilisateurs disponibles:")
    for user in User.objects.all():
        if user.username != 'AnonymousUser':
            print(f"   - {user.username}: {user.email} (staff: {user.is_staff})")

def test_authentication():
    """Tester l'authentification avec les comptes créés"""
    from django.contrib.auth import authenticate
    
    print("\n🔐 Test d'authentification:")
    
    # Test admin
    admin_user = authenticate(username='admin', password='admin')
    if admin_user:
        print("   ✅ admin/admin: OK")
    else:
        print("   ❌ admin/admin: ÉCHEC")
    
    # Test demo
    demo_user = authenticate(username='demo', password='demo123')
    if demo_user:
        print("   ✅ demo/demo123: OK")
    else:
        print("   ❌ demo/demo123: ÉCHEC")

if __name__ == '__main__':
    print("🚀 Configuration des utilisateurs de test pour la coopérative...")
    create_test_users()
    test_authentication()
    print("\n✨ Configuration terminée!")