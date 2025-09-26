"""
Sérialiseurs pour l'API d'authentification.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import UserProfile, UserRole, CooperativeAccess, SessionActivity


class UserRoleSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les rôles utilisateurs."""
    
    class Meta:
        model = UserRole
        fields = [
            'name', 'display_name', 'description', 'color', 'priority',
            'can_access_admin', 'can_view_reports', 'can_manage_members',
            'can_manage_inventory', 'can_manage_sales', 'can_manage_finance',
            'can_validate_transactions'
        ]
        read_only_fields = ['name']


class CooperativeAccessSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les accès coopérative."""
    
    class Meta:
        model = CooperativeAccess
        exclude = ['user']


class UserProfileSerializer(serializers.ModelSerializer):
    """Sérialiseur pour le profil utilisateur."""
    
    role = UserRoleSerializer(read_only=True)
    cooperative_access = CooperativeAccessSerializer(source='user.cooperative_access', read_only=True)
    member_number = serializers.CharField(source='member.member_number', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'phone', 'avatar', 'bio', 'language', 'theme', 'timezone',
            'email_notifications', 'sms_notifications', 'two_factor_enabled',
            'last_login_ip', 'login_count', 'role', 'cooperative_access', 'member_number'
        ]
        read_only_fields = ['last_login_ip', 'login_count']


class UserSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les utilisateurs."""
    
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_active', 'date_joined', 'last_login', 'profile'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']


class LoginSerializer(serializers.Serializer):
    """Sérialiseur pour la connexion."""
    
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    remember_me = serializers.BooleanField(default=False)
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            
            if not user:
                raise serializers.ValidationError(
                    'Nom d\'utilisateur ou mot de passe incorrect.'
                )
            
            if not user.is_active:
                raise serializers.ValidationError(
                    'Ce compte utilisateur est désactivé.'
                )
            
            attrs['user'] = user
            return attrs
        
        raise serializers.ValidationError(
            'Les champs username et password sont requis.'
        )


class RegisterSerializer(serializers.ModelSerializer):
    """Sérialiseur pour l'inscription."""
    
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    role_name = serializers.CharField(write_only=True, default='member')
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'password', 'password_confirm', 'role_name'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate_email(self, value):
        """Valider l'unicité de l'email."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                'Un utilisateur avec cet email existe déjà.'
            )
        return value
    
    def validate(self, attrs):
        """Valider les mots de passe."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError(
                'Les mots de passe ne correspondent pas.'
            )
        
        # Vérifier que le rôle existe
        role_name = attrs.get('role_name', 'member')
        if not UserRole.objects.filter(name=role_name).exists():
            raise serializers.ValidationError(
                f'Le rôle "{role_name}" n\'existe pas.'
            )
        
        return attrs
    
    def create(self, validated_data):
        """Créer un nouvel utilisateur avec profil."""
        password = validated_data.pop('password')
        validated_data.pop('password_confirm')
        role_name = validated_data.pop('role_name', 'member')
        
        # Créer l'utilisateur
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        
        # Assigner le rôle au profil (créé automatiquement par signal)
        try:
            role = UserRole.objects.get(name=role_name)
            user.profile.role = role
            user.profile.save()
        except UserRole.DoesNotExist:
            pass
        
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """Sérialiseur pour changer le mot de passe."""
    
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate_old_password(self, value):
        """Valider l'ancien mot de passe."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Ancien mot de passe incorrect.')
        return value
    
    def validate(self, attrs):
        """Valider les nouveaux mots de passe."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError(
                'Les nouveaux mots de passe ne correspondent pas.'
            )
        return attrs
    
    def save(self):
        """Changer le mot de passe."""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class SessionActivitySerializer(serializers.ModelSerializer):
    """Sérialiseur pour l'activité de session."""
    
    user = serializers.StringRelatedField()
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = SessionActivity
        fields = [
            'id', 'user', 'ip_address', 'user_agent', 'country', 'city',
            'login_time', 'logout_time', 'last_activity', 'is_active', 'duration'
        ]
    
    def get_duration(self, obj):
        """Calculer la durée de session."""
        if obj.logout_time:
            delta = obj.logout_time - obj.login_time
            return int(delta.total_seconds())
        elif obj.last_activity:
            delta = obj.last_activity - obj.login_time
            return int(delta.total_seconds())
        return None


class UpdateProfileSerializer(serializers.ModelSerializer):
    """Sérialiseur pour mettre à jour le profil utilisateur."""
    
    # Champs utilisateur
    first_name = serializers.CharField(source='user.first_name', max_length=150)
    last_name = serializers.CharField(source='user.last_name', max_length=150)
    email = serializers.EmailField(source='user.email')
    
    class Meta:
        model = UserProfile
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'bio',
            'language', 'theme', 'timezone', 'email_notifications',
            'sms_notifications'
        ]
    
    def validate_email(self, value):
        """Valider l'unicité de l'email."""
        user = self.instance.user
        if User.objects.filter(email=value).exclude(id=user.id).exists():
            raise serializers.ValidationError(
                'Un utilisateur avec cet email existe déjà.'
            )
        return value
    
    def update(self, instance, validated_data):
        """Mettre à jour l'utilisateur et le profil."""
        # Données utilisateur
        user_data = validated_data.pop('user', {})
        user = instance.user
        
        for field, value in user_data.items():
            setattr(user, field, value)
        user.save()
        
        # Données profil
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        
        return instance