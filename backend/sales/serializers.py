from rest_framework import serializers
from .models import (
    Customer, Sale, SaleItem, Payment, Promotion
)


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer pour les clients."""
    
    class Meta:
        model = Customer
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class SaleItemSerializer(serializers.ModelSerializer):
    """Serializer pour les articles d'une vente."""
    product_name = serializers.CharField(source='product.name', read_only=True)
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    
    class Meta:
        model = SaleItem
        fields = [
            'id', 'product', 'product_name',
            'quantity', 'unit_price', 'discount', 'total_amount'
        ]


class SaleSerializer(serializers.ModelSerializer):
    """Serializer pour les ventes."""
    items = SaleItemSerializer(many=True, required=False)
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    
    class Meta:
        model = Sale
        fields = [
            'id', 'sale_number', 'customer', 'customer_name',
            'sale_date', 'total_amount', 'discount',
            'tax_amount', 'final_amount', 'payment_method', 'status',
            'notes', 'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ('id', 'sale_number', 'total_amount', 'final_amount', 'created_at', 'updated_at')


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer pour les paiements."""
    sale_number = serializers.CharField(source='sale.sale_number', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'sale', 'sale_number', 'payment_method', 'amount',
            'payment_date', 'reference', 'notes', 'created_at'
        ]
        read_only_fields = ('id', 'created_at')


class PromotionSerializer(serializers.ModelSerializer):
    """Serializer pour les promotions."""
    
    class Meta:
        model = Promotion
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')