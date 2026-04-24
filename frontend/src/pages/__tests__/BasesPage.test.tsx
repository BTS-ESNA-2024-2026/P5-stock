import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { AuthProvider } from '../../context/AuthContext'
import BasesPage from '../BasesPage'

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>('react-router-dom')
  return { ...actual, useNavigate: () => vi.fn() }
})

type FetchArgs = Parameters<typeof fetch>

function setupMocks({
  role = 'viewer',
  bases = [{ id: 'b1', name: 'Base Alpha', address: 'Paris' }] as object[],
} = {}) {
  const user = { id: 'u1', username: 'testuser', name: 'Test', role, active: true }
  vi.mocked(fetch).mockImplementation((input: FetchArgs[0]) => {
    const url = typeof input === 'string' ? input : input instanceof Request ? input.url : String(input)
    if (url.includes('/me')) {
      return Promise.resolve(new Response(JSON.stringify(user), { status: 200 }))
    }
    if (url.includes('/bases')) {
      return Promise.resolve(new Response(JSON.stringify(bases), { status: 200 }))
    }
    return Promise.resolve(new Response(JSON.stringify([]), { status: 200 }))
  })
}

function renderPage() {
  return render(
    <MemoryRouter>
      <AuthProvider>
        <BasesPage />
      </AuthProvider>
    </MemoryRouter>,
  )
}

beforeEach(() => vi.mocked(fetch).mockReset())

// ---------------------------------------------------------------------------
// Rendering
// ---------------------------------------------------------------------------

describe('BasesPage – rendering', () => {
  it('shows the page title', async () => {
    setupMocks()
    renderPage()
    await waitFor(() => expect(screen.getAllByText('Bases').length).toBeGreaterThan(0))
  })

  it('lists bases after load', async () => {
    setupMocks({
      bases: [
        { id: 'b1', name: 'Base Alpha', address: 'Paris' },
        { id: 'b2', name: 'Base Bravo', address: 'Lyon' },
      ],
    })
    renderPage()
    await waitFor(() => expect(screen.getByText('Base Alpha')).toBeInTheDocument())
    expect(screen.getByText('Base Bravo')).toBeInTheDocument()
    expect(screen.getByText('Paris')).toBeInTheDocument()
  })

  it('shows total count stat', async () => {
    setupMocks({
      bases: [
        { id: 'b1', name: 'Base Alpha', address: 'Paris' },
        { id: 'b2', name: 'Base Bravo', address: 'Lyon' },
      ],
    })
    renderPage()
    await waitFor(() => screen.getByText('Base Alpha'))
    expect(screen.getByText('2')).toBeInTheDocument()
  })
})

// ---------------------------------------------------------------------------
// Viewer – read-only
// ---------------------------------------------------------------------------

describe('BasesPage – viewer role', () => {
  it('does not show create button for viewer', async () => {
    setupMocks({ role: 'viewer' })
    renderPage()
    await waitFor(() => screen.getByText('Base Alpha'))
    // The button (not modal h3) should not be present for viewers
    expect(screen.queryByRole('button', { name: /\+ nouvelle base/i })).not.toBeInTheDocument()
  })

  it('does not show Edit buttons for viewer', async () => {
    setupMocks({ role: 'viewer' })
    renderPage()
    await waitFor(() => screen.getByText('Base Alpha'))
    expect(screen.queryByText(/edit/i)).not.toBeInTheDocument()
  })
})

// ---------------------------------------------------------------------------
// Technician – edit capabilities
// ---------------------------------------------------------------------------

describe('BasesPage – technician role', () => {
  it('shows + Nouvelle base button', async () => {
    setupMocks({ role: 'technician' })
    renderPage()
    await waitFor(() => screen.getByRole('button', { name: /\+ nouvelle base/i }))
  })

  it('opens create modal on button click', async () => {
    setupMocks({ role: 'technician' })
    renderPage()
    await waitFor(() => screen.getByRole('button', { name: /\+ nouvelle base/i }))
    fireEvent.click(screen.getByRole('button', { name: /\+ nouvelle base/i }))
    await waitFor(() =>
      expect(screen.getByPlaceholderText(/base alpha/i)).toBeInTheDocument(),
    )
  })

  it('shows Edit buttons for technician', async () => {
    setupMocks({ role: 'technician' })
    renderPage()
    await waitFor(() => screen.getByText('Base Alpha'))
    expect(screen.getAllByText(/edit/i).length).toBeGreaterThan(0)
  })
})

// ---------------------------------------------------------------------------
// Search filter
// ---------------------------------------------------------------------------

describe('BasesPage – search', () => {
  it('filters bases by name', async () => {
    setupMocks({
      bases: [
        { id: 'b1', name: 'Base Alpha', address: 'Paris' },
        { id: 'b2', name: 'Base Bravo', address: 'Lyon' },
      ],
    })
    renderPage()
    await waitFor(() => screen.getByText('Base Alpha'))

    const input = screen.getByPlaceholderText(/rechercher une base/i)
    fireEvent.change(input, { target: { value: 'bravo' } })

    await waitFor(() => {
      expect(screen.queryByText('Base Alpha')).not.toBeInTheDocument()
      expect(screen.getByText('Base Bravo')).toBeInTheDocument()
    })
  })

  it('filters bases by address', async () => {
    setupMocks({
      bases: [
        { id: 'b1', name: 'Base Alpha', address: 'Paris' },
        { id: 'b2', name: 'Base Bravo', address: 'Marseille' },
      ],
    })
    renderPage()
    await waitFor(() => screen.getByText('Base Alpha'))

    const input = screen.getByPlaceholderText(/rechercher une base/i)
    fireEvent.change(input, { target: { value: 'marseille' } })

    await waitFor(() => {
      expect(screen.queryByText('Base Alpha')).not.toBeInTheDocument()
      expect(screen.getByText('Base Bravo')).toBeInTheDocument()
    })
  })
})

// ---------------------------------------------------------------------------
// Empty state
// ---------------------------------------------------------------------------

describe('BasesPage – empty state', () => {
  it('shows no result message when no bases match', async () => {
    setupMocks({ bases: [] })
    renderPage()
    await waitFor(() =>
      expect(screen.getByText(/aucune base correspondante/i)).toBeInTheDocument(),
    )
  })
})
