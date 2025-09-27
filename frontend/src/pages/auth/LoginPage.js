import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress,
  Container,
  Avatar,
  IconButton,
  InputAdornment,
  Link,
} from '@mui/material';
import { LockOutlined, Visibility, VisibilityOff } from '@mui/icons-material';
import { useNavigate, useLocation, Link as RouterLink } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, isAuthenticated, isLoading, error, clearError } = useAuth();

  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });
  const [formErrors, setFormErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  // Rediriger si déjà authentifié
  useEffect(() => {
    console.log('LoginPage useEffect: isAuthenticated =', isAuthenticated);
    if (isAuthenticated) {
      const from = location.state?.from?.pathname || '/dashboard';
      console.log('LoginPage useEffect: Redirection vers', from);
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, navigate, location.state?.from?.pathname]);

  // Effacer l'erreur quand le composant se monte (une seule fois)
  useEffect(() => {
    clearError();
  }, []); // Dépendance vide - s'exécute une seule fois

  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setFormData({
      ...formData,
      [name]: value,
    });
    
    // Effacer l'erreur du champ quand l'utilisateur tape
    if (formErrors[name]) {
      setFormErrors({
        ...formErrors,
        [name]: '',
      });
    }
  };

  const validateForm = () => {
    const errors = {};

    if (!formData.username.trim()) {
      errors.username = 'Le nom d\'utilisateur est requis';
    }

    if (!formData.password) {
      errors.password = 'Le mot de passe est requis';
    } else if (formData.password.length < 6) {
      errors.password = 'Le mot de passe doit contenir au moins 6 caractères';
    }

    return errors;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    
    // Validation côté client
    const errors = validateForm();
    if (Object.keys(errors).length > 0) {
      setFormErrors(errors);
      return;
    }

    setIsSubmitting(true);
    setFormErrors({});

    try {
      console.log('Tentative de connexion avec:', formData);
      const result = await login(formData);
      console.log('Résultat de connexion:', result);
      
      if (result.success) {
        console.log('Connexion réussie, l\'état isAuthenticated va déclencher la redirection automatique');
        // La redirection est gérée automatiquement par le useEffect qui surveille isAuthenticated
      } else {
        console.log('Échec de connexion:', result.error);
        setFormErrors({
          general: result.error || 'Erreur de connexion inconnue'
        });
      }
    } catch (err) {
      console.error('Erreur de connexion:', err);
      setFormErrors({
        general: err.message || 'Erreur de connexion inattendue'
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
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

  return (
    <Container component="main" maxWidth="xs">
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
        }}
      >
        <Paper
          elevation={3}
          sx={{
            p: 4,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            width: '100%',
          }}
        >
          <Avatar sx={{ m: 1, bgcolor: 'primary.main', width: 56, height: 56 }}>
            <LockOutlined fontSize="large" />
          </Avatar>
          
          <Typography component="h1" variant="h4" gutterBottom>
            CoopManager
          </Typography>
          
          <Typography variant="h6" color="textSecondary" gutterBottom>
            Connexion
          </Typography>

                    {error && (
            <Alert 
              severity="error" 
              sx={{ mb: 2 }}
              onClose={clearError}
            >
              {error}
            </Alert>
          )}

          {formErrors.general && (
            <Alert 
              severity="error" 
              sx={{ mb: 2 }}
            >
              {formErrors.general}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1, width: '100%' }}>
            <TextField
              margin="normal"
              required
              fullWidth
              id="username"
              label="Nom d'utilisateur"
              name="username"
              autoComplete="username"
              autoFocus
              value={formData.username}
              onChange={handleInputChange}
              error={!!formErrors.username}
              helperText={formErrors.username}
              disabled={isSubmitting}
            />
            
            <TextField
              margin="normal"
              required
              fullWidth
              name="password"
              label="Mot de passe"
              type={showPassword ? 'text' : 'password'}
              id="password"
              autoComplete="current-password"
              value={formData.password}
              onChange={handleInputChange}
              error={!!formErrors.password}
              helperText={formErrors.password}
              disabled={isSubmitting}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      aria-label="toggle password visibility"
                      onClick={() => setShowPassword(!showPassword)}
                      edge="end"
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
            
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2, py: 1.5 }}
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <CircularProgress size={24} color="inherit" />
              ) : (
                'Se connecter'
              )}
            </Button>

            <Box textAlign="center" sx={{ mt: 2 }}>
              <Link component={RouterLink} to="/register" variant="body2">
                Pas encore de compte ? S'inscrire comme admin de coopérative
              </Link>
            </Box>
          </Box>

          <Typography variant="body2" color="textSecondary" align="center" sx={{ mt: 2 }}>
            Système de Gestion des Coopératives Agricoles
          </Typography>
        </Paper>
        
        <Typography variant="body2" color="textSecondary" align="center" sx={{ mt: 4 }}>
          © 2024 CoopManager - Tous droits réservés
        </Typography>
      </Box>
    </Container>
  );
}

export default LoginPage;