"""
Modèles de base pour le système de gestion des coopératives.
Classes abstraites et modèles communs réutilisables.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
import uuid


class TimestampedModel(models.Model):
    """
    Modèle abstrait avec horodatage automatique.
    Utilisé comme classe de base pour tous les modèles.
    """
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Modifié le"), auto_now=True)
    
    class Meta:
        abstract = True


class UUIDModel(models.Model):
    """
    Modèle abstrait avec UUID comme clé primaire.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("Identifiant")
    )
    
    class Meta:
        abstract = True


class ActiveModel(models.Model):
    """
    Modèle abstrait avec gestion du statut actif/inactif.
    """
    is_active = models.BooleanField(
        _("Actif"),
        default=True,
        help_text=_("Désélectionner pour désactiver sans supprimer.")
    )
    
    class Meta:
        abstract = True


class BaseModel(TimestampedModel, ActiveModel):
    """
    Modèle de base combinant horodatage et statut actif.
    """
    class Meta:
        abstract = True


class Address(BaseModel):
    """
    Modèle d'adresse réutilisable.
    """
    street = models.CharField(_("Rue"), max_length=255)
    city = models.CharField(_("Ville"), max_length=100)
    postal_code = models.CharField(_("Code postal"), max_length=20, blank=True)
    region = models.CharField(_("Région/État"), max_length=100, blank=True)
    country = models.CharField(_("Pays"), max_length=100, default="Côte d'Ivoire")
    
    class Meta:
        verbose_name = _("Adresse")
        verbose_name_plural = _("Adresses")
    
    def __str__(self):
        return f"{self.street}, {self.city}"


class ContactInfo(BaseModel):
    """
    Informations de contact réutilisables.
    """
    phone_primary = models.CharField(_("Téléphone principal"), max_length=20)
    phone_secondary = models.CharField(_("Téléphone secondaire"), max_length=20, blank=True)
    email = models.EmailField(_("Email"), blank=True)
    whatsapp = models.CharField(_("WhatsApp"), max_length=20, blank=True)
    
    class Meta:
        verbose_name = _("Contact")
        verbose_name_plural = _("Contacts")
    
    def __str__(self):
        return self.phone_primary


class CooperativeInfo(BaseModel):
    """
    Informations générales de la coopérative.
    Modèle singleton pour les paramètres globaux.
    """
    name = models.CharField(_("Nom de la coopérative"), max_length=200)
    legal_name = models.CharField(_("Raison sociale"), max_length=200, blank=True)
    registration_number = models.CharField(_("Numéro d'enregistrement"), max_length=50, blank=True)
    tax_id = models.CharField(_("Numéro fiscal"), max_length=50, blank=True)
    logo = models.ImageField(_("Logo"), upload_to='cooperative/', blank=True, null=True)
    description = models.TextField(_("Description"), blank=True)
    
    # Informations de contact
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
    
    # Paramètres financiers
    currency = models.CharField(_("Devise"), max_length=10, default="XOF")
    default_member_fee = models.DecimalField(
        _("Cotisation par défaut"),
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    class Meta:
        verbose_name = _("Information coopérative")
        verbose_name_plural = _("Informations coopérative")
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Assurer qu'il n'y a qu'une seule instance."""
        if not self.pk and CooperativeInfo.objects.exists():
            raise ValueError(_("Il ne peut y avoir qu'une seule instance de CooperativeInfo"))
        return super().save(*args, **kwargs)
