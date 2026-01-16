import { useState, useEffect, FormEvent } from 'react'
import { Layout } from '../components/Layout'
import { assetsApi, assetTypesApi, roomsApi } from '../services/api'

interface Asset {
  id: number
  name: string
  number: string | null
  status: string
  type: string | null
  type_id: number
  room_id: number | null
  room: string | null
  quantity: number | null
  shelf: string | null
  sensible: boolean | null
  created_at: string | null
  updated_at: string | null
}

interface AssetType {
  id: number
  type: string
}

interface Room {
  id: number
  room: string
  base_id: number
  base_name: string | null
}

export default function Assets() {
  const [assets, setAssets] = useState<Asset[]>([])
  const [assetTypes, setAssetTypes] = useState<AssetType[]>([])
  const [rooms, setRooms] = useState<Room[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  // Pagination
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [total, setTotal] = useState(0)

  // Filters
  const [statusFilter, setStatusFilter] = useState('')
  const [typeFilter, setTypeFilter] = useState('')
  const [searchQuery, setSearchQuery] = useState('')

  // Modal
  const [showModal, setShowModal] = useState(false)
  const [editingAsset, setEditingAsset] = useState<Asset | null>(null)

  // Form
  const [formData, setFormData] = useState({
    name: '',
    number: '',
    asset_type_id: '',
    status: 'STOCK',
    room_id: '',
    quantity: '',
    shelf: '',
    sensible: false,
  })

  const loadAssets = async () => {
    setIsLoading(true)
    setError('')
    try {
      const params: {
        page: number
        per_page: number
        status?: string
        type_id?: number
        search?: string
      } = { page, per_page: 20 }
      if (statusFilter) params.status = statusFilter
      if (typeFilter) params.type_id = parseInt(typeFilter)
      if (searchQuery) params.search = searchQuery

      const response = await assetsApi.getAll(params)
      setAssets(response.data.assets || [])
      setTotal(response.data.total || 0)
      setTotalPages(response.data.pages || 1)
    } catch (err) {
      console.error('Error loading assets:', err)
      setError('Erreur lors du chargement des assets')
    } finally {
      setIsLoading(false)
    }
  }

  const loadFilters = async () => {
    try {
      const [typesRes, roomsRes] = await Promise.all([
        assetTypesApi.getAll(),
        roomsApi.getAll(),
      ])
      setAssetTypes(typesRes.data.asset_types || [])
      setRooms(roomsRes.data.rooms || [])
    } catch (err) {
      console.error('Error loading filters:', err)
    }
  }

  useEffect(() => {
    loadFilters()
  }, [])

  useEffect(() => {
    loadAssets()
  }, [page, statusFilter, typeFilter])

  const handleSearch = () => {
    setPage(1)
    loadAssets()
  }

  const openCreateModal = () => {
    setEditingAsset(null)
    setFormData({
      name: '',
      number: '',
      asset_type_id: '',
      status: 'STOCK',
      room_id: '',
      quantity: '',
      shelf: '',
      sensible: false,
    })
    setShowModal(true)
  }

  const openEditModal = (asset: Asset) => {
    setEditingAsset(asset)
    setFormData({
      name: asset.name,
      number: asset.number || '',
      asset_type_id: asset.type_id.toString(),
      status: asset.status,
      room_id: asset.room_id?.toString() || '',
      quantity: asset.quantity?.toString() || '',
      shelf: asset.shelf || '',
      sensible: asset.sensible || false,
    })
    setShowModal(true)
  }

  const closeModal = () => {
    setShowModal(false)
    setEditingAsset(null)
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')

    try {
      const data = {
        name: formData.name,
        asset_type_id: parseInt(formData.asset_type_id),
        status: formData.status,
        number: formData.number || undefined,
        room_id: formData.room_id ? parseInt(formData.room_id) : undefined,
        quantity: formData.quantity ? parseInt(formData.quantity) : undefined,
        shelf: formData.shelf || undefined,
        sensible: formData.sensible,
      }

      if (editingAsset) {
        await assetsApi.update(editingAsset.id, data)
        setSuccess('Asset mis à jour avec succès')
      } else {
        await assetsApi.create(data)
        setSuccess('Asset créé avec succès')
      }

      closeModal()
      loadAssets()
    } catch (err: unknown) {
      const error = err as { response?: { data?: { error?: string; message?: string } } }
      setError(error.response?.data?.error || error.response?.data?.message || 'Erreur lors de la sauvegarde')
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Êtes-vous sûr de vouloir supprimer cet asset ?')) return

    try {
      await assetsApi.delete(id)
      setSuccess('Asset supprimé avec succès')
      loadAssets()
    } catch (err) {
      console.error('Error deleting asset:', err)
      setError('Erreur lors de la suppression')
    }
  }

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'STOCK':
        return 'badge-success'
      case 'TRANSIT':
        return 'badge-warning'
      case 'DESTROYED':
      case 'LOST':
        return 'badge-danger'
      default:
        return 'badge-info'
    }
  }

  return (
    <Layout>
      <section className="page-hero">
        <div className="page-meta">
          <span className="brand-sub">Inventaire</span>
          <div className="title">Gestion des assets</div>
          <div className="subtitle">
            Filtrer, créer et superviser les équipements.
          </div>
        </div>
        <div className="controls-row">
          <span className="chip">Flux en direct</span>
          <button className="btn btn-primary btn-sm" onClick={openCreateModal}>
            + Nouvel asset
          </button>
        </div>
      </section>

      {error && <div className="alert alert-danger">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      <section className="panel">
        <div className="panel-header">
          <div className="panel-title">Filtres</div>
          <div className="search-bar" style={{ width: 'min(360px, 100%)' }}>
            <span style={{ opacity: 0.6 }}>&#9776;</span>
            <input
              type="text"
              placeholder="Rechercher un asset"
              aria-label="Rechercher un asset"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            />
          </div>
        </div>
        <div className="filters">
          <select
            className="form-select"
            value={typeFilter}
            onChange={(e) => {
              setTypeFilter(e.target.value)
              setPage(1)
            }}
          >
            <option value="">Tous les types</option>
            {assetTypes.map((type) => (
              <option key={type.id} value={type.id}>
                {type.type}
              </option>
            ))}
          </select>
          <select
            className="form-select"
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value)
              setPage(1)
            }}
          >
            <option value="">Tous les statuts</option>
            <option value="STOCK">Stock</option>
            <option value="TRANSIT">Transit</option>
            <option value="PURCHASED">Acheté</option>
            <option value="SOLD">Vendu</option>
            <option value="DESTROYED">Détruit</option>
            <option value="LOST">Perdu</option>
          </select>
        </div>
      </section>

      <section className="data-table">
        <div className="table-header">
          <h3>Liste des assets ({total})</h3>
        </div>
        <table>
          <thead>
            <tr>
              <th>Numéro</th>
              <th>Nom</th>
              <th>Type</th>
              <th>Statut</th>
              <th>Localisation</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              <tr>
                <td colSpan={6} className="text-center">
                  <div className="spinner"></div>
                </td>
              </tr>
            ) : assets.length === 0 ? (
              <tr>
                <td colSpan={6} className="text-center">
                  Aucun asset trouvé
                </td>
              </tr>
            ) : (
              assets.map((asset) => (
                <tr key={asset.id}>
                  <td>{asset.number || '-'}</td>
                  <td>{asset.name}</td>
                  <td>{asset.type || '-'}</td>
                  <td>
                    <span className={`badge ${getStatusBadgeClass(asset.status)}`}>
                      {asset.status}
                    </span>
                  </td>
                  <td>{asset.room || '-'}</td>
                  <td className="flex gap-1">
                    <button
                      className="btn btn-sm btn-secondary"
                      onClick={() => openEditModal(asset)}
                    >
                      Edit
                    </button>
                    <button
                      className="btn btn-sm btn-danger"
                      onClick={() => handleDelete(asset.id)}
                    >
                      Supprimer
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
        {totalPages > 1 && (
          <div className="pagination">
            {Array.from({ length: totalPages }, (_, i) => i + 1).map((p) => (
              <button
                key={p}
                className={p === page ? 'active' : ''}
                onClick={() => setPage(p)}
              >
                {p}
              </button>
            ))}
          </div>
        )}
      </section>

      {/* Modal */}
      <div className={`modal ${showModal ? 'active' : ''}`}>
        <div className="modal-content">
          <div className="modal-header">
            <h3>{editingAsset ? 'Modifier asset' : 'Nouvel asset'}</h3>
            <button className="modal-close" onClick={closeModal}>
              &times;
            </button>
          </div>

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Type d'asset *</label>
              <select
                className="form-select"
                value={formData.asset_type_id}
                onChange={(e) =>
                  setFormData({ ...formData, asset_type_id: e.target.value })
                }
                required
              >
                <option value="">Sélectionner un type</option>
                {assetTypes.map((type) => (
                  <option key={type.id} value={type.id}>
                    {type.type}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Nom *</label>
              <input
                type="text"
                className="form-input"
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Numéro</label>
              <input
                type="text"
                className="form-input"
                value={formData.number}
                onChange={(e) =>
                  setFormData({ ...formData, number: e.target.value })
                }
              />
            </div>

            <div className="form-group">
              <label className="form-label">Statut</label>
              <select
                className="form-select"
                value={formData.status}
                onChange={(e) =>
                  setFormData({ ...formData, status: e.target.value })
                }
              >
                <option value="STOCK">Stock</option>
                <option value="TRANSIT">Transit</option>
                <option value="PURCHASED">Acheté</option>
                <option value="SOLD">Vendu</option>
                <option value="DESTROYED">Détruit</option>
                <option value="LOST">Perdu</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Local</label>
              <select
                className="form-select"
                value={formData.room_id}
                onChange={(e) =>
                  setFormData({ ...formData, room_id: e.target.value })
                }
              >
                <option value="">Sélectionner un local</option>
                {rooms.map((room) => (
                  <option key={room.id} value={room.id}>
                    {room.room} {room.base_name && `(${room.base_name})`}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Quantité</label>
              <input
                type="number"
                className="form-input"
                value={formData.quantity}
                onChange={(e) =>
                  setFormData({ ...formData, quantity: e.target.value })
                }
              />
            </div>

            <div className="form-group">
              <label className="form-label">Étagère</label>
              <input
                type="text"
                className="form-input"
                value={formData.shelf}
                onChange={(e) =>
                  setFormData({ ...formData, shelf: e.target.value })
                }
              />
            </div>

            <div className="flex gap-2">
              <button type="submit" className="btn btn-primary" style={{ flex: 1 }}>
                Enregistrer
              </button>
              <button
                type="button"
                className="btn btn-secondary"
                style={{ flex: 1 }}
                onClick={closeModal}
              >
                Annuler
              </button>
            </div>
          </form>
        </div>
      </div>
    </Layout>
  )
}
