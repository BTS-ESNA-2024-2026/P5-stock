import { describe, it, expect, vi } from 'vitest'
import { fetchUsers, fetchRoles } from '../admin'

function mockFetch(payload: unknown, status = 200) {
  vi.mocked(fetch).mockResolvedValueOnce(
    new Response(JSON.stringify(payload), { status }),
  )
}

beforeEach(() => vi.mocked(fetch).mockClear())

describe('fetchUsers', () => {
  it('calls GET /api/users', async () => {
    mockFetch([])
    await fetchUsers()
    expect(fetch).toHaveBeenCalledWith('/api/users', expect.any(Object))
  })

  it('returns users list', async () => {
    const users = [{ id: 'u1', username: 'alice', active: true }]
    mockFetch(users)
    const result = await fetchUsers()
    expect(result).toEqual(users)
  })

  it('throws ApiError on 403', async () => {
    mockFetch({ message: 'Forbidden' }, 403)
    await expect(fetchUsers()).rejects.toMatchObject({ status: 403 })
  })
})

describe('fetchRoles', () => {
  it('calls GET /api/roles', async () => {
    mockFetch([])
    await fetchRoles()
    expect(fetch).toHaveBeenCalledWith('/api/roles', expect.any(Object))
  })

  it('returns roles list', async () => {
    const roles = [{ id: 'r1', name: 'admin' }, { id: 'r2', name: 'viewer' }]
    mockFetch(roles)
    const result = await fetchRoles()
    expect(result).toEqual(roles)
  })
})
