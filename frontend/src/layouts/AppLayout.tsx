import type { ReactNode } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'

type AppLayoutProps = {
  children: ReactNode
}

const links = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/assets', label: 'Assets' },
  { to: '/missions', label: 'Missions' },
  { to: '/users', label: 'Utilisateurs' },
  { to: '/reports', label: 'Rapports' },
  { to: '/adminpanel', label: 'Admin' },
]

export default function AppLayout({ children }: AppLayoutProps) {
  const navigate = useNavigate()

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
            <span id="userAvatar" className="icon-btn user-avatar">A</span>
            <div className="user-meta">
              <span id="userName" className="user-name">Admin</span>
              <small id="userRole" className="user-role">ADMIN</small>
            </div>
          </div>
          <button className="btn btn-secondary btn-sm" onClick={() => navigate('/login')}>
            Deconnexion
          </button>
        </div>
      </header>

      <main className="content">{children}</main>
    </div>
  )
}