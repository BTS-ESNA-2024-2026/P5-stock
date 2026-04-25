import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { AuthProvider } from '../../context/AuthContext'
import LoginPage from '../LoginPage'

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function renderLoginPage(fetchImpl?: () => Promise<Response>) {
  if (fetchImpl) {
    vi.mocked(fetch).mockImplementation(fetchImpl)
  }
  return render(
    <MemoryRouter initialEntries={['/login']}>
      <AuthProvider>
        <LoginPage />
      </AuthProvider>
    </MemoryRouter>,
  )
}

beforeEach(() => vi.mocked(fetch).mockReset())
afterEach(() => {})

// Mock react-router-dom navigate
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>('react-router-dom')
  return {
    ...actual,
    useNavigate: () => vi.fn(),
  }
})

// ---------------------------------------------------------------------------
// Rendering
// ---------------------------------------------------------------------------

describe('LoginPage – rendering', () => {
  it('renders the login form', async () => {
    // /auth/me → not authenticated (so page is shown)
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(JSON.stringify({ message: 'Unauthorized' }), { status: 401 }),
    )
    renderLoginPage()

    await waitFor(() => {
      expect(screen.getByLabelText(/username/i)).toBeInTheDocument()
    })
    expect(document.getElementById('password')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /se connecter/i })).toBeInTheDocument()
  })

  it('shows the brand name', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(JSON.stringify({ message: 'Unauthorized' }), { status: 401 }),
    )
    renderLoginPage()
    await waitFor(() =>
      expect(screen.getByText('PSSTOCK', { selector: '.brand-mark' })).toBeInTheDocument(),
    )
  })
})

// ---------------------------------------------------------------------------
// Form interactions
// ---------------------------------------------------------------------------

describe('LoginPage – form interactions', () => {
  async function waitForForm() {
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(JSON.stringify({ message: 'Unauthorized' }), { status: 401 }),
    )
    renderLoginPage()
    await waitFor(() => screen.getByLabelText(/username/i))
  }

  it('updates username input', async () => {
    await waitForForm()
    const input = screen.getByLabelText(/username/i) as HTMLInputElement
    fireEvent.change(input, { target: { value: 'alice' } })
    expect(input.value).toBe('alice')
  })

  it('updates password input', async () => {
    await waitForForm()
    const input = document.getElementById('password') as HTMLInputElement
    fireEvent.change(input, { target: { value: 'secret' } })
    expect(input.value).toBe('secret')
  })

  it('shows error message on failed login', async () => {
    await waitForForm()

    // POST /auth/login → bad credentials
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(
        JSON.stringify({ message: 'Username or password incorrect' }),
        { status: 401 },
      ),
    )

    fireEvent.change(screen.getByLabelText(/username/i), { target: { value: 'bad' } })
    fireEvent.change(document.getElementById('password')!, { target: { value: 'wrong' } })
    fireEvent.submit(screen.getByRole('button', { name: /se connecter/i }).closest('form')!)

    await waitFor(() => {
      expect(screen.getByText(/incorrect/i)).toBeInTheDocument()
    })
  })

  it('disables the submit button while loading', async () => {
    await waitForForm()

    // Keep the fetch pending forever to stay in loading state
    vi.mocked(fetch).mockReturnValueOnce(new Promise(() => {}))

    fireEvent.change(screen.getByLabelText(/username/i), { target: { value: 'alice' } })
    fireEvent.change(document.getElementById('password')!, { target: { value: 'pass' } })
    fireEvent.submit(screen.getByRole('button', { name: /se connecter/i }).closest('form')!)

    expect(screen.getByRole('button', { name: /connexion/i })).toBeDisabled()
  })
})

// ---------------------------------------------------------------------------
// Redirect when already authenticated
// ---------------------------------------------------------------------------

describe('LoginPage – already authenticated', () => {
  it('redirects to /dashboard when user is logged in', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(
        JSON.stringify({ id: 'u1', username: 'alice', role: 'admin', active: true }),
        { status: 200 },
      ),
    )
    renderLoginPage()
    // The page should redirect — login form should not be visible
    await waitFor(() => {
      expect(screen.queryByLabelText(/username/i)).not.toBeInTheDocument()
    })
  })
})
