import { describe, it, expect, vi } from 'vitest'
import {
  fetchAssets,
  createAsset,
  updateAsset,
  deleteAsset,
  fetchAssetTypes,
  createAssetType,
  updateAssetType,
  deleteAssetType,
  fetchSpecs,
  createSpec,
  updateSpec,
  deleteSpec,
  fetchAssetValues,
  createValue,
  updateValue,
  deleteValue,
  fetchRooms,
  fetchBases,
  createBase,
  updateBase,
  deleteBase,
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

// ---------------------------------------------------------------------------
// updateAssetType
// ---------------------------------------------------------------------------

describe('updateAssetType', () => {
  it('calls PUT /api/asset_type/:id', async () => {
    mockFetch({ message: 'updated' })
    await updateAssetType('t1', { type: 'Armement' })
    expect(fetch).toHaveBeenCalledWith(
      '/api/asset_type/t1',
      expect.objectContaining({ method: 'PUT', body: JSON.stringify({ type: 'Armement' }) }),
    )
  })

  it('returns the server message', async () => {
    mockFetch({ message: 'ok' })
    const result = await updateAssetType('t1', { type: 'X' })
    expect(result).toEqual({ message: 'ok' })
  })
})

// ---------------------------------------------------------------------------
// deleteAssetType
// ---------------------------------------------------------------------------

describe('deleteAssetType', () => {
  it('calls DELETE /api/asset_type/:id', async () => {
    mockFetch({ message: 'deleted' })
    await deleteAssetType('t1')
    expect(fetch).toHaveBeenCalledWith(
      '/api/asset_type/t1',
      expect.objectContaining({ method: 'DELETE' }),
    )
  })

  it('throws ApiError on 403', async () => {
    mockFetchError({ message: 'Forbidden' }, 403)
    await expect(deleteAssetType('t1')).rejects.toMatchObject({ status: 403 })
  })
})

// ---------------------------------------------------------------------------
// fetchSpecs
// ---------------------------------------------------------------------------

describe('fetchSpecs', () => {
  it('calls GET /api/specs and returns list', async () => {
    const specs = [{ id: 's1', type_id: 't1', name: 'Kilometrage' }]
    mockFetch(specs)
    const result = await fetchSpecs()
    expect(fetch).toHaveBeenCalledWith('/api/specs', expect.any(Object))
    expect(result).toEqual(specs)
  })
})

// ---------------------------------------------------------------------------
// createSpec
// ---------------------------------------------------------------------------

describe('createSpec', () => {
  it('calls POST /api/spec with correct payload', async () => {
    mockFetch({ message: 'created' })
    await createSpec({ type_id: 't1', name: 'Poids' })
    expect(fetch).toHaveBeenCalledWith(
      '/api/spec',
      expect.objectContaining({ method: 'POST', body: JSON.stringify({ type_id: 't1', name: 'Poids' }) }),
    )
  })
})

// ---------------------------------------------------------------------------
// updateSpec
// ---------------------------------------------------------------------------

describe('updateSpec', () => {
  it('calls PUT /api/spec/:id', async () => {
    mockFetch({ message: 'updated' })
    await updateSpec('s1', { name: 'Poids total' })
    expect(fetch).toHaveBeenCalledWith(
      '/api/spec/s1',
      expect.objectContaining({ method: 'PUT', body: JSON.stringify({ name: 'Poids total' }) }),
    )
  })
})

// ---------------------------------------------------------------------------
// deleteSpec
// ---------------------------------------------------------------------------

describe('deleteSpec', () => {
  it('calls DELETE /api/spec/:id', async () => {
    mockFetch({ message: 'deleted' })
    await deleteSpec('s1')
    expect(fetch).toHaveBeenCalledWith(
      '/api/spec/s1',
      expect.objectContaining({ method: 'DELETE' }),
    )
  })
})

// ---------------------------------------------------------------------------
// fetchAssetValues
// ---------------------------------------------------------------------------

describe('fetchAssetValues', () => {
  it('calls GET /api/asset/:id/values and returns list', async () => {
    const values = [{ id: 'v1', asset_id: 'a1', spec_id: 's1', value: '42km', spec_name: 'Kilometrage' }]
    mockFetch(values)
    const result = await fetchAssetValues('a1')
    expect(fetch).toHaveBeenCalledWith('/api/asset/a1/values', expect.any(Object))
    expect(result).toEqual(values)
  })

  it('throws ApiError on 404', async () => {
    mockFetchError({ message: 'Not found' }, 404)
    await expect(fetchAssetValues('missing')).rejects.toMatchObject({ status: 404 })
  })
})

// ---------------------------------------------------------------------------
// createValue
// ---------------------------------------------------------------------------

describe('createValue', () => {
  it('calls POST /api/value with correct payload', async () => {
    mockFetch({ message: 'created' })
    await createValue({ asset_id: 'a1', spec_id: 's1', value: '25000 km' })
    expect(fetch).toHaveBeenCalledWith(
      '/api/value',
      expect.objectContaining({ method: 'POST', body: JSON.stringify({ asset_id: 'a1', spec_id: 's1', value: '25000 km' }) }),
    )
  })
})

// ---------------------------------------------------------------------------
// updateValue
// ---------------------------------------------------------------------------

describe('updateValue', () => {
  it('calls PUT /api/value/:id', async () => {
    mockFetch({ message: 'updated' })
    await updateValue('v1', { value: '30000 km' })
    expect(fetch).toHaveBeenCalledWith(
      '/api/value/v1',
      expect.objectContaining({ method: 'PUT', body: JSON.stringify({ value: '30000 km' }) }),
    )
  })
})

// ---------------------------------------------------------------------------
// deleteValue
// ---------------------------------------------------------------------------

describe('deleteValue', () => {
  it('calls DELETE /api/value/:id', async () => {
    mockFetch({ message: 'deleted' })
    await deleteValue('v1')
    expect(fetch).toHaveBeenCalledWith(
      '/api/value/v1',
      expect.objectContaining({ method: 'DELETE' }),
    )
  })

  it('throws ApiError on 403', async () => {
    mockFetchError({ message: 'Forbidden' }, 403)
    await expect(deleteValue('v1')).rejects.toMatchObject({ status: 403 })
  })
})

// ---------------------------------------------------------------------------
// createBase
// ---------------------------------------------------------------------------

describe('createBase', () => {
  it('calls POST /api/base with correct payload', async () => {
    mockFetch({ message: 'created' })
    await createBase({ name: 'Base Alpha', address: '1 rue de la Paix' })
    expect(fetch).toHaveBeenCalledWith(
      '/api/base',
      expect.objectContaining({ method: 'POST', body: JSON.stringify({ name: 'Base Alpha', address: '1 rue de la Paix' }) }),
    )
  })
})

// ---------------------------------------------------------------------------
// updateBase
// ---------------------------------------------------------------------------

describe('updateBase', () => {
  it('calls PUT /api/base/:id', async () => {
    mockFetch({ message: 'updated' })
    await updateBase('b1', { name: 'Base Beta', address: 'Lyon' })
    expect(fetch).toHaveBeenCalledWith(
      '/api/base/b1',
      expect.objectContaining({ method: 'PUT', body: JSON.stringify({ name: 'Base Beta', address: 'Lyon' }) }),
    )
  })
})

// ---------------------------------------------------------------------------
// deleteBase
// ---------------------------------------------------------------------------

describe('deleteBase', () => {
  it('calls DELETE /api/base/:id', async () => {
    mockFetch({ message: 'deleted' })
    await deleteBase('b1')
    expect(fetch).toHaveBeenCalledWith(
      '/api/base/b1',
      expect.objectContaining({ method: 'DELETE' }),
    )
  })

  it('throws ApiError on 403', async () => {
    mockFetchError({ message: 'Forbidden' }, 403)
    await expect(deleteBase('b1')).rejects.toMatchObject({ status: 403 })
  })
})
