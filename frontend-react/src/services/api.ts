// Configuration de base de l'API
export const API_BASE_URL = 'http://localhost:8000/api'

// Fonction utilitaire pour construire les headers avec authentification
export const getAuthHeaders = (token?: string | null) => {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  }
  
  if (token) {
    headers['Authorization'] = `Token ${token}`
  }
  
  return headers
}

// Fonction utilitaire pour gérer les réponses d'erreur
export const handleApiError = async (response: Response) => {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ 
      detail: 'Erreur de communication avec le serveur' 
    }))
    throw new Error(errorData.detail || `Erreur HTTP ${response.status}`)
  }
  return response
}

// Types de base pour les réponses d'API
export interface ApiResponse<T> {
  results: T[]
  count: number
  next: string | null
  previous: string | null
}

export interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  is_staff: boolean
  is_superuser: boolean
}

export interface Member {
  id: number
  user: User
  phone_number: string
  address: string
  date_of_birth: string
  membership_number: string
  date_joined: string
  is_active: boolean
}

export interface Product {
  id: number
  name: string
  description: string
  category: {
    id: number
    name: string
    description: string
  }
  unit: string
  price: number
  stock_quantity: number
  minimum_stock: number
  created_at: string
}

export interface Order {
  id: number
  customer: Member
  status: 'pending' | 'confirmed' | 'delivered' | 'cancelled'
  total_amount: number
  order_date: string
  delivery_date: string | null
  items: OrderItem[]
}

export interface OrderItem {
  id: number
  product: Product
  quantity: number
  price: number
  total: number
}

export interface Account {
  id: number
  name: string
  account_type: 'bank' | 'cash' | 'loan' | 'savings'
  balance: number
  description: string
  is_active: boolean
}

export interface Transaction {
  id: number
  account: Account
  amount: number
  transaction_type: 'credit' | 'debit'
  description: string
  date: string
  reference: string
}

export interface Loan {
  id: number
  borrower: Member
  amount: number
  interest_rate: number
  duration_months: number
  status: 'active' | 'completed' | 'defaulted'
  created_date: string
  due_date: string
}

export interface SavingsAccount {
  id: number
  member: Member
  balance: number
  interest_rate: number
  created_date: string
  last_transaction_date: string
}