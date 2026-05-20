import { useCallback, useEffect, useMemo, useState } from 'react'
import AppLayout from '../layouts/AppLayout'
import { fetchAdminLogs } from '../api/dashboard'
import { formatDateTime } from '../utils/dates'
import type { LogEntry, LogKind } from '../types'

const KIND_LABELS: Record<LogKind, string> = {
  asset: 'Asset',
  mission: 'Mission',
  admin: 'Utilisateur',
}

const KIND_BADGE: Record<LogKind, string> = {
  asset: 'badge-success',
  mission: 'badge-info',
  admin: 'badge-warning',
}

const ALL_LIMITS = [100, 200, 500, 1000]

export default function LogsPage() {
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [typeFilter, setTypeFilter] = useState<'' | LogKind>('')
  const [actionFilter, setActionFilter] = useState('')
  const [search, setSearch] = useState('')
  const [limit, setLimit] = useState(200)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const loadData = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const data = await fetchAdminLogs({ type: typeFilter, limit })
      setLogs(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur de chargement')
    } finally {
      setLoading(false)
    }
  }, [typeFilter, limit])

  useEffect(() => { loadData() }, [loadData])

  const actions = useMemo(() => {
    return Array.from(new Set(logs.map((l) => l.action))).sort()
  }, [logs])

  const filtered = useMemo(() => {
    const needle = search.trim().toLowerCase()
    return logs.filter((l) => {
      if (actionFilter && l.action !== actionFilter) return false
      if (!needle) return true
      const target = l.asset_name ?? l.entity_name ?? ''
      return (
        target.toLowerCase().includes(needle)
        || (l.description ?? '').toLowerCase().includes(needle)
      )
    })
  }, [logs, actionFilter, search])

  const counts = useMemo(() => {
    const c: Record<LogKind, number> = { asset: 0, mission: 0, admin: 0 }
    logs.forEach((l) => {
      const k = (l.log_type ?? 'asset') as LogKind
      c[k] = (c[k] ?? 0) + 1
    })
    return c
  }, [logs])

  return (
    <AppLayout>
      <section className="page-hero">
        <div className="page-meta">
          <span className="brand-sub">Audit</span>
          <div className="title">Journaux d'activite</div>
          <div className="subtitle">Consultation seule — les entrees sont immuables (cree par les triggers, jamais modifie ni supprime).</div>
        </div>
        <div className="controls-row">
          <button className="btn btn-secondary btn-sm" onClick={loadData} disabled={loading}>
            {loading ? 'Chargement...' : '↻ Actualiser'}
          </button>
        </div>
      </section>

      {error ? <div className="alert alert-danger">{error}</div> : null}

      <section className="stats-grid">
        <div className="stat-card success">
          <h3>Logs assets</h3>
          <div className="stat-value">{counts.asset}</div>
          <div className="stat-meta">CRUD assets / values / specs</div>
        </div>
        <div className="stat-card">
          <h3>Logs missions</h3>
          <div className="stat-value">{counts.mission}</div>
          <div className="stat-meta">Cycle de vie des missions</div>
        </div>
        <div className="stat-card warning">
          <h3>Logs admin</h3>
          <div className="stat-value">{counts.admin}</div>
          <div className="stat-meta">Comptes utilisateurs</div>
        </div>
      </section>

      <section className="panel">
        <div className="panel-header">
          <div className="panel-title">Filtres</div>
          <div className="search-bar search-compact">
            <span className="search-icon">&#9776;</span>
            <input
              type="text"
              placeholder="Rechercher dans la description ou la cible"
              aria-label="Rechercher dans les logs"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
        </div>
        <div className="filters">
          <select
            className="form-select"
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value as '' | LogKind)}
            aria-label="Type de log"
          >
            <option value="">Tous les types</option>
            <option value="asset">Asset</option>
            <option value="mission">Mission</option>
            <option value="admin">Utilisateur</option>
          </select>
          <select
            className="form-select"
            value={actionFilter}
            onChange={(e) => setActionFilter(e.target.value)}
            aria-label="Action"
          >
            <option value="">Toutes les actions</option>
            {actions.map((a) => (
              <option key={a} value={a}>{a}</option>
            ))}
          </select>
          <select
            className="form-select"
            value={limit}
            onChange={(e) => setLimit(Number(e.target.value))}
            aria-label="Nombre max d'entrees"
          >
            {ALL_LIMITS.map((n) => (
              <option key={n} value={n}>{n} max</option>
            ))}
          </select>
        </div>
      </section>

      <section className="data-table">
        <div className="table-header">
          <h3>Liste des entrees</h3>
          <span className="chip">{filtered.length} resultat(s)</span>
        </div>
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Type</th>
              <th>Action</th>
              <th>Cible</th>
              <th>Description</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={5} className="text-center">Chargement...</td></tr>
            ) : filtered.length === 0 ? (
              <tr><td colSpan={5} className="text-center">Aucune entree.</td></tr>
            ) : (
              filtered.map((log) => {
                const kind = (log.log_type ?? 'asset') as LogKind
                const target = log.asset_name ?? log.entity_name ?? '—'
                return (
                  <tr key={`${kind}-${log.id}`}>
                    <td>{formatDateTime(log.D)}</td>
                    <td><span className={`badge ${KIND_BADGE[kind]}`}>{KIND_LABELS[kind]}</span></td>
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
