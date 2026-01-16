import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { ReactNode } from 'react'

interface LayoutProps {
  children: ReactNode
}

export function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const { user, logout } = useAuth()

  const navLinks = [
    { path: '/dashboard', label: 'Dashboard' },
    { path: '/assets', label: 'Assets' },
    { path: '/missions', label: 'Missions' },
    { path: '/users', label: 'Utilisateurs' },
    { path: '/reports', label: 'Rapports' },
  ]

  // Add admin link if user is admin
  if (user?.role === 'admin') {
    navLinks.push({ path: '/adminpanel', label: 'Admin' })
  }

  const handleLogout = async () => {
    try {
      await logout()
    } catch (error) {
      console.error('Logout failed:', error)
    }
  }

  return (
    <div className="shell">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark">PSSTOCK</span>
          <span className="brand-sub">ops board</span>
        </div>

        <nav className="nav-links">
          {navLinks.map((link) => (
            <Link
              key={link.path}
              to={link.path}
              className={`nav-link ${location.pathname === link.path ? 'active' : ''}`}
            >
              {link.label}
            </Link>
          ))}
        </nav>

        <div className="top-actions">
          <div className="chip">
            <span
              className="icon-btn"
              style={{ width: '34px', height: '34px', boxShadow: 'none' }}
            >
              {user?.name?.charAt(0) || user?.username?.charAt(0) || 'U'}
            </span>
            <div style={{ display: 'flex', flexDirection: 'column', lineHeight: 1.2 }}>
              <span style={{ color: 'var(--text)' }}>
                {user?.name || user?.username}
              </span>
              <small style={{ color: 'var(--muted)', fontWeight: 600 }}>
                {user?.role?.toUpperCase()}
              </small>
            </div>
          </div>
          <button className="btn btn-secondary btn-sm" onClick={handleLogout}>
            Déconnexion
          </button>
        </div>
      </header>

      <main className="content">{children}</main>
    </div>
  )
}
