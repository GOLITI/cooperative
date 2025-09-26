import React from 'react'
import { Box, Typography, Paper, Button } from '@mui/material'
import { Add as AddIcon } from '@mui/icons-material'

export const MembersPage: React.FC = () => {
  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <div>
          <Typography variant="h4" component="h1" gutterBottom>
            Gestion des Membres
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Gérez les membres de votre coopérative agricole
          </Typography>
        </div>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          size="large"
        >
          Nouveau Membre
        </Button>
      </Box>

      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" color="text.secondary" align="center">
          Interface de gestion des membres en cours de développement...
        </Typography>
        <Typography variant="body1" color="text.secondary" align="center" sx={{ mt: 2 }}>
          Cette page permettra de :
        </Typography>
        <ul style={{ marginTop: '16px', color: '#666' }}>
          <li>Visualiser la liste complète des membres</li>
          <li>Ajouter de nouveaux membres à la coopérative</li>
          <li>Modifier les informations des membres existants</li>
          <li>Gérer l'historique d'adhésion et les cotisations</li>
          <li>Consulter les statistiques de participation</li>
        </ul>
      </Paper>
    </Box>
  )
}