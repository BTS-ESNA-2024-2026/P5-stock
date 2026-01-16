import { useState, useEffect } from 'react'
import { Layout } from '../components/Layout'
import { assetsApi, assetTypesApi } from '../services/api'

interface DashboardStats {
  totalAssets: number
  availableAssets: number
  inUseAssets: number
  maintenanceAssets: number
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats>({
    totalAssets: 0,
    availableAssets: 0,
    inUseAssets: 0,
    maintenanceAssets: 0,
  })
  const [assetTypes, setAssetTypes] = useState<{ id: number; type: string }[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  const loadDashboard = async () => {
    setIsLoading(true)
    setError('')
    try {
      const [assetsRes, typesRes] = await Promise.all([
        assetsApi.getAll({ per_page: 1000 }),
        assetTypesApi.getAll(),
      ])

      const assets = assetsRes.data.assets || []
      setStats({
        totalAssets: assetsRes.data.total || assets.length,
        availableAssets: assets.filter((a: { status: string }) => a.status === 'STOCK').length,
        inUseAssets: assets.filter((a: { status: string }) => a.status === 'TRANSIT').length,
        maintenanceAssets: assets.filter((a: { status: string }) => a.status === 'PURCHASED').length,
      })

      setAssetTypes(typesRes.data.asset_types || [])
    } catch (err) {
      console.error('Error loading dashboard:', err)
      setError('Erreur lors du chargement des données')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadDashboard()
  }, [])

  return (
    <Layout>
      <section className="page-hero">
        <div className="page-meta">
          <span className="brand-sub">Vue d'ensemble</span>
          <div className="title">Tableau de bord</div>
          <div className="subtitle">
            Synthèse en temps réel des missions et assets.
          </div>
        </div>
        <div className="controls-row">
          <button
            className="icon-btn"
            onClick={loadDashboard}
            title="Actualiser"
          >
            &#8635;
          </button>
          <button className="btn btn-primary btn-sm" onClick={loadDashboard}>
            Actualiser
          </button>
        </div>
      </section>

      {error && <div className="alert alert-danger">{error}</div>}

      <section className="panel">
        <div className="panel-header">
          <div className="panel-title">Indicateurs clé</div>
          <div className="search-bar">
            <span style={{ opacity: 0.6 }}>&#9776;</span>
            <input
              type="text"
              placeholder="Rechercher une information rapide"
              aria-label="Recherche"
            />
          </div>
        </div>
        <div className="stats-grid">
          {isLoading ? (
            <div className="spinner"></div>
          ) : (
            <>
              <div className="stat-card">
                <h3>Total Assets</h3>
                <div className="stat-value">{stats.totalAssets}</div>
                <div className="stat-meta">Équipements enregistrés</div>
              </div>
              <div className="stat-card success">
                <h3>Disponibles</h3>
                <div className="stat-value">{stats.availableAssets}</div>
                <div className="stat-meta">En stock</div>
              </div>
              <div className="stat-card warning">
                <h3>En transit</h3>
                <div className="stat-value">{stats.inUseAssets}</div>
                <div className="stat-meta">En déplacement</div>
              </div>
              <div className="stat-card danger">
                <h3>Achetés</h3>
                <div className="stat-value">{stats.maintenanceAssets}</div>
                <div className="stat-meta">Récemment achetés</div>
              </div>
            </>
          )}
        </div>
      </section>

      <section className="panel">
        <div className="panel-header">
          <div className="panel-title">Types d'assets</div>
        </div>
        <div className="stats-grid">
          {assetTypes.map((type) => (
            <div key={type.id} className="stat-card">
              <h3>{type.type}</h3>
              <div className="stat-value">#{type.id}</div>
              <div className="stat-meta">Type d'équipement</div>
            </div>
          ))}
        </div>
      </section>

      <section className="data-table">
        <div className="table-header">
          <h3>Activité récente</h3>
          <span className="chip">Live feed</span>
        </div>
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Action</th>
              <th>Description</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>{new Date().toLocaleDateString('fr-FR')}</td>
              <td>
                <span className="badge badge-info">Connexion</span>
              </td>
              <td>Connexion au tableau de bord</td>
            </tr>
          </tbody>
        </table>
      </section>
    </Layout>
  )
}
