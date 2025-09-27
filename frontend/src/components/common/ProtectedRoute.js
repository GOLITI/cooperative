import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { Box, CircularProgress } from '@mui/material';
import { useAuth } from '../../contexts/AuthContext';

function ProtectedRoute({ children }) {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  console.log('ProtectedRoute: isLoading =', isLoading, ', isAuthenticated =', isAuthenticated, ', location =', location.pathname);

  // Afficher un loader pendant la vérification de l'authentification
  if (isLoading) {
    console.log('ProtectedRoute: Affichage du loader');
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
      >
        <CircularProgress />
      </Box>
    );
  }

  // Rediriger vers la page de connexion si non authentifié
  if (!isAuthenticated) {
    console.log('ProtectedRoute: Non authentifié, redirection vers /login');
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Afficher le contenu protégé si authentifié
  console.log('ProtectedRoute: Authentifié, affichage du contenu');
  return children;
}

export default ProtectedRoute;