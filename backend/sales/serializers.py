"""
Sérialiseurs pour l'API des ventes.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from members.models import Member
from inventory.models import Product
from .models import Customer, Sale, SaleLine, SalePayment


class CustomerSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les clients."""
    
    # Champs calculés
    member_name = serializers.CharField(source='member.full_name', read_only=True)
    balance_due = serializers.SerializerMethodField()
    
    class Meta:
        model = Customer
        fields = [
            'id', 'customer_code', 'customer_type', 'member', 'member_name',
            'name', 'contact_person', 'phone', 'email', 'address',
            'credit_limit', 'payment_terms_days', 'total_purchases',
            'last_purchase_date', 'balance_due', 'created_at', 'updated_at'
        ]
        read_only_fields = ['customer_code', 'total_purchases', 'last_purchase_date']
    
    def get_balance_due(self, obj):
        """Calcul du solde dû par le client."""
        # Somme des factures non payées
        unpaid_sales = obj.sales.exclude(payment_status='paid')
        return sum(sale.balance_due for sale in unpaid_sales)


class CustomerListSerializer(serializers.ModelSerializer):
    """Sérialiseur simplifié pour la liste des clients."""
    
    member_name = serializers.CharField(source='member.full_name', read_only=True)
    sales_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Customer
        fields = [
            'id', 'customer_code', 'customer_type', 'member_name',
            'name', 'phone', 'email', 'total_purchases',
            'sales_count', 'created_at'
        ]
    
    def get_sales_count(self, obj):
        """Nombre de ventes du client."""
        return obj.sales.count()


class SaleLineSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les lignes de vente."""
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_unit = serializers.CharField(source='product.unit.name', read_only=True)
    line_total_before_discount = serializers.ReadOnlyField()
    discount_amount = serializers.ReadOnlyField()
    total_price = serializers.ReadOnlyField()
    
    class Meta:
        model = SaleLine
        fields = [
            'id', 'product', 'product_name', 'product_unit',
            'quantity', 'unit_price', 'discount_percentage',
            'lot_number', 'line_total_before_discount',
            'discount_amount', 'total_price'
        ]
    
    def validate_quantity(self, value):
        """Validation de la quantité disponible."""
        if self.instance:
            product = self.instance.product
        else:
            product = self.initial_data.get('product')
            if isinstance(product, int):
                try:
                    product = Product.objects.get(id=product)
                except Product.DoesNotExist:
                    raise serializers.ValidationError("Produit non trouvé.")
        
        # Vérification du stock disponible
        if hasattr(product, 'current_stock') and product.current_stock < value:
            raise serializers.ValidationError(
                f"Stock insuffisant. Stock disponible: {product.current_stock}"
            )
        
        return value


class SalePaymentSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les paiements de vente."""
    
    validated_by_name = serializers.CharField(
        source='validated_by.username', 
        read_only=True
    )
    
    class Meta:
        model = SalePayment
        fields = [
            'id', 'amount', 'payment_method', 'payment_date',
            'reference', 'notes', 'validated_by', 'validated_by_name',
            'created_at'
        ]
        read_only_fields = ['validated_by']
    
    def validate_amount(self, value):
        """Validation du montant du paiement."""
        if value <= 0:
            raise serializers.ValidationError("Le montant doit être positif.")
        
        # Vérification que le paiement ne dépasse pas le solde dû
        if self.instance:
            sale = self.instance.sale
            current_payment = self.instance.amount
        else:
            sale_id = self.initial_data.get('sale')
            if sale_id:
                try:
                    sale = Sale.objects.get(id=sale_id)
                except Sale.DoesNotExist:
                    return value
            else:
                return value
            current_payment = 0
        
        balance_due = sale.balance_due + current_payment
        if value > balance_due:
            raise serializers.ValidationError(
                f"Le montant ne peut pas dépasser le solde dû: {balance_due}"
            )
        
        return value


class SaleSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les ventes."""
    
    # Relations
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    customer_code = serializers.CharField(source='customer.customer_code', read_only=True)
    salesperson_name = serializers.CharField(source='salesperson.username', read_only=True)
    
    # Lignes de vente
    lines = SaleLineSerializer(many=True, read_only=True)
    payments = SalePaymentSerializer(many=True, read_only=True)
    
    # Champs calculés
    balance_due = serializers.ReadOnlyField()
    is_fully_paid = serializers.ReadOnlyField()
    lines_count = serializers.SerializerMethodField()
    payments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Sale
        fields = [
            'id', 'sale_number', 'customer', 'customer_name', 'customer_code',
            'salesperson', 'salesperson_name', 'sale_date', 
            'expected_delivery_date', 'actual_delivery_date',
            'status', 'payment_status', 'subtotal', 'discount_percentage',
            'discount_amount', 'tax_percentage', 'tax_amount',
            'total_amount', 'paid_amount', 'balance_due', 'is_fully_paid',
            'notes', 'internal_notes', 'lines', 'payments',
            'lines_count', 'payments_count', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'sale_number', 'subtotal', 'discount_amount', 'tax_amount',
            'total_amount', 'paid_amount'
        ]
    
    def get_lines_count(self, obj):
        """Nombre de lignes de vente."""
        return obj.lines.count()
    
    def get_payments_count(self, obj):
        """Nombre de paiements."""
        return obj.payments.count()


class SaleListSerializer(serializers.ModelSerializer):
    """Sérialiseur simplifié pour la liste des ventes."""
    
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    salesperson_name = serializers.CharField(source='salesperson.username', read_only=True)
    balance_due = serializers.ReadOnlyField()
    lines_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Sale
        fields = [
            'id', 'sale_number', 'customer_name', 'salesperson_name',
            'sale_date', 'status', 'payment_status', 'total_amount',
            'paid_amount', 'balance_due', 'lines_count', 'created_at'
        ]
    
    def get_lines_count(self, obj):
        """Nombre de lignes de vente."""
        return obj.lines.count()


class SaleCreateUpdateSerializer(serializers.ModelSerializer):
    """Sérialiseur pour créer/modifier une vente avec ses lignes."""
    
    lines_data = SaleLineSerializer(many=True, write_only=True, required=False)
    
    class Meta:
        model = Sale
        fields = [
            'customer', 'salesperson', 'sale_date', 'expected_delivery_date',
            'status', 'discount_percentage', 'tax_percentage',
            'notes', 'internal_notes', 'lines_data'
        ]
    
    def create(self, validated_data):
        """Création d'une vente avec ses lignes."""
        lines_data = validated_data.pop('lines_data', [])
        sale = Sale.objects.create(**validated_data)
        
        # Création des lignes de vente
        for line_data in lines_data:
            SaleLine.objects.create(sale=sale, **line_data)
        
        # Recalcul des totaux
        sale.calculate_totals()
        
        return sale
    
    def update(self, instance, validated_data):
        """Mise à jour d'une vente."""
        lines_data = validated_data.pop('lines_data', None)
        
        # Mise à jour des champs de base
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Mise à jour des lignes si fournies
        if lines_data is not None:
            # Supprimer les anciennes lignes
            instance.lines.all().delete()
            
            # Créer les nouvelles lignes
            for line_data in lines_data:
                SaleLine.objects.create(sale=instance, **line_data)
        
        # Recalcul des totaux
        instance.calculate_totals()
        
        return instance


# Sérialiseurs pour les statistiques
class SalesStatsSerializer(serializers.Serializer):
    """Sérialiseur pour les statistiques des ventes."""
    
    total_sales = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_paid = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_pending = serializers.DecimalField(max_digits=15, decimal_places=2)
    average_sale_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    sales_by_status = serializers.DictField()
    sales_by_payment_status = serializers.DictField()
    top_customers = serializers.ListField()
    monthly_sales = serializers.ListField()