// Service API pour la gestion des membres
import axios from 'axios';
import { API_CONFIG, API_ENDPOINTS } from '../constants/api';

const api = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
});

// Intercepteur pour ajouter le token JWT
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Intercepteur pour gérer le renouvellement du token
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      const refreshToken = localStorage.getItem('refreshToken');
      if (refreshToken) {
        try {
          const response = await axios.post(
            `${API_CONFIG.BASE_URL}${API_ENDPOINTS.AUTH.REFRESH}`,
            { refresh: refreshToken }
          );
          
          const { access } = response.data;
          localStorage.setItem('accessToken', access);
          originalRequest.headers.Authorization = `Bearer ${access}`;
          
          return api(originalRequest);
        } catch (refreshError) {
          localStorage.removeItem('accessToken');
          localStorage.removeItem('refreshToken');
          window.location.href = '/login';
        }
      }
    }
    
    return Promise.reject(error);
  }
);

// Service des membres
export const membersService = {
  // Récupérer tous les membres
  getMembers: async (params = {}) => {
    try {
      const response = await api.get(API_ENDPOINTS.MEMBERS.MEMBERS, { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Récupérer un membre par ID
  getMember: async (id) => {
    try {
      const response = await api.get(`${API_ENDPOINTS.MEMBERS.MEMBERS}${id}/`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Créer un nouveau membre
  createMember: async (memberData) => {
    try {
      const response = await api.post(API_ENDPOINTS.MEMBERS.MEMBERS, memberData);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Mettre à jour un membre
  updateMember: async (id, memberData) => {
    try {
      const response = await api.put(`${API_ENDPOINTS.MEMBERS.MEMBERS}${id}/`, memberData);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Supprimer un membre
  deleteMember: async (id) => {
    try {
      await api.delete(`${API_ENDPOINTS.MEMBERS.MEMBERS}${id}/`);
      return true;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Récupérer les statistiques des membres
  getMembersStatistics: async () => {
    try {
      const response = await api.get(`${API_ENDPOINTS.MEMBERS.MEMBERS}statistics/`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Récupérer les types d'adhésion
  getMembershipTypes: async () => {
    try {
      const response = await api.get(`${API_CONFIG.BASE_URL}/api/v1/members/membership-types/`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Rechercher des membres
  searchMembers: async (query) => {
    try {
      const response = await api.get(API_ENDPOINTS.MEMBERS.MEMBERS, {
        params: { search: query }
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  }
};

export default membersService;