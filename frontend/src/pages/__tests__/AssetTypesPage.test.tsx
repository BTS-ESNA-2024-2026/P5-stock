import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { AuthProvider } from '../../context/AuthContext'
import AssetTypesPage from '../AssetTypesPage'

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
  types = [{ id: 't1', type: 'Vehicule' }] as { id: string; type: string }[],
  specs = [{ id: 's1', type_id: 't1', name: 'Kilometrage', type_name: 'Vehicule' }] as object[],
} = {}) {
  const user = { id: 'u1', username: 'testuser', name: 'Test', role, active: true }
  vi.mocked(fetch).mockImplementation((input: FetchArgs[0]) => {
    const url = typeof input === 'string' ? input : input instanceof Request ? input.url : String(input)
    if (url.includes('/me')) {
      return Promise.resolve(new Response(JSON.stringify(user), { status: 200 }))
    }
    if (url.includes('/asset_types')) {
      return Promise.resolve(new Response(JSON.stringify(types), { status: 200 }))
    }
    if (url.includes('/specs')) {
      return Promise.resolve(new Response(JSON.stringify(specs), { status: 200 }))
    }
    return Promise.resolve(new Response(JSON.stringify([]), { status: 200 }))
  })
}

function renderPage() {
  return render(
    <MemoryRouter>
      <AuthProvider>
        <AssetTypesPage />
      </AuthProvider>
    </MemoryRouter>,
  )
}

beforeEach(() => vi.mocked(fetch).mockReset())

// ---------------------------------------------------------------------------
// Rendering
// ---------------------------------------------------------------------------

describe('AssetTypesPage – rendering', () => {
  it('shows the page title', async () => {
    setupMocks()
    renderPage()
    await waitFor(() =>
      expect(screen.getByText("Types d'assets & Specs")).toBeInTheDocument(),
    )
  })

  it('lists asset types after load', async () => {
    setupMocks({ types: [{ id: 't1', type: 'Armement' }, { id: 't2', type: 'MRE' }] })
    renderPage()
    await waitFor(() => expect(screen.getByText('Armement')).toBeInTheDocument())
    expect(screen.getByText('MRE')).toBeInTheDocument()
  })

  it('shows spec count badge per type', async () => {
    setupMocks({
      types: [{ id: 't1', type: 'Vehicule' }],
      specs: [
        { id: 's1', type_id: 't1', name: 'Kilometrage', type_name: 'Vehicule' },
        { id: 's2', type_id: 't1', name: 'Poids', type_name: 'Vehicule' },
      ],
    })
    renderPage()
    await waitFor(() => screen.getByText('Vehicule'))
    expect(screen.getByText('2')).toBeInTheDocument()
  })
})

// ---------------------------------------------------------------------------
// Viewer – no edit buttons
// ---------------------------------------------------------------------------

describe('AssetTypesPage – viewer role', () => {
  it('does not show create button for viewer', async () => {
    setupMocks({ role: 'viewer' })
    renderPage()
    await waitFor(() => screen.getByText('Vehicule'))
    expect(screen.queryByRole('button', { name: /\+ nouveau type/i })).not.toBeInTheDocument()
  })
})

// ---------------------------------------------------------------------------
// Technician – edit buttons visible
// ---------------------------------------------------------------------------

describe('AssetTypesPage – technician role', () => {
  it('shows + Nouveau type button', async () => {
    setupMocks({ role: 'technician' })
    renderPage()
    await waitFor(() => screen.getByRole('button', { name: /\+ nouveau type/i }))
  })

  it('opens create modal on button click', async () => {
    setupMocks({ role: 'technician' })
    renderPage()
    await waitFor(() => screen.getByRole('button', { name: /\+ nouveau type/i }))
    fireEvent.click(screen.getByRole('button', { name: /\+ nouveau type/i }))
    await waitFor(() =>
      expect(screen.getByPlaceholderText(/vehicule, armement/i)).toBeInTheDocument(),
    )
  })
})

// ---------------------------------------------------------------------------
// Spec panel
// ---------------------------------------------------------------------------

describe('AssetTypesPage – spec panel', () => {
  it('opens spec panel when clicking a type row', async () => {
    setupMocks({
      role: 'technician',
      types: [{ id: 't1', type: 'Vehicule' }],
      specs: [{ id: 's1', type_id: 't1', name: 'Kilometrage', type_name: 'Vehicule' }],
    })
    renderPage()
    await waitFor(() => screen.getByText('Vehicule'))
    fireEvent.click(screen.getByText('Vehicule'))
    await waitFor(() => expect(screen.getByText('Kilometrage')).toBeInTheDocument())
  })

  it('shows empty message when no specs', async () => {
    setupMocks({
      role: 'technician',
      types: [{ id: 't1', type: 'MRE' }],
      specs: [],
    })
    renderPage()
    await waitFor(() => screen.getByText('MRE'))
    fireEvent.click(screen.getByText('MRE'))
    await waitFor(() =>
      expect(screen.getByText(/aucune spec pour ce type/i)).toBeInTheDocument(),
    )
  })
})

// ---------------------------------------------------------------------------
// Search filter
// ---------------------------------------------------------------------------

describe('AssetTypesPage – search', () => {
  it('filters types by search text', async () => {
    setupMocks({ types: [{ id: 't1', type: 'Vehicule' }, { id: 't2', type: 'Armement' }] })
    renderPage()
    await waitFor(() => screen.getByText('Vehicule'))

    const input = screen.getByPlaceholderText(/rechercher un type/i)
    fireEvent.change(input, { target: { value: 'arm' } })

    await waitFor(() => {
      expect(screen.queryByText('Vehicule')).not.toBeInTheDocument()
      expect(screen.getByText('Armement')).toBeInTheDocument()
    })
  })
})
