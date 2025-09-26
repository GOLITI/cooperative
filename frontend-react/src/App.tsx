import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material'
import { Layout } from './components/Layout/Layout'
import { AuthProvider } from './contexts/AuthContext'
import { LoginPage } from './pages/Auth/LoginPage'
import { DashboardPage } from './pages/Dashboard/DashboardPage'
import { MembersPage } from './pages/Members/MembersPage'
import { InventoryPage } from './pages/Inventory/InventoryPage'
import { SalesPage } from './pages/Sales/SalesPage'
import { FinancePage } from './pages/Finance/FinancePage'
import { ReportsPage } from './pages/Reports/ReportsPage'
import { ProtectedRoute } from './components/Auth/ProtectedRoute'

// Configuration du client React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
    },
  },
})

// Thème Material-UI personnalisé pour la coopérative
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2', // Bleu coopératif
      light: '#42a5f5',
      dark: '#1565c0',
    },
    secondary: {
      main: '#388e3c', // Vert agriculture
      light: '#66bb6a',
      dark: '#2e7d32',
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
    },
    h5: {
      fontWeight: 500,
    },
  },
  components: {
    MuiAppBar: {
      defaultProps: {
        elevation: 1,
      },
    },
    MuiCard: {
      defaultProps: {
        elevation: 2,
      },
    },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <AuthProvider>
          <Router>
            <Routes>
              {/* Route de connexion */}
              <Route path="/login" element={<LoginPage />} />
              
              {/* Routes protégées avec layout */}
              <Route path="/" element={
                <ProtectedRoute>
                  <Layout />
                </ProtectedRoute>
              }>
                <Route index element={<Navigate to="/dashboard" replace />} />
                <Route path="dashboard" element={<DashboardPage />} />
                <Route path="members/*" element={<MembersPage />} />
                <Route path="inventory/*" element={<InventoryPage />} />
                <Route path="sales/*" element={<SalesPage />} />
                <Route path="finance/*" element={<FinancePage />} />
                <Route path="reports/*" element={<ReportsPage />} />
              </Route>
              
              {/* Route par défaut */}
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </Router>
        </AuthProvider>
      </ThemeProvider>
    </QueryClientProvider>
  )
}

export default App
