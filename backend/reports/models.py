from django.db import models
from django.contrib.auth.models import User
from core.models import TimestampedModel

class Report(TimestampedModel):
    """Rapports générés"""
    name = models.CharField(max_length=200, verbose_name="Nom du rapport")
    description = models.TextField(blank=True, verbose_name="Description")
    
    report_type = models.CharField(
        max_length=50,
        choices=[
            ('members_report', 'Rapport des membres'),
            ('financial_report', 'Rapport financier'),
            ('inventory_report', 'Rapport de stock'),
            ('sales_report', 'Rapport des ventes'),
            ('loan_report', 'Rapport des prêts'),
            ('custom_report', 'Rapport personnalisé')
        ],
        verbose_name="Type de rapport"
    )
    
    # Paramètres du rapport
    parameters = models.JSONField(default=dict, verbose_name="Paramètres")
    
    # Période couverte
    period_start = models.DateField(verbose_name="Début de période")
    period_end = models.DateField(verbose_name="Fin de période")
    
    # Fichier généré
    file_path = models.CharField(max_length=500, blank=True, verbose_name="Chemin du fichier")
    file_format = models.CharField(
        max_length=10,
        choices=[
            ('pdf', 'PDF'),
            ('excel', 'Excel'),
            ('csv', 'CSV')
        ],
        verbose_name="Format de fichier"
    )
    
    # Métadonnées
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Généré par")
    generation_time = models.DateTimeField(verbose_name="Heure de génération")
    file_size = models.PositiveIntegerField(default=0, verbose_name="Taille du fichier (bytes)")
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('generating', 'En cours de génération'),
            ('completed', 'Terminé'),
            ('failed', 'Échoué')
        ],
        default='generating',
        verbose_name="Statut"
    )
    
    class Meta:
        verbose_name = "Rapport"
        verbose_name_plural = "Rapports"
        ordering = ['-generation_time']
    
    def __str__(self):
        return f"{self.name} - {self.generation_time.date()}"

class Dashboard(TimestampedModel):
    """Tableaux de bord personnalisés"""
    name = models.CharField(max_length=200, verbose_name="Nom du tableau de bord")
    description = models.TextField(blank=True, verbose_name="Description")
    
    # Configuration des widgets
    widgets_config = models.JSONField(default=list, verbose_name="Configuration des widgets")
    
    # Accès
    is_public = models.BooleanField(default=False, verbose_name="Public")
    allowed_users = models.ManyToManyField(User, blank=True, verbose_name="Utilisateurs autorisés")
    
    # Métadonnées
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_dashboards', verbose_name="Créé par")
    is_default = models.BooleanField(default=False, verbose_name="Tableau par défaut")
    
    class Meta:
        verbose_name = "Tableau de bord"
        verbose_name_plural = "Tableaux de bord"
    
    def __str__(self):
        return self.name

class ReportTemplate(TimestampedModel):
    """Modèles de rapports"""
    name = models.CharField(max_length=200, verbose_name="Nom du modèle")
    description = models.TextField(verbose_name="Description")
    
    report_type = models.CharField(
        max_length=50,
        choices=[
            ('members_report', 'Rapport des membres'),
            ('financial_report', 'Rapport financier'),
            ('inventory_report', 'Rapport de stock'),
            ('sales_report', 'Rapport des ventes'),
            ('loan_report', 'Rapport des prêts')
        ],
        verbose_name="Type de rapport"
    )
    
    # Configuration du modèle
    template_config = models.JSONField(default=dict, verbose_name="Configuration du modèle")
    default_parameters = models.JSONField(default=dict, verbose_name="Paramètres par défaut")
    
    # Design
    html_template = models.TextField(blank=True, verbose_name="Template HTML")
    css_styles = models.TextField(blank=True, verbose_name="Styles CSS")
    
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Créé par")
    
    class Meta:
        verbose_name = "Modèle de rapport"
        verbose_name_plural = "Modèles de rapports"
    
    def __str__(self):
        return self.name
