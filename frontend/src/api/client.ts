export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

// Centralised handler for "session expired" responses. AuthContext registers a
// callback here so any apiFetch/authFetch call that returns 401 can clear the
// in-memory user and bounce the browser to /login without each page handling it.
type UnauthorizedHandler = () => void
let onUnauthorized: UnauthorizedHandler | null = null

export function setUnauthorizedHandler(handler: UnauthorizedHandler | null) {
  onUnauthorized = handler
}

function isLoginCall(path: string, base: '/api' | '/auth'): boolean {
  // The /auth/login and /auth/me endpoints legitimately return 401 during
  // normal operation; we should not treat those as session-expiry redirects.
  if (base !== '/auth') return false
  return path.startsWith('/login') || path.startsWith('/me')
}

async function fetchJson<T>(base: '/api' | '/auth', path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${base}${path}`, {
    ...options,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  })

  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    const message = data.message ?? data.error ?? 'Request failed'

    if (res.status === 401 && !isLoginCall(path, base)) {
      const handler = onUnauthorized
      if (handler) handler()
      throw new ApiError(401, 'Session expiree, reconnexion requise')
    }

    throw new ApiError(res.status, message)
  }

  return res.json()
}

export function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  return fetchJson<T>('/api', path, options)
}

export function authFetch<T>(path: string, options?: RequestInit): Promise<T> {
  return fetchJson<T>('/auth', path, options)
}
