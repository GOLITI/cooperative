from rest_framework import serializers
from .models import MembershipType, Member, MembershipFee, FamilyMember
from core.serializers import AddressSerializer, ContactSerializer


class MembershipTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembershipType
        fields = ['id', 'name', 'description', 'monthly_fee', 'benefits', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class FamilyMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyMember
        fields = ['id', 'name', 'relationship', 'birth_date', 'phone', 'created_at']
        read_only_fields = ['id', 'created_at']


class MembershipFeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembershipFee
        fields = ['id', 'member', 'amount', 'period_month', 'period_year', 'payment_date', 
                 'payment_method', 'receipt_number', 'notes', 'created_at']
        read_only_fields = ['id', 'receipt_number', 'created_at']


class MemberListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des membres (données simplifiées)"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    membership_type_name = serializers.CharField(source='membership_type.name', read_only=True)
    
    class Meta:
        model = Member
        fields = ['id', 'membership_number', 'user_name', 'membership_type_name', 'status', 
                 'join_date', 'photo', 'is_active']
        read_only_fields = ['id', 'membership_number']


class MemberDetailSerializer(serializers.ModelSerializer):
    """Serializer pour le détail d'un membre (toutes les données)"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    membership_type_name = serializers.CharField(source='membership_type.name', read_only=True)
    address = AddressSerializer(read_only=True)
    contact = ContactSerializer(read_only=True)
    family_members = FamilyMemberSerializer(many=True, read_only=True)
    fees = MembershipFeeSerializer(many=True, read_only=True)
    
    class Meta:
        model = Member
        fields = ['id', 'membership_number', 'user', 'user_name', 'user_email', 'membership_type', 
                 'membership_type_name', 'birth_date', 'gender', 'nationality', 'id_number', 
                 'profession', 'address', 'contact', 'emergency_contact_name', 
                 'emergency_contact_phone', 'emergency_contact_relation', 'join_date', 'status', 
                 'skills', 'specialties', 'photo', 'id_document', 'family_members', 'fees',
                 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'membership_number', 'created_at', 'updated_at']


class MemberCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création d'un membre"""
    address_id = serializers.IntegerField(write_only=True)
    contact_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Member
        fields = ['user', 'membership_type', 'birth_date', 'gender', 'nationality', 'id_number', 
                 'profession', 'address_id', 'contact_id', 'emergency_contact_name', 
                 'emergency_contact_phone', 'emergency_contact_relation', 'join_date', 
                 'skills', 'specialties', 'photo', 'id_document']
        
    def create(self, validated_data):
        address_id = validated_data.pop('address_id')
        contact_id = validated_data.pop('contact_id')
        
        # Générer automatiquement le numéro d'adhésion
        last_member = Member.objects.filter(membership_number__startswith='MB').order_by('id').last()
        if last_member:
            last_number = int(last_member.membership_number[2:])
            membership_number = f"MB{last_number + 1:06d}"
        else:
            membership_number = "MB000001"
        
        validated_data['membership_number'] = membership_number
        validated_data['address_id'] = address_id
        validated_data['contact_id'] = contact_id
        
        return super().create(validated_data)