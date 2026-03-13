import { useState } from 'react'
import type { FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'

export default function LoginPage() {
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      const body = new URLSearchParams({ username, password })
      const response = await fetch('/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        },
        credentials: 'include',
        body,
      })

      if (!response.ok) {
        const data = await response.json().catch(() => ({}))
        setError(data.message ?? 'Connexion echouee')
        return
      }

      navigate('/dashboard')
    } catch {
      setError('Impossible de joindre le backend')
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
          <span className="chip">Acces securise</span>
        </div>
      </header>

      <main className="auth">
        <div className="auth-card">
          <div className="auth-header">
            <span className="brand-sub">Portail operationnel</span>
            <div className="auth-title">Connexion</div>
            <p className="subtitle">Acces au tableau de bord et a la supervision PSSTOCK.</p>
          </div>

          {error ? <div className="alert alert-danger mb-2">{error}</div> : null}

          <form onSubmit={onSubmit}>
            <div className="form-group">
              <label htmlFor="username" className="form-label">Username</label>
              <input
                type="text"
                id="username"
                className="form-input"
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                required
                placeholder="Username"
                autoComplete="username"
              />
            </div>

            <div className="form-group">
              <label htmlFor="password" className="form-label">Mot de passe</label>
              <input
                type="password"
                id="password"
                className="form-input"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                required
                placeholder="Votre mot de passe"
                autoComplete="current-password"
              />
            </div>

            <div className="flex gap-1 mb-2 row-between">
              <span className="brand-sub">Authentification chiffree</span>
              <a href="#" className="subtitle" aria-label="Mot de passe oublie">Mot de passe oublie ?</a>
            </div>

            <button type="submit" className="btn btn-primary full-width" disabled={isLoading}>
              {isLoading ? 'Connexion...' : 'Se connecter'}
            </button>
          </form>

          <div className="flex gap-1 mt-2 wrap-center">
            <span className="chip">Tracabilite active</span>
            <span className="chip">Surveillance 24/7</span>
          </div>
        </div>
      </main>
    </div>
  )
}