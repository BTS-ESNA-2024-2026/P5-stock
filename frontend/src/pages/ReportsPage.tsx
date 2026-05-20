import { useCallback, useEffect, useMemo, useState } from 'react'
import AppLayout from '../layouts/AppLayout'
import { fetchAssets, fetchAssetTypes, fetchBases, fetchRooms } from '../api/assets'
import { fetchMissions } from '../api/missions'
import { fetchLogs } from '../api/dashboard'
import type { Asset, AssetType, Base, Room, Mission, LogEntry, AssetStatus } from '../types'
import { ASSET_STATUS_LABELS } from '../types'

function downloadCsv(filename: string, rows: (string | number | null | undefined)[][]) {
  const escape = (v: string | number | null | undefined) => {
    if (v === null || v === undefined) return ''
    const s = String(v)
    return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s
  }
  const csv = rows.map((r) => r.map(escape).join(',')).join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
  URL.revokeObjectURL(url)
}

export default function ReportsPage() {
  const [assets, setAssets] = useState<Asset[]>([])
  const [assetTypes, setAssetTypes] = useState<AssetType[]>([])
  const [bases, setBases] = useState<Base[]>([])
  const [rooms, setRooms] = useState<Room[]>([])
  const [missions, setMissions] = useState<Mission[]>([])
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const loadData = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const [a, t, b, r, m, l] = await Promise.all([
        fetchAssets(), fetchAssetTypes(), fetchBases(), fetchRooms(), fetchMissions(), fetchLogs(),
      ])
      setAssets(a)
      setAssetTypes(t)
      setBases(b)
      setRooms(r)
      setMissions(m)
      setLogs(l)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur de chargement')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { loadData() }, [loadData])

  const byStatus = useMemo(() => {
    const map = new Map<AssetStatus, number>()
    assets.forEach((a) => map.set(a.status, (map.get(a.status) ?? 0) + 1))
    return map
  }, [assets])

  const byType = useMemo(() => {
    const map = new Map<string, number>()
    assets.forEach((a) => {
      const key = a.type_name ?? '—'
      map.set(key, (map.get(key) ?? 0) + 1)
    })
    return [...map.entries()].sort((a, b) => b[1] - a[1])
  }, [assets])

  const byBase = useMemo(() => {
    const map = new Map<string, number>()
    assets.forEach((a) => {
      const key = a.base_name ?? 'Sans base'
      map.set(key, (map.get(key) ?? 0) + 1)
    })
    return [...map.entries()].sort((a, b) => b[1] - a[1])
  }, [assets])

  const sensitiveCount = assets.filter((a) => a.sensible).length
  const inMissionCount = assets.filter((a) => a.mission_id).length
  const activeMissions = missions.filter((m) => m.status === 'active' || m.status === 'planned').length

  const exportAssets = () => {
    const header = ['id', 'name', 'number', 'type', 'status', 'base', 'room', 'mission', 'quantity', 'shelf', 'sensible']
    const rows: (string | number | null | undefined)[][] = [header]
    assets.forEach((a) => {
      rows.push([
        a.id, a.name, a.number, a.type_name, a.status,
        a.base_name, a.room_name, a.mission_title,
        a.quantity, a.shelf, a.sensible ? 'oui' : 'non',
      ])
    })
    downloadCsv(`assets-${new Date().toISOString().slice(0, 10)}.csv`, rows)
  }

  const exportLogs = () => {
    const header = ['date', 'action', 'asset', 'description']
    const rows: (string | number | null | undefined)[][] = [header]
    logs.forEach((l) => {
      rows.push([l.D, l.action, l.asset_name, l.description])
    })
    downloadCsv(`logs-${new Date().toISOString().slice(0, 10)}.csv`, rows)
  }

  const exportMissions = () => {
    const header = ['id', 'title', 'theatre', 'status', 'start', 'end', 'description']
    const rows: (string | number | null | undefined)[][] = [header]
    missions.forEach((m) => {
      rows.push([m.id, m.title, m.theatre, m.status, m.date_start, m.date_end, m.description])
    })
    downloadCsv(`missions-${new Date().toISOString().slice(0, 10)}.csv`, rows)
  }

  return (
    <AppLayout>
      <section className="page-hero">
        <div className="page-meta">
          <span className="brand-sub">Analyses</span>
          <div className="title">Rapports</div>
          <div className="subtitle">Synthese des stocks, missions et exports CSV.</div>
        </div>
        <div className="controls-row">
          <button className="btn btn-secondary btn-sm" onClick={loadData} disabled={loading}>
            {loading ? 'Chargement...' : '↻ Actualiser'}
          </button>
        </div>
      </section>

      {error ? <div className="alert alert-danger">{error}</div> : null}

      <section className="stats-grid">
        <div className="stat-card">
          <h3>Assets totaux</h3>
          <div className="stat-value">{assets.length}</div>
          <div className="stat-meta">{assetTypes.length} types, {bases.length} bases, {rooms.length} salles</div>
        </div>
        <div className="stat-card warning">
          <h3>Sensibles</h3>
          <div className="stat-value">{sensitiveCount}</div>
          <div className="stat-meta">Assets classifies sensibles</div>
        </div>
        <div className="stat-card success">
          <h3>En mission</h3>
          <div className="stat-value">{inMissionCount}</div>
          <div className="stat-meta">{activeMissions} mission(s) active(s)/planifiee(s)</div>
        </div>
        <div className="stat-card">
          <h3>Activite</h3>
          <div className="stat-value">{logs.length}</div>
          <div className="stat-meta">Entrees recentes</div>
        </div>
      </section>

      <section className="panel">
        <div className="panel-header">
          <div className="panel-title">Exports CSV</div>
        </div>
        <div className="flex gap-2" style={{ flexWrap: 'wrap' }}>
          <button className="btn btn-primary btn-sm" onClick={exportAssets} disabled={assets.length === 0}>
            Exporter assets ({assets.length})
          </button>
          <button className="btn btn-primary btn-sm" onClick={exportMissions} disabled={missions.length === 0}>
            Exporter missions ({missions.length})
          </button>
          <button className="btn btn-primary btn-sm" onClick={exportLogs} disabled={logs.length === 0}>
            Exporter logs ({logs.length})
          </button>
        </div>
      </section>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
        <section className="data-table">
          <div className="table-header">
            <h3>Repartition par statut</h3>
          </div>
          <table>
            <thead>
              <tr><th>Statut</th><th>Total</th></tr>
            </thead>
            <tbody>
              {[...byStatus.entries()].map(([s, n]) => (
                <tr key={s}>
                  <td>{ASSET_STATUS_LABELS[s] ?? s}</td>
                  <td>{n}</td>
                </tr>
              ))}
              {byStatus.size === 0 && (
                <tr><td colSpan={2} className="text-center">Aucune donnee.</td></tr>
              )}
            </tbody>
          </table>
        </section>

        <section className="data-table">
          <div className="table-header">
            <h3>Repartition par type</h3>
          </div>
          <table>
            <thead>
              <tr><th>Type</th><th>Total</th></tr>
            </thead>
            <tbody>
              {byType.map(([t, n]) => (
                <tr key={t}><td>{t}</td><td>{n}</td></tr>
              ))}
              {byType.length === 0 && (
                <tr><td colSpan={2} className="text-center">Aucune donnee.</td></tr>
              )}
            </tbody>
          </table>
        </section>

        <section className="data-table">
          <div className="table-header">
            <h3>Repartition par base</h3>
          </div>
          <table>
            <thead>
              <tr><th>Base</th><th>Total</th></tr>
            </thead>
            <tbody>
              {byBase.map(([b, n]) => (
                <tr key={b}><td>{b}</td><td>{n}</td></tr>
              ))}
              {byBase.length === 0 && (
                <tr><td colSpan={2} className="text-center">Aucune donnee.</td></tr>
              )}
            </tbody>
          </table>
        </section>
      </div>
    </AppLayout>
  )
}
