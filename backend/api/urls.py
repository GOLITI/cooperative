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

urlpatterns = [
    # API endpoints
    path('v1/', include(router.urls)),
    
    # JWT Authentication
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # API Documentation
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]