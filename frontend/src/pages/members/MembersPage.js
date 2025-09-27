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
  InputAdornment
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Search as SearchIcon,
  People as PeopleIcon,
  PersonAdd as PersonAddIcon,
  TrendingUp as TrendingUpIcon
} from '@mui/icons-material';
import { membersService } from '../../services/membersNew';

const MembersPage = () => {
  // États pour les données
  const [members, setMembers] = useState([]);
  const [membershipTypes, setMembershipTypes] = useState([]);
  const [statistics, setStatistics] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // États pour la table et la recherche
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchQuery, setSearchQuery] = useState('');
  const [totalCount, setTotalCount] = useState(0);

  // États pour les dialogues
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedMember, setSelectedMember] = useState(null);
  const [dialogMode, setDialogMode] = useState('add'); // 'add', 'edit', 'view'

  // Charger les données initiales
  useEffect(() => {
    loadData();
  }, [page, rowsPerPage, searchQuery]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError('');

      // Charger les membres avec pagination
      const membersParams = {
        page: page + 1,
        page_size: rowsPerPage,
        search: searchQuery || undefined
      };

      const [membersData, statsData, typesData] = await Promise.all([
        membersService.getMembers(membersParams),
        membersService.getMembersStatistics(),
        membersService.getMembershipTypes()
      ]);

      setMembers(membersData.results || membersData);
      setTotalCount(membersData.count || membersData.length);
      setStatistics(statsData);
      setMembershipTypes(typesData.results || typesData);

    } catch (err) {
      const errorMessage = err.message || err.toString() || 'Erreur inconnue';
      setError('Erreur lors du chargement des données: ' + errorMessage);
      console.error('Erreur détaillée:', err);
    } finally {
      setLoading(false);
    }
  };

  // Gestion de la recherche
  const handleSearch = (event) => {
    setSearchQuery(event.target.value);
    setPage(0); // Reset à la première page lors d'une recherche
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
  const handleOpenDialog = (mode, member = null) => {
    setDialogMode(mode);
    setSelectedMember(member);
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedMember(null);
  };

  // Formatage de la date
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('fr-FR');
  };

  // Couleur du statut
  const getStatusColor = (status) => {
    const colors = {
      'active': 'success',
      'suspended': 'warning',
      'inactive': 'error'
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

  if (loading && members.length === 0) {
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
          Gestion des Membres
        </Typography>
        <Typography variant="body1" color="textSecondary">
          Gérez les membres de votre coopérative agricole
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Cartes de statistiques */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Membres"
            value={statistics.total_members || 0}
            icon={<PeopleIcon sx={{ fontSize: 40 }} />}
            color="primary.main"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Membres Actifs"
            value={statistics.active_members || 0}
            icon={<PersonAddIcon sx={{ fontSize: 40 }} />}
            color="success.main"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Nouveaux ce mois"
            value={statistics.new_members_this_month || 0}
            icon={<TrendingUpIcon sx={{ fontSize: 40 }} />}
            color="info.main"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Types d'adhésion"
            value={membershipTypes.length}
            icon={<PeopleIcon sx={{ fontSize: 40 }} />}
            color="warning.main"
          />
        </Grid>
      </Grid>

      {/* Barre d'outils */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <TextField
            placeholder="Rechercher des membres..."
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
            onClick={() => handleOpenDialog('add')}
          >
            Ajouter un membre
          </Button>
        </Box>
      </Paper>

      {/* Table des membres */}
      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Numéro d'adhésion</TableCell>
                <TableCell>Nom complet</TableCell>
                <TableCell>Type d'adhésion</TableCell>
                <TableCell>Statut</TableCell>
                <TableCell>Date d'adhésion</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {members.map((member) => (
                <TableRow key={member.id} hover>
                  <TableCell>{member.membership_number}</TableCell>
                  <TableCell>
                    {member.user ? `${member.user.first_name} ${member.user.last_name}` : 'N/A'}
                  </TableCell>
                  <TableCell>{member.membership_type?.name || 'N/A'}</TableCell>
                  <TableCell>
                    <Chip
                      label={member.status}
                      color={getStatusColor(member.status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{formatDate(member.join_date)}</TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      onClick={() => handleOpenDialog('edit', member)}
                      color="primary"
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleOpenDialog('delete', member)}
                      color="error"
                    >
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
              {members.length === 0 && !loading && (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    <Typography variant="body1" color="textSecondary">
                      Aucun membre trouvé
                    </Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Pagination */}
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

      {/* Dialog pour les actions */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {dialogMode === 'add' && 'Ajouter un membre'}
          {dialogMode === 'edit' && 'Modifier le membre'}
          {dialogMode === 'delete' && 'Supprimer le membre'}
        </DialogTitle>
        <DialogContent>
          {dialogMode === 'delete' ? (
            <Typography>
              Êtes-vous sûr de vouloir supprimer ce membre ? Cette action est irréversible.
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

export default MembersPage;