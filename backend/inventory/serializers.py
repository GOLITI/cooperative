"""
Sérialiseurs pour l'API de gestion de l'inventaire.
"""
from rest_framework import serializers
from django.utils import timezone
from django.db.models import Sum, F
from decimal import Decimal

from .models import (
    Product, ProductCategory, Unit, StockMovement
)


class UnitSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les unités de mesure."""
    
    class Meta:
        model = Unit
        fields = [
            'id', 'name', 'abbreviation', 'type', 'is_active', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class CategorySerializer(serializers.ModelSerializer):
    """Sérialiseur pour les catégories de produits."""
    
    product_count = serializers.SerializerMethodField()
    total_stock_value = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductCategory
        fields = [
            'id', 'name', 'description', 'parent', 'image', 'sort_order',
            'product_count', 'total_stock_value', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_product_count(self, obj):
        """Nombre de produits dans cette catégorie."""
        return obj.products.filter(is_active=True).count()
    
    def get_total_stock_value(self, obj):
        """Valeur totale du stock dans cette catégorie."""
        total_value = obj.products.filter(is_active=True).aggregate(
            total=Sum(F('current_stock') * F('selling_price'))
        )['total']
        return total_value or Decimal('0.00')


class ProductListSerializer(serializers.ModelSerializer):
    """Sérialiseur pour la liste des produits."""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    unit_name = serializers.CharField(source='unit.name', read_only=True)
    unit_abbreviation = serializers.CharField(source='unit.abbreviation', read_only=True)
    stock_status = serializers.SerializerMethodField()
    stock_value = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'code', 'category_name',
            'unit_name', 'unit_abbreviation', 'current_stock', 'min_stock_level',
            'selling_price', 'stock_status', 'stock_value', 'is_active'
        ]
    
    def get_stock_status(self, obj):
        """Status du stock."""
        if obj.current_stock <= 0:
            return "stock_out"
        elif obj.current_stock <= obj.min_stock_level:
            return "low_stock"
        elif obj.current_stock <= obj.min_stock_level * 2:
            return "medium_stock"
        else:
            return "good_stock"
    
    def get_stock_value(self, obj):
        """Valeur du stock."""
        return obj.current_stock * obj.selling_price


class ProductDetailSerializer(serializers.ModelSerializer):
    """Sérialiseur complet pour les détails d'un produit."""
    
    category = CategorySerializer(read_only=True)
    unit = UnitSerializer(read_only=True)
    stock_status = serializers.SerializerMethodField()
    stock_value = serializers.SerializerMethodField()
    stock_turnover = serializers.SerializerMethodField()
    last_movement = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'code', 'barcode', 'description', 'specifications',
            'category', 'unit', 'product_type', 'image', 'weight', 'dimensions',
            'purchase_price', 'selling_price', 'member_price',
            'current_stock', 'min_stock_level', 'max_stock_level',
            'origin', 'quality_grade', 'expiry_tracking', 'lot_tracking',
            'stock_status', 'stock_value', 'stock_turnover', 'last_movement',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_stock_status(self, obj):
        """Status du stock."""
        if obj.current_stock <= 0:
            return "stock_out"
        elif obj.current_stock <= obj.min_stock_level:
            return "low_stock"
        elif obj.current_stock <= obj.min_stock_level * 2:
            return "medium_stock"
        else:
            return "good_stock"
    
    def get_stock_value(self, obj):
        """Valeur du stock."""
        return obj.current_stock * obj.selling_price
    
    def get_stock_turnover(self, obj):
        """Rotation du stock (derniers 30 jours)."""
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        total_out = obj.movements.filter(
            movement_type='out',
            created_at__gte=thirty_days_ago
        ).aggregate(total=Sum('quantity'))['total'] or Decimal('0.00')
        
        avg_stock = obj.current_stock
        if avg_stock > 0:
            return total_out / avg_stock
        return Decimal('0.00')
    
    def get_last_movement(self, obj):
        """Dernier mouvement de stock."""
        last_movement = obj.movements.order_by('-created_at').first()
        if last_movement:
            return {
                'date': last_movement.created_at,
                'type': last_movement.movement_type,
                'quantity': last_movement.quantity,
                'reason': last_movement.reason
            }
        return None


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Sérialiseur pour créer et modifier les produits."""
    
    class Meta:
        model = Product
        fields = [
            'name', 'code', 'barcode', 'description', 'specifications',
            'category', 'unit', 'product_type', 'image', 'weight', 'dimensions',
            'purchase_price', 'selling_price', 'member_price',
            'current_stock', 'min_stock_level', 'max_stock_level',
            'origin', 'quality_grade', 'expiry_tracking', 'lot_tracking',
            'is_active'
        ]
    
    def validate_code(self, value):
        """Validation du code produit."""
        if self.instance and self.instance.code == value:
            return value
        
        if Product.objects.filter(code=value).exists():
            raise serializers.ValidationError("Un produit avec ce code existe déjà.")
        return value
    
    def validate(self, attrs):
        """Validations générales."""
        if attrs.get('min_stock_level', 0) < 0:
            raise serializers.ValidationError("Le stock minimum ne peut pas être négatif.")
        
        if attrs.get('max_stock_level') and attrs.get('min_stock_level', 0) > attrs['max_stock_level']:
            raise serializers.ValidationError("Le stock maximum doit être supérieur au stock minimum.")
        
        if attrs.get('selling_price', 0) < attrs.get('purchase_price', 0):
            raise serializers.ValidationError("Le prix de vente ne peut pas être inférieur au prix d'achat.")
        
        return attrs


class StockMovementSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les mouvements de stock."""
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_code = serializers.CharField(source='product.code', read_only=True)
    unit_abbreviation = serializers.CharField(source='product.unit.abbreviation', read_only=True)
    total_cost = serializers.SerializerMethodField()
    
    class Meta:
        model = StockMovement
        fields = [
            'id', 'product', 'product_name', 'product_code', 'unit_abbreviation',
            'movement_type', 'quantity', 'unit_cost', 'total_cost',
            'reason', 'lot_number', 'expiry_date', 'supplier_info', 'reference_document',
            'created_at'
        ]
        read_only_fields = ['created_at']
    
    def get_total_cost(self, obj):
        """Calculer le coût total."""
        return obj.quantity * obj.unit_cost
    
    def create(self, validated_data):
        """Créer un mouvement de stock et mettre à jour le stock du produit."""
        movement = super().create(validated_data)
        
        # Mettre à jour le stock du produit
        product = movement.product
        if movement.movement_type == 'in':
            product.current_stock += movement.quantity
        elif movement.movement_type == 'out':
            product.current_stock -= movement.quantity
        elif movement.movement_type == 'adjustment':
            # Pour les ajustements, la quantité est la nouvelle valeur
            product.current_stock = movement.quantity
        
        product.save()
        return movement


