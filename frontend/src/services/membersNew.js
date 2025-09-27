// Service API unifié pour la gestion des membres
import apiService from './api';
import { API_ENDPOINTS } from '../constants/api';

class MembersService {
  // Récupérer tous les membres avec pagination et filtres
  async getMembers(params = {}) {
    try {
      const response = await apiService.get(API_ENDPOINTS.MEMBERS.MEMBERS, { params });
      return response;
    } catch (error) {
      console.error('Erreur lors de la récupération des membres:', error);
      throw error;
    }
  }

  // Récupérer un membre par ID
  async getMemberById(id) {
    try {
      const response = await apiService.get(`${API_ENDPOINTS.MEMBERS.MEMBERS}${id}/`);
      return response;
    } catch (error) {
      console.error(`Erreur lors de la récupération du membre ${id}:`, error);
      throw error;
    }
  }

  // Créer un nouveau membre
  async createMember(memberData) {
    try {
      const response = await apiService.post(API_ENDPOINTS.MEMBERS.MEMBERS, memberData);
      return response;
    } catch (error) {
      console.error('Erreur lors de la création du membre:', error);
      throw error;
    }
  }

  // Mettre à jour un membre
  async updateMember(id, memberData) {
    try {
      const response = await apiService.put(`${API_ENDPOINTS.MEMBERS.MEMBERS}${id}/`, memberData);
      return response;
    } catch (error) {
      console.error(`Erreur lors de la mise à jour du membre ${id}:`, error);
      throw error;
    }
  }

  // Supprimer un membre
  async deleteMember(id) {
    try {
      const response = await apiService.delete(`${API_ENDPOINTS.MEMBERS.MEMBERS}${id}/`);
      return response;
    } catch (error) {
      console.error(`Erreur lors de la suppression du membre ${id}:`, error);
      throw error;
    }
  }

  // Récupérer les statistiques des membres
  async getMembersStatistics() {
    try {
      const response = await apiService.get(`${API_ENDPOINTS.MEMBERS.MEMBERS}statistics/`);
      return response;
    } catch (error) {
      console.error('Erreur lors de la récupération des statistiques:', error);
      // Retourner des statistiques par défaut en cas d'erreur
      return {
        total_members: 0,
        active_members: 0,
        inactive_members: 0,
        new_members_this_month: 0
      };
    }
  }

  // Récupérer les types d'adhésion
  async getMembershipTypes() {
    try {
      const response = await apiService.get(`${API_ENDPOINTS.MEMBERS.MEMBERS}membership-types/`);
      return response;
    } catch (error) {
      console.error('Erreur lors de la récupération des types d\'adhésion:', error);
      // Retourner des types par défaut en cas d'erreur
      return [
        { id: 1, name: 'Membre Standard' },
        { id: 2, name: 'Membre Premium' }
      ];
    }
  }

  // Récupérer les cotisations d'un membre
  async getMembershipFees(memberId) {
    try {
      const response = await apiService.get(API_ENDPOINTS.MEMBERS.MEMBERSHIP_FEES, {
        params: { member: memberId }
      });
      return response;
    } catch (error) {
      console.error(`Erreur lors de la récupération des cotisations du membre ${memberId}:`, error);
      throw error;
    }
  }

  // Enregistrer le paiement d'une cotisation
  async payMembershipFee(feeData) {
    try {
      const response = await apiService.post(API_ENDPOINTS.MEMBERS.MEMBERSHIP_FEES, feeData);
      return response;
    } catch (error) {
      console.error('Erreur lors de l\'enregistrement du paiement:', error);
      throw error;
    }
  }

  // Rechercher des membres
  async searchMembers(query) {
    try {
      const params = { search: query };
      const response = await apiService.get(API_ENDPOINTS.MEMBERS.MEMBERS, { params });
      return response;
    } catch (error) {
      console.error('Erreur lors de la recherche de membres:', error);
      throw error;
    }
  }

  // Exporter la liste des membres
  async exportMembers(format = 'csv') {
    try {
      const response = await apiService.get(`${API_ENDPOINTS.MEMBERS.MEMBERS}export/`, {
        params: { format },
        responseType: 'blob'
      });
      return response;
    } catch (error) {
      console.error('Erreur lors de l\'export des membres:', error);
      throw error;
    }
  }

  // Importer des membres depuis un fichier
  async importMembers(file) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await apiService.post(`${API_ENDPOINTS.MEMBERS.MEMBERS}import/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response;
    } catch (error) {
      console.error('Erreur lors de l\'import des membres:', error);
      throw error;
    }
  }
}

// Instance singleton
const membersService = new MembersService();
export { membersService };
export default membersService;