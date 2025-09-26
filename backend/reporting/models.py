"""
Modèles pour le système de reporting avancé.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from core.models import BaseModel
import json


class ReportTemplate(BaseModel):
    """
    Modèles de rapports réutilisables.
    """
    REPORT_TYPE_CHOICES = [
        ('financial', _('Rapport financier')),
        ('members', _('Rapport des membres')),
        ('sales', _('Rapport des ventes')),
        ('inventory', _('Rapport d\'inventaire')),
        ('custom', _('Rapport personnalisé')),
    ]
    
    OUTPUT_FORMAT_CHOICES = [
        ('json', 'JSON'),
        ('csv', 'CSV'),
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
    ]
    
    name = models.CharField(_("Nom du rapport"), max_length=200)
    description = models.TextField(_("Description"), blank=True)
    report_type = models.CharField(
        _("Type de rapport"),
        max_length=20,
        choices=REPORT_TYPE_CHOICES
    )
    
    # Configuration du rapport
    query_config = models.JSONField(
        _("Configuration des requêtes"),
        default=dict,
        help_text=_("Configuration JSON des filtres et paramètres")
    )
    fields_config = models.JSONField(
        _("Configuration des champs"),
        default=list,
        help_text=_("Liste des champs à inclure dans le rapport")
    )
    
    # Paramètres d'affichage
    output_formats = models.JSONField(
        _("Formats de sortie supportés"),
        default=list,
        help_text=_("Formats dans lesquels le rapport peut être généré")
    )
    
    # Permissions et accès
    is_public = models.BooleanField(_("Rapport public"), default=False)
    allowed_roles = models.JSONField(
        _("Rôles autorisés"),
        default=list,
        blank=True,
        help_text=_("Liste des rôles autorisés à utiliser ce rapport")
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("Créé par"),
        related_name='created_reports'
    )
    
    class Meta:
        verbose_name = _("Modèle de rapport")
        verbose_name_plural = _("Modèles de rapports")
        ordering = ['name']
    
    def __str__(self):
        return self.name


class ReportExecution(BaseModel):
    """
    Historique d'exécution des rapports.
    """
    STATUS_CHOICES = [
        ('pending', _('En attente')),
        ('running', _('En cours')),
        ('completed', _('Terminé')),
        ('failed', _('Échoué')),
        ('cancelled', _('Annulé')),
    ]
    
    template = models.ForeignKey(
        ReportTemplate,
        on_delete=models.CASCADE,
        verbose_name=_("Modèle de rapport"),
        related_name='executions'
    )
    
    # Paramètres d'exécution
    parameters = models.JSONField(
        _("Paramètres d'exécution"),
        default=dict,
        help_text=_("Paramètres utilisés pour cette exécution")
    )
    output_format = models.CharField(
        _("Format de sortie"),
        max_length=10,
        choices=ReportTemplate.OUTPUT_FORMAT_CHOICES
    )
    
    # État de l'exécution
    status = models.CharField(
        _("État"),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    started_at = models.DateTimeField(_("Démarré à"), null=True, blank=True)
    completed_at = models.DateTimeField(_("Terminé à"), null=True, blank=True)
    
    # Résultats
    result_data = models.JSONField(
        _("Données du rapport"),
        null=True,
        blank=True,
        help_text=_("Résultats du rapport en format JSON")
    )
    result_file = models.FileField(
        _("Fichier de résultat"),
        upload_to='reports/results/',
        null=True,
        blank=True
    )
    
    # Métadonnées
    execution_time = models.FloatField(
        _("Temps d'exécution (secondes)"),
        null=True,
        blank=True
    )
    row_count = models.IntegerField(
        _("Nombre de lignes"),
        null=True,
        blank=True
    )
    error_message = models.TextField(_("Message d'erreur"), blank=True)
    
    # Audit
    executed_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("Exécuté par"),
        related_name='executed_reports'
    )
    
    class Meta:
        verbose_name = _("Exécution de rapport")
        verbose_name_plural = _("Exécutions de rapports")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.template.name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def duration(self):
        """Durée d'exécution calculée."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


class ReportWidget(BaseModel):
    """
    Widgets de données pour tableaux de bord.
    """
    WIDGET_TYPE_CHOICES = [
        ('chart_line', _('Graphique en ligne')),
        ('chart_bar', _('Graphique en barres')),
        ('chart_pie', _('Graphique en camembert')),
        ('chart_area', _('Graphique en aire')),
        ('table', _('Tableau')),
        ('metric', _('Métrique')),
        ('progress', _('Barre de progression')),
        ('gauge', _('Jauge')),
    ]
    
    name = models.CharField(_("Nom du widget"), max_length=200)
    description = models.TextField(_("Description"), blank=True)
    widget_type = models.CharField(
        _("Type de widget"),
        max_length=20,
        choices=WIDGET_TYPE_CHOICES
    )
    
    # Configuration des données
    data_source = models.CharField(
        _("Source de données"),
        max_length=100,
        help_text=_("Nom de la vue ou méthode fournissant les données")
    )
    query_parameters = models.JSONField(
        _("Paramètres de requête"),
        default=dict,
        blank=True
    )
    
    # Configuration d'affichage
    chart_config = models.JSONField(
        _("Configuration du graphique"),
        default=dict,
        help_text=_("Configuration Chart.js ou autre bibliothèque")
    )
    
    # Mise à jour et cache
    refresh_interval = models.PositiveIntegerField(
        _("Intervalle de rafraîchissement (minutes)"),
        default=15,
        help_text=_("Fréquence de mise à jour des données")
    )
    cache_duration = models.PositiveIntegerField(
        _("Durée de cache (minutes)"),
        default=5,
        help_text=_("Durée de conservation des données en cache")
    )
    
    # Permissions
    is_public = models.BooleanField(_("Widget public"), default=False)
    allowed_roles = models.JSONField(
        _("Rôles autorisés"),
        default=list,
        blank=True
    )
    
    # Ordre d'affichage
    display_order = models.PositiveIntegerField(_("Ordre d'affichage"), default=0)
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("Créé par"),
        related_name='created_widgets'
    )
    
    class Meta:
        verbose_name = _("Widget de rapport")
        verbose_name_plural = _("Widgets de rapports")
        ordering = ['display_order', 'name']
    
    def __str__(self):
        return self.name
