import React, { useEffect, useState } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  Avatar,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  People,
  Inventory,
  ShoppingCart,
  AccountBalance,
  TrendingUp,
  TrendingDown,
} from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';
import apiService from '../../services/api';

// Composant pour les cartes de statistiques
function StatCard({ title, value, icon, color, trend, trendValue }) {
  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography color="textSecondary" gutterBottom variant="body2">
              {title}
            </Typography>
            <Typography variant="h4" component="div" sx={{ fontWeight: 'bold' }}>
              {value || '0'}
            </Typography>
            {trend && (
              <Box display="flex" alignItems="center" mt={1}>
                {trend === 'up' ? (
                  <TrendingUp sx={{ color: 'success.main', mr: 0.5 }} />
                ) : (
                  <TrendingDown sx={{ color: 'error.main', mr: 0.5 }} />
                )}
                <Typography
                  variant="body2"
                  color={trend === 'up' ? 'success.main' : 'error.main'}
                >
                  {trendValue}%
                </Typography>
              </Box>
            )}
          </Box>
          <Avatar
            sx={{
              bgcolor: color,
              width: 56,
              height: 56,
            }}
          >
            {icon}
          </Avatar>
        </Box>
      </CardContent>
    </Card>
  );
}

function DashboardPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    members: 0,
    products: 0,
    sales: 0,
    revenue: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardStats();
  }, []);

  const fetchDashboardStats = async () => {
    setLoading(true);
    setError(null);

    try {
      // Ces appels peuvent échouer en raison de l'authentification,
      // mais nous affichons quand même le dashboard avec des valeurs par défaut
      const [membersRes, productsRes, salesRes] = await Promise.allSettled([
        apiService.get('/api/v1/members/members/'),
        apiService.get('/api/v1/inventory/products/'),
        apiService.get('/api/v1/sales/sales/'),
      ]);

      setStats({
        members: membersRes.status === 'fulfilled' ? membersRes.value.count || 0 : 0,
        products: productsRes.status === 'fulfilled' ? productsRes.value.count || 0 : 0,
        sales: salesRes.status === 'fulfilled' ? salesRes.value.count || 0 : 0,
        revenue: 0, // À calculer depuis les données de vente
      });
    } catch (err) {
      console.warn('Erreur lors de la récupération des statistiques:', err);
      setError('Impossible de charger certaines statistiques');
    } finally {
      setLoading(false);
    }
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Bonjour';
    if (hour < 18) return 'Bon après-midi';
    return 'Bonsoir';
  };

  const getUserName = () => {
    if (user?.first_name && user?.last_name) {
      return `${user.first_name} ${user.last_name}`;
    }
    return user?.username || 'Utilisateur';
  };

  return (
    <Box>
      {/* En-tête de bienvenue */}
      <Box mb={4}>
        <Typography variant="h4" component="h1" gutterBottom>
          {getGreeting()}, {getUserName()} ! 👋
        </Typography>
        <Typography variant="subtitle1" color="textSecondary">
          Voici un aperçu de votre coopérative aujourd'hui.
        </Typography>
      </Box>

      {/* Affichage d'erreur si nécessaire */}
      {error && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Cartes de statistiques */}
      {loading ? (
        <Box display="flex" justifyContent="center" py={8}>
          <CircularProgress />
        </Box>
      ) : (
        <Grid container spacing={3} mb={4}>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Membres Totaux"
              value={stats.members}
              icon={<People />}
              color="#1976d2"
              trend="up"
              trendValue="12"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Produits en Stock"
              value={stats.products}
              icon={<Inventory />}
              color="#388e3c"
              trend="down"
              trendValue="3"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Ventes ce Mois"
              value={stats.sales}
              icon={<ShoppingCart />}
              color="#f57c00"
              trend="up"
              trendValue="25"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Chiffre d'Affaires"
              value={`${stats.revenue.toLocaleString()} FCFA`}
              icon={<AccountBalance />}
              color="#7b1fa2"
              trend="up"
              trendValue="18"
            />
          </Grid>
        </Grid>
      )}

      {/* Sections supplémentaires */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              Activités Récentes
            </Typography>
            <Box
              display="flex"
              alignItems="center"
              justifyContent="center"
              height="300px"
              color="textSecondary"
            >
              <Typography>
                Graphique des activités - À implémenter
              </Typography>
            </Box>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              Actions Rapides
            </Typography>
            <Box mt={2}>
              <Typography variant="body2" color="textSecondary">
                • Ajouter un nouveau membre
              </Typography>
              <Typography variant="body2" color="textSecondary" mt={1}>
                • Enregistrer une vente
              </Typography>
              <Typography variant="body2" color="textSecondary" mt={1}>
                • Mise à jour du stock
              </Typography>
              <Typography variant="body2" color="textSecondary" mt={1}>
                • Générer un rapport
              </Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

export default DashboardPage;