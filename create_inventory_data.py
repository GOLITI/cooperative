#!/usr/bin/env python
"""
Script pour créer des données d'inventaire
"""
import os
import sys
import django

# Configuration Django
sys.path.append('/home/marc-goliti/PROJETS/DJANGO/cooperative/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cooperative.settings')
django.setup()

from inventory.models import Category, Unit, Product

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
    
    created_units = 0
    for unit_data in units_data:
        unit, created = Unit.objects.get_or_create(
            name=unit_data['name'],
            defaults=unit_data
        )
        if created:
            created_units += 1
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
    
    created_categories = 0
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            code=cat_data['code'],
            defaults=cat_data
        )
        if created:
            created_categories += 1
            print(f"✅ Catégorie créée: {category.name}")
    
    # Créer les produits
    try:
        kg_unit = Unit.objects.get(abbreviation='kg')
        sac_unit = Unit.objects.get(abbreviation='sac')
        
        products_data = [
            {
                'name': 'Riz Broken',
                'sku': 'RIZ001',
                'category': Category.objects.get(code='CER'),
                'unit': kg_unit,
                'cost_price': 300,
                'selling_price_member': 350,
                'selling_price_non_member': 380,
                'minimum_stock': 100,
                'current_stock': 500,
            },
            {
                'name': 'Riz Local',
                'sku': 'RIZ002', 
                'category': Category.objects.get(code='CER'),
                'unit': kg_unit,
                'cost_price': 400,
                'selling_price_member': 450,
                'selling_price_non_member': 480,
                'minimum_stock': 50,
                'current_stock': 150,
            },
            {
                'name': 'Mil Local',
                'sku': 'MIL001',
                'category': Category.objects.get(code='CER'),
                'unit': sac_unit,
                'cost_price': 25000,
                'selling_price_member': 28000,
                'selling_price_non_member': 30000,
                'minimum_stock': 10,
                'current_stock': 25,
            },
            {
                'name': 'Haricots Niébé',
                'sku': 'HAR001',
                'category': Category.objects.get(code='LEG'),
                'unit': kg_unit,
                'cost_price': 800,
                'selling_price_member': 950,
                'selling_price_non_member': 1000,
                'minimum_stock': 20,
                'current_stock': 80,
            },
            {
                'name': 'Tomates Fraîches',
                'sku': 'TOM001',
                'category': Category.objects.get(code='VEG'),
                'unit': kg_unit,
                'cost_price': 500,
                'selling_price_member': 650,
                'selling_price_non_member': 700,
                'minimum_stock': 50,
                'current_stock': 15,  # Stock faible
            },
            {
                'name': 'Oignons',
                'sku': 'OIG001',
                'category': Category.objects.get(code='VEG'),
                'unit': kg_unit,
                'cost_price': 300,
                'selling_price_member': 400,
                'selling_price_non_member': 420,
                'minimum_stock': 30,
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
                
    except Exception as e:
        print(f"❌ Erreur lors de la création des produits: {e}")
        created_products = 0

    print(f"\n📦 Données d'inventaire créées:")
    print(f"   - Unités: {created_units}")
    print(f"   - Catégories: {created_categories}")
    print(f"   - Produits: {created_products}")
    print(f"   - Total produits: {Product.objects.count()}")

if __name__ == "__main__":
    create_inventory_data()