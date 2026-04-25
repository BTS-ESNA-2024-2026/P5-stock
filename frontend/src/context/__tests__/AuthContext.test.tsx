import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { AuthProvider, useAuth } from '../AuthContext'

// ---------------------------------------------------------------------------
// Reset the fetch mock before every test so results don't bleed across.
// ---------------------------------------------------------------------------
beforeEach(() => {
  vi.mocked(fetch).mockReset()
})

// ---------------------------------------------------------------------------
// Helper – a component that exposes AuthContext values to the DOM.
// ---------------------------------------------------------------------------
function ConsumerComponent() {
  const { user, loading, logout } = useAuth()
  if (loading) return <div data-testid="loading">loading</div>
  if (!user) return <div data-testid="unauthenticated">not logged in</div>
  return (
    <div>
      <div data-testid="username">{user.username}</div>
      <button onClick={logout} data-testid="logout-btn">Logout</button>
    </div>
  )
}

// ---------------------------------------------------------------------------
// AuthProvider — initial load
// ---------------------------------------------------------------------------

describe('AuthProvider – initial load', () => {
  it('sets user when /auth/me succeeds', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(JSON.stringify({ id: 'u1', username: 'alice', role: 'admin', active: true }), {
        status: 200,
      }),
    )
    render(
      <AuthProvider>
        <ConsumerComponent />
      </AuthProvider>,
    )
    await waitFor(() => expect(screen.getByTestId('username')).toHaveTextContent('alice'))
  })

  it('leaves user null when /auth/me returns 401', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(JSON.stringify({ message: 'Unauthorized' }), { status: 401 }),
    )
    render(
      <AuthProvider>
        <ConsumerComponent />
      </AuthProvider>,
    )
    await waitFor(() => expect(screen.getByTestId('unauthenticated')).toBeInTheDocument())
  })

  it('leaves user null when fetch rejects (network error)', async () => {
    vi.mocked(fetch).mockRejectedValueOnce(new Error('Network error'))
    render(
      <AuthProvider>
        <ConsumerComponent />
      </AuthProvider>,
    )
    await waitFor(() => expect(screen.getByTestId('unauthenticated')).toBeInTheDocument())
  })
})

// ---------------------------------------------------------------------------
// AuthProvider – login
// ---------------------------------------------------------------------------

describe('AuthProvider – login', () => {
  function LoginButton() {
    const { login, user } = useAuth()
    const doLogin = () => { login('alice', 'password123').catch(() => {}) }
    if (user) return <div data-testid="logged-in">{user.username}</div>
    return <button onClick={doLogin} data-testid="login-btn">Login</button>
  }

  it('updates user state after successful login', async () => {
    // Initial /auth/me → not logged in
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(JSON.stringify({ message: 'Unauthorized' }), { status: 401 }),
    )
    render(
      <AuthProvider>
        <LoginButton />
      </AuthProvider>,
    )
    await waitFor(() => screen.getByTestId('login-btn'))

    // POST /auth/login → success
    vi.mocked(fetch).mockResolvedValueOnce(new Response('{}', { status: 200 }))
    // /auth/me refresh after login → user data
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(JSON.stringify({ id: 'u1', username: 'alice', role: 'admin', active: true }), {
        status: 200,
      }),
    )

    fireEvent.click(screen.getByTestId('login-btn'))
    await waitFor(() => expect(screen.getByTestId('logged-in')).toHaveTextContent('alice'))
  })

  it('throws ApiError on failed login', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(JSON.stringify({ message: 'Unauthorized' }), { status: 401 }),
    )

    let caughtError: unknown
    function ErrorLoginButton() {
      const { login } = useAuth()
      const doLogin = async () => {
        try {
          await login('bad', 'creds')
        } catch (e) {
          caughtError = e
        }
      }
      return <button onClick={doLogin} data-testid="login-btn">Login</button>
    }

    render(
      <AuthProvider>
        <ErrorLoginButton />
      </AuthProvider>,
    )
    await waitFor(() => screen.getByTestId('login-btn'))

    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(JSON.stringify({ message: 'Username or password incorrect' }), { status: 401 }),
    )

    fireEvent.click(screen.getByTestId('login-btn'))
    await waitFor(() => expect(caughtError).toBeDefined())
  })
})

// ---------------------------------------------------------------------------
// AuthProvider – logout
// ---------------------------------------------------------------------------

describe('AuthProvider – logout', () => {
  it('clears the user state after logout', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(JSON.stringify({ id: 'u1', username: 'alice', role: 'admin', active: true }), {
        status: 200,
      }),
    )
    render(
      <AuthProvider>
        <ConsumerComponent />
      </AuthProvider>,
    )
    await waitFor(() => expect(screen.getByTestId('logout-btn')).toBeInTheDocument())

    vi.mocked(fetch).mockResolvedValueOnce(new Response('{}', { status: 200 }))
    fireEvent.click(screen.getByTestId('logout-btn'))
    await waitFor(() => expect(screen.getByTestId('unauthenticated')).toBeInTheDocument())
  })

  it('clears user even when logout request fails', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(JSON.stringify({ id: 'u1', username: 'alice', role: 'admin', active: true }), {
        status: 200,
      }),
    )
    render(
      <AuthProvider>
        <ConsumerComponent />
      </AuthProvider>,
    )
    await waitFor(() => screen.getByTestId('logout-btn'))

    vi.mocked(fetch).mockResolvedValueOnce(new Response('{}', { status: 500 }))
    fireEvent.click(screen.getByTestId('logout-btn'))
    await waitFor(() => expect(screen.getByTestId('unauthenticated')).toBeInTheDocument())
  })
})

// ---------------------------------------------------------------------------
// useAuth – outside provider
// ---------------------------------------------------------------------------

describe('useAuth outside provider', () => {
  it('throws when used outside AuthProvider', () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    expect(() => render(<ConsumerComponent />)).toThrow()
    consoleSpy.mockRestore()
  })
})
