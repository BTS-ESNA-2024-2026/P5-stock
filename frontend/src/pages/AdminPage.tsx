import { useCallback, useEffect, useMemo, useState } from 'react'
import AppLayout from '../layouts/AppLayout'
import { fetchUsers, fetchRoles } from '../api/admin'
import type { User, Role } from '../types'

export default function AdminPage() {
  const [query, setQuery] = useState('')
  const [users, setUsers] = useState<User[]>([])
  const [roles, setRoles] = useState<Role[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const loadData = useCallback(async () => {
    setLoading(true)
    try {
      const [u, r] = await Promise.all([fetchUsers(), fetchRoles()])
      setUsers(u)
      setRoles(r)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur de chargement')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { loadData() }, [loadData])

  const visibleUsers = useMemo(() => {
    return users.filter((user) => {
      const row = `${user.username} ${user.name ?? ''} ${user.role_name ?? ''}`.toLowerCase()
      return row.includes(query.toLowerCase())
    })
  }, [users, query])

  const activeCount = users.filter((u) => u.active).length

  return (
    <AppLayout>
      <section className="page-hero">
        <div className="page-meta">
          <span className="brand-sub">Administration</span>
          <div className="title">Centre de controle</div>
          <div className="subtitle">Superviser les roles, utilisateurs et la conformite du systeme.</div>
        </div>
        <div className="controls-row">
          <button className="btn btn-secondary btn-sm" onClick={loadData} disabled={loading}>
            {loading ? 'Chargement...' : '&#8635; Actualiser'}
          </button>
        </div>
      </section>

      {error ? <div className="alert alert-danger">{error}</div> : null}

      <section className="stats-grid">
        <div className="stat-card success">
          <h3>Utilisateurs actifs</h3>
          <div className="stat-value">{activeCount}</div>
          <div className="stat-meta">Sur {users.length} total</div>
        </div>
        <div className="stat-card warning">
          <h3>Roles</h3>
          <div className="stat-value">{roles.length}</div>
          <div className="stat-meta">Profils disponibles</div>
        </div>
        <div className="stat-card">
          <h3>Utilisateurs inactifs</h3>
          <div className="stat-value">{users.length - activeCount}</div>
          <div className="stat-meta">Comptes desactives</div>
        </div>
      </section>

      <section className="data-table">
        <div className="table-header">
          <h3>Utilisateurs</h3>
          <div className="search-bar">
            <span className="search-icon">&#9776;</span>
            <input
              type="text"
              placeholder="Rechercher un utilisateur"
              aria-label="Recherche utilisateur"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>
        </div>
        <table>
          <thead>
            <tr>
              <th>Username</th>
              <th>Nom</th>
              <th>Role</th>
              <th>Status</th>
              <th>Cree le</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={5} className="text-center">Chargement...</td></tr>
            ) : visibleUsers.length === 0 ? (
              <tr><td colSpan={5} className="text-center">Aucun utilisateur correspondant.</td></tr>
            ) : (
              visibleUsers.map((user) => (
                <tr key={user.id}>
                  <td>{user.username}</td>
                  <td>{user.name ?? '—'}</td>
                  <td><span className="badge badge-info">{user.role_name?.toUpperCase() ?? '—'}</span></td>
                  <td>
                    <span className={`badge ${user.active ? 'badge-success' : 'badge-danger'}`}>
                      {user.active ? 'Actif' : 'Inactif'}
                    </span>
                  </td>
                  <td>{new Date(user.DA).toLocaleDateString('fr-FR')}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </section>

      <section className="panel">
        <div className="panel-header">
          <div className="panel-title">Roles du systeme</div>
        </div>
        <div className="stats-grid">
          {roles.map((role) => (
            <div key={role.id} className="stat-card">
              <h3>{role.name.toUpperCase()}</h3>
              <div className="stat-meta">{role.desc ?? '—'}</div>
              <div className="stat-value" style={{ fontSize: '1.2rem' }}>
                {users.filter((u) => u.group_id === role.id).length} utilisateur(s)
              </div>
            </div>
          ))}
        </div>
      </section>
    </AppLayout>
  )
}