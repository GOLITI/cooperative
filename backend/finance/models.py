from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from core.models import TimestampedModel, SoftDeleteModel
from members.models import Member

class Account(SoftDeleteModel):
    """Comptes comptables"""
    code = models.CharField(max_length=20, unique=True, verbose_name="Code comptable")
    name = models.CharField(max_length=200, verbose_name="Nom du compte")
    account_type = models.CharField(
        max_length=20,
        choices=[
            ('asset', 'Actif'),
            ('liability', 'Passif'),
            ('equity', 'Capitaux propres'),
            ('revenue', 'Produits'),
            ('expense', 'Charges')
        ],
        verbose_name="Type de compte"
    )
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, verbose_name="Compte parent")
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Solde")
    is_reconcilable = models.BooleanField(default=False, verbose_name="Rapprochable")
    
    class Meta:
        verbose_name = "Compte"
        verbose_name_plural = "Comptes"
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class FinancialTransaction(TimestampedModel):
    """Transactions financières"""
    transaction_number = models.CharField(max_length=20, unique=True, verbose_name="Numéro de transaction")
    date = models.DateField(verbose_name="Date")
    description = models.CharField(max_length=255, verbose_name="Description")
    
    transaction_type = models.CharField(
        max_length=20,
        choices=[
            ('income', 'Recette'),
            ('expense', 'Dépense'),
            ('transfer', 'Transfert'),
            ('loan', 'Prêt'),
            ('loan_repayment', 'Remboursement prêt'),
            ('membership_fee', 'Cotisation'),
            ('dividend', 'Dividende')
        ],
        verbose_name="Type de transaction"
    )
    
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Montant")
    
    # Comptes de débit et crédit
    debit_account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='debit_transactions', verbose_name="Compte débit")
    credit_account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='credit_transactions', verbose_name="Compte crédit")
    
    # Références
    reference_type = models.CharField(
        max_length=20,
        choices=[
            ('sale', 'Vente'),
            ('purchase', 'Achat'),
            ('member_fee', 'Cotisation membre'),
            ('loan', 'Prêt'),
            ('other', 'Autre')
        ],
        blank=True,
        verbose_name="Type de référence"
    )
    reference_id = models.PositiveIntegerField(null=True, blank=True, verbose_name="ID de référence")
    
    # Métadonnées
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Créé par")
    notes = models.TextField(blank=True, verbose_name="Notes")
    is_reconciled = models.BooleanField(default=False, verbose_name="Rapproché")
    
    class Meta:
        verbose_name = "Transaction financière"
        verbose_name_plural = "Transactions financières"
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"{self.transaction_number} - {self.description}"

class MemberSavings(TimestampedModel):
    """Épargne des membres"""
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='savings', verbose_name="Membre")
    account_number = models.CharField(max_length=20, unique=True, verbose_name="Numéro de compte")
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Solde")
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=2, verbose_name="Taux d'intérêt (%)")
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Actif'),
            ('suspended', 'Suspendu'),
            ('closed', 'Fermé')
        ],
        default='active',
        verbose_name="Statut"
    )
    
    opening_date = models.DateField(verbose_name="Date d'ouverture")
    closing_date = models.DateField(null=True, blank=True, verbose_name="Date de fermeture")
    
    class Meta:
        verbose_name = "Épargne membre"
        verbose_name_plural = "Épargnes des membres"
    
    def __str__(self):
        return f"{self.account_number} - {self.member}"

class SavingsTransaction(TimestampedModel):
    """Transactions d'épargne"""
    savings_account = models.ForeignKey(MemberSavings, on_delete=models.CASCADE, related_name='transactions', verbose_name="Compte d'épargne")
    transaction_type = models.CharField(
        max_length=20,
        choices=[
            ('deposit', 'Dépôt'),
            ('withdrawal', 'Retrait'),
            ('interest', 'Intérêts'),
            ('fee', 'Frais')
        ],
        verbose_name="Type de transaction"
    )
    
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Montant")
    balance_after = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Solde après")
    description = models.CharField(max_length=255, verbose_name="Description")
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Traité par")
    
    class Meta:
        verbose_name = "Transaction d'épargne"
        verbose_name_plural = "Transactions d'épargne"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.savings_account.account_number} - {self.get_transaction_type_display()} - {self.amount}"

