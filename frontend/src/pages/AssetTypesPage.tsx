import { useCallback, useEffect, useMemo, useState } from 'react'
import type { FormEvent } from 'react'
import AppLayout from '../layouts/AppLayout'
import {
  fetchAssetTypes, createAssetType, updateAssetType, deleteAssetType,
  fetchSpecs, createSpec, updateSpec, deleteSpec,
} from '../api/assets'
import { useAuth } from '../context/AuthContext'
import type { AssetType, Spec } from '../types'

const ROLE_HIERARCHY = ['viewer', 'user', 'secure_user', 'technician', 'admin']

function canEdit(role: string | undefined): boolean {
  return ROLE_HIERARCHY.indexOf(role ?? '') >= ROLE_HIERARCHY.indexOf('technician')
}

export default function AssetTypesPage() {
  const { user } = useAuth()
  const [search, setSearch] = useState('')
  const [assetTypes, setAssetTypes] = useState<AssetType[]>([])
  const [specs, setSpecs] = useState<Spec[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  // Modal type
  const [showTypeModal, setShowTypeModal] = useState(false)
  const [editingTypeId, setEditingTypeId] = useState<string | null>(null)
  const [typeForm, setTypeForm] = useState({ type: '' })

  // Panel specs
  const [selectedTypeId, setSelectedTypeId] = useState<string | null>(null)

  // Modal spec — type_id is required so we can create from the global button
  // even without a selected type in the side panel.
  const [showSpecModal, setShowSpecModal] = useState(false)
  const [editingSpecId, setEditingSpecId] = useState<string | null>(null)
  const [specForm, setSpecForm] = useState({ name: '', type_id: '' })

  const editable = canEdit(user?.role)

  const loadData = useCallback(async () => {
    setLoading(true)
    try {
      const [t, s] = await Promise.all([fetchAssetTypes(), fetchSpecs()])
      setAssetTypes(t)
      setSpecs(s)
    } catch {
      setError('Erreur de chargement')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { loadData() }, [loadData])

  const filtered = useMemo(() =>
    assetTypes.filter((t) => t.type.toLowerCase().includes(search.toLowerCase())),
    [assetTypes, search]
  )

  const selectedType = assetTypes.find((t) => t.id === selectedTypeId) ?? null
  const selectedSpecs = specs.filter((s) => s.type_id === selectedTypeId)

  // ---- Type modal ----
  const openCreateTypeModal = () => {
    setEditingTypeId(null)
    setTypeForm({ type: '' })
    setError('')
    setShowTypeModal(true)
  }

  const openEditTypeModal = (t: AssetType) => {
    setEditingTypeId(t.id)
    setTypeForm({ type: t.type })
    setError('')
    setShowTypeModal(true)
  }

  const handleSaveType = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setSaving(true)
    setError('')
    try {
      if (editingTypeId) {
        await updateAssetType(editingTypeId, { type: typeForm.type })
      } else {
        await createAssetType({ type: typeForm.type })
      }
      setShowTypeModal(false)
      await loadData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur')
    } finally {
      setSaving(false)
    }
  }

  const handleDeleteType = async (id: string) => {
    if (!confirm('Supprimer ce type ? Les specs associees seront aussi supprimees.')) return
    try {
      await deleteAssetType(id)
      if (selectedTypeId === id) setSelectedTypeId(null)
      await loadData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur de suppression')
    }
  }

  // ---- Spec modal ----
  const openCreateSpecModal = () => {
    setEditingSpecId(null)
    // Pre-select the side-panel type if one is open, otherwise the first type.
    setSpecForm({ name: '', type_id: selectedTypeId ?? assetTypes[0]?.id ?? '' })
    setError('')
    setShowSpecModal(true)
  }

  const openEditSpecModal = (s: Spec) => {
    setEditingSpecId(s.id)
    setSpecForm({ name: s.name, type_id: s.type_id })
    setError('')
    setShowSpecModal(true)
  }

  const handleSaveSpec = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!editingSpecId && !specForm.type_id) {
      setError('Choisissez un type')
      return
    }
    setSaving(true)
    setError('')
    try {
      if (editingSpecId) {
        await updateSpec(editingSpecId, { name: specForm.name })
      } else {
        await createSpec({ type_id: specForm.type_id, name: specForm.name })
      }
      setShowSpecModal(false)
      await loadData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur')
    } finally {
      setSaving(false)
    }
  }

  const handleDeleteSpec = async (id: string) => {
    if (!confirm('Supprimer cette spec ?')) return
    try {
      await deleteSpec(id)
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
          <div className="title">Types d'assets &amp; Specs</div>
          <div className="subtitle">Gerer les categories d'equipements et leurs specifications.</div>
        </div>
        <div className="controls-row">
          <button className="btn btn-secondary btn-sm" onClick={loadData} disabled={loading}>
            {loading ? 'Chargement...' : '↻ Actualiser'}
          </button>
          {editable && (
            <button className="btn btn-primary btn-sm" onClick={openCreateTypeModal}>+ Nouveau type</button>
          )}
        </div>
      </section>

      {error && !showTypeModal && !showSpecModal ? <div className="alert alert-danger">{error}</div> : null}

      <section className="panel">
        <div className="panel-header">
          <div className="panel-title">Filtres</div>
          <div className="search-bar search-compact">
            <span className="search-icon">&#9776;</span>
            <input
              type="text"
              placeholder="Rechercher un type"
              aria-label="Rechercher un type"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
        </div>
      </section>

      <div style={{ display: 'grid', gridTemplateColumns: selectedTypeId ? '1fr 1fr' : '1fr', gap: '1.5rem' }}>
        <section className="data-table">
          <div className="table-header">
            <h3>Types d'assets</h3>
            <span className="chip">{filtered.length} resultat(s)</span>
          </div>
          <table>
            <thead>
              <tr>
                <th>Type</th>
                <th>Specs</th>
                {editable && <th>Actions</th>}
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={editable ? 3 : 2} className="text-center">Chargement...</td></tr>
              ) : filtered.length === 0 ? (
                <tr><td colSpan={editable ? 3 : 2} className="text-center">Aucun type correspondant.</td></tr>
              ) : (
                filtered.map((t) => {
                  const specCount = specs.filter((s) => s.type_id === t.id).length
                  const isSelected = selectedTypeId === t.id
                  return (
                    <tr
                      key={t.id}
                      style={{ cursor: 'pointer', background: isSelected ? 'var(--bg-elevated, #1e2433)' : undefined }}
                      onClick={() => setSelectedTypeId(isSelected ? null : t.id)}
                    >
                      <td>{t.type}</td>
                      <td><span className="chip">{specCount}</span></td>
                      {editable && (
                        <td className="flex gap-1" onClick={(e) => e.stopPropagation()}>
                          <button className="btn btn-sm btn-secondary" onClick={() => openEditTypeModal(t)}>Edit</button>
                          <button className="btn btn-sm btn-danger" onClick={() => handleDeleteType(t.id)}>Supprimer</button>
                        </td>
                      )}
                    </tr>
                  )
                })
              )}
            </tbody>
          </table>
        </section>

        {selectedType && (
          <section className="data-table">
            <div className="table-header">
              <h3>Specs — {selectedType.type}</h3>
              <div className="flex gap-1">
                {editable && (
                  <button className="btn btn-primary btn-sm" onClick={openCreateSpecModal}>+ Spec</button>
                )}
                <button className="btn btn-secondary btn-sm" onClick={() => setSelectedTypeId(null)}>&times;</button>
              </div>
            </div>
            <table>
              <thead>
                <tr>
                  <th>Nom de la spec</th>
                  {editable && <th>Actions</th>}
                </tr>
              </thead>
              <tbody>
                {selectedSpecs.length === 0 ? (
                  <tr><td colSpan={editable ? 2 : 1} className="text-center">Aucune spec pour ce type.</td></tr>
                ) : (
                  selectedSpecs.map((s) => (
                    <tr key={s.id}>
                      <td>{s.name}</td>
                      {editable && (
                        <td className="flex gap-1">
                          <button className="btn btn-sm btn-secondary" onClick={() => openEditSpecModal(s)}>Edit</button>
                          <button className="btn btn-sm btn-danger" onClick={() => handleDeleteSpec(s.id)}>Supprimer</button>
                        </td>
                      )}
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </section>
        )}
      </div>

      {/* Modal type */}
      {showTypeModal && (
      <div className="modal active">
        <div className="modal-content">
          <div className="modal-header">
            <h3>{editingTypeId ? 'Modifier le type' : 'Nouveau type d\'asset'}</h3>
            <button className="modal-close" onClick={() => setShowTypeModal(false)} aria-label="Fermer">&times;</button>
          </div>
          {error && showTypeModal ? <div className="alert alert-danger">{error}</div> : null}
          <form onSubmit={handleSaveType}>
            <div className="form-group">
              <label className="form-label">Nom du type *</label>
              <input
                type="text"
                className="form-input"
                value={typeForm.type}
                onChange={(e) => setTypeForm({ type: e.target.value })}
                placeholder="ex: Vehicule, Armement, MRE..."
                required
              />
            </div>
            <div className="flex gap-2">
              <button type="submit" className="btn btn-primary flex-grow" disabled={saving}>
                {saving ? 'Enregistrement...' : 'Enregistrer'}
              </button>
              <button type="button" className="btn btn-secondary flex-grow" onClick={() => setShowTypeModal(false)}>
                Annuler
              </button>
            </div>
          </form>
        </div>
      </div>
      )}

      {/* Modal spec */}
      {showSpecModal && (
      <div className="modal active">
        <div className="modal-content">
          <div className="modal-header">
            <h3>{editingSpecId ? 'Modifier la spec' : 'Nouvelle spec'}</h3>
            <button className="modal-close" onClick={() => setShowSpecModal(false)} aria-label="Fermer">&times;</button>
          </div>
          {error && showSpecModal ? <div className="alert alert-danger">{error}</div> : null}
          <form onSubmit={handleSaveSpec}>
            <div className="form-group">
              <label className="form-label">Type d'asset *</label>
              <select
                className="form-select"
                value={specForm.type_id}
                onChange={(e) => setSpecForm((p) => ({ ...p, type_id: e.target.value }))}
                disabled={Boolean(editingSpecId)}
                required
              >
                <option value="">Selectionner un type</option>
                {assetTypes.map((t) => (
                  <option key={t.id} value={t.id}>{t.type}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Nom de la spec *</label>
              <input
                type="text"
                className="form-input"
                value={specForm.name}
                onChange={(e) => setSpecForm((p) => ({ ...p, name: e.target.value }))}
                placeholder="ex: Kilometrage, Date d'expiration, Calibre..."
                required
              />
            </div>
            <div className="flex gap-2">
              <button type="submit" className="btn btn-primary flex-grow" disabled={saving}>
                {saving ? 'Enregistrement...' : 'Enregistrer'}
              </button>
              <button type="button" className="btn btn-secondary flex-grow" onClick={() => setShowSpecModal(false)}>
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
