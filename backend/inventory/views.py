from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, F
from decimal import Decimal

from .models import Product, ProductCategory, Unit, StockMovement
from .serializers import CategorySerializer, UnitSerializer, ProductListSerializer, ProductDetailSerializer, ProductCreateUpdateSerializer, StockMovementSerializer, InventoryStatsSerializer, StockAlertSerializer
from accounts.permissions import BaseCooperativePermission

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [BaseCooperativePermission]

class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    permission_classes = [BaseCooperativePermission]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category', 'unit')
    permission_classes = [BaseCooperativePermission]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        else:
            return ProductDetailSerializer
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        stats_data = {
            'total_products': Product.objects.count(),
            'active_products': Product.objects.filter(is_active=True).count(),
            'total_categories': ProductCategory.objects.count(),
            'total_stock_value': Decimal('0.00'),
            'low_stock_count': 0,
            'out_of_stock_count': 0,
            'total_movements_today': 0,
        }
        serializer = InventoryStatsSerializer(stats_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def alerts(self, request):
        serializer = StockAlertSerializer([], many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        serializer = ProductListSerializer([], many=True)
        return Response(serializer.data)

class StockMovementViewSet(viewsets.ModelViewSet):
    queryset = StockMovement.objects.all()
    serializer_class = StockMovementSerializer
    permission_classes = [BaseCooperativePermission]
