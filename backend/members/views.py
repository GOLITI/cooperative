"""
Vues API pour la gestion des membres.
"""
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from .models import (
    Member, MembershipType, MemberPayment, MembershipHistory
)
from .serializers import (
    MemberListSerializer, MemberDetailSerializer, MemberCreateUpdateSerializer,
    MembershipTypeSerializer, MemberPaymentSerializer, MembershipHistorySerializer,
    MemberStatsSerializer
)
from accounts.permissions import (
    BaseCooperativePermission, CanViewMembers, CanManageMembers
)


@extend_schema_view(
    list=extend_schema(
        summary="Liste des types d'adhésion",
        description="Récupère la liste complète des types d'adhésion disponibles avec leurs tarifs et conditions.",
        tags=['membres'],
        examples=[
            OpenApiExample(
                'Réponse type',
                value={
                    "count": 3,
                    "results": [
                        {
                            "id": 1,
                            "name": "Membre ordinaire",
                            "description": "Adhésion standard pour les membres individuels",
                            "annual_fee": 25000.00,
                            "voting_rights": True,
                            "loan_eligibility": True
                        }
                    ]
                }
            )
        ]
    ),
    create=extend_schema(
        summary="Créer un type d'adhésion",
        description="Crée un nouveau type d'adhésion avec ses conditions et tarifs.",
        tags=['membres']
    ),
    retrieve=extend_schema(
        summary="Détail d'un type d'adhésion",
        description="Récupère les détails complets d'un type d'adhésion spécifique.",
        tags=['membres']
    ),
    update=extend_schema(
        summary="Modifier un type d'adhésion",
        description="Modifie complètement un type d'adhésion existant.",
        tags=['membres']
    ),
    partial_update=extend_schema(
        summary="Modification partielle d'un type d'adhésion",
        description="Modifie partiellement un type d'adhésion existant.",
        tags=['membres']
    ),
    destroy=extend_schema(
        summary="Supprimer un type d'adhésion",
        description="Supprime définitivement un type d'adhésion (si aucun membre n'y est associé).",
        tags=['membres']
    )
)
class MembershipTypeViewSet(viewsets.ModelViewSet):
    """
    🎫 **Types d'Adhésion**
    
    Gestion des différents types d'adhésion disponibles dans la coopérative.
    Chaque type définit les droits, obligations et tarifs des membres.
    """
    queryset = MembershipType.objects.all()
    serializer_class = MembershipTypeSerializer
    permission_classes = [BaseCooperativePermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'monthly_fee', 'created_at']
    ordering = ['name']
    
    def get_permissions(self):
        """Permissions spécifiques par action."""
        if self.action in ['list', 'retrieve']:
            permission_classes = [CanViewMembers]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [CanManageMembers]
        else:
            permission_classes = [BaseCooperativePermission]
        
        return [permission() for permission in permission_classes]
    
    def destroy(self, request, *args, **kwargs):
        """Empêcher la suppression si des membres utilisent ce type."""
        instance = self.get_object()
        if instance.members.exists():
            return Response(
                {
                    'error': 'Impossible de supprimer ce type d\'adhésion car des membres l\'utilisent.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)


@extend_schema_view(
    list=extend_schema(
        summary="Liste des membres",
        description="Récupère la liste paginée des membres avec leurs informations principales.",
        tags=['membres'],
        parameters=[
            OpenApiParameter(
                name='membership_type',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filtrer par type d\'adhésion (ID)'
            ),
            OpenApiParameter(
                name='gender',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filtrer par genre (M/F)'
            ),
            OpenApiParameter(
                name='is_active',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Filtrer par statut actif'
            ),
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Recherche par nom, prénom ou numéro'
            )
        ]
    ),
    create=extend_schema(
        summary="Créer un nouveau membre",
        description="Enregistre un nouveau membre dans la coopérative avec ses informations complètes.",
        tags=['membres']
    ),
    retrieve=extend_schema(
        summary="Détail d'un membre",
        description="Récupère toutes les informations détaillées d'un membre spécifique.",
        tags=['membres']
    ),
    update=extend_schema(
        summary="Modifier un membre",
        description="Modifie complètement les informations d'un membre existant.",
        tags=['membres']
    ),
    partial_update=extend_schema(
        summary="Modification partielle d'un membre",
        description="Modifie partiellement les informations d'un membre.",
        tags=['membres']
    ),
    destroy=extend_schema(
        summary="Supprimer un membre",
        description="Supprime définitivement un membre (désactive plutôt que supprimer).",
        tags=['membres']
    )
)
class MemberViewSet(viewsets.ModelViewSet):
    """
    👥 **Gestion des Membres**
    
    CRUD complet pour la gestion des membres de la coopérative.
    Inclut les informations personnelles, adhésion, paiements et historique.
    
    **Fonctionnalités :**
    - ✅ Recherche et filtrage avancés
    - 📊 Statistiques et analyses
    - 💰 Gestion des paiements
    - 📋 Historique des adhésions
    """
    queryset = Member.objects.select_related(
        'membership_type', 'address', 'contact_info', 'user'
    ).prefetch_related('payments', 'membership_history')
    
    permission_classes = [BaseCooperativePermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'membership_type': ['exact'],
        'gender': ['exact'],
        'is_active': ['exact'],
        'join_date': ['gte', 'lte'],
        'date_of_birth': ['gte', 'lte']
    }
    search_fields = [
        'first_name', 'last_name', 'member_number', 'national_id',
        'profession', 'user__username', 'user__email'
    ]
    ordering_fields = [
        'first_name', 'last_name', 'member_number', 'join_date', 'created_at'
    ]
    ordering = ['-created_at']
    
    def get_permissions(self):
        """Permissions spécifiques par action."""
        if self.action in ['list', 'retrieve', 'stats', 'export']:
            permission_classes = [CanViewMembers]
        elif self.action in ['create', 'update', 'partial_update', 'destroy', 'activate', 'deactivate']:
            permission_classes = [CanManageMembers]
        else:
            permission_classes = [BaseCooperativePermission]
        
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        """Sérializeur selon l'action."""
        if self.action == 'list':
            return MemberListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return MemberCreateUpdateSerializer
        else:
            return MemberDetailSerializer
    
    def get_queryset(self):
        """Filtrer selon les permissions."""
        queryset = super().get_queryset()
        
        # Filtrer par statut si demandé
        status_filter = self.request.query_params.get('status')
        if status_filter == 'active':
            queryset = queryset.filter(is_active=True)
        elif status_filter == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        # Filtrer par âge si demandé
        min_age = self.request.query_params.get('min_age')
        max_age = self.request.query_params.get('max_age')
        
        if min_age:
            min_birth_date = timezone.now().date() - timedelta(days=int(min_age) * 365)
            queryset = queryset.filter(date_of_birth__lte=min_birth_date)
        
        if max_age:
            max_birth_date = timezone.now().date() - timedelta(days=int(max_age) * 365)
            queryset = queryset.filter(date_of_birth__gte=max_birth_date)
        
        return queryset
    
    @extend_schema(
        summary="Statistiques des membres",
        description="""
        Récupère les statistiques complètes des membres de la coopérative.
        
        **Données incluses :**
        - Nombre total de membres (actifs/inactifs)
        - Nouveaux membres du mois
        - Répartition par type d'adhésion
        - Répartition par genre et âge
        - Historique mensuel des adhésions
        """,
        tags=['membres'],
        examples=[
            OpenApiExample(
                'Réponse statistiques',
                value={
                    "total_members": 150,
                    "active_members": 142,
                    "inactive_members": 8,
                    "new_members_this_month": 5,
                    "members_by_type": {
                        "Membre ordinaire": 120,
                        "Membre fondateur": 30
                    },
                    "members_by_gender": {
                        "M": 85,
                        "F": 65
                    },
                    "average_age": 35.5
                }
            )
        ]
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """📊 Statistiques complètes des membres."""
        # Statistiques de base
        total_members = Member.objects.count()
        active_members = Member.objects.filter(is_active=True).count()
        inactive_members = total_members - active_members
        
        # Nouveaux membres ce mois
        this_month = timezone.now().replace(day=1)
        new_members_this_month = Member.objects.filter(
            created_at__gte=this_month
        ).count()
        
        # Membres par type
        members_by_type = dict(
            Member.objects.filter(is_active=True)
            .values('membership_type__name')
            .annotate(count=Count('id'))
            .values_list('membership_type__name', 'count')
        )
        
        # Membres par genre
        members_by_gender = dict(
            Member.objects.filter(is_active=True)
            .values('gender')
            .annotate(count=Count('id'))
            .values_list('gender', 'count')
        )
        
        # Âge moyen
        average_age = Member.objects.filter(
            is_active=True, date_of_birth__isnull=False
        ).aggregate(
            avg_age=Avg(
                timezone.now().year - 
                timezone.now().date().year
            )
        )['avg_age'] or 0
        
        # Paiements ce mois
        total_payments_this_month = MemberPayment.objects.filter(
            payment_date__gte=this_month,
            is_validated=True
        ).aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        stats = {
            'total_members': total_members,
            'active_members': active_members,
            'inactive_members': inactive_members,
            'new_members_this_month': new_members_this_month,
            'members_by_type': members_by_type,
            'members_by_gender': members_by_gender,
            'average_age': round(average_age, 1),
            'total_payments_this_month': total_payments_this_month
        }
        
        serializer = MemberStatsSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activer un membre."""
        member = self.get_object()
        member.is_active = True
        member.save()
        
        # Créer un historique d'adhésion
        MembershipHistory.objects.create(
            member=member,
            membership_type=member.membership_type,
            start_date=timezone.now().date(),
            status='active',
            notes=f"Réactivation par {request.user.get_full_name()}"
        )
        
        return Response({'message': 'Membre activé avec succès.'})
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Désactiver un membre."""
        member = self.get_object()
        member.is_active = False
        member.save()
        
        # Mettre à jour l'historique d'adhésion
        last_history = member.membership_history.filter(
            end_date__isnull=True
        ).first()
        
        if last_history:
            last_history.end_date = timezone.now().date()
            last_history.status = 'inactive'
            last_history.save()
        
        return Response({'message': 'Membre désactivé avec succès.'})
    
    @action(detail=True, methods=['get'])
    def payments(self, request, pk=None):
        """Historique des paiements d'un membre."""
        member = self.get_object()
        payments = member.payments.all().order_by('-payment_date')
        
        page = self.paginate_queryset(payments)
        if page is not None:
            serializer = MemberPaymentSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = MemberPaymentSerializer(payments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Historique d'adhésion d'un membre."""
        member = self.get_object()
        history = member.membership_history.all().order_by('-start_date')
        
        serializer = MembershipHistorySerializer(history, many=True)
        return Response(serializer.data)


class MemberPaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des paiements des membres.
    """
    queryset = MemberPayment.objects.select_related('member', 'validated_by')
    serializer_class = MemberPaymentSerializer
    permission_classes = [BaseCooperativePermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'member': ['exact'],
        'payment_method': ['exact'],
        'is_validated': ['exact'],
        'payment_date': ['gte', 'lte']
    }
    search_fields = [
        'member__first_name', 'member__last_name', 'member__member_number',
        'reference', 'notes'
    ]
    ordering_fields = ['payment_date', 'amount', 'created_at']
    ordering = ['-payment_date']
    
    def get_permissions(self):
        """Permissions spécifiques par action."""
        if self.action in ['list', 'retrieve']:
            permission_classes = [CanViewMembers]
        elif self.action in ['create', 'update', 'partial_update', 'validate_payment', 'destroy', 'cancel_validation']:
            permission_classes = [CanManageMembers]
        else:
            permission_classes = [BaseCooperativePermission]
        
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """Auto-validation si l'utilisateur a les permissions."""
        # Auto-valider si l'utilisateur peut éditer les membres
        if hasattr(self.request.user, 'cooperativeaccess'):
            access = self.request.user.cooperativeaccess
            if access.can_edit_members:
                serializer.save(
                    is_validated=True,
                    validated_by=self.request.user,
                    validated_at=timezone.now()
                )
            else:
                serializer.save()
        else:
            serializer.save()
    
    @action(detail=True, methods=['post'])
    def validate_payment(self, request, pk=None):
        """Valider un paiement."""
        payment = self.get_object()
        
        if payment.is_validated:
            return Response(
                {'error': 'Ce paiement est déjà validé.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment.is_validated = True
        payment.validated_by = request.user
        payment.validated_at = timezone.now()
        payment.save()
        
        return Response({'message': 'Paiement validé avec succès.'})
    
    @action(detail=True, methods=['post'])
    def cancel_validation(self, request, pk=None):
        """Annuler la validation d'un paiement."""
        payment = self.get_object()
        
        if not payment.is_validated:
            return Response(
                {'error': 'Ce paiement n\'est pas validé.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment.is_validated = False
        payment.validated_by = None
        payment.validated_at = None
        payment.save()
        
        return Response({'message': 'Validation annulée avec succès.'})


class MembershipHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet en lecture seule pour l'historique d'adhésion.
    """
    queryset = MembershipHistory.objects.select_related('member', 'membership_type')
    serializer_class = MembershipHistorySerializer
    permission_classes = [CanViewMembers]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'member': ['exact'],
        'old_type': ['exact'],
        'new_type': ['exact'],
        'change_date': ['gte', 'lte']
    }
    search_fields = [
        'member__first_name', 'member__last_name', 'member__member_number',
        'notes'
    ]
    ordering_fields = ['start_date', 'end_date', 'created_at']
    ordering = ['-start_date']
