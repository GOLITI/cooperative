from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Q, F
from django.db import models
from .models import (
    Category, Unit, Product, StockMovement, Inventory, InventoryLine
)
from .serializers import (
    CategorySerializer, UnitSerializer, ProductListSerializer, ProductDetailSerializer,
    ProductCreateSerializer, StockMovementSerializer, InventorySerializer, InventoryLineSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['parent']
    search_fields = ['name', 'description', 'code']
    ordering = ['name']


class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['unit_type']
    search_fields = ['name', 'abbreviation']
    ordering = ['name']


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True).select_related('category', 'unit')
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status']
    search_fields = ['name', 'sku', 'barcode']
    ordering_fields = ['name', 'sku', 'current_stock', 'created_at']
    ordering = ['name']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        elif self.action == 'create':
            return ProductCreateSerializer
        else:
            return ProductDetailSerializer

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Produits en stock faible"""
        low_stock_products = self.queryset.filter(
            Q(current_stock__lte=F('minimum_stock')) | Q(current_stock=0)
        )
        serializer = ProductListSerializer(low_stock_products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Statistiques des stocks"""
        stats = {
            'total_products': self.queryset.count(),
            'active_products': self.queryset.filter(status='active').count(),
            'low_stock_products': self.queryset.filter(current_stock__lte=F('minimum_stock')).count(),
            'out_of_stock_products': self.queryset.filter(current_stock=0).count(),
            'total_stock_value': self.queryset.aggregate(
                total=Sum(models.F('current_stock') * models.F('cost_price'))
            )['total'] or 0,
            'products_by_category': list(
                self.queryset.values('category__name')
                .annotate(count=Count('id'))
                .order_by('category__name')
            )
        }
        return Response(stats)

    @action(detail=True, methods=['post'])
    def adjust_stock(self, request, pk=None):
        """Ajuster le stock d'un produit"""
        product = self.get_object()
        quantity = request.data.get('quantity', 0)
        movement_type = request.data.get('movement_type', 'adjustment')
        notes = request.data.get('notes', '')
        
        try:
            quantity = float(quantity)
        except (ValueError, TypeError):
            return Response({'error': 'Quantité invalide'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Créer le mouvement de stock
        movement_data = {
            'product': product.id,
            'movement_type': movement_type,
            'quantity': abs(quantity),
            'reference_type': 'adjustment',
            'notes': notes,
            'user': request.user.id
        }
        
        movement_serializer = StockMovementSerializer(data=movement_data)
        if movement_serializer.is_valid():
            # Calculer le nouveau stock
            if movement_type in ['in', 'adjustment']:
                new_stock = product.current_stock + abs(quantity)
            else:
                new_stock = product.current_stock - abs(quantity)
                if new_stock < 0:
                    return Response({'error': 'Stock insuffisant'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Mettre à jour le stock du produit
            product.current_stock = new_stock
            product.save()
            
            # Sauvegarder le mouvement avec le nouveau stock
            movement = movement_serializer.save(stock_after=new_stock)
            
            return Response({
                'message': 'Stock ajusté avec succès',
                'new_stock': new_stock,
                'movement': StockMovementSerializer(movement).data
            })
        
        return Response(movement_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StockMovementViewSet(viewsets.ReadOnlyModelViewSet):
    """Mouvements de stock en lecture seule"""
    queryset = StockMovement.objects.all().select_related('product', 'user')
    serializer_class = StockMovementSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['product', 'movement_type', 'reference_type']
    ordering = ['-created_at']

    @action(detail=False, methods=['get'])
    def recent_movements(self, request):
        """50 derniers mouvements de stock"""
        recent = self.queryset[:50]
        serializer = self.get_serializer(recent, many=True)
        return Response(serializer.data)


class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all().select_related('created_by')
    serializer_class = InventorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering = ['-date_start']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def start_inventory(self, request, pk=None):
        """Démarrer un inventaire"""
        inventory = self.get_object()
        if inventory.status != 'planned':
            return Response({'error': 'Inventaire déjà démarré'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Créer les lignes d'inventaire pour tous les produits actifs
        products = Product.objects.filter(is_active=True)
        for product in products:
            InventoryLine.objects.get_or_create(
                inventory=inventory,
                product=product,
                defaults={
                    'theoretical_quantity': product.current_stock
                }
            )
        
        inventory.status = 'in_progress'
        inventory.save()
        
        return Response({'message': 'Inventaire démarré avec succès'})

    @action(detail=True, methods=['post'])
    def complete_inventory(self, request, pk=None):
        """Terminer un inventaire"""
        inventory = self.get_object()
        if inventory.status != 'in_progress':
            return Response({'error': 'Inventaire non en cours'}, status=status.HTTP_400_BAD_REQUEST)
        
        from django.utils import timezone
        inventory.status = 'completed'
        inventory.date_end = timezone.now()
        inventory.save()
        
        return Response({'message': 'Inventaire terminé avec succès'})


class InventoryLineViewSet(viewsets.ModelViewSet):
    queryset = InventoryLine.objects.all().select_related('inventory', 'product', 'counted_by')
    serializer_class = InventoryLineSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['inventory', 'product']
    search_fields = ['product__name', 'product__sku']

    def perform_update(self, serializer):
        serializer.save(counted_by=self.request.user)



