// Service API unifié pour la gestion de l'inventaire
import apiService from './api';
import { API_ENDPOINTS } from '../constants/api';

class InventoryService {
  // ===== PRODUITS =====
  
  // Récupérer tous les produits avec pagination et filtres
  async getProducts(params = {}) {
    try {
      const response = await apiService.get(API_ENDPOINTS.INVENTORY.PRODUCTS, { params });
      return response;
    } catch (error) {
      console.error('Erreur lors de la récupération des produits:', error);
      throw error;
    }
  }

  // Récupérer un produit par ID
  async getProductById(id) {
    try {
      const response = await apiService.get(`${API_ENDPOINTS.INVENTORY.PRODUCTS}${id}/`);
      return response;
    } catch (error) {
      console.error(`Erreur lors de la récupération du produit ${id}:`, error);
      throw error;
    }
  }

  // Créer un nouveau produit
  async createProduct(productData) {
    try {
      const response = await apiService.post(API_ENDPOINTS.INVENTORY.PRODUCTS, productData);
      return response;
    } catch (error) {
      console.error('Erreur lors de la création du produit:', error);
      throw error;
    }
  }

  // Mettre à jour un produit
  async updateProduct(id, productData) {
    try {
      const response = await apiService.put(`${API_ENDPOINTS.INVENTORY.PRODUCTS}${id}/`, productData);
      return response;
    } catch (error) {
      console.error(`Erreur lors de la mise à jour du produit ${id}:`, error);
      throw error;
    }
  }

  // Supprimer un produit
  async deleteProduct(id) {
    try {
      const response = await apiService.delete(`${API_ENDPOINTS.INVENTORY.PRODUCTS}${id}/`);
      return response;
    } catch (error) {
      console.error(`Erreur lors de la suppression du produit ${id}:`, error);
      throw error;
    }
  }

  // ===== CATÉGORIES =====
  
  // Récupérer toutes les catégories
  async getCategories(params = {}) {
    try {
      const response = await apiService.get(API_ENDPOINTS.INVENTORY.CATEGORIES, { params });
      return response;
    } catch (error) {
      console.error('Erreur lors de la récupération des catégories:', error);
      throw error;
    }
  }

  // Créer une nouvelle catégorie
  async createCategory(categoryData) {
    try {
      const response = await apiService.post(API_ENDPOINTS.INVENTORY.CATEGORIES, categoryData);
      return response;
    } catch (error) {
      console.error('Erreur lors de la création de la catégorie:', error);
      throw error;
    }
  }

  // Mettre à jour une catégorie
  async updateCategory(id, categoryData) {
    try {
      const response = await apiService.put(`${API_ENDPOINTS.INVENTORY.CATEGORIES}${id}/`, categoryData);
      return response;
    } catch (error) {
      console.error(`Erreur lors de la mise à jour de la catégorie ${id}:`, error);
      throw error;
    }
  }

  // Supprimer une catégorie
  async deleteCategory(id) {
    try {
      const response = await apiService.delete(`${API_ENDPOINTS.INVENTORY.CATEGORIES}${id}/`);
      return response;
    } catch (error) {
      console.error(`Erreur lors de la suppression de la catégorie ${id}:`, error);
      throw error;
    }
  }

  // ===== UNITÉS =====
  
  // Récupérer toutes les unités
  async getUnits(params = {}) {
    try {
      const response = await apiService.get(API_ENDPOINTS.INVENTORY.UNITS, { params });
      return response;
    } catch (error) {
      console.error('Erreur lors de la récupération des unités:', error);
      throw error;
    }
  }

  // Créer une nouvelle unité
  async createUnit(unitData) {
    try {
      const response = await apiService.post(API_ENDPOINTS.INVENTORY.UNITS, unitData);
      return response;
    } catch (error) {
      console.error('Erreur lors de la création de l\'unité:', error);
      throw error;
    }
  }

  // ===== MOUVEMENTS DE STOCK =====
  
  // Récupérer les mouvements de stock
  async getStockMovements(params = {}) {
    try {
      const response = await apiService.get(API_ENDPOINTS.INVENTORY.STOCK_MOVEMENTS, { params });
      return response;
    } catch (error) {
      console.error('Erreur lors de la récupération des mouvements de stock:', error);
      throw error;
    }
  }

  // Créer un mouvement de stock
  async createStockMovement(movementData) {
    try {
      const response = await apiService.post(API_ENDPOINTS.INVENTORY.STOCK_MOVEMENTS, movementData);
      return response;
    } catch (error) {
      console.error('Erreur lors de la création du mouvement de stock:', error);
      throw error;
    }
  }

  // ===== STATISTIQUES ET RAPPORTS =====
  
  // Récupérer les statistiques de l'inventaire
  async getInventoryStatistics() {
    try {
      const response = await apiService.get(`${API_ENDPOINTS.INVENTORY.PRODUCTS}statistics/`);
      return response;
    } catch (error) {
      console.error('Erreur lors de la récupération des statistiques:', error);
      // Retourner des statistiques par défaut en cas d'erreur
      return {
        total_products: 0,
        low_stock_products: 0,
        out_of_stock_products: 0,
        total_categories: 0,
        total_stock_value: 0
      };
    }
  }

  // Récupérer les produits en rupture de stock
  async getLowStockProducts() {
    try {
      const response = await apiService.get(`${API_ENDPOINTS.INVENTORY.PRODUCTS}low-stock/`);
      return response;
    } catch (error) {
      console.error('Erreur lors de la récupération des produits en rupture:', error);
      throw error;
    }
  }

  // Récupérer les produits les plus vendus
  async getTopSellingProducts(params = {}) {
    try {
      const response = await apiService.get(`${API_ENDPOINTS.INVENTORY.PRODUCTS}top-selling/`, { params });
      return response;
    } catch (error) {
      console.error('Erreur lors de la récupération des produits les plus vendus:', error);
      throw error;
    }
  }

  // ===== RECHERCHE ET FILTRES =====
  
  // Rechercher des produits
  async searchProducts(query, filters = {}) {
    try {
      const params = { search: query, ...filters };
      const response = await apiService.get(API_ENDPOINTS.INVENTORY.PRODUCTS, { params });
      return response;
    } catch (error) {
      console.error('Erreur lors de la recherche de produits:', error);
      throw error;
    }
  }

  // ===== IMPORT/EXPORT =====
  
  // Exporter la liste des produits
  async exportProducts(format = 'csv') {
    try {
      const response = await apiService.get(`${API_ENDPOINTS.INVENTORY.PRODUCTS}export/`, {
        params: { format },
        responseType: 'blob'
      });
      return response;
    } catch (error) {
      console.error('Erreur lors de l\'export des produits:', error);
      throw error;
    }
  }

  // Importer des produits depuis un fichier
  async importProducts(file) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await apiService.post(`${API_ENDPOINTS.INVENTORY.PRODUCTS}import/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response;
    } catch (error) {
      console.error('Erreur lors de l\'import des produits:', error);
      throw error;
    }
  }
}

// Instance singleton
const inventoryService = new InventoryService();
export { inventoryService };
export default inventoryService;