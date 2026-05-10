import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import AppLayout from '../layouts/AppLayout'
import { fetchAssets } from '../api/assets'
import { fetchMissions } from '../api/missions'
import { fetchLogs } from '../api/dashboard'
import { useAuth } from '../context/AuthContext'
import { formatDateTime, formatTime } from '../utils/dates'
import type { Asset, Mission, LogEntry, LogKind } from '../types'

const KIND_BADGE: Record<LogKind, string> = {
  asset: 'badge-success',
  mission: 'badge-info',
  admin: 'badge-warning',
}

const KIND_LABEL: Record<LogKind, string> = {
  asset: 'Asset',
  mission: 'Mission',
  admin: 'Utilisateur',
}

const KIND_ROUTE: Record<LogKind, string> = {
  asset: '/assets',
  mission: '/missions',
  admin: '/adminpanel',
}

export default function DashboardPage() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const [lastRefresh, setLastRefresh] = useState(new Date())
  const [assets, setAssets] = useState<Asset[]>([])
  const [missions, setMissions] = useState<Mission[]>([])
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const loadData = useCallback(async () => {
    setLoading(true)
    setError('')
    // Run independently so a partial failure (e.g. user has no admin_panel
    // perm so /api/missions returns) doesn't blank out the rest of the page.
    const results = await Promise.allSettled([fetchAssets(), fetchMissions(), fetchLogs()])
    const [a, m, l] = results
    if (a.status === 'fulfilled') setAssets(a.value)
    if (m.status === 'fulfilled') setMissions(m.value)
    if (l.status === 'fulfilled') setLogs(l.value)
    const failed = results.filter((r) => r.status === 'rejected')
    if (failed.length > 0) {
      const reason = (failed[0] as PromiseRejectedResult).reason
      setError(reason instanceof Error ? reason.message : 'Erreur de chargement')
    }
    setLastRefresh(new Date())
    setLoading(false)
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

  // Roles that may follow a log row to its source page. Lower roles see the
  // activity feed but the corresponding pages are gated.
  const canOpen: Record<LogKind, boolean> = {
    asset: ['user', 'secure_user', 'technician', 'admin'].includes(user?.role ?? ''),
    mission: ['technician', 'admin'].includes(user?.role ?? ''),
    admin: user?.role === 'admin',
  }

  return (
    <AppLayout>
      <section className="page-hero">
        <div className="page-meta">
          <span className="brand-sub">Vue d'ensemble</span>
          <div className="title">Tableau de bord</div>
          <div className="subtitle">Synthese en temps reel des missions et assets.</div>
        </div>
        <div className="controls-row">
          <button className="btn btn-secondary btn-sm" onClick={loadData} disabled={loading}>
            {loading ? 'Chargement...' : '↻ Actualiser'}
          </button>
        </div>
      </section>

      {error ? <div className="alert alert-danger">{error}</div> : null}

      <section className="panel">
        <div className="panel-header">
          <div className="panel-title">Indicateurs cle</div>
          <span className="chip">MAJ: {formatTime(lastRefresh)}</span>
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
              <th>Source</th>
              <th>Action</th>
              <th>Cible</th>
              <th>Description</th>
            </tr>
          </thead>
          <tbody>
            {logs.length === 0 ? (
              <tr>
                <td colSpan={5} className="text-center">
                  {loading ? 'Chargement...' : 'Aucune activite enregistree pour le moment.'}
                </td>
              </tr>
            ) : (
              logs.slice(0, 20).map((log) => {
                const kind = (log.log_type ?? 'asset') as LogKind
                const target = log.asset_name ?? log.entity_name ?? '—'
                const clickable = canOpen[kind]
                return (
                  <tr
                    key={`${kind}-${log.id}`}
                    onClick={clickable ? () => navigate(KIND_ROUTE[kind]) : undefined}
                    style={clickable ? { cursor: 'pointer' } : undefined}
                    title={clickable ? `Ouvrir ${KIND_LABEL[kind]}s` : undefined}
                  >
                    <td>{formatDateTime(log.D)}</td>
                    <td><span className={`badge ${KIND_BADGE[kind]}`}>{KIND_LABEL[kind]}</span></td>
                    <td><span className="badge badge-info">{log.action}</span></td>
                    <td>{target}</td>
                    <td>{log.description ?? '—'}</td>
                  </tr>
                )
              })
            )}
          </tbody>
        </table>
      </section>
    </AppLayout>
  )
}
