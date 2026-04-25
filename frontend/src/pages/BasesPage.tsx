import { useCallback, useEffect, useMemo, useState } from 'react'
import type { FormEvent } from 'react'
import AppLayout from '../layouts/AppLayout'
import { fetchBases, createBase, updateBase, deleteBase } from '../api/assets'
import { useAuth } from '../context/AuthContext'
import type { Base } from '../types'

const ROLE_HIERARCHY = ['viewer', 'user', 'secure_user', 'technician', 'admin']

function canEdit(role: string | undefined): boolean {
  return ROLE_HIERARCHY.indexOf(role ?? '') >= ROLE_HIERARCHY.indexOf('technician')
}

export default function BasesPage() {
  const { user } = useAuth()
  const [search, setSearch] = useState('')
  const [bases, setBases] = useState<Base[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [form, setForm] = useState({ name: '', address: '' })

  const editable = canEdit(user?.role)

  const loadData = useCallback(async () => {
    setLoading(true)
    try {
      setBases(await fetchBases())
    } catch {
      setError('Erreur de chargement')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { loadData() }, [loadData])

  const filtered = useMemo(() => {
    return bases.filter((b) =>
      `${b.name} ${b.address}`.toLowerCase().includes(search.toLowerCase())
    )
  }, [bases, search])

  const openCreateModal = () => {
    setEditingId(null)
    setForm({ name: '', address: '' })
    setError('')
    setShowModal(true)
  }

  const openEditModal = (b: Base) => {
    setEditingId(b.id)
    setForm({ name: b.name, address: b.address })
    setError('')
    setShowModal(true)
  }

  const handleSave = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setSaving(true)
    setError('')
    try {
      if (editingId) {
        await updateBase(editingId, { name: form.name, address: form.address })
      } else {
        await createBase({ name: form.name, address: form.address })
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
    if (!confirm('Supprimer cette base ? Les salles associees seront impactees.')) return
    try {
      await deleteBase(id)
      await loadData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur de suppression')
    }
  }

  return (
    <AppLayout>
      <section className="page-hero">
        <div className="page-meta">
          <span className="brand-sub">Referentiels</span>
          <div className="title">Bases</div>
          <div className="subtitle">Gerer les bases et leurs emplacements.</div>
        </div>
        <div className="controls-row">
          <button className="btn btn-secondary btn-sm" onClick={loadData} disabled={loading}>
            {loading ? 'Chargement...' : '&#8635; Actualiser'}
          </button>
          {editable && (
            <button className="btn btn-primary btn-sm" onClick={openCreateModal}>+ Nouvelle base</button>
          )}
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
              placeholder="Rechercher une base"
              aria-label="Rechercher une base"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
        </div>
      </section>

      <section className="stats-grid">
        <div className="stat-card">
          <h3>Total bases</h3>
          <div className="stat-value">{bases.length}</div>
          <div className="stat-meta">Sites enregistres</div>
        </div>
      </section>

      <section className="data-table">
        <div className="table-header">
          <h3>Liste des bases</h3>
          <span className="chip">{filtered.length} resultat(s)</span>
        </div>
        <table>
          <thead>
            <tr>
              <th>Nom</th>
              <th>Adresse</th>
              {editable && <th>Actions</th>}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={editable ? 3 : 2} className="text-center">Chargement...</td></tr>
            ) : filtered.length === 0 ? (
              <tr><td colSpan={editable ? 3 : 2} className="text-center">Aucune base correspondante.</td></tr>
            ) : (
              filtered.map((b) => (
                <tr key={b.id}>
                  <td>{b.name}</td>
                  <td>{b.address}</td>
                  {editable && (
                    <td className="flex gap-1">
                      <button className="btn btn-sm btn-secondary" onClick={() => openEditModal(b)}>Edit</button>
                      <button className="btn btn-sm btn-danger" onClick={() => handleDelete(b.id)}>Supprimer</button>
                    </td>
                  )}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </section>

      <div className={`modal${showModal ? ' active' : ''}`}>
        <div className="modal-content">
          <div className="modal-header">
            <h3>{editingId ? 'Modifier la base' : 'Nouvelle base'}</h3>
            <button className="modal-close" onClick={() => setShowModal(false)} aria-label="Fermer">&times;</button>
          </div>

          {error && showModal ? <div className="alert alert-danger">{error}</div> : null}

          <form onSubmit={handleSave}>
            <div className="form-group">
              <label className="form-label">Nom *</label>
              <input
                type="text"
                className="form-input"
                value={form.name}
                onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))}
                placeholder="ex: Base Alpha, Caserne Nord..."
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Adresse *</label>
              <input
                type="text"
                className="form-input"
                value={form.address}
                onChange={(e) => setForm((p) => ({ ...p, address: e.target.value }))}
                placeholder="ex: 12 rue de la Paix, Paris"
                required
              />
            </div>

            <div className="flex gap-2">
              <button type="submit" className="btn btn-primary flex-grow" disabled={saving}>
                {saving ? 'Enregistrement...' : 'Enregistrer'}
              </button>
              <button type="button" className="btn btn-secondary flex-grow" onClick={() => setShowModal(false)}>
                Annuler
              </button>
            </div>
          </form>
        </div>
      </div>
    </AppLayout>
  )
}
