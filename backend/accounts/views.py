"""
Vues API pour l'authentification et gestion des utilisateurs.
"""
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.gis.geoip2 import GeoIP2
from django.conf import settings
import logging

from .models import UserProfile, UserRole, SessionActivity, LoginAttempt, CooperativeAccess
from .serializers import (
    LoginSerializer, RegisterSerializer, UserSerializer, UserProfileSerializer,
    ChangePasswordSerializer, UpdateProfileSerializer, UserRoleSerializer,
    SessionActivitySerializer
)
from .permissions import IsOwnerOrReadOnly, CanManageUsers


logger = logging.getLogger(__name__)


class LoginAPIView(APIView):
    """
    API de connexion utilisateur.
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Connecter un utilisateur."""
        serializer = LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            remember_me = serializer.validated_data.get('remember_me', False)
            
            # Connexion de l'utilisateur
            login(request, user)
            
            # Configuration de la session
            if remember_me:
                request.session.set_expiry(settings.SESSION_COOKIE_AGE)
            else:
                request.session.set_expiry(0)  # Expire à la fermeture du navigateur
            
            # Enregistrer la tentative de connexion
            self._log_login_attempt(request, user, success=True)
            
            # Créer ou récupérer l'activité de session
            self._create_session_activity(request, user)
            
            # Mettre à jour le profil
            if hasattr(user, 'profile'):
                profile = user.profile
                profile.last_login_ip = self._get_client_ip(request)
                profile.login_count += 1
                profile.save()
            
            # Créer ou récupérer le token
            token, created = Token.objects.get_or_create(user=user)
            
            # Sérialiser les données utilisateur
            user_serializer = UserSerializer(user)
            
            return Response({
                'message': 'Connexion réussie',
                'user': user_serializer.data,
                'token': token.key,
                'session_id': request.session.session_key
            }, status=status.HTTP_200_OK)
        
        else:
            # Enregistrer l'échec de connexion
            username = request.data.get('username', '')
            self._log_login_attempt(request, None, success=False, username=username)
            
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _get_client_ip(self, request):
        """Obtenir l'IP du client."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _log_login_attempt(self, request, user, success=True, username=''):
        """Enregistrer la tentative de connexion."""
        try:
            LoginAttempt.objects.create(
                user=user,
                username=username or (user.username if user else ''),
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                success=success,
                failure_reason='' if success else 'Invalid credentials'
            )
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement de la tentative de connexion: {e}")
    
    def _create_session_activity(self, request, user):
        """Créer l'activité de session."""
        try:
            ip_address = self._get_client_ip(request)
            
            # Géolocalisation (optionnel)
            country, city = '', ''
            try:
                g = GeoIP2()
                location = g.city(ip_address)
                country = location.get('country_name', '')
                city = location.get('city', '')
            except:
                pass
            
            SessionActivity.objects.create(
                user=user,
                session_key=request.session.session_key,
                ip_address=ip_address,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                country=country,
                city=city,
                login_time=timezone.now(),
                is_active=True
            )
        except Exception as e:
            logger.error(f"Erreur lors de la création de l'activité de session: {e}")


