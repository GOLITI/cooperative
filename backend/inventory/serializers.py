from rest_framework import serializers
from .models import Category, Unit, Product, StockMovement, Inventory, InventoryLine


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ['id', 'name', 'abbreviation', 'unit_type', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CategorySerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'parent', 'parent_name', 'code', 
                 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des produits (données simplifiées)"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    unit_name = serializers.CharField(source='unit.name', read_only=True)
    stock_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['id', 'sku', 'name', 'category_name', 'unit_name', 'current_stock', 
                 'minimum_stock', 'selling_price_member', 'selling_price_non_member', 
                 'status', 'stock_status', 'image']
        
    def get_stock_status(self, obj):
        if obj.current_stock <= 0:
            return 'out_of_stock'
        elif obj.is_low_stock:
            return 'low_stock'
        else:
            return 'in_stock'


class ProductDetailSerializer(serializers.ModelSerializer):
    """Serializer pour le détail d'un produit"""
    category = CategorySerializer(read_only=True)
    unit = UnitSerializer(read_only=True)
    stock_value = serializers.ReadOnlyField()
    is_low_stock = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'category', 'sku', 'barcode', 'unit', 
                 'cost_price', 'selling_price_member', 'selling_price_non_member',
                 'current_stock', 'minimum_stock', 'maximum_stock', 'status', 
                 'expiry_date', 'image', 'stock_value', 'is_low_stock',
                 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'current_stock', 'created_at', 'updated_at']


class ProductCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création d'un produit"""
    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'sku', 'barcode', 'unit', 
                 'cost_price', 'selling_price_member', 'selling_price_non_member',
                 'minimum_stock', 'maximum_stock', 'expiry_date', 'image']


class StockMovementSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = StockMovement
        fields = ['id', 'product', 'product_name', 'movement_type', 'quantity', 'unit_cost',
                 'reference_type', 'reference_number', 'notes', 'user', 'user_name',
                 'stock_after', 'created_at']
        read_only_fields = ['id', 'user', 'stock_after', 'created_at']


class InventoryLineSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    counted_by_name = serializers.CharField(source='counted_by.username', read_only=True)
    
    class Meta:
        model = InventoryLine
        fields = ['id', 'product', 'product_name', 'product_sku', 'theoretical_quantity', 
                 'physical_quantity', 'difference', 'notes', 'counted_by', 'counted_by_name', 
                 'created_at']
        read_only_fields = ['id', 'theoretical_quantity', 'difference', 'created_at']


class InventorySerializer(serializers.ModelSerializer):
    lines = InventoryLineSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Inventory
        fields = ['id', 'name', 'date_start', 'date_end', 'status', 'notes', 
                 'created_by', 'created_by_name', 'lines', 'created_at']
        read_only_fields = ['id', 'created_by', 'created_at']