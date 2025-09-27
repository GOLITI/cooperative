#!/usr/bin/env python3

"""
Script pour créer des données de test pour le module ventes/clients
Exécuter avec: python manage.py shell < create_sales_data.py
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal
import random

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cooperative.settings')
django.setup()

from sales.models import Customer, Sale, SaleItem
from inventory.models import Product
from members.models import Member

def create_customers():
    """Créer des clients de test"""
    print("Création des clients...")
    
    customers_data = [
        {
            'name': 'Aliou Diallo',
            'customer_type': 'individual',
            'phone': '+221 77 123 4567',
            'email': 'aliou.diallo@email.com',
            'address': 'Dakar, Sénégal',
            'credit_limit': Decimal('500000.00')
        },
        {
            'name': 'Fatou Sall',
            'customer_type': 'individual', 
            'phone': '+221 76 987 6543',
            'email': 'fatou.sall@email.com',
            'address': 'Thiès, Sénégal',
            'credit_limit': Decimal('300000.00')
        },
        {
            'name': 'Coopérative Agricole de Kaolack',
            'customer_type': 'organization',
            'phone': '+221 77 555 1234',
            'email': 'contact@coop-kaolack.sn',
            'address': 'Kaolack, Sénégal',
            'credit_limit': Decimal('2000000.00')
        },
        {
            'name': 'Mamadou Ba',
            'customer_type': 'individual',
            'phone': '+221 78 222 3333',
            'email': 'mamadou.ba@email.com',
            'address': 'Saint-Louis, Sénégal',
            'credit_limit': Decimal('750000.00')
        }
    ]
    
    # Vérifier si des membres peuvent être convertis en clients
    members = Member.objects.all()[:2]  # Prendre 2 membres existants
    
    for member in members:
        customers_data.append({
            'name': f'{member.first_name} {member.last_name}',
            'customer_type': 'member',
            'phone': member.phone,
            'email': member.email,
            'address': member.address,
            'credit_limit': Decimal('1000000.00'),  # Limite plus élevée pour les membres
            'member': member
        })
    
    created_customers = []
    for data in customers_data:
        customer, created = Customer.objects.get_or_create(
            name=data['name'],
            defaults=data
        )
        if created:
            print(f"✓ Client créé: {customer.name}")
        else:
            print(f"- Client existant: {customer.name}")
        created_customers.append(customer)
    
    return created_customers

def create_sales(customers):
    """Créer des ventes de test"""
    print("\nCréation des ventes...")
    
    # Récupérer les produits existants
    products = list(Product.objects.all())
    if not products:
        print("⚠️ Aucun produit trouvé. Exécutez d'abord le script de création d'inventaire.")
        return []
    
    created_sales = []
    
    # Créer des ventes sur les 30 derniers jours
    for i in range(15):  # 15 ventes de test
        # Date aléatoire dans les 30 derniers jours
        days_ago = random.randint(0, 30)
        sale_date = datetime.now().date() - timedelta(days=days_ago)
        
        # Client aléatoire
        customer = random.choice(customers)
        
        # Créer la vente
        sale = Sale.objects.create(
            customer=customer,
            sale_date=sale_date,
            status=random.choice(['completed', 'pending', 'completed', 'completed']),  # Majorité complétées
            notes=f"Vente #{i+1} - {customer.name}"
        )
        
        # Ajouter des articles à la vente (1-4 produits par vente)
        num_items = random.randint(1, 4)
        selected_products = random.sample(products, min(num_items, len(products)))
        
        total_amount = Decimal('0.00')
        
        for product in selected_products:
            quantity = random.randint(1, 10)
            unit_price = product.selling_price
            total_price = unit_price * quantity
            
            SaleItem.objects.create(
                sale=sale,
                product=product,
                quantity=quantity,
                unit_price=unit_price,
                total_price=total_price
            )
            
            total_amount += total_price
        
        # Mettre à jour le montant total de la vente
        sale.total_amount = total_amount
        sale.save()
        
        print(f"✓ Vente créée: {sale.sale_number} - {customer.name} - {total_amount} FCFA")
        created_sales.append(sale)
    
    return created_sales

def main():
    """Fonction principale"""
    print("=== Création de données de test pour les ventes ===\n")
    
    try:
        # Créer les clients
        customers = create_customers()
        print(f"\n✓ {len(customers)} clients disponibles")
        
        # Créer les ventes
        sales = create_sales(customers)
        print(f"\n✓ {len(sales)} ventes créées")
        
        # Statistiques finales
        print("\n=== Résumé ===")
        print(f"Clients total: {Customer.objects.count()}")
        print(f"Ventes total: {Sale.objects.count()}")
        print(f"Articles vendus: {SaleItem.objects.count()}")
        
        # Calculer le CA total
        total_revenue = sum(sale.total_amount for sale in Sale.objects.filter(status='completed'))
        print(f"Chiffre d'affaires total: {total_revenue:,.0f} FCFA")
        
        print("\n✅ Données de ventes créées avec succès!")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de la création des données: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()