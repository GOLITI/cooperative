// Service API pour la gestion des ventes
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

// Service des ventes
export const salesService = {
  // ========== CLIENTS ==========
  
  // Récupérer tous les clients
  getCustomers: async (params = {}) => {
    try {
      const response = await api.get(API_ENDPOINTS.SALES.CUSTOMERS, { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Créer un client
  createCustomer: async (customerData) => {
    try {
      const response = await api.post(API_ENDPOINTS.SALES.CUSTOMERS, customerData);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Mettre à jour un client
  updateCustomer: async (id, customerData) => {
    try {
      const response = await api.put(`${API_ENDPOINTS.SALES.CUSTOMERS}${id}/`, customerData);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Supprimer un client
  deleteCustomer: async (id) => {
    try {
      await api.delete(`${API_ENDPOINTS.SALES.CUSTOMERS}${id}/`);
      return true;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // ========== VENTES ==========

  // Récupérer toutes les ventes
  getSales: async (params = {}) => {
    try {
      const response = await api.get(API_ENDPOINTS.SALES.SALES, { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Récupérer une vente par ID
  getSale: async (id) => {
    try {
      const response = await api.get(`${API_ENDPOINTS.SALES.SALES}${id}/`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Créer une nouvelle vente
  createSale: async (saleData) => {
    try {
      const response = await api.post(API_ENDPOINTS.SALES.SALES, saleData);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Mettre à jour une vente
  updateSale: async (id, saleData) => {
    try {
      const response = await api.put(`${API_ENDPOINTS.SALES.SALES}${id}/`, saleData);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Supprimer une vente
  deleteSale: async (id) => {
    try {
      await api.delete(`${API_ENDPOINTS.SALES.SALES}${id}/`);
      return true;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // ========== STATISTIQUES ET RAPPORTS ==========

  // Récupérer les statistiques des ventes
  getSalesStatistics: async (params = {}) => {
    try {
      const response = await api.get(`${API_ENDPOINTS.SALES.SALES}statistics/`, { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Récupérer le chiffre d'affaires
  getRevenue: async (params = {}) => {
    try {
      const response = await api.get(`${API_ENDPOINTS.SALES.SALES}revenue/`, { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Récupérer les ventes par période
  getSalesByPeriod: async (params = {}) => {
    try {
      const response = await api.get(`${API_ENDPOINTS.SALES.SALES}by_period/`, { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Récupérer les top produits vendus
  getTopProducts: async (params = {}) => {
    try {
      const response = await api.get(`${API_ENDPOINTS.SALES.SALES}top_products/`, { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // ========== FONCTIONS UTILITAIRES ==========

  // Rechercher des ventes
  searchSales: async (query) => {
    try {
      const response = await api.get(API_ENDPOINTS.SALES.SALES, {
        params: { search: query }
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Rechercher des clients
  searchCustomers: async (query) => {
    try {
      const response = await api.get(API_ENDPOINTS.SALES.CUSTOMERS, {
        params: { search: query }
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Calculer le total d'une vente
  calculateSaleTotal: (saleItems) => {
    if (!Array.isArray(saleItems)) return 0;
    
    return saleItems.reduce((total, item) => {
      const itemTotal = (item.quantity || 0) * (item.unit_price || 0);
      return total + itemTotal;
    }, 0);
  },

  // Formater le numéro de vente
  formatSaleNumber: (saleNumber) => {
    return saleNumber ? `V${saleNumber.toString().padStart(6, '0')}` : '';
  },

  // Vérifier si une vente peut être modifiée
  canEditSale: (sale) => {
    if (!sale) return false;
    return sale.status === 'draft' || sale.status === 'pending';
  },

  // Vérifier si une vente peut être supprimée
  canDeleteSale: (sale) => {
    if (!sale) return false;
    return sale.status === 'draft';
  }
};

export default salesService;