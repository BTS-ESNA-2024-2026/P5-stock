import { useMemo, useState } from 'react'
import type { FormEvent } from 'react'
import AppLayout from '../layouts/AppLayout'
import type { AssetRecord, AssetStatus } from '../types/assets'

export default function AssetsPage() {
  const [search, setSearch] = useState('')
  const [typeFilter, setTypeFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [assets, setAssets] = useState<AssetRecord[]>([
    { id: 'A-100', number: 'VX-190', name: 'Drone Orion', type: 'Drone', status: 'AVAILABLE', room: 'Hangar 3' },
    { id: 'A-101', number: 'TR-481', name: 'Camion Atlas', type: 'Vehicule', status: 'IN_USE', room: 'Base Nord' },
    { id: 'A-102', number: 'RD-322', name: 'Radio Echo', type: 'Communication', status: 'MAINTENANCE', room: 'Atelier 2' },
  ])

  const [form, setForm] = useState<AssetRecord>({
    id: '',
    number: '',
    name: '',
    type: '',
    status: 'AVAILABLE',
    room: '',
  })

  const types = useMemo(() => ['Drone', 'Vehicule', 'Communication', 'Informatique'], [])

  const filteredAssets = useMemo(() => {
    return assets.filter((asset) => {
      const matchSearch = `${asset.number} ${asset.name} ${asset.room}`.toLowerCase().includes(search.toLowerCase())
      const matchType = typeFilter ? asset.type === typeFilter : true
      const matchStatus = statusFilter ? asset.status === statusFilter : true
      return matchSearch && matchType && matchStatus
    })
  }, [assets, search, statusFilter, typeFilter])

  const openCreateModal = () => {
    setEditingId(null)
    setForm({ id: '', number: '', name: '', type: '', status: 'AVAILABLE', room: '' })
    setShowModal(true)
  }

  const openEditModal = (asset: AssetRecord) => {
    setEditingId(asset.id)
    setForm(asset)
    setShowModal(true)
  }

  const saveAsset = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (editingId) {
      setAssets((previous) => previous.map((asset) => (asset.id === editingId ? form : asset)))
    } else {
      setAssets((previous) => [
        ...previous,
        {
          ...form,
          id: crypto.randomUUID(),
        },
      ])
    }
    setShowModal(false)
  }

  return (
    <AppLayout>
      <section className="page-hero">
        <div className="page-meta">
          <span className="brand-sub">Inventaire</span>
          <div className="title">Gestion des assets</div>
          <div className="subtitle">Filtrer, creer et superviser les equipements.</div>
        </div>
        <div className="controls-row">
          <span className="chip">Flux en direct</span>
          <button className="btn btn-primary btn-sm" onClick={openCreateModal}>+ Nouvel asset</button>
        </div>
      </section>

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
              onChange={(event) => setSearch(event.target.value)}
            />
          </div>
        </div>
        <div className="filters">
          <select className="form-select" value={typeFilter} onChange={(event) => setTypeFilter(event.target.value)}>
            <option value="">Selectionner un type</option>
            {types.map((type) => (
              <option key={type} value={type}>{type}</option>
            ))}
          </select>
          <select className="form-select" value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
            <option value="">Tous les statuts</option>
            <option value="AVAILABLE">Disponible</option>
            <option value="IN_USE">En utilisation</option>
            <option value="MAINTENANCE">Maintenance</option>
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
            {filteredAssets.length === 0 ? (
              <tr>
                <td colSpan={6} className="text-center">Aucun asset correspondant.</td>
              </tr>
            ) : (
              filteredAssets.map((asset) => (
                <tr key={asset.id}>
                  <td>{asset.number}</td>
                  <td>{asset.name}</td>
                  <td>{asset.type}</td>
                  <td>
                    <span className={`badge ${asset.status === 'AVAILABLE' ? 'badge-success' : asset.status === 'IN_USE' ? 'badge-info' : 'badge-warning'}`}>
                      {asset.status === 'AVAILABLE' ? 'Disponible' : asset.status === 'IN_USE' ? 'En utilisation' : 'Maintenance'}
                    </span>
                  </td>
                  <td>{asset.room}</td>
                  <td className="flex gap-1">
                    <button className="btn btn-sm btn-secondary" onClick={() => openEditModal(asset)}>Edit</button>
                    <button
                      className="btn btn-sm btn-danger"
                      onClick={() => setAssets((previous) => previous.filter((item) => item.id !== asset.id))}
                    >
                      Supprimer
                    </button>
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

          <form onSubmit={saveAsset}>
            <div className="form-group">
              <label className="form-label">Type d'asset *</label>
              <select
                className="form-select"
                value={form.type}
                onChange={(event) => setForm((previous) => ({ ...previous, type: event.target.value }))}
                required
              >
                <option value="">Selectionner un type</option>
                {types.map((type) => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Nom *</label>
              <input
                type="text"
                className="form-input"
                value={form.name}
                onChange={(event) => setForm((previous) => ({ ...previous, name: event.target.value }))}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Numero *</label>
              <input
                type="text"
                className="form-input"
                value={form.number}
                onChange={(event) => setForm((previous) => ({ ...previous, number: event.target.value }))}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Statut</label>
              <select
                className="form-select"
                value={form.status}
                onChange={(event) => setForm((previous) => ({ ...previous, status: event.target.value as AssetStatus }))}
              >
                <option value="AVAILABLE">Disponible</option>
                <option value="IN_USE">En utilisation</option>
                <option value="MAINTENANCE">Maintenance</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Localisation</label>
              <input
                type="text"
                className="form-input"
                value={form.room}
                onChange={(event) => setForm((previous) => ({ ...previous, room: event.target.value }))}
                placeholder="Batiment / salle"
              />
            </div>

            <div className="flex gap-2">
              <button type="submit" className="btn btn-primary flex-grow">Enregistrer</button>
              <button type="button" className="btn btn-secondary flex-grow" onClick={() => setShowModal(false)}>Annuler</button>
            </div>
          </form>
        </div>
      </div>
    </AppLayout>
  )
}