from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Q, F, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from .models import (
    Account, FinancialTransaction, MemberSavings, Loan,
    LoanPayment, Budget, BudgetLine
)
from .serializers import (
    AccountSerializer, FinancialTransactionSerializer, MemberSavingsSerializer,
    LoanSerializer, LoanPaymentSerializer, BudgetSerializer, BudgetLineSerializer
)


class AccountViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des comptes."""
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['account_type', 'is_active']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    @action(detail=True, methods=['get'])
    def balance_history(self, request, pk=None):
        """Historique du solde du compte."""
        account = self.get_object()
        
        # Transactions récentes
        debit_transactions = FinancialTransaction.objects.filter(debit_account=account).order_by('-date')[:20]
        credit_transactions = FinancialTransaction.objects.filter(credit_account=account).order_by('-date')[:20]
        
        return Response({
            'current_balance': account.balance,
            'recent_debits': FinancialTransactionSerializer(debit_transactions, many=True).data,
            'recent_credits': FinancialTransactionSerializer(credit_transactions, many=True).data
        })
    
    @action(detail=False, methods=['get'])
    def balance_summary(self, request):
        """Résumé des soldes par type de compte."""
        summary = self.queryset.values('account_type').annotate(
            total_balance=Sum('balance'),
            account_count=Count('id')
        ).order_by('account_type')
        
        return Response(summary)


class FinancialTransactionViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des transactions financières."""
    queryset = FinancialTransaction.objects.select_related('debit_account', 'credit_account', 'created_by')
    serializer_class = FinancialTransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['debit_account', 'credit_account', 'created_by', 'transaction_type']
    search_fields = ['reference', 'description']
    ordering_fields = ['date', 'amount']
    ordering = ['-date']
    
    def perform_create(self, serializer):
        """Créer une transaction avec l'utilisateur actuel."""
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def cash_flow(self, request):
        """Flux de trésorerie."""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        queryset = self.queryset
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        # Calculs des flux
        cash_accounts = Account.objects.filter(account_type='cash')
        
        inflows = queryset.filter(credit_account__in=cash_accounts).aggregate(
            total=Sum('amount') or Decimal('0')
        )
        
        outflows = queryset.filter(debit_account__in=cash_accounts).aggregate(
            total=Sum('amount') or Decimal('0')
        )
        
        net_flow = inflows['total'] - outflows['total']
        
        return Response({
            'inflows': inflows['total'],
            'outflows': outflows['total'],
            'net_flow': net_flow,
            'period': {
                'start_date': start_date,
                'end_date': end_date
            }
        })


class MemberSavingsViewSet(viewsets.ModelViewSet):
    """ViewSet pour l'épargne des membres."""
    queryset = MemberSavings.objects.select_related('member__user')
    serializer_class = MemberSavingsSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['member', 'savings_type']
    ordering_fields = ['created_at', 'balance']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['get'])
    def savings_summary(self, request):
        """Résumé des épargnes."""
        summary = self.queryset.values('savings_type').annotate(
            total_balance=Sum('balance'),
            member_count=Count('member', distinct=True)
        ).order_by('savings_type')
        
        return Response(summary)
    
    @action(detail=False, methods=['get'])
    def top_savers(self, request):
        """Meilleurs épargnants."""
        top_savers = self.queryset.values(
            'member__id', 'member__user__first_name', 'member__user__last_name'
        ).annotate(
            total_savings=Sum('balance')
        ).order_by('-total_savings')[:10]
        
        return Response(top_savers)


class LoanViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des prêts."""
    queryset = Loan.objects.select_related('member__user', 'approved_by').prefetch_related('payments')
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'member']
    search_fields = ['loan_number', 'member__user__first_name', 'member__user__last_name']
    ordering_fields = ['loan_date', 'amount']
    ordering = ['-loan_date']
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approuver un prêt."""
        loan = self.get_object()
        
        if loan.status != 'pending':
            return Response(
                {'error': 'Seuls les prêts en attente peuvent être approuvés'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        loan.status = 'approved'
        loan.approved_by = request.user
        loan.approved_date = timezone.now()
        loan.save()
        
        return Response({'message': 'Prêt approuvé avec succès'})
    
    @action(detail=True, methods=['post'])
    def disburse(self, request, pk=None):
        """Débloquer un prêt."""
        loan = self.get_object()
        
        if loan.status != 'approved':
            return Response(
                {'error': 'Seuls les prêts approuvés peuvent être débloqués'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        loan.status = 'disbursed'
        loan.disbursement_date = timezone.now()
        loan.save()
        
        return Response({'message': 'Prêt débloqué avec succès'})
    
    @action(detail=False, methods=['get'])
    def loan_statistics(self, request):
        """Statistiques des prêts."""
        stats = {
            'total_loans': self.queryset.count(),
            'active_loans': self.queryset.filter(status='disbursed').count(),
            'total_disbursed': self.queryset.filter(status__in=['disbursed', 'completed']).aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0'),
            'total_outstanding': self.queryset.filter(status='disbursed').aggregate(
                total=Sum('outstanding_balance')
            )['total'] or Decimal('0')
        }
        
        return Response(stats)


class LoanPaymentViewSet(viewsets.ModelViewSet):
    """ViewSet pour les remboursements de prêts."""
    queryset = LoanPayment.objects.select_related('loan__member__user', 'loan')
    serializer_class = LoanPaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['loan', 'payment_method']
    ordering_fields = ['payment_date', 'amount']
    ordering = ['-payment_date']


class BudgetViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des budgets."""
    queryset = Budget.objects.prefetch_related('lines__account')
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['name', 'description']
    ordering_fields = ['start_date', 'name']
    ordering = ['-start_date']
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activer un budget."""
        budget = self.get_object()
        budget.status = 'active'
        budget.save()
        return Response({'message': 'Budget activé avec succès'})
    
    @action(detail=True, methods=['get'])
    def variance_report(self, request, pk=None):
        """Rapport des écarts budgétaires."""
        budget = self.get_object()
        
        # Statistiques des écarts
        lines = budget.lines.all()
        
        variances = []
        for line in lines:
            variance = line.actual_amount - line.budgeted_amount
            if line.budgeted_amount > 0:
                variance_percent = (variance / line.budgeted_amount) * 100
                variances.append({
                    'account': line.account.name,
                    'budgeted': line.budgeted_amount,
                    'actual': line.actual_amount,
                    'variance': variance,
                    'variance_percent': variance_percent
                })
        
        return Response({
            'budget': BudgetSerializer(budget).data,
            'line_variances': variances
        })


class BudgetLineViewSet(viewsets.ModelViewSet):
    """ViewSet pour les lignes budgétaires."""
    queryset = BudgetLine.objects.select_related('budget', 'account')
    serializer_class = BudgetLineSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['budget', 'account']
    ordering_fields = ['account__name']
    ordering = ['account__name']