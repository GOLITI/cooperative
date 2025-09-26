from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Q, F, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from .models import Report, Dashboard, ReportTemplate
from .serializers import (
    ReportSerializer, DashboardSerializer, ReportTemplateSerializer
)

# Import des modèles pour les statistiques
from members.models import Member, MembershipFee
from inventory.models import Product, StockMovement
from sales.models import Sale, SaleItem
from finance.models import Account, FinancialTransaction, Loan


class ReportViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des rapports."""
    queryset = Report.objects.select_related('created_by')
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['report_type', 'status']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        """Créer un rapport avec l'utilisateur actuel."""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def generate(self, request, pk=None):
        """Générer un rapport."""
        report = self.get_object()
        
        try:
            # Logique de génération selon le type de rapport
            if report.report_type == 'members':
                data = self._generate_members_report(report.parameters)
            elif report.report_type == 'sales':
                data = self._generate_sales_report(report.parameters)
            elif report.report_type == 'inventory':
                data = self._generate_inventory_report(report.parameters)
            elif report.report_type == 'finance':
                data = self._generate_finance_report(report.parameters)
            else:
                return Response(
                    {'error': 'Type de rapport non supporté'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Marquer le rapport comme généré
            report.status = 'completed'
            report.generated_at = timezone.now()
            report.save()
            
            return Response({
                'message': 'Rapport généré avec succès',
                'data': data
            })
            
        except Exception as e:
            report.status = 'error'
            report.save()
            return Response(
                {'error': f'Erreur lors de la génération: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _generate_members_report(self, parameters):
        """Générer un rapport des membres."""
        queryset = Member.objects.select_related('user')
        
        # Filtres selon les paramètres
        if parameters and parameters.get('membership_type'):
            queryset = queryset.filter(membership_type=parameters['membership_type'])
        
        if parameters and parameters.get('date_from'):
            queryset = queryset.filter(date_joined__gte=parameters['date_from'])
        
        if parameters and parameters.get('date_to'):
            queryset = queryset.filter(date_joined__lte=parameters['date_to'])
        
        # Statistiques
        total_members = queryset.count()
        active_members = queryset.filter(is_active=True).count()
        
        # Répartition par type d'adhésion
        by_type = queryset.values('membership_type').annotate(
            count=Count('id')
        ).order_by('membership_type')
        
        return {
            'total_members': total_members,
            'active_members': active_members,
            'inactive_members': total_members - active_members,
            'by_membership_type': list(by_type),
            'members': list(queryset.values(
                'id', 'membership_number', 'user__first_name', 
                'user__last_name', 'membership_type', 'date_joined', 'is_active'
            ))
        }
    
    def _generate_sales_report(self, parameters):
        """Générer un rapport des ventes."""
        queryset = Sale.objects.select_related('customer')
        
        # Filtres selon les paramètres
        if parameters and parameters.get('date_from'):
            queryset = queryset.filter(sale_date__date__gte=parameters['date_from'])
        
        if parameters and parameters.get('date_to'):
            queryset = queryset.filter(sale_date__date__lte=parameters['date_to'])
        
        if parameters and parameters.get('status'):
            queryset = queryset.filter(status=parameters['status'])
        
        # Statistiques
        stats = queryset.aggregate(
            total_sales=Sum('final_amount') or Decimal('0'),
            total_orders=Count('id'),
            average_order=Avg('final_amount') or Decimal('0')
        )
        
        # Top produits vendus
        top_products = SaleItem.objects.filter(
            sale__in=queryset
        ).values('product__name').annotate(
            quantity_sold=Sum('quantity'),
            revenue=Sum(F('quantity') * F('unit_price'))
        ).order_by('-quantity_sold')[:10]
        
        return {
            'statistics': stats,
            'top_products': list(top_products),
            'sales': list(queryset.values(
                'id', 'sale_number', 'customer__name', 'sale_date',
                'total_amount', 'final_amount', 'status'
            ))
        }
    
    def _generate_inventory_report(self, parameters):
        """Générer un rapport d'inventaire."""
        queryset = Product.objects.select_related('category')
        
        # Filtres selon les paramètres
        if parameters and parameters.get('category'):
            queryset = queryset.filter(category=parameters['category'])
        
        if parameters and parameters.get('low_stock_only'):
            queryset = queryset.filter(current_stock__lte=F('minimum_stock'))
        
        # Statistiques
        total_products = queryset.count()
        low_stock_products = queryset.filter(current_stock__lte=F('minimum_stock')).count()
        total_value = queryset.aggregate(
            value=Sum(F('current_stock') * F('cost_price'))
        )['value'] or Decimal('0')
        
        # Mouvements récents
        recent_movements = StockMovement.objects.select_related(
            'product'
        ).order_by('-date')[:50]
        
        return {
            'statistics': {
                'total_products': total_products,
                'low_stock_products': low_stock_products,
                'total_inventory_value': total_value
            },
            'products': list(queryset.values(
                'id', 'name', 'category__name', 'current_stock',
                'minimum_stock', 'cost_price', 'selling_price'
            )),
            'recent_movements': list(recent_movements.values(
                'product__name', 'movement_type', 'quantity', 'date'
            ))
        }
    
    def _generate_finance_report(self, parameters):
        """Générer un rapport financier."""
        # Soldes des comptes
        accounts_balance = Account.objects.aggregate(
            total_cash=Sum('balance', filter=Q(account_type='cash')),
            total_bank=Sum('balance', filter=Q(account_type='bank')),
            total_assets=Sum('balance', filter=Q(account_type='asset')),
            total_liabilities=Sum('balance', filter=Q(account_type='liability'))
        )
        
        # Transactions récentes
        transactions = FinancialTransaction.objects.select_related(
            'debit_account', 'credit_account'
        ).order_by('-date')[:100]
        
        # Prêts en cours
        active_loans = Loan.objects.filter(status='disbursed').aggregate(
            total_outstanding=Sum('outstanding_balance'),
            count=Count('id')
        )
        
        return {
            'accounts_balance': accounts_balance,
            'active_loans': active_loans,
            'recent_transactions': list(transactions.values(
                'reference', 'date', 'debit_account__name',
                'credit_account__name', 'amount', 'description'
            ))
        }


class DashboardViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des tableaux de bord."""
    queryset = Dashboard.objects.all()
    serializer_class = DashboardSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        """Filtrer selon les permissions utilisateur."""
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(is_public=True) | Q(created_by=self.request.user)
            )
        return queryset
    
    def perform_create(self, serializer):
        """Créer un tableau de bord avec l'utilisateur actuel."""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def data(self, request, pk=None):
        """Récupérer les données du tableau de bord."""
        dashboard = self.get_object()
        
        # Données KPI de base
        kpis = self._get_kpi_data()
        
        # Données graphiques
        chart_data = self._get_chart_data()
        
        return Response({
            'dashboard': DashboardSerializer(dashboard).data,
            'kpis': kpis,
            'chart_data': chart_data
        })
    
    def _get_kpi_data(self):
        """Récupérer les données KPI."""
        return {
            'total_members': Member.objects.count(),
            'active_members': Member.objects.filter(is_active=True).count(),
            'total_sales_today': Sale.objects.filter(
                sale_date__date=timezone.now().date(),
                status='completed'
            ).aggregate(total=Sum('final_amount'))['total'] or Decimal('0'),
            'low_stock_products': Product.objects.filter(
                current_stock__lte=F('minimum_stock')
            ).count(),
            'active_loans': Loan.objects.filter(status='disbursed').count()
        }
    
    def _get_chart_data(self):
        """Récupérer les données pour graphiques."""
        from django.db.models import TruncMonth
        
        # Ventes par mois
        sales_by_month = Sale.objects.filter(
            status='completed',
            sale_date__gte=timezone.now() - timedelta(days=365)
        ).annotate(
            month=TruncMonth('sale_date')
        ).values('month').annotate(
            total=Sum('final_amount')
        ).order_by('month')
        
        return {
            'sales_by_month': {
                'labels': [item['month'].strftime('%Y-%m') for item in sales_by_month],
                'data': [float(item['total']) for item in sales_by_month]
            }
        }


class ReportTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des modèles de rapports."""
    queryset = ReportTemplate.objects.all()
    serializer_class = ReportTemplateSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['report_type', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']