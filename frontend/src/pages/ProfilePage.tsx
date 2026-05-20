import { useState } from 'react'
import AppLayout from '../layouts/AppLayout'
import { useAuth } from '../context/AuthContext'
import { setupOtp, verifyOtp, disableOtp, type OtpSetupResponse } from '../api/auth'

export default function ProfilePage() {
  const { user, refresh } = useAuth()
  const [pending, setPending] = useState(false)
  const [error, setError] = useState('')
  const [info, setInfo] = useState('')
  const [setupData, setSetupData] = useState<OtpSetupResponse | null>(null)
  const [otpCode, setOtpCode] = useState('')
  const [copied, setCopied] = useState<'secret' | 'uri' | null>(null)

  const mfaEnabled = Boolean(user?.MFA)

  const handleStartSetup = async () => {
    setPending(true)
    setError('')
    setInfo('')
    try {
      const data = await setupOtp()
      setSetupData(data)
      setOtpCode('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Echec de la generation')
    } finally {
      setPending(false)
    }
  }

  const handleVerify = async () => {
    if (!setupData) return
    if (!/^\d{6}$/.test(otpCode)) {
      setError('Le code doit etre 6 chiffres')
      return
    }
    setPending(true)
    setError('')
    try {
      await verifyOtp(setupData.secret, otpCode)
      setSetupData(null)
      setOtpCode('')
      setInfo('2FA activee avec succes.')
      await refresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Code invalide')
    } finally {
      setPending(false)
    }
  }

  const handleCancel = () => {
    setSetupData(null)
    setOtpCode('')
    setError('')
  }

  const handleDisable = async () => {
    if (!confirm('Desactiver le 2FA ? Votre compte sera moins protege.')) return
    setPending(true)
    setError('')
    setInfo('')
    try {
      await disableOtp()
      await refresh()
      setInfo('2FA desactivee.')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Echec de la desactivation')
    } finally {
      setPending(false)
    }
  }

  const copy = async (value: string, kind: 'secret' | 'uri') => {
    try {
      await navigator.clipboard.writeText(value)
      setCopied(kind)
      setTimeout(() => setCopied(null), 1500)
    } catch {
      setError('Copie impossible')
    }
  }

  return (
    <AppLayout>
      <section className="page-hero">
        <div className="page-meta">
          <span className="brand-sub">Compte</span>
          <div className="title">Profil &amp; securite</div>
          <div className="subtitle">Gerer votre authentification a deux facteurs.</div>
        </div>
      </section>

      {error ? <div className="alert alert-danger">{error}</div> : null}
      {info ? <div className="alert alert-success">{info}</div> : null}

      <section className="panel">
        <div className="panel-header">
          <div className="panel-title">Informations</div>
        </div>
        <div className="form-group">
          <label className="form-label">Nom d'utilisateur</label>
          <input className="form-input" value={user?.username ?? ''} disabled />
        </div>
        <div className="form-group">
          <label className="form-label">Nom</label>
          <input className="form-input" value={user?.name ?? ''} disabled />
        </div>
        <div className="form-group">
          <label className="form-label">Role</label>
          <input className="form-input" value={user?.role ?? ''} disabled />
        </div>
      </section>

      <section className="panel">
        <div className="panel-header">
          <div className="panel-title">Authentification a deux facteurs (2FA)</div>
          <span className={`chip ${mfaEnabled ? 'badge-success' : 'badge-warning'}`}>
            {mfaEnabled ? 'Activee' : 'Desactivee'}
          </span>
        </div>

        <p className="subtitle">
          Une fois activee, un code a 6 chiffres sera demande a chaque connexion en plus du mot de passe.
          Utilisez une application TOTP (Google Authenticator, Aegis, Authy, 1Password...).
        </p>

        {!mfaEnabled && !setupData && (
          <button className="btn btn-primary" onClick={handleStartSetup} disabled={pending}>
            {pending ? 'Generation...' : 'Activer le 2FA'}
          </button>
        )}

        {setupData && (
          <div className="alert alert-warning" style={{ marginTop: '1rem' }}>
            <strong>Etape 1.</strong> Ajoutez ce compte a votre application d'authentification en
            scannant l'URI ou en saisissant la cle secrete manuellement.

            <div className="form-group" style={{ marginTop: '1rem' }}>
              <label className="form-label">Parametres a configurer (si saisie manuelle)</label>
              <table className="data-table" style={{ width: '100%' }}>
                <tbody>
                  <tr><td>Type</td><td><code>{setupData.type}</code></td></tr>
                  <tr><td>Algorithme</td><td><code>{setupData.algorithm}</code></td></tr>
                  <tr><td>Chiffres</td><td><code>{setupData.digits}</code></td></tr>
                  <tr><td>Periode</td><td><code>{setupData.period}s</code></td></tr>
                  <tr><td>Emetteur</td><td><code>{setupData.issuer}</code></td></tr>
                  <tr><td>Compte</td><td><code>{user?.username}</code></td></tr>
                </tbody>
              </table>
            </div>

            <div className="form-group">
              <label className="form-label">Cle secrete</label>
              <div className="flex gap-1">
                <input className="form-input" value={setupData.secret} readOnly style={{ fontFamily: 'monospace' }} />
                <button type="button" className="btn btn-secondary btn-sm" onClick={() => copy(setupData.secret, 'secret')}>
                  {copied === 'secret' ? 'Copie' : 'Copier'}
                </button>
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">URI otpauth:// (collable dans Aegis / Authy)</label>
              <div className="flex gap-1">
                <input className="form-input" value={setupData.uri} readOnly style={{ fontFamily: 'monospace' }} />
                <button type="button" className="btn btn-secondary btn-sm" onClick={() => copy(setupData.uri, 'uri')}>
                  {copied === 'uri' ? 'Copie' : 'Copier'}
                </button>
              </div>
            </div>

            <hr style={{ margin: '1rem 0', opacity: 0.2 }} />

            <strong>Etape 2.</strong> Saisissez le code a 6 chiffres genere par votre application
            pour confirmer la configuration. Le 2FA ne sera active qu'apres validation reussie.

            <div className="form-group" style={{ marginTop: '1rem' }}>
              <label className="form-label">Code de verification</label>
              <input
                className="form-input"
                value={otpCode}
                onChange={(e) => setOtpCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                placeholder="123456"
                inputMode="numeric"
                maxLength={6}
                autoFocus
                style={{ fontFamily: 'monospace', letterSpacing: '0.3em', textAlign: 'center' }}
              />
            </div>

            <div className="flex gap-2">
              <button className="btn btn-primary" onClick={handleVerify} disabled={pending || otpCode.length !== 6}>
                {pending ? 'Verification...' : 'Verifier et activer'}
              </button>
              <button className="btn btn-secondary" onClick={handleCancel} disabled={pending}>
                Annuler
              </button>
            </div>
          </div>
        )}

        {mfaEnabled && !setupData && (
          <button className="btn btn-danger" onClick={handleDisable} disabled={pending}>
            {pending ? 'Desactivation...' : 'Desactiver le 2FA'}
          </button>
        )}
      </section>
    </AppLayout>
  )
}