class LogoutAPIView(APIView):
    """
    API de déconnexion utilisateur.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Déconnecter un utilisateur."""
        try:
            # Marquer la session comme terminée
            if hasattr(request, 'session') and request.session.session_key:
                SessionActivity.objects.filter(
                    user=request.user,
                    session_key=request.session.session_key,
                    is_active=True
                ).update(
                    logout_time=timezone.now(),
                    is_active=False
                )
            
            # Supprimer le token d'authentification
            try:
                token = Token.objects.get(user=request.user)
                token.delete()
            except Token.DoesNotExist:
                pass
            
            # Déconnexion
            logout(request)
            
            return Response({
                'message': 'Déconnexion réussie'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Erreur lors de la déconnexion: {e}")
            return Response({
                'error': 'Erreur lors de la déconnexion'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RegisterAPIView(APIView):
    """
    API d'inscription utilisateur.
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Inscrire un nouvel utilisateur."""
        serializer = RegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            # Créer le token
            token, created = Token.objects.get_or_create(user=user)
            
            # Sérialiser les données utilisateur
            user_serializer = UserSerializer(user)
            
            return Response({
                'message': 'Inscription réussie',
                'user': user_serializer.data,
                'token': token.key
            }, status=status.HTTP_201_CREATED)
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class UserProfileViewSet(ModelViewSet):
    """
    ViewSet pour les profils utilisateurs.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        """Filtrer selon les permissions."""
        user = self.request.user
        
        # Les administrateurs peuvent voir tous les profils
        if user.is_superuser or (
            hasattr(user, 'cooperative_access') and 
            user.cooperative_access.can_manage_users
        ):
            return UserProfile.objects.select_related('user', 'role', 'member').all()
        
        # Les autres utilisateurs ne voient que leur profil
        return UserProfile.objects.filter(user=user)
    
    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        """Gérer le profil de l'utilisateur connecté."""
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            return Response(
                {'error': 'Profil non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if request.method == 'GET':
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data)
        
        elif request.method in ['PUT', 'PATCH']:
            serializer = UpdateProfileSerializer(
                profile, 
                data=request.data, 
                partial=(request.method == 'PATCH')
            )
            if serializer.is_valid():
                serializer.save()
                return Response(UserProfileSerializer(profile).data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordAPIView(APIView):
    """
    API pour changer le mot de passe.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Changer le mot de passe."""
        serializer = ChangePasswordSerializer(
            data=request.data, 
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            
            # Mettre à jour la date de changement de mot de passe
            if hasattr(request.user, 'profile'):
                profile = request.user.profile
                profile.last_password_change = timezone.now()
                profile.save()
            
            return Response({
                'message': 'Mot de passe changé avec succès'
            }, status=status.HTTP_200_OK)
        
        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST
        )


class UserRoleViewSet(ReadOnlyModelViewSet):
    """
    ViewSet pour les rôles utilisateurs (lecture seule).
    """
    queryset = UserRole.objects.filter(is_active=True).order_by('priority')
    serializer_class = UserRoleSerializer
    permission_classes = [permissions.IsAuthenticated]


class SessionActivityViewSet(ReadOnlyModelViewSet):
    """
    ViewSet pour l'activité de session (lecture seule).
    """
    serializer_class = SessionActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtrer selon les permissions."""
        user = self.request.user
        
        # Les administrateurs peuvent voir toutes les sessions
        if user.is_superuser or (
            hasattr(user, 'cooperative_access') and 
            user.cooperative_access.can_view_logs
        ):
            return SessionActivity.objects.select_related('user').order_by('-login_time')
        
        # Les autres utilisateurs ne voient que leurs sessions
        return SessionActivity.objects.filter(user=user).order_by('-login_time')


class UserManagementViewSet(ModelViewSet):
    """
    ViewSet pour la gestion des utilisateurs (admin seulement).
    """
    queryset = User.objects.select_related('profile', 'profile__role').all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageUsers]
    
    def get_queryset(self):
        """Personnaliser le queryset selon les filtres."""
        queryset = super().get_queryset()
        
        # Filtres optionnels
        role = self.request.query_params.get('role', None)
        is_active = self.request.query_params.get('is_active', None)
        
        if role:
            queryset = queryset.filter(profile__role__name=role)
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('-date_joined')


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def current_user(request):
    """
    Obtenir les informations de l'utilisateur connecté.
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_permissions(request):
    """
    Obtenir les permissions de l'utilisateur connecté.
    """
    try:
        access = request.user.cooperative_access
        permissions_data = {
            # Permissions générales
            'can_view_dashboard': access.can_view_dashboard,
            'can_manage_own_profile': access.can_manage_own_profile,
            
            # Gestion des membres
            'can_view_members': access.can_view_members,
            'can_add_members': access.can_add_members,
            'can_edit_members': access.can_edit_members,
            'can_delete_members': access.can_delete_members,
            
            # Gestion de l'inventaire
            'can_view_inventory': access.can_view_inventory,
            'can_add_products': access.can_add_products,
            'can_edit_products': access.can_edit_products,
            'can_delete_products': access.can_delete_products,
            'can_manage_stock': access.can_manage_stock,
            
            # Gestion des ventes
            'can_view_sales': access.can_view_sales,
            'can_create_sales': access.can_create_sales,
            'can_edit_sales': access.can_edit_sales,
            'can_delete_sales': access.can_delete_sales,
            'can_process_payments': access.can_process_payments,
            
            # Gestion financière
            'can_view_finances': access.can_view_finances,
            'can_create_transactions': access.can_create_transactions,
            'can_validate_transactions': access.can_validate_transactions,
            'can_manage_accounts': access.can_manage_accounts,
            'can_manage_loans': access.can_manage_loans,
            
            # Rapports et administration
            'can_view_basic_reports': access.can_view_basic_reports,
            'can_view_financial_reports': access.can_view_financial_reports,
            'can_export_data': access.can_export_data,
            'can_manage_users': access.can_manage_users,
            'can_manage_permissions': access.can_manage_permissions,
            'can_view_logs': access.can_view_logs,
            'can_backup_data': access.can_backup_data,
        }
        
        return Response({
            'user_id': request.user.id,
            'username': request.user.username,
            'role': request.user.profile.role.name if hasattr(request.user, 'profile') and request.user.profile.role else None,
            'permissions': permissions_data
        })
        
    except CooperativeAccess.DoesNotExist:
        return Response({
            'error': 'Accès coopérative non configuré'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': f'Erreur lors de la récupération des permissions: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
