"""
URLs API pour l'application members.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    MemberViewSet, MembershipTypeViewSet, MemberPaymentViewSet,
    MembershipHistoryViewSet
)

# Router pour les ViewSets
router = DefaultRouter()
router.register(r'members', MemberViewSet)
router.register(r'membership-types', MembershipTypeViewSet)
router.register(r'payments', MemberPaymentViewSet)
router.register(r'history', MembershipHistoryViewSet)

urlpatterns = [
    # Inclure les routes du router
    path('', include(router.urls)),
]