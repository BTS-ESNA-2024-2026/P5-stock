import { useState } from 'react'
import AppLayout from '../layouts/AppLayout'

export default function DashboardPage() {
  const [lastRefresh, setLastRefresh] = useState(new Date())

  const stats = [
    { title: 'Assets operationnels', value: '162', meta: 'Affectables', variant: '' },
    { title: 'Missions en cours', value: '14', meta: 'Zones actives', variant: 'warning' },
    { title: 'Disponibilite stock', value: '92%', meta: 'Niveau global', variant: 'success' },
    { title: 'Alertes critiques', value: '3', meta: 'A traiter', variant: 'danger' },
  ]

  const activities = [
    { date: '2026-03-13 09:25', action: 'Affectation', detail: 'Drone de surveillance assigne a Mission Ares' },
    { date: '2026-03-13 08:48', action: 'Maintenance', detail: 'Camion tactique passe en maintenance preventive' },
    { date: '2026-03-12 21:10', action: 'Controle', detail: 'Inventaire nocturne termine sans ecart' },
  ]

  return (
    <AppLayout>
      <section className="page-hero">
        <div className="page-meta">
          <span className="brand-sub">Vue d'ensemble</span>
          <div className="title">Tableau de bord</div>
          <div className="subtitle">Synthese en temps reel des missions et assets.</div>
        </div>
        <div className="controls-row">
          <button className="icon-btn" onClick={() => setLastRefresh(new Date())} title="Actualiser">
            &#8635;
          </button>
          <button className="btn btn-primary btn-sm" onClick={() => setLastRefresh(new Date())}>
            Actualiser
          </button>
        </div>
      </section>

      <section className="panel">
        <div className="panel-header">
          <div className="panel-title">Indicateurs cle</div>
          <span className="chip">MAJ: {lastRefresh.toLocaleTimeString('fr-FR')}</span>
        </div>
        <div className="stats-grid">
          {stats.map((stat) => (
            <div key={stat.title} className={`stat-card ${stat.variant}`.trim()}>
              <h3>{stat.title}</h3>
              <div className="stat-value">{stat.value}</div>
              <div className="stat-meta">{stat.meta}</div>
            </div>
          ))}
        </div>
      </section>

      <section className="data-table">
        <div className="table-header">
          <h3>Activite recente</h3>
          <span className="chip">Live feed</span>
        </div>
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Action</th>
              <th>Description</th>
            </tr>
          </thead>
          <tbody>
            {activities.map((activity) => (
              <tr key={`${activity.date}-${activity.action}`}>
                <td>{activity.date}</td>
                <td>{activity.action}</td>
                <td>{activity.detail}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </AppLayout>
  )
}