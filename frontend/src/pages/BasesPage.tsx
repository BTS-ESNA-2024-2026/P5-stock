import { useCallback, useEffect, useMemo, useState } from 'react'
import type { FormEvent } from 'react'
import AppLayout from '../layouts/AppLayout'
import {
  fetchBases, createBase, updateBase, deleteBase,
  fetchRooms, createRoom, updateRoom, deleteRoom,
} from '../api/assets'
import { useAuth } from '../context/AuthContext'
import type { Base, Room } from '../types'

const ROLE_HIERARCHY = ['viewer', 'user', 'secure_user', 'technician', 'admin']

function canEdit(role: string | undefined): boolean {
  return ROLE_HIERARCHY.indexOf(role ?? '') >= ROLE_HIERARCHY.indexOf('technician')
}

export default function BasesPage() {
  const { user } = useAuth()
  const editable = canEdit(user?.role)

  const [baseSearch, setBaseSearch] = useState('')
  const [roomSearch, setRoomSearch] = useState('')
  const [baseFilter, setBaseFilter] = useState('')
  const [bases, setBases] = useState<Base[]>([])
  const [rooms, setRooms] = useState<Room[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  // Base modal
  const [showBaseModal, setShowBaseModal] = useState(false)
  const [editingBaseId, setEditingBaseId] = useState<string | null>(null)
  const [baseForm, setBaseForm] = useState({ name: '', address: '' })

  // Room modal
  const [showRoomModal, setShowRoomModal] = useState(false)
  const [editingRoomId, setEditingRoomId] = useState<string | null>(null)
  const [roomForm, setRoomForm] = useState({ room: '', base_id: '' })

  const loadData = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const [b, r] = await Promise.all([fetchBases(), fetchRooms()])
      setBases(b)
      setRooms(r)
    } catch {
      setError('Erreur de chargement')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { loadData() }, [loadData])

  const filteredBases = useMemo(() => {
    return bases.filter((b) =>
      `${b.name} ${b.address}`.toLowerCase().includes(baseSearch.toLowerCase())
    )
  }, [bases, baseSearch])

  const filteredRooms = useMemo(() => {
    const needle = roomSearch.toLowerCase()
    return rooms.filter((r) => {
      const matchSearch = `${r.room} ${r.base_name ?? ''}`.toLowerCase().includes(needle)
      const matchBase = baseFilter ? r.base_id === baseFilter : true
      return matchSearch && matchBase
    })
  }, [rooms, roomSearch, baseFilter])

  // ---- Base ----
  const openCreateBaseModal = () => {
    setEditingBaseId(null)
    setBaseForm({ name: '', address: '' })
    setError('')
    setShowBaseModal(true)
  }

  const openEditBaseModal = (b: Base) => {
    setEditingBaseId(b.id)
    setBaseForm({ name: b.name, address: b.address })
    setError('')
    setShowBaseModal(true)
  }

  const handleSaveBase = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setSaving(true)
    setError('')
    try {
      if (editingBaseId) {
        await updateBase(editingBaseId, { name: baseForm.name, address: baseForm.address })
      } else {
        await createBase({ name: baseForm.name, address: baseForm.address })
      }
      setShowBaseModal(false)
      await loadData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur')
    } finally {
      setSaving(false)
    }
  }

  const handleDeleteBase = async (id: string) => {
    if (!confirm('Supprimer cette base ? Les salles associees seront impactees.')) return
    try {
      await deleteBase(id)
      if (baseFilter === id) setBaseFilter('')
      await loadData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur de suppression')
    }
  }

  // ---- Room ----
  const openCreateRoomModal = (preselectedBaseId?: string) => {
    if (bases.length === 0) {
      setError('Creez d\'abord une base avant d\'ajouter une salle.')
      return
    }
    setEditingRoomId(null)
    setRoomForm({
      room: '',
      base_id: preselectedBaseId ?? baseFilter ?? bases[0]?.id ?? '',
    })
    setError('')
    setShowRoomModal(true)
  }

  const openEditRoomModal = (r: Room) => {
    setEditingRoomId(r.id)
    setRoomForm({ room: r.room, base_id: r.base_id })
    setError('')
    setShowRoomModal(true)
  }

  const handleSaveRoom = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setSaving(true)
    setError('')
    try {
      if (editingRoomId) {
        // The backend update endpoint accepts only `room` for renames; moving a
        // salle between bases would require a delete+recreate.
        await updateRoom(editingRoomId, { room: roomForm.room })
      } else {
        await createRoom({ base_id: roomForm.base_id, room: roomForm.room })
      }
      setShowRoomModal(false)
      await loadData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur')
    } finally {
      setSaving(false)
    }
  }

  const handleDeleteRoom = async (id: string) => {
    if (!confirm('Supprimer cette salle ? Les assets places ici perdront leur localisation.')) return
    try {
      await deleteRoom(id)
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
          <div className="title">Bases &amp; Salles</div>
          <div className="subtitle">Gerer les bases et leurs salles. Les salles sont les emplacements assignables aux assets.</div>
        </div>
        <div className="controls-row">
          <button className="btn btn-secondary btn-sm" onClick={loadData} disabled={loading}>
            {loading ? 'Chargement...' : '↻ Actualiser'}
          </button>
          {editable && (
            <>
              <button className="btn btn-primary btn-sm" onClick={openCreateBaseModal}>+ Nouvelle base</button>
              <button
                className="btn btn-primary btn-sm"
                onClick={() => openCreateRoomModal()}
                disabled={bases.length === 0}
                title={bases.length === 0 ? 'Creez d\'abord une base' : ''}
              >
                + Nouvelle salle
              </button>
            </>
          )}
        </div>
      </section>

      {error && !showBaseModal && !showRoomModal ? <div className="alert alert-danger">{error}</div> : null}

      <section className="stats-grid">
        <div className="stat-card">
          <h3>Total bases</h3>
          <div className="stat-value">{bases.length}</div>
          <div className="stat-meta">Sites enregistres</div>
        </div>
        <div className="stat-card">
          <h3>Total salles</h3>
          <div className="stat-value">{rooms.length}</div>
          <div className="stat-meta">Emplacements assignables aux assets</div>
        </div>
      </section>

      {/* --- Bases --- */}
      <section className="data-table">
        <div className="table-header">
          <h3>Bases</h3>
          <div className="flex gap-1" style={{ alignItems: 'center', flexWrap: 'wrap' }}>
            <span className="chip">{filteredBases.length} resultat(s)</span>
            <div className="search-bar search-compact">
              <span className="search-icon">&#9776;</span>
              <input
                type="text"
                placeholder="Rechercher une base"
                aria-label="Rechercher une base"
                value={baseSearch}
                onChange={(e) => setBaseSearch(e.target.value)}
              />
            </div>
          </div>
        </div>
        <table>
          <thead>
            <tr>
              <th>Nom</th>
              <th>Adresse</th>
              <th>Salles</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={4} className="text-center">Chargement...</td></tr>
            ) : filteredBases.length === 0 ? (
              <tr><td colSpan={4} className="text-center">Aucune base correspondante.</td></tr>
            ) : (
              filteredBases.map((b) => {
                const roomCount = rooms.filter((r) => r.base_id === b.id).length
                return (
                  <tr key={b.id}>
                    <td>{b.name}</td>
                    <td>{b.address}</td>
                    <td>
                      <button
                        type="button"
                        className="chip"
                        onClick={() => { setBaseFilter(b.id); setRoomSearch('') }}
                        style={{ cursor: 'pointer', border: 'none' }}
                        title="Filtrer les salles de cette base"
                      >
                        {roomCount}
                      </button>
                    </td>
                    <td className="flex gap-1">
                      {editable && (
                        <>
                          <button className="btn btn-sm btn-primary" onClick={() => openCreateRoomModal(b.id)}>+ Salle</button>
                          <button className="btn btn-sm btn-secondary" onClick={() => openEditBaseModal(b)}>Edit</button>
                          <button className="btn btn-sm btn-danger" onClick={() => handleDeleteBase(b.id)}>Supprimer</button>
                        </>
                      )}
                    </td>
                  </tr>
                )
              })
            )}
          </tbody>
        </table>
      </section>

      {/* --- Rooms --- */}
      <section className="data-table">
        <div className="table-header">
          <h3>Salles</h3>
          <div className="flex gap-1" style={{ alignItems: 'center', flexWrap: 'wrap' }}>
            <span className="chip">{filteredRooms.length} resultat(s)</span>
            <select
              className="form-select"
              value={baseFilter}
              onChange={(e) => setBaseFilter(e.target.value)}
              aria-label="Filtre par base"
            >
              <option value="">Toutes les bases</option>
              {bases.map((b) => (
                <option key={b.id} value={b.id}>{b.name}</option>
              ))}
            </select>
            <div className="search-bar search-compact">
              <span className="search-icon">&#9776;</span>
              <input
                type="text"
                placeholder="Rechercher une salle"
                aria-label="Rechercher une salle"
                value={roomSearch}
                onChange={(e) => setRoomSearch(e.target.value)}
              />
            </div>
          </div>
        </div>
        <table>
          <thead>
            <tr>
              <th>Salle</th>
              <th>Base</th>
              {editable && <th>Actions</th>}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={editable ? 3 : 2} className="text-center">Chargement...</td></tr>
            ) : rooms.length === 0 ? (
              <tr>
                <td colSpan={editable ? 3 : 2} className="text-center">
                  Aucune salle creee. {editable && bases.length > 0 ? (
                    <button className="btn btn-sm btn-primary" style={{ marginLeft: '0.5rem' }} onClick={() => openCreateRoomModal()}>
                      + Creer la premiere salle
                    </button>
                  ) : null}
                </td>
              </tr>
            ) : filteredRooms.length === 0 ? (
              <tr><td colSpan={editable ? 3 : 2} className="text-center">Aucune salle correspondante.</td></tr>
            ) : (
              filteredRooms.map((r) => (
                <tr key={r.id}>
                  <td>{r.room}</td>
                  <td>{r.base_name ?? '—'}</td>
                  {editable && (
                    <td className="flex gap-1">
                      <button className="btn btn-sm btn-secondary" onClick={() => openEditRoomModal(r)}>Edit</button>
                      <button className="btn btn-sm btn-danger" onClick={() => handleDeleteRoom(r.id)}>Supprimer</button>
                    </td>
                  )}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </section>

      {/* Modal base */}
      {showBaseModal && (
        <div className="modal active">
          <div className="modal-content">
            <div className="modal-header">
              <h3>{editingBaseId ? 'Modifier la base' : 'Nouvelle base'}</h3>
              <button className="modal-close" onClick={() => setShowBaseModal(false)} aria-label="Fermer">&times;</button>
            </div>

            {error ? <div className="alert alert-danger">{error}</div> : null}

            <form onSubmit={handleSaveBase}>
              <div className="form-group">
                <label className="form-label">Nom *</label>
                <input
                  type="text"
                  className="form-input"
                  value={baseForm.name}
                  onChange={(e) => setBaseForm((p) => ({ ...p, name: e.target.value }))}
                  placeholder="ex: Base Alpha, Caserne Nord..."
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Adresse *</label>
                <input
                  type="text"
                  className="form-input"
                  value={baseForm.address}
                  onChange={(e) => setBaseForm((p) => ({ ...p, address: e.target.value }))}
                  placeholder="ex: 12 rue de la Paix, Paris"
                  required
                />
              </div>

              <div className="flex gap-2">
                <button type="submit" className="btn btn-primary flex-grow" disabled={saving}>
                  {saving ? 'Enregistrement...' : 'Enregistrer'}
                </button>
                <button type="button" className="btn btn-secondary flex-grow" onClick={() => setShowBaseModal(false)}>
                  Annuler
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal room */}
      {showRoomModal && (
        <div className="modal active">
          <div className="modal-content">
            <div className="modal-header">
              <h3>{editingRoomId ? 'Modifier la salle' : 'Nouvelle salle'}</h3>
              <button className="modal-close" onClick={() => setShowRoomModal(false)} aria-label="Fermer">&times;</button>
            </div>

            {error ? <div className="alert alert-danger">{error}</div> : null}

            <form onSubmit={handleSaveRoom}>
              <div className="form-group">
                <label className="form-label">Base *</label>
                <select
                  className="form-select"
                  value={roomForm.base_id}
                  onChange={(e) => setRoomForm((p) => ({ ...p, base_id: e.target.value }))}
                  disabled={Boolean(editingRoomId)}
                  required
                >
                  <option value="">Selectionner une base</option>
                  {bases.map((b) => (
                    <option key={b.id} value={b.id}>{b.name}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Nom de la salle *</label>
                <input
                  type="text"
                  className="form-input"
                  value={roomForm.room}
                  onChange={(e) => setRoomForm((p) => ({ ...p, room: e.target.value }))}
                  placeholder="ex: Armurerie A1, Hangar 3..."
                  required
                />
              </div>

              <div className="flex gap-2">
                <button type="submit" className="btn btn-primary flex-grow" disabled={saving}>
                  {saving ? 'Enregistrement...' : 'Enregistrer'}
                </button>
                <button type="button" className="btn btn-secondary flex-grow" onClick={() => setShowRoomModal(false)}>
                  Annuler
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </AppLayout>
  )
}
