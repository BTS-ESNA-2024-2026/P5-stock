import { useState, FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const navigate = useNavigate()
  const { login } = useAuth()

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      await login(username, password)
      navigate('/dashboard')
    } catch (err: unknown) {
      const error = err as { response?: { data?: { message?: string } } }
      setError(error.response?.data?.message || 'Erreur de connexion')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="shell">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark">PSSTOCK</span>
          <span className="brand-sub">secure access</span>
        </div>
        <div className="top-actions">
          <span className="chip">Centre logistique</span>
          <span className="chip">Accès sécurisé</span>
        </div>
      </header>

      <main className="auth">
        <div className="auth-card">
          <div className="auth-header">
            <span className="brand-sub">Portail opérationnel</span>
            <div className="auth-title">Connexion</div>
            <p className="subtitle">
              Accès au tableau de bord et à la supervision PSSTOCK.
            </p>
          </div>

          {error && (
            <div className="alert alert-danger mb-2">{error}</div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="username" className="form-label">
                Username
              </label>
              <input
                type="text"
                id="username"
                className="form-input"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                placeholder="Username"
                autoComplete="username"
              />
            </div>

            <div className="form-group">
              <label htmlFor="password" className="form-label">
                Mot de passe
              </label>
              <input
                type="password"
                id="password"
                className="form-input"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="Votre mot de passe"
                autoComplete="current-password"
              />
            </div>

            <div
              className="flex gap-1 mb-2"
              style={{ justifyContent: 'space-between', alignItems: 'center' }}
            >
              <span className="brand-sub">Authentification chiffrée</span>
              <a href="#" className="subtitle" aria-label="Mot de passe oublié">
                Mot de passe oublié ?
              </a>
            </div>

            <button
              type="submit"
              className="btn btn-primary"
              disabled={isLoading}
              style={{ width: '100%' }}
            >
              {isLoading ? 'Connexion...' : 'Se connecter'}
            </button>
          </form>

          <div
            className="flex gap-1 mt-2"
            style={{ flexWrap: 'wrap', justifyContent: 'center' }}
          >
            <span className="chip">Traçabilité active</span>
            <span className="chip">Surveillance 24/7</span>
          </div>
        </div>
      </main>
    </div>
  )
}