class Loan(TimestampedModel):
    """Prêts aux membres"""
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='loans', verbose_name="Membre")
    loan_number = models.CharField(max_length=20, unique=True, verbose_name="Numéro de prêt")
    
    # Montants
    principal_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Montant principal")
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Taux d'intérêt (%)")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Montant total")
    
    # Dates
    application_date = models.DateField(verbose_name="Date de demande")
    approval_date = models.DateField(null=True, blank=True, verbose_name="Date d'approbation")
    disbursement_date = models.DateField(null=True, blank=True, verbose_name="Date de déblocage")
    due_date = models.DateField(verbose_name="Date d'échéance")
    
    # Statut
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'En attente'),
            ('approved', 'Approuvé'),
            ('disbursed', 'Débloqué'),
            ('active', 'Actif'),
            ('completed', 'Terminé'),
            ('defaulted', 'En défaut'),
            ('cancelled', 'Annulé')
        ],
        default='pending',
        verbose_name="Statut"
    )
    
    # Remboursement
    monthly_payment = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Paiement mensuel")
    balance_remaining = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Solde restant")
    
    # Garanties
    guarantor1 = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True, related_name='guaranteed_loans1', verbose_name="Garant 1")
    guarantor2 = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True, related_name='guaranteed_loans2', verbose_name="Garant 2")
    collateral_description = models.TextField(blank=True, verbose_name="Description des garanties")
    
    # Métadonnées
    purpose = models.TextField(verbose_name="Objet du prêt")
    notes = models.TextField(blank=True, verbose_name="Notes")
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Approuvé par")
    
    class Meta:
        verbose_name = "Prêt"
        verbose_name_plural = "Prêts"
        ordering = ['-application_date']
    
    def __str__(self):
        return f"{self.loan_number} - {self.member}"
    
    @property
    def is_overdue(self):
        from django.utils import timezone
        return self.due_date < timezone.now().date() and self.balance_remaining > 0

class LoanPayment(TimestampedModel):
    """Remboursements de prêts"""
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='payments', verbose_name="Prêt")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant")
    payment_date = models.DateField(verbose_name="Date de paiement")
    
    # Répartition
    principal_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Capital")
    interest_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Intérêts")
    penalty_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Pénalités")
    
    balance_after = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Solde après")
    receipt_number = models.CharField(max_length=50, unique=True, verbose_name="Numéro de reçu")
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Reçu par")
    notes = models.TextField(blank=True, verbose_name="Notes")
    
    class Meta:
        verbose_name = "Remboursement de prêt"
        verbose_name_plural = "Remboursements de prêts"
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"{self.loan.loan_number} - {self.amount} - {self.payment_date}"

class Budget(TimestampedModel):
    """Budgets prévisionnels"""
    name = models.CharField(max_length=200, verbose_name="Nom du budget")
    description = models.TextField(blank=True, verbose_name="Description")
    
    # Période
    start_date = models.DateField(verbose_name="Date de début")
    end_date = models.DateField(verbose_name="Date de fin")
    
    # Montants
    total_revenue_budget = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Budget recettes")
    total_expense_budget = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Budget dépenses")
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Brouillon'),
            ('active', 'Actif'),
            ('closed', 'Fermé')
        ],
        default='draft',
        verbose_name="Statut"
    )
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Créé par")
    
    class Meta:
        verbose_name = "Budget"
        verbose_name_plural = "Budgets"
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.name} ({self.start_date} - {self.end_date})"

class BudgetLine(TimestampedModel):
    """Lignes de budget"""
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='lines', verbose_name="Budget")
    account = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name="Compte")
    budgeted_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Montant budgété")
    actual_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Montant réel")
    notes = models.TextField(blank=True, verbose_name="Notes")
    
    class Meta:
        verbose_name = "Ligne de budget"
        verbose_name_plural = "Lignes de budget"
        unique_together = ['budget', 'account']
    
    def __str__(self):
        return f"{self.budget.name} - {self.account.name}"
    
    @property
    def variance(self):
        return self.actual_amount - self.budgeted_amount
    
    @property
    def variance_percentage(self):
        if self.budgeted_amount == 0:
            return 0
        return (self.variance / self.budgeted_amount) * 100
