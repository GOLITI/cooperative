import { API_BASE_URL, getAuthHeaders, handleApiError, type Member, type ApiResponse } from './api'

export const membersApi = {
  // Obtenir la liste des membres
  getMembers: async (token: string | null, params?: { 
    page?: number
    search?: string 
    is_active?: boolean 
  }): Promise<ApiResponse<Member>> => {
    const queryParams = new URLSearchParams()
    if (params?.page) queryParams.append('page', params.page.toString())
    if (params?.search) queryParams.append('search', params.search)
    if (params?.is_active !== undefined) queryParams.append('is_active', params.is_active.toString())
    
    const url = `${API_BASE_URL}/members/?${queryParams.toString()}`
    const response = await fetch(url, {
      headers: getAuthHeaders(token),
    })
    
    await handleApiError(response)
    return response.json()
  },

  // Obtenir un membre par ID
  getMember: async (token: string | null, id: number): Promise<Member> => {
    const response = await fetch(`${API_BASE_URL}/members/${id}/`, {
      headers: getAuthHeaders(token),
    })
    
    await handleApiError(response)
    return response.json()
  },

  // Créer un nouveau membre
  createMember: async (token: string | null, memberData: Partial<Member>): Promise<Member> => {
    const response = await fetch(`${API_BASE_URL}/members/`, {
      method: 'POST',
      headers: getAuthHeaders(token),
      body: JSON.stringify(memberData),
    })
    
    await handleApiError(response)
    return response.json()
  },

  // Mettre à jour un membre
  updateMember: async (token: string | null, id: number, memberData: Partial<Member>): Promise<Member> => {
    const response = await fetch(`${API_BASE_URL}/members/${id}/`, {
      method: 'PUT',
      headers: getAuthHeaders(token),
      body: JSON.stringify(memberData),
    })
    
    await handleApiError(response)
    return response.json()
  },

  // Supprimer un membre
  deleteMember: async (token: string | null, id: number): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/members/${id}/`, {
      method: 'DELETE',
      headers: getAuthHeaders(token),
    })
    
    await handleApiError(response)
  },

  // Obtenir les statistiques des membres
  getMemberStats: async (token: string | null) => {
    const response = await fetch(`${API_BASE_URL}/members/stats/`, {
      headers: getAuthHeaders(token),
    })
    
    await handleApiError(response)
    return response.json()
  },
}