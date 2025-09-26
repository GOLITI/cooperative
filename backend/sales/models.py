"""
Modèles pour la gestion des ventes.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.utils import timezone
from core.models import BaseModel
from decimal import Decimal


class Customer(BaseModel):
    """
    Modèle des clients (membres et non-membres).
    """
    CUSTOMER_TYPE_CHOICES = [
        ('member', _('Membre')),
        ('external', _('Externe')),
        ('corporate', _('Entreprise')),
    ]
    
    # Informations de base
    customer_code = models.CharField(
        _("Code client"),
        max_length=20,
        unique=True,
        help_text=_("Généré automatiquement")
    )
    customer_type = models.CharField(
        _("Type de client"),
        max_length=20,
        choices=CUSTOMER_TYPE_CHOICES,
        default='external'
    )
    
    # Lien avec les membres (si applicable)
    member = models.OneToOneField(
        'members.Member',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Membre associé")
    )
    
    # Informations pour clients externes
    name = models.CharField(_("Nom/Raison sociale"), max_length=200)
    contact_person = models.CharField(_("Personne de contact"), max_length=200, blank=True)
    phone = models.CharField(_("Téléphone"), max_length=20, blank=True)
    email = models.EmailField(_("Email"), blank=True)
    address = models.TextField(_("Adresse"), blank=True)
    
    # Informations commerciales
    credit_limit = models.DecimalField(
        _("Limite de crédit"),
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    payment_terms_days = models.PositiveIntegerField(
        _("Délai de paiement (jours)"),
        default=0
    )
    
    # Statistiques
    total_purchases = models.DecimalField(
        _("Total des achats"),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    last_purchase_date = models.DateTimeField(_("Dernier achat"), null=True, blank=True)
    
    class Meta:
        verbose_name = _("Client")
        verbose_name_plural = _("Clients")
        ordering = ['name']
    
    def __str__(self):
        if self.member:
            return f"{self.member.full_name} (Membre)"
        return self.name
    
    def save(self, *args, **kwargs):
        """Génération automatique du code client."""
        if not self.customer_code:
            year = timezone.now().year
            last_customer = Customer.objects.filter(
                customer_code__startswith=f"CLI-{year}-"
            ).order_by('customer_code').last()
            
            if last_customer:
                last_number = int(last_customer.customer_code.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.customer_code = f"CLI-{year}-{new_number:04d}"
        
        super().save(*args, **kwargs)


class Sale(BaseModel):
    """
    Modèle principal des ventes.
    """
    STATUS_CHOICES = [
        ('draft', _('Brouillon')),
        ('confirmed', _('Confirmée')),
        ('delivered', _('Livrée')),
        ('paid', _('Payée')),
        ('cancelled', _('Annulée')),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', _('En attente')),
        ('partial', _('Partiel')),
        ('paid', _('Payé')),
        ('overdue', _('En retard')),
    ]
    
    # Identification
    sale_number = models.CharField(
        _("Numéro de vente"),
        max_length=20,
        unique=True,
        help_text=_("Généré automatiquement")
    )
    
    # Client et vendeur
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='sales',
        verbose_name=_("Client")
    )
    salesperson = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='sales',
        verbose_name=_("Vendeur")
    )
    
    # Dates
    sale_date = models.DateTimeField(_("Date de vente"), default=timezone.now)
    expected_delivery_date = models.DateField(_("Date de livraison prévue"), null=True, blank=True)
    actual_delivery_date = models.DateField(_("Date de livraison réelle"), null=True, blank=True)
    
    # Statut
    status = models.CharField(
        _("Statut"),
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    payment_status = models.CharField(
        _("Statut de paiement"),
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )
    
    # Montants
    subtotal = models.DecimalField(
        _("Sous-total"),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    discount_percentage = models.DecimalField(
        _("Remise (%)"),
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    discount_amount = models.DecimalField(
        _("Montant de remise"),
        max_digits=12,
        decimal_places=2,
        default=0
    )
    tax_percentage = models.DecimalField(
        _("Taxe (%)"),
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    tax_amount = models.DecimalField(
        _("Montant de taxe"),
        max_digits=12,
        decimal_places=2,
        default=0
    )
    total_amount = models.DecimalField(
        _("Montant total"),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    paid_amount = models.DecimalField(
        _("Montant payé"),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    
    # Informations supplémentaires
    notes = models.TextField(_("Notes"), blank=True)
    internal_notes = models.TextField(_("Notes internes"), blank=True)
    
    class Meta:
        verbose_name = _("Vente")
        verbose_name_plural = _("Ventes")
        ordering = ['-sale_date']
        indexes = [
            models.Index(fields=['sale_number']),
            models.Index(fields=['customer', 'sale_date']),
            models.Index(fields=['sale_date']),
        ]
    
    def __str__(self):
        return f"{self.sale_number} - {self.customer}"
    
    @property
    def balance_due(self):
        """Solde restant à payer."""
        return self.total_amount - self.paid_amount
    
    @property
    def is_fully_paid(self):
        """Vérifie si la vente est entièrement payée."""
        return self.paid_amount >= self.total_amount
    
    def calculate_totals(self):
        """Calcule les totaux de la vente."""
        # Calcul du sous-total à partir des lignes de vente
        self.subtotal = sum(
            line.total_price for line in self.lines.all()
        )
        
        # Calcul de la remise
        if self.discount_percentage > 0:
            self.discount_amount = (self.subtotal * self.discount_percentage) / 100
        
        # Montant après remise
        amount_after_discount = self.subtotal - self.discount_amount
        
        # Calcul de la taxe
        if self.tax_percentage > 0:
            self.tax_amount = (amount_after_discount * self.tax_percentage) / 100
        
        # Total final
        self.total_amount = amount_after_discount + self.tax_amount
        
        self.save()
    
    def save(self, *args, **kwargs):
        """Génération automatique du numéro de vente."""
        if not self.sale_number:
            year = timezone.now().year
            month = timezone.now().month
            last_sale = Sale.objects.filter(
                sale_number__startswith=f"VEN-{year}{month:02d}-"
            ).order_by('sale_number').last()
            
            if last_sale:
                last_number = int(last_sale.sale_number.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.sale_number = f"VEN-{year}{month:02d}-{new_number:04d}"
        
        super().save(*args, **kwargs)


class SaleLine(BaseModel):
    """
    Lignes de vente (produits vendus).
    """
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name='lines',
        verbose_name=_("Vente")
    )
    product = models.ForeignKey(
        'inventory.Product',
        on_delete=models.PROTECT,
        verbose_name=_("Produit")
    )
    
    # Quantité et prix
    quantity = models.DecimalField(
        _("Quantité"),
        max_digits=15,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))]
    )
    unit_price = models.DecimalField(
        _("Prix unitaire"),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    discount_percentage = models.DecimalField(
        _("Remise ligne (%)"),
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    # Traçabilité
    lot_number = models.CharField(_("Numéro de lot"), max_length=100, blank=True)
    
    class Meta:
        verbose_name = _("Ligne de vente")
        verbose_name_plural = _("Lignes de vente")
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    @property
    def line_total_before_discount(self):
        """Total de la ligne avant remise."""
        return self.quantity * self.unit_price
    
    @property
    def discount_amount(self):
        """Montant de la remise de ligne."""
        if self.discount_percentage > 0:
            return (self.line_total_before_discount * self.discount_percentage) / 100
        return 0
    
    @property
    def total_price(self):
        """Prix total de la ligne après remise."""
        return self.line_total_before_discount - self.discount_amount
    
    def save(self, *args, **kwargs):
        """Mise à jour du total de la vente."""
        super().save(*args, **kwargs)
        self.sale.calculate_totals()


class SalePayment(BaseModel):
    """
    Paiements reçus pour les ventes.
    """
    PAYMENT_METHOD_CHOICES = [
        ('cash', _('Espèces')),
        ('bank_transfer', _('Virement bancaire')),
        ('mobile_money', _('Mobile Money')),
        ('check', _('Chèque')),
        ('card', _('Carte bancaire')),
        ('credit', _('À crédit')),
    ]
    
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name=_("Vente")
    )
    
    # Montant et méthode
    amount = models.DecimalField(
        _("Montant"),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    payment_method = models.CharField(
        _("Mode de paiement"),
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES
    )
    
    # Dates
    payment_date = models.DateTimeField(_("Date de paiement"), default=timezone.now)
    
    # Références
    reference = models.CharField(_("Référence"), max_length=100, blank=True)
    notes = models.TextField(_("Notes"), blank=True)
    
    # Validation
    validated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Validé par")
    )
    
    class Meta:
        verbose_name = _("Paiement de vente")
        verbose_name_plural = _("Paiements de vente")
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"{self.sale.sale_number} - {self.amount} XOF"
    
    def save(self, *args, **kwargs):
        """Mise à jour du montant payé de la vente."""
        super().save(*args, **kwargs)
        
        # Recalcul du total payé pour la vente
        total_paid = self.sale.payments.aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        
        self.sale.paid_amount = total_paid
        
        # Mise à jour du statut de paiement
        if total_paid >= self.sale.total_amount:
            self.sale.payment_status = 'paid'
        elif total_paid > 0:
            self.sale.payment_status = 'partial'
        else:
            self.sale.payment_status = 'pending'
        
        self.sale.save()