class InventoryStatsSerializer(serializers.Serializer):
    """Sérialiseur pour les statistiques d'inventaire."""
    
    total_products = serializers.IntegerField()
    active_products = serializers.IntegerField()
    total_categories = serializers.IntegerField()
    total_stock_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    low_stock_count = serializers.IntegerField()
    out_of_stock_count = serializers.IntegerField()
    total_movements_today = serializers.IntegerField()


class StockAlertSerializer(serializers.Serializer):
    """Sérialiseur pour les alertes de stock."""
    
    product_id = serializers.IntegerField()
    product_name = serializers.CharField()
    product_code = serializers.CharField()
    current_stock = serializers.DecimalField(max_digits=15, decimal_places=3)
    min_stock_level = serializers.DecimalField(max_digits=15, decimal_places=3)
    alert_type = serializers.ChoiceField(choices=[
        ('out_of_stock', 'Rupture de stock'),
        ('low_stock', 'Stock faible'),
    ])
    category_name = serializers.CharField()
    days_until_stockout = serializers.IntegerField(allow_null=True)


class ProductStatsSerializer(serializers.Serializer):
    """Sérialiseur pour les statistiques d'un produit."""
    
    total_movements = serializers.IntegerField()
    movements_in = serializers.IntegerField()
    movements_out = serializers.IntegerField()
    total_quantity_in = serializers.DecimalField(max_digits=15, decimal_places=3)
    total_quantity_out = serializers.DecimalField(max_digits=15, decimal_places=3)
    current_stock = serializers.DecimalField(max_digits=15, decimal_places=3)
    stock_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    average_cost = serializers.DecimalField(max_digits=12, decimal_places=2)
    last_movement_date = serializers.DateTimeField(allow_null=True)
    stock_turnover_30d = serializers.DecimalField(max_digits=10, decimal_places=2)