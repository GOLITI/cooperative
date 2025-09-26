import React from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Avatar,
} from '@mui/material'
import {
  People as PeopleIcon,
  Inventory as InventoryIcon,
  TrendingUp as TrendingUpIcon,
  AccountBalance as AccountBalanceIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material'

// Type pour les statistiques du dashboard
interface DashboardStats {
  members: {
    total: number
    active: number
    new_this_month: number
  }
  inventory: {
    total_products: number
    low_stock_alerts: number
    total_value: number
  }
  sales: {
    today: number
    this_month: number
    growth_percentage: number
  }
  finance: {
    total_balance: number
    pending_loans: number
    recent_transactions: Array<{
      id: number
      description: string
      amount: number
      date: string
      type: 'credit' | 'debit'
    }>
  }
}

// Composant de carte statistique
interface StatCardProps {
  title: string
  value: string | number
  subtitle?: string
  icon: React.ReactNode
  color: 'primary' | 'secondary' | 'success' | 'warning' | 'error'
  progress?: number
}

const StatCard: React.FC<StatCardProps> = ({ 
  title, 
  value, 
  subtitle, 
  icon, 
  color, 
  progress 
}) => (
  <Card elevation={2}>
    <CardContent>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <Avatar sx={{ bgcolor: `${color}.main`, mr: 2 }}>
          {icon}
        </Avatar>
        <Box>
          <Typography variant="h4" component="div" color={`${color}.main`}>
            {typeof value === 'number' ? value.toLocaleString() : value}
          </Typography>
          <Typography variant="h6" color="text.secondary">
            {title}
          </Typography>
        </Box>
      </Box>
      {subtitle && (
        <Typography variant="body2" color="text.secondary">
          {subtitle}
        </Typography>
      )}
      {progress !== undefined && (
        <Box sx={{ mt: 1 }}>
          <LinearProgress 
            variant="determinate" 
            value={progress} 
            color={color}
          />
          <Typography variant="caption" color="text.secondary">
            {progress}% de l'objectif
          </Typography>
        </Box>
      )}
    </CardContent>
  </Card>
)

export const DashboardPage: React.FC = () => {
  // Simulation de données pour le développement
  // Dans un vrai projet, ceci serait remplacé par un appel API
  const dashboardData: DashboardStats = {
    members: {
      total: 247,
      active: 198,
      new_this_month: 12
    },
    inventory: {
      total_products: 156,
      low_stock_alerts: 8,
      total_value: 45650
    },
    sales: {
      today: 2340,
      this_month: 78650,
      growth_percentage: 15.3
    },
    finance: {
      total_balance: 125430,
      pending_loans: 5,
      recent_transactions: [
        {
          id: 1,
          description: "Vente produits agricoles",
          amount: 1250,
          date: "2024-01-15",
          type: "credit"
        },
        {
          id: 2,
          description: "Achat équipement",
          amount: -850,
          date: "2024-01-14", 
          type: "debit"
        },
        {
          id: 3,
          description: "Remboursement prêt",
          amount: 500,
          date: "2024-01-13",
          type: "credit"
        }
      ]
    }
  }

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Tableau de Bord
      </Typography>
      <Typography variant="subtitle1" color="text.secondary" gutterBottom>
        Vue d'ensemble de votre coopérative agricole
      </Typography>

      {/* Cartes statistiques principales */}
      <Box sx={{ 
        display: 'grid', 
        gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr 1fr' }, 
        gap: 3, 
        mb: 4 
      }}>
        <StatCard
          title="Membres Actifs"
          value={dashboardData.members.active}
          subtitle={`${dashboardData.members.new_this_month} nouveaux ce mois`}
          icon={<PeopleIcon />}
          color="primary"
          progress={Math.round((dashboardData.members.active / dashboardData.members.total) * 100)}
        />

        <StatCard
          title="Produits en Stock"
          value={dashboardData.inventory.total_products}
          subtitle={`${dashboardData.inventory.low_stock_alerts} alertes stock faible`}
          icon={<InventoryIcon />}
          color="secondary"
        />

        <StatCard
          title="Ventes du Mois"
          value={`€${dashboardData.sales.this_month.toLocaleString()}`}
          subtitle={`+${dashboardData.sales.growth_percentage}% vs mois dernier`}
          icon={<TrendingUpIcon />}
          color="success"
        />

        <StatCard
          title="Solde Total"
          value={`€${dashboardData.finance.total_balance.toLocaleString()}`}
          subtitle={`${dashboardData.finance.pending_loans} prêts en cours`}
          icon={<AccountBalanceIcon />}
          color="warning"
        />
      </Box>

      {/* Section des alertes et activités récentes */}
      <Box sx={{ 
        display: 'grid', 
        gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, 
        gap: 3 
      }}>
        {/* Alertes */}
        <Card elevation={2}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Alertes et Notifications
            </Typography>
            <List>
              <ListItem>
                <ListItemIcon>
                  <WarningIcon color="warning" />
                </ListItemIcon>
                <ListItemText
                  primary="Stock faible"
                  secondary="8 produits nécessitent un réapprovisionnement"
                />
                <Chip label="8" color="warning" size="small" />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <CheckCircleIcon color="success" />
                </ListItemIcon>
                <ListItemText
                  primary="Paiements à jour"
                  secondary="Tous les membres sont à jour de cotisation"
                />
                <Chip label="✓" color="success" size="small" />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <AccountBalanceIcon color="info" />
                </ListItemIcon>
                <ListItemText
                  primary="Prêts en attente"
                  secondary="5 demandes de prêt nécessitent approbation"
                />
                <Chip label="5" color="info" size="small" />
              </ListItem>
            </List>
          </CardContent>
        </Card>

        {/* Transactions récentes */}
        <Card elevation={2}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Transactions Récentes
            </Typography>
            <List>
              {dashboardData.finance.recent_transactions.map((transaction) => (
                <ListItem key={transaction.id}>
                  <ListItemIcon>
                    <Avatar 
                      sx={{ 
                        bgcolor: transaction.type === 'credit' ? 'success.main' : 'error.main',
                        width: 32,
                        height: 32
                      }}
                    >
                      {transaction.type === 'credit' ? '+' : '-'}
                    </Avatar>
                  </ListItemIcon>
                  <ListItemText
                    primary={transaction.description}
                    secondary={new Date(transaction.date).toLocaleDateString('fr-FR')}
                  />
                  <Typography 
                    variant="body2" 
                    color={transaction.type === 'credit' ? 'success.main' : 'error.main'}
                    fontWeight="bold"
                  >
                    {transaction.type === 'credit' ? '+' : ''}€{Math.abs(transaction.amount)}
                  </Typography>
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      </Box>
    </Box>
  )
}