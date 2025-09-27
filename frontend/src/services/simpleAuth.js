import { API_CONFIG, API_ENDPOINTS, STORAGE_KEYS } from '../constants/api';

class SimpleAuthService {
  async login(credentials) {
    try {
      console.log('SimpleAuthService: Tentative de connexion', credentials);
      
      const url = `${API_CONFIG.BASE_URL}${API_ENDPOINTS.AUTH.LOGIN}`;
      console.log('SimpleAuthService: URL complète', url);
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });
      
      console.log('SimpleAuthService: Statut de réponse', response.status);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const errorMessage = errorData.detail || errorData.message || `Erreur ${response.status}`;
        console.log('SimpleAuthService: Erreur', errorMessage);
        return {
          success: false,
          error: errorMessage,
        };
      }
      
      const data = await response.json();
      console.log('SimpleAuthService: Données reçues', data);
      
      if (data.access) {
        // Sauvegarder les tokens
        localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, data.access);
        if (data.refresh) {
          localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, data.refresh);
        }
        
        // Sauvegarder les données utilisateur
        if (data.user) {
          localStorage.setItem(STORAGE_KEYS.USER_DATA, JSON.stringify(data.user));
        }
        
        console.log('SimpleAuthService: Connexion réussie');
        return {
          success: true,
          user: data.user,
          tokens: {
            access: data.access,
            refresh: data.refresh,
          },
        };
      }
      
      return {
        success: false,
        error: 'Tokens manquants dans la réponse',
      };
      
    } catch (error) {
      console.error('SimpleAuthService: Erreur réseau', error);
      return {
        success: false,
        error: error.message || 'Erreur de connexion',
      };
    }
  }

  // Vérifier l'état d'authentification
  async checkAuthState() {
    const token = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
    return !!token;
  }

  // Récupérer l'utilisateur actuel
  getCurrentUser() {
    const userData = localStorage.getItem(STORAGE_KEYS.USER_DATA);
    return userData ? JSON.parse(userData) : null;
  }

  // Déconnexion
  async logout() {
    localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
    localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
    localStorage.removeItem(STORAGE_KEYS.USER_DATA);
  }
}

const simpleAuthService = new SimpleAuthService();
export default simpleAuthService;