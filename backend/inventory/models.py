"""
Modèles pour la gestion des stocks et inventaire.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.utils import timezone
from core.models import BaseModel
from decimal import Decimal


class ProductCategory(BaseModel):
    """
    Catégories de produits avec hiérarchie.
    """
    name = models.CharField(_("Nom de la catégorie"), max_length=100)
    description = models.TextField(_("Description"), blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories',
        verbose_name=_("Catégorie parent")
    )
    image = models.ImageField(
        _("Image"),
        upload_to='categories/',
        blank=True,
        null=True
    )
    sort_order = models.PositiveIntegerField(_("Ordre d'affichage"), default=0)
    
    class Meta:
        verbose_name = _("Catégorie de produit")
        verbose_name_plural = _("Catégories de produits")
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name
    
    @property
    def full_path(self):
        """Chemin complet de la catégorie."""
        path = [self.name]
        parent = self.parent
        while parent:
            path.insert(0, parent.name)
            parent = parent.parent
        return " > ".join(path)


class Unit(BaseModel):
    """
    Unités de mesure pour les produits.
    """
    name = models.CharField(_("Nom de l'unité"), max_length=50)
    abbreviation = models.CharField(_("Abréviation"), max_length=10)
    type = models.CharField(
        _("Type"),
        max_length=20,
        choices=[
            ('weight', _('Poids')),
            ('volume', _('Volume')),
            ('length', _('Longueur')),
            ('area', _('Surface')),
            ('piece', _('Pièce')),
            ('other', _('Autre')),
        ],
        default='piece'
    )
    
    class Meta:
        verbose_name = _("Unité de mesure")
        verbose_name_plural = _("Unités de mesure")
    
    def __str__(self):
        return f"{self.name} ({self.abbreviation})"


class Product(BaseModel):
    """
    Modèle principal des produits.
    """
    PRODUCT_TYPE_CHOICES = [
        ('raw_material', _('Matière première')),
        ('finished_product', _('Produit fini')),
        ('service', _('Service')),
        ('consumable', _('Consommable')),
    ]
    
    # Identification
    name = models.CharField(_("Nom du produit"), max_length=200)
    code = models.CharField(
        _("Code produit"),
        max_length=50,
        unique=True,
        help_text=_("Code unique du produit")
    )
    barcode = models.CharField(
        _("Code-barres"),
        max_length=100,
        blank=True,
        unique=True,
        null=True
    )
    
    # Classification
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.PROTECT,
        verbose_name=_("Catégorie"),
        related_name='products'
    )
    product_type = models.CharField(
        _("Type de produit"),
        max_length=20,
        choices=PRODUCT_TYPE_CHOICES,
        default='finished_product'
    )
    
    # Description
    description = models.TextField(_("Description"), blank=True)
    specifications = models.TextField(_("Spécifications techniques"), blank=True)
    image = models.ImageField(
        _("Image principale"),
        upload_to='products/',
        blank=True,
        null=True
    )
    
    # Unités et mesures
    unit = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        verbose_name=_("Unité de base")
    )
    weight = models.DecimalField(
        _("Poids unitaire"),
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.001'))]
    )
    dimensions = models.CharField(
        _("Dimensions (L x l x h)"),
        max_length=100,
        blank=True
    )
    
    # Prix
    purchase_price = models.DecimalField(
        _("Prix d'achat"),
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    selling_price = models.DecimalField(
        _("Prix de vente"),
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    member_price = models.DecimalField(
        _("Prix membre"),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text=_("Prix préférentiel pour les membres")
    )
    
    # Gestion des stocks
    current_stock = models.DecimalField(
        _("Stock actuel"),
        max_digits=15,
        decimal_places=3,
        default=0,
        validators=[MinValueValidator(0)]
    )
    min_stock_level = models.DecimalField(
        _("Stock minimum"),
        max_digits=15,
        decimal_places=3,
        default=0,
        validators=[MinValueValidator(0)]
    )
    max_stock_level = models.DecimalField(
        _("Stock maximum"),
        max_digits=15,
        decimal_places=3,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    
    # Qualité et traçabilité
    origin = models.CharField(_("Origine"), max_length=200, blank=True)
    quality_grade = models.CharField(
        _("Grade de qualité"),
        max_length=50,
        blank=True
    )
    expiry_tracking = models.BooleanField(
        _("Suivi d'expiration"),
        default=False,
        help_text=_("Activer si le produit a une date de péremption")
    )
    lot_tracking = models.BooleanField(
        _("Suivi par lot"),
        default=False,
        help_text=_("Activer pour tracer les lots de production")
    )
    
    # Statuts
    is_sellable = models.BooleanField(_("Vendable"), default=True)
    is_purchasable = models.BooleanField(_("Achetable"), default=True)
    
    class Meta:
        verbose_name = _("Produit")
        verbose_name_plural = _("Produits")
        ordering = ['name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['name']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    @property
    def stock_status(self):
        """Statut du stock basé sur les seuils."""
        if self.current_stock <= 0:
            return 'out_of_stock'
        elif self.current_stock <= self.min_stock_level:
            return 'low_stock'
        elif self.max_stock_level and self.current_stock >= self.max_stock_level:
            return 'overstock'
        else:
            return 'normal'
    
    @property
    def margin(self):
        """Marge bénéficiaire."""
        if self.purchase_price > 0:
            return ((self.selling_price - self.purchase_price) / self.purchase_price) * 100
        return 0
    
    def save(self, *args, **kwargs):
        """Génération automatique du code produit si non fourni."""
        if not self.code:
            # Format: CAT-YYYY-NNNN
            category_prefix = self.category.name[:3].upper()
            year = timezone.now().year
            last_product = Product.objects.filter(
                code__startswith=f"{category_prefix}-{year}-"
            ).order_by('code').last()
            
            if last_product:
                last_number = int(last_product.code.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.code = f"{category_prefix}-{year}-{new_number:04d}"
        
        super().save(*args, **kwargs)


class StockMovement(BaseModel):
    """
    Mouvements de stock (entrées, sorties, ajustements).
    """
    MOVEMENT_TYPE_CHOICES = [
        ('in', _('Entrée')),
        ('out', _('Sortie')),
        ('adjustment', _('Ajustement')),
        ('transfer', _('Transfert')),
        ('return', _('Retour')),
        ('loss', _('Perte')),
    ]
    
    MOVEMENT_REASON_CHOICES = [
        ('purchase', _('Achat')),
        ('production', _('Production')),
        ('sale', _('Vente')),
        ('donation', _('Don')),
        ('inventory', _('Inventaire')),
        ('expiry', _('Péremption')),
        ('damage', _('Dommage')),
        ('theft', _('Vol')),
        ('other', _('Autre')),
    ]
    
    # Produit et quantité
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='movements',
        verbose_name=_("Produit")
    )
    quantity = models.DecimalField(
        _("Quantité"),
        max_digits=15,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))]
    )
    unit_cost = models.DecimalField(
        _("Coût unitaire"),
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    # Type et raison
    movement_type = models.CharField(
        _("Type de mouvement"),
        max_length=20,
        choices=MOVEMENT_TYPE_CHOICES
    )
    reason = models.CharField(
        _("Raison"),
        max_length=20,
        choices=MOVEMENT_REASON_CHOICES
    )
    
    # Traçabilité
    lot_number = models.CharField(_("Numéro de lot"), max_length=100, blank=True)
    expiry_date = models.DateField(_("Date d'expiration"), null=True, blank=True)
    supplier_info = models.CharField(_("Informations fournisseur"), max_length=200, blank=True)
    
    # Références
    reference_document = models.CharField(
        _("Document de référence"),
        max_length=100,
        blank=True,
        help_text=_("Bon de commande, facture, etc.")
    )
    
    # Relations (à compléter plus tard)
    # purchase_order = models.ForeignKey('purchasing.PurchaseOrder', ...)
    # sale = models.ForeignKey('sales.Sale', ...)
    
    # Utilisateur et validation
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Créé par")
    )
    validated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='validated_movements',
        verbose_name=_("Validé par")
    )
    validated_at = models.DateTimeField(_("Validé le"), null=True, blank=True)
    
    # Notes
    notes = models.TextField(_("Notes"), blank=True)
    
    class Meta:
        verbose_name = _("Mouvement de stock")
        verbose_name_plural = _("Mouvements de stock")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', 'created_at']),
            models.Index(fields=['movement_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.product.name} - {self.get_movement_type_display()} - {self.quantity}"
    
    @property
    def total_cost(self):
        """Coût total du mouvement."""
        return self.quantity * self.unit_cost
    
    def save(self, *args, **kwargs):
        """Mise à jour automatique du stock du produit."""
        is_new = self._state.adding
        
        if not is_new:
            # Si c'est une modification, on annule d'abord l'ancien mouvement
            old_movement = StockMovement.objects.get(pk=self.pk)
            if old_movement.movement_type == 'in':
                old_movement.product.current_stock -= old_movement.quantity
            elif old_movement.movement_type == 'out':
                old_movement.product.current_stock += old_movement.quantity
            old_movement.product.save()
        
        # Application du nouveau mouvement
        if self.movement_type == 'in':
            self.product.current_stock += self.quantity
        elif self.movement_type == 'out':
            self.product.current_stock -= self.quantity
        elif self.movement_type == 'adjustment':
            # Pour les ajustements, la quantité représente la nouvelle valeur
            self.product.current_stock = self.quantity
        
        self.product.save()
        super().save(*args, **kwargs)
