import React from 'react'
import { Box, Typography, Paper, Button } from '@mui/material'
import { Assessment as AssessmentIcon } from '@mui/icons-material'

export const ReportsPage: React.FC = () => {
  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <div>
          <Typography variant="h4" component="h1" gutterBottom>
            Rapports et Analyses
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Consultez les rapports statistiques de la coopérative
          </Typography>
        </div>
        <Button
          variant="contained"
          startIcon={<AssessmentIcon />}
          size="large"
        >
          Nouveau Rapport
        </Button>
      </Box>

      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" color="text.secondary" align="center">
          Interface de rapports en cours de développement...
        </Typography>
        <Typography variant="body1" color="text.secondary" align="center" sx={{ mt: 2 }}>
          Cette page permettra de :
        </Typography>
        <ul style={{ marginTop: '16px', color: '#666' }}>
          <li>Générer des rapports personnalisables</li>
          <li>Visualiser les données avec des graphiques</li>
          <li>Exporter les rapports en PDF/Excel</li>
          <li>Programmer l'envoi automatique de rapports</li>
          <li>Analyser les tendances sur plusieurs périodes</li>
          <li>Créer des tableaux de bord dynamiques</li>
        </ul>
      </Paper>
    </Box>
  )
}