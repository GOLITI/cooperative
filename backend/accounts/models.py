"""
Modèles pour la gestion des comptes utilisateurs et permissions.
Système de rôles pour les coopératives.
"""
from django.db import models
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import BaseModel
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserRole(BaseModel):
    """
    Rôles utilisateur spécifiques aux coopératives.
    """
    ROLE_CHOICES = [
        ('admin', _('Administrateur')),
        ('manager', _('Gestionnaire')),
        ('member', _('Membre')),
        ('visitor', _('Visiteur')),
        ('accountant', _('Comptable')),
        ('salesperson', _('Vendeur')),
        ('stockkeeper', _('Gestionnaire de stock')),
    ]
    
    name = models.CharField(_("Nom du rôle"), max_length=50, choices=ROLE_CHOICES, unique=True)
    display_name = models.CharField(_("Nom d'affichage"), max_length=100)
    description = models.TextField(_("Description"), blank=True)
    color = models.CharField(_("Couleur"), max_length=7, default="#6c757d")
    priority = models.PositiveIntegerField(
        _("Priorité"), 
        default=1, 
        help_text=_("1 = plus haute priorité")
    )
    
    # Permissions globales
    can_access_admin = models.BooleanField(_("Accès administration"), default=False)
    can_view_reports = models.BooleanField(_("Voir les rapports"), default=False)
    can_manage_members = models.BooleanField(_("Gérer les membres"), default=False)
    can_manage_inventory = models.BooleanField(_("Gérer l'inventaire"), default=False)
    can_manage_sales = models.BooleanField(_("Gérer les ventes"), default=False)
    can_manage_finance = models.BooleanField(_("Gérer les finances"), default=False)
    can_validate_transactions = models.BooleanField(_("Valider les transactions"), default=False)
    
    class Meta:
        verbose_name = _("Rôle utilisateur")
        verbose_name_plural = _("Rôles utilisateurs")
        ordering = ['priority', 'name']
    
    def __str__(self):
        return self.display_name


class UserProfile(BaseModel):
    """
    Profil étendu des utilisateurs.
    """
    LANGUAGE_CHOICES = [
        ('fr', _('Français')),
        ('en', _('Anglais')),
    ]
    
    THEME_CHOICES = [
        ('light', _('Clair')),
        ('dark', _('Sombre')),
        ('auto', _('Automatique')),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name=_("Utilisateur")
    )
    
    # Rôle et membre associé
    role = models.ForeignKey(
        UserRole,
        on_delete=models.PROTECT,
        verbose_name=_("Rôle"),
        null=True,
        blank=True
    )
    member = models.OneToOneField(
        'members.Member',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Membre associé")
    )
    
    # Informations personnelles supplémentaires
    phone = models.CharField(_("Téléphone"), max_length=20, blank=True)
    avatar = models.ImageField(
        _("Avatar"), 
        upload_to='avatars/', 
        blank=True, 
        null=True
    )
    bio = models.TextField(_("Biographie"), blank=True, max_length=500)
    
    # Préférences
    language = models.CharField(
        _("Langue"),
        max_length=5,
        choices=LANGUAGE_CHOICES,
        default='fr'
    )
    theme = models.CharField(
        _("Thème"),
        max_length=10,
        choices=THEME_CHOICES,
        default='light'
    )
    timezone = models.CharField(
        _("Fuseau horaire"),
        max_length=50,
        default='Africa/Abidjan'
    )
    
    # Notifications
    email_notifications = models.BooleanField(_("Notifications email"), default=True)
    sms_notifications = models.BooleanField(_("Notifications SMS"), default=False)
    
    # Sécurité
    two_factor_enabled = models.BooleanField(_("Authentification à 2 facteurs"), default=False)
    last_password_change = models.DateTimeField(_("Dernier changement de mot de passe"), null=True, blank=True)
    password_expires_at = models.DateTimeField(_("Expiration du mot de passe"), null=True, blank=True)
    
    # Statistiques d'utilisation
    last_login_ip = models.GenericIPAddressField(_("Dernière IP de connexion"), null=True, blank=True)
    login_count = models.PositiveIntegerField(_("Nombre de connexions"), default=0)
    
    class Meta:
        verbose_name = _("Profil utilisateur")
        verbose_name_plural = _("Profils utilisateurs")
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.role})"
    
    @property
    def display_name(self):
        """Nom d'affichage préféré."""
        if self.user.get_full_name():
            return self.user.get_full_name()
        elif self.member:
            return self.member.full_name
        return self.user.username
    
    def has_permission(self, permission_name):
        """Vérification des permissions basée sur le rôle."""
        if not self.role:
            return False
        
        # Mappage des permissions
        permission_mapping = {
            'can_access_admin': self.role.can_access_admin,
            'can_view_reports': self.role.can_view_reports,
            'can_manage_members': self.role.can_manage_members,
            'can_manage_inventory': self.role.can_manage_inventory,
            'can_manage_sales': self.role.can_manage_sales,
            'can_manage_finance': self.role.can_manage_finance,
            'can_validate_transactions': self.role.can_validate_transactions,
        }
        
        return permission_mapping.get(permission_name, False)


