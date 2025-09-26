from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Address, Contact, ActivityLog
from .serializers import AddressSerializer, ContactSerializer, ActivityLogSerializer


class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['city', 'region', 'country']
    search_fields = ['street', 'city', 'region']
    ordering_fields = ['city', 'region', 'created_at']
    ordering = ['-created_at']


class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['phone_primary', 'phone_secondary', 'email']


class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Journal d'activité en lecture seule"""
    queryset = ActivityLog.objects.all()
    serializer_class = ActivityLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'action', 'model_name']
    search_fields = ['user__username', 'action', 'model_name']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['get'])
    def recent_activities(self, request):
        """Récupérer les 50 dernières activités"""
        recent = self.queryset[:50]
        serializer = self.get_serializer(recent, many=True)
        return Response(serializer.data)
