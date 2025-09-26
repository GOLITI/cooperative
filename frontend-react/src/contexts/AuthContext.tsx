import React, { createContext, useContext, useState, useEffect } from 'react'

interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  is_staff: boolean
  is_superuser: boolean
}

interface AuthContextType {
  user: User | null
  token: string | null
  login: (username: string, password: string) => Promise<boolean>
  logout: () => void
  isLoading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

const API_BASE_URL = 'http://localhost:8000/api'

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Charger le token depuis localStorage au démarrage
  useEffect(() => {
    const savedToken = localStorage.getItem('authToken')
    if (savedToken) {
      setToken(savedToken)
      // Valider le token avec l'API
      validateToken(savedToken)
    } else {
      setIsLoading(false)
    }
  }, [])

  const validateToken = async (tokenToValidate: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/me/`, {
        headers: {
          'Authorization': `Token ${tokenToValidate}`,
          'Content-Type': 'application/json',
        },
      })

      if (response.ok) {
        const userData = await response.json()
        console.log('Token validation réussie:', userData) // Debug
        setUser(userData)
        setToken(tokenToValidate)
      } else {
        console.log('Token validation échoué:', response.status) // Debug
        // Token invalide, le supprimer
        localStorage.removeItem('authToken')
        setToken(null)
        setUser(null)
      }
    } catch (error) {
      console.error('Erreur de validation du token:', error)
      localStorage.removeItem('authToken')
      setToken(null)
      setUser(null)
    } finally {
      setIsLoading(false)
    }
  }

  const login = async (username: string, password: string): Promise<boolean> => {
    console.log('Tentative de connexion pour:', username) // Debug
    
    try {
      const url = `${API_BASE_URL}/auth/login/`
      console.log('URL d\'authentification:', url) // Debug
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      })

      console.log('Status de réponse:', response.status) // Debug
      
      if (response.ok) {
        const data = await response.json()
        console.log('Réponse d\'authentification complète:', data) // Debug
        
        // L'API Django renvoie {message, user, token}
        const { token: newToken, user: userData } = data
        
        if (newToken && userData) {
          setToken(newToken)
          setUser(userData)
          localStorage.setItem('authToken', newToken)
          console.log('Authentification réussie, token sauvegardé') // Debug
          return true
        } else {
          console.error('Token ou données utilisateur manquants:', { newToken: !!newToken, userData: !!userData })
          return false
        }
      } else {
        const errorData = await response.json().catch(() => ({}))
        console.error('Erreur de connexion:', response.status, errorData)
        return false
      }
    } catch (error) {
      console.error('Erreur réseau lors de la connexion:', error)
      return false
    }
  }

  const logout = () => {
    setUser(null)
    setToken(null)
    localStorage.removeItem('authToken')
  }

  const value: AuthContextType = {
    user,
    token,
    login,
    logout,
    isLoading,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth doit être utilisé dans un AuthProvider')
  }
  return context
}