class PermissionLog(BaseModel):
    """
    Journal des changements de permissions.
    """
    ACTION_CHOICES = [
        ('granted', _('Accordé')),
        ('revoked', _('Révoqué')),
        ('modified', _('Modifié')),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='permission_logs',
        verbose_name=_("Utilisateur concerné")
    )
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='permission_changes_made',
        verbose_name=_("Modifié par")
    )
    
    action = models.CharField(_("Action"), max_length=20, choices=ACTION_CHOICES)
    permission_name = models.CharField(_("Permission"), max_length=100)
    old_value = models.TextField(_("Ancienne valeur"), blank=True)
    new_value = models.TextField(_("Nouvelle valeur"), blank=True)
    reason = models.TextField(_("Motif"), blank=True)
    ip_address = models.GenericIPAddressField(_("Adresse IP"), null=True, blank=True)
    
    class Meta:
        verbose_name = _("Journal des permissions")
        verbose_name_plural = _("Journal des permissions")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.permission_name} - {self.get_action_display()}"


class LoginAttempt(BaseModel):
    """
    Tentatives de connexion pour sécurité.
    """
    SUCCESS_CHOICES = [
        (True, _('Succès')),
        (False, _('Échec')),
    ]
    
    username = models.CharField(_("Nom d'utilisateur"), max_length=150)
    ip_address = models.GenericIPAddressField(_("Adresse IP"))
    user_agent = models.TextField(_("Navigateur"), blank=True)
    success = models.BooleanField(_("Succès"), choices=SUCCESS_CHOICES)
    failure_reason = models.CharField(_("Raison de l'échec"), max_length=200, blank=True)
    
    class Meta:
        verbose_name = _("Tentative de connexion")
        verbose_name_plural = _("Tentatives de connexion")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['username', 'ip_address']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        status = "Succès" if self.success else "Échec"
        return f"{self.username} - {status} - {self.ip_address}"


