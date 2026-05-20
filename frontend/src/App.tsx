import { Navigate, Route, Routes } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import AdminPage from './pages/AdminPage'
import AssetTypesPage from './pages/AssetTypesPage'
import AssetsPage from './pages/AssetsPage'
import BasesPage from './pages/BasesPage'
import DashboardPage from './pages/DashboardPage'
import LoginPage from './pages/LoginPage'
import LogsPage from './pages/LogsPage'
import MissionsPage from './pages/MissionsPage'
import ProfilePage from './pages/ProfilePage'
import ReportsPage from './pages/ReportsPage'

type Role = 'viewer' | 'user' | 'secure_user' | 'technician' | 'admin'

const ROLE_RANK: Record<Role, number> = {
  viewer: 0,
  user: 1,
  secure_user: 2,
  technician: 3,
  admin: 4,
}

function ProtectedRoute({ children, minRole = 'viewer' }: { children: React.ReactNode; minRole?: Role }) {
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

  const userRank = user.role && user.role in ROLE_RANK ? ROLE_RANK[user.role as Role] : -1
  if (userRank < ROLE_RANK[minRole]) {
    return <Navigate to="/dashboard" replace />
  }

  return <>{children}</>
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
      <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
      <Route path="/assets" element={<ProtectedRoute minRole="user"><AssetsPage /></ProtectedRoute>} />
      <Route path="/asset-types" element={<ProtectedRoute minRole="technician"><AssetTypesPage /></ProtectedRoute>} />
      <Route path="/bases" element={<ProtectedRoute minRole="technician"><BasesPage /></ProtectedRoute>} />
      <Route path="/missions" element={<ProtectedRoute minRole="technician"><MissionsPage /></ProtectedRoute>} />
      <Route path="/reports" element={<ProtectedRoute minRole="technician"><ReportsPage /></ProtectedRoute>} />
      <Route path="/logs" element={<ProtectedRoute minRole="technician"><LogsPage /></ProtectedRoute>} />
      <Route path="/adminpanel" element={<ProtectedRoute minRole="admin"><AdminPage /></ProtectedRoute>} />
      <Route path="/users" element={<Navigate to="/adminpanel" replace />} />
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}

export default App
