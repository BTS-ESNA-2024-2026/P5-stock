import { useState } from 'react'
import type { FormEvent } from 'react'
import { useNavigate, Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function LoginPage() {
  const navigate = useNavigate()
  const { user, loading, login } = useAuth()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [otpCode, setOtpCode] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  if (!loading && user) {
    return <Navigate to="/dashboard" replace />
  }

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      await login(username, password, otpCode || undefined)
      navigate('/dashboard')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Connexion echouee')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="shell">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark">PSSTOCK</span>
        </div>
      </header>

      <main className="auth">
        <div className="auth-card">
          <div className="auth-header">
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

            <div className="form-group">
              <label htmlFor="otp_code" className="form-label">Code OTP <span className="subtitle">(si activé)</span></label>
              <input
                type="text"
                id="otp_code"
                className="form-input"
                value={otpCode}
                onChange={(event) => setOtpCode(event.target.value)}
                placeholder="6 chiffres"
                autoComplete="one-time-code"
                inputMode="numeric"
                maxLength={6}
              />
            </div>

            <button type="submit" className="btn btn-primary full-width" disabled={isLoading}>
              {isLoading ? 'Connexion...' : 'Se connecter'}
            </button>
          </form>
        </div>
      </main>
    </div>
  )
}