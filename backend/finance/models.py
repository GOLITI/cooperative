"""
Modèles pour la gestion financière et comptable.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.utils import timezone
from core.models import BaseModel
from decimal import Decimal


class AccountCategory(BaseModel):
    """
    Catégories de comptes comptables.
    """
    name = models.CharField(_("Nom de la catégorie"), max_length=100)
    code = models.CharField(_("Code"), max_length=10, unique=True)
    description = models.TextField(_("Description"), blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories',
        verbose_name=_("Catégorie parent")
    )
    
    class Meta:
        verbose_name = _("Catégorie de compte")
        verbose_name_plural = _("Catégories de comptes")
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Account(BaseModel):
    """
    Plan comptable simplifié pour les coopératives.
    """
    ACCOUNT_TYPE_CHOICES = [
        ('asset', _('Actif')),
        ('liability', _('Passif')),
        ('equity', _('Capitaux propres')),
        ('revenue', _('Produits')),
        ('expense', _('Charges')),
    ]
    
    # Identification
    name = models.CharField(_("Nom du compte"), max_length=200)
    code = models.CharField(_("Code comptable"), max_length=20, unique=True)
    account_type = models.CharField(
        _("Type de compte"),
        max_length=20,
        choices=ACCOUNT_TYPE_CHOICES
    )
    
    # Classification
    category = models.ForeignKey(
        AccountCategory,
        on_delete=models.PROTECT,
        verbose_name=_("Catégorie"),
        null=True,
        blank=True
    )
    
    # Propriétés
    description = models.TextField(_("Description"), blank=True)
    is_system = models.BooleanField(
        _("Compte système"),
        default=False,
        help_text=_("Ne peut pas être supprimé")
    )
    
    # Soldes
    current_balance = models.DecimalField(
        _("Solde actuel"),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    
    class Meta:
        verbose_name = _("Compte")
        verbose_name_plural = _("Comptes")
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @property
    def balance_display(self):
        """Affichage du solde selon le type de compte."""
        if self.account_type in ['asset', 'expense']:
            return self.current_balance  # Débit positif
        else:
            return -self.current_balance  # Crédit positif


class FinancialTransaction(BaseModel):
    """
    Transactions financières (recettes, dépenses, transferts).
    """
    TRANSACTION_TYPE_CHOICES = [
        ('income', _('Recette')),
        ('expense', _('Dépense')),
        ('transfer', _('Transfert')),
        ('adjustment', _('Ajustement')),
    ]
    
    TRANSACTION_SOURCE_CHOICES = [
        ('manual', _('Saisie manuelle')),
        ('sale', _('Vente')),
        ('purchase', _('Achat')),
        ('membership_fee', _('Cotisation')),
        ('loan', _('Prêt')),
        ('dividend', _('Dividende')),
        ('donation', _('Don')),
        ('other', _('Autre')),
    ]
    
    # Identification
    transaction_number = models.CharField(
        _("Numéro de transaction"),
        max_length=20,
        unique=True,
        help_text=_("Généré automatiquement")
    )
    
    # Type et source
    transaction_type = models.CharField(
        _("Type de transaction"),
        max_length=20,
        choices=TRANSACTION_TYPE_CHOICES
    )
    source = models.CharField(
        _("Source"),
        max_length=20,
        choices=TRANSACTION_SOURCE_CHOICES,
        default='manual'
    )
    
    # Montant et comptes
    amount = models.DecimalField(
        _("Montant"),
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    debit_account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name='debit_transactions',
        verbose_name=_("Compte débité")
    )
    credit_account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name='credit_transactions',
        verbose_name=_("Compte crédité")
    )
    
    # Dates
    transaction_date = models.DateTimeField(_("Date de transaction"), default=timezone.now)
    value_date = models.DateField(_("Date de valeur"), null=True, blank=True)
    
    # Description et références
    description = models.TextField(_("Description"))
    reference = models.CharField(_("Référence"), max_length=100, blank=True)
    external_reference = models.CharField(_("Référence externe"), max_length=100, blank=True)
    
    # Relations avec d'autres modules
    member = models.ForeignKey(
        'members.Member',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Membre concerné")
    )
    sale = models.ForeignKey(
        'sales.Sale',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Vente associée")
    )
    
    # Validation et approbation
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_transactions',
        verbose_name=_("Créé par")
    )
    validated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='validated_transactions',
        verbose_name=_("Validé par")
    )
    validated_at = models.DateTimeField(_("Validé le"), null=True, blank=True)
    is_reconciled = models.BooleanField(_("Rapproché"), default=False)
    
    class Meta:
        verbose_name = _("Transaction financière")
        verbose_name_plural = _("Transactions financières")
        ordering = ['-transaction_date']
        indexes = [
            models.Index(fields=['transaction_number']),
            models.Index(fields=['transaction_date']),
            models.Index(fields=['debit_account', 'transaction_date']),
            models.Index(fields=['credit_account', 'transaction_date']),
        ]
    
    def __str__(self):
        return f"{self.transaction_number} - {self.description}"
    
    def save(self, *args, **kwargs):
        """Génération automatique du numéro et mise à jour des soldes."""
        # Génération du numéro de transaction
        if not self.transaction_number:
            year = timezone.now().year
            month = timezone.now().month
            last_transaction = FinancialTransaction.objects.filter(
                transaction_number__startswith=f"TXN-{year}{month:02d}-"
            ).order_by('transaction_number').last()
            
            if last_transaction:
                last_number = int(last_transaction.transaction_number.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.transaction_number = f"TXN-{year}{month:02d}-{new_number:04d}"
        
        is_new = self._state.adding
        
        # Sauvegarde de la transaction
        super().save(*args, **kwargs)
        
        # Mise à jour des soldes des comptes
        if is_new:
            # Débit du compte débiteur
            self.debit_account.current_balance += self.amount
            self.debit_account.save()
            
            # Crédit du compte créditeur
            self.credit_account.current_balance -= self.amount
            self.credit_account.save()


class MemberLoan(BaseModel):
    """
    Prêts accordés aux membres.
    """
    LOAN_STATUS_CHOICES = [
        ('pending', _('En attente')),
        ('approved', _('Approuvé')),
        ('disbursed', _('Déboursé')),
        ('active', _('Actif')),
        ('completed', _('Remboursé')),
        ('defaulted', _('En défaut')),
        ('cancelled', _('Annulé')),
    ]
    
    # Informations de base
    loan_number = models.CharField(
        _("Numéro de prêt"),
        max_length=20,
        unique=True,
        help_text=_("Généré automatiquement")
    )
    member = models.ForeignKey(
        'members.Member',
        on_delete=models.CASCADE,
        related_name='loans',
        verbose_name=_("Membre")
    )
    
    # Montants
    requested_amount = models.DecimalField(
        _("Montant demandé"),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('1.00'))]
    )
    approved_amount = models.DecimalField(
        _("Montant approuvé"),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('1.00'))]
    )
    outstanding_balance = models.DecimalField(
        _("Solde restant"),
        max_digits=12,
        decimal_places=2,
        default=0
    )
    
    # Conditions du prêt
    interest_rate = models.DecimalField(
        _("Taux d'intérêt (%)"),
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    term_months = models.PositiveIntegerField(_("Durée (mois)"))
    
    # Dates importantes
    application_date = models.DateField(_("Date de demande"), default=timezone.now)
    approval_date = models.DateField(_("Date d'approbation"), null=True, blank=True)
    disbursement_date = models.DateField(_("Date de déboursement"), null=True, blank=True)
    maturity_date = models.DateField(_("Date d'échéance"), null=True, blank=True)
    
    # Statut et validation
    status = models.CharField(
        _("Statut"),
        max_length=20,
        choices=LOAN_STATUS_CHOICES,
        default='pending'
    )
    purpose = models.TextField(_("Objet du prêt"))
    notes = models.TextField(_("Notes"), blank=True)
    
    # Approbation
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Approuvé par")
    )
    
    class Meta:
        verbose_name = _("Prêt membre")
        verbose_name_plural = _("Prêts membres")
        ordering = ['-application_date']
    
    def __str__(self):
        return f"{self.loan_number} - {self.member.full_name}"
    
    @property
    def monthly_payment(self):
        """Calcul du paiement mensuel (approximatif)."""
        if self.approved_amount and self.term_months > 0:
            principal = float(self.approved_amount)
            rate = float(self.interest_rate) / 100 / 12  # Taux mensuel
            
            if rate > 0:
                # Formule d'annuité
                payment = principal * (rate * (1 + rate) ** self.term_months) / ((1 + rate) ** self.term_months - 1)
                return Decimal(str(payment))
            else:
                # Pas d'intérêts
                return self.approved_amount / self.term_months
        return 0
    
    def save(self, *args, **kwargs):
        """Génération automatique du numéro de prêt."""
        if not self.loan_number:
            year = timezone.now().year
            last_loan = MemberLoan.objects.filter(
                loan_number__startswith=f"PRT-{year}-"
            ).order_by('loan_number').last()
            
            if last_loan:
                last_number = int(last_loan.loan_number.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.loan_number = f"PRT-{year}-{new_number:04d}"
        
        super().save(*args, **kwargs)


class MemberSavings(BaseModel):
    """
    Épargne des membres.
    """
    SAVINGS_TYPE_CHOICES = [
        ('regular', _('Épargne courante')),
        ('term', _('Épargne à terme')),
        ('special', _('Épargne spéciale')),
    ]
    
    member = models.ForeignKey(
        'members.Member',
        on_delete=models.CASCADE,
        related_name='savings',
        verbose_name=_("Membre")
    )
    savings_type = models.CharField(
        _("Type d'épargne"),
        max_length=20,
        choices=SAVINGS_TYPE_CHOICES,
        default='regular'
    )
    
    # Soldes
    current_balance = models.DecimalField(
        _("Solde actuel"),
        max_digits=12,
        decimal_places=2,
        default=0
    )
    
    # Conditions
    interest_rate = models.DecimalField(
        _("Taux d'intérêt (%)"),
        max_digits=5,
        decimal_places=2,
        default=0
    )
    minimum_balance = models.DecimalField(
        _("Solde minimum"),
        max_digits=12,
        decimal_places=2,
        default=0
    )
    
    # Dates
    opening_date = models.DateField(_("Date d'ouverture"), default=timezone.now)
    maturity_date = models.DateField(_("Date d'échéance"), null=True, blank=True)
    last_interest_date = models.DateField(
        _("Dernière capitalisation"),
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = _("Épargne membre")
        verbose_name_plural = _("Épargnes membres")
        unique_together = ['member', 'savings_type']
    
    def __str__(self):
        return f"{self.member.full_name} - {self.get_savings_type_display()}"
