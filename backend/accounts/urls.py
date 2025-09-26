"""
URLs pour l'API d'authentification.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router pour les ViewSets
router = DefaultRouter()
router.register(r'profiles', views.UserProfileViewSet, basename='userprofile')
router.register(r'roles', views.UserRoleViewSet, basename='userrole')
router.register(r'sessions', views.SessionActivityViewSet, basename='sessionactivity')
router.register(r'users', views.UserManagementViewSet, basename='usermanagement')

app_name = 'accounts'

urlpatterns = [
    # Authentification
    path('login/', views.LoginAPIView.as_view(), name='login'),
    path('logout/', views.LogoutAPIView.as_view(), name='logout'),
    path('register/', views.RegisterAPIView.as_view(), name='register'),
    
    # Gestion du profil
    path('me/', views.current_user, name='current-user'),
    path('permissions/', views.user_permissions, name='user-permissions'),
    path('change-password/', views.ChangePasswordAPIView.as_view(), name='change-password'),
    
    # Inclure les routes du router
    path('', include(router.urls)),
]