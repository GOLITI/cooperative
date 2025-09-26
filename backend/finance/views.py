"""
Vues API pour la gestion financière.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Q, Avg, F
from django.utils import timezone
from datetime import datetime, timedelta
from accounts.permissions import CanViewFinances, CanManageFinances, CanValidateTransactions

from .models import (
    AccountCategory, Account, FinancialTransaction, 
    MemberLoan, MemberSavings
)
from .serializers import (
    AccountCategorySerializer, AccountSerializer, AccountListSerializer,
    FinancialTransactionSerializer, FinancialTransactionListSerializer,
    MemberLoanSerializer, MemberLoanListSerializer,
    MemberSavingsSerializer, MemberSavingsListSerializer,
    FinancialStatsSerializer
)


class AccountCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des catégories de comptes.
    """
    queryset = AccountCategory.objects.all()
    serializer_class = AccountCategorySerializer
    permission_classes = [IsAuthenticated, CanViewFinances]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['parent']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['code']
    
    def get_permissions(self):
        """Permissions selon l'action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, CanManageFinances]
        else:
            permission_classes = [IsAuthenticated, CanViewFinances]
        return [permission() for permission in permission_classes]


class AccountViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des comptes comptables.
    """
    queryset = Account.objects.select_related('category')
    permission_classes = [IsAuthenticated, CanViewFinances]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['account_type', 'category', 'is_system']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'account_type', 'current_balance', 'created_at']
    ordering = ['code']
    
    def get_serializer_class(self):
        """Sélection du sérialiseur selon l'action."""
        if self.action == 'list':
            return AccountListSerializer
        return AccountSerializer
    
    def get_permissions(self):
        """Permissions selon l'action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, CanManageFinances]
        else:
            permission_classes = [IsAuthenticated, CanViewFinances]
        return [permission() for permission in permission_classes]
    
    def destroy(self, request, *args, **kwargs):
        """Empêcher la suppression des comptes système."""
        instance = self.get_object()
        if instance.is_system:
            return Response(
                {'error': 'Les comptes système ne peuvent pas être supprimés'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        """Historique des transactions du compte."""
        account = self.get_object()
        
        # Transactions au débit et au crédit
        debit_transactions = account.debit_transactions.all()
        credit_transactions = account.credit_transactions.all()
        
        # Combinaison et tri par date
        all_transactions = list(debit_transactions) + list(credit_transactions)
        all_transactions.sort(key=lambda x: x.transaction_date, reverse=True)
        
        serializer = FinancialTransactionListSerializer(all_transactions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def balance_sheet(self, request):
        """Bilan comptable simplifié."""
        # Actifs
        assets = Account.objects.filter(account_type='asset').aggregate(
            total=Sum('current_balance')
        )['total'] or 0
        
        # Passifs
        liabilities = Account.objects.filter(account_type='liability').aggregate(
            total=Sum('current_balance')
        )['total'] or 0
        
        # Capitaux propres
        equity = Account.objects.filter(account_type='equity').aggregate(
            total=Sum('current_balance')
        )['total'] or 0
        
        return Response({
            'assets': assets,
            'liabilities': abs(liabilities),  # Valeur absolue pour l'affichage
            'equity': abs(equity),
            'balance_check': assets + liabilities + equity,  # Doit être proche de 0
            'as_of_date': timezone.now().date()
        })
    
    @action(detail=False, methods=['get'])
    def income_statement(self, request):
        """Compte de résultat simplifié."""
        # Période (par défaut: année en cours)
        year = int(request.query_params.get('year', timezone.now().year))
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31)
        
        # Revenus (produits)
        revenues = FinancialTransaction.objects.filter(
            credit_account__account_type='revenue',
            transaction_date__year=year
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Charges (dépenses)
        expenses = FinancialTransaction.objects.filter(
            debit_account__account_type='expense',
            transaction_date__year=year
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Résultat net
        net_income = revenues - expenses
        
        return Response({
            'revenues': revenues,
            'expenses': expenses,
            'net_income': net_income,
            'period': f'{year}',
            'start_date': start_date.date(),
            'end_date': end_date.date()
        })


class FinancialTransactionViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des transactions financières.
    """
    queryset = FinancialTransaction.objects.select_related(
        'debit_account', 'credit_account', 'member', 'sale', 'created_by', 'validated_by'
    )
    permission_classes = [IsAuthenticated, CanViewFinances]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'transaction_type', 'source', 'debit_account', 'credit_account', 
        'member', 'is_reconciled'
    ]
    search_fields = ['transaction_number', 'description', 'reference']
    ordering_fields = ['transaction_date', 'amount', 'created_at']
    ordering = ['-transaction_date']
    
    def get_serializer_class(self):
        """Sélection du sérialiseur selon l'action."""
        if self.action == 'list':
            return FinancialTransactionListSerializer
        return FinancialTransactionSerializer
    
    def get_permissions(self):
        """Permissions selon l'action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, CanManageFinances]
        elif self.action in ['validate_transaction', 'reconcile']:
            permission_classes = [IsAuthenticated, CanValidateTransactions]
        else:
            permission_classes = [IsAuthenticated, CanViewFinances]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """Assignation du créateur lors de la création."""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def validate_transaction(self, request, pk=None):
        """Valider une transaction."""
        transaction = self.get_object()
        
        if transaction.validated_at:
            return Response(
                {'error': 'Cette transaction est déjà validée'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        transaction.validated_by = request.user
        transaction.validated_at = timezone.now()
        transaction.save()
        
        return Response({'message': 'Transaction validée avec succès'})
    
    @action(detail=True, methods=['post'])
    def reconcile(self, request, pk=None):
        """Marquer une transaction comme rapprochée."""
        transaction = self.get_object()
        transaction.is_reconciled = True
        transaction.save()
        
        return Response({'message': 'Transaction rapprochée'})
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Statistiques des transactions."""
        # Période de calcul
        period = request.query_params.get('period', '30')  # 30 jours par défaut
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=int(period))
        
        # Filtrage des transactions
        transactions_qs = FinancialTransaction.objects.filter(
            transaction_date__date__gte=start_date,
            transaction_date__date__lte=end_date
        )
        
        # Calculs de base
        total_transactions = transactions_qs.count()
        total_amount = transactions_qs.aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Transactions par type
        transactions_by_type = {}
        for choice in FinancialTransaction.TRANSACTION_TYPE_CHOICES:
            type_key = choice[0]
            count = transactions_qs.filter(transaction_type=type_key).count()
            amount = transactions_qs.filter(transaction_type=type_key).aggregate(
                Sum('amount')
            )['amount__sum'] or 0
            transactions_by_type[type_key] = {'count': count, 'amount': amount}
        
        # Transactions mensuelles (12 derniers mois)
        monthly_transactions = []
        for i in range(12):
            month_start = end_date.replace(day=1) - timedelta(days=i*30)
            month_end = month_start + timedelta(days=30)
            month_total = FinancialTransaction.objects.filter(
                transaction_date__date__gte=month_start,
                transaction_date__date__lt=month_end
            ).aggregate(Sum('amount'))['amount__sum'] or 0
            
            monthly_transactions.append({
                'month': month_start.strftime('%Y-%m'),
                'total': month_total
            })
        
        return Response({
            'total_transactions': total_transactions,
            'total_amount': total_amount,
            'transactions_by_type': transactions_by_type,
            'monthly_transactions': monthly_transactions,
            'period_start': start_date,
            'period_end': end_date
        })


class MemberLoanViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des prêts aux membres.
    """
    queryset = MemberLoan.objects.select_related('member', 'approved_by')
    permission_classes = [IsAuthenticated, CanViewFinances]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'member', 'approved_by']
    search_fields = ['loan_number', 'member__full_name', 'purpose']
    ordering_fields = ['application_date', 'approved_amount', 'status']
    ordering = ['-application_date']
    
    def get_serializer_class(self):
        """Sélection du sérialiseur selon l'action."""
        if self.action == 'list':
            return MemberLoanListSerializer
        return MemberLoanSerializer
    
    def get_permissions(self):
        """Permissions selon l'action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, CanManageFinances]
        elif self.action in ['approve', 'disburse', 'record_payment']:
            permission_classes = [IsAuthenticated, CanValidateTransactions]
        else:
            permission_classes = [IsAuthenticated, CanViewFinances]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approuver un prêt."""
        loan = self.get_object()
        
        if loan.status != 'pending':
            return Response(
                {'error': 'Seuls les prêts en attente peuvent être approuvés'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        approved_amount = request.data.get('approved_amount', loan.requested_amount)
        
        loan.status = 'approved'
        loan.approved_amount = approved_amount
        loan.approval_date = timezone.now().date()
        loan.approved_by = request.user
        loan.save()
        
        return Response({'message': 'Prêt approuvé avec succès'})
    
    @action(detail=True, methods=['post'])
    def disburse(self, request, pk=None):
        """Débourser un prêt (créer la transaction)."""
        loan = self.get_object()
        
        if loan.status != 'approved':
            return Response(
                {'error': 'Seuls les prêts approuvés peuvent être déboursés'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Créer la transaction de déboursement
        # TODO: Implémenter la logique de déboursement avec comptes comptables
        
        loan.status = 'disbursed'
        loan.disbursement_date = timezone.now().date()
        loan.outstanding_balance = loan.approved_amount
        loan.save()
        
        return Response({'message': 'Prêt déboursé avec succès'})
    
    @action(detail=True, methods=['post'])
    def record_payment(self, request, pk=None):
        """Enregistrer un remboursement."""
        loan = self.get_object()
        payment_amount = request.data.get('amount', 0)
        
        if payment_amount <= 0:
            return Response(
                {'error': 'Le montant doit être positif'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if payment_amount > loan.outstanding_balance:
            return Response(
                {'error': 'Le montant ne peut pas dépasser le solde restant'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mettre à jour le solde
        loan.outstanding_balance -= payment_amount
        if loan.outstanding_balance <= 0:
            loan.status = 'completed'
        
        loan.save()
        
        return Response({
            'message': 'Paiement enregistré avec succès',
            'remaining_balance': loan.outstanding_balance
        })


class MemberSavingsViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion de l'épargne des membres.
    """
    queryset = MemberSavings.objects.select_related('member')
    permission_classes = [IsAuthenticated, CanViewFinances]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['savings_type', 'member']
    search_fields = ['member__full_name']
    ordering_fields = ['opening_date', 'current_balance', 'member__full_name']
    ordering = ['-current_balance']
    
    def get_serializer_class(self):
        """Sélection du sérialiseur selon l'action."""
        if self.action == 'list':
            return MemberSavingsListSerializer
        return MemberSavingsSerializer
    
    def get_permissions(self):
        """Permissions selon l'action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, CanManageFinances]
        elif self.action in ['deposit', 'withdraw', 'capitalize_interest']:
            permission_classes = [IsAuthenticated, CanValidateTransactions]
        else:
            permission_classes = [IsAuthenticated, CanViewFinances]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['post'])
    def deposit(self, request, pk=None):
        """Effectuer un dépôt."""
        savings = self.get_object()
        amount = request.data.get('amount', 0)
        
        if amount <= 0:
            return Response(
                {'error': 'Le montant doit être positif'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mettre à jour le solde
        savings.current_balance += amount
        savings.save()
        
        return Response({
            'message': 'Dépôt effectué avec succès',
            'new_balance': savings.current_balance
        })
    
    @action(detail=True, methods=['post'])
    def withdraw(self, request, pk=None):
        """Effectuer un retrait."""
        savings = self.get_object()
        amount = request.data.get('amount', 0)
        
        if amount <= 0:
            return Response(
                {'error': 'Le montant doit être positif'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifier le solde minimum
        if (savings.current_balance - amount) < savings.minimum_balance:
            return Response(
                {'error': f'Le solde minimum de {savings.minimum_balance} doit être maintenu'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mettre à jour le solde
        savings.current_balance -= amount
        savings.save()
        
        return Response({
            'message': 'Retrait effectué avec succès',
            'new_balance': savings.current_balance
        })
    
    @action(detail=True, methods=['post'])
    def capitalize_interest(self, request, pk=None):
        """Capitaliser les intérêts."""
        savings = self.get_object()
        
        if savings.interest_rate <= 0:
            return Response(
                {'error': 'Aucun taux d\'intérêt configuré'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculer les intérêts
        last_date = savings.last_interest_date or savings.opening_date
        days = (timezone.now().date() - last_date).days
        
        if days < 30:  # Capitalisation mensuelle minimum
            return Response(
                {'error': 'La capitalisation ne peut se faire qu\'une fois par mois'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        annual_interest = savings.current_balance * (savings.interest_rate / 100)
        interest_amount = annual_interest * (days / 365)
        
        # Ajouter les intérêts au solde
        savings.current_balance += interest_amount
        savings.last_interest_date = timezone.now().date()
        savings.save()
        
        return Response({
            'message': 'Intérêts capitalisés avec succès',
            'interest_amount': interest_amount,
            'new_balance': savings.current_balance
        })
