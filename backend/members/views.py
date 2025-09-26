from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count
from .models import MembershipType, Member, MembershipFee, FamilyMember
from .serializers import (
    MembershipTypeSerializer, MemberListSerializer, MemberDetailSerializer, 
    MemberCreateSerializer, MembershipFeeSerializer, FamilyMemberSerializer
)


class MembershipTypeViewSet(viewsets.ModelViewSet):
    queryset = MembershipType.objects.filter(is_active=True)
    serializer_class = MembershipTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering = ['name']


class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.filter(is_active=True).select_related('user', 'membership_type', 'address', 'contact')
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['membership_type', 'status', 'gender']
    search_fields = ['membership_number', 'user__first_name', 'user__last_name', 'user__email']
    ordering_fields = ['membership_number', 'join_date', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return MemberListSerializer
        elif self.action == 'create':
            return MemberCreateSerializer
        else:
            return MemberDetailSerializer
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Statistiques des membres"""
        stats = {
            'total_members': self.queryset.count(),
            'active_members': self.queryset.filter(status='active').count(),
            'new_members_this_month': self.queryset.filter(
                join_date__year=2025, join_date__month=9
            ).count(),
            'members_by_type': list(
                self.queryset.values('membership_type__name')
                .annotate(count=Count('id'))
                .order_by('membership_type__name')
            )
        }
        return Response(stats)
    
    @action(detail=True, methods=['get'])
    def fees_history(self, request, pk=None):
        """Historique des cotisations d'un membre"""
        member = self.get_object()
        fees = MembershipFee.objects.filter(member=member).order_by('-period_year', '-period_month')
        serializer = MembershipFeeSerializer(fees, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def pay_fee(self, request, pk=None):
        """Enregistrer le paiement d'une cotisation"""
        member = self.get_object()
        serializer = MembershipFeeSerializer(data=request.data)
        if serializer.is_valid():
            # Générer automatiquement le numéro de reçu
            import uuid
            receipt_number = f"FEE{uuid.uuid4().hex[:8].upper()}"
            serializer.save(member=member, receipt_number=receipt_number)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MembershipFeeViewSet(viewsets.ModelViewSet):
    queryset = MembershipFee.objects.all()
    serializer_class = MembershipFeeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['member', 'period_year', 'period_month', 'payment_method']
    ordering = ['-period_year', '-period_month']


class FamilyMemberViewSet(viewsets.ModelViewSet):
    queryset = FamilyMember.objects.all()
    serializer_class = FamilyMemberSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['member', 'relationship']
    search_fields = ['name']
