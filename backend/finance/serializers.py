from rest_framework import serializers
from .models import (
    Account, FinancialTransaction, MemberSavings, Loan,
    LoanPayment, Budget, BudgetLine
)


class AccountSerializer(serializers.ModelSerializer):
    """Serializer pour les comptes."""
    balance = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    
    class Meta:
        model = Account
        fields = [
            'id', 'code', 'name', 'account_type', 
            'balance', 'description', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ('id', 'balance', 'created_at', 'updated_at')


class FinancialTransactionSerializer(serializers.ModelSerializer):
    """Serializer pour les transactions financières."""
    debit_account_name = serializers.CharField(source='debit_account.name', read_only=True)
    credit_account_name = serializers.CharField(source='credit_account.name', read_only=True)
    
    class Meta:
        model = FinancialTransaction
        fields = [
            'id', 'reference', 'date', 'debit_account', 'debit_account_name',
            'credit_account', 'credit_account_name', 'amount', 'description',
            'transaction_type', 'created_by', 'created_at'
        ]
        read_only_fields = ('id', 'created_at')
    
    def validate(self, attrs):
        debit_account = attrs.get('debit_account')
        credit_account = attrs.get('credit_account')
        
        if debit_account == credit_account:
            raise serializers.ValidationError(
                "Le compte de débit et de crédit ne peuvent pas être identiques"
            )
        
        return attrs


class MemberSavingsSerializer(serializers.ModelSerializer):
    """Serializer pour l'épargne des membres."""
    member_name = serializers.CharField(source='member.user.get_full_name', read_only=True)
    
    class Meta:
        model = MemberSavings
        fields = [
            'id', 'member', 'member_name', 'savings_type', 'balance',
            'interest_rate', 'minimum_balance', 'created_at', 'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')


class LoanPaymentSerializer(serializers.ModelSerializer):
    """Serializer pour les remboursements de prêts."""
    loan_number = serializers.CharField(source='loan.loan_number', read_only=True)
    
    class Meta:
        model = LoanPayment
        fields = [
            'id', 'loan', 'loan_number', 'payment_date', 'amount',
            'payment_method', 'reference', 'notes', 'created_at'
        ]
        read_only_fields = ('id', 'created_at')


class LoanSerializer(serializers.ModelSerializer):
    """Serializer pour les prêts."""
    member_name = serializers.CharField(source='member.user.get_full_name', read_only=True)
    payments = LoanPaymentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Loan
        fields = [
            'id', 'loan_number', 'member', 'member_name', 'amount',
            'interest_rate', 'duration_months', 'monthly_payment',
            'loan_date', 'due_date', 'status', 'purpose',
            'approved_by', 'approved_date', 'disbursement_date',
            'outstanding_balance', 'payments', 'created_at', 'updated_at'
        ]
        read_only_fields = (
            'id', 'loan_number', 'monthly_payment', 'due_date', 
            'outstanding_balance', 'created_at', 'updated_at'
        )
    
    def validate(self, attrs):
        amount = attrs.get('amount')
        
        if amount and amount <= 0:
            raise serializers.ValidationError(
                "Le montant du prêt doit être supérieur à zéro"
            )
        
        return attrs


class BudgetLineSerializer(serializers.ModelSerializer):
    """Serializer pour les lignes de budget."""
    account_name = serializers.CharField(source='account.name', read_only=True)
    
    class Meta:
        model = BudgetLine
        fields = [
            'id', 'budget', 'account', 'account_name', 'budgeted_amount',
            'actual_amount', 'notes'
        ]
        read_only_fields = ('id', 'actual_amount')


class BudgetSerializer(serializers.ModelSerializer):
    """Serializer pour les budgets."""
    lines = BudgetLineSerializer(many=True, required=False)
    total_budgeted = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    total_actual = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    
    class Meta:
        model = Budget
        fields = [
            'id', 'name', 'description', 'start_date', 'end_date',
            'status', 'total_budgeted', 'total_actual', 'lines',
            'created_at', 'updated_at'
        ]
        read_only_fields = ('id', 'total_budgeted', 'total_actual', 'created_at', 'updated_at')
    
    def create(self, validated_data):
        lines_data = validated_data.pop('lines', [])
        budget = Budget.objects.create(**validated_data)
        
        for line_data in lines_data:
            BudgetLine.objects.create(budget=budget, **line_data)
        
        return budget