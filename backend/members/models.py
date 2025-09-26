"""
Modèles pour la gestion des membres de la coopérative.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import BaseModel, Address, ContactInfo
from datetime import date


class MembershipType(BaseModel):
    """
    Types d'adhésion (Membre actif, honoraire, associé, etc.)
    """
    name = models.CharField(_("Nom du type"), max_length=100)
    description = models.TextField(_("Description"), blank=True)
    monthly_fee = models.DecimalField(
        _("Cotisation mensuelle"),
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    benefits = models.TextField(_("Avantages"), blank=True)
    color = models.CharField(_("Couleur"), max_length=7, default="#007bff")  # Couleur hex
    
    class Meta:
        verbose_name = _("Type d'adhésion")
        verbose_name_plural = _("Types d'adhésion")
    
    def __str__(self):
        return self.name


class Member(BaseModel):
    """
    Modèle principal des membres de la coopérative.
    """
    GENDER_CHOICES = [
        ('M', _('Masculin')),
        ('F', _('Féminin')),
        ('O', _('Autre')),
    ]
    
    MARITAL_STATUS_CHOICES = [
        ('single', _('Célibataire')),
        ('married', _('Marié(e)')),
        ('divorced', _('Divorcé(e)')),
        ('widowed', _('Veuf/Veuve')),
    ]
    
    # Informations personnelles
    member_number = models.CharField(
        _("Numéro de membre"), 
        max_length=20, 
        unique=True,
        help_text=_("Généré automatiquement")
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("Utilisateur"),
        null=True,
        blank=True,
        help_text=_("Compte utilisateur associé (optionnel)")
    )
    
    # Identité
    first_name = models.CharField(_("Prénom"), max_length=100)
    last_name = models.CharField(_("Nom de famille"), max_length=100)
    date_of_birth = models.DateField(_("Date de naissance"), null=True, blank=True)
    gender = models.CharField(_("Sexe"), max_length=1, choices=GENDER_CHOICES, blank=True)
    national_id = models.CharField(_("Pièce d'identité"), max_length=50, blank=True)
    marital_status = models.CharField(
        _("Situation matrimoniale"),
        max_length=20,
        choices=MARITAL_STATUS_CHOICES,
        blank=True
    )
    
    # Photo et documents
    photo = models.ImageField(_("Photo"), upload_to='members/photos/', blank=True, null=True)
    id_document = models.FileField(
        _("Document d'identité"),
        upload_to='members/documents/',
        blank=True,
        null=True
    )
    
    # Adresse et contact
    address = models.OneToOneField(
        Address,
        on_delete=models.CASCADE,
        verbose_name=_("Adresse"),
        null=True,
        blank=True
    )
    contact = models.OneToOneField(
        ContactInfo,
        on_delete=models.CASCADE,
        verbose_name=_("Contact"),
        null=True,
        blank=True
    )
    
    # Adhésion
    membership_type = models.ForeignKey(
        MembershipType,
        on_delete=models.PROTECT,
        verbose_name=_("Type d'adhésion")
    )
    join_date = models.DateField(_("Date d'adhésion"), default=date.today)
    membership_number = models.CharField(
        _("Numéro d'adhésion"),
        max_length=50,
        blank=True
    )
    
    # Informations professionnelles
    profession = models.CharField(_("Profession"), max_length=100, blank=True)
    specialties = models.TextField(
        _("Spécialités/Compétences"),
        blank=True,
        help_text=_("Compétences particulières du membre")
    )
    experience_years = models.PositiveIntegerField(
        _("Années d'expérience"),
        null=True,
        blank=True,
        validators=[MaxValueValidator(100)]
    )
    
    # Situation familiale
    dependents_count = models.PositiveIntegerField(
        _("Nombre de personnes à charge"),
        default=0,
        validators=[MaxValueValidator(50)]
    )
    emergency_contact_name = models.CharField(
        _("Contact d'urgence - Nom"),
        max_length=200,
        blank=True
    )
    emergency_contact_phone = models.CharField(
        _("Contact d'urgence - Téléphone"),
        max_length=20,
        blank=True
    )
    emergency_contact_relationship = models.CharField(
        _("Contact d'urgence - Relation"),
        max_length=100,
        blank=True
    )
    
    # Statuts
    is_founder = models.BooleanField(_("Membre fondateur"), default=False)
    is_board_member = models.BooleanField(_("Membre du conseil"), default=False)
    notes = models.TextField(_("Notes"), blank=True)
    
    class Meta:
        verbose_name = _("Membre")
        verbose_name_plural = _("Membres")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['member_number']),
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['join_date']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.member_number})"
    
    @property
    def full_name(self):
        """Nom complet du membre."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        """Âge calculé à partir de la date de naissance."""
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None
    
    def save(self, *args, **kwargs):
        """Génération automatique du numéro de membre."""
        if not self.member_number:
            # Format: COOP-YYYY-NNNN
            year = date.today().year
            last_member = Member.objects.filter(
                member_number__startswith=f"COOP-{year}-"
            ).order_by('member_number').last()
            
            if last_member:
                last_number = int(last_member.member_number.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.member_number = f"COOP-{year}-{new_number:04d}"
        
        super().save(*args, **kwargs)


class MembershipHistory(BaseModel):
    """
    Historique des changements de type d'adhésion.
    """
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='membership_history',
        verbose_name=_("Membre")
    )
    old_type = models.ForeignKey(
        MembershipType,
        on_delete=models.CASCADE,
        related_name='old_memberships',
        verbose_name=_("Ancien type"),
        null=True,
        blank=True
    )
    new_type = models.ForeignKey(
        MembershipType,
        on_delete=models.CASCADE,
        related_name='new_memberships',
        verbose_name=_("Nouveau type")
    )
    change_date = models.DateField(_("Date du changement"), default=date.today)
    reason = models.TextField(_("Motif du changement"), blank=True)
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Modifié par")
    )
    
    class Meta:
        verbose_name = _("Historique d'adhésion")
        verbose_name_plural = _("Historiques d'adhésion")
        ordering = ['-change_date']
    
    def __str__(self):
        return f"{self.member} - {self.change_date}"


class MemberPayment(BaseModel):
    """
    Paiements des cotisations des membres.
    """
    PAYMENT_STATUS_CHOICES = [
        ('pending', _('En attente')),
        ('paid', _('Payé')),
        ('overdue', _('En retard')),
        ('cancelled', _('Annulé')),
    ]
    
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name=_("Membre")
    )
    amount = models.DecimalField(
        _("Montant"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    payment_date = models.DateField(_("Date de paiement"), null=True, blank=True)
    due_date = models.DateField(_("Date d'échéance"))
    status = models.CharField(
        _("Statut"),
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )
    payment_method = models.CharField(_("Mode de paiement"), max_length=50, blank=True)
    reference = models.CharField(_("Référence"), max_length=100, blank=True)
    notes = models.TextField(_("Notes"), blank=True)
    
    # Relations avec d'autres modèles (à ajouter plus tard)
    # financial_transaction = models.OneToOneField('finance.FinancialTransaction', ...)
    
    class Meta:
        verbose_name = _("Paiement de cotisation")
        verbose_name_plural = _("Paiements de cotisations")
        ordering = ['-due_date']
    
    def __str__(self):
        return f"{self.member} - {self.amount} XOF - {self.due_date}"
    
    @property
    def is_overdue(self):
        """Vérifie si le paiement est en retard."""
        if self.status != 'paid' and self.due_date < date.today():
            return True
        return False
