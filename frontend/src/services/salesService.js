// Service API unifié pour la gestion des ventes
import apiService from './api';
import { API_ENDPOINTS } from '../constants/api';

class SalesService {
  // === Gestion des clients ===
  
  async getCustomers(params = {}) {
    try {
      const queryString = new URLSearchParams(params).toString();
      const url = queryString ? `${API_ENDPOINTS.SALES.CUSTOMERS}?${queryString}` : API_ENDPOINTS.SALES.CUSTOMERS;
      return await apiService.get(url);
    } catch (error) {
      throw new Error(error.message || 'Erreur lors de la récupération des clients');
    }
  }

  async getCustomer(id) {
    try {
      return await apiService.get(`${API_ENDPOINTS.SALES.CUSTOMERS}${id}/`);
    } catch (error) {
      throw new Error(error.message || 'Erreur lors de la récupération du client');
    }
  }

  async createCustomer(customerData) {
    try {
      return await apiService.post(API_ENDPOINTS.SALES.CUSTOMERS, customerData);
    } catch (error) {
      throw new Error(error.message || 'Erreur lors de la création du client');
    }
  }

  async updateCustomer(id, customerData) {
    try {
      return await apiService.put(`${API_ENDPOINTS.SALES.CUSTOMERS}${id}/`, customerData);
    } catch (error) {
      throw new Error(error.message || 'Erreur lors de la mise à jour du client');
    }
  }

  async deleteCustomer(id) {
    try {
      return await apiService.delete(`${API_ENDPOINTS.SALES.CUSTOMERS}${id}/`);
    } catch (error) {
      throw new Error(error.message || 'Erreur lors de la suppression du client');
    }
  }

  // === Gestion des ventes ===
  
  async getSales(params = {}) {
    try {
      const queryString = new URLSearchParams(params).toString();
      const url = queryString ? `${API_ENDPOINTS.SALES.SALES}?${queryString}` : API_ENDPOINTS.SALES.SALES;
      return await apiService.get(url);
    } catch (error) {
      throw new Error(error.message || 'Erreur lors de la récupération des ventes');
    }
  }

  async getSale(id) {
    try {
      return await apiService.get(`${API_ENDPOINTS.SALES.SALES}${id}/`);
    } catch (error) {
      throw new Error(error.message || 'Erreur lors de la récupération de la vente');
    }
  }

  async createSale(saleData) {
    try {
      return await apiService.post(API_ENDPOINTS.SALES.SALES, saleData);
    } catch (error) {
      throw new Error(error.message || 'Erreur lors de la création de la vente');
    }
  }

  async updateSale(id, saleData) {
    try {
      return await apiService.put(`${API_ENDPOINTS.SALES.SALES}${id}/`, saleData);
    } catch (error) {
      throw new Error(error.message || 'Erreur lors de la mise à jour de la vente');
    }
  }

  async deleteSale(id) {
    try {
      return await apiService.delete(`${API_ENDPOINTS.SALES.SALES}${id}/`);
    } catch (error) {
      throw new Error(error.message || 'Erreur lors de la suppression de la vente');
    }
  }

  // === Statistiques ===
  
  async getSalesStatistics() {
    try {
      // L'URL correcte inclut le slash final pour l'endpoint statistics
      const url = `${API_ENDPOINTS.SALES.SALES}statistics/`;
      return await apiService.get(url);
    } catch (error) {
      throw new Error(error.message || 'Erreur lors de la récupération des statistiques des ventes');
    }
  }

  async getCustomerPurchaseHistory(customerId) {
    try {
      return await apiService.get(`${API_ENDPOINTS.SALES.CUSTOMERS}${customerId}/purchase_history/`);
    } catch (error) {
      throw new Error(error.message || 'Erreur lors de la récupération de l\'historique des achats');
    }
  }

  // === Méthodes utilitaires ===
  
  formatSaleNumber(saleNumber) {
    return saleNumber || 'N/A';
  }

  formatPrice(price) {
    if (typeof price === 'number' || typeof price === 'string') {
      return new Intl.NumberFormat('fr-FR', {
        style: 'currency',
        currency: 'XOF',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
      }).format(parseFloat(price) || 0);
    }
    return '0 FCFA';
  }

  formatDate(dateString) {
    if (!dateString) return 'N/A';
    try {
      return new Date(dateString).toLocaleDateString('fr-FR');
    } catch (error) {
      return 'Date invalide';
    }
  }

  formatDateTime(dateString) {
    if (!dateString) return 'N/A';
    try {
      return new Date(dateString).toLocaleString('fr-FR');
    } catch (error) {
      return 'Date invalide';
    }
  }

  getStatusLabel(status) {
    const statusLabels = {
      'draft': 'Brouillon',
      'confirmed': 'Confirmée',
      'delivered': 'Livrée',
      'cancelled': 'Annulée',
      'returned': 'Retournée'
    };
    return statusLabels[status] || status;
  }

  getStatusColor(status) {
    const statusColors = {
      'draft': 'default',
      'confirmed': 'primary',
      'delivered': 'success',
      'cancelled': 'error',
      'returned': 'warning'
    };
    return statusColors[status] || 'default';
  }

  getPaymentStatusLabel(paymentStatus) {
    const paymentStatusLabels = {
      'pending': 'En attente',
      'partial': 'Partiel',
      'paid': 'Payé',
      'overdue': 'En retard'
    };
    return paymentStatusLabels[paymentStatus] || paymentStatus;
  }

  getPaymentStatusColor(paymentStatus) {
    const paymentStatusColors = {
      'pending': 'warning',
      'partial': 'info',
      'paid': 'success',
      'overdue': 'error'
    };
    return paymentStatusColors[paymentStatus] || 'default';
  }

  getCustomerTypeLabel(customerType) {
    const customerTypeLabels = {
      'member': 'Membre',
      'non_member': 'Non-membre',
      'corporate': 'Entreprise'
    };
    return customerTypeLabels[customerType] || customerType;
  }
}

// Instance singleton
const salesService = new SalesService();

export default salesService;