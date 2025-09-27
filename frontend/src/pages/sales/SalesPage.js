import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  IconButton,
  Grid,
  Card,
  CardContent,
  Alert,
  CircularProgress,
  Tabs,
  Tab
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Visibility as ViewIcon,
  ShoppingCart as SalesIcon,
  People as CustomersIcon,
  TrendingUp as RevenueIcon,
  Assessment as StatsIcon
} from '@mui/icons-material';
import salesService from '../../services/salesService';

const SalesPage = () => {
  // États pour les onglets
  const [currentTab, setCurrentTab] = useState(0);
  
  // États pour les données
  const [sales, setSales] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [statistics, setStatistics] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // États pour la pagination
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [totalCount, setTotalCount] = useState(0);

  // Charger les données initiales
  useEffect(() => {
    loadData();
  }, [currentTab, page, rowsPerPage]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError('');

      if (currentTab === 0) {
        // Onglet Ventes
        const params = {
          page: page + 1,
          page_size: rowsPerPage
        };

        const [salesData, statsData] = await Promise.all([
          salesService.getSales(params),
          salesService.getSalesStatistics().catch(() => ({}))
        ]);

        setSales(salesData.results || salesData);
        setTotalCount(salesData.count || salesData.length);
        setStatistics(statsData);

      } else if (currentTab === 1) {
        // Onglet Clients
        const customersData = await salesService.getCustomers({ 
          page: page + 1, 
          page_size: rowsPerPage 
        });
        setCustomers(customersData.results || customersData);
        setTotalCount(customersData.count || customersData.length);
      }

    } catch (err) {
      const errorMessage = err.message || err.toString() || 'Erreur inconnue';
      setError('Erreur lors du chargement des données: ' + errorMessage);
      console.error('Erreur détaillée:', err);
    } finally {
      setLoading(false);
    }
  };

  // Gestion des onglets
  const handleTabChange = (event, newValue) => {
    setCurrentTab(newValue);
    setPage(0);
  };

  // Gestion de la pagination
  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  // Formatage des prix
  const formatPrice = (price) => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'XOF'
    }).format(price || 0);
  };

  // Formatage des dates
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('fr-FR');
  };

  // Couleur du statut
  const getStatusColor = (status) => {
    const colors = {
      'draft': 'default',
      'pending': 'warning',
      'completed': 'success',
      'cancelled': 'error'
    };
    return colors[status] || 'default';
  };

  // Rendu des cartes de statistiques
  const StatCard = ({ title, value, icon, color }) => (
    <Card>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography color="textSecondary" gutterBottom variant="body2">
              {title}
            </Typography>
            <Typography variant="h4" component="div">
              {value}
            </Typography>
          </Box>
          <Box sx={{ color: color }}>
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  // Rendu de la table des ventes
  const SalesTable = () => (
    <>
      {/* Barre d'outils */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6">
            Liste des ventes
          </Typography>
          
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => console.log('Nouvelle vente')}
          >
            Nouvelle vente
          </Button>
        </Box>
      </Paper>

      {/* Table */}
      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>N° Vente</TableCell>
                <TableCell>Client</TableCell>
                <TableCell>Date</TableCell>
                <TableCell>Montant total</TableCell>
                <TableCell>Statut</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {sales.map((sale) => (
                <TableRow key={sale.id} hover>
                  <TableCell>{salesService.formatSaleNumber(sale.sale_number)}</TableCell>
                  <TableCell>{sale.customer?.name || 'N/A'}</TableCell>
                  <TableCell>{formatDate(sale.sale_date)}</TableCell>
                  <TableCell>{formatPrice(sale.total_amount)}</TableCell>
                  <TableCell>
                    <Chip
                      label={sale.status || 'N/A'}
                      color={getStatusColor(sale.status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <IconButton size="small" color="primary">
                      <ViewIcon />
                    </IconButton>
                    <IconButton size="small" color="primary">
                      <EditIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
              {sales.length === 0 && !loading && (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    <Typography variant="body1" color="textSecondary">
                      Aucune vente trouvée
                    </Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>

        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={totalCount}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
          labelRowsPerPage="Lignes par page:"
          labelDisplayedRows={({ from, to, count }) => 
            `${from}–${to} sur ${count !== -1 ? count : `plus de ${to}`}`
          }
        />
      </Paper>
    </>
  );

  // Rendu de la table des clients
  const CustomersTable = () => (
    <>
      {/* Barre d'outils */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6">
            Liste des clients
          </Typography>
          
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => console.log('Nouveau client')}
          >
            Nouveau client
          </Button>
        </Box>
      </Paper>

      {/* Table */}
      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Nom</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Téléphone</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Limite crédit</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {customers.map((customer) => (
                <TableRow key={customer.id} hover>
                  <TableCell>{customer.name}</TableCell>
                  <TableCell>
                    <Chip 
                      label={customer.customer_type} 
                      size="small"
                      color={customer.customer_type === 'member' ? 'success' : 'default'}
                    />
                  </TableCell>
                  <TableCell>{customer.phone || 'N/A'}</TableCell>
                  <TableCell>{customer.email || 'N/A'}</TableCell>
                  <TableCell>{formatPrice(customer.credit_limit)}</TableCell>
                  <TableCell>
                    <IconButton size="small" color="primary">
                      <EditIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
              {customers.length === 0 && !loading && (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    <Typography variant="body1" color="textSecondary">
                      Aucun client trouvé
                    </Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>

        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={totalCount}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
          labelRowsPerPage="Lignes par page:"
          labelDisplayedRows={({ from, to, count }) => 
            `${from}–${to} sur ${count !== -1 ? count : `plus de ${to}`}`
          }
        />
      </Paper>
    </>
  );

  if (loading && (sales.length === 0 && customers.length === 0)) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* En-tête */}
      <Box mb={3}>
        <Typography variant="h4" component="h1" gutterBottom>
          Gestion des Ventes
        </Typography>
        <Typography variant="body1" color="textSecondary">
          Gérez les ventes et les clients de votre coopérative
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Cartes de statistiques */}
      {currentTab === 0 && (
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Ventes aujourd'hui"
              value={statistics.sales_today || 0}
              icon={<SalesIcon sx={{ fontSize: 40 }} />}
              color="primary.main"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="CA du mois"
              value={formatPrice(statistics.monthly_revenue || 0)}
              icon={<RevenueIcon sx={{ fontSize: 40 }} />}
              color="success.main"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Total clients"
              value={statistics.total_customers || 0}
              icon={<CustomersIcon sx={{ fontSize: 40 }} />}
              color="info.main"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Ventes ce mois"
              value={statistics.monthly_sales || 0}
              icon={<StatsIcon sx={{ fontSize: 40 }} />}
              color="warning.main"
            />
          </Grid>
        </Grid>
      )}

      {/* Onglets */}
      <Paper sx={{ mb: 3 }}>
        <Tabs 
          value={currentTab} 
          onChange={handleTabChange}
          indicatorColor="primary"
          textColor="primary"
        >
          <Tab label="Ventes" />
          <Tab label="Clients" />
        </Tabs>
      </Paper>

      {/* Contenu des onglets */}
      {currentTab === 0 && <SalesTable />}
      {currentTab === 1 && <CustomersTable />}
    </Box>
  );
};

export default SalesPage;