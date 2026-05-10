import { useCallback, useEffect, useMemo, useState } from 'react'
import type { FormEvent } from 'react'
import AppLayout from '../layouts/AppLayout'
import { fetchMissions, createMission, updateMission, deleteMission } from '../api/missions'
import { combineDateTime, formatDate, toDateInputValue, toTimeInputValue } from '../utils/dates'
import type { Mission } from '../types'

const MISSION_STATUS_OPTIONS = ['planned', 'active', 'finished', 'cancelled']
const MISSION_STATUS_LABELS: Record<string, string> = {
  planned: 'Planifiee',
  active: 'Active',
  finished: 'Terminee',
  cancelled: 'Annulee',
}
const MISSION_STATUS_BADGE: Record<string, string> = {
  planned: 'badge-info',
  active: 'badge-success',
  finished: 'badge-warning',
  cancelled: 'badge-danger',
}

export default function MissionsPage() {
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [missions, setMissions] = useState<Mission[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const [form, setForm] = useState({
    title: '',
    status: 'planned',
    theatre: '',
    description: '',
    date_start_date: '',
    date_start_time: '',
    date_end_date: '',
    date_end_time: '',
  })

  const loadData = useCallback(async () => {
    setLoading(true)
    try {
      const data = await fetchMissions()
      setMissions(data)
    } catch {
      setError('Erreur de chargement')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { loadData() }, [loadData])

  const filteredMissions = useMemo(() => {
    return missions.filter((m) => {
      const text = `${m.title} ${m.theatre} ${m.description ?? ''}`.toLowerCase()
      const matchSearch = text.includes(search.toLowerCase())
      const matchStatus = statusFilter ? m.status === statusFilter : true
      return matchSearch && matchStatus
    })
  }, [missions, search, statusFilter])

  const openCreateModal = () => {
    setEditingId(null)
    setForm({
      title: '', status: 'planned', theatre: '', description: '',
      date_start_date: '', date_start_time: '',
      date_end_date: '', date_end_time: '',
    })
    setError('')
    setShowModal(true)
  }

  const openEditModal = (m: Mission) => {
    setEditingId(m.id)
    setForm({
      title: m.title,
      status: m.status,
      theatre: m.theatre,
      description: m.description ?? '',
      date_start_date: toDateInputValue(m.date_start),
      date_start_time: toTimeInputValue(m.date_start),
      date_end_date: toDateInputValue(m.date_end),
      date_end_time: toTimeInputValue(m.date_end),
    })
    setError('')
    setShowModal(true)
  }

  const saveMission = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setSaving(true)
    setError('')

    const payload: Record<string, unknown> = {
      title: form.title,
      status: form.status,
      theatre: form.theatre,
    }
    if (form.description) payload.description = form.description
    const start = combineDateTime(form.date_start_date, form.date_start_time)
    const end = combineDateTime(form.date_end_date, form.date_end_time)
    if (start) payload.date_start = start
    if (end) payload.date_end = end

    try {
      if (editingId) {
        await updateMission(editingId, payload)
      } else {
        await createMission(payload)
      }
      setShowModal(false)
      await loadData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Supprimer cette mission ?')) return
    try {
      await deleteMission(id)
      await loadData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur de suppression')
    }
  }

  return (
    <AppLayout>
      <section className="page-hero">
        <div className="page-meta">
          <span className="brand-sub">Operations</span>
          <div className="title">Gestion des missions</div>
          <div className="subtitle">Planifier, suivre et piloter les operations terrain.</div>
        </div>
        <div className="controls-row">
          <button className="btn btn-secondary btn-sm" onClick={loadData} disabled={loading}>
            {loading ? 'Chargement...' : '↻ Actualiser'}
          </button>
          <button className="btn btn-primary btn-sm" onClick={openCreateModal}>+ Nouvelle mission</button>
        </div>
      </section>

      {error && !showModal ? <div className="alert alert-danger">{error}</div> : null}

      <section className="panel">
        <div className="panel-header">
          <div className="panel-title">Filtres</div>
          <div className="search-bar search-compact">
            <span className="search-icon">&#9776;</span>
            <input
              type="text"
              placeholder="Rechercher une mission"
              aria-label="Rechercher une mission"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
        </div>
        <div className="filters">
          <select className="form-select" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="">Tous les statuts</option>
            {MISSION_STATUS_OPTIONS.map((s) => (
              <option key={s} value={s}>{MISSION_STATUS_LABELS[s] ?? s}</option>
            ))}
          </select>
        </div>
      </section>

      <section className="data-table">
        <div className="table-header">
          <h3>Liste des missions</h3>
          <span className="chip">{filteredMissions.length} resultat(s)</span>
        </div>
        <table>
          <thead>
            <tr>
              <th>Titre</th>
              <th>Theatre</th>
              <th>Statut</th>
              <th>Debut</th>
              <th>Fin</th>
              <th>Assets</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={7} className="text-center">Chargement...</td></tr>
            ) : filteredMissions.length === 0 ? (
              <tr><td colSpan={7} className="text-center">Aucune mission correspondante.</td></tr>
            ) : (
              filteredMissions.map((m) => (
                <tr key={m.id}>
                  <td>{m.title}</td>
                  <td>{m.theatre}</td>
                  <td>
                    <span className={`badge ${MISSION_STATUS_BADGE[m.status] ?? 'badge-info'}`}>
                      {MISSION_STATUS_LABELS[m.status] ?? m.status}
                    </span>
                  </td>
                  <td>{formatDate(m.date_start)}</td>
                  <td>{formatDate(m.date_end)}</td>
                  <td>{m.asset_count ?? 0}</td>
                  <td className="flex gap-1">
                    <button className="btn btn-sm btn-secondary" onClick={() => openEditModal(m)}>Edit</button>
                    <button className="btn btn-sm btn-danger" onClick={() => handleDelete(m.id)}>Supprimer</button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </section>

      <div className={`modal${showModal ? ' active' : ''}`}>
        <div className="modal-content">
          <div className="modal-header">
            <h3>{editingId ? 'Modifier mission' : 'Nouvelle mission'}</h3>
            <button className="modal-close" onClick={() => setShowModal(false)} aria-label="Fermer">&times;</button>
          </div>

          {error && showModal ? <div className="alert alert-danger">{error}</div> : null}

          <form onSubmit={saveMission}>
            <div className="form-group">
              <label className="form-label">Titre *</label>
              <input
                type="text"
                className="form-input"
                value={form.title}
                onChange={(e) => setForm((p) => ({ ...p, title: e.target.value }))}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Theatre *</label>
              <input
                type="text"
                className="form-input"
                value={form.theatre}
                onChange={(e) => setForm((p) => ({ ...p, theatre: e.target.value }))}
                required
                placeholder="Zone d'operation"
              />
            </div>

            <div className="form-group">
              <label className="form-label">Statut *</label>
              <select
                className="form-select"
                value={form.status}
                onChange={(e) => setForm((p) => ({ ...p, status: e.target.value }))}
              >
                {MISSION_STATUS_OPTIONS.map((s) => (
                  <option key={s} value={s}>{MISSION_STATUS_LABELS[s] ?? s}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Description</label>
              <input
                type="text"
                className="form-input"
                value={form.description}
                onChange={(e) => setForm((p) => ({ ...p, description: e.target.value }))}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Debut (date / heure)</label>
              <div className="flex gap-1">
                <input
                  type="date"
                  lang="fr-FR"
                  className="form-input"
                  value={form.date_start_date}
                  onChange={(e) => setForm((p) => ({ ...p, date_start_date: e.target.value }))}
                  style={{ flex: 2 }}
                />
                <input
                  type="time"
                  lang="fr-FR"
                  step={60}
                  className="form-input"
                  value={form.date_start_time}
                  onChange={(e) => setForm((p) => ({ ...p, date_start_time: e.target.value }))}
                  disabled={!form.date_start_date}
                  style={{ flex: 1 }}
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Fin (date / heure)</label>
              <div className="flex gap-1">
                <input
                  type="date"
                  lang="fr-FR"
                  className="form-input"
                  value={form.date_end_date}
                  onChange={(e) => setForm((p) => ({ ...p, date_end_date: e.target.value }))}
                  style={{ flex: 2 }}
                />
                <input
                  type="time"
                  lang="fr-FR"
                  step={60}
                  className="form-input"
                  value={form.date_end_time}
                  onChange={(e) => setForm((p) => ({ ...p, date_end_time: e.target.value }))}
                  disabled={!form.date_end_date}
                  style={{ flex: 1 }}
                />
              </div>
            </div>

            <div className="flex gap-2">
              <button type="submit" className="btn btn-primary flex-grow" disabled={saving}>
                {saving ? 'Enregistrement...' : 'Enregistrer'}
              </button>
              <button type="button" className="btn btn-secondary flex-grow" onClick={() => setShowModal(false)}>Annuler</button>
            </div>
          </form>
        </div>
      </div>
    </AppLayout>
  )
}
