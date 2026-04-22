import { useState, useEffect, useCallback } from 'react'
import AppLayout from '../layouts/AppLayout'
import { fetchAssets } from '../api/assets'
import { fetchMissions } from '../api/missions'
import { fetchLogs } from '../api/dashboard'
import type { Asset, Mission, LogEntry } from '../types'

export default function DashboardPage() {
  const [lastRefresh, setLastRefresh] = useState(new Date())
  const [assets, setAssets] = useState<Asset[]>([])
  const [missions, setMissions] = useState<Mission[]>([])
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [loading, setLoading] = useState(true)

  const loadData = useCallback(async () => {
    setLoading(true)
    try {
      const [a, m, l] = await Promise.all([fetchAssets(), fetchMissions(), fetchLogs()])
      setAssets(a)
      setMissions(m)
      setLogs(l)
      setLastRefresh(new Date())
    } catch {
      // silently fail — data will appear empty
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { loadData() }, [loadData])

  const stockCount = assets.filter((a) => a.status === 'STOCK').length
  const transitCount = assets.filter((a) => a.status === 'TRANSIT').length
  const activeMissions = missions.length
  const availability = assets.length > 0
    ? Math.round((stockCount / assets.length) * 100)
    : 0

  const stats = [
    { title: 'Assets totaux', value: String(assets.length), meta: `${stockCount} en stock`, variant: '' },
    { title: 'Missions', value: String(activeMissions), meta: 'Enregistrees', variant: 'warning' },
    { title: 'Disponibilite stock', value: `${availability}%`, meta: 'Niveau global', variant: 'success' },
    { title: 'En transit', value: String(transitCount), meta: 'Mouvements', variant: 'danger' },
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
          <button className="icon-btn" onClick={loadData} title="Actualiser" disabled={loading}>
            &#8635;
          </button>
          <button className="btn btn-primary btn-sm" onClick={loadData} disabled={loading}>
            {loading ? 'Chargement...' : 'Actualiser'}
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
          <span className="chip">{logs.length} entree(s)</span>
        </div>
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Action</th>
              <th>Asset</th>
              <th>Description</th>
            </tr>
          </thead>
          <tbody>
            {logs.length === 0 ? (
              <tr>
                <td colSpan={4} className="text-center">
                  {loading ? 'Chargement...' : 'Aucune activite recente.'}
                </td>
              </tr>
            ) : (
              logs.slice(0, 20).map((log) => (
                <tr key={log.id}>
                  <td>{new Date(log.D).toLocaleString('fr-FR')}</td>
                  <td><span className="badge badge-info">{log.action}</span></td>
                  <td>{log.asset_name ?? '—'}</td>
                  <td>{log.description ?? '—'}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </section>
    </AppLayout>
  )
}