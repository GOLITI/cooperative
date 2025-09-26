from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from core.models import TimestampedModel, SoftDeleteModel

class Category(SoftDeleteModel):
    """Catégories de produits"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom")
    description = models.TextField(blank=True, verbose_name="Description")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, verbose_name="Catégorie parent")
    code = models.CharField(max_length=20, unique=True, verbose_name="Code")
    
    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
    
    def __str__(self):
        return self.name

class Unit(TimestampedModel):
    """Unités de mesure"""
    name = models.CharField(max_length=50, unique=True, verbose_name="Nom")
    abbreviation = models.CharField(max_length=10, verbose_name="Abréviation")
    unit_type = models.CharField(
        max_length=20,
        choices=[
            ('weight', 'Poids'),
            ('volume', 'Volume'),
            ('length', 'Longueur'),
            ('unit', 'Unité'),
            ('other', 'Autre')
        ],
        verbose_name="Type d'unité"
    )
    
    class Meta:
        verbose_name = "Unité de mesure"
        verbose_name_plural = "Unités de mesure"
    
    def __str__(self):
        return f"{self.name} ({self.abbreviation})"

class Product(SoftDeleteModel):
    """Produits de la coopérative"""
    name = models.CharField(max_length=200, verbose_name="Nom")
    description = models.TextField(blank=True, verbose_name="Description")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name="Catégorie")
    
    # Codes et identification
    sku = models.CharField(max_length=50, unique=True, verbose_name="Code produit (SKU)")
    barcode = models.CharField(max_length=50, blank=True, verbose_name="Code-barres")
    
    # Unités
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, verbose_name="Unité de base")
    
    # Prix
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Prix de revient")
    selling_price_member = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Prix membre")
    selling_price_non_member = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Prix non-membre")
    
    # Stock
    current_stock = models.DecimalField(max_digits=15, decimal_places=3, default=0, verbose_name="Stock actuel")
    minimum_stock = models.DecimalField(max_digits=15, decimal_places=3, default=0, verbose_name="Stock minimum")
    maximum_stock = models.DecimalField(max_digits=15, decimal_places=3, default=0, verbose_name="Stock maximum")
    
    # Statut et qualité
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Actif'),
            ('inactive', 'Inactif'),
            ('discontinued', 'Arrêté')
        ],
        default='active',
        verbose_name="Statut"
    )
    
    # Dates importantes
    expiry_date = models.DateField(null=True, blank=True, verbose_name="Date d'expiration")
    
    # Média
    image = models.ImageField(upload_to='products/', blank=True, verbose_name="Image")
    
    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.sku} - {self.name}"
    
    @property
    def is_low_stock(self):
        return self.current_stock <= self.minimum_stock
    
    @property
    def stock_value(self):
        return self.current_stock * self.cost_price

class StockMovement(TimestampedModel):
    """Mouvements de stock"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='movements', verbose_name="Produit")
    movement_type = models.CharField(
        max_length=20,
        choices=[
            ('in', 'Entrée'),
            ('out', 'Sortie'),
            ('adjustment', 'Ajustement'),
            ('transfer', 'Transfert')
        ],
        verbose_name="Type de mouvement"
    )
    
    quantity = models.DecimalField(max_digits=15, decimal_places=3, verbose_name="Quantité")
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Coût unitaire")
    
    # Références
    reference_type = models.CharField(
        max_length=20,
        choices=[
            ('purchase', 'Achat'),
            ('sale', 'Vente'),
            ('production', 'Production'),
            ('loss', 'Perte'),
            ('inventory', 'Inventaire'),
            ('donation', 'Don')
        ],
        verbose_name="Type de référence"
    )
    reference_number = models.CharField(max_length=50, blank=True, verbose_name="Numéro de référence")
    
    # Détails
    notes = models.TextField(blank=True, verbose_name="Notes")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Utilisateur")
    
    # Stock après mouvement
    stock_after = models.DecimalField(max_digits=15, decimal_places=3, verbose_name="Stock après")
    
    class Meta:
        verbose_name = "Mouvement de stock"
        verbose_name_plural = "Mouvements de stock"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.product.name} - {self.get_movement_type_display()} - {self.quantity}"

class Inventory(TimestampedModel):
    """Inventaires physiques"""
    name = models.CharField(max_length=200, verbose_name="Nom de l'inventaire")
    date_start = models.DateTimeField(verbose_name="Date de début")
    date_end = models.DateTimeField(null=True, blank=True, verbose_name="Date de fin")
    status = models.CharField(
        max_length=20,
        choices=[
            ('planned', 'Planifié'),
            ('in_progress', 'En cours'),
            ('completed', 'Terminé'),
            ('cancelled', 'Annulé')
        ],
        default='planned',
        verbose_name="Statut"
    )
    notes = models.TextField(blank=True, verbose_name="Notes")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Créé par")
    
    class Meta:
        verbose_name = "Inventaire"
        verbose_name_plural = "Inventaires"
        ordering = ['-date_start']
    
    def __str__(self):
        return f"{self.name} - {self.date_start.date()}"

class InventoryLine(TimestampedModel):
    """Lignes d'inventaire"""
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name='lines', verbose_name="Inventaire")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Produit")
    theoretical_quantity = models.DecimalField(max_digits=15, decimal_places=3, verbose_name="Quantité théorique")
    physical_quantity = models.DecimalField(max_digits=15, decimal_places=3, null=True, blank=True, verbose_name="Quantité physique")
    difference = models.DecimalField(max_digits=15, decimal_places=3, default=0, verbose_name="Écart")
    notes = models.TextField(blank=True, verbose_name="Notes")
    counted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Compté par")
    
    class Meta:
        verbose_name = "Ligne d'inventaire"
        verbose_name_plural = "Lignes d'inventaire"
        unique_together = ['inventory', 'product']
    
    def save(self, *args, **kwargs):
        if self.physical_quantity is not None:
            self.difference = self.physical_quantity - self.theoretical_quantity
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.inventory.name} - {self.product.name}"
