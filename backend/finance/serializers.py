"""
Sérialiseurs pour l'API financière.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from members.models import Member
from sales.models import Sale
from .models import (
    AccountCategory, Account, FinancialTransaction, 
    MemberLoan, MemberSavings
)


class AccountCategorySerializer(serializers.ModelSerializer):
    """Sérialiseur pour les catégories de comptes."""
    
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    subcategories_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AccountCategory
        fields = [
            'id', 'name', 'code', 'description', 'parent', 
            'parent_name', 'subcategories_count', 'created_at', 'updated_at'
        ]
    
    def get_subcategories_count(self, obj):
        """Nombre de sous-catégories."""
        return obj.subcategories.count()


class AccountSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les comptes comptables."""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    balance_display = serializers.ReadOnlyField()
    debit_transactions_count = serializers.SerializerMethodField()
    credit_transactions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Account
        fields = [
            'id', 'name', 'code', 'account_type', 'category', 'category_name',
            'description', 'is_system', 'current_balance', 'balance_display',
            'debit_transactions_count', 'credit_transactions_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['current_balance']
    
    def get_debit_transactions_count(self, obj):
        """Nombre de transactions au débit."""
        return obj.debit_transactions.count()
    
    def get_credit_transactions_count(self, obj):
        """Nombre de transactions au crédit."""
        return obj.credit_transactions.count()


class AccountListSerializer(serializers.ModelSerializer):
    """Sérialiseur simplifié pour la liste des comptes."""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    balance_display = serializers.ReadOnlyField()
    
    class Meta:
        model = Account
        fields = [
            'id', 'name', 'code', 'account_type', 'category_name',
            'current_balance', 'balance_display', 'is_system'
        ]


class FinancialTransactionSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les transactions financières."""
    
    # Relations
    debit_account_name = serializers.CharField(source='debit_account.name', read_only=True)
    debit_account_code = serializers.CharField(source='debit_account.code', read_only=True)
    credit_account_name = serializers.CharField(source='credit_account.name', read_only=True)
    credit_account_code = serializers.CharField(source='credit_account.code', read_only=True)
    member_name = serializers.CharField(source='member.full_name', read_only=True)
    sale_number = serializers.CharField(source='sale.sale_number', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    validated_by_name = serializers.CharField(source='validated_by.username', read_only=True)
    
    class Meta:
        model = FinancialTransaction
        fields = [
            'id', 'transaction_number', 'transaction_type', 'source', 'amount',
            'debit_account', 'debit_account_name', 'debit_account_code',
            'credit_account', 'credit_account_name', 'credit_account_code',
            'transaction_date', 'value_date', 'description', 'reference',
            'external_reference', 'member', 'member_name', 'sale', 'sale_number',
            'created_by', 'created_by_name', 'validated_by', 'validated_by_name',
            'validated_at', 'is_reconciled', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'transaction_number', 'created_by', 'validated_by', 'validated_at'
        ]
    
    def validate(self, data):
        """Validation des comptes et montants."""
        debit_account = data.get('debit_account')
        credit_account = data.get('credit_account')
        
        # Vérifier que les comptes sont différents
        if debit_account == credit_account:
            raise serializers.ValidationError(
                "Le compte débité et crédité ne peuvent pas être identiques."
            )
        
        # Vérifier que les comptes système ne sont pas modifiés manuellement
        if self.context.get('request') and self.context['request'].method == 'POST':
            if debit_account and debit_account.is_system and data.get('source') == 'manual':
                raise serializers.ValidationError(
                    f"Le compte {debit_account.code} est un compte système."
                )
            if credit_account and credit_account.is_system and data.get('source') == 'manual':
                raise serializers.ValidationError(
                    f"Le compte {credit_account.code} est un compte système."
                )
        
        return data


class FinancialTransactionListSerializer(serializers.ModelSerializer):
    """Sérialiseur simplifié pour la liste des transactions."""
    
    debit_account_code = serializers.CharField(source='debit_account.code', read_only=True)
    credit_account_code = serializers.CharField(source='credit_account.code', read_only=True)
    member_name = serializers.CharField(source='member.full_name', read_only=True)
    
    class Meta:
        model = FinancialTransaction
        fields = [
            'id', 'transaction_number', 'transaction_type', 'amount',
            'debit_account_code', 'credit_account_code', 'transaction_date',
            'description', 'member_name', 'is_reconciled', 'validated_at'
        ]


class MemberLoanSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les prêts aux membres."""
    
    member_name = serializers.CharField(source='member.full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.username', read_only=True)
    monthly_payment = serializers.ReadOnlyField()
    total_to_repay = serializers.SerializerMethodField()
    payments_made = serializers.SerializerMethodField()
    
    class Meta:
        model = MemberLoan
        fields = [
            'id', 'loan_number', 'member', 'member_name', 'requested_amount',
            'approved_amount', 'outstanding_balance', 'interest_rate',
            'term_months', 'application_date', 'approval_date',
            'disbursement_date', 'maturity_date', 'status', 'purpose',
            'notes', 'approved_by', 'approved_by_name', 'monthly_payment',
            'total_to_repay', 'payments_made', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'loan_number', 'outstanding_balance', 'approved_by',
            'approval_date', 'disbursement_date'
        ]
    
    def get_total_to_repay(self, obj):
        """Montant total à rembourser (capital + intérêts)."""
        if obj.approved_amount and obj.monthly_payment:
            return obj.monthly_payment * obj.term_months
        return obj.approved_amount or 0
    
    def get_payments_made(self, obj):
        """Montant des paiements déjà effectués."""
        if obj.approved_amount:
            return obj.approved_amount - obj.outstanding_balance
        return 0


class MemberLoanListSerializer(serializers.ModelSerializer):
    """Sérialiseur simplifié pour la liste des prêts."""
    
    member_name = serializers.CharField(source='member.full_name', read_only=True)
    monthly_payment = serializers.ReadOnlyField()
    
    class Meta:
        model = MemberLoan
        fields = [
            'id', 'loan_number', 'member_name', 'requested_amount',
            'approved_amount', 'outstanding_balance', 'interest_rate',
            'term_months', 'status', 'application_date', 'monthly_payment'
        ]


class MemberSavingsSerializer(serializers.ModelSerializer):
    """Sérialiseur pour l'épargne des membres."""
    
    member_name = serializers.CharField(source='member.full_name', read_only=True)
    accrued_interest = serializers.SerializerMethodField()
    days_since_opening = serializers.SerializerMethodField()
    
    class Meta:
        model = MemberSavings
        fields = [
            'id', 'member', 'member_name', 'savings_type', 'current_balance',
            'interest_rate', 'minimum_balance', 'opening_date', 'maturity_date',
            'last_interest_date', 'accrued_interest', 'days_since_opening',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['current_balance', 'last_interest_date']
    
    def get_accrued_interest(self, obj):
        """Intérêts courus depuis la dernière capitalisation."""
        if obj.current_balance > 0 and obj.interest_rate > 0:
            last_date = obj.last_interest_date or obj.opening_date
            days = (timezone.now().date() - last_date).days
            annual_interest = obj.current_balance * (obj.interest_rate / 100)
            return annual_interest * (days / 365)
        return 0
    
    def get_days_since_opening(self, obj):
        """Nombre de jours depuis l'ouverture."""
        return (timezone.now().date() - obj.opening_date).days


class MemberSavingsListSerializer(serializers.ModelSerializer):
    """Sérialiseur simplifié pour la liste des épargnes."""
    
    member_name = serializers.CharField(source='member.full_name', read_only=True)
    accrued_interest = serializers.SerializerMethodField()
    
    class Meta:
        model = MemberSavings
        fields = [
            'id', 'member_name', 'savings_type', 'current_balance',
            'interest_rate', 'opening_date', 'accrued_interest'
        ]
    
    def get_accrued_interest(self, obj):
        """Intérêts courus."""
        if obj.current_balance > 0 and obj.interest_rate > 0:
            last_date = obj.last_interest_date or obj.opening_date
            days = (timezone.now().date() - last_date).days
            annual_interest = obj.current_balance * (obj.interest_rate / 100)
            return annual_interest * (days / 365)
        return 0


# Sérialiseurs pour les statistiques financières
class FinancialStatsSerializer(serializers.Serializer):
    """Sérialiseur pour les statistiques financières."""
    
    # Comptes
    total_accounts = serializers.IntegerField()
    accounts_by_type = serializers.DictField()
    
    # Transactions
    total_transactions = serializers.IntegerField()
    transactions_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    transactions_by_type = serializers.DictField()
    monthly_transactions = serializers.ListField()
    
    # Prêts
    total_loans = serializers.IntegerField()
    active_loans = serializers.IntegerField()
    total_loan_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    outstanding_loan_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    
    # Épargne
    total_savings_accounts = serializers.IntegerField()
    total_savings_balance = serializers.DecimalField(max_digits=15, decimal_places=2)
    average_savings_balance = serializers.DecimalField(max_digits=15, decimal_places=2)
    
    # Ratios financiers
    liquidity_ratio = serializers.DecimalField(max_digits=5, decimal_places=2)
    loan_to_deposit_ratio = serializers.DecimalField(max_digits=5, decimal_places=2)