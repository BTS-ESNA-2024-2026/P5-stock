import { Navigate, Route, Routes } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import AdminPage from './pages/AdminPage'
import AssetsPage from './pages/AssetsPage'
import DashboardPage from './pages/DashboardPage'
import LoginPage from './pages/LoginPage'
import MissionsPage from './pages/MissionsPage'
import PlaceholderPage from './pages/PlaceholderPage'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="shell" style={{ display: 'grid', placeItems: 'center', minHeight: '100vh' }}>
        <span className="chip">Chargement...</span>
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
      <Route path="/assets" element={<ProtectedRoute><AssetsPage /></ProtectedRoute>} />
      <Route path="/missions" element={<ProtectedRoute><MissionsPage /></ProtectedRoute>} />
      <Route path="/adminpanel" element={<ProtectedRoute><AdminPage /></ProtectedRoute>} />
      <Route path="/users" element={<ProtectedRoute><PlaceholderPage title="Utilisateurs" subtitle="Gestion des comptes et permissions." /></ProtectedRoute>} />
      <Route path="/reports" element={<ProtectedRoute><PlaceholderPage title="Rapports" subtitle="KPI, exports et analyses de conformite." /></ProtectedRoute>} />
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}

export default App
