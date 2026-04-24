import { describe, it, expect, vi } from 'vitest'
import { fetchLogs } from '../dashboard'

function mockFetch(payload: unknown, status = 200) {
  vi.mocked(fetch).mockResolvedValueOnce(
    new Response(JSON.stringify(payload), { status }),
  )
}

beforeEach(() => vi.mocked(fetch).mockClear())

describe('fetchLogs', () => {
  it('calls GET /api/logs', async () => {
    mockFetch([])
    await fetchLogs()
    expect(fetch).toHaveBeenCalledWith('/api/logs', expect.any(Object))
  })

  it('returns the logs list', async () => {
    const logs = [{ id: 'l1', action: 'CREATE', asset_id: 'a1' }]
    mockFetch(logs)
    const result = await fetchLogs()
    expect(result).toEqual(logs)
  })

  it('throws ApiError on 401', async () => {
    mockFetch({ message: 'Unauthorized' }, 401)
    await expect(fetchLogs()).rejects.toMatchObject({ status: 401 })
  })
})
