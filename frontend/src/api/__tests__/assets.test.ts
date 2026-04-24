import { describe, it, expect, vi } from 'vitest'
import {
  fetchAssets,
  createAsset,
  updateAsset,
  deleteAsset,
  fetchAssetTypes,
  createAssetType,
  fetchRooms,
  fetchBases,
} from '../assets'

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function mockFetch(payload: unknown, status = 200) {
  vi.mocked(fetch).mockResolvedValueOnce(
    new Response(JSON.stringify(payload), { status }),
  )
}

function mockFetchError(payload: unknown, status: number) {
  vi.mocked(fetch).mockResolvedValueOnce(
    new Response(JSON.stringify(payload), { status }),
  )
}

beforeEach(() => vi.mocked(fetch).mockClear())

// ---------------------------------------------------------------------------
// fetchAssets
// ---------------------------------------------------------------------------

describe('fetchAssets', () => {
  it('calls GET /api/assets', async () => {
    mockFetch([])
    await fetchAssets()
    expect(fetch).toHaveBeenCalledWith('/api/assets', expect.any(Object))
  })

  it('returns the asset list', async () => {
    const assets = [{ id: '1', name: 'Laptop', status: 'STOCK' }]
    mockFetch(assets)
    const result = await fetchAssets()
    expect(result).toEqual(assets)
  })

  it('throws ApiError on failure', async () => {
    mockFetchError({ message: 'Forbidden' }, 401)
    await expect(fetchAssets()).rejects.toMatchObject({ status: 401 })
  })
})

// ---------------------------------------------------------------------------
// createAsset
// ---------------------------------------------------------------------------

describe('createAsset', () => {
  it('calls POST /api/asset with the payload', async () => {
    mockFetch({ message: 'created' })
    const data = { name: 'New Laptop', type_asset_id: 'tid', status: 'STOCK' }
    await createAsset(data)
    expect(fetch).toHaveBeenCalledWith(
      '/api/asset',
      expect.objectContaining({ method: 'POST', body: JSON.stringify(data) }),
    )
  })

  it('returns the server message', async () => {
    mockFetch({ message: 'Asset created' })
    const result = await createAsset({ name: 'x', type_asset_id: 't', status: 'STOCK' })
    expect(result).toEqual({ message: 'Asset created' })
  })

  it('throws ApiError on 400', async () => {
    mockFetchError({ message: 'Bad request' }, 400)
    await expect(createAsset({})).rejects.toMatchObject({ status: 400 })
  })
})

// ---------------------------------------------------------------------------
// updateAsset
// ---------------------------------------------------------------------------

describe('updateAsset', () => {
  it('calls PUT /api/asset/:id', async () => {
    mockFetch({ message: 'updated' })
    await updateAsset('abc-123', { name: 'Updated' })
    expect(fetch).toHaveBeenCalledWith(
      '/api/asset/abc-123',
      expect.objectContaining({ method: 'PUT' }),
    )
  })

  it('returns the server message', async () => {
    mockFetch({ message: 'Asset updated' })
    const result = await updateAsset('abc', { name: 'Patched' })
    expect(result).toEqual({ message: 'Asset updated' })
  })
})

// ---------------------------------------------------------------------------
// deleteAsset
// ---------------------------------------------------------------------------

describe('deleteAsset', () => {
  it('calls DELETE /api/asset/:id', async () => {
    mockFetch({ message: 'deleted' })
    await deleteAsset('abc-123')
    expect(fetch).toHaveBeenCalledWith(
      '/api/asset/abc-123',
      expect.objectContaining({ method: 'DELETE' }),
    )
  })

  it('throws ApiError on 404', async () => {
    mockFetchError({ message: 'Not found' }, 404)
    await expect(deleteAsset('missing')).rejects.toMatchObject({ status: 404 })
  })
})

// ---------------------------------------------------------------------------
// fetchAssetTypes
// ---------------------------------------------------------------------------

describe('fetchAssetTypes', () => {
  it('calls GET /api/asset_types', async () => {
    mockFetch([])
    await fetchAssetTypes()
    expect(fetch).toHaveBeenCalledWith('/api/asset_types', expect.any(Object))
  })

  it('returns the types list', async () => {
    const types = [{ id: 't1', type: 'Laptop' }]
    mockFetch(types)
    const result = await fetchAssetTypes()
    expect(result).toEqual(types)
  })
})

// ---------------------------------------------------------------------------
// createAssetType
// ---------------------------------------------------------------------------

describe('createAssetType', () => {
  it('calls POST /api/asset_type', async () => {
    mockFetch({ message: 'created' })
    await createAssetType({ type: 'Server' })
    expect(fetch).toHaveBeenCalledWith(
      '/api/asset_type',
      expect.objectContaining({ method: 'POST', body: JSON.stringify({ type: 'Server' }) }),
    )
  })
})

// ---------------------------------------------------------------------------
// fetchRooms
// ---------------------------------------------------------------------------

describe('fetchRooms', () => {
  it('calls GET /api/rooms and returns list', async () => {
    const rooms = [{ id: 'r1', base_id: 'b1', room: 'Salle 1' }]
    mockFetch(rooms)
    const result = await fetchRooms()
    expect(fetch).toHaveBeenCalledWith('/api/rooms', expect.any(Object))
    expect(result).toEqual(rooms)
  })
})

// ---------------------------------------------------------------------------
// fetchBases
// ---------------------------------------------------------------------------

describe('fetchBases', () => {
  it('calls GET /api/bases and returns list', async () => {
    const bases = [{ id: 'b1', name: 'Base Navale', address: 'Toulon' }]
    mockFetch(bases)
    const result = await fetchBases()
    expect(fetch).toHaveBeenCalledWith('/api/bases', expect.any(Object))
    expect(result).toEqual(bases)
  })
})