class SessionActivity(BaseModel):
    """
    Activité des sessions utilisateur.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='session_activities',
        verbose_name=_("Utilisateur")
    )
    session_key = models.CharField(_("Clé de session"), max_length=40)
    ip_address = models.GenericIPAddressField(_("Adresse IP"))
    user_agent = models.TextField(_("Navigateur"), blank=True)
    
    # Timestamps de session
    login_time = models.DateTimeField(_("Heure de connexion"), auto_now_add=True)
    logout_time = models.DateTimeField(_("Heure de déconnexion"), null=True, blank=True)
    last_activity = models.DateTimeField(_("Dernière activité"), auto_now=True)
    
    # Localisation (optionnel)
    country = models.CharField(_("Pays"), max_length=100, blank=True)
    city = models.CharField(_("Ville"), max_length=100, blank=True)
    
    class Meta:
        verbose_name = _("Activité de session")
        verbose_name_plural = _("Activités de session")
        ordering = ['-login_time']
    
    def __str__(self):
        return f"{self.user.username} - {self.login_time}"
    
    @property
    def session_duration(self):
        """Durée de la session."""
        if self.logout_time:
            return self.logout_time - self.login_time
        return None
    
    @property
    def is_active(self):
        """Vérification si la session est toujours active."""
        return self.logout_time is None


# Signaux pour créer automatiquement les profils
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Création automatique du profil utilisateur."""
    if created:
        # Déterminer le rôle par défaut
        default_role = None
        try:
            # Si c'est le premier utilisateur (superuser), lui donner le rôle admin
            if instance.is_superuser and User.objects.count() == 1:
                default_role = UserRole.objects.get(name='admin')
            else:
                default_role = UserRole.objects.get(name='visitor')
        except UserRole.DoesNotExist:
            pass
        
        UserProfile.objects.create(
            user=instance,
            role=default_role
        )

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Sauvegarde automatique du profil utilisateur."""
    if hasattr(instance, 'profile'):
        instance.profile.save()


class CooperativeAccess(BaseModel):
    """
    Gestion des accès spécifiques à la coopérative.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='cooperative_access',
        verbose_name=_("Utilisateur")
    )
    
    # Accès par module
    can_view_dashboard = models.BooleanField(_("Tableau de bord"), default=True)
    can_manage_own_profile = models.BooleanField(_("Gérer son profil"), default=True)
    
    # Membres
    can_view_members = models.BooleanField(_("Voir les membres"), default=False)
    can_add_members = models.BooleanField(_("Ajouter des membres"), default=False)
    can_edit_members = models.BooleanField(_("Modifier les membres"), default=False)
    can_delete_members = models.BooleanField(_("Supprimer les membres"), default=False)
    
    # Inventaire
    can_view_inventory = models.BooleanField(_("Voir l'inventaire"), default=False)
    can_add_products = models.BooleanField(_("Ajouter des produits"), default=False)
    can_edit_products = models.BooleanField(_("Modifier les produits"), default=False)
    can_delete_products = models.BooleanField(_("Supprimer les produits"), default=False)
    can_manage_stock = models.BooleanField(_("Gérer les stocks"), default=False)
    
    # Ventes
    can_view_sales = models.BooleanField(_("Voir les ventes"), default=False)
    can_create_sales = models.BooleanField(_("Créer des ventes"), default=False)
    can_edit_sales = models.BooleanField(_("Modifier les ventes"), default=False)
    can_delete_sales = models.BooleanField(_("Supprimer les ventes"), default=False)
    can_process_payments = models.BooleanField(_("Traiter les paiements"), default=False)
    
    # Finances
    can_view_finances = models.BooleanField(_("Voir les finances"), default=False)
    can_create_transactions = models.BooleanField(_("Créer des transactions"), default=False)
    can_validate_transactions = models.BooleanField(_("Valider les transactions"), default=False)
    can_manage_accounts = models.BooleanField(_("Gérer les comptes"), default=False)
    can_manage_loans = models.BooleanField(_("Gérer les prêts"), default=False)
    
    # Rapports
    can_view_basic_reports = models.BooleanField(_("Rapports de base"), default=False)
    can_view_financial_reports = models.BooleanField(_("Rapports financiers"), default=False)
    can_export_data = models.BooleanField(_("Exporter les données"), default=False)
    
    # Administration
    can_manage_users = models.BooleanField(_("Gérer les utilisateurs"), default=False)
    can_manage_permissions = models.BooleanField(_("Gérer les permissions"), default=False)
    can_view_logs = models.BooleanField(_("Voir les journaux"), default=False)
    can_backup_data = models.BooleanField(_("Sauvegarder les données"), default=False)
    
    class Meta:
        verbose_name = _("Accès coopérative")
        verbose_name_plural = _("Accès coopérative")
    
    def __str__(self):
        return f"Accès de {self.user.username}"
