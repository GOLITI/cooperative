"""
Sérialiseurs pour l'API de gestion des membres.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Sum
from decimal import Decimal

from .models import (
    Member, MembershipType, MemberPayment, MembershipHistory
)
from core.models import Address, ContactInfo


class AddressSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les adresses."""
    
    class Meta:
        model = Address
        fields = [
            'street_address', 'city', 'state_province', 
            'postal_code', 'country', 'is_primary'
        ]


class ContactInfoSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les informations de contact."""
    
    class Meta:
        model = ContactInfo
        fields = [
            'phone_primary', 'phone_secondary', 'email_primary', 
            'email_secondary', 'website', 'social_media'
        ]


class MembershipTypeSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les types d'adhésion."""
    
    member_count = serializers.SerializerMethodField()
    
    class Meta:
        model = MembershipType
        fields = [
            'id', 'name', 'description', 'monthly_fee', 'benefits', 
            'color', 'is_active', 'member_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_member_count(self, obj):
        """Nombre de membres avec ce type d'adhésion."""
        return obj.members.filter(is_active=True).count()


class MemberPaymentSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les paiements des membres."""
    
    member_name = serializers.CharField(source='member.get_full_name', read_only=True)
    member_number = serializers.CharField(source='member.member_number', read_only=True)
    
    class Meta:
        model = MemberPayment
        fields = [
            'id', 'member', 'member_name', 'member_number', 'amount', 
            'payment_date', 'payment_method', 'reference', 'notes',
            'is_validated', 'validated_by', 'validated_at', 
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'validated_by', 'validated_at', 'created_at', 'updated_at'
        ]
    
    def validate_amount(self, value):
        """Valider le montant du paiement."""
        if value <= 0:
            raise serializers.ValidationError("Le montant doit être positif.")
        return value


class MembershipHistorySerializer(serializers.ModelSerializer):
    """Sérialiseur pour l'historique d'adhésion."""
    
    member_name = serializers.CharField(source='member.get_full_name', read_only=True)
    membership_type_name = serializers.CharField(source='membership_type.name', read_only=True)
    
    class Meta:
        model = MembershipHistory
        fields = [
            'id', 'member', 'member_name', 'membership_type', 
            'membership_type_name', 'start_date', 'end_date', 
            'status', 'notes', 'created_at'
        ]
        read_only_fields = ['created_at']


class MemberListSerializer(serializers.ModelSerializer):
    """Sérialiseur pour la liste des membres (données minimales)."""
    
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    membership_type_name = serializers.CharField(source='membership_type.name', read_only=True)
    membership_type_color = serializers.CharField(source='membership_type.color', read_only=True)
    age = serializers.SerializerMethodField()
    membership_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Member
        fields = [
            'id', 'member_number', 'full_name', 'first_name', 'last_name',
            'membership_type_name', 'membership_type_color', 'age',
            'membership_status', 'join_date', 'is_active'
        ]
    
    def get_age(self, obj):
        """Calculer l'âge du membre."""
        if obj.birth_date:
            today = timezone.now().date()
            return today.year - obj.birth_date.year - (
                (today.month, today.day) < (obj.birth_date.month, obj.birth_date.day)
            )
        return None
    
    def get_membership_status(self, obj):
        """Status de l'adhésion."""
        if not obj.is_active:
            return "Inactif"
        
        # Vérifier si les cotisations sont à jour
        last_payment = obj.payments.filter(is_validated=True).order_by('-payment_date').first()
        if last_payment:
            days_since_payment = (timezone.now().date() - last_payment.payment_date).days
            if days_since_payment <= 30:
                return "À jour"
            elif days_since_payment <= 60:
                return "En retard"
            else:
                return "Très en retard"
        
        return "Aucun paiement"


class MemberDetailSerializer(serializers.ModelSerializer):
    """Sérialiseur complet pour les détails d'un membre."""
    
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    membership_type = MembershipTypeSerializer(read_only=True)
    address = AddressSerializer(read_only=True)
    contact_info = ContactInfoSerializer(read_only=True)
    age = serializers.SerializerMethodField()
    membership_duration = serializers.SerializerMethodField()
    total_payments = serializers.SerializerMethodField()
    last_payment = serializers.SerializerMethodField()
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Member
        fields = [
            'id', 'member_number', 'full_name', 'first_name', 'last_name',
            'gender', 'birth_date', 'age', 'marital_status', 'profession',
            'national_id', 'membership_type', 'join_date', 'membership_duration',
            'emergency_contact_name', 'emergency_contact_phone', 'bio', 'photo',
            'address', 'contact_info', 'user', 'user_username',
            'total_payments', 'last_payment', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'member_number', 'created_at', 'updated_at', 'full_name'
        ]
    
    def get_age(self, obj):
        """Calculer l'âge du membre."""
        if obj.birth_date:
            today = timezone.now().date()
            return today.year - obj.birth_date.year - (
                (today.month, today.day) < (obj.birth_date.month, obj.birth_date.day)
            )
        return None
    
    def get_membership_duration(self, obj):
        """Durée d'adhésion en jours."""
        if obj.join_date:
            return (timezone.now().date() - obj.join_date).days
        return 0
    
    def get_total_payments(self, obj):
        """Total des paiements validés."""
        return obj.payments.filter(is_validated=True).aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
    
    def get_last_payment(self, obj):
        """Dernier paiement."""
        last_payment = obj.payments.filter(is_validated=True).order_by('-payment_date').first()
        if last_payment:
            return {
                'date': last_payment.payment_date,
                'amount': last_payment.amount,
                'method': last_payment.get_payment_method_display()
            }
        return None


class MemberCreateUpdateSerializer(serializers.ModelSerializer):
    """Sérialiseur pour créer/modifier un membre."""
    
    # Données imbriquées
    address = AddressSerializer(required=False)
    contact_info = ContactInfoSerializer(required=False)
    
    # Champs pour lier à un utilisateur existant
    username = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Member
        fields = [
            'first_name', 'last_name', 'gender', 'birth_date', 
            'marital_status', 'profession', 'national_id',
            'membership_type', 'emergency_contact_name', 
            'emergency_contact_phone', 'bio', 'photo',
            'address', 'contact_info', 'username', 'is_active'
        ]
    
    def validate_national_id(self, value):
        """Valider l'unicité de l'ID national."""
        if value:
            member_id = self.instance.id if self.instance else None
            if Member.objects.filter(national_id=value).exclude(id=member_id).exists():
                raise serializers.ValidationError(
                    "Un membre avec cet ID national existe déjà."
                )
        return value
    
    def validate_birth_date(self, value):
        """Valider la date de naissance."""
        if value and value > timezone.now().date():
            raise serializers.ValidationError(
                "La date de naissance ne peut pas être dans le futur."
            )
        return value
    
    def create(self, validated_data):
        """Créer un nouveau membre avec adresse et contact."""
        address_data = validated_data.pop('address', None)
        contact_data = validated_data.pop('contact_info', None)
        username = validated_data.pop('username', None)
        
        # Lier à un utilisateur existant si fourni
        if username:
            try:
                user = User.objects.get(username=username)
                validated_data['user'] = user
            except User.DoesNotExist:
                raise serializers.ValidationError({
                    'username': 'Utilisateur non trouvé.'
                })
        
        # Créer le membre
        member = Member.objects.create(**validated_data)
        
        # Créer l'adresse si fournie
        if address_data:
            Address.objects.create(member=member, **address_data)
        
        # Créer les infos de contact si fournies
        if contact_data:
            ContactInfo.objects.create(member=member, **contact_data)
        
        return member
    
    def update(self, instance, validated_data):
        """Mettre à jour un membre avec adresse et contact."""
        address_data = validated_data.pop('address', None)
        contact_data = validated_data.pop('contact_info', None)
        username = validated_data.pop('username', None)
        
        # Mettre à jour l'utilisateur lié
        if username:
            try:
                user = User.objects.get(username=username)
                instance.user = user
            except User.DoesNotExist:
                raise serializers.ValidationError({
                    'username': 'Utilisateur non trouvé.'
                })
        
        # Mettre à jour les champs du membre
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Mettre à jour l'adresse
        if address_data:
            address, created = Address.objects.get_or_create(
                member=instance,
                defaults=address_data
            )
            if not created:
                for attr, value in address_data.items():
                    setattr(address, attr, value)
                address.save()
        
        # Mettre à jour les infos de contact
        if contact_data:
            contact, created = ContactInfo.objects.get_or_create(
                member=instance,
                defaults=contact_data
            )
            if not created:
                for attr, value in contact_data.items():
                    setattr(contact, attr, value)
                contact.save()
        
        return instance


class MemberStatsSerializer(serializers.Serializer):
    """Sérialiseur pour les statistiques des membres."""
    
    total_members = serializers.IntegerField()
    active_members = serializers.IntegerField()
    inactive_members = serializers.IntegerField()
    new_members_this_month = serializers.IntegerField()
    members_by_type = serializers.DictField()
    members_by_gender = serializers.DictField()
    average_age = serializers.FloatField()
    total_payments_this_month = serializers.DecimalField(max_digits=12, decimal_places=2)