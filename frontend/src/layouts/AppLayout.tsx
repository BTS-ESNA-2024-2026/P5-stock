import type { ReactNode } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

type AppLayoutProps = {
  children: ReactNode
}

type NavItem = { to: string; label: string; minRole: Role }
type Role = 'viewer' | 'user' | 'secure_user' | 'technician' | 'admin'

const ROLE_RANK: Record<Role, number> = {
  viewer: 0,
  user: 1,
  secure_user: 2,
  technician: 3,
  admin: 4,
}

const links: NavItem[] = [
  { to: '/dashboard', label: 'Dashboard', minRole: 'viewer' },
  { to: '/assets', label: 'Assets', minRole: 'user' },
  { to: '/asset-types', label: 'Types', minRole: 'technician' },
  { to: '/bases', label: 'Bases', minRole: 'technician' },
  { to: '/missions', label: 'Missions', minRole: 'technician' },
  { to: '/reports', label: 'Rapports', minRole: 'technician' },
  { to: '/logs', label: 'Logs', minRole: 'technician' },
  { to: '/adminpanel', label: 'Admin', minRole: 'admin' },
]

export default function AppLayout({ children }: AppLayoutProps) {
  const navigate = useNavigate()
  const { user, logout } = useAuth()

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  const initial = user?.name?.charAt(0).toUpperCase() ?? user?.username?.charAt(0).toUpperCase() ?? '?'
  const userRank = user?.role && user.role in ROLE_RANK ? ROLE_RANK[user.role as Role] : -1
  const visibleLinks = links.filter((l) => userRank >= ROLE_RANK[l.minRole])

  return (
    <div className="shell">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark">PSSTOCK</span>
          <span className="brand-sub">ops board</span>
        </div>

        <nav className="nav-links">
          {visibleLinks.map((link) => (
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
