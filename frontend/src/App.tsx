import { Navigate, Route, Routes, useLocation } from 'react-router-dom'
import AdminPage from './pages/AdminPage'
import AssetsPage from './pages/AssetsPage'
import DashboardPage from './pages/DashboardPage'
import LoginPage from './pages/LoginPage'
import PlaceholderPage from './pages/PlaceholderPage'

function App() {
  const location = useLocation()

  if (location.pathname === '/') {
    return <Navigate to="/login" replace />
  }

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/dashboard" element={<DashboardPage />} />
      <Route path="/assets" element={<AssetsPage />} />
      <Route path="/adminpanel" element={<AdminPage />} />
      <Route path="/missions" element={<PlaceholderPage title="Missions" subtitle="Pilotage des operations et affectations." />} />
      <Route path="/users" element={<PlaceholderPage title="Utilisateurs" subtitle="Gestion des comptes et permissions." />} />
      <Route path="/reports" element={<PlaceholderPage title="Rapports" subtitle="KPI, exports et analyses de conformite." />} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}

export default App
