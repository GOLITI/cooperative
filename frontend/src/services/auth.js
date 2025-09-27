import apiService, { tokenManager } from './api';
import { API_ENDPOINTS, STORAGE_KEYS } from '../constants/api';

class AuthService {
  // Connexion utilisateur
  async login(credentials) {
    try {
      console.log('AuthService.login - credentials:', credentials);
      const response = await apiService.post(API_ENDPOINTS.AUTH.LOGIN, credentials);
      console.log('AuthService.login - response:', response);
      
      if (response.access) {
        // Sauvegarder les tokens
        tokenManager.setTokens(response.access, response.refresh);
        
        // Sauvegarder les données utilisateur si disponibles
        if (response.user) {
          localStorage.setItem(STORAGE_KEYS.USER_DATA, JSON.stringify(response.user));
        }
        
        console.log('AuthService.login - success, tokens saved');
        return {
          success: true,
          user: response.user,
          tokens: {
            access: response.access,
            refresh: response.refresh,
          },
        };
      }
      
      throw new Error('Tokens manquants dans la réponse');
    } catch (error) {
      console.error('AuthService.login - error:', error);
      return {
        success: false,
        error: error.message || 'Erreur de connexion',
      };
    }
  }

  // Déconnexion utilisateur
  async logout() {
    try {
      // Appeler l'endpoint de déconnexion côté serveur
      await apiService.post(API_ENDPOINTS.AUTH.LOGOUT);
    } catch (error) {
      console.warn('Erreur lors de la déconnexion côté serveur:', error);
    } finally {
      // Nettoyer le stockage local dans tous les cas
      tokenManager.clearTokens();
    }
  }

  // Actualiser le token
  async refreshToken() {
    try {
      const refreshToken = tokenManager.getRefreshToken();
      if (!refreshToken) {
        throw new Error('Aucun token de rafraîchissement disponible');
      }

      const response = await apiService.post(API_ENDPOINTS.AUTH.REFRESH, {
        refresh: refreshToken,
      });

      if (response.access) {
        tokenManager.setTokens(response.access);
        return response.access;
      }

      throw new Error('Token d\'accès manquant dans la réponse');
    } catch (error) {
      // En cas d'erreur, déconnecter l'utilisateur
      this.logout();
      throw error;
    }
  }

  // Vérifier si l'utilisateur est connecté
  isAuthenticated() {
    return apiService.isAuthenticated();
  }

  // Obtenir les données utilisateur stockées
  getCurrentUser() {
    try {
      const userData = localStorage.getItem(STORAGE_KEYS.USER_DATA);
      return userData ? JSON.parse(userData) : null;
    } catch (error) {
      console.error('Erreur lors de la lecture des données utilisateur:', error);
      return null;
    }
  }

  // Obtenir le profil utilisateur depuis l'API
  async getUserProfile() {
    try {
      // Endpoint à ajuster selon votre API
      const response = await apiService.get('/api/v1/auth/profile/');
      
      // Mettre à jour les données utilisateur locales
      localStorage.setItem(STORAGE_KEYS.USER_DATA, JSON.stringify(response));
      
      return response;
    } catch (error) {
      console.error('Erreur lors de la récupération du profil:', error);
      throw error;
    }
  }

  // Mettre à jour le profil utilisateur
  async updateProfile(profileData) {
    try {
      const response = await apiService.patch('/api/v1/auth/profile/', profileData);
      
      // Mettre à jour les données utilisateur locales
      localStorage.setItem(STORAGE_KEYS.USER_DATA, JSON.stringify(response));
      
      return response;
    } catch (error) {
      console.error('Erreur lors de la mise à jour du profil:', error);
      throw error;
    }
  }

  // Changer le mot de passe
  async changePassword(passwordData) {
    try {
      return await apiService.post('/api/v1/auth/change-password/', passwordData);
    } catch (error) {
      console.error('Erreur lors du changement de mot de passe:', error);
      throw error;
    }
  }

  // Inscription (si applicable)
  async register(userData) {
    try {
      const response = await apiService.post('/api/v1/auth/register/', userData);
      
      if (response.access) {
        tokenManager.setTokens(response.access, response.refresh);
        if (response.user) {
          localStorage.setItem(STORAGE_KEYS.USER_DATA, JSON.stringify(response.user));
        }
      }
      
      return response;
    } catch (error) {
      console.error('Erreur lors de l\'inscription:', error);
      throw error;
    }
  }

  // Vérification de l'état de connexion au démarrage
  async checkAuthState() {
    if (!this.isAuthenticated()) {
      return false;
    }

    try {
      // Vérifier si le token est encore valide en récupérant le profil
      await this.getUserProfile();
      return true;
    } catch (error) {
      // Token invalide, déconnecter
      this.logout();
      return false;
    }
  }
}

// Instance singleton
const authService = new AuthService();

export default authService;