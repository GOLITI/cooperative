import React from 'react'
import { Box, Typography, Paper, Button } from '@mui/material'
import { Add as AddIcon } from '@mui/icons-material'

export const SalesPage: React.FC = () => {
  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <div>
          <Typography variant="h4" component="h1" gutterBottom>
            Gestion des Ventes
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Gérez les commandes et transactions commerciales
          </Typography>
        </div>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          size="large"
        >
          Nouvelle Vente
        </Button>
      </Box>

      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" color="text.secondary" align="center">
          Interface de gestion des ventes en cours de développement...
        </Typography>
        <Typography variant="body1" color="text.secondary" align="center" sx={{ mt: 2 }}>
          Cette page permettra de :
        </Typography>
        <ul style={{ marginTop: '16px', color: '#666' }}>
          <li>Enregistrer de nouvelles commandes clients</li>
          <li>Suivre le statut des commandes en cours</li>
          <li>Gérer les retours et échanges</li>
          <li>Consulter l'historique des ventes</li>
          <li>Générer des factures et devis</li>
          <li>Analyser les tendances de vente</li>
        </ul>
      </Paper>
    </Box>
  )
}