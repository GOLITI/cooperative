"""
Vues API pour la gestion des ventes.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from accounts.permissions import CanViewSales, CanManageSales

from .models import Customer, Sale, SaleLine, SalePayment
from .serializers import (
    CustomerSerializer, CustomerListSerializer,
    SaleSerializer, SaleListSerializer, SaleCreateUpdateSerializer,
    SaleLineSerializer, SalePaymentSerializer, SalesStatsSerializer
)


class CustomerViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des clients.
    """
    queryset = Customer.objects.all()
    permission_classes = [IsAuthenticated, CanViewSales]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['customer_type', 'member']
    search_fields = ['name', 'customer_code', 'contact_person', 'email', 'phone']
    ordering_fields = ['name', 'customer_code', 'total_purchases', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Sélection du sérialiseur selon l'action."""
        if self.action == 'list':
            return CustomerListSerializer
        return CustomerSerializer
    
    def get_permissions(self):
        """Permissions selon l'action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, CanManageSales]
        else:
            permission_classes = [IsAuthenticated, CanViewSales]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['get'])
    def sales_history(self, request, pk=None):
        """Historique des ventes du client."""
        customer = self.get_object()
        sales = customer.sales.all()
        serializer = SaleListSerializer(sales, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def payment_history(self, request, pk=None):
        """Historique des paiements du client."""
        customer = self.get_object()
        payments = SalePayment.objects.filter(sale__customer=customer)
        serializer = SalePaymentSerializer(payments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def top_customers(self, request):
        """Top des meilleurs clients."""
        limit = int(request.query_params.get('limit', 10))
        top_customers = Customer.objects.annotate(
            sales_count=Count('sales'),
            total_amount=Sum('sales__total_amount')
        ).filter(
            total_amount__gt=0
        ).order_by('-total_amount')[:limit]
        
        serializer = CustomerListSerializer(top_customers, many=True)
        return Response(serializer.data)


class SaleViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des ventes.
    """
    queryset = Sale.objects.select_related('customer', 'salesperson').prefetch_related('lines', 'payments')
    permission_classes = [IsAuthenticated, CanViewSales]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_status', 'customer', 'salesperson']
    search_fields = ['sale_number', 'customer__name', 'notes']
    ordering_fields = ['sale_date', 'total_amount', 'created_at']
    ordering = ['-sale_date']
    
    def get_serializer_class(self):
        """Sélection du sérialiseur selon l'action."""
        if self.action == 'list':
            return SaleListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return SaleCreateUpdateSerializer
        return SaleSerializer
    
    def get_permissions(self):
        """Permissions selon l'action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, CanManageSales]
        else:
            permission_classes = [IsAuthenticated, CanViewSales]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """Assignation du vendeur lors de la création."""
        serializer.save(salesperson=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_line(self, request, pk=None):
        """Ajouter une ligne à la vente."""
        sale = self.get_object()
        serializer = SaleLineSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(sale=sale)
            sale.calculate_totals()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def add_payment(self, request, pk=None):
        """Ajouter un paiement à la vente."""
        sale = self.get_object()
        serializer = SalePaymentSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(sale=sale, validated_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def confirm_sale(self, request, pk=None):
        """Confirmer une vente."""
        sale = self.get_object()
        if sale.status == 'draft':
            sale.status = 'confirmed'
            sale.save()
            return Response({'message': 'Vente confirmée avec succès'})
        return Response(
            {'error': 'Seules les ventes en brouillon peuvent être confirmées'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['post'])
    def mark_delivered(self, request, pk=None):
        """Marquer une vente comme livrée."""
        sale = self.get_object()
        if sale.status in ['confirmed', 'delivered']:
            sale.status = 'delivered'
            sale.actual_delivery_date = timezone.now().date()
            sale.save()
            return Response({'message': 'Vente marquée comme livrée'})
        return Response(
            {'error': 'La vente doit être confirmée pour être livrée'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['post'])
    def cancel_sale(self, request, pk=None):
        """Annuler une vente."""
        sale = self.get_object()
        if sale.status in ['draft', 'confirmed']:
            sale.status = 'cancelled'
            sale.save()
            return Response({'message': 'Vente annulée avec succès'})
        return Response(
            {'error': 'Seules les ventes non livrées peuvent être annulées'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Statistiques des ventes."""
        # Période de calcul
        period = request.query_params.get('period', '30')  # 30 jours par défaut
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=int(period))
        
        # Filtrage des ventes
        sales_qs = Sale.objects.filter(
            sale_date__date__gte=start_date,
            sale_date__date__lte=end_date
        ).exclude(status='cancelled')
        
        # Calculs de base
        total_sales = sales_qs.count()
        total_amount = sales_qs.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        total_paid = sales_qs.aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0
        total_pending = total_amount - total_paid
        avg_sale = sales_qs.aggregate(Avg('total_amount'))['total_amount__avg'] or 0
        
        # Ventes par statut
        sales_by_status = {}
        for choice in Sale.STATUS_CHOICES:
            status_key = choice[0]
            count = sales_qs.filter(status=status_key).count()
            sales_by_status[status_key] = count
        
        # Ventes par statut de paiement
        sales_by_payment_status = {}
        for choice in Sale.PAYMENT_STATUS_CHOICES:
            status_key = choice[0]
            count = sales_qs.filter(payment_status=status_key).count()
            sales_by_payment_status[status_key] = count
        
        # Top clients
        top_customers = list(
            Customer.objects.annotate(
                period_total=Sum('sales__total_amount', 
                               filter=Q(sales__sale_date__date__gte=start_date,
                                       sales__sale_date__date__lte=end_date))
            ).filter(
                period_total__gt=0
            ).order_by('-period_total')[:5].values(
                'name', 'period_total'
            )
        )
        
        # Ventes mensuelles (12 derniers mois)
        monthly_sales = []
        for i in range(12):
            month_start = end_date.replace(day=1) - timedelta(days=i*30)
            month_end = month_start + timedelta(days=30)
            month_total = Sale.objects.filter(
                sale_date__date__gte=month_start,
                sale_date__date__lt=month_end
            ).exclude(status='cancelled').aggregate(
                Sum('total_amount')
            )['total_amount__sum'] or 0
            
            monthly_sales.append({
                'month': month_start.strftime('%Y-%m'),
                'total': month_total
            })
        
        stats_data = {
            'total_sales': total_sales,
            'total_amount': total_amount,
            'total_paid': total_paid,
            'total_pending': total_pending,
            'average_sale_amount': avg_sale,
            'sales_by_status': sales_by_status,
            'sales_by_payment_status': sales_by_payment_status,
            'top_customers': top_customers,
            'monthly_sales': monthly_sales
        }
        
        serializer = SalesStatsSerializer(stats_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue_payments(self, request):
        """Ventes avec paiements en retard."""
        overdue_sales = Sale.objects.filter(
            payment_status__in=['pending', 'partial'],
            expected_delivery_date__lt=timezone.now().date()
        ).exclude(status='cancelled')
        
        serializer = SaleListSerializer(overdue_sales, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def daily_sales(self, request):
        """Ventes du jour."""
        today = timezone.now().date()
        today_sales = Sale.objects.filter(
            sale_date__date=today
        ).exclude(status='cancelled')
        
        serializer = SaleListSerializer(today_sales, many=True)
        return Response(serializer.data)


class SaleLineViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des lignes de vente.
    """
    queryset = SaleLine.objects.select_related('sale', 'product')
    serializer_class = SaleLineSerializer
    permission_classes = [IsAuthenticated, CanViewSales]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['sale', 'product']
    
    def get_permissions(self):
        """Permissions selon l'action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, CanManageSales]
        else:
            permission_classes = [IsAuthenticated, CanViewSales]
        return [permission() for permission in permission_classes]


class SalePaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des paiements de vente.
    """
    queryset = SalePayment.objects.select_related('sale', 'validated_by')
    serializer_class = SalePaymentSerializer
    permission_classes = [IsAuthenticated, CanViewSales]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['sale', 'payment_method', 'validated_by']
    ordering_fields = ['payment_date', 'amount']
    ordering = ['-payment_date']
    
    def get_permissions(self):
        """Permissions selon l'action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, CanManageSales]
        else:
            permission_classes = [IsAuthenticated, CanViewSales]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """Assignation du validateur lors de la création."""
        serializer.save(validated_by=self.request.user)
