from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from .models import (
    Customer, Sale, SaleItem, Payment, Promotion
)
from .serializers import (
    CustomerSerializer, SaleSerializer, SaleItemSerializer,
    PaymentSerializer, PromotionSerializer
)


class CustomerViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des clients."""
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['customer_type']
    search_fields = ['name', 'phone', 'email']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']
    
    @action(detail=True, methods=['get'])
    def purchase_history(self, request, pk=None):
        """Historique des achats du client."""
        customer = self.get_object()
        sales = Sale.objects.filter(customer=customer).order_by('-sale_date')
        
        # Statistiques
        total_purchases = sales.aggregate(
            total_amount=Sum('total_amount'),
            total_orders=Count('id')
        )
        
        # Sérialiser les ventes récentes
        recent_sales = sales[:10]
        sales_data = SaleSerializer(recent_sales, many=True).data
        
        return Response({
            'statistics': total_purchases,
            'recent_purchases': sales_data
        })


class SaleViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des ventes."""
    queryset = Sale.objects.select_related('customer').prefetch_related('lines__product')
    serializer_class = SaleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['sale_number', 'customer__name']
    ordering_fields = ['sale_date', 'total_amount']
    ordering = ['-sale_date']
    
    def perform_create(self, serializer):
        """Créer une vente avec l'utilisateur actuel."""
        serializer.save(salesperson=self.request.user)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Statistiques des ventes."""
        today = timezone.now().date()
        this_month = today.replace(day=1)
        
        stats = {
            'today': self._get_period_stats(today, today),
            'this_week': self._get_period_stats(today - timedelta(days=7), today),
            'this_month': self._get_period_stats(this_month, today),
            'total': self._get_total_stats()
        }
        
        return Response(stats)
    
    def _get_period_stats(self, start_date, end_date):
        """Statistiques pour une période donnée."""
        sales = self.queryset.filter(
            sale_date__date__gte=start_date,
            sale_date__date__lte=end_date,
            status__in=['confirmed', 'delivered']
        )
        
        return sales.aggregate(
            total_sales=Sum('total_amount') or Decimal('0'),
            total_orders=Count('id'),
            average_order=Sum('total_amount') / Count('id') if Count('id') > 0 else Decimal('0')
        )
    
    def _get_total_stats(self):
        """Statistiques totales."""
        return self.queryset.filter(status__in=['confirmed', 'delivered']).aggregate(
            total_sales=Sum('total_amount') or Decimal('0'),
            total_orders=Count('id')
        )
    
    @action(detail=False, methods=['get'])
    def top_products(self, request):
        """Produits les plus vendus."""
        from django.db.models import Sum
        from inventory.serializers import ProductSerializer
        
        top_items = SaleItem.objects.select_related('product').values(
            'product__id', 'product__name'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_amount=Sum(F('quantity') * F('unit_price'))
        ).order_by('-total_quantity')[:10]
        
        return Response(top_items)
    
    @action(detail=True, methods=['post'])
    def confirm_sale(self, request, pk=None):
        """Confirmer une vente."""
        sale = self.get_object()
        
        if sale.status != 'pending':
            return Response(
                {'error': 'Seules les ventes en attente peuvent être confirmées'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifier le stock
        for item in sale.items.all():
            if item.quantity > item.product.current_stock:
                return Response(
                    {'error': f'Stock insuffisant pour {item.product.name}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Confirmer la vente
        sale.confirm_sale()
        
        return Response({'message': 'Vente confirmée avec succès'})
    
    @action(detail=True, methods=['post'])
    def cancel_sale(self, request, pk=None):
        """Annuler une vente."""
        sale = self.get_object()
        
        if sale.status == 'cancelled':
            return Response(
                {'error': 'Cette vente est déjà annulée'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        sale.cancel_sale()
        return Response({'message': 'Vente annulée avec succès'})


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des paiements."""
    queryset = Payment.objects.select_related('sale')
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['payment_method', 'sale']
    ordering_fields = ['payment_date', 'amount']
    ordering = ['-payment_date']


class PromotionViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des promotions."""
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
