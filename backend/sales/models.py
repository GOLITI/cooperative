from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from core.models import TimestampedModel, SoftDeleteModel, Address, Contact
from members.models import Member
from inventory.models import Product

class Customer(SoftDeleteModel):
    """Clients (membres et non-membres)"""
    name = models.CharField(max_length=200, verbose_name="Nom")
    customer_type = models.CharField(
        max_length=20,
        choices=[
            ('member', 'Membre'),
            ('non_member', 'Non-membre'),
            ('corporate', 'Entreprise')
        ],
        verbose_name="Type de client"
    )
    member = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Membre associé")
    
    # Contact
    phone = models.CharField(max_length=20, verbose_name="Téléphone")
    email = models.EmailField(blank=True, verbose_name="Email")
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Adresse")
    
    # Informations de crédit
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Limite de crédit")
    current_credit = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Crédit actuel")
    
    # Points de fidélité
    loyalty_points = models.PositiveIntegerField(default=0, verbose_name="Points de fidélité")
    
    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
    
    def __str__(self):
        return f"{self.name} ({self.get_customer_type_display()})"
    
    @property
    def available_credit(self):
        return self.credit_limit - self.current_credit

class Sale(TimestampedModel):
    """Ventes"""
    sale_number = models.CharField(max_length=20, unique=True, verbose_name="Numéro de vente")
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, verbose_name="Client")
    sale_date = models.DateTimeField(verbose_name="Date de vente")
    
    # Montants
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Sous-total")
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Remise")
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Taxes")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Total")
    
    # Paiement
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'En attente'),
            ('partial', 'Partiel'),
            ('paid', 'Payé'),
            ('overdue', 'En retard')
        ],
        default='pending',
        verbose_name="Statut de paiement"
    )
    
    # Statut de la vente
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Brouillon'),
            ('confirmed', 'Confirmée'),
            ('delivered', 'Livrée'),
            ('cancelled', 'Annulée'),
            ('returned', 'Retournée')
        ],
        default='draft',
        verbose_name="Statut"
    )
    
    # Informations additionnelles
    notes = models.TextField(blank=True, verbose_name="Notes")
    salesperson = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Vendeur")
    
    # Livraison
    delivery_date = models.DateTimeField(null=True, blank=True, verbose_name="Date de livraison")
    delivery_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Adresse de livraison")
    
    class Meta:
        verbose_name = "Vente"
        verbose_name_plural = "Ventes"
        ordering = ['-sale_date']
    
    def __str__(self):
        return f"{self.sale_number} - {self.customer.name}"
    
    def calculate_totals(self):
        """Calculer les totaux de la vente"""
        lines = self.lines.all()
        self.subtotal = sum(line.total for line in lines)
        self.total_amount = self.subtotal - self.discount_amount + self.tax_amount
        self.save()

class SaleItem(TimestampedModel):
    """Articles de vente"""
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='lines', verbose_name="Vente")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Produit")
    quantity = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="Quantité")
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Prix unitaire")
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Remise (%)")
    total = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Total")
    
    class Meta:
        verbose_name = "Article de vente"
        verbose_name_plural = "Articles de vente"
    
    def save(self, *args, **kwargs):
        discount_amount = (self.unit_price * self.discount_percent / 100)
        self.total = (self.unit_price - discount_amount) * self.quantity
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

class Payment(TimestampedModel):
    """Paiements"""
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='payments', verbose_name="Vente")
    payment_number = models.CharField(max_length=20, unique=True, verbose_name="Numéro de paiement")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Montant")
    payment_date = models.DateTimeField(verbose_name="Date de paiement")
    
    payment_method = models.CharField(
        max_length=20,
        choices=[
            ('cash', 'Espèces'),
            ('mobile_money', 'Mobile Money'),
            ('bank_transfer', 'Virement bancaire'),
            ('check', 'Chèque'),
            ('credit_card', 'Carte de crédit'),
            ('credit', 'Crédit')
        ],
        verbose_name="Mode de paiement"
    )
    
    reference_number = models.CharField(max_length=50, blank=True, verbose_name="Numéro de référence")
    notes = models.TextField(blank=True, verbose_name="Notes")
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Reçu par")
    
    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"{self.payment_number} - {self.amount}"

class Promotion(TimestampedModel):
    """Promotions et remises"""
    name = models.CharField(max_length=200, verbose_name="Nom")
    description = models.TextField(verbose_name="Description")
    
    # Type de promotion
    promotion_type = models.CharField(
        max_length=20,
        choices=[
            ('percentage', 'Pourcentage'),
            ('fixed_amount', 'Montant fixe'),
            ('buy_x_get_y', 'Acheter X obtenir Y')
        ],
        verbose_name="Type de promotion"
    )
    
    # Valeurs
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Pourcentage de remise")
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Montant de remise")
    
    # Conditions
    minimum_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Montant minimum")
    products = models.ManyToManyField(Product, blank=True, verbose_name="Produits concernés")
    customer_types = models.JSONField(default=list, verbose_name="Types de clients")
    
    # Période
    start_date = models.DateTimeField(verbose_name="Date de début")
    end_date = models.DateTimeField(verbose_name="Date de fin")
    
    # Statut
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    
    class Meta:
        verbose_name = "Promotion"
        verbose_name_plural = "Promotions"
    
    def __str__(self):
        return self.name
    
    def is_valid(self):
        """Vérifier si la promotion est valide"""
        from django.utils import timezone
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date

class Order(TimestampedModel):
    """Commandes (pour livraison différée)"""
    order_number = models.CharField(max_length=20, unique=True, verbose_name="Numéro de commande")
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, verbose_name="Client")
    order_date = models.DateTimeField(verbose_name="Date de commande")
    expected_delivery_date = models.DateTimeField(verbose_name="Date de livraison prévue")
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'En attente'),
            ('confirmed', 'Confirmée'),
            ('preparing', 'En préparation'),
            ('ready', 'Prête'),
            ('delivered', 'Livrée'),
            ('cancelled', 'Annulée')
        ],
        default='pending',
        verbose_name="Statut"
    )
    
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Montant total")
    notes = models.TextField(blank=True, verbose_name="Notes")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Créé par")
    
    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        ordering = ['-order_date']
    
    def __str__(self):
        return f"{self.order_number} - {self.customer.name}"
