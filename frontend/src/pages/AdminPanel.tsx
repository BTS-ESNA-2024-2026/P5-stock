import { Layout } from '../components/Layout'

export default function AdminPanel() {
  return (
    <Layout>
      <section className="page-hero">
        <div className="page-meta">
          <span className="brand-sub">Administration</span>
          <div className="title">Centre de contrôle</div>
          <div className="subtitle">
            Superviser les rôles, utilisateurs et la conformité du système.
          </div>
        </div>
        <div className="controls-row">
          <span className="chip">Audit actif</span>
          <button className="btn btn-primary btn-sm">Actualiser</button>
        </div>
      </section>

      <section className="stats-grid">
        <div className="stat-card success">
          <h3>Utilisateurs actifs</h3>
          <div className="stat-value">--</div>
          <div className="stat-meta">Connectés dans les 24h</div>
        </div>
        <div className="stat-card warning">
          <h3>Rôles</h3>
          <div className="stat-value">5</div>
          <div className="stat-meta">Profils disponibles</div>
        </div>
        <div className="stat-card">
          <h3>Demandes en attente</h3>
          <div className="stat-value">--</div>
          <div className="stat-meta">Approvals / créations</div>
        </div>
        <div className="stat-card danger">
          <h3>Alertes sécurité</h3>
          <div className="stat-value">--</div>
          <div className="stat-meta">À traiter</div>
        </div>
      </section>

      <section className="panel">
        <div className="panel-header">
          <div className="panel-title">Actions rapides</div>
        </div>
        <div className="controls-row">
          <button className="btn btn-primary btn-sm">+ Nouvel utilisateur</button>
          <button className="btn btn-secondary btn-sm">+ Nouveau rôle</button>
          <button className="btn btn-secondary btn-sm">Exporter journal</button>
        </div>
      </section>

      <section className="data-table">
        <div className="table-header">
          <h3>Utilisateurs</h3>
          <div className="search-bar">
            <span style={{ opacity: 0.6 }}>&#9776;</span>
            <input
              type="text"
              placeholder="Rechercher un utilisateur"
              aria-label="Recherche utilisateur"
            />
          </div>
        </div>
        <table>
          <thead>
            <tr>
              <th>Nom</th>
              <th>Rôle</th>
              <th>Status</th>
              <th>Dernière connexion</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Jean Dupont</td>
              <td>
                <span className="badge badge-info">ADMIN</span>
              </td>
              <td>
                <span className="badge badge-success">Actif</span>
              </td>
              <td>2025-01-05 10:22</td>
              <td className="flex gap-1">
                <button className="btn btn-sm btn-secondary">Edit</button>
                <button className="btn btn-sm btn-danger">Suspendre</button>
              </td>
            </tr>
            <tr>
              <td>Marie Martin</td>
              <td>
                <span className="badge badge-info">OPERATEUR</span>
              </td>
              <td>
                <span className="badge badge-warning">En attente</span>
              </td>
              <td>2025-01-04 21:11</td>
              <td className="flex gap-1">
                <button className="btn btn-sm btn-secondary">Edit</button>
                <button className="btn btn-sm btn-danger">Suspendre</button>
              </td>
            </tr>
          </tbody>
        </table>
      </section>

      <section className="data-table">
        <div className="table-header">
          <h3>Rôles et permissions</h3>
        </div>
        <table>
          <thead>
            <tr>
              <th>Rôle</th>
              <th>Description</th>
              <th>Permissions clé</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>ADMIN</td>
              <td>Contrôle global sur la plateforme</td>
              <td>Users, Assets, Rapports</td>
            </tr>
            <tr>
              <td>TECHNICIAN</td>
              <td>Gestion technique des équipements</td>
              <td>Assets, Bases, Rooms</td>
            </tr>
            <tr>
              <td>USER</td>
              <td>Exécution des opérations et suivi</td>
              <td>Assets, Missions</td>
            </tr>
            <tr>
              <td>VIEWER</td>
              <td>Consultation uniquement</td>
              <td>Lecture seule</td>
            </tr>
          </tbody>
        </table>
      </section>

      <section className="data-table">
        <div className="table-header">
          <h3>Journal sécurité</h3>
          <span className="chip">Live feed</span>
        </div>
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Événement</th>
              <th>Détail</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>{new Date().toLocaleString('fr-FR')}</td>
              <td>
                <span className="badge badge-info">Connexion</span>
              </td>
              <td>Connexion au panneau d'administration</td>
            </tr>
          </tbody>
        </table>
      </section>
    </Layout>
  )
}
