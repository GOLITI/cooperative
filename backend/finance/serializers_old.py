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
            'id', 'name', 'account_number', 'account_type', 
            'balance', 'description', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ('id', 'balance', 'created_at', 'updated_at')


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer pour les transactions."""
    debit_account_name = serializers.CharField(source='debit_account.name', read_only=True)
    credit_account_name = serializers.CharField(source='credit_account.name', read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'transaction_number', 'date', 'debit_account', 'debit_account_name',
            'credit_account', 'credit_account_name', 'amount', 'description',
            'reference', 'created_by', 'created_at'
        ]
        read_only_fields = ('id', 'transaction_number', 'created_at')
    
    def validate(self, attrs):
        debit_account = attrs.get('debit_account')
        credit_account = attrs.get('credit_account')
        
        if debit_account == credit_account:
            raise serializers.ValidationError(
                "Le compte de débit et de crédit ne peuvent pas être identiques"
            )
        
        return attrs


class MemberSavingSerializer(serializers.ModelSerializer):
    """Serializer pour l'épargne des membres."""
    member_name = serializers.CharField(source='member.user.get_full_name', read_only=True)
    total_savings = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    
    class Meta:
        model = MemberSaving
        fields = [
            'id', 'member', 'member_name', 'saving_type', 'amount',
            'date', 'description', 'total_savings', 'created_at'
        ]
        read_only_fields = ('id', 'total_savings', 'created_at')


class LoanTypeSerializer(serializers.ModelSerializer):
    """Serializer pour les types de prêts."""
    
    class Meta:
        model = LoanType
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class LoanPaymentSerializer(serializers.ModelSerializer):
    """Serializer pour les remboursements de prêts."""
    loan_number = serializers.CharField(source='loan.loan_number', read_only=True)
    
    class Meta:
        model = LoanPayment
        fields = [
            'id', 'loan', 'loan_number', 'payment_date', 'principal_amount',
            'interest_amount', 'total_amount', 'payment_method',
            'reference', 'notes', 'created_at'
        ]
        read_only_fields = ('id', 'created_at')


class LoanSerializer(serializers.ModelSerializer):
    """Serializer pour les prêts."""
    member_name = serializers.CharField(source='member.user.get_full_name', read_only=True)
    loan_type_name = serializers.CharField(source='loan_type.name', read_only=True)
    payments = LoanPaymentSerializer(many=True, read_only=True)
    remaining_balance = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    
    class Meta:
        model = Loan
        fields = [
            'id', 'loan_number', 'member', 'member_name', 'loan_type', 'loan_type_name',
            'principal_amount', 'interest_rate', 'term_months', 'monthly_payment',
            'start_date', 'end_date', 'status', 'purpose', 'collateral',
            'approved_by', 'approved_date', 'disbursed_date', 'remaining_balance',
            'payments', 'created_at', 'updated_at'
        ]
        read_only_fields = (
            'id', 'loan_number', 'monthly_payment', 'end_date', 
            'remaining_balance', 'created_at', 'updated_at'
        )
    
    def validate(self, attrs):
        principal_amount = attrs.get('principal_amount')
        loan_type = attrs.get('loan_type')
        
        if loan_type and principal_amount:
            if principal_amount > loan_type.maximum_amount:
                raise serializers.ValidationError(
                    f"Le montant du prêt ne peut pas dépasser {loan_type.maximum_amount}"
                )
            if principal_amount < loan_type.minimum_amount:
                raise serializers.ValidationError(
                    f"Le montant du prêt ne peut pas être inférieur à {loan_type.minimum_amount}"
                )
        
        return attrs


class BudgetLineSerializer(serializers.ModelSerializer):
    """Serializer pour les lignes de budget."""
    account_name = serializers.CharField(source='account.name', read_only=True)
    
    class Meta:
        model = BudgetLine
        fields = [
            'id', 'account', 'account_name', 'planned_amount',
            'actual_amount', 'variance', 'notes'
        ]
        read_only_fields = ('id', 'actual_amount', 'variance')


class BudgetSerializer(serializers.ModelSerializer):
    """Serializer pour les budgets."""
    lines = BudgetLineSerializer(many=True, required=False)
    total_planned = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    total_actual = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    
    class Meta:
        model = Budget
        fields = [
            'id', 'name', 'description', 'start_date', 'end_date',
            'status', 'total_planned', 'total_actual', 'lines',
            'created_at', 'updated_at'
        ]
        read_only_fields = ('id', 'total_planned', 'total_actual', 'created_at', 'updated_at')
    
    def create(self, validated_data):
        lines_data = validated_data.pop('lines', [])
        budget = Budget.objects.create(**validated_data)
        
        for line_data in lines_data:
            BudgetLine.objects.create(budget=budget, **line_data)
        
        return budget


class FinancialYearSerializer(serializers.ModelSerializer):
    """Serializer pour les exercices financiers."""
    
    class Meta:
        model = FinancialYear
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def validate(self, attrs):
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        
        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError(
                "La date de début doit être antérieure à la date de fin"
            )
        
        return attrs