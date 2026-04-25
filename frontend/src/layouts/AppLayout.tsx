import type { ReactNode } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

type AppLayoutProps = {
  children: ReactNode
}

const links = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/assets', label: 'Assets' },
  { to: '/asset-types', label: 'Types' },
  { to: '/bases', label: 'Bases' },
  { to: '/missions', label: 'Missions' },
  { to: '/users', label: 'Utilisateurs' },
  { to: '/reports', label: 'Rapports' },
  { to: '/adminpanel', label: 'Admin' },
]

export default function AppLayout({ children }: AppLayoutProps) {
  const navigate = useNavigate()
  const { user, logout } = useAuth()

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  const initial = user?.name?.charAt(0).toUpperCase() ?? user?.username?.charAt(0).toUpperCase() ?? '?'

  return (
    <div className="shell">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark">PSSTOCK</span>
          <span className="brand-sub">ops board</span>
        </div>

        <nav className="nav-links">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
            >
              {link.label}
            </NavLink>
          ))}
        </nav>

        <div className="top-actions">
          <div className="chip">
            <span className="icon-btn user-avatar">{initial}</span>
            <div className="user-meta">
              <span className="user-name">{user?.name ?? user?.username ?? '—'}</span>
              <small className="user-role">{user?.role?.toUpperCase() ?? ''}</small>
            </div>
          </div>
          <button className="btn btn-secondary btn-sm" onClick={handleLogout}>
            Deconnexion
          </button>
        </div>
      </header>

      <main className="content">{children}</main>
    </div>
  )
}