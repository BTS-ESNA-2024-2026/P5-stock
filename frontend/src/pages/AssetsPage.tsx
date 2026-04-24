import { useCallback, useEffect, useMemo, useState } from 'react'
import type { FormEvent } from 'react'
import AppLayout from '../layouts/AppLayout'
import { fetchAssets, fetchAssetTypes, fetchRooms, fetchSpecs, createAsset, updateAsset, deleteAsset, fetchAssetValues, createValue, updateValue, deleteValue } from '../api/assets'
import { useAuth } from '../context/AuthContext'
import type { Asset, AssetType, Room, AssetStatus, Spec, Value } from '../types'
import { ASSET_STATUS_LABELS, ASSET_STATUS_BADGE } from '../types'

const ALL_STATUSES: AssetStatus[] = ['STOCK', 'DESTROYED', 'SOLD', 'LOST', 'TRANSIT', 'PURCHASED']
const ROLE_HIERARCHY = ['viewer', 'user', 'secure_user', 'technician', 'admin']
function canEdit(role: string | undefined) {
  return ROLE_HIERARCHY.indexOf(role ?? '') >= ROLE_HIERARCHY.indexOf('technician')
}

export default function AssetsPage() {
  const { user } = useAuth()
  const editable = canEdit(user?.role)

  const [search, setSearch] = useState('')
  const [typeFilter, setTypeFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [assets, setAssets] = useState<Asset[]>([])
  const [assetTypes, setAssetTypes] = useState<AssetType[]>([])
  const [rooms, setRooms] = useState<Room[]>([])
  const [specs, setSpecs] = useState<Spec[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  // Values modal
  const [showValuesModal, setShowValuesModal] = useState(false)
  const [valuesAsset, setValuesAsset] = useState<Asset | null>(null)
  const [assetValues, setAssetValues] = useState<Value[]>([])
  const [valuesLoading, setValuesLoading] = useState(false)
  const [editingValueId, setEditingValueId] = useState<string | null>(null)
  const [valueForm, setValueForm] = useState('')
  const [valueSpecId, setValueSpecId] = useState('')
  const [savingValue, setSavingValue] = useState(false)
  const [valueError, setValueError] = useState('')

  const [form, setForm] = useState({
    type_asset_id: '',
    name: '',
    number: '',
    status: 'STOCK' as AssetStatus,
    room_id: '',
    quantity: '',
    shelf: '',
    sensible: false,
  })

  const loadData = useCallback(async () => {
    setLoading(true)
    try {
      const [a, t, r, s] = await Promise.all([fetchAssets(), fetchAssetTypes(), fetchRooms(), fetchSpecs()])
      setAssets(a)
      setAssetTypes(t)
      setRooms(r)
      setSpecs(s)
    } catch {
      setError('Erreur de chargement')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { loadData() }, [loadData])

  const filteredAssets = useMemo(() => {
    return assets.filter((asset) => {
      const text = `${asset.number ?? ''} ${asset.name} ${asset.room_name ?? ''} ${asset.type_name ?? ''}`.toLowerCase()
      const matchSearch = text.includes(search.toLowerCase())
      const matchType = typeFilter ? asset.type_asset_id === typeFilter : true
      const matchStatus = statusFilter ? asset.status === statusFilter : true
      return matchSearch && matchType && matchStatus
    })
  }, [assets, search, statusFilter, typeFilter])

  const openCreateModal = () => {
    setEditingId(null)
    setForm({ type_asset_id: '', name: '', number: '', status: 'STOCK', room_id: '', quantity: '', shelf: '', sensible: false })
    setError('')
    setShowModal(true)
  }

  const openEditModal = (asset: Asset) => {
    setEditingId(asset.id)
    setForm({
      type_asset_id: asset.type_asset_id,
      name: asset.name,
      number: asset.number ?? '',
      status: asset.status,
      room_id: asset.room_id ?? '',
      quantity: asset.quantity?.toString() ?? '',
      shelf: asset.shelf ?? '',
      sensible: asset.sensible ?? false,
    })
    setError('')
    setShowModal(true)
  }

  const saveAsset = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setSaving(true)
    setError('')

    const payload: Record<string, unknown> = {
      type_asset_id: form.type_asset_id,
      name: form.name,
      status: form.status,
    }
    if (form.number) payload.number = form.number
    if (form.room_id) payload.room_id = form.room_id
    if (form.quantity) payload.quantity = parseInt(form.quantity, 10)
    if (form.shelf) payload.shelf = form.shelf
    payload.sensible = form.sensible

    try {
      if (editingId) {
        await updateAsset(editingId, payload)
      } else {
        await createAsset(payload)
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
    if (!confirm('Supprimer cet asset ?')) return
    try {
      await deleteAsset(id)
      await loadData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur de suppression')
    }
  }

  const openValuesModal = async (asset: Asset) => {
    setValuesAsset(asset)
    setValuesLoading(true)
    setValueError('')
    setEditingValueId(null)
    setValueForm('')
    setValueSpecId('')
    setShowValuesModal(true)
    try {
      setAssetValues(await fetchAssetValues(asset.id))
    } catch {
      setValueError('Erreur de chargement des valeurs')
    } finally {
      setValuesLoading(false)
    }
  }

  const startEditValue = (v: Value) => {
    setEditingValueId(v.id)
    setValueSpecId(v.spec_id)
    setValueForm(v.value)
    setValueError('')
  }

  const startAddValue = (specId: string) => {
    setEditingValueId(null)
    setValueSpecId(specId)
    setValueForm('')
    setValueError('')
  }

  const cancelValueEdit = () => {
    setEditingValueId(null)
    setValueSpecId('')
    setValueForm('')
    setValueError('')
  }

  const saveValue = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (!valuesAsset) return
    setSavingValue(true)
    setValueError('')
    try {
      if (editingValueId) {
        await updateValue(editingValueId, { value: valueForm })
      } else {
        await createValue({ asset_id: valuesAsset.id, spec_id: valueSpecId, value: valueForm })
      }
      setAssetValues(await fetchAssetValues(valuesAsset.id))
      cancelValueEdit()
    } catch (err) {
      setValueError(err instanceof Error ? err.message : 'Erreur')
    } finally {
      setSavingValue(false)
    }
  }

  const handleDeleteValue = async (id: string) => {
    if (!confirm('Supprimer cette valeur ?')) return
    if (!valuesAsset) return
    try {
      await deleteValue(id)
      setAssetValues(await fetchAssetValues(valuesAsset.id))
    } catch (err) {
      setValueError(err instanceof Error ? err.message : 'Erreur de suppression')
    }
  }

  // Specs for the currently viewed asset's type
  const specsForAsset = valuesAsset
    ? specs.filter((s) => s.type_id === valuesAsset.type_asset_id)
    : []

  return (
    <AppLayout>
      <section className="page-hero">
        <div className="page-meta">
          <span className="brand-sub">Inventaire</span>
          <div className="title">Gestion des assets</div>
          <div className="subtitle">Filtrer, creer et superviser les equipements.</div>
        </div>
        <div className="controls-row">
          <button className="btn btn-secondary btn-sm" onClick={loadData} disabled={loading}>
            {loading ? 'Chargement...' : '&#8635; Actualiser'}
          </button>
          <button className="btn btn-primary btn-sm" onClick={openCreateModal}>+ Nouvel asset</button>
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
              placeholder="Rechercher un asset"
              aria-label="Rechercher un asset"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
        </div>
        <div className="filters">
          <select className="form-select" value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}>
            <option value="">Tous les types</option>
            {assetTypes.map((t) => (
              <option key={t.id} value={t.id}>{t.type}</option>
            ))}
          </select>
          <select className="form-select" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="">Tous les statuts</option>
            {ALL_STATUSES.map((s) => (
              <option key={s} value={s}>{ASSET_STATUS_LABELS[s]}</option>
            ))}
          </select>
        </div>
      </section>

      <section className="data-table">
        <div className="table-header">
          <h3>Liste des assets</h3>
          <span className="chip">{filteredAssets.length} resultat(s)</span>
        </div>
        <table>
          <thead>
            <tr>
              <th>Numero</th>
              <th>Nom</th>
              <th>Type</th>
              <th>Statut</th>
              <th>Localisation</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={6} className="text-center">Chargement...</td></tr>
            ) : filteredAssets.length === 0 ? (
              <tr><td colSpan={6} className="text-center">Aucun asset correspondant.</td></tr>
            ) : (
              filteredAssets.map((asset) => (
                <tr key={asset.id}>
                  <td>{asset.number ?? '—'}</td>
                  <td>{asset.name}</td>
                  <td>{asset.type_name ?? '—'}</td>
                  <td>
                    <span className={`badge ${ASSET_STATUS_BADGE[asset.status]}`}>
                      {ASSET_STATUS_LABELS[asset.status]}
                    </span>
                  </td>
                  <td>{asset.room_name ?? '—'}{asset.base_name ? ` (${asset.base_name})` : ''}</td>
                  <td className="flex gap-1">
                    <button className="btn btn-sm btn-secondary" onClick={() => openValuesModal(asset)}>Specs</button>
                    <button className="btn btn-sm btn-secondary" onClick={() => openEditModal(asset)}>Edit</button>
                    <button className="btn btn-sm btn-danger" onClick={() => handleDelete(asset.id)}>Supprimer</button>
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
            <h3>{editingId ? 'Modifier asset' : 'Nouvel asset'}</h3>
            <button className="modal-close" onClick={() => setShowModal(false)} aria-label="Fermer">&times;</button>
          </div>

          {error && showModal ? <div className="alert alert-danger">{error}</div> : null}

          <form onSubmit={saveAsset}>
            <div className="form-group">
              <label className="form-label">Type d'asset *</label>
              <select
                className="form-select"
                value={form.type_asset_id}
                onChange={(e) => setForm((p) => ({ ...p, type_asset_id: e.target.value }))}
                required
              >
                <option value="">Selectionner un type</option>
                {assetTypes.map((t) => (
                  <option key={t.id} value={t.id}>{t.type}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Nom *</label>
              <input
                type="text"
                className="form-input"
                value={form.name}
                onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Numero</label>
              <input
                type="text"
                className="form-input"
                value={form.number}
                onChange={(e) => setForm((p) => ({ ...p, number: e.target.value }))}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Statut *</label>
              <select
                className="form-select"
                value={form.status}
                onChange={(e) => setForm((p) => ({ ...p, status: e.target.value as AssetStatus }))}
              >
                {ALL_STATUSES.map((s) => (
                  <option key={s} value={s}>{ASSET_STATUS_LABELS[s]}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Localisation</label>
              <select
                className="form-select"
                value={form.room_id}
                onChange={(e) => setForm((p) => ({ ...p, room_id: e.target.value }))}
              >
                <option value="">Aucune</option>
                {rooms.map((r) => (
                  <option key={r.id} value={r.id}>{r.room}{r.base_name ? ` (${r.base_name})` : ''}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Quantite</label>
              <input
                type="number"
                className="form-input"
                value={form.quantity}
                onChange={(e) => setForm((p) => ({ ...p, quantity: e.target.value }))}
                min="0"
              />
            </div>

            <div className="form-group">
              <label className="form-label">Etagere</label>
              <input
                type="text"
                className="form-input"
                value={form.shelf}
                onChange={(e) => setForm((p) => ({ ...p, shelf: e.target.value }))}
              />
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

      {/* Modal valeurs / specs */}
      <div className={`modal${showValuesModal ? ' active' : ''}`}>
        <div className="modal-content" style={{ maxWidth: '640px' }}>
          <div className="modal-header">
            <h3>Specs — {valuesAsset?.name ?? ''}</h3>
            <button className="modal-close" onClick={() => { setShowValuesModal(false); cancelValueEdit() }} aria-label="Fermer">&times;</button>
          </div>

          {valueError ? <div className="alert alert-danger">{valueError}</div> : null}

          {valuesLoading ? (
            <div className="text-center" style={{ padding: '1.5rem' }}>Chargement...</div>
          ) : specsForAsset.length === 0 ? (
            <div className="alert" style={{ marginBottom: '1rem' }}>
              Aucune spec definie pour ce type d'asset. Ajoutez-en depuis la page <strong>Types</strong>.
            </div>
          ) : (
            <table style={{ marginBottom: '1rem' }}>
              <thead>
                <tr>
                  <th>Spec</th>
                  <th>Valeur</th>
                  {editable && <th>Actions</th>}
                </tr>
              </thead>
              <tbody>
                {specsForAsset.map((spec) => {
                  const existing = assetValues.find((v) => v.spec_id === spec.id)
                  const isEditing = (editingValueId === (existing?.id ?? null) || (valueSpecId === spec.id && !editingValueId && !existing)) && (editingValueId !== null || valueSpecId === spec.id)

                  return (
                    <tr key={spec.id}>
                      <td>{spec.name}</td>
                      <td>
                        {isEditing ? (
                          <form onSubmit={saveValue} style={{ display: 'flex', gap: '0.5rem' }}>
                            <input
                              type="text"
                              className="form-input"
                              value={valueForm}
                              onChange={(e) => setValueForm(e.target.value)}
                              placeholder="Valeur..."
                              required
                              autoFocus
                              style={{ flex: 1 }}
                            />
                            <button type="submit" className="btn btn-sm btn-primary" disabled={savingValue}>
                              {savingValue ? '...' : '✓'}
                            </button>
                            <button type="button" className="btn btn-sm btn-secondary" onClick={cancelValueEdit}>✕</button>
                          </form>
                        ) : (
                          existing ? existing.value : <span style={{ opacity: 0.4 }}>—</span>
                        )}
                      </td>
                      {editable && !isEditing && (
                        <td className="flex gap-1">
                          {existing ? (
                            <>
                              <button className="btn btn-sm btn-secondary" onClick={() => startEditValue(existing)}>Edit</button>
                              <button className="btn btn-sm btn-danger" onClick={() => handleDeleteValue(existing.id)}>✕</button>
                            </>
                          ) : (
                            <button className="btn btn-sm btn-secondary" onClick={() => startAddValue(spec.id)}>+ Saisir</button>
                          )}
                        </td>
                      )}
                      {editable && isEditing && <td />}
                    </tr>
                  )
                })}
              </tbody>
            </table>
          )}

          <button className="btn btn-secondary" style={{ width: '100%' }} onClick={() => { setShowValuesModal(false); cancelValueEdit() }}>
            Fermer
          </button>
        </div>
      </div>
    </AppLayout>
  )
}