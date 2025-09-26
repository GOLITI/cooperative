from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class TimestampedModel(models.Model):
    """Modèle abstrait avec timestamps automatiques"""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    
    class Meta:
        abstract = True

class SoftDeleteModel(TimestampedModel):
    """Modèle abstrait avec suppression logique"""
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="Supprimé le")
    
    class Meta:
        abstract = True
    
    def soft_delete(self):
        """Suppression logique"""
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save()
    
    def restore(self):
        """Restauration"""
        self.is_active = True
        self.deleted_at = None
        self.save()

class Address(TimestampedModel):
    """Modèle pour les adresses"""
    street = models.CharField(max_length=255, verbose_name="Rue")
    city = models.CharField(max_length=100, verbose_name="Ville")
    region = models.CharField(max_length=100, verbose_name="Région")
    country = models.CharField(max_length=100, default="Sénégal", verbose_name="Pays")
    postal_code = models.CharField(max_length=20, blank=True, verbose_name="Code postal")
    
    class Meta:
        verbose_name = "Adresse"
        verbose_name_plural = "Adresses"
    
    def __str__(self):
        return f"{self.street}, {self.city}, {self.region}"

class Contact(TimestampedModel):
    """Modèle pour les contacts"""
    phone_primary = models.CharField(max_length=20, verbose_name="Téléphone principal")
    phone_secondary = models.CharField(max_length=20, blank=True, verbose_name="Téléphone secondaire")
    email = models.EmailField(blank=True, verbose_name="Email")
    whatsapp = models.CharField(max_length=20, blank=True, verbose_name="WhatsApp")
    
    class Meta:
        verbose_name = "Contact"
        verbose_name_plural = "Contacts"
    
    def __str__(self):
        return self.phone_primary

class ActivityLog(TimestampedModel):
    """Journal d'activité pour audit"""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Utilisateur")
    action = models.CharField(max_length=50, verbose_name="Action")
    model_name = models.CharField(max_length=50, verbose_name="Modèle")
    object_id = models.PositiveIntegerField(verbose_name="ID Objet")
    details = models.JSONField(default=dict, verbose_name="Détails")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Adresse IP")
    
    class Meta:
        verbose_name = "Journal d'activité"
        verbose_name_plural = "Journaux d'activité"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user} - {self.action} - {self.model_name}"
