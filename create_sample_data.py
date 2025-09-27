#!/usr/bin/env python
"""
Script pour créer des données de test pour le système de coopérative
"""
import os
import sys
import django
from datetime import date, datetime, timedelta
    # 3. Créer les données d'inventaire
    create_inventory_data()

    print(f"🎉 Données créées avec succès!")
    print(f"📊 Résumé:")
    print(f"   - Types d'adhésion: {len(membership_types)}")
    print(f"   - Nouveaux membres: {created_members}")
    print(f"   - Total membres: {Member.objects.count()}")

def create_inventory_data():
    """Créer les données d'inventaire"""
    print("📦 Création des données d'inventaire...")
    
    # Créer les unités de mesure
    units_data = [
        {'name': 'Kilogramme', 'abbreviation': 'kg', 'unit_type': 'weight'},
        {'name': 'Gramme', 'abbreviation': 'g', 'unit_type': 'weight'},
        {'name': 'Litre', 'abbreviation': 'l', 'unit_type': 'volume'},
        {'name': 'Unité', 'abbreviation': 'u', 'unit_type': 'unit'},
        {'name': 'Sac', 'abbreviation': 'sac', 'unit_type': 'unit'},
    ]
    
    for unit_data in units_data:
        unit, created = Unit.objects.get_or_create(
            name=unit_data['name'],
            defaults=unit_data
        )
        if created:
            print(f"✅ Unité créée: {unit.name}")
    
    # Créer les catégories
    categories_data = [
        {'name': 'Céréales', 'code': 'CER', 'description': 'Riz, mil, sorgho, maïs'},
        {'name': 'Légumineuses', 'code': 'LEG', 'description': 'Haricots, pois, lentilles'},
        {'name': 'Tubercules', 'code': 'TUB', 'description': 'Patates douces, manioc, ignames'},
        {'name': 'Légumes', 'code': 'VEG', 'description': 'Tomates, oignons, choux'},
        {'name': 'Fruits', 'code': 'FRU', 'description': 'Mangues, oranges, bananes'},
        {'name': 'Épices', 'code': 'EPI', 'description': 'Piment, gingembre, ail'},
    ]
    
    created_categories = []
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            code=cat_data['code'],
            defaults=cat_data
        )
        created_categories.append(category)
        if created:
            print(f"✅ Catégorie créée: {category.name}")
    
    # Créer les produits
    kg_unit = Unit.objects.get(abbreviation='kg')
    sac_unit = Unit.objects.get(abbreviation='sac')
    unit_unit = Unit.objects.get(abbreviation='u')
    
    products_data = [
        {
            'name': 'Riz Broken',
            'sku': 'RIZ001',
            'category': Category.objects.get(code='CER'),
            'unit': kg_unit,
            'purchase_price': 300,
            'sale_price': 350,
            'min_stock_level': 100,
            'current_stock': 500,
        },
        {
            'name': 'Riz Local',
            'sku': 'RIZ002', 
            'category': Category.objects.get(code='CER'),
            'unit': kg_unit,
            'purchase_price': 400,
            'sale_price': 450,
            'min_stock_level': 50,
            'current_stock': 150,
        },
        {
            'name': 'Mil Local',
            'sku': 'MIL001',
            'category': Category.objects.get(code='CER'),
            'unit': sac_unit,
            'purchase_price': 25000,
            'sale_price': 28000,
            'min_stock_level': 10,
            'current_stock': 25,
        },
        {
            'name': 'Haricots Niébé',
            'sku': 'HAR001',
            'category': Category.objects.get(code='LEG'),
            'unit': kg_unit,
            'purchase_price': 800,
            'sale_price': 950,
            'min_stock_level': 20,
            'current_stock': 80,
        },
        {
            'name': 'Tomates Fraîches',
            'sku': 'TOM001',
            'category': Category.objects.get(code='VEG'),
            'unit': kg_unit,
            'purchase_price': 500,
            'sale_price': 650,
            'min_stock_level': 50,
            'current_stock': 15,  # Stock faible
        },
        {
            'name': 'Oignons',
            'sku': 'OIG001',
            'category': Category.objects.get(code='VEG'),
            'unit': kg_unit,
            'purchase_price': 300,
            'sale_price': 400,
            'min_stock_level': 30,
            'current_stock': 0,  # Rupture de stock
        }
    ]
    
    created_products = 0
    for prod_data in products_data:
        try:
            product, created = Product.objects.get_or_create(
                sku=prod_data['sku'],
                defaults=prod_data
            )
            if created:
                created_products += 1
                print(f"✅ Produit créé: {product.name} ({product.sku})")
        except Exception as e:
            print(f"❌ Erreur lors de la création du produit {prod_data['name']}: {e}")
    
    print(f"📦 Inventaire créé: {created_products} produits")

if __name__ == "__main__":
    create_sample_data()andom

