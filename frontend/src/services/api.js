import axios from 'axios';
import { API_CONFIG, HTTP_STATUS, STORAGE_KEYS } from '../constants/api';

// Instance Axios principale
const apiClient = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Gestionnaire de tokens JWT
const tokenManager = {
  getAccessToken: () => localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN),
  getRefreshToken: () => localStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN),
  setTokens: (accessToken, refreshToken) => {
    localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, accessToken);
    if (refreshToken) {
      localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, refreshToken);
    }
  },
  clearTokens: () => {
    localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
    localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
    localStorage.removeItem(STORAGE_KEYS.USER_DATA);
  },
};

// Intercepteur de requête - Ajouter le token JWT
apiClient.interceptors.request.use(
  (config) => {
    const token = tokenManager.getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Intercepteur de réponse - Gestion automatique du refresh token
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (
      error.response?.status === HTTP_STATUS.UNAUTHORIZED &&
      !originalRequest._retry
    ) {
      originalRequest._retry = true;

      try {
        const refreshToken = tokenManager.getRefreshToken();
        if (!refreshToken) {
          throw new Error('No refresh token available');
        }

        const refreshResponse = await axios.post(
          `${API_CONFIG.BASE_URL}/api/v1/auth/refresh/`,
          { refresh: refreshToken }
        );

        const { access } = refreshResponse.data;
        tokenManager.setTokens(access);

        // Retry la requête originale avec le nouveau token
        originalRequest.headers.Authorization = `Bearer ${access}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Refresh failed, déconnecter l'utilisateur
        tokenManager.clearTokens();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Service API principal
class ApiService {
  // Méthodes HTTP de base
  async get(url, config = {}) {
    try {
      const response = await apiClient.get(url, config);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async post(url, data = {}, config = {}) {
    try {
      const response = await apiClient.post(url, data, config);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async put(url, data = {}, config = {}) {
    try {
      const response = await apiClient.put(url, data, config);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async patch(url, data = {}, config = {}) {
    try {
      const response = await apiClient.patch(url, data, config);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async delete(url, config = {}) {
    try {
      const response = await apiClient.delete(url, config);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Gestion des erreurs
  handleError(error) {
    if (error.response) {
      // Erreur du serveur avec réponse
      const { status, data } = error.response;
      const errorMessage = data?.detail || data?.message || data?.non_field_errors?.[0] || 'Erreur du serveur';
      const errorObj = new Error(errorMessage);
      errorObj.status = status;
      errorObj.errors = data?.errors || data;
      return errorObj;
    } else if (error.request) {
      // Erreur réseau
      const errorObj = new Error('Erreur de connexion au serveur');
      errorObj.status = 0;
      errorObj.errors = error.message;
      return errorObj;
    } else {
      // Autre erreur
      const errorObj = new Error(error.message || 'Une erreur inattendue s\'est produite');
      errorObj.status = 0;
      errorObj.errors = error;
      return errorObj;
    }
  }

  // Méthodes utilitaires
  setAuthToken(token) {
    tokenManager.setTokens(token);
  }

  clearAuthToken() {
    tokenManager.clearTokens();
  }

  isAuthenticated() {
    return !!tokenManager.getAccessToken();
  }

  // Upload de fichiers
  async uploadFile(url, file, onProgress = null) {
    const formData = new FormData();
    formData.append('file', file);

    const config = {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    };

    if (onProgress) {
      config.onUploadProgress = (progressEvent) => {
        const progress = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        onProgress(progress);
      };
    }

    return this.post(url, formData, config);
  }
}

// Instance singleton
const apiService = new ApiService();

export default apiService;
export { tokenManager };