from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from core.models import TimestampedModel, SoftDeleteModel, Address, Contact

class MembershipType(TimestampedModel):
    """Types d'adhésion"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom")
    description = models.TextField(verbose_name="Description")
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Cotisation mensuelle")
    benefits = models.JSONField(default=list, verbose_name="Avantages")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    
    class Meta:
        verbose_name = "Type d'adhésion"
        verbose_name_plural = "Types d'adhésion"
    
    def __str__(self):
        return self.name

class Member(SoftDeleteModel):
    """Modèle des membres de la coopérative"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Utilisateur")
    membership_number = models.CharField(max_length=20, unique=True, verbose_name="Numéro d'adhésion")
    membership_type = models.ForeignKey(MembershipType, on_delete=models.PROTECT, verbose_name="Type d'adhésion")
    
    # Informations personnelles
    birth_date = models.DateField(verbose_name="Date de naissance")
    gender = models.CharField(max_length=1, choices=[('M', 'Masculin'), ('F', 'Féminin')], verbose_name="Sexe")
    nationality = models.CharField(max_length=50, default="Sénégalaise", verbose_name="Nationalité")
    id_number = models.CharField(max_length=30, verbose_name="Numéro CNI/Passeport")
    profession = models.CharField(max_length=100, verbose_name="Profession")
    
    # Adresse et contact
    address = models.ForeignKey(Address, on_delete=models.PROTECT, verbose_name="Adresse")
    contact = models.ForeignKey(Contact, on_delete=models.PROTECT, verbose_name="Contact")
    
    # Contact d'urgence
    emergency_contact_name = models.CharField(max_length=200, verbose_name="Contact d'urgence (nom)")
    emergency_contact_phone = models.CharField(max_length=20, verbose_name="Contact d'urgence (téléphone)")
    emergency_contact_relation = models.CharField(max_length=50, verbose_name="Relation")
    
    # Informations d'adhésion
    join_date = models.DateField(verbose_name="Date d'adhésion")
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Actif'),
            ('suspended', 'Suspendu'),
            ('inactive', 'Inactif'),
            ('honorary', 'Honoraire')
        ],
        default='active',
        verbose_name="Statut"
    )
    
    # Compétences et spécialités
    skills = models.JSONField(default=list, verbose_name="Compétences")
    specialties = models.JSONField(default=list, verbose_name="Spécialités")
    
    # Photo et documents
    photo = models.ImageField(upload_to='members/photos/', blank=True, verbose_name="Photo")
    id_document = models.FileField(upload_to='members/documents/', blank=True, verbose_name="Document d'identité")
    
    class Meta:
        verbose_name = "Membre"
        verbose_name_plural = "Membres"
        ordering = ['membership_number']
    
    def __str__(self):
        return f"{self.membership_number} - {self.user.get_full_name()}"
    
    def is_up_to_date_with_fees(self):
        """Vérifier si le membre est à jour avec ses cotisations"""
        # Logique à implémenter
        return True

class MembershipFee(TimestampedModel):
    """Cotisations des membres"""
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='fees', verbose_name="Membre")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant")
    period_month = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)], verbose_name="Mois")
    period_year = models.PositiveIntegerField(verbose_name="Année")
    payment_date = models.DateField(verbose_name="Date de paiement")
    payment_method = models.CharField(
        max_length=20,
        choices=[
            ('cash', 'Espèces'),
            ('mobile', 'Mobile Money'),
            ('bank', 'Virement bancaire'),
            ('check', 'Chèque')
        ],
        verbose_name="Mode de paiement"
    )
    receipt_number = models.CharField(max_length=50, unique=True, verbose_name="Numéro de reçu")
    notes = models.TextField(blank=True, verbose_name="Notes")
    
    class Meta:
        verbose_name = "Cotisation"
        verbose_name_plural = "Cotisations"
        unique_together = ['member', 'period_month', 'period_year']
        ordering = ['-period_year', '-period_month']
    
    def __str__(self):
        return f"{self.member} - {self.period_month}/{self.period_year}"

class FamilyMember(TimestampedModel):
    """Membres de famille d'un adhérent"""
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='family_members', verbose_name="Membre")
    name = models.CharField(max_length=200, verbose_name="Nom complet")
    relationship = models.CharField(
        max_length=20,
        choices=[
            ('spouse', 'Époux/Épouse'),
            ('child', 'Enfant'),
            ('parent', 'Parent'),
            ('sibling', 'Frère/Sœur'),
            ('other', 'Autre')
        ],
        verbose_name="Relation"
    )
    birth_date = models.DateField(blank=True, null=True, verbose_name="Date de naissance")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    
    class Meta:
        verbose_name = "Membre de famille"
        verbose_name_plural = "Membres de famille"
    
    def __str__(self):
        return f"{self.name} ({self.get_relationship_display()})"
