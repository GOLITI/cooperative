// Service API unifié pour la gestion des ventes
import apiService from './api';
import { API_ENDPOINTS } from '../constants/api';

class SalesService {
  // ===== CLIENTS =====
  
  // Récupérer tous les clients avec pagination et filtres
  async getCustomers(params = {}) {
    try {
      const response = await apiService.get(API_ENDPOINTS.SALES.CUSTOMERS, { params });
      return response;
    } catch (error) {
      console.error('Erreur lors de la récupération des clients:', error);
      throw error;
    }
  }

  // Récupérer un client par ID
  async getCustomerById(id) {
    try {
      const response = await apiService.get(`${API_ENDPOINTS.SALES.CUSTOMERS}${id}/`);
      return response;
    } catch (error) {
      console.error(`Erreur lors de la récupération du client ${id}:`, error);
      throw error;
    }
  }

  // Créer un nouveau client
  async createCustomer(customerData) {
    try {
      const response = await apiService.post(API_ENDPOINTS.SALES.CUSTOMERS, customerData);
      return response;
    } catch (error) {
      console.error('Erreur lors de la création du client:', error);
      throw error;
    }
  }

  // Mettre à jour un client
  async updateCustomer(id, customerData) {
    try {
      const response = await apiService.put(`${API_ENDPOINTS.SALES.CUSTOMERS}${id}/`, customerData);
      return response;
    } catch (error) {
      console.error(`Erreur lors de la mise à jour du client ${id}:`, error);
      throw error;
    }
  }

  // Supprimer un client
  async deleteCustomer(id) {
    try {
      const response = await apiService.delete(`${API_ENDPOINTS.SALES.CUSTOMERS}${id}/`);
      return response;
    } catch (error) {
      console.error(`Erreur lors de la suppression du client ${id}:`, error);
      throw error;
    }
  }

  // ===== VENTES =====
  
  // Récupérer toutes les ventes avec pagination et filtres
  async getSales(params = {}) {
    try {
      const response = await apiService.get(API_ENDPOINTS.SALES.SALES, { params });
      return response;
    } catch (error) {
      console.error('Erreur lors de la récupération des ventes:', error);
      throw error;
    }
  }

  // Récupérer une vente par ID
  async getSaleById(id) {
    try {
      const response = await apiService.get(`${API_ENDPOINTS.SALES.SALES}${id}/`);
      return response;
    } catch (error) {
      console.error(`Erreur lors de la récupération de la vente ${id}:`, error);
      throw error;
    }
  }

  // Créer une nouvelle vente
  async createSale(saleData) {
    try {
      const response = await apiService.post(API_ENDPOINTS.SALES.SALES, saleData);
      return response;
    } catch (error) {
      console.error('Erreur lors de la création de la vente:', error);
      throw error;
    }
  }

  // Mettre à jour une vente
  async updateSale(id, saleData) {
    try {
      const response = await apiService.put(`${API_ENDPOINTS.SALES.SALES}${id}/`, saleData);
      return response;
    } catch (error) {
      console.error(`Erreur lors de la mise à jour de la vente ${id}:`, error);
      throw error;
    }
  }

  // Supprimer une vente
  async deleteSale(id) {
    try {
      const response = await apiService.delete(`${API_ENDPOINTS.SALES.SALES}${id}/`);
      return response;
    } catch (error) {
      console.error(`Erreur lors de la suppression de la vente ${id}:`, error);
      throw error;
    }
  }

  // ===== STATISTIQUES DES VENTES =====
  
  // Récupérer les statistiques des ventes
  async getSalesStatistics() {
    try {
      const response = await apiService.get(`${API_ENDPOINTS.SALES.SALES}statistics/`);
      return response;
    } catch (error) {
      console.error('Erreur lors de la récupération des statistiques de ventes:', error);
      // Retourner des statistiques par défaut en cas d'erreur
      return {
        sales_today: 0,
        monthly_revenue: 0,
        total_customers: 0,
        monthly_sales: 0,
        top_products: [],
        sales_by_status: {}
      };
    }
  }

  // Récupérer le chiffre d'affaires par période
  async getRevenuByPeriod(period = 'month') {
    try {
      const response = await apiService.get(`${API_ENDPOINTS.SALES.SALES}revenue/`, {
        params: { period }
      });
      return response;
    } catch (error) {
      console.error('Erreur lors de la récupération du chiffre d\'affaires:', error);
      throw error;
    }
  }

  // Récupérer les produits les plus vendus
  async getTopSellingProducts(params = {}) {
    try {
      const response = await apiService.get(`${API_ENDPOINTS.SALES.SALES}top-products/`, { params });
      return response;
    } catch (error) {
      console.error('Erreur lors de la récupération des produits les plus vendus:', error);
      throw error;
    }
  }

  // Récupérer les ventes par client
  async getSalesByCustomer(customerId, params = {}) {
    try {
      const response = await apiService.get(`${API_ENDPOINTS.SALES.SALES}by-customer/${customerId}/`, { params });
      return response;
    } catch (error) {
      console.error(`Erreur lors de la récupération des ventes du client ${customerId}:`, error);
      throw error;
    }
  }

  // ===== RECHERCHE ET FILTRES =====
  
  // Rechercher des ventes
  async searchSales(query, filters = {}) {
    try {
      const params = { search: query, ...filters };
      const response = await apiService.get(API_ENDPOINTS.SALES.SALES, { params });
      return response;
    } catch (error) {
      console.error('Erreur lors de la recherche de ventes:', error);
      throw error;
    }
  }

  // Rechercher des clients
  async searchCustomers(query, filters = {}) {
    try {
      const params = { search: query, ...filters };
      const response = await apiService.get(API_ENDPOINTS.SALES.CUSTOMERS, { params });
      return response;
    } catch (error) {
      console.error('Erreur lors de la recherche de clients:', error);
      throw error;
    }
  }

  // ===== UTILITAIRES =====
  
  // Formater le numéro de vente
  formatSaleNumber(saleNumber) {
    return saleNumber || 'N/A';
  }

  // Calculer le montant total d'une vente
  calculateSaleTotal(saleItems) {
    return saleItems.reduce((total, item) => {
      return total + (item.quantity * item.unit_price);
    }, 0);
  }

  // Obtenir le statut coloré
  getStatusColor(status) {
    const colors = {
      'draft': 'default',
      'confirmed': 'primary',
      'delivered': 'success',
      'cancelled': 'error'
    };
    return colors[status] || 'default';
  }

  // ===== RAPPORTS =====
  
  // Exporter les ventes
  async exportSales(format = 'csv', params = {}) {
    try {
      const response = await apiService.get(`${API_ENDPOINTS.SALES.SALES}export/`, {
        params: { format, ...params },
        responseType: 'blob'
      });
      return response;
    } catch (error) {
      console.error('Erreur lors de l\'export des ventes:', error);
      throw error;
    }
  }

  // Générer un rapport de ventes
  async generateSalesReport(reportType, params = {}) {
    try {
      const response = await apiService.get(`${API_ENDPOINTS.SALES.SALES}report/`, {
        params: { type: reportType, ...params }
      });
      return response;
    } catch (error) {
      console.error('Erreur lors de la génération du rapport:', error);
      throw error;
    }
  }
}

// Instance singleton
const salesService = new SalesService();
export { salesService };
export default salesService;