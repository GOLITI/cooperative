from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

# Import des ViewSets
from core.views import AddressViewSet, ContactViewSet, ActivityLogViewSet
from members.views import MembershipTypeViewSet, MemberViewSet, MembershipFeeViewSet, FamilyMemberViewSet

# Configuration du router
router = DefaultRouter()

# Core endpoints
router.register(r'addresses', AddressViewSet)
router.register(r'contacts', ContactViewSet)
router.register(r'activity-logs', ActivityLogViewSet)

# Members endpoints
router.register(r'membership-types', MembershipTypeViewSet)
router.register(r'members', MemberViewSet)
router.register(r'membership-fees', MembershipFeeViewSet)
router.register(r'family-members', FamilyMemberViewSet)

# TODO: Ajouter les autres modules (inventory, sales, finance, reports)

from django.urls import path
from . import views

app_name = 'api'
urlpatterns = [
    path('auth/login/', views.login_view, name='login'),
    path('auth/register/', views.register_view, name='register'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('auth/refresh/', views.refresh_token_view, name='refresh_token'),
]