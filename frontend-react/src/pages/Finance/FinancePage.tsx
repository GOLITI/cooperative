import React from 'react'
import { Box, Typography, Paper, Button } from '@mui/material'
import { Add as AddIcon } from '@mui/icons-material'

export const FinancePage: React.FC = () => {
  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <div>
          <Typography variant="h4" component="h1" gutterBottom>
            Gestion Financière
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Gérez les comptes, transactions et prêts de la coopérative
          </Typography>
        </div>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          size="large"
        >
          Nouvelle Transaction
        </Button>
      </Box>

      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" color="text.secondary" align="center">
          Interface de gestion financière en cours de développement...
        </Typography>
        <Typography variant="body1" color="text.secondary" align="center" sx={{ mt: 2 }}>
          Cette page permettra de :
        </Typography>
        <ul style={{ marginTop: '16px', color: '#666' }}>
          <li>Consulter les comptes bancaires et leur solde</li>
          <li>Enregistrer les transactions financières</li>
          <li>Gérer les prêts et crédits accordés</li>
          <li>Suivre les comptes d'épargne des membres</li>
          <li>Générer des états financiers</li>
          <li>Analyser les flux de trésorerie</li>
        </ul>
      </Paper>
    </Box>
  )
}