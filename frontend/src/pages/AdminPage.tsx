import { useCallback, useEffect, useMemo, useState } from 'react'
import type { FormEvent } from 'react'
import AppLayout from '../layouts/AppLayout'
import {
  fetchUsers, fetchRoles,
  createUser, updateUser, deleteUser, clearUserMfa,
  type UserCreatePayload, type UserUpdatePayload,
} from '../api/admin'
import { useAuth } from '../context/AuthContext'
import { formatDate } from '../utils/dates'
import type { User, Role } from '../types'

interface UserForm {
  username: string
  name: string
  password: string
  group_id: string
  active: boolean
}

const emptyForm: UserForm = {
  username: '',
  name: '',
  password: '',
  group_id: '',
  active: true,
}

export default function AdminPage() {
  const { user: currentUser } = useAuth()
  const isAdmin = currentUser?.role === 'admin'

  const [query, setQuery] = useState('')
  const [users, setUsers] = useState<User[]>([])
  const [roles, setRoles] = useState<Role[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const [showModal, setShowModal] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [form, setForm] = useState<UserForm>(emptyForm)
  const [saving, setSaving] = useState(false)

  const loadData = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const [u, r] = await Promise.all([fetchUsers(), fetchRoles()])
      setUsers(u)
      setRoles(r)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur de chargement')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { loadData() }, [loadData])

  const visibleUsers = useMemo(() => {
    return users.filter((user) => {
      const row = `${user.username} ${user.name ?? ''} ${user.role_name ?? ''}`.toLowerCase()
      return row.includes(query.toLowerCase())
    })
  }, [users, query])

  const activeCount = users.filter((u) => u.active).length

  const openCreateModal = () => {
    setEditingId(null)
    setForm({ ...emptyForm, group_id: roles[0]?.id ?? '' })
    setError('')
    setShowModal(true)
  }

  const openEditModal = (u: User) => {
    setEditingId(u.id)
    setForm({
      username: u.username,
      name: u.name ?? '',
      password: '',
      group_id: u.group_id,
      active: u.active,
    })
    setError('')
    setShowModal(true)
  }

  const handleSave = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setSaving(true)
    setError('')
    try {
      if (editingId) {
        const payload: UserUpdatePayload = {
          username: form.username,
          name: form.name || null,
          group_id: form.group_id,
          active: form.active,
        }
        if (form.password) payload.password = form.password
        await updateUser(editingId, payload)
      } else {
        if (!form.password) {
          setError('Mot de passe requis')
          setSaving(false)
          return
        }
        const payload: UserCreatePayload = {
          username: form.username,
          password: form.password,
          group_id: form.group_id,
          active: form.active,
        }
        if (form.name) payload.name = form.name
        await createUser(payload)
      }
      setShowModal(false)
      await loadData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (id: string, username: string) => {
    if (!confirm(`Supprimer l'utilisateur "${username}" ?`)) return
    try {
      await deleteUser(id)
      await loadData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur de suppression')
    }
  }

  const handleToggleActive = async (u: User) => {
    try {
      await updateUser(u.id, { active: !u.active })
      await loadData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur')
    }
  }

  const handleClearMfa = async (u: User) => {
    if (!confirm(`Reinitialiser le 2FA de "${u.username}" ? L'utilisateur devra le reconfigurer.`)) return
    try {
      await clearUserMfa(u.id)
      await loadData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur')
    }
  }

  return (
    <AppLayout>
      <section className="page-hero">
        <div className="page-meta">
          <span className="brand-sub">Administration</span>
          <div className="title">Centre de controle</div>
          <div className="subtitle">Superviser les roles, utilisateurs et la conformite du systeme.</div>
        </div>
        <div className="controls-row">
          <button className="btn btn-secondary btn-sm" onClick={loadData} disabled={loading}>
            {loading ? 'Chargement...' : '↻ Actualiser'}
          </button>
          {isAdmin && (
            <button className="btn btn-primary btn-sm" onClick={openCreateModal}>+ Nouvel utilisateur</button>
          )}
        </div>
      </section>

      {error && !showModal ? <div className="alert alert-danger">{error}</div> : null}

      <section className="stats-grid">
        <div className="stat-card success">
          <h3>Utilisateurs actifs</h3>
          <div className="stat-value">{activeCount}</div>
          <div className="stat-meta">Sur {users.length} total</div>
        </div>
        <div className="stat-card warning">
          <h3>Roles</h3>
          <div className="stat-value">{roles.length}</div>
          <div className="stat-meta">Profils disponibles</div>
        </div>
        <div className="stat-card">
          <h3>Utilisateurs inactifs</h3>
          <div className="stat-value">{users.length - activeCount}</div>
          <div className="stat-meta">Comptes desactives</div>
        </div>
      </section>

      <section className="data-table">
        <div className="table-header">
          <h3>Utilisateurs</h3>
          <div className="search-bar">
            <span className="search-icon">&#9776;</span>
            <input
              type="text"
              placeholder="Rechercher un utilisateur"
              aria-label="Recherche utilisateur"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>
        </div>
        <table>
          <thead>
            <tr>
              <th>Username</th>
              <th>Nom</th>
              <th>Role</th>
              <th>Status</th>
              <th>2FA</th>
              <th>Cree le</th>
              {isAdmin && <th>Actions</th>}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={isAdmin ? 7 : 6} className="text-center">Chargement...</td></tr>
            ) : visibleUsers.length === 0 ? (
              <tr><td colSpan={isAdmin ? 7 : 6} className="text-center">Aucun utilisateur correspondant.</td></tr>
            ) : (
              visibleUsers.map((u) => (
                <tr key={u.id}>
                  <td>{u.username}</td>
                  <td>{u.name ?? '—'}</td>
                  <td><span className="badge badge-info">{u.role_name?.toUpperCase() ?? '—'}</span></td>
                  <td>
                    <span className={`badge ${u.active ? 'badge-success' : 'badge-danger'}`}>
                      {u.active ? 'Actif' : 'Inactif'}
                    </span>
                  </td>
                  <td>
                    <span className={`badge ${u.MFA ? 'badge-success' : 'badge-warning'}`}>
                      {u.MFA ? 'Activee' : 'Desactivee'}
                    </span>
                  </td>
                  <td>{formatDate(u.DA)}</td>
                  {isAdmin && (
                    <td className="flex gap-1">
                      <button className="btn btn-sm btn-secondary" onClick={() => openEditModal(u)}>Edit</button>
                      <button
                        className="btn btn-sm btn-secondary"
                        onClick={() => handleToggleActive(u)}
                        title={u.active ? 'Desactiver' : 'Activer'}
                      >
                        {u.active ? 'Desactiver' : 'Activer'}
                      </button>
                      {u.MFA && (
                        <button
                          className="btn btn-sm btn-warning"
                          onClick={() => handleClearMfa(u)}
                          title="Reinitialiser le 2FA"
                        >
                          Reset 2FA
                        </button>
                      )}
                      <button className="btn btn-sm btn-danger" onClick={() => handleDelete(u.id, u.username)}>Supprimer</button>
                    </td>
                  )}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </section>

      <section className="panel">
        <div className="panel-header">
          <div className="panel-title">Roles du systeme</div>
        </div>
        <div className="stats-grid">
          {roles.map((role) => (
            <div key={role.id} className="stat-card">
              <h3>{role.name.toUpperCase()}</h3>
              <div className="stat-meta">{role.desc ?? '—'}</div>
              <div className="stat-value" style={{ fontSize: '1.2rem' }}>
                {users.filter((u) => u.group_id === role.id).length} utilisateur(s)
              </div>
            </div>
          ))}
        </div>
      </section>

      <div className={`modal${showModal ? ' active' : ''}`}>
        <div className="modal-content">
          <div className="modal-header">
            <h3>{editingId ? 'Modifier utilisateur' : 'Nouvel utilisateur'}</h3>
            <button className="modal-close" onClick={() => setShowModal(false)} aria-label="Fermer">&times;</button>
          </div>

          {error && showModal ? <div className="alert alert-danger">{error}</div> : null}

          <form onSubmit={handleSave}>
            <div className="form-group">
              <label className="form-label">Username *</label>
              <input
                type="text"
                className="form-input"
                value={form.username}
                onChange={(e) => setForm((p) => ({ ...p, username: e.target.value }))}
                required
                minLength={2}
                maxLength={35}
                pattern="[a-zA-Z0-9_-]+"
                placeholder="alphanumerique, _ ou -"
              />
            </div>

            <div className="form-group">
              <label className="form-label">Nom complet</label>
              <input
                type="text"
                className="form-input"
                value={form.name}
                onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))}
                placeholder="optionnel"
              />
            </div>

            <div className="form-group">
              <label className="form-label">{editingId ? 'Nouveau mot de passe' : 'Mot de passe *'}</label>
              <input
                type="password"
                className="form-input"
                value={form.password}
                onChange={(e) => setForm((p) => ({ ...p, password: e.target.value }))}
                required={!editingId}
                placeholder={editingId ? 'Laisser vide pour conserver' : ''}
                autoComplete="new-password"
              />
            </div>

            <div className="form-group">
              <label className="form-label">Role *</label>
              <select
                className="form-select"
                value={form.group_id}
                onChange={(e) => setForm((p) => ({ ...p, group_id: e.target.value }))}
                required
              >
                <option value="">Selectionner un role</option>
                {roles.map((r) => (
                  <option key={r.id} value={r.id}>{r.name}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="flex gap-1" style={{ alignItems: 'center' }}>
                <input
                  type="checkbox"
                  checked={form.active}
                  onChange={(e) => setForm((p) => ({ ...p, active: e.target.checked }))}
                />
                <span>Compte actif</span>
              </label>
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
