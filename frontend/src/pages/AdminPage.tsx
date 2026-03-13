import { useState } from 'react'
import AppLayout from '../layouts/AppLayout'

export default function AdminPage() {
  const [query, setQuery] = useState('')

  const users = [
    { name: 'Jean Dupont', role: 'ADMIN', status: 'Actif', lastLogin: '2026-03-13 10:22' },
    { name: 'Marie Martin', role: 'OPERATEUR', status: 'En attente', lastLogin: '2026-03-12 21:11' },
    { name: 'Lea Bernard', role: 'VIEWER', status: 'Actif', lastLogin: '2026-03-12 08:40' },
  ]

  const visibleUsers = users.filter((user) => {
    const row = `${user.name} ${user.role} ${user.status}`.toLowerCase()
    return row.includes(query.toLowerCase())
  })

  return (
    <AppLayout>
      <section className="page-hero">
        <div className="page-meta">
          <span className="brand-sub">Administration</span>
          <div className="title">Centre de controle</div>
          <div className="subtitle">Superviser les roles, utilisateurs et la conformite du systeme.</div>
        </div>
        <div className="controls-row">
          <span className="chip">Audit actif</span>
        </div>
      </section>

      <section className="stats-grid">
        <div className="stat-card success">
          <h3>Utilisateurs actifs</h3>
          <div className="stat-value">52</div>
          <div className="stat-meta">Connectes dans les 24h</div>
        </div>
        <div className="stat-card warning">
          <h3>Roles</h3>
          <div className="stat-value">5</div>
          <div className="stat-meta">Profils disponibles</div>
        </div>
        <div className="stat-card">
          <h3>Demandes en attente</h3>
          <div className="stat-value">7</div>
          <div className="stat-meta">Approvals / creations</div>
        </div>
        <div className="stat-card danger">
          <h3>Alertes securite</h3>
          <div className="stat-value">2</div>
          <div className="stat-meta">A traiter</div>
        </div>
      </section>

      <section className="panel">
        <div className="panel-header">
          <div className="panel-title">Actions rapides</div>
        </div>
        <div className="controls-row">
          <button className="btn btn-primary btn-sm">+ Nouvel utilisateur</button>
          <button className="btn btn-secondary btn-sm">+ Nouveau role</button>
          <button className="btn btn-secondary btn-sm">Exporter journal</button>
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
              onChange={(event) => setQuery(event.target.value)}
            />
          </div>
        </div>
        <table>
          <thead>
            <tr>
              <th>Nom</th>
              <th>Role</th>
              <th>Status</th>
              <th>Derniere connexion</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {visibleUsers.map((user) => (
              <tr key={user.name}>
                <td>{user.name}</td>
                <td><span className="badge badge-info">{user.role}</span></td>
                <td>
                  <span className={`badge ${user.status === 'Actif' ? 'badge-success' : 'badge-warning'}`}>
                    {user.status}
                  </span>
                </td>
                <td>{user.lastLogin}</td>
                <td className="flex gap-1">
                  <button className="btn btn-sm btn-secondary">Edit</button>
                  <button className="btn btn-sm btn-danger">Suspendre</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </AppLayout>
  )
}