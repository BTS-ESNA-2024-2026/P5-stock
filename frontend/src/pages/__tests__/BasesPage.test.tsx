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
    await waitFor(() => expect(screen.getAllByText(/Bases\s*&\s*Salles/i).length).toBeGreaterThan(0))
  })

  it('lists bases after load', async () => {
    setupMocks({
      bases: [
        { id: 'b1', name: 'Base Alpha', address: 'Paris' },
        { id: 'b2', name: 'Base Bravo', address: 'Lyon' },
      ],
    })
    renderPage()
    // Base names appear in both the table and the rooms-table base-filter
    // dropdown options, so use getAllByText for the assertion.
    await waitFor(() => expect(screen.getAllByText('Base Alpha').length).toBeGreaterThan(0))
    expect(screen.getAllByText('Base Bravo').length).toBeGreaterThan(0)
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
    await waitFor(() => screen.getAllByText('Base Alpha'))
    expect(screen.getAllByText('2').length).toBeGreaterThan(0)
  })
})

// ---------------------------------------------------------------------------
// Viewer – read-only
// ---------------------------------------------------------------------------

describe('BasesPage – viewer role', () => {
  it('does not show create button for viewer', async () => {
    setupMocks({ role: 'viewer' })
    renderPage()
    await waitFor(() => screen.getAllByText('Base Alpha'))
    // The button (not modal h3) should not be present for viewers
    expect(screen.queryByRole('button', { name: /\+ nouvelle base/i })).not.toBeInTheDocument()
  })

  it('does not show Edit buttons for viewer', async () => {
    setupMocks({ role: 'viewer' })
    renderPage()
    await waitFor(() => screen.getAllByText('Base Alpha'))
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
    await waitFor(() => screen.getAllByText('Base Alpha'))
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
    await waitFor(() => screen.getAllByText('Base Alpha'))

    const inputs = screen.getAllByPlaceholderText(/rechercher une base/i)
    fireEvent.change(inputs[0], { target: { value: 'bravo' } })

    await waitFor(() => {
      // After search, "Base Alpha" stays only in the rooms-table base filter
      // dropdown options (1 occurrence), but is gone from the bases table.
      expect(screen.getAllByText('Base Alpha').length).toBe(1)
      expect(screen.getAllByText('Base Bravo').length).toBeGreaterThan(0)
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
    await waitFor(() => screen.getAllByText('Base Alpha'))

    const inputs = screen.getAllByPlaceholderText(/rechercher une base/i)
    fireEvent.change(inputs[0], { target: { value: 'marseille' } })

    await waitFor(() => {
      expect(screen.getAllByText('Base Alpha').length).toBe(1)
      expect(screen.getAllByText('Base Bravo').length).toBeGreaterThan(0)
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
