// Service API pour la gestion de l'inventaire
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

// Service de l'inventaire
export const inventoryService = {
  // ========== CATÉGORIES ==========
  
  // Récupérer toutes les catégories
  getCategories: async (params = {}) => {
    try {
      const response = await api.get(API_ENDPOINTS.INVENTORY.CATEGORIES, { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Créer une catégorie
  createCategory: async (categoryData) => {
    try {
      const response = await api.post(API_ENDPOINTS.INVENTORY.CATEGORIES, categoryData);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Mettre à jour une catégorie
  updateCategory: async (id, categoryData) => {
    try {
      const response = await api.put(`${API_ENDPOINTS.INVENTORY.CATEGORIES}${id}/`, categoryData);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Supprimer une catégorie
  deleteCategory: async (id) => {
    try {
      await api.delete(`${API_ENDPOINTS.INVENTORY.CATEGORIES}${id}/`);
      return true;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // ========== UNITÉS DE MESURE ==========

  // Récupérer toutes les unités
  getUnits: async () => {
    try {
      const response = await api.get(API_ENDPOINTS.INVENTORY.UNITS);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Créer une unité
  createUnit: async (unitData) => {
    try {
      const response = await api.post(API_ENDPOINTS.INVENTORY.UNITS, unitData);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // ========== PRODUITS ==========

  // Récupérer tous les produits
  getProducts: async (params = {}) => {
    try {
      const response = await api.get(API_ENDPOINTS.INVENTORY.PRODUCTS, { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Récupérer un produit par ID
  getProduct: async (id) => {
    try {
      const response = await api.get(`${API_ENDPOINTS.INVENTORY.PRODUCTS}${id}/`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Créer un nouveau produit
  createProduct: async (productData) => {
    try {
      const response = await api.post(API_ENDPOINTS.INVENTORY.PRODUCTS, productData);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Mettre à jour un produit
  updateProduct: async (id, productData) => {
    try {
      const response = await api.put(`${API_ENDPOINTS.INVENTORY.PRODUCTS}${id}/`, productData);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Supprimer un produit
  deleteProduct: async (id) => {
    try {
      await api.delete(`${API_ENDPOINTS.INVENTORY.PRODUCTS}${id}/`);
      return true;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // ========== MOUVEMENTS DE STOCK ==========

  // Récupérer les mouvements de stock
  getStockMovements: async (params = {}) => {
    try {
      const response = await api.get(API_ENDPOINTS.INVENTORY.STOCK_MOVEMENTS, { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Créer un mouvement de stock
  createStockMovement: async (movementData) => {
    try {
      const response = await api.post(API_ENDPOINTS.INVENTORY.STOCK_MOVEMENTS, movementData);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // ========== INVENTAIRES ==========

  // Récupérer les inventaires
  getInventories: async (params = {}) => {
    try {
      const response = await api.get(API_ENDPOINTS.INVENTORY.INVENTORIES, { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Créer un inventaire
  createInventory: async (inventoryData) => {
    try {
      const response = await api.post(API_ENDPOINTS.INVENTORY.INVENTORIES, inventoryData);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // ========== STATISTIQUES ET RAPPORTS ==========

  // Récupérer les statistiques de l'inventaire
  getInventoryStatistics: async () => {
    try {
      const response = await api.get(`${API_ENDPOINTS.INVENTORY.PRODUCTS}statistics/`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Récupérer les produits en rupture de stock
  getOutOfStockProducts: async () => {
    try {
      const response = await api.get(`${API_ENDPOINTS.INVENTORY.PRODUCTS}out_of_stock/`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Récupérer les produits avec stock faible
  getLowStockProducts: async () => {
    try {
      const response = await api.get(`${API_ENDPOINTS.INVENTORY.PRODUCTS}low_stock/`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Rechercher des produits
  searchProducts: async (query) => {
    try {
      const response = await api.get(API_ENDPOINTS.INVENTORY.PRODUCTS, {
        params: { search: query }
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  }
};

export default inventoryService;