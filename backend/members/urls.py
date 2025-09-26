from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'membership-types', views.MembershipTypeViewSet)
router.register(r'members', views.MemberViewSet)
router.register(r'family-members', views.FamilyMemberViewSet)
router.register(r'membership-fees', views.MembershipFeeViewSet)

app_name = 'members'
urlpatterns = [
    path('', include(router.urls)),
]