# Configuration Django
sys.path.append('/home/marc-goliti/PROJETS/DJANGO/cooperative/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cooperative.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Address, Contact
from members.models import MembershipType, Member
from inventory.models import Category, Unit, Product

def create_sample_data():
    """Créer des données d'exemple"""
    print("🚀 Création des données d'exemple...")
    
    # 1. Créer des types d'adhésion
    membership_types_data = [
        {
            'name': 'Membre Standard',
            'description': 'Adhésion de base avec accès aux services essentiels',
            'monthly_fee': 5000.00,
            'benefits': ['Achat de produits', 'Formation de base', 'Assemblées générales']
        },
        {
            'name': 'Membre Premium', 
            'description': 'Adhésion complète avec tous les avantages',
            'monthly_fee': 10000.00,
            'benefits': ['Tous les services standard', 'Crédit privilégié', 'Formation avancée', 'Dividendes prioritaires']
        },
        {
            'name': 'Membre Jeune',
            'description': 'Tarif réduit pour les jeunes agriculteurs (18-30 ans)',
            'monthly_fee': 2500.00,
            'benefits': ['Services essentiels', 'Mentorat', 'Formation jeunes']
        }
    ]
    
    membership_types = []
    for type_data in membership_types_data:
        membership_type, created = MembershipType.objects.get_or_create(
            name=type_data['name'],
            defaults=type_data
        )
        membership_types.append(membership_type)
        if created:
            print(f"✅ Type d'adhésion créé: {membership_type.name}")
    
    # 2. Créer des membres d'exemple
    members_data = [
        {
            'first_name': 'Amadou',
            'last_name': 'Diallo',
            'email': 'amadou.diallo@email.com',
            'birth_date': date(1985, 3, 15),
            'gender': 'M',
            'profession': 'Agriculteur',
            'phone': '77 123 45 67',
            'village': 'Thies',
            'region': 'Thiès'
        },
        {
            'first_name': 'Fatou',
            'last_name': 'Sall',
            'email': 'fatou.sall@email.com',
            'birth_date': date(1990, 7, 22),
            'gender': 'F', 
            'profession': 'Maraîchère',
            'phone': '78 234 56 78',
            'village': 'Kaolack',
            'region': 'Kaolack'
        },
        {
            'first_name': 'Ousmane',
            'last_name': 'Ba',
            'email': 'ousmane.ba@email.com',
            'birth_date': date(1982, 12, 8),
            'gender': 'M',
            'profession': 'Éleveur',
            'phone': '76 345 67 89',
            'village': 'Saint-Louis',
            'region': 'Saint-Louis'
        },
        {
            'first_name': 'Aissatou',
            'last_name': 'Ndiaye',
            'email': 'aissatou.ndiaye@email.com',
            'birth_date': date(1995, 5, 18),
            'gender': 'F',
            'profession': 'Transformatrice',
            'phone': '70 456 78 90',
            'village': 'Ziguinchor',
            'region': 'Ziguinchor'
        },
        {
            'first_name': 'Mamadou',
            'last_name': 'Fall',
            'email': 'mamadou.fall@email.com',
            'birth_date': date(1988, 9, 3),
            'gender': 'M',
            'profession': 'Agriculteur',
            'phone': '77 567 89 01',
            'village': 'Diourbel',
            'region': 'Diourbel'
        }
    ]
    
    created_members = 0
    for i, member_data in enumerate(members_data):
        try:
            # Créer l'utilisateur
            username = f"{member_data['first_name'].lower()}.{member_data['last_name'].lower()}"
            user, user_created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': member_data['first_name'],
                    'last_name': member_data['last_name'],
                    'email': member_data['email'],
                    'is_active': True
                }
            )
            
            if user_created:
                user.set_password('password123')  # Mot de passe par défaut
                user.save()
            
            # Créer l'adresse
            address, addr_created = Address.objects.get_or_create(
                city=member_data['village'],
                defaults={
                    'street': f"Quartier {member_data['village']}",
                    'region': member_data['region'],
                    'country': 'Sénégal'
                }
            )
            
            # Créer le contact
            contact, contact_created = Contact.objects.get_or_create(
                phone_primary=member_data['phone'],
                defaults={
                    'email': member_data['email']
                }
            )
            
            # Vérifier si le membre existe déjà
            if not Member.objects.filter(user=user).exists():
                # Créer le membre
                membership_type = random.choice(membership_types)
                join_date = date.today() - timedelta(days=random.randint(30, 365))
                
                member = Member.objects.create(
                    user=user,
                    membership_number=f"COOP{2025}{i+1:04d}",
                    membership_type=membership_type,
                    birth_date=member_data['birth_date'],
                    gender=member_data['gender'],
                    nationality="Sénégalaise",
                    id_number=f"1234567890{i:02d}",
                    profession=member_data['profession'],
                    address=address,
                    contact=contact,
                    emergency_contact_name=f"Famille {member_data['last_name']}",
                    emergency_contact_phone="77 000 00 00",
                    emergency_contact_relation="Famille",
                    join_date=join_date,
                    status='active'
                )
                created_members += 1
                print(f"✅ Membre créé: {member.user.get_full_name()} - {member.membership_number}")
            
        except Exception as e:
            print(f"❌ Erreur lors de la création du membre {member_data['first_name']}: {e}")
    
    print(f"\n🎉 Données créées avec succès!")
    print(f"📊 Résumé:")
    print(f"   - Types d'adhésion: {len(membership_types)}")
    print(f"   - Nouveaux membres: {created_members}")
    print(f"   - Total membres: {Member.objects.count()}")

if __name__ == "__main__":
    create_sample_data()