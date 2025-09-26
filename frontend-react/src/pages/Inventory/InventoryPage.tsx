import React from 'react'
import { Box, Typography, Paper, Button } from '@mui/material'
import { Add as AddIcon } from '@mui/icons-material'

export const InventoryPage: React.FC = () => {
  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <div>
          <Typography variant="h4" component="h1" gutterBottom>
            Gestion de l'Inventaire
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Gérez les produits et équipements de la coopérative
          </Typography>
        </div>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          size="large"
        >
          Nouveau Produit
        </Button>
      </Box>

      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" color="text.secondary" align="center">
          Interface de gestion de l'inventaire en cours de développement...
        </Typography>
        <Typography variant="body1" color="text.secondary" align="center" sx={{ mt: 2 }}>
          Cette page permettra de :
        </Typography>
        <ul style={{ marginTop: '16px', color: '#666' }}>
          <li>Consulter le stock complet des produits</li>
          <li>Ajouter de nouveaux produits au catalogue</li>
          <li>Suivre les mouvements de stock en temps réel</li>
          <li>Gérer les alertes de stock faible</li>
          <li>Organiser les produits par catégories</li>
          <li>Importer/Exporter les données d'inventaire</li>
        </ul>
      </Paper>
    </Box>
  )
}