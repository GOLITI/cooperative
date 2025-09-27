import React, { createContext, useContext, useReducer, useEffect } from 'react';
import authService from '../services/simpleAuth';

// États d'authentification
const authStates = {
  LOADING: 'loading',
  AUTHENTICATED: 'authenticated',
  UNAUTHENTICATED: 'unauthenticated',
  ERROR: 'error',
};

// Actions du reducer
const authActions = {
  SET_LOADING: 'SET_LOADING',
  SET_AUTHENTICATED: 'SET_AUTHENTICATED',
  SET_UNAUTHENTICATED: 'SET_UNAUTHENTICATED',
  SET_ERROR: 'SET_ERROR',
  SET_USER: 'SET_USER',
  CLEAR_ERROR: 'CLEAR_ERROR',
};

// État initial
const initialState = {
  status: authStates.LOADING,
  user: null,
  error: null,
  isAuthenticated: false,
};

// Reducer d'authentification
function authReducer(state, action) {
  switch (action.type) {
    case authActions.SET_LOADING:
      return {
        ...state,
        status: authStates.LOADING,
        error: null,
      };

    case authActions.SET_AUTHENTICATED:
      return {
        ...state,
        status: authStates.AUTHENTICATED,
        user: action.payload.user,
        isAuthenticated: true,
        error: null,
      };

    case authActions.SET_UNAUTHENTICATED:
      return {
        ...state,
        status: authStates.UNAUTHENTICATED,
        user: null,
        isAuthenticated: false,
        error: null,
      };

    case authActions.SET_ERROR:
      return {
        ...state,
        status: authStates.ERROR,
        error: action.payload.error,
        isAuthenticated: false,
      };

    case authActions.SET_USER:
      return {
        ...state,
        user: action.payload.user,
      };

    case authActions.CLEAR_ERROR:
      return {
        ...state,
        error: null,
      };

    default:
      return state;
  }
}

// Contexte d'authentification
const AuthContext = createContext();

// Provider d'authentification
export function AuthProvider({ children }) {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Vérification de l'état d'authentification au démarrage
  useEffect(() => {
    checkInitialAuthState();
  }, []);

  const checkInitialAuthState = async () => {
    dispatch({ type: authActions.SET_LOADING });

    try {
      const isAuth = await authService.checkAuthState();
      
      if (isAuth) {
        const user = authService.getCurrentUser();
        dispatch({
          type: authActions.SET_AUTHENTICATED,
          payload: { user },
        });
      } else {
        dispatch({ type: authActions.SET_UNAUTHENTICATED });
      }
    } catch (error) {
      console.error('Erreur lors de la vérification auth:', error);
      dispatch({
        type: authActions.SET_ERROR,
        payload: { error: 'Erreur de vérification d\'authentification' },
      });
    }
  };

  // Connexion
  const login = async (credentials) => {
    dispatch({ type: authActions.SET_LOADING });

    try {
      const result = await authService.login(credentials);
      
      if (result.success) {
        dispatch({
          type: authActions.SET_AUTHENTICATED,
          payload: { user: result.user },
        });
        return { success: true };
      } else {
        dispatch({
          type: authActions.SET_ERROR,
          payload: { error: result.error },
        });
        return { success: false, error: result.error };
      }
    } catch (error) {
      console.error('Erreur lors de la connexion:', error);
      const errorMessage = error.message || 'Erreur de connexion';
      dispatch({
        type: authActions.SET_ERROR,
        payload: { error: errorMessage },
      });
      return { success: false, error: errorMessage };
    }
  };

  // Déconnexion
  const logout = async () => {
    dispatch({ type: authActions.SET_LOADING });

    try {
      await authService.logout();
    } catch (error) {
      console.warn('Erreur lors de la déconnexion:', error);
    } finally {
      dispatch({ type: authActions.SET_UNAUTHENTICATED });
    }
  };

  // Mise à jour du profil utilisateur
  const updateUser = async (userData) => {
    try {
      const updatedUser = await authService.updateProfile(userData);
      dispatch({
        type: authActions.SET_USER,
        payload: { user: updatedUser },
      });
      return { success: true, user: updatedUser };
    } catch (error) {
      return { success: false, error: error.message };
    }
  };

  // Rafraîchir les données utilisateur
  const refreshUser = async () => {
    try {
      const user = await authService.getUserProfile();
      dispatch({
        type: authActions.SET_USER,
        payload: { user },
      });
      return user;
    } catch (error) {
      console.error('Erreur lors du rafraîchissement utilisateur:', error);
      throw error;
    }
  };

  // Effacer l'erreur
  const clearError = () => {
    dispatch({ type: authActions.CLEAR_ERROR });
  };

  // Valeur du contexte
  const contextValue = {
    // État
    ...state,
    
    // Actions
    login,
    logout,
    updateUser,
    refreshUser,
    clearError,
    
    // Utilitaires
    isLoading: state.status === authStates.LOADING,
    hasError: state.status === authStates.ERROR,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}

// Hook pour utiliser le contexte d'authentification
export function useAuth() {
  const context = useContext(AuthContext);
  
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
}

export default AuthContext;