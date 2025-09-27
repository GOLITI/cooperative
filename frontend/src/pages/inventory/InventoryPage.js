import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  TextField,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  Card,
  CardContent,
  Alert,
  CircularProgress,
  InputAdornment,
  Tabs,
  Tab,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Search as SearchIcon,
  Inventory as InventoryIcon,
  Category as CategoryIcon,
  TrendingDown as TrendingDownIcon,
  Warning as WarningIcon,
  Timeline as TimelineIcon
} from '@mui/icons-material';
import { inventoryService } from '../../services/inventoryNew';

const InventoryPage = () => {
  // États pour les onglets
  const [currentTab, setCurrentTab] = useState(0);
  
  // États pour les données
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [units, setUnits] = useState([]);
  const [statistics, setStatistics] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // États pour la table
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [totalCount, setTotalCount] = useState(0);

  // États pour les dialogues
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [dialogMode, setDialogMode] = useState('add');
  const [dialogType, setDialogType] = useState('product'); // 'product', 'category'

  // Charger les données initiales
  useEffect(() => {
    loadData();
  }, [currentTab, page, rowsPerPage, searchQuery, categoryFilter]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError('');

      if (currentTab === 0) {
        // Onglet Produits
        const params = {
          page: page + 1,
          page_size: rowsPerPage,
          search: searchQuery || undefined,
          category: categoryFilter || undefined
        };

        const [productsData, categoriesData, unitsData, statsData] = await Promise.all([
          inventoryService.getProducts(params),
          inventoryService.getCategories(),
          inventoryService.getUnits(),
          inventoryService.getInventoryStatistics().catch(() => ({}))
        ]);

        setProducts(productsData.results || productsData);
        setTotalCount(productsData.count || productsData.length);
        setCategories(categoriesData.results || categoriesData);
        setUnits(unitsData.results || unitsData);
        setStatistics(statsData);

      } else if (currentTab === 1) {
        // Onglet Catégories
        const categoriesData = await inventoryService.getCategories();
        setCategories(categoriesData.results || categoriesData);
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
    setSearchQuery('');
  };

  // Gestion de la recherche
  const handleSearch = (event) => {
    setSearchQuery(event.target.value);
    setPage(0);
  };

  // Gestion du filtre par catégorie
  const handleCategoryFilter = (event) => {
    setCategoryFilter(event.target.value);
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

  // Gestion des dialogues
  const handleOpenDialog = (type, mode, item = null) => {
    setDialogType(type);
    setDialogMode(mode);
    setSelectedItem(item);
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedItem(null);
  };

  // Formatage des nombres
  const formatNumber = (number) => {
    return new Intl.NumberFormat('fr-FR').format(number);
  };

  // Formatage des prix
  const formatPrice = (price) => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'XOF'
    }).format(price);
  };

  // Couleur du statut de stock
  const getStockStatusColor = (currentStock, minStock) => {
    if (currentStock === 0) return 'error';
    if (currentStock <= minStock) return 'warning';
    return 'success';
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

  // Rendu de la table des produits
  const ProductsTable = () => (
    <>
      {/* Barre d'outils */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" gap={2}>
          <Box display="flex" alignItems="center" gap={2}>
            <TextField
              placeholder="Rechercher des produits..."
              variant="outlined"
              size="small"
              value={searchQuery}
              onChange={handleSearch}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                )
              }}
              sx={{ width: 300 }}
            />
            
            <FormControl size="small" sx={{ width: 200 }}>
              <InputLabel>Catégorie</InputLabel>
              <Select
                value={categoryFilter}
                onChange={handleCategoryFilter}
                label="Catégorie"
              >
                <MenuItem value="">Toutes les catégories</MenuItem>
                {categories.map((category) => (
                  <MenuItem key={category.id} value={category.id}>
                    {category.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>
          
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleOpenDialog('product', 'add')}
          >
            Ajouter un produit
          </Button>
        </Box>
      </Paper>

      {/* Table */}
      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>SKU</TableCell>
                <TableCell>Nom du produit</TableCell>
                <TableCell>Catégorie</TableCell>
                <TableCell>Prix unitaire</TableCell>
                <TableCell>Stock actuel</TableCell>
                <TableCell>Stock minimum</TableCell>
                <TableCell>Statut</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {products.map((product) => (
                <TableRow key={product.id} hover>
                  <TableCell>{product.sku}</TableCell>
                  <TableCell>{product.name}</TableCell>
                  <TableCell>{product.category?.name || 'N/A'}</TableCell>
                  <TableCell>{formatPrice(product.selling_price_member || 0)}</TableCell>
                  <TableCell>{formatNumber(product.current_stock || 0)}</TableCell>
                  <TableCell>{formatNumber(product.minimum_stock || 0)}</TableCell>
                  <TableCell>
                    <Chip
                      label={
                        product.current_stock === 0 ? 'Rupture' :
                        product.current_stock <= product.minimum_stock ? 'Stock faible' : 'En stock'
                      }
                      color={getStockStatusColor(product.current_stock, product.minimum_stock)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      onClick={() => handleOpenDialog('product', 'edit', product)}
                      color="primary"
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleOpenDialog('product', 'delete', product)}
                      color="error"
                    >
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
              {products.length === 0 && !loading && (
                <TableRow>
                  <TableCell colSpan={8} align="center">
                    <Typography variant="body1" color="textSecondary">
                      Aucun produit trouvé
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

  // Rendu de la table des catégories
  const CategoriesTable = () => (
    <>
      {/* Barre d'outils */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <TextField
            placeholder="Rechercher des catégories..."
            variant="outlined"
            size="small"
            value={searchQuery}
            onChange={handleSearch}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              )
            }}
            sx={{ width: 300 }}
          />
          
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleOpenDialog('category', 'add')}
          >
            Ajouter une catégorie
          </Button>
        </Box>
      </Paper>

      {/* Table */}
      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Code</TableCell>
                <TableCell>Nom</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Catégorie parent</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {categories.map((category) => (
                <TableRow key={category.id} hover>
                  <TableCell>{category.code}</TableCell>
                  <TableCell>{category.name}</TableCell>
                  <TableCell>{category.description}</TableCell>
                  <TableCell>{category.parent?.name || 'Racine'}</TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      onClick={() => handleOpenDialog('category', 'edit', category)}
                      color="primary"
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleOpenDialog('category', 'delete', category)}
                      color="error"
                    >
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </>
  );

  if (loading && (products.length === 0 && categories.length === 0)) {
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
          Gestion de l'Inventaire
        </Typography>
        <Typography variant="body1" color="textSecondary">
          Gérez les produits, catégories et stocks de votre coopérative
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
              title="Total Produits"
              value={statistics.total_products || 0}
              icon={<InventoryIcon sx={{ fontSize: 40 }} />}
              color="primary.main"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Catégories"
              value={categories.length}
              icon={<CategoryIcon sx={{ fontSize: 40 }} />}
              color="success.main"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Rupture de stock"
              value={statistics.out_of_stock || 0}
              icon={<TrendingDownIcon sx={{ fontSize: 40 }} />}
              color="error.main"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Stock faible"
              value={statistics.low_stock || 0}
              icon={<WarningIcon sx={{ fontSize: 40 }} />}
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
          <Tab label="Produits" />
          <Tab label="Catégories" />
        </Tabs>
      </Paper>

      {/* Contenu des onglets */}
      {currentTab === 0 && <ProductsTable />}
      {currentTab === 1 && <CategoriesTable />}

      {/* Dialog pour les actions */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {dialogMode === 'add' && `Ajouter ${dialogType === 'product' ? 'un produit' : 'une catégorie'}`}
          {dialogMode === 'edit' && `Modifier ${dialogType === 'product' ? 'le produit' : 'la catégorie'}`}
          {dialogMode === 'delete' && `Supprimer ${dialogType === 'product' ? 'le produit' : 'la catégorie'}`}
        </DialogTitle>
        <DialogContent>
          {dialogMode === 'delete' ? (
            <Typography>
              Êtes-vous sûr de vouloir supprimer cet élément ? Cette action est irréversible.
            </Typography>
          ) : (
            <Typography>
              Formulaire de {dialogMode === 'add' ? 'création' : 'modification'} à implémenter
            </Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>
            Annuler
          </Button>
          <Button 
            variant="contained" 
            color={dialogMode === 'delete' ? 'error' : 'primary'}
          >
            {dialogMode === 'add' && 'Ajouter'}
            {dialogMode === 'edit' && 'Modifier'}
            {dialogMode === 'delete' && 'Supprimer'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default InventoryPage;