from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Report, Dashboard, ReportTemplate

User = get_user_model()


class ReportSerializer(serializers.ModelSerializer):
    """Serializer pour les rapports."""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = Report
        fields = [
            'id', 'name', 'description', 'report_type', 'parameters',
            'status', 'created_by', 'created_by_name', 'created_at',
            'generated_at', 'file_url'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'generated_at']
    
    def validate_parameters(self, value):
        """Valider les paramètres du rapport."""
        if value and not isinstance(value, dict):
            raise serializers.ValidationError("Les paramètres doivent être un objet JSON valide.")
        return value
    
    def validate_report_type(self, value):
        """Valider le type de rapport."""
        allowed_types = ['members', 'sales', 'inventory', 'finance']
        if value not in allowed_types:
            raise serializers.ValidationError(
                f"Type de rapport non valide. Types autorisés: {', '.join(allowed_types)}"
            )
        return value


class DashboardSerializer(serializers.ModelSerializer):
    """Serializer pour les tableaux de bord."""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    widget_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Dashboard
        fields = [
            'id', 'name', 'description', 'layout', 'is_public',
            'created_by', 'created_by_name', 'created_at', 'updated_at',
            'widget_count'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
    def get_widget_count(self, obj):
        """Retourner le nombre de widgets (simulé car pas de modèle DashboardWidget)."""
        # Si le layout est défini, compter les widgets
        if obj.layout and isinstance(obj.layout, dict):
            return len(obj.layout.get('widgets', []))
        return 0
    
    def validate_layout(self, value):
        """Valider la structure du layout."""
        if value and not isinstance(value, dict):
            raise serializers.ValidationError("Le layout doit être un objet JSON valide.")
        
        # Validation basique de la structure
        if value and 'widgets' in value:
            widgets = value['widgets']
            if not isinstance(widgets, list):
                raise serializers.ValidationError("Les widgets doivent être une liste.")
            
            for widget in widgets:
                if not isinstance(widget, dict):
                    raise serializers.ValidationError("Chaque widget doit être un objet.")
                
                required_fields = ['type', 'position']
                for field in required_fields:
                    if field not in widget:
                        raise serializers.ValidationError(
                            f"Le champ '{field}' est requis pour chaque widget."
                        )
        
        return value


class ReportTemplateSerializer(serializers.ModelSerializer):
    """Serializer pour les modèles de rapports."""
    
    class Meta:
        model = ReportTemplate
        fields = [
            'id', 'name', 'description', 'report_type', 'template_content',
            'default_parameters', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_template_content(self, value):
        """Valider le contenu du modèle."""
        if value and not isinstance(value, dict):
            raise serializers.ValidationError("Le contenu du modèle doit être un objet JSON valide.")
        
        # Validation basique de la structure
        if value:
            required_fields = ['title', 'sections']
            for field in required_fields:
                if field not in value:
                    raise serializers.ValidationError(
                        f"Le champ '{field}' est requis dans le contenu du modèle."
                    )
            
            sections = value.get('sections', [])
            if not isinstance(sections, list):
                raise serializers.ValidationError("Les sections doivent être une liste.")
            
            for section in sections:
                if not isinstance(section, dict):
                    raise serializers.ValidationError("Chaque section doit être un objet.")
                
                if 'type' not in section:
                    raise serializers.ValidationError("Chaque section doit avoir un type.")
        
        return value
    
    def validate_default_parameters(self, value):
        """Valider les paramètres par défaut."""
        if value and not isinstance(value, dict):
            raise serializers.ValidationError("Les paramètres par défaut doivent être un objet JSON valide.")
        return value
    
    def validate_report_type(self, value):
        """Valider le type de rapport."""
        allowed_types = ['members', 'sales', 'inventory', 'finance']
        if value not in allowed_types:
            raise serializers.ValidationError(
                f"Type de rapport non valide. Types autorisés: {', '.join(allowed_types)}"
            )
        return value


# Serializers additionnels pour des données spécifiques

class ReportGenerationRequestSerializer(serializers.Serializer):
    """Serializer pour les demandes de génération de rapport."""
    parameters = serializers.JSONField(required=False, allow_null=True)
    format = serializers.ChoiceField(
        choices=['json', 'csv', 'pdf'],
        default='json',
        required=False
    )
    
    def validate_parameters(self, value):
        """Valider les paramètres de génération."""
        if value and not isinstance(value, dict):
            raise serializers.ValidationError("Les paramètres doivent être un objet JSON valide.")
        return value


class DashboardWidgetSerializer(serializers.Serializer):
    """Serializer pour les widgets de tableau de bord (structure de données)."""
    type = serializers.ChoiceField(choices=[
        'kpi', 'chart', 'table', 'progress', 'list'
    ])
    title = serializers.CharField(max_length=200)
    position = serializers.JSONField()
    size = serializers.JSONField()
    config = serializers.JSONField(required=False, allow_null=True)
    
    def validate_position(self, value):
        """Valider la position du widget."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("La position doit être un objet.")
        
        required_fields = ['x', 'y']
        for field in required_fields:
            if field not in value or not isinstance(value[field], int):
                raise serializers.ValidationError(f"Le champ '{field}' doit être un entier.")
        
        return value
    
    def validate_size(self, value):
        """Valider la taille du widget."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("La taille doit être un objet.")
        
        required_fields = ['width', 'height']
        for field in required_fields:
            if field not in value or not isinstance(value[field], int):
                raise serializers.ValidationError(f"Le champ '{field}' doit être un entier.")
        
        return value